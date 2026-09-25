"""UX-L15: adapter output fields match source rows (L4 equivalence)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest

from computronium.ui.adapters import (
    adapt_discovery_map,
    adapt_health_panel,
    adapt_repair_bench,
    adapt_tradeoffs_panel,
)
from computronium.visualization.live_atlas import render_snapshot
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def test_repair_bench_matches_funnel_rows(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    snapshot = render_snapshot(root, with_atlas=False)
    data = adapt_repair_bench(snapshot, root)
    assert {d.defect_id for d in data.defects} == {
        row["defect_id"] for row in snapshot.funnel_rows
    }
    assert data.defects[0].status == "open"
    assert "0x7f00" in data.defects[0].message


def test_health_tiles_match_snapshot_health(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    snapshot = render_snapshot(root, with_atlas=False)
    tiles = {t.label: t.value for t in adapt_health_panel(snapshot, root)}
    health = snapshot.health
    assert tiles["Open Defects"] == str(health["open_defects"])
    assert tiles["Measured Cells"] == str(health["measured_cells"])
    assert tiles["Cells / Burst"] == str(health["cells_per_burst"])


def test_discovery_map_specimens_match_measured_cells(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    snapshot = render_snapshot(root, with_atlas=False)
    data = adapt_discovery_map(snapshot, root)
    measured = {s.key for s in data.specimens if not s.is_void}
    assert len(measured) >= 1
    assert all(isinstance(s.is_pareto, bool) for s in data.specimens)
    # top-accuracy cell (0.83) sits on the Pareto front
    assert any(s.is_pareto for s in data.specimens)
    # regions derived from the 3×3 grid over the layout bounds
    assert data.regions


def test_tradeoffs_accuracy_values_from_pareto_front(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    snapshot = render_snapshot(root, with_atlas=False)
    data = adapt_tradeoffs_panel(snapshot, root)
    assert data.pareto_cells, "pareto front populated"
    source_accuracies = {
        float(cast("str", row["accuracy"])) for row in snapshot.pareto_rows
    }
    assert {c.metrics["accuracy"] for c in data.pareto_cells} <= source_accuracies
    assert data.pareto_cells[0].metrics["accuracy"] == pytest.approx(0.83)
