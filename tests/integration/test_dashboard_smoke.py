"""Dashboard smoke (TODO29 Phase 5): one headless render pass over a
fixture campaign root + artifact-signature change detection."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from computronium.visualization.live_atlas import (
    EmbedCache,
    build_dashboard,
    defect_funnel_rows,
    health_stats,
    log_tail,
    render_snapshot,
    watch_signature,
)

if TYPE_CHECKING:
    from pathlib import Path

_CELL_HP = {
    "geometry": {"topology_type": "feedforward", "depth": 2, "hidden_dim": 64},
    "dynamics": "energy_minimization",
    "credit": "prediction",
    "update": "euclidean",
    "param_budget": 25000,
}


def _seed_fixture(root: Path) -> None:
    """Tiny KB (4 measured cells across 2 bursts) + voids + defects + log."""
    from computronium.knowledge import KnowledgeBase, KnowledgeEntry

    (root / "logs").mkdir(parents=True, exist_ok=True)
    kb = KnowledgeBase(root / "kb.sqlite")
    for i, (burst, acc) in enumerate((
        ("burst:2026-09-16-1", 0.80),
        ("burst:2026-09-16-1", 0.65),
        ("burst:2026-09-16-2", 0.83),
        ("burst:2026-09-16-2", 0.60),
    )):
        kb.add_entry(
            KnowledgeEntry(
                id=f"dash_{i}",
                topic="experiment:mnist",
                model_family="eqprop",
                finding="fixture cell",
                details="",
                confidence=acc,
                tags=["experiment", "mnist", "broad_map", "maturity:l0", burst],
                source="experiment",
                metrics={
                    "final_accuracy": acc,
                    "walltime_s": 1.5 + i * 0.1,
                    "settle_horizon": 4,
                    "credit_alignment": 0.4,
                },
                hyperparameters=dict(_CELL_HP),
                extra={},
            )
        )
    row = {
        "timestamp": 1.0,
        "task": "mnist",
        "dynamics": "spike_integration",
        "credit": "prediction",
        "update": "euclidean",
        "topology": "recurrent",
        "category": "geometry_constraint",
        "error": "Spike integration dynamics requires temporal trace",
    }
    (root / "structural_voids.jsonl").write_text(
        json.dumps(row) + "\n", encoding="utf-8"
    )
    defect = {
        "defect_id": "a1b2c3d4e5f6",
        "timestamp": 2.0,
        "task": "mnist",
        "cell": "energy_minimization|prediction|euclidean|recurrent",
        "error_class": "RuntimeError",
        "message": "device poisoning at 0x7f00",
        "traceback_tail": "",
        "status": "open",
    }
    (root / "runtime_defects.jsonl").write_text(
        json.dumps(defect) + "\n", encoding="utf-8"
    )
    (root / "logs" / "continuous_500.log").write_text(
        "\n".join(f"line {i}" for i in range(40)) + "\n", encoding="utf-8"
    )


def test_snapshot_render_pass_produces_all_panels(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    _seed_fixture(root)
    snapshot = render_snapshot(root, root / "logs" / "continuous_500.log")

    health = snapshot.health
    assert health["measured_cells"] == 4
    assert health["bursts"] == 2
    assert health["cells_per_burst"] == 2.0
    assert health["open_defects"] == 1
    assert isinstance(health["last_burst_walltime_s"], float)

    assert len(snapshot.funnel_rows) == 1
    funnel = snapshot.funnel_rows[0]
    assert funnel["defect_id"] == "a1b2c3d4e5f6"
    assert funnel["status"] == "open"
    assert "0x7f00" in str(funnel["message"])

    assert len(snapshot.pareto_rows) >= 1  # bp_deficit is 0 without a ruler:
    # the non-dominated front is the top-accuracy tier only.
    assert (
        float(snapshot.pareto_rows[0]["accuracy"])  # type: ignore[arg-type]
        == 0.83
    )

    assert snapshot.atlas is not None  # islands figure rendered
    assert snapshot.layout_note is not None and "n=5" in snapshot.layout_note
    assert len(snapshot.ticker) == 30  # last 30 log lines
    assert snapshot.ticker[-1] == "line 39"


def test_embed_cache_refits_only_on_cell_count_change(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    _seed_fixture(root)
    cache = EmbedCache()
    first = render_snapshot(root, cache=cache)
    n_first = cache.n
    second = render_snapshot(root, cache=cache)
    assert cache.n == n_first  # same cell count: layout reused
    assert first.atlas is not None and second.atlas is not None


def test_signature_triggers_on_artifact_change(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    _seed_fixture(root)
    before = watch_signature(root)
    assert before  # artifacts exist

    with (root / "runtime_defects.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({}) + "\n")
    assert watch_signature(root) != before


def test_ticker_and_log_resolution(tmp_path: Path) -> None:
    root = tmp_path / "broad_map"
    _seed_fixture(root)
    from computronium.visualization.live_atlas import resolve_log_path

    assert resolve_log_path(root, None) == root / "logs" / "continuous_500.log"
    assert log_tail(root / "logs" / "continuous_500.log", lines=5)[-1] == "line 39"
    assert log_tail(None) == []


def test_build_dashboard_headless(tmp_path: Path) -> None:
    """The NiceGUI page builds without a live loop (no ui.run)."""
    root = tmp_path / "broad_map"
    _seed_fixture(root)
    build_dashboard(root, root / "logs" / "continuous_500.log", poll_seconds=2.0)
    assert defect_funnel_rows(root / "runtime_defects.jsonl")
    assert health_stats(root)["measured_cells"] == 4
