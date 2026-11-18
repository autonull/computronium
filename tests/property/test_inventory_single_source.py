"""Lock: one inventory (TODO95 D1 / P0a).

The census used to read ``schema.primitives.ALL_PRIMITIVES``, a hand list of 62
rows that dropped 11 credits/updates the axis registry composes. This test fails
if any axis row is missing from the census, if the two spec-only rows stop being
named gaps, or if the map stops carrying one row per censused primitive.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.acceleration.registry import primitives
from computronium.acceleration.spec import coordinate_of_id
from computronium.experiment.schema.axis import AXES_REGISTRIES
from computronium.experiment.sec_census import GAP_REASON, build_census, write_census
from computronium.experiment.sec_loop import update_map

if TYPE_CHECKING:
    from pathlib import Path

_SPEC_ONLY = {
    ("substrate", "noisy"),
    ("plasticity", "closed_form_ridge"),
}
_UNAVAILABLE_AXIS_ROWS = {
    "primitive.plasticity.rule_state",
    "primitive.plasticity.substrate_coupled",
}


def _axis_rows() -> set[tuple[str, str]]:
    return {
        (axis.value, name)
        for axis, registry in AXES_REGISTRIES.items()
        for name, _spec in registry.items()
    }


def test_the_census_is_the_spec_registry() -> None:
    entries = build_census()
    assert [entry.id for entry in entries] == sorted(spec.id for spec in primitives())


def test_every_axis_row_has_a_census_entry() -> None:
    covered = {coordinate_of_id(entry.id) for entry in build_census()}
    axis_rows = _axis_rows()
    assert len(axis_rows) == 73
    assert axis_rows <= covered
    assert covered - axis_rows == _SPEC_ONLY
    assert len(covered) == 75


def test_the_spec_only_rows_are_named_capability_gaps() -> None:
    gaps = {entry.id: entry for entry in build_census() if not entry.available}
    assert {
        "primitive.substrate.noisy",
        "primitive.plasticity.closed_form_ridge",
    } <= set(gaps)
    assert gaps["primitive.substrate.noisy"].unavailable_reason == GAP_REASON
    assert (
        gaps["primitive.plasticity.closed_form_ridge"].unavailable_reason == GAP_REASON
    )
    assert set(gaps) == _UNAVAILABLE_AXIS_ROWS | {
        f"primitive.{axis}.{name}" for axis, name in _SPEC_ONLY
    }
    assert all(entry.screen_status == "refused" for entry in gaps.values())


def test_census_json_prints_the_inventory(tmp_path: Path) -> None:
    write_census(tmp_path, build_census())
    data = json.loads((tmp_path / "census.json").read_text())
    assert data["total_primitives"] == 75
    assert data["available"] == 71
    assert len(data["gaps"]) == 4
    assert sum(row["total"] for row in data["by_axis"].values()) == 75


def test_the_map_has_one_row_per_censused_primitive(tmp_path: Path) -> None:
    entries = build_census()
    update_map(tmp_path, entries, p0_result=None)
    map_data = json.loads((tmp_path / "map.json").read_text())
    assert map_data["version"] == "SEC-v3"
    assert map_data["inventory"]["total"] == 75
    rows = map_data["primitives"]
    assert set(rows) == {entry.id for entry in entries}
    assert {row["status"] for row in rows.values()} <= {
        "measured",
        "defect",
        "refused",
        "unmeasured",
    }
    for row in rows.values():
        if row["status"] == "refused":
            assert row["trigger"], row["primitive"]
        assert "best_coordinate" not in row


def test_a_v3_map_keeps_rows_a_later_run_did_not_screen(tmp_path: Path) -> None:
    entries = build_census()
    measured = entries[0]
    cell = {
        "primitive": measured.id,
        "status": "MEASURED",
        "val_acc": 0.5,
        "loss": 1.0,
        "param_count": 10,
        "within_ceiling": True,
        "walltime_s": 1.0,
        "box": {"task": "mnist", "seed": 0},
        "ruler": "val_acc on mnist",
        "control_val_acc": 0.89,
        "binding": "bound",
        "binding_reason": None,
        "swapped": False,
    }
    update_map(
        tmp_path,
        entries,
        {"cells": [cell], "control_val_acc": 0.89, "base_box": {"task": "mnist"}},
    )
    update_map(
        tmp_path,
        entries,
        {"cells": [], "control_val_acc": 0.89, "base_box": {"task": "mnist"}},
    )

    rows = json.loads((tmp_path / "map.json").read_text())["primitives"]
    assert rows[measured.id]["status"] == "measured"
    assert rows[measured.id]["measurement"]["val_acc"] == 0.5
    assert rows[entries[1].id]["status"] == "unmeasured"
