"""The STDP specification, written before the kernels (TODO36 §4.5).

The last two triton kernels in the tree that do not compile, and the two whose
batch axis is never read. Both compute spike-timing correlation, and the torch
twin of the plain one already exists as
``contrastive_primitives.stdp_update``; the contrastive one has no twin, so this
file writes it.

The composition is the same one the PC and Hebbian rungs use, which is the point:
a contrastive learning rule is its phase term, differenced and divided by the
nudge strength. Here the phase term is a spike-timing correlation rather than a
batched outer product, and nothing else about the composition changes.

    dW = (stdp(nudged) - stdp(free)) / beta        (contrastive STDP)
    stdp = A_plus * ltp - A_minus * ltd            (plain STDP)
    ltp[o, i] = sum_{b,t} post[b, o, t+1] * pre[b, i, t]
    ltd[o, i] = sum_{b,t} post[b, o, t  ] * pre[b, i, t+1]

The three defects the specifications found, all in the same two kernels:

1. ``tl.dot(post_t, pre_t)`` is a rank-1 outer product with a contraction of
   length 1, which ``tl.dot`` refuses — the reason neither kernel compiled. The
   fix is the same broadcast product the rest of this family received.
2. **The batch axis is never read.** The loads address ``offs * T + t`` with no
   batch stride, so both kernels computed one sample's correlation and called it
   the mean. The torch twin sums over the batch.
3. **The plain kernel's two branches are each other's comment.** The branch
   labelled "LTP: post at t+1 with pre at t" loads post at ``t`` and pre at
   ``t+1``; the branch labelled LTD does the reverse. So the amplitudes were
   applied to the wrong terms and a positive-pair update became a negative-pair
   one. Swapping the two branches' outcomes changes the sign of every weight
   delta while leaving the shapes, the dtypes and the compiled-ness untouched.

`N_pre`, `N_post` and `T` are deliberately not multiples of `BLOCK`, for the
reason the rest of this family shares: a clean multiple hides a wrong grid.
"""

from __future__ import annotations

import pytest
import torch

from computronium.acceleration.contrastive_primitives import (
    contrastive_delta,
    stdp_update,
)

B, N_PRE, N_POST, T = 6, 24, 20, 8
BLOCK = 16
A_PLUS, A_MINUS, BETA = 0.01, 0.02, 0.5


def ltp_ref(pre: torch.Tensor, post: torch.Tensor) -> torch.Tensor:
    """Preceding-post potentiation: post fires at ``t+1``, pre at ``t``."""
    return torch.einsum("bot,bit->oi", post[:, :, 1:], pre[:, :, :-1])


def ltd_ref(pre: torch.Tensor, post: torch.Tensor) -> torch.Tensor:
    """Post-depression: post fires at ``t``, pre at ``t+1``."""
    return torch.einsum("bot,bit->oi", post[:, :, :-1], pre[:, :, 1:])


def stdp_ref(
    pre: torch.Tensor, post: torch.Tensor, a_plus: float, a_minus: float
) -> torch.Tensor:
    """The phase term every STDP rung here computes, in weight orientation."""
    return a_plus * ltp_ref(pre, post) - a_minus * ltd_ref(pre, post)


def _loop_reference(
    pre: torch.Tensor, post: torch.Tensor, a_plus: float, a_minus: float
) -> torch.Tensor:
    """The same expression one sample and one time step at a time."""
    delta = torch.zeros(N_POST, N_PRE, dtype=torch.float64)
    for b in range(pre.shape[0]):
        for t in range(pre.shape[2] - 1):
            delta += a_plus * torch.outer(
                post[b, :, t + 1].double(), pre[b, :, t].double()
            )
            delta -= a_minus * torch.outer(
                post[b, :, t].double(), pre[b, :, t + 1].double()
            )
    return delta.float()


@pytest.fixture
def spikes() -> tuple[torch.Tensor, torch.Tensor]:
    """Binary pre/post spike trains, ``[B, N, T]``."""
    generator = torch.Generator().manual_seed(17)
    return (
        (torch.rand(B, N_PRE, T, generator=generator) < 0.3).float(),
        (torch.rand(B, N_POST, T, generator=generator) < 0.3).float(),
    )


def test_the_reference_matches_an_explicit_loop(spikes) -> None:
    """The specification is anchored to a loop, not to a kernel."""
    pre, post = spikes
    assert torch.allclose(
        stdp_ref(pre, post, A_PLUS, A_MINUS),
        _loop_reference(pre, post, A_PLUS, A_MINUS),
        atol=1e-5,
    )


def test_the_reference_is_the_torch_twin(spikes) -> None:
    """The rung exists to replace `contrastive_primitives.stdp_update`."""
    pre, post = spikes
    assert torch.allclose(
        stdp_ref(pre, post, A_PLUS, A_MINUS),
        stdp_update(pre, post, A_plus=A_PLUS, A_minus=A_MINUS),
        atol=0.0,
    )


def test_the_contrastive_reference_is_the_difference_of_two_phases(spikes) -> None:
    """The composition is the one the PC and Hebbian rungs use.

    ``contrastive_delta`` is ``(nudged - free) / beta`` and
    ``contrastive_hebbian_update`` is its composition with a batched outer product
    as the phase term. The SNN contrastive rung is the same composition with a
    spike-timing correlation as the phase term, which is why the spec is written
    once and shared: two properties say so, without arithmetic.
    """
    pre, post = spikes
    free = stdp_ref(pre, post, A_PLUS, A_MINUS)
    assert torch.allclose(
        contrastive_delta(free, free, BETA), torch.zeros(N_POST, N_PRE), atol=0.0
    )
    doubled = contrastive_delta(free, 2 * free, BETA)
    assert torch.allclose(doubled, free / BETA, atol=1e-5)


def test_a_silent_train_is_a_zero_update(spikes) -> None:
    """Both correlations need both trains, so silencing either one zeroes the phase.

    Neither STDP kernel read the batch, so "the trains" is a statement about the
    whole ``[B, N, T]`` block and this is the coarsest form of it: an all-zero
    phase is a zero update, whatever the batch size.
    """
    pre, post = spikes
    assert torch.allclose(
        stdp_ref(pre, torch.zeros_like(post), A_PLUS, A_MINUS),
        torch.zeros(N_POST, N_PRE),
        atol=0.0,
    )
    assert torch.allclose(
        stdp_ref(torch.zeros_like(pre), post, A_PLUS, A_MINUS),
        torch.zeros(N_POST, N_PRE),
        atol=0.0,
    )


def test_the_batch_axis_is_not_optional(spikes) -> None:
    """The defect both kernels carried, as a property of the specification.

    Neither kernel addressed the batch, so each computed one sample's correlation
    and returned it for the whole batch. The correlation is additive over the
    batch, so a specification that summed only the first sample would pass such a
    kernel and fail this.
    """
    pre, post = spikes
    per_sample = torch.stack([
        stdp_ref(pre[b : b + 1], post[b : b + 1], A_PLUS, A_MINUS) for b in range(B)
    ]).sum(dim=0)
    assert torch.allclose(stdp_ref(pre, post, A_PLUS, A_MINUS), per_sample, atol=1e-5)
    assert not torch.allclose(
        per_sample, stdp_ref(pre[:1], post[:1], A_PLUS, A_MINUS), atol=1e-5
    )


def test_ltp_and_ltd_are_different_quantities(spikes) -> None:
    """The defect the plain kernel carried, as a property of the specification.

    The two branches loaded each other's time step, so the amplitudes landed on
    the wrong terms. On binary spikes the two correlations are equal only in
    expectation; on this fixture they are not equal at all, which is what makes
    the swap detectable at all.
    """
    pre, post = spikes
    assert not torch.allclose(ltp_ref(pre, post), ltd_ref(pre, post))


def _grid():
    from computronium.acceleration.grid import grid_2d

    return grid_2d(N_POST, N_PRE, BLOCK, BLOCK)


def _run_stdp(pre, post, a_plus: float, a_minus: float) -> torch.Tensor:
    import triton

    from computronium.acceleration.snn_kernels import _stdp_update_kernel

    if _stdp_update_kernel is False:
        pytest.skip("triton is unavailable, so the STDP kernel was never defined")
    delta = torch.empty(N_POST, N_PRE, device=pre.device, dtype=torch.float32)
    _stdp_update_kernel[_grid()](
        pre,
        post,
        delta,
        B,
        N_PRE,
        N_POST,
        T,
        a_plus,
        a_minus,
        BLOCK_PRE=BLOCK,
        BLOCK_POST=BLOCK,
        BLOCK_T=triton.next_power_of_2(T),
    )
    return delta


def _run_contrastive_stdp(pre_f, post_f, pre_n, post_n, beta: float) -> torch.Tensor:
    import triton

    from computronium.acceleration.snn_kernels import _contrastive_stdp_kernel

    if _contrastive_stdp_kernel is False:
        pytest.skip("triton is unavailable, so the STDP kernel was never defined")
    delta = torch.empty(N_POST, N_PRE, device=pre_f.device, dtype=torch.float32)
    _contrastive_stdp_kernel[_grid()](
        pre_f,
        post_f,
        pre_n,
        post_n,
        delta,
        B,
        N_PRE,
        N_POST,
        T,
        A_PLUS,
        A_MINUS,
        beta,
        BLOCK_PRE=BLOCK,
        BLOCK_POST=BLOCK,
        BLOCK_T=triton.next_power_of_2(T),
    )
    return delta


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
def test_the_stdp_kernel_equals_its_specification(spikes) -> None:
    """§4.5's done-when, for the plain rung."""
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    pre, post = (t.cuda() for t in spikes)
    assert_parity(
        _run_stdp(pre, post, A_PLUS, A_MINUS),
        stdp_ref(pre, post, A_PLUS, A_MINUS),
        get("algorithm.spiking_snn").parity,
    )


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
def test_the_contrastive_stdp_kernel_equals_its_specification(spikes) -> None:
    """§4.5's done-when, for the contrastive rung."""
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    pre, post = (t.cuda() for t in spikes)
    free = stdp_ref(pre, post, A_PLUS, A_MINUS)
    nudged = stdp_ref(pre + 0.5, post + 0.5, A_PLUS, A_MINUS)
    assert_parity(
        _run_contrastive_stdp(pre, post, pre + 0.5, post + 0.5, BETA),
        contrastive_delta(free, nudged, BETA),
        get("algorithm.spiking_snn").parity,
    )
