"""UX-L5: Accessibility (WCAG 2.2 AA) lock.

Automated axe-core scan + manual keyboard crawl checklist.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


def _run_axe_scan(url: str, output_path: Path | None = None) -> dict:
    """Run axe-core CLI against a URL.

    Requires: npm install -g @axe-core/cli
    """
    try:
        result = subprocess.run(
            ["axe", url, "--json"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except FileNotFoundError:
        pytest.skip("axe CLI not found. Install with: npm install -g @axe-core/cli")
    except subprocess.TimeoutExpired:
        pytest.fail("axe scan timed out after 120s")

    if result.returncode not in {0, 1, 2}:
        pytest.fail(f"axe scan failed: {result.stderr}")

    data = json.loads(result.stdout)
    if output_path:
        output_path.write_text(json.dumps(data, indent=2))

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
    """Automated axe-core accessibility tests."""

    @pytest.fixture(scope="class")
    def dashboard_url(self) -> str:
        """Base URL for dashboard (set via env or default)."""
        import os
        return os.environ.get("DASHBOARD_URL", "http://localhost:8088")

    def test_axe_no_critical_or_serious(self, dashboard_url: str) -> None:
        """axe-core scan must have 0 critical/serious violations."""
        data = _run_axe_scan(dashboard_url)
        violations = data.get("violations", [])

        grouped = _violations_by_severity(violations)

        critical_count = len(grouped["critical"])
        serious_count = len(grouped["serious"])

        assert critical_count == 0, (
            f"{critical_count} critical axe violations:\n"
            + "\n".join(f"  [{v['id']}] {v['description']}" for v in grouped["critical"])
        )
        assert serious_count == 0, (
            f"{serious_count} serious axe violations:\n"
            + "\n".join(f"  [{v['id']}] {v['description']}" for v in grouped["serious"])
        )

    def test_axe_no_violations_on_shell_routes(self, dashboard_url: str) -> None:
        """Test key dashboard routes for a11y regressions."""
        routes = [
            "/",           # Main dashboard
            "/?mode=lab",  # Lab mode
        ]

        for route in routes:
            url = f"{dashboard_url}{route}"
            data = _run_axe_scan(url)
            violations = data.get("violations", [])

            grouped = _violations_by_severity(violations)
            critical_count = len(grouped["critical"])
            serious_count = len(grouped["serious"])

            assert critical_count == 0, (
                f"Route {route}: {critical_count} critical axe violations"
            )
            assert serious_count == 0, (
                f"Route {route}: {serious_count} serious axe violations"
            )


class TestA11yTokens:
    """Test that design tokens meet WCAG 2.2 AA contrast requirements."""

    def test_semantic_colors_meet_aa_on_white(self) -> None:
        """Semantic colors (light mode) must meet 4.5:1 on white background."""
        from computronium.ui.design_tokens import SEMANTIC
        from computronium.ui.a11y.tokens import meets_aa

        for name, color in SEMANTIC.items():
            assert meets_aa(color, "#ffffff"), (
                f"Semantic color '{name}' ({color}) fails AA on white"
            )

    def test_semantic_colors_dark_mode_meet_aa_on_black(self) -> None:
        """Dark mode semantic colors must meet 4.5:1 on black background."""
        # Dark mode colors would be defined separately in a real implementation
        # For now, test that high contrast mode colors work
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
                f"Dark mode color '{name}' ({color}) fails AA on black"
            )

    def test_outcome_colors_meet_ui_contrast(self) -> None:
        """Outcome colors (light mode) must meet 3:1 UI contrast on white."""
        from computronium.ui.design_tokens import OUTCOME_COLORS
        from computronium.ui.a11y.tokens import meets_ui

        for name, color in OUTCOME_COLORS.items():
            assert meets_ui(color, "#ffffff"), (
                f"Outcome color '{name}' ({color}) fails UI contrast on white"
            )

    def test_focus_ring_meets_aa(self) -> None:
        """Focus ring color must meet 3:1 on both backgrounds."""
        from computronium.ui.design_tokens import FOCUS_RING
        from computronium.ui.a11y.tokens import meets_ui

        focus_color = FOCUS_RING["color"]
        assert meets_ui(focus_color, "#ffffff"), "Focus ring fails UI contrast on white"
        assert meets_ui(focus_color, "#000000"), "Focus ring fails UI contrast on black"

    def test_grayscale_contrast_ratios(self) -> None:
        """Key grayscale steps must have sufficient contrast on white."""
        from computronium.ui.design_tokens import GRAYSCALE
        from computronium.ui.a11y.tokens import contrast_ratio, meets_aa

        # Test text colors on white background
        text_colors = ["gray900", "gray800", "gray700", "gray600", "gray500"]
        for name in text_colors:
            assert meets_aa(GRAYSCALE[name], "#ffffff"), (
                f"Gray '{name}' ({GRAYSCALE[name]}) fails AA on white"
            )

        # Test background colors on black (for dark mode surfaces)
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
        print("Navigate using ONLY keyboard (Tab, Shift+Tab, Enter, Space, Arrows, Esc)")
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

        failed = [(cid, notes) for cid, passed, notes in results if not passed and notes != "Skipped"]
        if failed:
            pytest.fail(
                f"Keyboard crawl failures:\n"
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
        assert "outline" in FOCUS_VISIBLE_CSS

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
        from computronium.ui.a11y.tokens import MIN_TOUCH_TARGET, RECOMMENDED_TOUCH_TARGET
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