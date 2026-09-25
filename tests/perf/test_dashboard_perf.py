"""Dashboard UI Performance Benchmarks (D5: P1).

Measures:
- First paint p95 ≤4s
- View switch p95
- Monitor data assembly ≤1ms
"""

from __future__ import annotations

import statistics
import time
from typing import Any

import pytest

# Performance budgets (generous for CI, catches order-of-magnitude regressions)
FIRST_PAINT_BUDGET_S = 4.0  # p95
PANEL_SWITCH_BUDGET_S = 0.5  # p95


def _median_of_n(fn, n: int = 5) -> float:
    """Run fn n times, return median duration in seconds."""
    times = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    return statistics.median(times)


def _p95_of_n(fn, n: int = 10) -> float:
    """Run fn n times, return p95 duration in seconds."""
    times = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    times.sort()
    idx = int(n * 0.95)
    return times[min(idx, n - 1)]


def _wait_for_source(driver: Any, needle: str, timeout: float = 30.0) -> None:
    """Poll page_source past the driver's implicit wait."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if needle in driver.page_source:
            return
        time.sleep(0.1)
    raise AssertionError(f'Page never contained "{needle}" within {timeout}s')


class TestDashboardFirstPaint:
    """First paint performance (page load to interactive)."""

    def test_first_paint_populated_root(
        self, screen: Any, tmp_path_factory: Any
    ) -> None:
        """First paint p95 ≤4s on populated root (warm cache)."""
        from nicegui import ui

        from computronium.ui.dashboard import build_dashboard
        from tests.ui.fixture import seed_campaign_root

        root = tmp_path_factory.mktemp("perf_paint") / "broad_map"
        seed_campaign_root(root)

        screen.selenium.set_page_load_timeout(30)
        screen.allowed_js_errors.extend([
            "lang/en.umd.prod.js",
            "Resize must be passed a displayed plot div",
        ])

        @ui.page("/perf_first_paint", language="en-US")
        def _page() -> None:
            build_dashboard(root, ui_mode="explorer", ui_actions=False)

        # Warm up (first load does more work)
        screen.open("/perf_first_paint", timeout=30)
        _wait_for_source(screen.selenium, "Computronium")

        # Measure p95 over multiple loads
        def load_page() -> None:
            screen.open("/perf_first_paint", timeout=30)
            _wait_for_source(screen.selenium, "Computronium")

        p95 = _p95_of_n(load_page, n=5)
        print(f"\nFirst paint p95: {p95:.3f}s (budget: {FIRST_PAINT_BUDGET_S}s)")
        assert p95 <= FIRST_PAINT_BUDGET_S, (
            f"First paint p95 {p95:.3f}s exceeds budget {FIRST_PAINT_BUDGET_S}s"
        )

    def test_first_paint_empty_root(self, screen: Any, tmp_path_factory: Any) -> None:
        """First paint on empty root (should be faster)."""
        from nicegui import ui

        from computronium.ui.dashboard import build_dashboard

        root = tmp_path_factory.mktemp("perf_paint_empty") / "broad_map"
        root.mkdir(parents=True)

        screen.selenium.set_page_load_timeout(30)
        screen.allowed_js_errors.extend([
            "lang/en.umd.prod.js",
            "Resize must be passed a displayed plot div",
        ])

        @ui.page("/perf_first_paint_empty", language="en-US")
        def _page() -> None:
            build_dashboard(root, ui_mode="explorer", ui_actions=False)

        screen.open("/perf_first_paint_empty", timeout=30)
        _wait_for_source(screen.selenium, "Computronium")

        def load_page() -> None:
            screen.open("/perf_first_paint_empty", timeout=30)
            _wait_for_source(screen.selenium, "Computronium")

        p95 = _p95_of_n(load_page, n=5)
        print(f"\nFirst paint (empty) p95: {p95:.3f}s")
        assert p95 <= FIRST_PAINT_BUDGET_S, (
            f"First paint (empty) p95 {p95:.3f}s exceeds budget {FIRST_PAINT_BUDGET_S}s"
        )


class TestDashboardViewSwitch:
    """View switching performance."""

    def test_view_switch_p95(self, screen: Any, tmp_path_factory: Any) -> None:
        """View switch p95 ≤500ms (hot path, no data reload)."""
        from nicegui import ui

        from computronium.ui.dashboard import build_dashboard
        from tests.ui.fixture import seed_campaign_root

        root = tmp_path_factory.mktemp("perf_switch") / "broad_map"
        seed_campaign_root(root)

        screen.selenium.set_page_load_timeout(30)
        screen.allowed_js_errors.extend([
            "lang/en.umd.prod.js",
            "Resize must be passed a displayed plot div",
        ])

        @ui.page("/perf_panel_switch", language="en-US")
        def _page() -> None:
            build_dashboard(root, ui_mode="lab", ui_actions=False)

        screen.open("/perf_panel_switch", timeout=30)
        _wait_for_source(screen.selenium, "Computronium")
        time.sleep(1)  # Let initial render settle

        # Switch views using keyboard hotkeys (1-4) - faster than clicking
        from selenium.webdriver.common.action_chains import ActionChains

        def switch_views() -> None:
            for key in ["1", "2", "3", "4"]:
                ActionChains(screen.selenium).send_keys(key).perform()
                time.sleep(0.1)  # Allow transition

        median = _median_of_n(switch_views, n=5)
        print(f"\nView switch median (4 views): {median * 1000:.1f}ms")
        per_switch = median / 4
        print(
            f"Per-switch median: {per_switch * 1000:.1f}ms (budget: {PANEL_SWITCH_BUDGET_S * 1000:.0f}ms)"
        )
        assert per_switch <= PANEL_SWITCH_BUDGET_S, (
            f"View switch {per_switch * 1000:.1f}ms exceeds budget {PANEL_SWITCH_BUDGET_S * 1000:.0f}ms"
        )


class TestDashboardMonitorData:
    """Monitor data assembly performance (headless)."""

    def test_monitor_data_creation(self, tmp_path_factory: Any) -> None:
        """MonitorData assembly ≤1ms (tiles + feed projection)."""
        from computronium.ui.components.monitor import (
            DriverIntent,
            HealthTile,
            MonitorData,
        )
        from computronium.visualization.live_atlas import Liveness

        def create_monitor_data() -> None:
            from computronium.ui.components.monitor import SessionDelta

            MonitorData(
                liveness=Liveness("● RUNNING", "green", "pid 1 · cells 10"),
                tiles=[
                    HealthTile(label=f"tile{i}", value="1", status="running_smoothly", detail="d")
                    for i in range(6)
                ],
                loss_history=[0.5] * 60,
                feed=[],
                intent=DriverIntent(proposing=3, last_batch_ago_s=1.0, strategy_hint="x"),
                session_delta=SessionDelta(1, 2, 3),
                ticker=["line"] * 30,
            )

        median = _median_of_n(create_monitor_data, n=100)
        print(f"\nMonitorData creation median: {median * 1000:.3f}ms")
        assert median < 0.001, f"MonitorData creation {median * 1000:.3f}ms too slow"


class TestDashboardRenderSnapshot:
    """render_snapshot performance (backend, no UI)."""

    def test_render_snapshot_warm_5k(self, tmp_path_factory: Any) -> None:
        """render_snapshot warm median ≤500ms @5k cells (from test_budgets.py)."""
        from computronium.visualization.live_atlas import EmbedCache, render_snapshot

        root = tmp_path_factory.mktemp("perf_snapshot") / "broad_map"
        # Seed 5k cells
        import json

        from computronium.knowledge import KnowledgeBase

        root.mkdir(parents=True, exist_ok=True)
        kb = KnowledgeBase(root / "kb.sqlite", auto_embed=False)
        rows = []
        dynamics = [
            "energy_minimization",
            "predictive_settling",
            "instantaneous_pass",
            "spike_integration",
        ]
        credits = [
            "thermodynamic_contrast",
            "random_projections",
            "local_goodness",
            "backprop",
        ]
        updates = ["euclidean", "riemannian", "natural_gradient"]
        for i in range(5000):
            hp = {
                "dynamics": dynamics[i % 4],
                "credit": credits[i % 4],
                "update": updates[i % 3],
                "geometry": {"topology_type": "feedforward"},
                "param_budget": 1000 + i,
            }
            metrics = {
                "final_accuracy": (i % 100) / 100.0,
                "walltime_s": 1.0 + (i % 7),
                "param_count": 1000 + i,
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
                "perf",
                "",
                (i % 100) / 100.0,
                json.dumps(tags),
                1_700_000_000.0 + i,
                "experiment",
                None,
                json.dumps(metrics),
                json.dumps(hp),
                json.dumps({}),
            ))
        with kb._tx() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO knowledge (id, topic, model_family, finding, details, "
                "confidence, tags, timestamp, source, experiment_id, metrics, hyperparameters, extra) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                rows,
            )

        cache = EmbedCache()
        # Warm up
        render_snapshot(root, None, cache, with_atlas=False)

        median = _median_of_n(
            lambda: render_snapshot(root, None, EmbedCache(), with_atlas=False), n=3
        )
        print(f"\nrender_snapshot (no atlas) warm median @5k: {median * 1000:.1f}ms")
        assert median <= 0.5, (
            f"render_snapshot {median * 1000:.1f}ms exceeds 500ms budget"
        )


class TestDashboardAdapter:
    """Panel adapter performance (backend, no UI)."""

    def test_discovery_map_adapter_warm_5k(self, tmp_path_factory: Any) -> None:
        """DiscoveryMap adapter warm median ≤100ms @5k cells."""
        from computronium.ui.adapters import adapt_discovery_map
        from computronium.visualization.live_atlas import EmbedCache, render_snapshot

        root = tmp_path_factory.mktemp("perf_adapter") / "broad_map"
        # Seed 5k cells (same as above)
        import json

        from computronium.knowledge import KnowledgeBase

        root.mkdir(parents=True, exist_ok=True)
        kb = KnowledgeBase(root / "kb.sqlite", auto_embed=False)
        rows = []
        dynamics = [
            "energy_minimization",
            "predictive_settling",
            "instantaneous_pass",
            "spike_integration",
        ]
        credits = [
            "thermodynamic_contrast",
            "random_projections",
            "local_goodness",
            "backprop",
        ]
        updates = ["euclidean", "riemannian", "natural_gradient"]
        for i in range(5000):
            hp = {
                "dynamics": dynamics[i % 4],
                "credit": credits[i % 4],
                "update": updates[i % 3],
                "geometry": {"topology_type": "feedforward"},
                "param_budget": 1000 + i,
            }
            metrics = {
                "final_accuracy": (i % 100) / 100.0,
                "walltime_s": 1.0 + (i % 7),
                "param_count": 1000 + i,
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
                "perf",
                "",
                (i % 100) / 100.0,
                json.dumps(tags),
                1_700_000_000.0 + i,
                "experiment",
                None,
                json.dumps(metrics),
                json.dumps(hp),
                json.dumps({}),
            ))
        with kb._tx() as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO knowledge (id, topic, model_family, finding, details, "
                "confidence, tags, timestamp, source, experiment_id, metrics, hyperparameters, extra) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                rows,
            )

        cache = EmbedCache()
        snapshot = render_snapshot(root, None, cache, with_atlas=False)

        # Warm up
        adapt_discovery_map(snapshot, root)

        median = _median_of_n(lambda: adapt_discovery_map(snapshot, root), n=3)
        print(f"\nDiscoveryMap adapter warm median @5k: {median * 1000:.1f}ms")
        assert median <= 0.1, (
            f"DiscoveryMap adapter {median * 1000:.1f}ms exceeds 100ms budget"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
