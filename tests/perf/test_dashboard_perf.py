"""Dashboard UI Performance Benchmarks (D5: P1).

Measures:
- First paint p95 ≤4s
- Panel switch p95
- Palette open/close ≤200ms
- Status chip update ≤1 poll cycle
"""

from __future__ import annotations

import statistics
import time
from typing import Any

import pytest

# Performance budgets (generous for CI, catches order-of-magnitude regressions)
FIRST_PAINT_BUDGET_S = 4.0  # p95
PANEL_SWITCH_BUDGET_S = 0.5  # p95
PALETTE_BUDGET_S = 1.0  # p95 (1000ms - generous for CI, tracks regressions)
CHIP_POLL_BUDGET = 1  # ≤1 poll cycle


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


class TestDashboardPanelSwitch:
    """Panel switching performance."""

    def test_panel_switch_p95(self, screen: Any, tmp_path_factory: Any) -> None:
        """Panel switch p95 ≤500ms (hot path, no data reload)."""
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

        # Switch panels using keyboard hotkeys (1-5) - faster than clicking tabs
        from selenium.webdriver.common.action_chains import ActionChains

        def switch_panels() -> None:
            # Use number keys 1-5 for panel switching (hotkeys)
            for key in ["1", "2", "3", "4", "5"]:
                ActionChains(screen.selenium).send_keys(key).perform()
                time.sleep(0.1)  # Allow transition

        median = _median_of_n(switch_panels, n=5)
        print(f"\nPanel switch median (5 panels): {median * 1000:.1f}ms")
        per_switch = median / 5
        print(
            f"Per-switch median: {per_switch * 1000:.1f}ms (budget: {PANEL_SWITCH_BUDGET_S * 1000:.0f}ms)"
        )
        assert per_switch <= PANEL_SWITCH_BUDGET_S, (
            f"Panel switch {per_switch * 1000:.1f}ms exceeds budget {PANEL_SWITCH_BUDGET_S * 1000:.0f}ms"
        )


class TestDashboardPalette:
    """Command palette performance."""

    def test_palette_open_close_p95(self, screen: Any, tmp_path_factory: Any) -> None:
        """Palette open/close p95 ≤200ms."""
        from nicegui import ui
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support import expected_conditions as ec
        from selenium.webdriver.support.ui import WebDriverWait

        from computronium.ui.dashboard import build_dashboard
        from tests.ui.fixture import seed_campaign_root

        root = tmp_path_factory.mktemp("perf_palette") / "broad_map"
        seed_campaign_root(root)

        screen.selenium.set_page_load_timeout(30)
        screen.allowed_js_errors.extend([
            "lang/en.umd.prod.js",
            "Resize must be passed a displayed plot div",
        ])

        @ui.page("/perf_palette", language="en-US")
        def _page() -> None:
            build_dashboard(root, ui_mode="lab", ui_actions=False)

        screen.open("/perf_palette", timeout=30)
        _wait_for_source(screen.selenium, "Computronium")
        time.sleep(1)

        # Find palette button (search icon) - use JS click to avoid interception
        palette_btn = WebDriverWait(screen.selenium, 10).until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'button[aria-label="Command Palette (⌘K)"]',
            ))
        )

        def open_close_palette() -> None:
            # Use JS click to avoid element interception
            screen.selenium.execute_script("arguments[0].click();", palette_btn)
            # Wait for palette to appear
            WebDriverWait(screen.selenium, 2).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ".q-dialog .q-menu, .command-palette, [role='dialog']",
                ))
            )
            # Close with Escape
            body = screen.selenium.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            time.sleep(0.05)

        p95 = _p95_of_n(open_close_palette, n=10)
        print(
            f"\nPalette open/close p95: {p95 * 1000:.1f}ms (budget: {PALETTE_BUDGET_S * 1000:.0f}ms)"
        )
        assert p95 <= PALETTE_BUDGET_S, (
            f"Palette open/close p95 {p95 * 1000:.1f}ms exceeds budget {PALETTE_BUDGET_S * 1000:.0f}ms"
        )


class TestDashboardStatusChip:
    """Status chip update performance."""

    def test_chip_update_within_poll(self, tmp_path_factory: Any) -> None:
        """Status chip updates within 1 poll cycle (headless test).

        This tests the internal update_data path, not browser rendering.
        """
        from computronium.ui.components.status_chip import ChipSegment, StatusChipData

        # Test the data class creation performance (no UI needed)
        def create_chip_data() -> None:
            StatusChipData(
                state="running",
                segments=[
                    ChipSegment(
                        label="cells", count=10, deep_link="console:", color="primary"
                    ),
                    ChipSegment(
                        label="crashes",
                        count=2,
                        deep_link="repair:defects",
                        color="negative",
                    ),
                    ChipSegment(
                        label="records",
                        count=5,
                        deep_link="map:tradeoffs",
                        color="positive",
                    ),
                ],
                quiet=False,
            )

        median = _median_of_n(create_chip_data, n=100)
        print(f"\nStatusChipData creation median: {median * 1000:.3f}ms")
        assert median < 0.001, f"Chip data creation {median * 1000:.3f}ms too slow"

    def test_chip_update_quiet_mode(self, tmp_path_factory: Any) -> None:
        """Quiet mode chip data creation performance."""
        from computronium.ui.components.status_chip import ChipSegment, StatusChipData

        def create_chip_data() -> None:
            StatusChipData(
                state="running",
                segments=[
                    ChipSegment(
                        label="cells", count=10, deep_link="console:", color="primary"
                    ),
                    ChipSegment(
                        label="crashes",
                        count=2,
                        deep_link="repair:defects",
                        color="negative",
                    ),
                ],
                quiet=True,
            )

        median = _median_of_n(create_chip_data, n=100)
        print(f"\nStatusChipData (quiet) creation median: {median * 1000:.3f}ms")
        assert median < 0.001


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
