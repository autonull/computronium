"""Lock: the dry-run gate scores only cells a supervised loss can score (N1).

``_dry_run_trainable`` scores a cell with cross-entropy on a task batch. A
continuous-control RL task has no supervised label — pendulum's batch target is
a dummy index into a one-wide head — so CE is constant, the gate reads
``all-zero pseudo-gradients`` and filters every pendulum cell out of the space.
The run then measures its positive control and nothing else: one record, no
cell, reported as "no more cells to evaluate".

The gate now declines to judge RL tasks and degenerate (one-class) heads. It
still judges a supervised multi-class cell, which is the case it exists for.

Falsified by removing either skip: the pendulum space holds zero cells again.
"""

from __future__ import annotations

from computronium.experiment.kernel.compose import _dry_run_trainable
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema import Coordinate

from ._specs import mechanism_spec

_CELL = Coordinate(
    substrate="digital",
    geometry="feedforward",
    dynamics="instantaneous",
    plasticity="null",
    credit="gradient",
    update="adam",
    params={},
)


def _gate(task_id: str) -> tuple[bool, str]:
    from computronium.experiment.kernel.evaluate import _task

    shape = task_shape(task_id, "cpu")
    return _dry_run_trainable(
        _CELL, {}, shape.input_shape, shape.output_dim, 0, task=_task(task_id, "cpu")
    )


def test_continuous_control_task_is_not_judged_by_a_supervised_loss() -> None:
    ok, reason = _gate("pendulum")
    assert ok, reason
    assert "RL task" in reason


def test_one_class_head_is_not_judged() -> None:
    ok, reason = _dry_run_trainable(_CELL, {}, (13,), 1, 0, task=None)
    assert ok, reason
    assert "one class" in reason


def test_a_supervised_multiclass_cell_is_still_judged() -> None:
    ok, reason = _gate("wine")
    assert ok, reason
    assert reason == "ok"


def test_the_pendulum_space_holds_a_cell() -> None:
    """The end the gate exists to protect: the declared cell is reachable."""
    base = mechanism_spec()
    spec = base.model_copy(update={"task": "pendulum", "task_cycle": ["pendulum"]})
    space = search_space_from_spec(spec, tasks=["pendulum"])
    cells = list(iter_candidates(spec, space, shape=task_shape, page_size=100))
    assert cells
    assert all(schedule.task_id == "pendulum" for _, schedule in cells)
    assert any(
        coordinate.geometry == "feedforward" and coordinate.credit == "gradient"
        for coordinate, _ in cells
    )
