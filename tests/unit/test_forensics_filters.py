"""Cell forensics (§4.1) + Atlas filters (§4.2) — content beyond the purity lock."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ui.adapters import (
    _defect_cell_keys,
    adapt_cell_forensics,
    adapt_discovery_map,
)
from computronium.ui.data_adapters import AdapterContext
from computronium.ui.state import AtlasFilters, atlas_filters, selected_cell_key
from computronium.visualization.live_atlas import (
    EmbedCache,
    _objectives_from_heartbeat,
    render_snapshot,
    resolve_log_path,
)
from tests.ui.fixture import seed_campaign_root

if TYPE_CHECKING:
    from pathlib import Path


def _context(root: Path) -> AdapterContext:
    snapshot = render_snapshot(
        root,
        resolve_log_path(root, root / "logs" / "continuous_500.log"),
        EmbedCache(),
        objectives=_objectives_from_heartbeat(root),
        with_atlas=False,
    )
    return AdapterContext(root=root, snapshot=snapshot)


def _recurrent_key() -> str:
    return "energy_minimization|prediction|euclidean|recurrent"


def _seed_recurrent_cell(root: Path) -> None:
    from computronium.knowledge import KnowledgeBase, KnowledgeEntry

    kb = KnowledgeBase(root / "kb.sqlite")
    kb.add_entry(
        KnowledgeEntry(
            id="dash_recurrent",
            topic="experiment:mnist",
            model_family="eqprop",
            finding="recurrent fixture cell",
            details="",
            confidence=0.70,
            tags=["experiment", "mnist", "broad_map", "maturity:l0"],
            source="experiment",
            metrics={"final_accuracy": 0.70, "walltime_s": 2.0},
            hyperparameters={
                "geometry": {"topology_type": "recurrent"},
                "dynamics": "energy_minimization",
                "credit": "prediction",
                "update": "euclidean",
            },
            extra={},
        )
    )


def test_forensics_unknown_key(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    ctx = _context(root)
    assert adapt_cell_forensics(ctx.snapshot, root, "nope|nope|nope|nope") is None


def test_forensics_content(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    _seed_recurrent_cell(root)
    ctx = _context(root)
    data = adapt_cell_forensics(ctx.snapshot, root, _recurrent_key())
    assert data is not None
    assert data.accuracy == 0.70
    assert data.maturity == ("l0",)
    assert data.defects and data.defects[0].defect_id == "a1b2c3d4e5f6"
    assert "device poisoning" in data.defects[0].message
    assert isinstance(data.is_pareto, bool)


def test_forensics_best_accuracy_union(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    ctx = _context(root)
    key = "energy_minimization|prediction|euclidean|feedforward"
    data = adapt_cell_forensics(ctx.snapshot, root, key)
    assert data is not None
    assert data.accuracy == 0.83
    assert len(data.bursts) == 2
    assert data.defects == ()


def test_defect_cells_mark_specimens(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    seed_campaign_root(root)
    _seed_recurrent_cell(root)
    assert _recurrent_key() in _defect_cell_keys(root)
    ctx = _context(root)
    specimens = adapt_discovery_map(ctx.snapshot, root).specimens
    flagged = [s for s in specimens if s.key == _recurrent_key()]
    assert flagged and all(s.is_defect for s in flagged)
    assert all(s.maturity == "l0" for s in flagged)


def _probe(
    filters: AtlasFilters,
    *,
    is_pareto: bool = False,
    is_nan: bool = False,
    is_defect: bool = False,
    maturity: str | None = None,
) -> bool:
    return filters.matches(
        key="a|b|c|d",
        dynamics="a",
        credit="b",
        update="c",
        topology="d",
        is_pareto=is_pareto,
        is_nan=is_nan,
        is_defect=is_defect,
        maturity=maturity,
    )


def test_filters_match_axes_outcome_query() -> None:
    assert _probe(AtlasFilters())
    assert not AtlasFilters().active
    assert not _probe(AtlasFilters(dynamics=frozenset({"x"})))
    assert _probe(AtlasFilters(dynamics=frozenset({"a"})))
    assert _probe(AtlasFilters(query="A|B"))
    assert not _probe(AtlasFilters(query="zzz"))
    assert _probe(AtlasFilters(outcome="pareto"), is_pareto=True)
    assert not _probe(AtlasFilters(outcome="pareto"))
    assert _probe(AtlasFilters(outcome="dominated"))
    assert not _probe(AtlasFilters(outcome="dominated"), is_pareto=True)
    assert _probe(AtlasFilters(outcome="diverged"), is_nan=True)
    assert _probe(AtlasFilters(outcome="defect"), is_defect=True)
    assert not _probe(AtlasFilters(outcome="defect"))


def test_filters_maturity_none_tolerant() -> None:
    assert _probe(AtlasFilters(maturity="l1"), maturity=None)
    assert _probe(AtlasFilters(maturity="l1"), maturity="l1")
    assert not _probe(AtlasFilters(maturity="l1"), maturity="l0")


def test_interaction_signals_roundtrip() -> None:
    assert selected_cell_key.peek() is None
    assert not atlas_filters.peek().active
    selected_cell_key.set(_recurrent_key())
    assert selected_cell_key.peek() == _recurrent_key()
    atlas_filters.set(AtlasFilters(query="recurrent"))
    assert atlas_filters.peek().active
    selected_cell_key.set(None)
    atlas_filters.set(AtlasFilters())
    assert selected_cell_key.peek() is None
    assert not atlas_filters.peek().active
