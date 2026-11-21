"""Locks for the breadth gap table: a red row is accounted, never excused.

The gate's ≥2-family condition is a default. A credit the repository cannot
place on a second family is parked by a named gap (reason, trigger, family,
cost), and the exit stays red: the gap makes the red output actionable, it does
not turn the gate green. Removing the table leaves the row unaccounted.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from computronium.experiment.evidence.breadth import (
    BREADTH_GAPS,
    _error_aware_credits,
    breadth_gate,
)
from computronium.experiment.registry.task_registry import PassBar
from computronium.experiment.schema.seed_registries import seed_all_registries

BAR = PassBar("val_acc", "maximize", 0.5)


@pytest.fixture(autouse=True, scope="module")
def _registries() -> None:
    seed_all_registries()


def _record(credit: str, task: str) -> SimpleNamespace:
    return SimpleNamespace(
        credit=credit,
        measurement_key=f"{credit}:{task}:0.8",
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        update="euclidean",
        params={},
        schedule=SimpleNamespace(fidelity="L2", n_seeds=5, task_id=task),
        status=SimpleNamespace(gate_verdict=SimpleNamespace(value="PASS")),
        payload={"val_acc": 0.8, "pass_bar_cleared": True},
    )


def _family(task: str) -> str:
    return {"mnist": "vision", "copy_task": "memory"}[task]


def _run(records, gaps=None):
    return breadth_gate(records, _family, lambda _task: BAR, gaps=gaps)


def test_every_gap_names_the_row_that_opens_it() -> None:
    declared = set(_error_aware_credits())
    for credit, gap in BREADTH_GAPS.items():
        assert credit in declared, f"{credit}: not an error-aware credit"
        assert gap.reason, f"{credit}: a gap without a reason is prose"
        assert gap.trigger, f"{credit}: a gap without a trigger never closes"
        assert gap.family, f"{credit}: a gap does not name the family it unlocks"
        assert gap.cost_s > 0, f"{credit}: an unpriced gap is not work"


def test_a_declared_gap_parks_a_one_family_credit() -> None:
    gate = _run([_record("rtrl_reference", "copy_task")])
    row = next(row for row in gate.credits if row.credit == "rtrl_reference")
    assert row.green is False
    assert row.gap is not None
    assert row.accounted is True
    assert "rtrl_reference" not in gate.unaccounted
    assert gate.green is False


def test_removing_the_gap_leaves_the_credit_unaccounted() -> None:
    gate = _run([_record("rtrl_reference", "copy_task")], gaps={})
    row = next(row for row in gate.credits if row.credit == "rtrl_reference")
    assert row.gap is None
    assert row.accounted is False
    assert "rtrl_reference" in gate.unaccounted


def test_a_measured_credit_does_not_carry_its_gap() -> None:
    gate = _run([
        _record("rtrl_reference", "copy_task"),
        _record("rtrl_reference", "mnist"),
    ])
    row = next(row for row in gate.credits if row.credit == "rtrl_reference")
    assert row.green is True
    assert row.gap is None


def test_a_gap_never_turns_the_exit_green() -> None:
    gate = _run([_record("rtrl_reference", "copy_task")])
    assert gate.green is False
    assert any(row.credit == "rtrl_reference" for row in gate.gaps)
