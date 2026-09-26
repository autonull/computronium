"""The contrastive-update specification, written before the kernels (TODO36 §4.5).

Seven kernels in the tree compute a maths nobody wrote down anywhere except in the
kernel itself, so there is no oracle to check them against. The rule this file
follows is §4.5's: **write the torch expression first, as a test, and do not port
from the kernel to the test.** The reference is derived from the maths the kernels
name — a difference of batched outer products, scaled by a learning rate and a
nudge strength — and is verified against an explicit loop, so the reference itself
is anchored to something other than the kernel.

One expression, two kernels, because they are the same maths:

* ``_ff_contrastive_update_kernel`` — ``dW = lr * (pos - neg) / B``; the FF
  pilot the plan names, whose sibling ``_ff_goodness_kernel`` already compiles and
  matches to 1.9e-5.
* ``_pc_contrastive_update_kernel`` — the same difference in the opposite
  (nudged − free) order, divided by the nudge strength ``beta``, which is
  `contrastive_primitives.contrastive_delta`'s convention.
"""

import pytest
import torch

from computronium.acceleration.contrastive_primitives import batched_outer_product

B, D_IN, D_OUT = 8, 16, 32


def contrastive_delta_ref(
    free_pre: torch.Tensor,
    free_post: torch.Tensor,
    other_pre: torch.Tensor,
    other_post: torch.Tensor,
    lr: float,
    divisor: float = 1.0,
) -> torch.Tensor:
    """The expression every contrastive-update kernel in this file computes.

    ``dW = lr * (other - free) / divisor``, where each term is a batched outer
    product averaged over the batch. FF passes ``(pos, neg)``; PC passes
    ``(nudged, free)`` with ``divisor=beta``.

    Args:
        free_pre: ``[B, D_in]`` layer input, subtracted.
        free_post: ``[B, D_out]`` layer output, subtracted.
        other_pre: ``[B, D_in]`` layer input, added.
        other_post: ``[B, D_out]`` layer output, added.
        lr: learning rate.
        divisor: nudge strength; ``1.0`` when the kernel has no ``beta``.

    Returns:
        ``[D_out, D_in]`` weight delta.
    """
    return (
        lr
        * (
            batched_outer_product(other_pre, other_post)
            - batched_outer_product(free_pre, free_post)
        )
        / divisor
    )


def ff_contrastive_delta(
    pre_pos: torch.Tensor,
    post_pos: torch.Tensor,
    pre_neg: torch.Tensor,
    post_neg: torch.Tensor,
    lr: float,
) -> torch.Tensor:
    """The expression the FF contrastive kernel is meant to equal.

    A layer's weight update is the difference between the positive and negative
    phases' batched outer products, averaged over the batch and scaled by the
    learning rate:

        dW = lr * ( (post_pos.T @ pre_pos) / B - (post_neg.T @ pre_neg) / B )

    Args:
        pre_pos: ``[B, D_in]`` layer input on the positive phase.
        post_pos: ``[B, D_out]`` layer output on the positive phase.
        pre_neg: ``[B, D_in]`` layer input on the negative phase.
        post_neg: ``[B, D_out]`` layer output on the negative phase.
        lr: learning rate.

    Returns:
        ``[D_out, D_in]`` weight delta.
    """
    return contrastive_delta_ref(pre_neg, post_neg, pre_pos, post_pos, lr)


def _loop_reference(
    pre_pos: torch.Tensor,
    post_pos: torch.Tensor,
    pre_neg: torch.Tensor,
    post_neg: torch.Tensor,
    lr: float,
) -> torch.Tensor:
    """The same expression written out, as the anchor the reference is checked against."""
    delta = torch.zeros(D_OUT, D_IN, dtype=torch.float64)
    for b in range(pre_pos.shape[0]):
        delta += torch.outer(post_pos[b].double(), pre_pos[b].double())
        delta -= torch.outer(post_neg[b].double(), pre_neg[b].double())
    return (lr * delta / pre_pos.shape[0]).float()


@pytest.fixture
def phases() -> tuple[torch.Tensor, ...]:
    generator = torch.Generator().manual_seed(7)
    return tuple(
        torch.randn(B, width, generator=generator)
        for width in (D_IN, D_OUT, D_IN, D_OUT)
    )


def test_the_reference_matches_an_explicit_loop(phases) -> None:
    """The specification is anchored to a loop, not to the kernel."""
    lr = 0.01
    assert torch.allclose(
        ff_contrastive_delta(*phases, lr), _loop_reference(*phases, lr), atol=1e-6
    )


def test_the_reference_is_the_difference_of_the_two_phases(phases) -> None:
    """Zero learning rate is zero update; a zero negative phase is one phase."""
    pre_pos, post_pos, pre_neg, post_neg = phases
    zero_neg = torch.zeros_like(post_neg)
    assert torch.allclose(
        ff_contrastive_delta(pre_pos, post_pos, pre_neg, post_neg, 0.0),
        torch.zeros(D_OUT, D_IN),
        atol=0.0,
    )
    assert torch.allclose(
        ff_contrastive_delta(pre_pos, post_pos, pre_pos, zero_neg, 1.0),
        batched_outer_product(pre_pos, post_pos),
        atol=1e-6,
    )


def _kernel(pre_pos, post_pos, pre_neg, post_neg, lr: float) -> torch.Tensor:
    import triton

    from computronium.acceleration import ff_kernels

    kernel = ff_kernels._ff_contrastive_update_kernel  # ruff: ignore[private-member-access]  (the rung under test)
    if kernel is False:
        pytest.skip("triton is unavailable, so the FF kernel was never defined")
    delta = torch.empty(D_OUT, D_IN, device=pre_pos.device, dtype=torch.float32)
    grid = (triton.cdiv(D_OUT, 16), triton.cdiv(D_IN, 16))  # (out, in): delta's layout
    kernel[grid](
        pre_pos,
        post_pos,
        pre_neg,
        post_neg,
        delta,
        B,
        D_IN,
        D_OUT,
        lr,
        BLOCK_IN=16,
        BLOCK_OUT=16,
    )
    return delta


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
def test_the_ff_contrastive_kernel_equals_its_specification(phases) -> None:
    """§4.5's done-when, for the pilot: the kernel matches the expression, or says why not."""
    args = tuple(t.cuda() for t in phases)
    expected = ff_contrastive_delta(*args, 0.01)
    got = _kernel(*args, 0.01)
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    assert_parity(got, expected, get("algorithm.ff").parity)


def _pc_kernel(pre_free, post_free, pre_nudged, post_nudged, lr: float, beta: float):
    import triton

    from computronium.acceleration import pc_kernels

    kernel = pc_kernels._pc_contrastive_update_kernel  # ruff: ignore[private-member-access]  (the rung under test)
    if kernel is False:
        pytest.skip("triton is unavailable, so the PC kernel was never defined")
    delta = torch.empty(D_OUT, D_IN, device=pre_free.device, dtype=torch.float32)
    kernel[triton.cdiv(D_OUT, 16), triton.cdiv(D_IN, 16)](
        pre_free,
        post_free,
        pre_nudged,
        post_nudged,
        delta,
        B,
        D_IN,
        D_OUT,
        beta,
        lr,
        BLOCK_IN=16,
        BLOCK_OUT=16,
    )
    return delta


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
def test_the_pc_contrastive_kernel_equals_the_same_specification(phases) -> None:
    """PC's rung is the FF maths in the other order, with the nudge strength divided out."""
    pre_pos, post_pos, pre_neg, post_neg = (t.cuda() for t in phases)
    lr, beta = 0.01, 0.5
    expected = contrastive_delta_ref(pre_pos, post_pos, pre_neg, post_neg, lr, beta)
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    assert_parity(
        _pc_kernel(pre_pos, post_pos, pre_neg, post_neg, lr, beta),
        expected,
        get("algorithm.pc").parity,
    )
