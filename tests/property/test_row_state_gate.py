"""One row-state source for the writer and the gate (TODO97 S5h).

The screen wrote ``defect`` and the audit compared ``defective``, so the gate's
lock predicates could never fire: a defective row without a failing test passed
the audit. These tests remove the mechanism and fail: the writer's state is the
gate's, the gate reports a missing lock, and each declared defect class stamps
its lock from the one register.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.sec_census import build_census
from computronium.experiment.sec_loop import _map_row, defect_lock
from computronium.experiment.sec_status import (
    CELL_STATUS,
    RowStatus,
    missing_locks,
)
from scripts.audit import row_without_lock

if TYPE_CHECKING:
    from pathlib import Path


def _cell(task: str, defect: str) -> dict[str, object]:
    return {
        "status": "DEFECT",
        "defect": defect,
        "box": {"task": task},
    }


def _row(task: str, defect: str) -> dict[str, object]:
    entry = build_census()[0]
    return _map_row(entry, _cell(task, defect))


def test_the_writer_emits_the_gates_state() -> None:
    """The cell statuses map onto the declared row states, in both readers."""
    assert CELL_STATUS["DEFECT"] is RowStatus.DEFECTIVE
    assert _row("mnist", "param_count 900 over ceiling")["status"] == (
        RowStatus.DEFECTIVE
    )


@pytest.mark.parametrize(
    ("task", "defect", "defect_class"),
    [
        ("mnist", "param_count 900 over ceiling", "ceiling_overrun"),
        (
            "cartpole",
            "a sequence geometry reads x (time, batch, input); got x (1, 4)",
            "time_major_credit",
        ),
        (
            "copy_task",
            "NcaGeometry: flattened input has 21 features, but grid requires 784",
            "grid_from_input_shape",
        ),
        (
            "copy_task",
            "Class values must be smaller than num_classes",
            "class_vocabulary",
        ),
        (
            "cartpole",
            "Trying to backward through the graph a second time",
            "recurrent_state_detach",
        ),
        ("tiny_shakespeare", "mat1 and mat2 must have the same dtype", "token_lane"),
    ],
)
def test_every_declared_defect_class_stamps_its_lock(
    task: str, defect: str, defect_class: str
) -> None:
    row = _row(task, defect)
    lock = defect_lock(task, defect)

    assert lock is not None
    assert row["defect_class"] == defect_class
    assert row["failing_test"] == lock.lock


def _write_map(path: Path, row: dict[str, object]) -> None:
    path.write_text(
        json.dumps({"primitives": {"primitive.geometry.nca": row}}),
        encoding="utf-8",
    )


def test_a_defect_row_without_a_lock_is_a_finding(tmp_path: Path) -> None:
    path = tmp_path / "map.json"
    _write_map(path, {"primitive": "primitive.geometry.nca", "status": "defective"})

    findings = row_without_lock([path])
    assert len(findings) == 1
    assert "failing_test" in findings[0].detail

    _write_map(
        path,
        {
            "primitive": "primitive.geometry.nca",
            "status": "defective",
            "failing_test": "tests/property/test_family_defect_locks.py::x",
        },
    )
    assert row_without_lock([path]) == []


def test_an_undeclared_state_is_a_finding(tmp_path: Path) -> None:
    """The deleted vocabulary cannot return as a quiet row."""
    path = tmp_path / "map.json"
    _write_map(path, {"primitive": "primitive.geometry.nca", "status": "defect"})

    findings = row_without_lock([path])
    assert len(findings) == 1
    assert "no declared state" in findings[0].detail


def test_a_refused_row_is_quiet_and_an_impossible_row_owes_two_locks(
    tmp_path: Path,
) -> None:
    assert missing_locks({"status": RowStatus.REFUSED}) == []
    assert missing_locks({"status": RowStatus.IMPOSSIBLE}) == [
        "refusal_test",
        "necessity_test",
    ]
