"""Visual verification (C2b/C4): screenshot capture for all panels + lenses.

Generates reference screenshots for:
- All 5 panels (Map, Repair, Console, Composer, Record)
- All lenses per panel (Map: 3, Repair: 2, Record: 3)
- Both registers (explorer, lab)
- Empty + populated states
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest

SCREENSHOT_DIR = Path("screenshots/dashboard")

# ──────────────────────────────────────────────────────────────────────────────
# Panel + Lens combinations to capture
# ──────────────────────────────────────────────────────────────────────────────

PANEL_LENS_MAP = {
    "map": ["map", "tradeoffs", "gallery"],
    "repair": ["defects", "maturation"],
    "console": [None],
    "composer": [None],
    "record": ["history", "ledger", "lessons"],
}

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


def _switch_panel_and_lens(screen: Any, panel: str, lens: str | None) -> None:
    """Switch to a panel and lens via the UI."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as ec
    from selenium.webdriver.support.ui import WebDriverWait

    # Click panel tab (1-5 hotkeys via tab index)
    tab_index = ["map", "repair", "console", "composer", "record"].index(panel)
    tabs = screen.selenium.find_elements(By.CSS_SELECTOR, "div.q-tabs__content button")
    if tabs and tab_index < len(tabs):
        tabs[tab_index].click()
        time.sleep(0.5)

    # If panel has lenses, switch lens via dropdown
    if lens:
        # Find lens selector - usually a select element in the panel
        try:
            lens_select = WebDriverWait(screen.selenium, 5).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    f"div.q-panel[data-panel='{panel}'] select, .lens-selector select",
                ))
            )
            # Select the lens
            from selenium.webdriver.support.ui import Select

            Select(lens_select).select_by_value(lens)
            time.sleep(0.5)
        except Exception:
            # Lens switching might be via tabs or buttons
            lens_buttons = screen.selenium.find_elements(
                By.CSS_SELECTOR, f"button[aria-label*='{lens}'], .lens-tab"
            )
            for btn in lens_buttons:
                if (
                    lens.lower() in btn.text.lower()
                    or lens.lower() in btn.get_attribute("aria-label", "").lower()
                ):
                    btn.click()
                    time.sleep(0.5)
                    break


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
    """Visual verification: capture all panel/lens/register/state combos."""

    @pytest.mark.parametrize("state", STATES)
    @pytest.mark.parametrize("register", REGISTERS)
    @pytest.mark.parametrize("panel,lenses", list(PANEL_LENS_MAP.items()))
    def test_capture_panel_lens(
        self,
        screen: Any,
        state: str,
        register: str,
        panel: str,
        lenses: list[str | None],
        populated_root: Path,
        empty_root: Path,
        capture_screenshots: bool,
    ) -> None:
        """Capture screenshot for each panel/lens/register/state combination.

        Run with: pytest tests/ui/test_dashboard_screenshots.py --capture-screenshots
        """
        if not capture_screenshots:
            pytest.skip("Use --capture-screenshots to enable screenshot capture")

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

        holder = {"root": root, "register": register}

        @ui.page(f"/dashboard_screenshot/{panel}/{lenses[0] or 'none'}", language="en-US")
        def _screenshot_page() -> None:
            build_dashboard(
                holder["root"],
                ui_mode=holder["register"],
                ui_actions=False,
            )

        # Navigate to page
        screen.open(f"/dashboard_screenshot/{panel}/{lenses[0] or 'none'}", timeout=30)
        _wait_for_source(screen.selenium, "Computronium")

        # Wait for initial render
        time.sleep(2)

        # Capture base panel
        for lens in lenses:
            if lens:
                _switch_panel_and_lens(screen, panel, lens)
            name = f"{panel}_{lens or 'base'}_{register}_{state}"
            filepath = _capture_screenshot(screen, name)
            print(f"Captured: {filepath}")

    def test_capture_all_registers_populated(
        self,
        screen: Any,
        populated_root: Path,
        capture_screenshots: bool,
    ) -> None:
        """Quick capture all registers in populated state."""
        if not capture_screenshots:
            pytest.skip("Use --capture-screenshots to enable screenshot capture")

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
            # All spacing should be multiples of 0.25rem (4px)
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

        # fast = "150ms ease"
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

        # Explorer = comfortable, Lab = compact (quiet density)
        assert EXPLORER_TOKENS.density == "comfortable"
        assert LAB_TOKENS.density == "compact"


class TestDashboardLensRendering:
    """Verify all lenses render without error (headless)."""

    @pytest.mark.parametrize("panel,lenses", list(PANEL_LENS_MAP.items()))
    def test_all_lenses_render_headless(
        self,
        panel: str,
        lenses: list[str | None],
        tmp_path: Path,
    ) -> None:
        """Verify all lenses render without error in headless mode."""
        from computronium.ui.dashboard import DashboardApp
        from tests.ui.fixture import seed_campaign_root

        root = tmp_path / "lens_test"
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

        for lens in lenses:
            if lens:
                app.current_lens = lens
            app.current_panel = panel
            app._render_current_panel()
            assert panel in app._panels


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--capture-screenshots"])
