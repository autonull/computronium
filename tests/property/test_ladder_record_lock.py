"""Lock: a near-chance row carries its ladder record (TODO97 S6b).

A measurement at the base box is not a verdict. The ladder decides whether
the row is one knob away from training, and its record carries the verdict,
the rungs, the cost and the replay hash. The predicates here are the audit's
``near_chance_without_ladder`` check, so the gate is executable in the suite
as well as in CI, and an unimplemented ladder stays a failing test.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from computronium.experiment.sec_ladder import (
    chance_of,
    ladder_rows,
    map_findings,
    near_chance_band,
    replay_hash,
)

MAP = Path("results/sec/map.json")
_RUNS = pytest.mark.skipif(
    not MAP.exists(), reason="no map artifact: the screen runs locally"
)
_PRIMITIVE = "primitive.credit_assignment.pc_alm"
_RUNGS = [
    {
        "factor": 0.1,
        "value": 0.05,
        "status": "measured",
        "val_acc": 0.11,
        "walltime_s": 1.0,
    },
    {
        "factor": 1.0,
        "value": 0.5,
        "status": "measured",
        "val_acc": 0.12,
        "walltime_s": 1.0,
    },
    {
        "factor": 10.0,
        "value": 5.0,
        "status": "measured",
        "val_acc": 0.13,
        "walltime_s": 1.0,
    },
]


def _record(verdict: str = "unimplemented") -> dict[str, Any]:
    """A complete record the schema accepts; a test tampers with one field."""
    rungs = [dict(rung) for rung in _RUNGS]
    record: dict[str, Any] = {
        "primitive": _PRIMITIVE,
        "axis": "credit",
        "task": "mnist",
        "knob": "credit.beta",
        "default": 0.5,
        "rungs": rungs,
        "confirm": dict(rungs[-1]),
        "best": dict(rungs[-1]),
        "verdict": verdict,
        "reason": "the ladder found no point clear of the near-chance band",
        "failing_test": (
            "tests/property/test_ladder_record_lock.py"
            f"::test_an_unimplemented_ladder_clears_its_band[{_PRIMITIVE}]"
        ),
        "close_condition": "the dual-variable settle is not composed",
        "runs": 4,
        "walltime_s": 4.0,
    }
    if verdict == "tuned":
        record["reason"] = None
        record["failing_test"] = None
        record["close_condition"] = None
    record["replay"] = replay_hash(record)
    return record


def _document(record: dict[str, Any] | None = None) -> dict[str, Any]:
    """One bound row at chance, with the record (or without it)."""
    document: dict[str, Any] = {
        "primitives": {
            _PRIMITIVE: {
                "binding": "bound",
                "measurement": {"val_acc": 0.12},
                "ruler": "val_acc on mnist (primary validation_accuracy, chance 0.100)",
                "task": "mnist",
            }
        }
    }
    if record is not None:
        document["ladders"] = {_PRIMITIVE: record}
    return document


def test_a_complete_record_has_no_problems() -> None:
    assert map_findings(_document(_record())) == []


def test_a_row_without_a_record_is_a_finding() -> None:
    findings = map_findings(_document())

    assert findings
    assert "no ladder record" in findings[0]


def test_a_record_without_a_verdict_is_a_finding() -> None:
    record = _record()
    del record["verdict"]

    assert any("verdict" in finding for finding in map_findings(_document(record)))


def test_an_unimplemented_record_without_a_close_is_a_finding() -> None:
    record = _record()
    record["close_condition"] = None

    assert any(
        "close condition" in finding for finding in map_findings(_document(record))
    )


def test_a_changed_number_changes_the_replay_hash() -> None:
    record = _record()
    record["rungs"][0]["val_acc"] = 0.99

    assert any("replay hash" in finding for finding in map_findings(_document(record)))


def test_a_claimed_rung_that_did_not_run_is_a_finding() -> None:
    record = _record()
    record["rungs"] = []
    record["replay"] = replay_hash(record)

    assert any(
        "ladder carries" in finding for finding in map_findings(_document(record))
    )


def test_a_tuned_record_needs_a_best_point() -> None:
    record = _record("tuned")
    record["best"] = None
    record["replay"] = replay_hash(record)

    assert any("best point" in finding for finding in map_findings(_document(record)))


@_RUNS
def test_the_base_coordinate_is_the_control_not_a_ladder_candidate() -> None:
    """A row that swaps an axis back to the base value re-measures the control."""
    document = {
        "base": {"credit": "gradient"},
        "primitives": {
            "primitive.credit_assignment.gradient": {
                "binding": "bound",
                "axis": "credit",
                "box": {"credit": "gradient"},
                "measurement": {"val_acc": 0.11},
                "ruler": "val_acc on mnist (chance 0.100)",
            },
            "primitive.credit_assignment.local_contrastive": {
                "binding": "bound",
                "axis": "credit",
                "box": {"credit": "local_contrastive"},
                "measurement": {"val_acc": 0.11},
                "ruler": "val_acc on mnist (chance 0.100)",
            },
        },
    }

    rows = [spec_id for spec_id, _row, _chance in ladder_rows(document)]

    assert rows == ["primitive.credit_assignment.local_contrastive"]


def test_every_near_chance_row_in_the_map_carries_a_record() -> None:
    document = json.loads(MAP.read_text(encoding="utf-8"))

    assert map_findings(document) == []


def _ladder_params() -> list[pytest.param]:
    """The map's near-chance rows: strict xfail while unimplemented."""
    if not MAP.exists():
        return []
    document = json.loads(MAP.read_text(encoding="utf-8"))
    params = []
    for spec_id, _row, _chance in ladder_rows(document):
        record = document["ladders"][spec_id]
        if record["verdict"] == "unimplemented":
            params.append(
                pytest.param(
                    spec_id,
                    id=spec_id,
                    marks=pytest.mark.xfail(
                        strict=True, reason=str(record["close_condition"])
                    ),
                )
            )
        else:
            params.append(pytest.param(spec_id, id=spec_id))
    return params


@_RUNS
@pytest.mark.parametrize("spec_id", _ladder_params())
def test_an_unimplemented_ladder_clears_its_band(spec_id: str) -> None:
    """An unimplemented ladder names the primitive that would clear the band."""
    document = json.loads(MAP.read_text(encoding="utf-8"))
    record = document["ladders"][spec_id]
    row = document["primitives"][spec_id]
    chance = chance_of(str(row["ruler"]))
    assert chance is not None

    values = [
        rung["val_acc"]
        for rung in record["rungs"]
        if rung["status"] == "measured" and rung["val_acc"] is not None
    ]
    confirm = record["confirm"]
    if confirm is not None and confirm["val_acc"] is not None:
        values.append(confirm["val_acc"])
    assert values, "the ladder recorded no measured point"

    band = near_chance_band(chance)
    assert max(values) > band, (
        f"best {max(values):.3f} is inside the band {band:.3f}: "
        f"{record['close_condition']}"
    )


@pytest.mark.parametrize(
    ("spec_id", "axis"),
    [
        ("primitive.parameter_update.quantized_adam", "update"),
        ("primitive.plasticity.temporal_psi", "plasticity"),
        ("primitive.substrate.noisy", "substrate"),
    ],
)
def test_the_knob_table_names_the_axis_own_fields(spec_id: str, axis: str) -> None:
    """Every axis's declared ladder knob is a field the config actually has.

    Measured 2026-11-20: the update/plasticity/substrate rows named ``lr``,
    ``decay``, ``bit_width`` and ``energy_per_op``, none of which those configs
    declare, so their ladders recorded "no numeric knob" for a trainable row.
    """
    from computronium.experiment.sec_ladder import ladder_knob
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate

    base = _coordinate(
        {**_AXIS_DEFAULTS, axis: spec_id.rsplit(".", 1)[-1]}, own_knobs=axis
    )
    knob = ladder_knob(spec_id, base, axis)
    assert knob is not None, f"{axis} declares no knob the config carries"
    assert knob[0].startswith(f"{axis}.")


@pytest.mark.parametrize(
    "spec_id",
    ["primitive.state_dynamics.error_predictive_coding", "primitive.geometry.conv"],
)
def test_the_ladder_sweeps_the_primitive_own_axis(spec_id: str) -> None:
    """A dynamics or geometry row ladders its own knob, not a credit one.

    Measured 2026-11-20: the credit-only ladder placed ``conv`` on the credit
    axis, composed nothing, and recorded "no ladder point trained" for a row
    the screen had just measured.
    """
    from computronium.experiment.kernel.evaluate import CellEvaluation
    from computronium.experiment.sec_ladder import run_ladder
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule("mnist")
    assert schedule is not None

    def fake(_coord: Any, run: Any) -> CellEvaluation:
        return CellEvaluation(
            metrics={"val_acc": 0.9, "loss": 0.1},
            params={},
            param_count=100,
            walltime_s=0.01,
            epochs_completed=1,
            task_id=run.task_id,
        )

    row = {"task": "mnist", "ruler": "val_acc on mnist (chance 0.100)"}
    record = run_ladder(spec_id, row, 0.1, evaluate=fake, schedule=schedule)
    axis = spec_id.split(".")[1]
    expected = {"state_dynamics": "dynamics", "geometry": "geometry"}[axis]
    assert record.axis == expected
    assert record.knob is not None and record.knob.startswith(f"{expected}.")
    assert record.runs == 4
    assert record.verdict == "tuned"
