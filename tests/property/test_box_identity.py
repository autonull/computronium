"""Lock: a claim names the box its run trained at (TODO95 P0b / D2).

``Schedule`` is the box: batch size and steps per task are part of the
measurement identity, a pre-registration that declares a box refuses a run at
another, and the cell log carries each screen beside the Record that identifies
it. This test fails if two boxes share a measurement key, if the loader drops
the declared box, or if the log stops carrying a record.
"""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING

from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.sec_census import MAP_VERSION, build_census
from computronium.experiment.sec_init import write_map
from computronium.experiment.sec_loop import (
    _box_summary,
    repair_boxes,
    update_cell_log,
    update_map,
)
from computronium.validation.preregistration import (
    PairedComparison,
    ThresholdRegistration,
)

if TYPE_CHECKING:
    from pathlib import Path

_COORDINATE = Coordinate(
    substrate="digital",
    geometry="feedforward",
    dynamics="instantaneous",
    plasticity="null",
    credit="gradient",
    update="euclidean",
    params={},
)
_SCHEDULE = Schedule(
    fidelity="L0",
    seed=0,
    n_seeds=1,
    epochs=1,
    batch_limit=375,
    batch_size=32,
    budget_id="p0",
    task_id="mnist",
)
_CONFIRM = PairedComparison(
    n=5, mean_diff=0.3, ci_lower=0.1, ci_upper=0.5, p_value=0.001, cohens_dz=1.0
)


def test_box_identity() -> None:
    other = replace(_SCHEDULE, batch_size=64)
    assert _COORDINATE.cell_key() == _COORDINATE.cell_key()
    assert _COORDINATE.measurement_key(_SCHEDULE) != _COORDINATE.measurement_key(other)


def test_steps_per_task_alone_changes_the_measurement_identity() -> None:
    other = replace(_SCHEDULE, steps_per_task=2)
    assert _COORDINATE.measurement_key(_SCHEDULE) != _COORDINATE.measurement_key(other)


def test_the_box_travels_with_the_screen() -> None:
    box = _box_summary(_COORDINATE, _SCHEDULE)
    assert box["batch_size"] == _SCHEDULE.batch_size
    assert box["batch_limit"] == _SCHEDULE.batch_limit
    assert box["task"] == _SCHEDULE.task_id


def _registration(box: dict | None = None) -> ThresholdRegistration:
    return ThresholdRegistration(
        claim="the pinned arm clears the bar",
        metric="val_acc",
        threshold=0.05,
        box=box,
    )


def test_a_registration_at_one_box_refuses_a_run_at_another() -> None:
    registration = _registration({"batch_size": 32, "epochs": 1})
    assert registration.box_mismatch(_SCHEDULE) is None
    assert registration.box_mismatch(replace(_SCHEDULE, batch_size=64)) is not None
    assert _CONFIRM.passes(registration, box=_SCHEDULE) is True
    assert _CONFIRM.passes(registration, box=replace(_SCHEDULE, epochs=5)) is False
    # A boxed registration decides only a run whose box it is given.
    assert _CONFIRM.passes(registration) is False


def test_the_loader_keeps_the_declared_box() -> None:
    registration = _registration({"batch_size": 32, "epochs": 1})
    loaded = ThresholdRegistration.from_dict(
        json.loads(json.dumps(registration.to_dict()))
    )
    assert loaded == registration
    assert loaded.box == {"batch_size": 32, "epochs": 1}


def test_init_then_update_keeps_a_row(tmp_path: Path) -> None:
    write_map(tmp_path)
    entries = build_census()
    cell = {
        "primitive": entries[0].id,
        "status": "MEASURED",
        "val_acc": 0.5,
        "loss": 1.0,
        "param_count": 10,
        "within_ceiling": True,
        "walltime_s": 1.0,
        "box": {**_box_summary(_COORDINATE, _SCHEDULE), "task": "mnist"},
        "ruler": "val_acc on mnist",
        "control_val_acc": 0.89,
        "binding": "bound",
        "binding_reason": None,
        "swapped": False,
    }
    update_map(tmp_path, entries, {"cells": [cell]})
    update_map(tmp_path, entries, {"cells": []})
    data = json.loads((tmp_path / "map.json").read_text())
    assert data["version"] == MAP_VERSION
    assert data["primitives"][entries[0].id]["status"] == "measured"
    assert data["primitives"][entries[0].id]["box"]["batch_size"] == 32


def test_a_box_is_repaired_from_its_cells_own_record(tmp_path: Path) -> None:
    """A box screened before its params is restored from the run's record.

    The cell log's record carries the params the cell ran at, so a row's box is
    rebuilt from that record — the same source its replay hash names — instead
    of re-screening (TODO97 S9c). The repair is idempotent: a box that carries
    its params is left alone.
    """
    write_map(tmp_path)
    entries = build_census()
    schedule = replace(_SCHEDULE, batch_size=64)
    coordinate = replace(
        _COORDINATE, params={"credit.lr": 0.01, "geometry.hidden_dim": 128}
    )
    box = _box_summary(coordinate, schedule)
    update_map(
        tmp_path,
        entries,
        {
            "cells": [
                {
                    "primitive": entries[0].id,
                    "status": "MEASURED",
                    "val_acc": 0.5,
                    "loss": 1.0,
                    "param_count": 10,
                    "within_ceiling": True,
                    "walltime_s": 1.0,
                    "box": {key: value for key, value in box.items() if "." not in key},
                    "ruler": "val_acc on mnist",
                    "control_val_acc": 0.89,
                    "binding": "bound",
                    "binding_reason": None,
                    "swapped": False,
                }
            ]
        },
    )
    update_cell_log(
        tmp_path,
        [
            {
                "track": "P0",
                "primitive": entries[0].id,
                "status": "MEASURED",
                "record": {
                    "params": {key: value for key, value in box.items() if "." in key}
                },
            }
        ],
    )

    assert repair_boxes(tmp_path) == 1
    row = json.loads((tmp_path / "map.json").read_text())["primitives"][entries[0].id]
    assert row["box"] == box
    assert repair_boxes(tmp_path) == 0


def test_the_cell_log_carries_a_record_and_a_screen(tmp_path: Path) -> None:
    update_cell_log(tmp_path, [{"track": "P0", "primitive": "x", "record": None}])
    line = json.loads((tmp_path / "cells.jsonl").read_text())
    assert line["screen"]["primitive"] == "x"
    assert "record" in line


def test_every_map_row_has_its_box(tmp_path: Path) -> None:
    """A screened row is comparable only with the box it ran at (TODO95 S2b)."""
    entries = build_census()
    box = _box_summary(_COORDINATE, _SCHEDULE)
    measured = {
        "primitive": entries[0].id,
        "status": "MEASURED",
        "val_acc": 0.5,
        "loss": 1.0,
        "param_count": 10,
        "within_ceiling": True,
        "walltime_s": 1.0,
        "box": box,
        "ruler": "val_acc on mnist",
        "control_val_acc": 0.89,
        "binding": "bound",
        "binding_reason": None,
        "swapped": False,
        "record": {"provenance": {"code_sha": "replay-mnist-0"}},
    }
    refused = {
        "primitive": entries[1].id,
        "status": "UNAVAILABLE",
        "reason": "control at chance at this box",
        "ruler": "val_acc on mnist",
        "box": box,
        "rule": "refused at the base box",
    }
    update_map(
        tmp_path,
        entries,
        {
            "cells": [measured, refused],
            "control_val_acc": 0.89,
            "control_spread": 0.0024,
            "bar": 0.106,
            "base_box": box,
        },
    )
    map_data = json.loads((tmp_path / "map.json").read_text())
    rows = map_data["primitives"]
    assert map_data["inventory"]["bar"] == 0.106
    assert map_data["inventory"]["control_spread"] == 0.0024
    for row in rows.values():
        assert {"box", "task", "rule", "control", "resource"} <= set(row)
        if row["last_screened"]:
            assert row["box"]["task"] == _SCHEDULE.task_id, row["primitive"]
            assert row["box"]["batch_size"] == _SCHEDULE.batch_size
            assert row["box"]["batch_limit"] == _SCHEDULE.batch_limit
            assert row["rule"], row["primitive"]
    assert rows[entries[0].id]["replay_hash"] == "replay-mnist-0"
    assert rows[entries[1].id]["replay_hash"] is None
    assert rows[entries[1].id]["trigger"] == "control at chance at this box"
