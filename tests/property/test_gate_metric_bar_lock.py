"""Lock: gate PASS means above the declared ruler, not merely defect-free.

TODO92 §3.3c. ``assess_gate_verdict`` used to read only void/hard/soft defects,
so a cell that learned nothing PASSed: a 1-epoch RL pendulum cell measuring
-1536.6 is the recorded example. This lock pins the bar to the task's own
chance/majority ruler and proves that removing the comparison flips a
below-chance cell back to PASS.
"""

from __future__ import annotations

import math

import pytest

from computronium.experiment.kernel.evaluate import (
    CellEvaluation,
    _clears_pass_bar,
    cell_record,
)
from computronium.experiment.registry.task_registry import (
    PassBar,
    TaskRegistry,
    primary_pass_bar,
)
from computronium.experiment.schema import (
    Coordinate,
    FailureCause,
    GateVerdict,
    Provenance,
    Record,
    Schedule,
)

_TASK_ID = "digits"


def test_every_registered_task_declares_a_ruler() -> None:
    """A task without a bar would PASS on defect-freedom alone."""
    unbarred = [task.name for task in TaskRegistry() if primary_pass_bar(task) is None]
    assert unbarred == [], f"tasks with no declared pass bar: {unbarred}"


def test_the_ruler_is_the_task_s_chance_rate_not_the_domain_target() -> None:
    """The bar sits at the trivial predictor, so a low-fidelity cell can pass."""
    registry = TaskRegistry()
    digits = primary_pass_bar(registry.get("digits"))
    proteins = primary_pass_bar(registry.get("proteins"))
    pendulum = primary_pass_bar(registry.get("pendulum"))

    assert digits is not None
    assert proteins is not None
    assert pendulum is not None
    assert (digits.metric_key, digits.direction, digits.value) == (
        "val_acc",
        "maximize",
        0.1,
    )
    assert proteins.value == pytest.approx(0.5964)
    assert pendulum.value == pytest.approx(-1200.0)


@pytest.mark.parametrize(
    ("bar", "measured", "cleared"),
    [
        (PassBar("val_acc", "maximize", 0.5), 0.6, True),
        (PassBar("val_acc", "maximize", 0.5), 0.5, False),
        (PassBar("val_acc", "maximize", 0.5), 0.4, False),
        (PassBar("val_ppl", "minimize", 27.0), 20.0, True),
        (PassBar("val_ppl", "minimize", 27.0), 27.0, False),
        (PassBar("val_ppl", "minimize", 27.0), 30.0, False),
        (PassBar("val_loss", "minimize", 1.0), math.nan, False),
    ],
)
def test_direction_decides_which_side_of_the_bar_clears(
    bar: PassBar, measured: float, cleared: bool
) -> None:
    assert _clears_pass_bar(bar, {bar.metric_key: measured}) is cleared


def test_a_missing_primary_metric_cannot_clear_a_bar() -> None:
    assert _clears_pass_bar(PassBar("val_acc", "maximize", 0.5), {}) is False


def _coordinate() -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )


def _schedule() -> Schedule:
    return Schedule(
        fidelity="L0",
        seed=0,
        n_seeds=1,
        epochs=1,
        batch_limit=4,
        budget_id="bar",
        task_id=_TASK_ID,
    )


def _provenance() -> Provenance:
    return Provenance(
        env={},
        dataset=_TASK_ID,
        dataset_version="1.0",
        code_sha="test",
        policy="test",
        links={"run_id": "bar"},
    )


def _fake_evaluation(val_acc: float) -> CellEvaluation:
    return CellEvaluation(
        metrics={"val_acc": val_acc, "train_acc": val_acc, "loss": 1.0},
        params={},
        param_count=100,
        walltime_s=1.0,
        epochs_completed=1,
        task_id=_TASK_ID,
    )


def _record(monkeypatch: pytest.MonkeyPatch, val_acc: float) -> Record:
    monkeypatch.setattr(
        "computronium.experiment.kernel.evaluate.evaluate_cell",
        lambda *_args, **_kwargs: _fake_evaluation(val_acc),
    )
    return cell_record(_coordinate(), _schedule(), _provenance())


def test_a_below_chance_cell_fails_and_names_the_bar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The acceptance case: this cell PASSed before §3.3c and FAILs now."""
    record = _record(monkeypatch, 0.0625)

    assert record.status.gate_verdict is GateVerdict.FAIL
    assert record.status.quarantine is True
    assert record.status.cause is FailureCause.DIVERGENCE
    assert "below bar" in record.status.defect
    assert record.payload["pass_bar"] == {
        "metric": "val_acc",
        "direction": "maximize",
        "value": 0.1,
    }
    assert record.payload["pass_bar_cleared"] is False


def test_an_above_bar_cell_passes_and_carries_its_ruler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = _record(monkeypatch, 0.5)

    assert record.status.gate_verdict is GateVerdict.PASS_
    assert record.status.quarantine is False
    assert record.status.defect == ""
    assert record.payload["pass_bar_cleared"] is True
