"""UX-L1: Pareto membership rendered == `pareto_top(df, objectives)` for all presets (L4)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from computronium.autoscientist.objectives import (
    DEFAULT_OBJECTIVES,
    PRESET_ACCURACY_WALLTIME_PARAMS,
    PRESET_CREDIT_EFFICIENCY,
    PRESET_CREDIT_EFFICIENCY_FULL,
    PRESET_EFFICIENCY,
    PRESET_FULL_COST,
    PRESET_STABILITY_PLASTICITY,
    PRESET_STABILITY_PLASTICITY_RATIO,
)
from computronium.ui.adapters import adapt_tradeoffs_panel
from computronium.visualization.live_atlas import render_snapshot
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.autoscientist.objectives import ObjectiveSpec

_PRESETS: tuple[tuple[str, tuple[ObjectiveSpec, ...]], ...] = (
    ("default", DEFAULT_OBJECTIVES),
    ("accuracy_walltime_params", PRESET_ACCURACY_WALLTIME_PARAMS),
    ("full_cost", PRESET_FULL_COST),
    ("efficiency", PRESET_EFFICIENCY),
    ("stability_plasticity", PRESET_STABILITY_PLASTICITY),
    ("stability_plasticity_ratio", PRESET_STABILITY_PLASTICITY_RATIO),
    ("credit_efficiency", PRESET_CREDIT_EFFICIENCY),
    ("credit_efficiency_full", PRESET_CREDIT_EFFICIENCY_FULL),
)


def _reference_membership(
    root: Path, objectives: tuple[ObjectiveSpec, ...]
) -> set[tuple[str, float]]:
    """Reference front membership via the same pipeline as pareto_strip_rows."""
    from computronium.visualization.atlas import (
        apply_bp_deficit,
        load_cells,
        pareto_top,
    )

    df = load_cells(root / "kb.sqlite")
    if df.empty:
        return set()
    df = apply_bp_deficit(df, root / "ruler_table.json", None)
    if "nan_loss" in df.columns:
        df = df.query("~nan_loss")
    top = pareto_top(df, k=len(df), objectives=objectives)
    return {
        (
            f"{row['dynamics'][:14]}|{row['credit'][:14]}|{row['update'][:12]}|{row['topology'][:10]}",
            round(float(row["accuracy"]), 6),
        )
        for _, row in top.iterrows()
    }


@pytest.mark.parametrize(("name", "objectives"), _PRESETS, ids=[p[0] for p in _PRESETS])
def test_ux_l1_membership_matches_pareto_top(
    tmp_path: Path, name: str, objectives: tuple[ObjectiveSpec, ...]
) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    snapshot = render_snapshot(root, objectives=objectives, with_atlas=False)
    data = adapt_tradeoffs_panel(snapshot, root)

    rendered = {(c.label, round(c.metrics["accuracy"], 6)) for c in data.pareto_cells}
    reference = _reference_membership(root, objectives)
    assert rendered == reference, (
        f"preset={name}: rendered {rendered} != pareto_top {reference}"
    )


def test_ux_l1_presets_produce_distinct_or_equal_membership(tmp_path: Path) -> None:
    """Sanity: at least two presets are evaluated and front is non-empty."""
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    memberships = []
    for _name, objectives in _PRESETS:
        snapshot = render_snapshot(root, objectives=objectives, with_atlas=False)
        data = adapt_tradeoffs_panel(snapshot, root)
        memberships.append(
            {(c.label, round(c.metrics["accuracy"], 6)) for c in data.pareto_cells}
        )
    assert memberships and all(m for m in memberships), (
        "every preset must yield a non-empty front"
    )
    assert data.objectives == [o.name.value for o in objectives]
