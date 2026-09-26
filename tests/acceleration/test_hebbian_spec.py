"""The Hebbian-update specification, written before the kernels (TODO36 §4.5).

The contrastive half of the hebbian family is specified in
``test_contrastive_update_spec.py``; this file covers the two rungs that have no
``beta`` in them and so are not a difference of anything:

* ``_hebbian_update_kernel`` — a single Hebbian step with Oja's subtraction,
  ``dW = lr * (batchmean(post ⊗ pre) - batchmean(post²) ⊗ W)``.
* ``_three_factor_hebbian_kernel`` — the same outer product with a
  per-sample third factor folded into the post-synaptic side,
  ``dW = lr * batchmean(mod ⊙ post ⊗ pre)``.

Both references are written from the maths, anchored to an explicit loop, and
then cross-checked against each other: with an all-ones modulator and Oja's term
switched off, the two rungs must agree exactly. That cross-check is what ties the
pair to one specification rather than two, and it is why one table serves both.

The shapes here are deliberately not multiples of ``BLOCK`` (48 and 32 against
16). Three of this family's five kernels had the *transposed* grid — program 0
walking the input axis while the store walked the output axis — and the failure
is a region of the output that is never written: no error, no partial result. A
shape that is a clean multiple hides it; these do not.
"""

from __future__ import annotations

import pytest
import torch

B, D_IN, D_OUT, BLOCK = 8, 48, 32, 16
LR = 0.01


def hebbian_delta_ref(
    pre: torch.Tensor, post: torch.Tensor, weight: torch.Tensor, lr: float
) -> torch.Tensor:
    """The expression ``_hebbian_update_kernel`` is meant to equal.

    A Hebbian layer grows the outer product of its pre- and post-synaptic
    activity; Oja's rule subtracts the current weights, scaled by the mean
    post-synaptic energy of the *same* batch:

        dW = lr * ( (post.T @ pre) / B - (post**2).mean(dim=0)[:, None] * W )

    Args:
        pre: ``[B, D_in]`` layer input.
        post: ``[B, D_out]`` layer output.
        weight: ``[D_out, D_in]`` the current weights, which Oja's term reads.
        lr: learning rate.

    Returns:
        ``[D_out, D_in]`` weight delta.
    """
    return lr * (
        (post.T @ pre) / post.shape[0] - post.pow(2).mean(dim=0)[:, None] * weight
    )


def three_factor_delta_ref(
    pre: torch.Tensor, post: torch.Tensor, modulator: torch.Tensor, lr: float
) -> torch.Tensor:
    """The expression ``_three_factor_hebbian_kernel`` is meant to equal.

    A three-factor rule gates the Hebbian outer product with a neuromodulatory
    signal, which is what makes it *three*-factor: the pre- and post-synaptic
    activities are two, the modulator is the third.

        dW = lr * ( (mod ⊙ post).T @ pre ) / B

    Args:
        pre: ``[B, D_in]`` layer input.
        post: ``[B, D_out]`` layer output.
        modulator: ``[B, D_out]`` the third factor, one scalar per sample and
            output unit.
        lr: learning rate.

    Returns:
        ``[D_out, D_in]`` weight delta.
    """
    return lr * ((modulator * post).T @ pre) / post.shape[0]


def _loop_reference(
    post: torch.Tensor, pre: torch.Tensor, weight: torch.Tensor, lr: float
) -> torch.Tensor:
    """The hebbian expression written out sample by sample, as its anchor."""
    delta = torch.zeros(D_OUT, D_IN, dtype=torch.float64)
    for b in range(pre.shape[0]):
        delta += torch.outer(post[b].double(), pre[b].double())
    delta /= pre.shape[0]
    return (
        lr * (delta - post.double().pow(2).mean(dim=0)[:, None] * weight.double())
    ).float()


@pytest.fixture
def hebbian_inputs() -> tuple[torch.Tensor, ...]:
    """``(pre, post, weight, modulator)``."""
    generator = torch.Generator().manual_seed(11)
    pre = torch.randn(B, D_IN, generator=generator)
    post = torch.randn(B, D_OUT, generator=generator)
    weight = torch.randn(D_OUT, D_IN, generator=generator)
    modulator = torch.rand(B, D_OUT, generator=generator)
    return pre, post, weight, modulator


def test_the_reference_matches_an_explicit_loop(hebbian_inputs) -> None:
    """The specification is anchored to a loop, not to a kernel."""
    pre, post, weight, _ = hebbian_inputs
    assert torch.allclose(
        hebbian_delta_ref(pre, post, weight, LR),
        _loop_reference(post, pre, weight, LR),
        atol=1e-6,
    )


def test_the_hebbian_reference_is_the_torch_path_it_replaces(hebbian_inputs) -> None:
    """The reference must not drift from ``HebbianKernelBackend.hebbian_update``."""
    from computronium.acceleration.hebbian_kernels import HebbianKernelBackend
    from computronium.acceleration.kernel_backend import (
        AlgorithmFamily,
        HardwareTarget,
        KernelConfig,
    )

    pre, post, weight, _ = hebbian_inputs
    backend = HebbianKernelBackend()
    backend.initialize(
        KernelConfig(
            algorithm=AlgorithmFamily.HEBBIAN,
            hardware=HardwareTarget.CPU,
            extra={"use_oja": True, "learning_rate": LR},
        )
    )
    backend.set_model_ref([torch.nn.Linear(D_IN, D_OUT)])
    backend._layers[0].weight.data.copy_(weight)  # ruff: ignore[private-member-access]
    got = backend.hebbian_update(pre, post, 0)["layers.0.weight"]
    assert torch.allclose(hebbian_delta_ref(pre, post, weight, LR), got, atol=1e-6)
    backend.initialize(
        KernelConfig(
            algorithm=AlgorithmFamily.HEBBIAN,
            hardware=HardwareTarget.CPU,
            extra={"use_oja": False, "learning_rate": LR},
        )
    )
    backend.set_model_ref([torch.nn.Linear(D_IN, D_OUT)])
    plain = backend.hebbian_update(pre, post, 0)["layers.0.weight"]
    assert torch.allclose(plain, LR * (post.T @ pre) / B, atol=1e-6)


def test_the_references_agree_with_each_other(hebbian_inputs) -> None:
    """A unit modulator is the two-factor rule; that is what ties this pair together.

    This is the property that makes ``hebbian_delta_ref`` and
    ``three_factor_delta_ref`` one specification rather than two plausible
    ones, and it is checked on the *references*, so a kernel cannot satisfy it by
    sharing a bug with its sibling.
    """
    pre, post, weight, _ = hebbian_inputs
    ones = torch.ones(B, D_OUT)
    plain = hebbian_delta_ref(pre, post, weight, LR)
    assert torch.allclose(
        three_factor_delta_ref(pre, post, ones, LR),
        plain + LR * post.pow(2).mean(dim=0)[:, None] * weight,
        atol=1e-6,
    )
    assert torch.allclose(
        three_factor_delta_ref(pre, post, ones, LR),
        three_factor_delta_ref(pre, post, torch.full_like(post, 0.5), LR) * 2.0,
        atol=1e-6,
    )
    assert torch.allclose(
        three_factor_delta_ref(pre, post, torch.zeros_like(post), LR),
        torch.zeros(D_OUT, D_IN),
        atol=0.0,
    )


def _grid():
    import triton

    # Row-major over delta's [D_out, D_in] layout: program 0 walks the output axis.
    return (triton.cdiv(D_OUT, BLOCK), triton.cdiv(D_IN, BLOCK))


def _run_hebbian(pre, post, weight, lr, use_oja: bool) -> torch.Tensor:
    from computronium.acceleration.hebbian_kernels import _hebbian_update_kernel

    if _hebbian_update_kernel is False:
        pytest.skip("triton is unavailable, so the hebbian kernel was never defined")
    delta = torch.empty(D_OUT, D_IN, device=pre.device, dtype=torch.float32)
    _hebbian_update_kernel[_grid()](
        pre,
        post,
        weight,
        delta,
        B,
        D_IN,
        D_OUT,
        lr,
        use_oja,
        BLOCK_IN=BLOCK,
        BLOCK_OUT=BLOCK,
    )
    return delta


def _run_three_factor(pre, post, modulator, lr) -> torch.Tensor:
    from computronium.acceleration.hebbian_kernels import _three_factor_hebbian_kernel

    if _three_factor_hebbian_kernel is False:
        pytest.skip("triton is unavailable, so the hebbian kernel was never defined")
    delta = torch.empty(D_OUT, D_IN, device=pre.device, dtype=torch.float32)
    _three_factor_hebbian_kernel[_grid()](
        pre,
        post,
        modulator,
        delta,
        B,
        D_IN,
        D_OUT,
        lr,
        BLOCK_IN=BLOCK,
        BLOCK_OUT=BLOCK,
    )
    return delta


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
@pytest.mark.parametrize("use_oja", (False, True), ids=("plain", "oja"))
def test_the_hebbian_kernel_equals_its_specification(
    use_oja: bool, hebbian_inputs
) -> None:
    """§4.5's done-when, for the two-factor rung."""
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    pre, post, weight, _ = (t.cuda() for t in hebbian_inputs)
    expected = hebbian_delta_ref(pre, post, weight, LR)
    if not use_oja:
        expected = LR * (post.T @ pre) / B
    assert_parity(
        _run_hebbian(pre, post, weight, LR, use_oja),
        expected,
        get("algorithm.hebbian").parity,
    )


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
def test_the_three_factor_kernel_equals_its_specification(hebbian_inputs) -> None:
    """§4.5's done-when, for the three-factor rung."""
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    pre, post, _, modulator = (t.cuda() for t in hebbian_inputs)
    assert_parity(
        _run_three_factor(pre, post, modulator, LR),
        three_factor_delta_ref(pre, post, modulator, LR),
        get("algorithm.hebbian").parity,
    )


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
def test_the_two_hebbian_kernels_agree_with_each_other(hebbian_inputs) -> None:
    """The pair's cross-check, on the kernels: unit modulator, Oja off.

    Two independent triton rungs of one specification, agreeing to the last bit.
    """
    pre, post, _, modulator = (t.cuda() for t in hebbian_inputs)
    ones = torch.ones_like(modulator)
    assert torch.equal(
        _run_three_factor(pre, post, ones, LR), _run_hebbian(pre, post, ones, LR, False)
    )
