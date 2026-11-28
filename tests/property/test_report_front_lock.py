"""W64: the report's front, its registrations and its chance line, locked.

``experiment/surface/report.py`` is the largest uncovered module in the tree
(3,219 lines, 44.4% covered) and the four rules below decide what a report
*means*:

* **A Pareto front** keeps the points no other point dominates, over any
  arity. TODO51 measured the failure a two-objective filter causes: a
  six-name front silently projected onto its first two and reported a front
  with four axes unconstrained.
* **A record missing an objective** cannot be placed on the front, and a
  substituted zero would place it there wrongly.
* **A registration** is dated by the moment it names, or by the day it was
  written, or before any run.
* **A chance line** is read from the task's output dimension, and a cost
  metric has none.

The report is the product's answer to "what did this run do", so these are
asserted directly — no store, no rendering (D6).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from computronium.experiment.schema import (
    Coordinate,
    FailureCause,
    GateVerdict,
    Maturity,
    Provenance,
    Record,
    ReproducibilityClass,
    Schedule,
    Severity,
    Status,
)
from computronium.experiment.surface.report import (
    _directions,
    _numeric_vector,
    chance_level,
    coordinate_key,
    measured_cells,
    non_dominated,
    registered_at,
)

_TWO_AXES = ["val_acc", "walltime_total"]


def _point(acc: float, wall: float) -> dict[str, float]:
    return {"val_acc": acc, "walltime_total": wall}


def _record(payload: dict[str, Any]) -> Record:
    return Record.create(
        run_id="run",
        coordinate=Coordinate(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="euclidean",
            params={},
        ),
        schedule=Schedule(
            fidelity="L1", seed=0, n_seeds=1, epochs=1, batch_limit=2, budget_id="b"
        ),
        provenance=Provenance(
            env={},
            dataset="digits",
            dataset_version="1.0",
            code_sha="sha",
            policy="policy",
            links={},
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L1,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload=payload,
    )


def test_a_front_keeps_only_points_no_other_dominates() -> None:
    """Higher accuracy and lower walltime are both better."""
    points = [_point(0.5, 10.0), _point(0.6, 8.0), _point(0.5, 12.0), _point(0.7, 9.0)]

    assert non_dominated(points, _TWO_AXES, (True, False)) == [1, 3]


def test_a_tie_is_not_dominance() -> None:
    """Equal on every axis, neither point dominates the other."""
    points = [_point(0.5, 10.0), _point(0.5, 10.0)]

    assert non_dominated(points, _TWO_AXES, (True, False)) == [0, 1]


def test_a_six_axis_front_is_not_projected_onto_two() -> None:
    """A point beaten only on the sixth axis is still dominated.

    A front over the first two axes would keep both points: same accuracy,
    same walltime, different capacity.
    """
    axes = ["val_acc", "walltime_total", "param_count", "rho", "sigma_max", "psi"]
    strong = dict(zip(axes, (0.5, 10.0, 100.0, 0.5, 1.0, 4.0), strict=True))
    weak = dict(zip(axes, (0.5, 10.0, 100.0, 0.5, 1.0, 2.0), strict=True))

    assert non_dominated(
        [strong, weak], axes, (True, False, False, True, True, True)
    ) == [0]


def test_a_front_refuses_axes_without_directions() -> None:
    with pytest.raises(ValueError, match="3 axes but 2 directions"):
        non_dominated([_point(0.5, 10.0)], ["a", "b", "c"], (True, False))


def test_a_record_missing_an_objective_is_not_a_zero() -> None:
    record = _record({"val_acc": 0.9})

    assert _numeric_vector(record, ("val_acc", "walltime_total")) is None
    assert _numeric_vector(record, ("val_acc",)) == {"val_acc": 0.9}


def test_a_non_numeric_objective_is_not_a_zero() -> None:
    record = _record({"val_acc": "high"})

    assert _numeric_vector(record, ("val_acc",)) is None


def test_an_unclaimed_metric_is_a_cost() -> None:
    """A key the study never declared a direction for is minimized."""
    assert _directions(("walltime_total",)) == (False,)


def test_a_coordinate_key_drops_axes_it_does_not_name() -> None:
    assert coordinate_key({"geometry": "feedforward", "substrate": ""}) == (
        ("geometry", "feedforward"),
    )


def test_a_measured_cell_is_its_structural_axes() -> None:
    cells = measured_cells([_record({"val_acc": 0.9})])

    assert len(cells) == 1
    assert ("credit", "gradient") in next(iter(cells))


def test_a_registration_dated_by_hand_is_read_at_the_start_of_its_day() -> None:
    assert registered_at({"created": "2026-11-01"}) == datetime(2026, 11, 1)
    assert registered_at({"registered_at": "2026-11-01T12:00:00"}) == datetime(
        2026, 11, 1, 12
    )
    assert registered_at({}) == datetime.min
    assert registered_at({"created": "not a date"}) == datetime.min


def test_a_chance_line_is_read_from_the_task_output_dimension() -> None:
    """``digits`` has ten classes, so chance is 1/10, not a hand-written line."""
    assert chance_level("digits", "val_acc") == pytest.approx(0.1)
    assert chance_level("digits", "walltime_total") is None
    assert chance_level(None, "val_acc") is None
