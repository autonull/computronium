"""Locks for E1, the estimator atlas (TODO93 §6a, track E).

The table is the artifact, but the controls are predicates: a reference that
misses its own finite difference invalidates the run, an exact control at
chance invalidates it, a zero update is a defect, and a refusal or a
below-floor treatment is a row with a trigger — never a silent exclusion.
E-lite is the cheapest screen and must stay a strict subset of the six-arm
rung. A single seed has no variance, and that field is ``None``, not zero.
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest

from computronium.validation.estimator_atlas import (
    ARMS,
    FLOOR,
    LITE_ARMS,
    REFERENCE_CONTROL_TOL,
    EstimatorCell,
    _aggregate,
    _build_arm,
    _note,
    _verdict,
    read_cells,
    replay_estimator_atlas,
)

_COORDINATES = {
    "gradient": ("exact", "exact_tractable"),
    "random_projections": ("gradient_approx", "exact_tractable"),
    "pc_alm": ("gradient_approx", "exact_tractable"),
    "pepita": ("objective_local", "none"),
    "local_goodness": ("objective_local", "none"),
    "hybrid": ("hybrid", "none"),
}


def _cell(
    *,
    arm: str = "gradient",
    seed: int = 61,
    lr: float = 0.01,
    stage: str = "atlas",
    val: float = 0.90,
    angle: float = 0.5,
    magnitude: float = 1.0,
    nonzero: bool = True,
    refused: bool = False,
) -> EstimatorCell:
    kind, reference = _COORDINATES[arm]
    return EstimatorCell(
        arm=arm,
        estimator_kind=kind,
        bias_reference=reference,
        stage=stage,
        seed=seed,
        lr=lr,
        angle=None if refused else angle,
        magnitude=None if refused else magnitude,
        update_norm=0.0 if refused or not nonzero else 0.1,
        reference_norm=0.1,
        nonzero_update=nonzero,
        val_acc=None if refused else val,
        train_acc=None if refused else val,
        steps=0 if refused else 600,
        forward_equivalents=None if refused else 6.0,
        time_s=1.0,
        refused=refused,
    )


def test_every_arm_declares_its_estimator_coordinate() -> None:
    assert len(ARMS) == 6
    for name in ARMS:
        arm = _build_arm(name)
        assert (arm.estimator_kind, arm.bias_reference) == _COORDINATES[name]
        assert arm.estimator_kind != "unspecified"
        assert arm.bias_reference != "unspecified"


def test_lite_is_a_strict_subset_of_the_six_arm_rung() -> None:
    assert set(LITE_ARMS) < set(ARMS)
    assert len(LITE_ARMS) == 4


def test_one_seed_has_no_variance() -> None:
    aggregate = _aggregate((_cell(),))
    assert aggregate["gradient"]["angle_sigma"] is None
    assert aggregate["gradient"]["val_acc_sigma"] is None


def test_three_seeds_report_the_sample_sigma() -> None:
    cells = (
        _cell(seed=61, angle=1.0, val=0.90),
        _cell(seed=62, angle=1.0, val=0.92),
        _cell(seed=63, angle=1.0, val=0.94),
    )
    aggregate = _aggregate(cells)
    assert aggregate["gradient"]["val_acc_sigma"] == pytest.approx(0.02)
    assert aggregate["gradient"]["angle_sigma"] == pytest.approx(0.0)


def test_reference_mismatch_invalidates_the_run() -> None:
    verdict, reason = _verdict(
        (_cell(),),
        reference_fd_cosine=REFERENCE_CONTROL_TOL - 0.01,
    )
    assert verdict == "invalid-instrument"
    assert "not validated" in reason


def test_exact_control_at_chance_invalidates_the_run() -> None:
    verdict, reason = _verdict(
        (_cell(arm="gradient", val=FLOOR - 0.05),),
        reference_fd_cosine=1.0,
    )
    assert verdict == "invalid-learning"
    assert "invalid, not the treatment" in reason


def test_zero_update_is_a_defect() -> None:
    verdict, reason = _verdict(
        (_cell(), _cell(arm="pepita", nonzero=False)),
        reference_fd_cosine=1.0,
    )
    assert verdict == "defect"
    assert "defect, not a coordinate" in reason


def test_a_refusal_is_an_atlas_row_with_its_trigger() -> None:
    verdict, reason = _verdict(
        (_cell(), _cell(arm="pc_alm", refused=True)),
        reference_fd_cosine=1.0,
    )
    assert verdict == "atlas"
    assert "refused" in reason
    assert "table is the artifact" in reason


def test_a_below_floor_treatment_is_an_atlas_row() -> None:
    verdict, reason = _verdict(
        (_cell(), _cell(arm="random_projections", val=FLOOR - 0.05)),
        reference_fd_cosine=1.0,
    )
    assert verdict == "atlas"
    assert "below the floor" in reason
    assert "not a silent exclusion" in reason


def test_pc_alm_chance_is_a_regime_mismatch_not_a_verdict() -> None:
    note = _note(_build_arm("pc_alm"), FLOOR - 0.05)
    assert "regime-mismatch" in note
    assert "depth 100" in note


def test_replay_recomputes_the_report_from_the_log(tmp_path) -> None:
    ladder = (
        _cell(arm="gradient", seed=59, stage="ladder", val=0.85),
        _cell(arm="gradient", seed=60, stage="confirm", val=0.86),
    )
    cells = (
        _cell(arm="gradient", seed=61, stage="atlas", val=0.90),
        _cell(arm="random_projections", seed=61, stage="atlas", val=0.82),
    )
    log = tmp_path / "estimator.cells.jsonl"
    rows = [json.dumps(asdict(cell)) for cell in (*ladder, *cells)]
    log.write_text("\n".join((*rows, rows[0])) + "\n", encoding="utf-8")

    report = replay_estimator_atlas(progress=log)
    assert report.verdict == "atlas"
    assert len(report.cells) == len(cells)
    assert len(report.ladder) == len(ladder)
    assert len(read_cells(log)) == len(ladder) + len(cells)


def test_read_cells_dedups_by_measurement_identity(tmp_path) -> None:
    cell = _cell()
    log = tmp_path / "estimator.cells.jsonl"
    log.write_text(
        "\n".join(json.dumps(asdict(cell)) for _ in range(3)) + "\n",
        encoding="utf-8",
    )
    assert len(read_cells(log)) == 1
