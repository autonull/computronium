"""Visual verification (C2b/C4): screenshot capture for all views.

Generates reference screenshots for:
- All 4 views (Monitor, Atlas, Repair, Compose)
- Both registers (explorer, lab)
- Empty + populated states
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest

SCREENSHOT_DIR = Path("screenshots/dashboard")

VIEWS = ["monitor", "atlas", "repair", "compose"]
REGISTERS = ["explorer", "lab"]
STATES = ["populated", "empty"]


def _wait_for_source(driver: Any, needle: str, timeout: float = 30.0) -> None:
    """Poll past the 4 s driver implicit wait (atlas fit can exceed it)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if needle in driver.page_source:
            return
        time.sleep(0.25)
    raise AssertionError(f'Page never contained "{needle}" within {timeout}s')


def _switch_view(screen: Any, view: str) -> None:
    """Switch views via the nav button group (labelled buttons)."""
    from selenium.webdriver.common.by import By

    labels = {"monitor": "Monitor", "atlas": "Atlas", "repair": "Repair", "compose": "Compose"}
    target = labels[view]
    for btn in screen.selenium.find_elements(By.CSS_SELECTOR, "button"):
        if btn.text.strip() == target:
            btn.click()
            time.sleep(0.5)
            return
    raise AssertionError(f"Nav button for view {view!r} not found")


def _capture_screenshot(screen: Any, name: str) -> Path:
    """Capture and save a screenshot."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = SCREENSHOT_DIR / f"{name}.png"
    screen.selenium.save_screenshot(str(filepath))
    return filepath


def pytest_addoption(parser: Any) -> None:
    parser.addoption(
        "--capture-screenshots",
        action="store_true",
        default=False,
        help="Enable screenshot capture for visual verification",
    )


def pytest_configure(config: Any) -> None:
    config.addinivalue_line(
        "markers", "screenshots: mark test as capturing screenshots"
    )


def pytest_collection_modifyitems(config: Any, items: list[Any]) -> None:
    """Skip capture tests before fixture setup (screen spins up a server)."""
    if config.getoption("--capture-screenshots"):
        return
    skip = pytest.mark.skip(reason="Use --capture-screenshots to enable capture")
    for item in items:
        if "screenshots" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(scope="session")
def populated_root(tmp_path_factory: Any) -> Path:
    """Create a populated campaign root once per session."""
    from tests.ui.fixture import seed_campaign_root

    root = tmp_path_factory.mktemp("populated") / "broad_map"
    seed_campaign_root(root)
    return root


@pytest.fixture(scope="session")
def empty_root(tmp_path_factory: Any) -> Path:
    """Create an empty campaign root once per session."""
    root = tmp_path_factory.mktemp("empty") / "broad_map"
    root.mkdir(parents=True)
    return root


@pytest.fixture
def capture_screenshots(request: Any) -> bool:
    """Check if screenshot capture is enabled."""
    return request.config.getoption("--capture-screenshots")


class TestDashboardScreenshots:
    """Visual verification: capture all view/register/state combos."""

    @pytest.mark.screenshots
    @pytest.mark.parametrize("state", STATES)
    @pytest.mark.parametrize("register", REGISTERS)
    @pytest.mark.parametrize("view", VIEWS)
    def test_capture_view(
        self,
        capture_screenshots: bool,
        screen: Any,
        state: str,
        register: str,
        view: str,
        populated_root: Path,
        empty_root: Path,
    ) -> None:
        """Capture screenshot for each view/register/state combination.

        Run with: pytest tests/ui/test_dashboard_screenshots.py --capture-screenshots
        """
        from nicegui import ui

        from computronium.ui.dashboard import build_dashboard

        root = populated_root if state == "populated" else empty_root

        # NiceGUI's session driver defaults to a 4 s page-load timeout;
        # the dashboard's first render (glossary + atlas + UMAP) can exceed it.
        screen.selenium.set_page_load_timeout(30)
        # language="en" requests a locale bundle NiceGUI doesn't ship for English.
        # Plotly throws resize error on hidden containers at teardown — external noise.
        screen.allowed_js_errors.extend([
            "lang/en.umd.prod.js",
            "Resize must be passed a displayed plot div",
        ])

        holder = {"root": root, "register": register, "view": view}

        @ui.page(f"/dashboard_screenshot/{view}/{register}", language="en-US")
        def _screenshot_page() -> None:
            build_dashboard(
                holder["root"],
                ui_mode=holder["register"],
                ui_actions=False,
            )

        screen.open(f"/dashboard_screenshot/{view}/{register}", timeout=30)
        _wait_for_source(screen.selenium, "Computronium")
        time.sleep(2)

        _switch_view(screen, view)
        filepath = _capture_screenshot(screen, f"{view}_{register}_{state}")
        print(f"Captured: {filepath}")

    @pytest.mark.screenshots
    def test_capture_all_registers_populated(
        self,
        capture_screenshots: bool,
        screen: Any,
        populated_root: Path,
    ) -> None:
        """Quick capture all registers in populated state."""
        from nicegui import ui

        from computronium.ui.dashboard import build_dashboard

        screen.selenium.set_page_load_timeout(30)
        screen.allowed_js_errors.extend([
            "lang/en.umd.prod.js",
            "Resize must be passed a displayed plot div",
        ])

        for register in REGISTERS:

            @ui.page(f"/dashboard_quick/{register}", language="en-US")
            def _quick_page() -> None:
                build_dashboard(populated_root, ui_mode=register, ui_actions=False)

            screen.open(f"/dashboard_quick/{register}", timeout=30)
            _wait_for_source(screen.selenium, "Computronium")
            time.sleep(2)
            _capture_screenshot(screen, f"overview_{register}_populated")


class TestVisualVerification:
    """Visual verification checks (C4: aesthetic spec)."""

    def test_design_tokens_4px_grid(self) -> None:
        """Verify spacing tokens follow 4px grid (C4a)."""
        from computronium.ui.design_tokens import SPACING

        for name, value in SPACING.items():
            if name == "0":
                continue
            rem_value = float(value.replace("rem", ""))
            assert rem_value % 0.25 == 0, f"Spacing {name}={value} not on 4px grid"

    def test_monospace_data_font_stack(self) -> None:
        """Verify mono font size token exists (C4a)."""
        from computronium.ui.design_tokens import TYPE_SCALE

        assert "mono" in TYPE_SCALE
        assert "mono_sm" in TYPE_SCALE
        assert TYPE_SCALE["mono"] == "0.875rem"  # 14px
        assert TYPE_SCALE["mono_sm"] == "0.75rem"  # 12px

    def test_semantic_colors_defined(self) -> None:
        """Verify semantic colors are defined (C4a)."""
        from computronium.ui.design_tokens import SEMANTIC

        required = ["success", "warning", "danger", "info", "neutral", "secondary"]
        for color in required:
            assert color in SEMANTIC
            assert SEMANTIC[color].startswith("#")

    def test_transition_fast_150ms(self) -> None:
        """Verify fast transition is ≤150ms (C4b)."""
        from computronium.ui.design_tokens import TRANSITIONS

        duration = TRANSITIONS["fast"].split("ms")[0]
        assert int(duration) <= 150, (
            f"Fast transition {TRANSITIONS['fast']} exceeds 150ms"
        )

    def test_reduced_motion_respects_preference(self) -> None:
        """Verify reduced-motion media query disables transitions (C4b)."""
        from computronium.ui.design_tokens import REDUCED_MOTION_CSS

        assert "prefers-reduced-motion: reduce" in REDUCED_MOTION_CSS
        assert "transition-duration: 0.01ms" in REDUCED_MOTION_CSS

    def test_high_contrast_media_query(self) -> None:
        """Verify high-contrast media query exists (C4b)."""
        from computronium.ui.design_tokens import HIGH_CONTRAST_CSS

        assert "prefers-contrast: high" in HIGH_CONTRAST_CSS

    def test_quiet_mode_density(self) -> None:
        """Verify quiet mode tokens exist (C4b)."""
        from computronium.ui.design_tokens import (
            EXPLORER_TOKENS,
            LAB_TOKENS,
        )

        assert EXPLORER_TOKENS.density == "comfortable"
        assert LAB_TOKENS.density == "compact"


class TestDashboardViewRendering:
    """Verify all views render without error (headless)."""

    @pytest.mark.parametrize("view", VIEWS)
    def test_all_views_render_headless(self, view: str, tmp_path: Path) -> None:
        """Verify all views render without error in headless mode."""
        from computronium.ui.dashboard import DashboardApp
        from tests.ui.fixture import seed_campaign_root

        root = tmp_path / "view_test"
        seed_campaign_root(root)

        app = DashboardApp(
            root=root,
            log_path=root / "logs" / "continuous_500.log",
            poll_seconds=2.0,
            daemon_url=None,
            ui_mode="lab",
            ui_actions=False,
            quiet=False,
        )
        app.build()
        app.switch_view(view)
        assert app.view == view
        assert view in app._views


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--capture-screenshots"])
