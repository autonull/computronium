"""Lock: one inventory (TODO95 D1 / P0a).

The census used to read ``schema.primitives.ALL_PRIMITIVES``, a hand list of 62
rows that dropped 11 credits/updates the axis registry composes. This test fails
if any axis row is missing from the census, if a gap stops being declared in
``schema.gaps.GAPS``, or if the map stops carrying one row per censused
primitive.

``noisy`` and ``closed_form_ridge`` now compose their own axis rows, so the
inventory is 75 rows with the two documented no-op plasticities as the only
declared gaps — breadth added, nothing retired.
"""

from __future__ import annotations

import json
from pathlib import Path

from computronium.acceleration.registry import primitives
from computronium.acceleration.spec import coordinate_of_id
from computronium.experiment.schema.axis import AXES_REGISTRIES
from computronium.experiment.schema.gaps import GAPS
from computronium.experiment.sec_census import build_census, write_census
from computronium.experiment.sec_loop import update_map

_GAPS = {
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
    assert len(axis_rows) == 75
    assert axis_rows == covered


def test_gap_table_single_source() -> None:
    gaps = {entry.id: entry for entry in build_census() if not entry.available}
    assert set(gaps) == _GAPS == set(GAPS)
    for primitive_id, entry in gaps.items():
        assert entry.unavailable_reason == GAPS[primitive_id].reason
        assert entry.unavailable_trigger == GAPS[primitive_id].trigger
        assert entry.screen_status == "refused"


def test_census_json_prints_the_inventory(tmp_path: Path) -> None:
    write_census(tmp_path, build_census())
    data = json.loads((tmp_path / "census.json").read_text())
    assert data["total_primitives"] == 75
    assert data["available"] == 73
    assert len(data["gaps"]) == 2
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


def test_map_summary_matches_census(tmp_path: Path) -> None:
    """The map's counts are the census's rows, never a second tally."""
    entries = build_census()
    update_map(tmp_path, entries, p0_result=None)
    data = json.loads((tmp_path / "map.json").read_text())
    census_rows = {entry.id: entry for entry in entries}

    assert data["inventory"]["total"] == len(entries)
    assert data["inventory"]["available"] == sum(entry.available for entry in entries)
    for axis, counts in data["by_axis"].items():
        expected = sum(1 for entry in entries if entry.axis == axis)
        assert sum(counts.values()) == expected, axis
    for row in data["primitives"].values():
        assert row["axis"] == census_rows[row["primitive"]].axis
    assert (
        sum(sum(counts.values()) for counts in data["by_axis"].values())
        == data["inventory"]["total"]
    )


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


def test_spec_composes() -> None:
    """No primitive ships without a coordinate and without a declared reason."""
    axis_rows = _axis_rows()
    for spec in primitives():
        coordinate = coordinate_of_id(spec.id)
        assert coordinate is not None, spec.id
        assert coordinate in axis_rows or spec.id in GAPS, spec.id


def test_one_record_version() -> None:
    """``MAP_VERSION`` is the only record version literal in the package."""
    repo = Path(__file__).resolve().parents[2]
    source = (repo / "computronium").rglob("*.py")
    offenders = [
        path.relative_to(repo)
        for path in source
        if '"SEC-v' in path.read_text(encoding="utf-8", errors="ignore")
        and path.name != "sec_census.py"
    ]
    assert offenders == []


def test_readme_counts_match_census() -> None:
    """The README's generated counts read the registry, not prose."""
    from tests.property._readme import load_readme_builder

    builder = load_readme_builder()
    entries = build_census()
    assert builder._primitive_total() == str(sum(row.available for row in entries))
    for axis, registry in AXES_REGISTRIES.items():
        generator = builder._GENERATORS[f"{axis.value}_count"]
        assert generator() == str(
            sum(1 for spec in registry.values() if spec.available)
        ), axis.value
