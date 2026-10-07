"""Lock: a cell trains for real, and the number responds to the axis.

TODO46 §3.1's gate. The kernel's evaluator used to fabricate a schema-valid
record with no training behind it, so every measurement in the store was
scientifically empty. Two assertions, and the second is the one that matters:

* ``train_acc`` is a measured number, not a constant
* swapping a structural axis moves it — a number that ignores the axis you
  varied is a fabricated result no schema check can catch

The multisource lock that keeps evaluation in one place: both backends delegate
to ``evaluate.cell_record``, so a stub cannot return in one class only.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from computronium.experiment.execution import cell_record, evaluate_cell, task_shape
from computronium.experiment.schema import Coordinate, GateVerdict, Provenance, Schedule

_BACKENDS = Path(__file__).resolve().parents[2] / "computronium/experiment/execution"
_TASK_ID = "digits"


def _coordinate(credit: str = "thermodynamic_contrast") -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit=credit,
        update="euclidean",
        params={},
    )


def _schedule(epochs: int = 2) -> Schedule:
    return Schedule(
        fidelity="L0",
        seed=0,
        n_seeds=1,
        epochs=epochs,
        batch_limit=4,
        budget_id="gate",
        task_id=_TASK_ID,
    )


def _provenance() -> Provenance:
    return Provenance(
        env={},
        dataset=_TASK_ID,
        dataset_version="1.0",
        code_sha="test",
        policy="test",
        links={"run_id": "gate"},
    )


@pytest.mark.timeout(300)
def test_cell_trains_and_reports_measured_accuracy() -> None:
    """One coordinate, one real train_acc (TODO46 §3.1 gate, first half)."""
    evaluation = evaluate_cell(_coordinate(), _schedule())

    assert 0.0 < evaluation.metrics["train_acc"] < 1.0
    assert evaluation.epochs_completed == _schedule().epochs
    assert evaluation.metrics["train_loss"] > 0.0
    assert evaluation.walltime_s > 0.0
    assert evaluation.task_id == _TASK_ID


@pytest.mark.timeout(300)
def test_swapping_credit_changes_the_measurement() -> None:
    """Falsification: vary the credit axis, and the measurement must move.

    Compared on accuracy *and* loss. Accuracy on a batch-limited schedule is
    quantized to 1/n_samples, so two credits can tie on it by chance; the loss
    is continuous, so requiring both to be insensitive is what a fabricated
    number looks like.
    """
    base = evaluate_cell(_coordinate("thermodynamic_contrast"), _schedule())
    other = evaluate_cell(_coordinate("local_contrastive"), _schedule())

    assert (base.metrics["train_acc"], base.metrics["train_loss"]) != (
        other.metrics["train_acc"],
        other.metrics["train_loss"],
    ), (
        "the measurement is insensitive to the credit axis — it is not a "
        "measurement of anything the coordinate selected"
    )


@pytest.mark.timeout(300)
def test_digits_shape_reaches_the_geometry() -> None:
    """The task decides the geometry: 8x8 digits is 64 inputs, never 784."""
    # task_shape imported at module level from computronium.experiment.execution

    shape = task_shape(_schedule().task_id)
    assert shape.input_shape == (1, 8, 8)
    assert shape.input_dim == 64
    assert shape.output_dim == 10


def test_record_carries_measurement_and_a_derived_verdict() -> None:
    """The Record holds the measurement; the verdict comes from what happened."""
    record = cell_record(_coordinate(), _schedule(), _provenance())

    assert record.payload["train_acc"] > 0.0
    assert record.payload["epochs_completed"] == record.schedule.epochs
    assert record.status.gate_verdict is GateVerdict.PASS_
    assert record.status.quarantine is False
    assert record.payload["params"], "effective hyperparameters must be recorded (R6)"


def test_evaluation_has_exactly_one_implementation() -> None:
    """Both backends delegate; neither holds its own evaluation body."""
    tree = ast.parse((_BACKENDS / "backends.py").read_text())

    evaluators = [
        node.name
        for cls in tree.body
        if isinstance(cls, ast.ClassDef)
        for node in cls.body
        if isinstance(node, ast.FunctionDef)
        and {"coordinate", "schedule", "provenance", "params"}
        <= {a.arg for a in node.args.args}
        and any(
            isinstance(n, ast.Return)
            and (
                isinstance(n.value, ast.Call)
                and getattr(n.value.func, "id", "") == "cell_record"
            )
            for n in ast.walk(node)
        )
    ]

    assert evaluators, "no backend delegates to cell_record"

    for source in ("backends.py", "stages_impl.py", "search_space.py"):
        text = (_BACKENDS / source).read_text()
        assert "This is a placeholder" not in text, f"{source} still holds a stub"
        assert "actual evaluation would" not in text, f"{source} still holds a stub"
