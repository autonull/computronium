"""The PC inference kernels' specification, written before the kernels (TODO36 §4.5).

`_pc_prediction_kernel` and `_pc_error_update_kernel` compile as of §4.5 and had no
torch reference and no parity test — compiling is not being correct. This file
writes the expressions down first, from the kernels' own docstrings and the
standard predictive-coding inference equations, and then holds the kernels to
them. The references are anchored to plain torch, and the activation table is
spelled out rather than imported from the kernel, so a change to the kernel cannot
change the specification.
"""

from dataclasses import replace

import pytest
import torch
import triton

B, D_IN, D_OUT = 16, 32, 32
LR = 0.01

#: ``activation_type`` as the kernels encode it.
ACTIVATIONS = ("relu", "silu", "tanh", "gelu")


def activation(value: torch.Tensor, kind: str) -> torch.Tensor:
    """The four activations the PC kernels dispatch on."""
    match kind:
        case "relu":
            return torch.relu(value)
        case "silu":
            return value * torch.sigmoid(value)
        case "tanh":
            return torch.tanh(value)
        case "gelu":
            return value * 0.5 * (1.0 + torch.erf(value * 0.7071067811865475))
    raise ValueError(f"unknown activation {kind!r}")


def activation_derivative(pre: torch.Tensor, kind: str) -> torch.Tensor:
    """The derivative of :func:`activation`, evaluated at the **pre**-activation.

    Every branch is the derivative of the activation applied to its input, which
    is the definition the kernels' docstrings state ("act_deriv(mu)").
    """
    match kind:
        case "relu":
            return (pre > 0).to(pre.dtype)
        case "silu":
            sig = torch.sigmoid(pre)
            return sig * (1.0 + pre * (1.0 - sig))
        case "tanh":
            return 1.0 - torch.tanh(pre) ** 2
        case "gelu":
            cdf = 0.5 * (1.0 + torch.erf(pre * 0.7071067811865475))
            pdf = torch.exp(-pre * pre * 0.5) * 0.3989422804014327
            return cdf + pre * pdf
    raise ValueError(f"unknown activation {kind!r}")


def pc_prediction(
    mu: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, kind: str
) -> torch.Tensor:
    """``pred = act(mu @ W.T + b)`` — the layer's prediction from its state."""
    return activation(mu @ weight.T + bias, kind)


def pc_inference_step(
    mu: torch.Tensor, pred: torch.Tensor, eta: float, kind: str
) -> torch.Tensor:
    """``mu' = mu - eta * (mu - pred) * act'(mu)`` — one gradient-ascent settle step."""
    return mu - eta * (mu - pred) * activation_derivative(mu, kind)


@pytest.fixture
def layer() -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(11)
    return (
        torch.randn(B, D_IN, generator=generator),
        torch.randn(D_OUT, D_IN, generator=generator),
        torch.randn(D_OUT, generator=generator),
    )


def test_the_references_are_the_standard_equations(layer) -> None:
    """The specification, anchored: a prediction is a forward pass, and a step is
    gradient ascent on the free energy with the activation's own derivative."""
    mu, weight, bias = layer
    pre = mu @ weight.T + bias
    for kind in ACTIVATIONS:
        assert torch.allclose(
            pc_prediction(mu, weight, bias, kind), activation(pre, kind)
        )
        assert torch.allclose(
            pc_inference_step(mu, pre, LR, kind),
            mu + LR * (pre - mu) * activation_derivative(mu, kind),
        )


def test_the_derivative_is_the_derivative() -> None:
    """Finite differences, so the table cannot be a plausible-looking fiction."""
    x = torch.linspace(-3, 3, 64, dtype=torch.float64).unsqueeze(1).requires_grad_(True)
    for kind in ACTIVATIONS:
        step = torch.autograd.grad(activation(x, kind).sum(), x, create_graph=True)[0]
        exact = activation_derivative(x.detach().squeeze(1), kind)
        assert torch.allclose(
            step.squeeze(1).detach(), exact.to(torch.float64), atol=1e-6
        ), kind


def _kernel(kernel_name: str):
    """The triton kernel under test, or a skip when triton is unavailable."""
    from computronium.acceleration import pc_kernels

    kernel = getattr(pc_kernels, kernel_name, False)
    if kernel is False:
        pytest.skip("triton is unavailable, so the PC kernels were never defined")
    return kernel


def _grid(rows: int, cols: int, block: int = 16) -> tuple[int, int]:
    return (triton.cdiv(rows, block), triton.cdiv(cols, block))


def _tolerance(spec_parity, kind: str):
    """The spec's tolerance, with one recorded per-family decision.

    ``max_rel_diff`` is not a meaningful gate for an activation whose output
    crosses zero: GELU's negative tail lands within 2.1e-6 of zero, and any
    relative measure of that element is noise (measured 0.48). ``max_abs_diff``
    (1e-4) and ``min_cosine`` (0.999) still apply and are the criteria that
    matter. Recorded here rather than loosened globally, per §4.4.
    """
    if kind != "gelu":
        return spec_parity
    return replace(spec_parity, max_rel_diff=float("inf"))


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
@pytest.mark.parametrize("kind", ACTIVATIONS)
def test_pc_prediction_kernel_equals_its_specification(layer, kind: str) -> None:
    mu, weight, bias = layer
    mu, weight, bias = mu.cuda(), weight.cuda(), bias.cuda()
    pred = torch.zeros(B, D_OUT, device="cuda")
    _kernel("_pc_prediction_kernel")[_grid(B, D_OUT)](
        mu,
        weight,
        bias,
        pred,
        B,
        D_IN,
        D_OUT,
        ACTIVATIONS.index(kind),
        BLOCK_B=16,
        BLOCK_D=16,
    )
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    assert_parity(
        pred,
        pc_prediction(mu, weight, bias, kind),
        _tolerance(get("algorithm.pc").parity, kind),
    )


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
@pytest.mark.parametrize("kind", ACTIVATIONS)
def test_pc_error_update_kernel_equals_its_specification(kind: str) -> None:
    generator = torch.Generator().manual_seed(13)
    mu = torch.randn(B, D_OUT, generator=generator).cuda()
    pred = torch.randn(B, D_OUT, generator=generator).cuda()
    mu_new = torch.zeros_like(mu)
    eta = 0.05
    _kernel("_pc_error_update_kernel")[_grid(B, D_OUT)](
        mu, pred, mu_new, eta, ACTIVATIONS.index(kind), B, D_OUT, BLOCK_B=16, BLOCK_D=16
    )
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    assert_parity(
        mu_new, pc_inference_step(mu, pred, eta, kind), get("algorithm.pc").parity
    )
