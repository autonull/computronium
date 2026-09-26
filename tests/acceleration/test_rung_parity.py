"""Parity between adjacent rungs, for every rung that compiles (TODO36 §4.4).

`test_all_implementations.test_kernel_parity` already checks rung 1 against rung 0
for all 64 specs, at the level of `step(case)`. This file checks the level below
that: the *kernel entry points* themselves, triton against the torch expression
they replace, with the tolerance the owning spec already carries. Two
implementations of one maths, each checked against the other, is the product
(§0.2); this is the second half of the pair, where the two implementations are
literally the same function in two languages.

Kernels that do not compile have no rung to compare — they are §4.5's work, and
`availability.compile_state` is what decides membership here, so this file cannot
quietly pass a family whose rung is not running.
"""

import pytest
import torch

from computronium.acceleration.availability import CompileState, compile_state, fixtures
from computronium.acceleration.parity import assert_parity
from computronium.acceleration.registry import get

DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])


def _spec_parity(spec_id: str):
    return get(spec_id).parity


def _state(name: str) -> CompileState:
    fixture = next(f for f in fixtures() if f.name == name)
    return compile_state(fixture).state


requires_fa = pytest.mark.skipif(
    _state("fa_kernels._fa_batched_outer_kernel") is not CompileState.COMPILES,
    reason="the fa triton rung does not compile here",
)
requires_pcalm = pytest.mark.skipif(
    _state("pcalm_kernels._FUSED_UPDATE_KERNEL") is not CompileState.COMPILES,
    reason="the pcalm triton rung does not compile here",
)
requires_cuda = pytest.mark.skipif(
    not torch.cuda.is_available(), reason="no CUDA device to run a triton rung on"
)


@requires_cuda
@requires_fa
@pytest.mark.parametrize("device", DEVICES)
def test_fa_feedback_projection_matches_the_matmul_it_replaces(device: str) -> None:
    from computronium.acceleration.fa_kernels import fa_feedback_projection_triton

    error = torch.randn(8, 16, device=device)
    feedback = torch.randn(16, 32, device=device)
    assert_parity(
        fa_feedback_projection_triton(error, feedback),
        error @ feedback,
        _spec_parity("primitive.credit_assignment.local_goodness"),
    )


@requires_cuda
@requires_fa
@pytest.mark.parametrize("device", DEVICES)
def test_fa_batched_outer_matches_the_outer_product_it_replaces(device: str) -> None:
    from computronium.acceleration.fa_kernels import fa_batched_outer_triton

    pre = torch.randn(8, 16, device=device)
    post = torch.randn(8, 32, device=device)
    assert_parity(
        fa_batched_outer_triton(pre, post),
        (post.T @ pre) / pre.shape[0],
        _spec_parity("primitive.credit_assignment.random_projections"),
    )


@requires_pcalm
@pytest.mark.parametrize("device", DEVICES)
def test_pcalm_fused_update_matches_the_eager_dual_primal_update(device: str) -> None:
    from computronium.acceleration.pcalm_kernels import (
        _eager_dual_primal_update,
        fused_dual_primal_update,
    )

    h, c, lam, topdown = (torch.randn(256, device=device) for _ in range(4))
    step_size, rho, alpha = 0.1, 1.0, 0.5
    fused = fused_dual_primal_update(h, c, lam, topdown, step_size, rho, alpha)
    eager = _eager_dual_primal_update(h, c, lam, topdown, step_size, rho, alpha)
    tolerance = _spec_parity("primitive.state_dynamics.pc_alm_settling")
    assert_parity(fused[0], eager[0], tolerance)
    assert_parity(fused[1], eager[1], tolerance)


@requires_cuda
@pytest.mark.xfail(
    strict=True,
    reason=(
        "known divergence, TODO36 §4.5: the triton rung runs the naive "
        "0.5*X(3I - X^T X) iteration while the torch rung is newton_schulz5's "
        "quintic, which replaced it because the naive form under-converges. "
        "The old test compared the triton rung against a copy of its own "
        "algorithm and passed; this one compares it to the rung it accelerates."
    ),
)
@pytest.mark.parametrize("device", DEVICES)
def test_muon_orthogonalize_matches_the_torch_newton_schulz(device: str) -> None:
    from computronium.acceleration.triton_kernels import MEP_TritonOps
    from computronium.core.optimization.strategies import MuonUpdate

    matrix = torch.randn(64, 48, device=device)
    assert_parity(
        MEP_TritonOps.muon_orthogonalize(matrix, ns_steps=5),
        MuonUpdate()._newton_schulz(matrix, 5),  # ruff: ignore[private-member-access]  (the torch rung under test)
        _spec_parity("primitive.parameter_update.muon"),
    )


@requires_cuda
@pytest.mark.parametrize("device", DEVICES)
def test_eqprop_step_matches_the_euler_tanh_it_replaces(device: str) -> None:
    from computronium.acceleration.triton_kernels import TritonEqPropOps

    h = torch.randn(256, device=device)
    pre_act = torch.randn(256, device=device)
    bias = torch.randn(16, device=device)
    alpha = 0.5
    assert_parity(
        TritonEqPropOps.step(h, pre_act, alpha, bias),
        (1 - alpha) * h + alpha * torch.tanh(pre_act + bias.repeat(16)),
        get("primitive.state_dynamics.energy_minimization").parity,
    )


#: Compiling kernels whose family no spec reaches. `_ff_goodness_kernel` is
#: correct today (TODO36 §2) and nothing verifies it, because no `kernel.py`
#: imports `ff_kernels`; `snn` likewise. Recorded rather than failed, because the
#: fix is §4.5/§4.6 (recover the spec, wire the rung), never to delete a kernel (§3).
UNWIRED_BUT_COMPILING: frozenset[str] = frozenset({"ff", "snn"})


def test_a_compiling_kernel_has_either_a_spec_or_a_recorded_reason() -> None:
    """A compiling kernel with no spec above it is a rung nobody verifies."""
    from computronium.acceleration.registry import all_specs
    from computronium.acceleration.status import family_of

    families = {family_of(spec) for spec in all_specs()}
    compiling = {
        report.family
        for report in (compile_state(f) for f in fixtures())
        if report.state is CompileState.COMPILES
    }
    assert compiling - families == UNWIRED_BUT_COMPILING, (
        "a newly compiling kernel with no spec above it: wire it (§4.6), or add it "
        f"to UNWIRED_BUT_COMPILING with a reason. Unaccounted: {sorted(compiling - families)}"
    )
