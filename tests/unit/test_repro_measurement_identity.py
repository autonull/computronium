"""Lock: the replay comparison key carries the task.

A ``cell_key`` collapses seeds and tasks, and one run's schedule can span
several tasks (``digits`` + ``iris``). Keying by ``(cell_key, seed)`` mispairs
the same cell across tasks, so ``comp repro`` compared different measurements
(TODO107 W31).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from computronium.experiment.surface._cli._repro import _measurement_identity

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


def _record(cell_key: str, task_id: str, seed: int) -> Record:
    schedule = SimpleNamespace(task_id=task_id, seed=seed)
    return cast("Record", SimpleNamespace(cell_key=cell_key, schedule=schedule))


def test_measurement_identity_separates_tasks() -> None:
    digits = _record("cell", "digits", 42)
    iris = _record("cell", "iris", 42)
    assert _measurement_identity(digits) != _measurement_identity(iris)
    assert _measurement_identity(digits) == ("cell", "digits", 42)


def test_measurement_identity_separates_seeds() -> None:
    first = _record("cell", "digits", 42)
    second = _record("cell", "digits", 43)
    assert _measurement_identity(first) != _measurement_identity(second)
