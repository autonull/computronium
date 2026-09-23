"""UX-L5: Accessibility (WCAG 2.2 AA) lock.

Selenium + vendored axe-core scan against an in-process dashboard (C4);
manual keyboard crawl checklist for certification.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

AXE_SOURCE_PATH = Path(__file__).parent / "fixtures" / "axe.min.js"
AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]


def _wait_for_page_source(
    driver: WebDriver, needle: str, timeout: float = 30.0
) -> None:
    """Poll page_source past the driver's 4 s implicit wait (atlas fit can exceed it)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if needle in driver.page_source:
            return
        time.sleep(0.25)
    raise AssertionError(f'Page never contained "{needle}" within {timeout}s')


def _run_axe_scan(driver: WebDriver) -> dict[str, Any]:
    """Run vendored axe-core in-page; returns {"violations": [...]} or {"error": ...}."""
    axe_source = AXE_SOURCE_PATH.read_text(encoding="utf-8")
    driver.execute_script(axe_source)
    payload = driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        axe.run(document, {runOnly: {type: 'tag', values: arguments[0]}})
            .then(r => done(JSON.stringify({violations: r.violations.map(v => ({
                id: v.id,
                impact: v.impact,
                description: v.description,
                nodes: (v.nodes || []).length,
                targets: (v.nodes || []).slice(0, 10).map(n => ({
                    target: n.target,
                    html: (n.html || '').slice(0, 160),
                    summary: (n.failureSummary || '').slice(0, 300),
                })),
            }))})))
            .catch(e => done(JSON.stringify({error: String(e)})));
        """,
        AXE_TAGS,
    )
    data = json.loads(payload)
    if "error" in data:
        pytest.fail(f"axe.run failed: {data['error']}")
    return data


def _has_critical_or_serious(violations: list[dict]) -> bool:
    """Check if result has any critical or serious violations."""
    return any(v["impact"] in {"critical", "serious"} for v in violations)


def _violations_by_severity(violations: list[dict]) -> dict[str, list[dict]]:
    """Group violations by severity."""
    grouped: dict[str, list[dict]] = {
        "critical": [],
        "serious": [],
        "moderate": [],
        "minor": [],
    }
    for v in violations:
        if v["impact"] in grouped:
            grouped[v["impact"]].append(v)
    return grouped


def _assert_no_critical_or_serious(violations: list[dict], label: str) -> None:
    grouped = _violations_by_severity(violations)
    critical_count = len(grouped["critical"])
    serious_count = len(grouped["serious"])
    assert critical_count == 0, (
        f"{label}: {critical_count} critical axe violations:\n"
        + json.dumps(grouped["critical"], indent=2)
    )
    assert serious_count == 0, (
        f"{label}: {serious_count} serious axe violations:\n"
        + json.dumps(grouped["serious"], indent=2)
    )


KEYBOARD_CHECKLIST = [
    {
        "id": "kbd_01",
        "description": "Tab reaches all interactive elements (buttons, links, inputs, selects)",
        "wcag": "2.1.1 Keyboard",
    },
    {
        "id": "kbd_02",
        "description": "Tab order is logical (left-to-right, top-to-bottom)",
        "wcag": "2.4.3 Focus Order",
    },
    {
        "id": "kbd_03",
        "description": "Focus indicator is visible on all interactive elements",
        "wcag": "2.4.7 Focus Visible",
    },
    {
        "id": "kbd_04",
        "description": "No keyboard traps (can tab away from every component)",
        "wcag": "2.1.2 No Keyboard Trap",
    },
    {
        "id": "kbd_05",
        "description": "Skip to main content link works",
        "wcag": "2.4.1 Bypass Blocks",
    },
    {
        "id": "kbd_06",
        "description": "All dialogs/modals trap focus and restore on close",
        "wcag": "2.4.3 Focus Order, 4.1.2 Name Role Value",
    },
    {
        "id": "kbd_07",
        "description": "Dropdowns/comboboxes navigable with arrow keys",
        "wcag": "2.1.1 Keyboard",
    },
    {
        "id": "kbd_08",
        "description": "Carousels/sliders have keyboard controls",
        "wcag": "2.1.1 Keyboard",
    },
    {
        "id": "kbd_09",
        "description": "Custom components have proper ARIA roles/states",
        "wcag": "4.1.2 Name Role Value",
    },
    {
        "id": "kbd_10",
        "description": "Live regions announce dynamic updates (aria-live)",
        "wcag": "4.1.3 Status Messages",
    },
]


class TestA11yAutomated:
    """Automated axe-core accessibility tests (C4: in-process + selenium)."""

    def test_axe_no_critical_or_serious(self, screen: Any, tmp_path: Path) -> None:
        """axe-core scan must have 0 critical/serious violations in both registers."""
        from nicegui import ui

        from computronium.ui.dashboard import build_dashboard
        from tests.ui.fixture import seed_campaign_root

        assert AXE_SOURCE_PATH.is_file(), f"vendored axe missing: {AXE_SOURCE_PATH}"
        root = tmp_path / "a11y_root"
        seed_campaign_root(root)
        holder = {"ui_mode": "explorer"}

        @ui.page("/a11y_dashboard", language="en")
        def _a11y_page() -> None:
            build_dashboard(
                root,
                ui_mode=holder["ui_mode"],
                gamify=False,
                ui_actions=False,
            )

        screen.open("/a11y_dashboard", timeout=30)
        _wait_for_page_source(screen.selenium, "Computronium")
        _wait_for_page_source(screen.selenium, "Navigation")
        data = _run_axe_scan(screen.selenium)
        _assert_no_critical_or_serious(data["violations"], "explorer")

        holder["ui_mode"] = "lab"
        screen.open("/a11y_dashboard", timeout=30)
        _wait_for_page_source(screen.selenium, "Navigation")
        data = _run_axe_scan(screen.selenium)
        _assert_no_critical_or_serious(data["violations"], "lab")


class TestA11yTokens:
    """Test that design tokens meet WCAG 2.2 AA contrast requirements."""

    def test_semantic_colors_meet_aa_on_white(self) -> None:
        """Semantic colors (light mode) must meet 4.5:1 on white background."""
        from computronium.ui.a11y.tokens import meets_aa
        from computronium.ui.design_tokens import SEMANTIC

        for name, color in SEMANTIC.items():
            assert meets_aa(color, "#ffffff"), (
                f"Semantic color '{name}' ({color}) fails AA on white"
            )

    def test_semantic_colors_dark_mode_meet_aa_on_black(self) -> None:
        """Dark mode semantic colors must meet 4.5:1 on black background."""
        from computronium.ui.a11y.tokens import meets_aa

        dark_colors = {
            "success": "#4cd964",
            "warning": "#ffdf00",
            "danger": "#ff6b6b",
            "info": "#5ac8fa",
            "neutral": "#adb5bd",
        }
        for name, color in dark_colors.items():
            assert meets_aa(color, "#000000"), (
                f"Dark color '{name}' ({color}) fails AA on black"
            )

    def test_outcome_colors_meet_ui_contrast(self) -> None:
        """Outcome colors (light mode) must meet 3:1 UI contrast on white."""
        from computronium.ui.a11y.tokens import meets_ui
        from computronium.ui.design_tokens import OUTCOME_COLORS

        for name, color in OUTCOME_COLORS.items():
            assert meets_ui(color, "#ffffff"), (
                f"Outcome color '{name}' ({color}) fails UI contrast on white"
            )

    def test_focus_ring_meet_aa(self) -> None:
        """Focus ring color must meet 3:1 on both backgrounds."""
        from computronium.ui.a11y.tokens import meets_ui
        from computronium.ui.design_tokens import FOCUS_RING

        focus_color = FOCUS_RING["color"]
        assert meets_ui(focus_color, "#ffffff"), "Focus ring fails UI contrast on white"
        assert meets_ui(focus_color, "#000000"), "Focus ring fails UI contrast on black"

    def test_grayscale_contrast_ratios(self) -> None:
        """Key grayscale steps must have sufficient contrast on white."""
        from computronium.ui.a11y.tokens import meets_aa
        from computronium.ui.design_tokens import GRAYSCALE

        text_colors = ["gray900", "gray800", "gray700", "gray600", "gray500"]
        for name in text_colors:
            assert meets_aa(GRAYSCALE[name], "#ffffff"), (
                f"Gray '{name}' ({GRAYSCALE[name]}) fails AA on white"
            )

        bg_colors = ["gray100", "gray200", "gray300"]
        for name in bg_colors:
            assert meets_aa(GRAYSCALE[name], "#000000"), (
                f"Gray '{name}' ({GRAYSCALE[name]}) fails AA on black"
            )


class TestA11yKeyboardCrawl:
    """Manual keyboard crawl checklist (record results in CI)."""

    @pytest.mark.skip(reason="Manual keyboard crawl - run interactively")
    def test_keyboard_crawl_checklist(self) -> None:
        """Manual keyboard crawl - run interactively.

        Usage: pytest tests/a11y/test_ux_l5_a11y.py::TestA11yKeyboardCrawl::test_keyboard_crawl_checklist -s
        """
        import os

        url = os.environ.get("DASHBOARD_URL", "http://localhost:8088")

        print(f"\nManual keyboard crawl for: {url}")
        print(
            "Navigate using ONLY keyboard (Tab, Shift+Tab, Enter, Space, Arrows, Esc)"
        )
        print("Record results for each check below.\n")

        results = []
        for check in KEYBOARD_CHECKLIST:
            print(f"[{check['id']}] {check['description']} (WCAG: {check['wcag']})")
            passed = input("  Passed? (y/n/skip): ").strip().lower()
            if passed == "y":
                results.append((check["id"], True, ""))
            elif passed == "n":
                notes = input("  Notes: ").strip()
                results.append((check["id"], False, notes))
            else:
                results.append((check["id"], False, "Skipped"))

        passed_count = sum(1 for r in results if r[1])
        total = len(results)
        print(f"\nKeyboard crawl complete: {passed_count}/{total} passed")

        failed = [
            (cid, notes)
            for cid, passed, notes in results
            if not passed and notes != "Skipped"
        ]
        if failed:
            pytest.fail(
                "Keyboard crawl failures:\n"
                + "\n".join(f"  {cid}: {notes}" for cid, notes in failed)
            )

    def test_skip_link_exists_in_a11y_css(self) -> None:
        """Skip link CSS must be present in a11y tokens."""
        from computronium.ui.a11y.tokens import SKIP_LINK_CSS

        assert ".skip-link" in SKIP_LINK_CSS
        assert "position: absolute" in SKIP_LINK_CSS
        assert "top: -100%" in SKIP_LINK_CSS
        assert ":focus" in SKIP_LINK_CSS

    def test_sr_only_exists_in_a11y_css(self) -> None:
        """Screen reader only CSS must be present."""
        from computronium.ui.a11y.tokens import SR_ONLY_CSS

        assert ".sr-only" in SR_ONLY_CSS
        assert "position: absolute" in SR_ONLY_CSS
        assert "width: 1px" in SR_ONLY_CSS
        assert "height: 1px" in SR_ONLY_CSS

    def test_focus_visible_polyfill_exists(self) -> None:
        """Focus visible polyfill CSS must be present."""
        from computronium.ui.a11y.tokens import FOCUS_VISIBLE_CSS

        assert ":focus-visible" in FOCUS_VISIBLE_CSS
        assert "outline: none" in FOCUS_VISIBLE_CSS or "outline" in FOCUS_VISIBLE_CSS

    def test_reduced_motion_media_query_exists(self) -> None:
        """Reduced motion media query must be in design tokens."""
        from computronium.ui.design_tokens import REDUCED_MOTION_CSS

        assert "prefers-reduced-motion: reduce" in REDUCED_MOTION_CSS
        assert "animation-duration: 0.01ms" in REDUCED_MOTION_CSS
        assert "transition-duration: 0.01ms" in REDUCED_MOTION_CSS

    def test_high_contrast_media_query_exists(self) -> None:
        """High contrast media query must be in design tokens."""
        from computronium.ui.design_tokens import HIGH_CONTRAST_CSS

        assert "prefers-contrast: high" in HIGH_CONTRAST_CSS

    def test_live_region_config(self) -> None:
        """Live region config must have polite politeness and rate limiting."""
        from computronium.ui.a11y.tokens import LIVE_REGION_CONFIG

        assert LIVE_REGION_CONFIG.politeness == "polite"
        assert LIVE_REGION_CONFIG.atomic is True
        assert LIVE_REGION_CONFIG.min_interval_ms >= 500

    def test_touch_target_sizes(self) -> None:
        """Touch target constants must meet WCAG minimums."""
        from computronium.ui.a11y.tokens import (
            MIN_TOUCH_TARGET,
            RECOMMENDED_TOUCH_TARGET,
        )

        assert MIN_TOUCH_TARGET == "44px"
        assert RECOMMENDED_TOUCH_TARGET == "48px"

    def test_text_spacing_tokens(self) -> None:
        """Text spacing tokens must meet WCAG 1.4.12."""
        from computronium.ui.a11y.tokens import TEXT_SPACING

        assert TEXT_SPACING.line_height >= 1.5
        assert TEXT_SPACING.paragraph_spacing >= 2.0
        assert TEXT_SPACING.letter_spacing >= 0.12
        assert TEXT_SPACING.word_spacing >= 0.16


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
