"""§2.7: the activation derivative in the FA backward pass is taken at the
wrong point, and the file's own vocabulary is what hid it.

`FAKernelBackend.forward` returns `activations = [x, act(L0(x)), act(L1(x)), ...]`,
so `activations[i]` is the **input** to layer `i` and `activations[i + 1]` is the
**post-activation output** of layer `i`. The weight gradient
`batched_outer_product(h_prev, grad_h)` pairs `grad_h` with `activations[i]`,
which means `grad_h` must be d(loss)/d(**pre**-activation of layer i) — so the
feedback error has to be multiplied by f' evaluated at the pre-activation.

The pass multiplied by f' at `activations[i + 1]`, the post-activation. ReLU
and Tanh are invariant to that substitution (ReLU's sign is preserved, Tanh's
`1 - tanh(x)**2` *is* `1 - h**2` for `h = tanh(x)`), which is why two of the
four branches were right. SiLU and GELU are not: `f'(x) = sigma(x)(1 +
x(1-sigma(x)))` and `gelu'(x) = Phi(x) + x*phi(x)` are both functions of the
**pre**-activation, and neither can be evaluated from the post-activation value.

`backward_contrastive` read the same list with the opposite naming
(`free_pre = activations[i]`, `free_post = activations[i + 1]`), which was the
second half of the trap: the file asserted two incompatible contracts for one
value, and neither matched `forward`.

`forward` now records each layer's pre-activation, because the derivative has
to be taken there and for three of the four activations it cannot be recovered
from the value the activations list carries. The Tanh branch had to change with
it: `1 - x**2` was the *post*-activation form, and it was only right because
the caller passed the wrong argument.

These tests pin the contract numerically against autograd for all four
activations, so the two convention-sensitive ones cannot drift back.
"""

import pytest
import torch

from computronium.acceleration.fa_kernels import (
    FAKernelBackend,
)

ACTIVATIONS = {
    "relu": torch.nn.ReLU,
    "silu": torch.nn.SiLU,
    "tanh": torch.nn.Tanh,
    "gelu": torch.nn.GELU,
}

D_IN, D_HID, D_OUT, BATCH = 6, 5, 3, 8


def _activation_derivative(
    activation: torch.nn.Module, pre: torch.Tensor
) -> torch.Tensor:
    """f'(pre) via autograd, so the reference never restates the formula."""
    leaf = pre.detach().clone().requires_grad_(True)
    (grad,) = torch.autograd.grad(activation(leaf).sum(), leaf)
    return grad.detach()


def _fixture(
    activation: torch.nn.Module,
) -> tuple[FAKernelBackend, torch.Tensor, list[torch.Tensor]]:
    """A two-layer FA backend, its input, and the activations forward returns."""
    torch.manual_seed(0)
    backend = FAKernelBackend()
    backend.set_model_ref(
        [torch.nn.Linear(D_IN, D_HID), torch.nn.Linear(D_HID, D_OUT)],
        activation=activation,
    )
    x = torch.randn(BATCH, D_IN)
    _, activations = backend.forward(x)
    return backend, x, activations


@pytest.mark.parametrize("name", sorted(ACTIVATIONS))
def test_backward_differentiates_at_the_pre_activation(name: str) -> None:
    """grad_h must be (feedback error) * f'(pre-activation), not f'(post)."""
    activation = ACTIVATIONS[name]()
    backend, x, activations = _fixture(activation)

    error = torch.randn(BATCH, D_OUT)
    grads = backend.backward(activations, error)

    pre_0 = backend._layers[0](x)
    feedback_error = error @ backend._feedback_weights[1]
    expected_grad_h = feedback_error * _activation_derivative(activation, pre_0)

    torch.testing.assert_close(
        grads["layers.0.weight"],
        (expected_grad_h.T @ x) / BATCH,
        msg=lambda m: f"{name}: FA backward differentiates at the wrong point\n{m}",
    )


@pytest.mark.parametrize("name", sorted(ACTIVATIONS))
def test_only_relu_is_recoverable_from_the_post_activation(name: str) -> None:
    """Only ReLU's derivative is a function of its own output.

    This is *why* the defect survived so long. Evaluated at the post-activation
    value, the Tanh branch computes `1 - h**2` — which is exactly `1 - tanh(x)**2`
    when `h = tanh(x)`, and ReLU's sign survives too. So two of the four
    branches returned correct gradients by accident, and the two that did not
    (SiLU, GELU) were the ones nobody ran. A property of the activations, not of
    the implementation: it stays true after the fix and says which branches a
    future argument change would silently break.
    """
    activation = ACTIVATIONS[name]()
    backend, x, _ = _fixture(activation)
    pre = backend._layers[0](x)
    at_pre = _activation_derivative(activation, pre)
    at_post = _activation_derivative(activation, activation(pre))
    assert torch.allclose(at_pre, at_post) == (name == "relu"), (
        f"{name}: f'(x) and f'(f(x)) changed relationship; the argument this "
        "backward pass may be handed is only interchangeable for relu"
    )


def test_activations_layout_is_input_then_output() -> None:
    """`activations[i]` is layer i's input, `activations[i + 1]` its output.

    The backward pass's correctness rests entirely on this layout, and
    `backward_contrastive` historically read it the other way round.
    """
    activation = torch.nn.ReLU()
    backend, x, activations = _fixture(activation)

    assert len(activations) == len(backend._layers) + 1
    torch.testing.assert_close(activations[0], x)
    last = len(backend._layers) - 1
    for i, layer in enumerate(backend._layers):
        pre = layer(activations[i])
        expected = pre if i == last else activation(pre)
        torch.testing.assert_close(activations[i + 1], expected)
    assert not torch.equal(activations[1], backend._layers[0](x)), (
        "activations[i + 1] is the POST-activation output, so the pre-activation "
        "f' is taken at is not recoverable from it and must be retained separately"
    )


def test_backward_without_forward_raises_instead_of_guessing() -> None:
    """The pre-activations cannot be synthesised, so the dependency is explicit.

    Silently falling back to the post-activation is exactly the defect this
    file exists to prevent, so a `backward` with no recorded `forward` must
    fail loudly rather than return plausible-looking gradients.
    """
    torch.manual_seed(0)
    backend = FAKernelBackend()
    backend.set_model_ref(
        [torch.nn.Linear(D_IN, D_HID), torch.nn.Linear(D_HID, D_OUT)],
        activation=torch.nn.GELU(),
    )
    activations = [torch.randn(BATCH, D_IN), torch.randn(BATCH, D_HID)]
    activations.append(torch.randn(BATCH, D_OUT))
    with pytest.raises(RuntimeError, match="pre-activations"):
        backend.backward(activations, torch.randn(BATCH, D_OUT))
