"""Phase 3: ψ-only adaptation, boundaries, composition, Z3, probe hygiene."""

from __future__ import annotations

import pytest
import torch
from computronium_lab import Lab, TrainOptions
from computronium_lab.adaptation import (
    AdaptationMode,
    AdaptationResult,
    PsiProgram,
    PsiStep,
    TaskBoundary,
    TaskBoundaryDetector,
    adapt,
    heldout_split,
    paired_slope,
    probe_campaign,
    select_z3_operator,
)

BATCH = 32


@pytest.fixture
def lab() -> Lab:
    return Lab(seed=0)


@pytest.fixture
def system(lab: Lab) -> object:
    return lab.compose("backprop_mlp")


def _task_stream(n: int = 8, classes: int = 4, seed: int = 1):
    gen = torch.Generator().manual_seed(seed)
    for _ in range(n):
        x = torch.randn(BATCH, 32, generator=gen)
        y = torch.randint(0, classes, (BATCH,), generator=gen)
        yield x, y


def test_adaptation_modes_resolve(lab: Lab, system: object) -> None:
    for mode in AdaptationMode:
        result = lab.adapt(system, _task_stream(2), mode=mode, episodes=2)
        assert isinstance(result, AdaptationResult)
        assert result.mode is mode


def test_psi_only_alias_and_theta_invariance(lab: Lab, system: object) -> None:
    result = lab.adapt(system, _task_stream(4), mode="psi_only", episodes=4)
    assert result.mode is AdaptationMode.TEMPORAL
    assert result.theta.bitwise_invariant
    assert result.theta.sha_before == result.theta.sha_after
    assert result.psi_updated
    assert result.metrics["loss"] > 0.0


def test_manual_boundary_forced(lab: Lab, system: object) -> None:
    boundary = TaskBoundary(reason="manual", signal=1.0, detected=True)
    result = lab.adapt(system, _task_stream(2), episodes=2, boundary=boundary)
    assert result.boundary == boundary
    assert boundary.reason == "manual"


def test_boundary_detector_plateau() -> None:
    detector = TaskBoundaryDetector(window=4, plateau_slope=1e-3)
    flat = [1.0, 1.0001, 0.9999, 1.0]
    hit = detector.plateau(flat)
    assert hit is not None and hit.reason == "plateau"
    assert detector.plateau([1.0, 0.9, 0.7, 0.4]) is None


def test_psi_program_composition(lab: Lab, system: object) -> None:
    program = PsiProgram((
        PsiStep("t1", AdaptationMode.TEMPORAL, episodes=3),
        PsiStep("t2", AdaptationMode.CONFLICT_ADAPTIVE, episodes=3),
    ))
    merged = program + PsiProgram((PsiStep("t3", AdaptationMode.ROLE_SPLIT, 2),))
    assert len(merged) == 3
    cumulative, per_step = merged.run(
        system,
        {
            "t1": _task_stream(3),
            "t2": _task_stream(3, seed=2),
            "t3": _task_stream(2, seed=3),
        },
    )
    assert len(per_step) == 3
    assert cumulative.theta.bitwise_invariant
    assert cumulative.psi_updated
    assert cumulative.psi_sha == per_step[-1].psi_sha


def test_z3_closed_form_selection() -> None:
    gen = torch.Generator().manual_seed(0)
    x = torch.randn(4, 6, 5, generator=gen)
    # accumulate target: y equals the cumulative sum of x along the sequence
    y = x.cumsum(dim=1)
    selection = select_z3_operator(x, y)
    assert selection.name == "accumulate"
    assert selection.match_rate == pytest.approx(1.0)
    # identity target
    y_identity = x.clone()
    assert select_z3_operator(x, y_identity).name == "identity"


def test_probe_campaign_forked_and_paired(lab: Lab, system: object) -> None:
    stream = list(_task_stream(12))
    parent_sha = None
    from computronium_lab.adaptation import theta_digest

    parent_sha = theta_digest(system)
    campaign = probe_campaign(system, stream, episodes=4)
    assert campaign.forked and campaign.equal_compute_batches
    assert len(campaign.treated_losses) == 4
    assert theta_digest(system) == parent_sha  # parent isolated
    slope, stat, pvalue = paired_slope(campaign.treated_losses, campaign.control_losses)
    assert slope == campaign.slope
    assert pvalue == campaign.paired_p
    assert stat != 0.0


def test_heldout_split_never_shares() -> None:
    stream = list(_task_stream(10))
    probe, heldout = heldout_split(stream, probe_frac=0.5)
    assert probe and heldout
    assert not set(map(id, probe)) & set(map(id, heldout))
    assert len(probe) + len(heldout) == 10


def test_train_still_works_after_adapt(lab: Lab, system: object) -> None:
    lab.adapt(system, _task_stream(2), episodes=2)
    result = lab.train(system, epochs=1, options=TrainOptions(harvest=True))
    assert result.metrics["accuracy"] >= 0.0
    assert result.harvest is not None and result.harvest.applied


def test_psi_episode_over_ntm_sequence() -> None:
    """E4 over NTM: sequence-shaped ψ episodes, θ bitwise frozen."""
    from computronium_lab.recipes import build_ntm_sequence
    from computronium_lab.sequential import train_sequence

    system = build_ntm_sequence()
    train_sequence(system, "last_symbol", epochs=20, seed=0)

    def stream():
        for _ in range(4):
            # (B, T, D) sequence episodes with a binary task label
            x = torch.randn(16, 8, 8)
            y = (x.sum(dim=(1, 2)) > 0).long()
            yield x, y

    result = adapt(system, stream(), "temporal", episodes=3)
    assert result.theta.bitwise_invariant
    assert result.psi_updated
    assert 0.0 <= result.metrics["free_accuracy"] <= 1.0
