"""Lock: S9 turns the tuned ladder records into one pre-registered claim list.

The candidate pool is the maps' ``ladders`` table with ``verdict == "tuned"``,
ranked by the confirmation seed's difference from the default rung. Each claim
commits its margin before the first seed, pairs five index-matched seeds at
one box, and reports a CI: claim, marginal, coordinate, defect or refused.
"""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.sec_claims import (
    ClaimCandidate,
    _marginal,
    candidate_box,
    claim_candidates,
    margin_for,
    register_claim,
    registration_path,
    run_claim,
    write_claim,
)
from computronium.experiment.sec_deep_dive import (
    CLAIM_SEEDS,
    MARGIN,
    load_registration,
)

if TYPE_CHECKING:
    from pathlib import Path


def _record(
    primitive: str,
    *,
    verdict: str = "tuned",
    knob: str = "credit.feedback_scale",
    default: float = 0.01,
    best_factor: float = 10.0,
    best_value: float = 0.1,
    default_val: float = 0.14,
    confirm_val: float = 0.50,
) -> dict:
    return {
        "primitive": primitive,
        "axis": "credit",
        "task": "mnist",
        "knob": knob,
        "default": default,
        "rungs": [
            {"factor": 0.1, "value": default * 0.1, "val_acc": 0.10},
            {"factor": 1.0, "value": default, "val_acc": default_val},
            {"factor": best_factor, "value": best_value, "val_acc": 0.40},
        ],
        "confirm": {"factor": 1.0, "value": best_value, "val_acc": confirm_val},
        "best": {"factor": best_factor, "value": best_value, "val_acc": 0.40},
        "verdict": verdict,
    }


def _map(tmp_path: Path, records: dict[str, dict]) -> Path:
    document = {
        "version": "SEC-v3",
        "base": {"task": "mnist", "credit": "gradient"},
        "inventory": {"bar": 0.106},
        "primitives": {
            primitive: {
                "status": "measured",
                "binding": "bound",
                "axis": "credit_assignment",
                "box": {
                    "credit": primitive.rsplit(".", 1)[-1],
                    "credit.feedback_scale": 0.01,
                },
            }
            for primitive in records
        },
        "ladders": records,
    }
    path = tmp_path / "map.json"
    path.write_text(json.dumps(document))
    return path


def _schedule(**extra):
    from computronium.experiment.sec_loop import base_schedule

    schedule = base_schedule("mnist", "cpu")
    assert schedule is not None
    return replace(schedule, **extra)


def test_the_claim_list_is_the_tuned_records_ranked_by_effect(tmp_path: Path) -> None:
    path = _map(
        tmp_path,
        {
            "primitive.credit_assignment.alpha": _record(
                "primitive.credit_assignment.alpha", confirm_val=0.20
            ),
            "primitive.credit_assignment.beta": _record(
                "primitive.credit_assignment.beta", confirm_val=0.50
            ),
            "primitive.credit_assignment.gamma": _record(
                "primitive.credit_assignment.gamma", verdict="unimplemented"
            ),
        },
    )
    candidates = claim_candidates([path])
    assert [candidate.primitive for candidate in candidates] == [
        "primitive.credit_assignment.beta",
        "primitive.credit_assignment.alpha",
    ]
    assert candidates[0].effect == pytest.approx(0.50 - 0.14)
    assert candidates[0].best_factor == pytest.approx(10.0)
    assert candidates[0].axis == "credit"
    assert candidates[0].level == "beta"
    assert registration_path(candidates[0]).name == "sec_credit_beta.json"


def test_the_claim_list_is_capped_at_five(tmp_path: Path) -> None:
    path = _map(
        tmp_path,
        {
            f"primitive.credit_assignment.p{index}": _record(
                f"primitive.credit_assignment.p{index}",
                confirm_val=0.20 + index * 0.01,
            )
            for index in range(6)
        },
    )
    assert len(claim_candidates([path])) == 5


def test_the_tuning_rows_are_the_largest_margin_over_the_bar() -> None:
    """The S9 ladders take the headroom rows; the control re-measure is out."""
    from computronium.experiment.sec_deep_dive import tuning_candidates

    map_data = {
        "version": "SEC-v3",
        "base": {"credit": "gradient"},
        "inventory": {"bar": 0.106},
        "primitives": {
            "primitive.credit_assignment.local_contrastive": {
                "status": "measured",
                "binding": "bound",
                "axis": "credit_assignment",
                "box": {"credit": "local_contrastive"},
                "measurement": {"val_acc": 0.30},
            },
            "primitive.credit_assignment.random_projections": {
                "status": "measured",
                "binding": "bound",
                "axis": "credit_assignment",
                "box": {"credit": "random_projections"},
                "measurement": {"val_acc": 0.20},
            },
            "primitive.credit_assignment.gradient": {
                "status": "measured",
                "binding": "bound",
                "axis": "credit_assignment",
                "box": {"credit": "gradient"},
                "measurement": {"val_acc": 0.90},
            },
        },
    }
    picked = tuning_candidates(map_data, 2)
    assert [candidate.level for candidate in picked] == [
        "local_contrastive",
        "random_projections",
    ]


def test_the_margin_is_the_rulers_resolution_when_coarser() -> None:
    assert margin_for("mnist") == pytest.approx(MARGIN)
    assert margin_for("iris") == pytest.approx(1.0 / 30.0)
    assert margin_for("iris") > MARGIN


def test_the_registration_is_committed_before_the_first_seed(tmp_path: Path) -> None:
    path = _map(
        tmp_path,
        {
            "primitive.credit_assignment.beta": _record(
                "primitive.credit_assignment.beta"
            )
        },
    )
    candidate = claim_candidates([path])[0]
    schedule = _schedule()
    registration = write_claim(candidate, schedule, tmp_path)
    target = tmp_path / "sec_credit_beta.json"
    assert target.exists()
    assert registration.min_seeds == CLAIM_SEEDS == 5
    assert registration.threshold == pytest.approx(MARGIN)
    assert load_registration(target, candidate_box(candidate, schedule)) == registration
    assert json.loads(target.read_text())["created"]


def test_a_foreign_box_registration_refuses_the_claim() -> None:
    candidate = ClaimCandidate(
        primitive="primitive.credit_assignment.beta",
        axis="credit",
        level="beta",
        task="mnist",
        knob="credit.feedback_scale",
        default=0.01,
        best_factor=10.0,
        best_value=0.1,
        effect=0.3,
        box={"credit": "beta", "credit.feedback_scale": 0.01},
    )
    schedule = _schedule()
    registration = register_claim(candidate, schedule)
    record = run_claim(candidate, registration, replace(schedule, batch_size=8))
    assert record.verdict == "refused"
    assert record.cells == ()


def test_five_paired_seeds_carry_a_clearing_ci() -> None:
    candidate = ClaimCandidate(
        primitive="primitive.credit_assignment.beta",
        axis="credit",
        level="beta",
        task="mnist",
        knob="credit.feedback_scale",
        default=0.01,
        best_factor=10.0,
        best_value=0.1,
        effect=0.3,
        box={"credit": "beta", "credit.feedback_scale": 0.01},
    )
    schedule = _schedule()
    registration = register_claim(candidate, schedule)

    def measure(coordinate, run):
        control = 0.20 + 0.002 * run.seed
        treatment = coordinate.params["credit.feedback_scale"] == 0.1
        return {
            "status": "measured",
            "val_acc": control + (0.06 if treatment else 0.0),
            "loss": 1.0,
            "walltime_s": 0.1,
            "replay_hash": "fake",
            "box": {"seed": run.seed},
        }

    record = run_claim(candidate, registration, schedule, measure=measure)
    assert len(record.cells) == 2 * CLAIM_SEEDS
    assert [cell.seed for cell in record.cells if cell.arm == "control"] == list(
        range(CLAIM_SEEDS)
    )
    assert record.paired is not None
    assert record.paired["mean_diff"] == pytest.approx(0.06)
    assert record.paired["ci_lower"] > registration.threshold
    assert record.verdict == "claim"


def test_an_identical_pair_is_marked_no_power() -> None:
    candidate = ClaimCandidate(
        primitive="primitive.credit_assignment.beta",
        axis="credit",
        level="beta",
        task="mnist",
        knob="credit.feedback_scale",
        default=0.01,
        best_factor=10.0,
        best_value=0.1,
        effect=0.3,
        box={"credit": "beta", "credit.feedback_scale": 0.01},
    )
    schedule = _schedule()
    registration = register_claim(candidate, schedule)

    def measure(coordinate, run):
        return {
            "status": "measured",
            "val_acc": 0.2,
            "loss": 1.0,
            "walltime_s": 0.1,
            "replay_hash": "fake",
            "box": {"seed": run.seed},
        }

    record = run_claim(candidate, registration, schedule, measure=measure)
    assert record.verdict == "coordinate"
    assert record.no_power is True
    assert record.paired is None


def test_a_best_point_at_the_default_is_marked_without_cells() -> None:
    candidate = ClaimCandidate(
        primitive="primitive.geometry.attention",
        axis="geometry",
        level="attention",
        task="mnist",
        knob="geometry.hidden_dim",
        default=64.0,
        best_factor=1.0,
        best_value=64.0,
        effect=0.0,
        box={"geometry": "attention", "geometry.hidden_dim": 64.0},
    )
    schedule = _schedule()
    registration = register_claim(candidate, schedule)
    record = run_claim(candidate, registration, schedule)
    assert record.verdict == "coordinate"
    assert record.no_power is True
    assert record.cells == ()


def test_a_stale_box_refuses_the_claim_before_its_first_cell() -> None:
    """A row screened before the box carried its params cannot be priced.

    The candidate's box names the six axes and nothing else, so the two arms
    would train at a rebuilt coordinate whose params are the screen's defaults
    (measured 2026-11-20, S9c: three of six sampled rows did not reproduce at
    their rebuilt box). The pair refuses by name; the close is the screen's own
    re-run, which writes the params into the box.
    """
    candidate = ClaimCandidate(
        primitive="primitive.credit_assignment.beta",
        axis="credit",
        level="beta",
        task="mnist",
        knob="credit.feedback_scale",
        default=0.01,
        best_factor=10.0,
        best_value=0.1,
        effect=0.3,
        box={"credit": "beta"},
    )
    schedule = _schedule()
    registration = register_claim(candidate, schedule)

    def boom(_coordinate, _run):
        raise AssertionError("a stale claim trained a cell")

    record = run_claim(candidate, registration, schedule, measure=boom)

    assert record.verdict == "refused"
    assert record.cells == ()
    assert "no structural params" in record.stop_reason


def test_a_registration_without_params_is_stale() -> None:
    """A registration written before S9c is refused, never compared.

    The registration carries the coordinate's box, so a claim re-boxed between
    the ladder and the run is caught before its first seed.
    """
    candidate = ClaimCandidate(
        primitive="primitive.credit_assignment.beta",
        axis="credit",
        level="beta",
        task="mnist",
        knob="credit.feedback_scale",
        default=0.01,
        best_factor=10.0,
        best_value=0.1,
        effect=0.3,
        box={"credit": "beta", "credit.feedback_scale": 0.01},
    )
    schedule = _schedule()
    fresh = register_claim(candidate, schedule)
    assert fresh.box is not None
    assert "credit.feedback_scale" in fresh.box
    stale = replace(fresh, box=schedule.to_dict())

    record = run_claim(candidate, stale, schedule)

    assert record.verdict == "refused"
    assert "re-register" in record.stop_reason


def test_a_point_within_one_standard_error_is_marginal() -> None:
    assert _marginal([0.05, 0.02, 0.04, 0.01, 0.06], 0.0333) is True
    assert _marginal([0.5, 0.5, 0.5, 0.5, 0.5], 0.01) is False
    assert _marginal([0.0, 0.01, 0.02, 0.01, 0.0], 0.0333) is False
