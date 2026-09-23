"""D2 performance budgets (invoke by path — tests/perf is not in testpaths).

Budgets are generous medians on a warm 5k-cell root: they catch order-of-
magnitude regressions (the pre-D2 hotspots) without being machine-brittle.
"""

from __future__ import annotations

import json
import statistics
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    import pytest

N_CELLS = 5000
ADAPTER_BUDGET_S = 0.100  # DiscoveryMap adapter, warm, median-of-3 @5k
SNAPSHOT_BUDGET_S = 3.0  # render_snapshot (no atlas), warm, median-of-3 @5k

_DYNAMICS = (
    "energy_minimization",
    "predictive_settling",
    "instantaneous_pass",
    "spike_integration",
)
_CREDITS = (
    "thermodynamic_contrast",
    "random_projections",
    "local_goodness",
    "backprop",
)
_UPDATES = ("euclidean", "riemannian", "natural_gradient")


def _seed_bulk(root: Path, n: int) -> None:
    """Bulk-load n measured cells in one transaction (no per-row commit)."""
    from computronium.knowledge import KnowledgeBase

    root.mkdir(parents=True, exist_ok=True)
    kb = KnowledgeBase(root / "kb.sqlite", auto_embed=False)
    rows = []
    for i in range(n):
        hyperparameters = {
            "dynamics": _DYNAMICS[i % len(_DYNAMICS)],
            "credit": _CREDITS[i % len(_CREDITS)],
            "update": _UPDATES[i % len(_UPDATES)],
            "geometry": {"topology_type": "feedforward"},
            "param_budget": 1000 + i,
        }
        metrics = {
            "final_accuracy": (i % 100) / 100.0,
            "walltime_s": 1.0 + (i % 7),
            "param_count": 1000 + i,
            "nan_loss": i % 50 == 0,
        }
        tags = [
            "experiment",
            "mnist",
            f"burst:2026-09-20-{i // 1000:02d}",
            "maturity:l0",
        ]
        rows.append((
            f"perf{i}",
            "experiment:mnist",
            "eqprop",
            "perf fixture cell",
            "",
            (i % 100) / 100.0,
            json.dumps(tags),
            1_700_000_000.0 + i,
            "experiment",
            None,
            json.dumps(metrics),
            json.dumps(hyperparameters),
            json.dumps({}),
        ))
    with kb._tx() as conn:
        conn.executemany(
            "INSERT OR REPLACE INTO knowledge (id, topic, model_family, finding, "
            "details, confidence, tags, timestamp, source, experiment_id, metrics, "
            "hyperparameters, extra) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            rows,
        )


def _median_of_3(fn: Callable[[], object]) -> float:
    times: list[float] = []
    for _ in range(3):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def test_perf_budgets_warm_5k(tmp_path_factory: pytest.TempPathFactory) -> None:
    from computronium.ui.adapters import adapt_discovery_map
    from computronium.visualization.live_atlas import EmbedCache, render_snapshot

    root = tmp_path_factory.mktemp("perf_root") / "broad_map"
    seed_start = time.perf_counter()
    _seed_bulk(root, N_CELLS)
    print(f"\nseeded {N_CELLS} cells in {time.perf_counter() - seed_start:.2f}s")

    snapshot = render_snapshot(root, None, EmbedCache(), with_atlas=False)

    # Warm (loads populate the mtime cache), then median-of-3.
    adapt_discovery_map(snapshot, root)
    adapter_median = _median_of_3(lambda: adapt_discovery_map(snapshot, root))
    print(f"discovery_map adapter warm median @5k: {adapter_median * 1000:.1f} ms")
    assert adapter_median <= ADAPTER_BUDGET_S, (
        f"DiscoveryMap adapter {adapter_median * 1000:.1f} ms > "
        f"{ADAPTER_BUDGET_S * 1000:.0f} ms budget"
    )

    render_snapshot(root, None, EmbedCache(), with_atlas=False)
    snapshot_median = _median_of_3(
        lambda: render_snapshot(root, None, EmbedCache(), with_atlas=False)
    )
    print(f"render_snapshot(no atlas) warm median @5k: {snapshot_median * 1000:.1f} ms")
    assert snapshot_median <= SNAPSHOT_BUDGET_S, (
        f"render_snapshot {snapshot_median * 1000:.1f} ms > "
        f"{SNAPSHOT_BUDGET_S * 1000:.0f} ms budget"
    )


def test_ws_paint_interval_budget() -> None:
    """UX-L5 paint throttle: WS repaints at most every second."""
    from computronium.ui.dashboard import DashboardApp

    assert DashboardApp._WS_PAINT_INTERVAL_S >= 1.0


def test_row_virtualization_cap_constant() -> None:
    from computronium.ui.design_tokens import MAX_RENDERED_ROWS

    assert 0 < MAX_RENDERED_ROWS <= 5000
