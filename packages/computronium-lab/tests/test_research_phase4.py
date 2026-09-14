"""Phase 4 tests: continual benchmark with invariance proofs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium_lab import Lab

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_benchmark_continual_smoke(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = Lab(seed=0)
    report = lab.benchmark_continual(
        mechanism="backprop_mlp",
        curriculum="two_task_switch",
        modes=("temporal",),
        controls=("frozen_no_psi", "theta_finetune_matched_compute"),
        seeds=(0,),
    )
    assert report.mechanism == "backprop_mlp"
    assert {arm.arm for arm in report.arms} >= {
        "temporal",
        "frozen_no_psi",
        "theta_finetune_matched_compute",
    }
    temporal = next(arm for arm in report.arms if arm.arm == "temporal")
    assert temporal.metric_values["theta_invariant"] == (1.0,)
    assert report.comparisons
    assert "temporal" in report.invariance_proofs
    assert report.state_inventory
    assert report.manifest_paths


def test_benchmark_unknown_curriculum() -> None:
    lab = Lab(seed=0)
    try:
        lab.benchmark_continual(curriculum="no_such_curriculum", seeds=(0,))
    except ValueError as exc:
        assert "unknown curriculum" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_capacity_control_present_or_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    lab = Lab(seed=0)
    report = lab.benchmark_continual(
        mechanism="backprop_mlp",
        modes=("temporal",),
        controls=("frozen_no_psi",),
        seeds=(0,),
    )
    assert report.capacity_control == "capacity_matched_recurrent" or any(
        "capacity-matched" in block.reason for block in report.blocks
    )


def test_benchmark_continual_composed_psi(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TODO26 S.1/S.2: the composed backbone+ψ mechanism rides the
    continual benchmark end-to-end — task-A lab.train, per-episode ψ
    ridge re-solve, bitwise θ invariance."""
    monkeypatch.chdir(tmp_path)
    lab = Lab(seed=0)
    report = lab.benchmark_continual(
        mechanism="temporal_psi_task_switcher",
        modes=("conflict_adaptive",),
        controls=("frozen_no_psi",),
        seeds=(0,),
    )
    assert report.mechanism == "temporal_psi_task_switcher"
    assert not report.blocks, [b.reason for b in report.blocks]
    mode = next(a for a in report.arms if a.arm == "conflict_adaptive")
    frozen = next(a for a in report.arms if a.arm == "frozen_no_psi")
    assert mode.metric_values["theta_invariant"] == (1.0,)
    assert mode.metric_values["accuracy"][0] > frozen.metric_values["accuracy"][0]
