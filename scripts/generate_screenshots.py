#!/usr/bin/env python
"""Generate dashboard screenshots for all panels and lenses using pytest+selenium.

This uses the existing test infrastructure (pytest + screen fixture from nicegui)
to render the dashboard and capture screenshots.

Usage:
    uv run python scripts/generate_screenshots.py --output-dir screenshots
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import pytest


def generate_screenshots(output_dir: Path) -> None:
    """Generate screenshots by running a custom pytest session."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create a temporary test file that captures screenshots
    test_code = f'''"""Auto-generated screenshot capture test."""

import time
import tempfile
from pathlib import Path
import pytest

from tests.ui.fixture import seed_campaign_root
from computronium.ui.dashboard import build_dashboard
from nicegui import ui


SCREENSHOT_DIR = Path(r"{output_dir}")
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def _wait_for_source(driver, needle: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if needle in driver.page_source:
            return
        time.sleep(0.25)
    raise AssertionError(f'Page never contained "{{needle}}" within {{timeout}}s')


def test_capture_all_panels_and_lenses(screen):
    """Capture screenshots of all 5 panels and their lenses."""
    root = Path(tempfile.mkdtemp()) / "screenshot_campaign"
    root.mkdir(parents=True)
    seed_campaign_root(root)

    holder = {{"root": root}}

    @ui.page("/dash", language="en")
    def _page():
        build_dashboard(
            holder["root"],
            ui_mode="lab",  # lab mode shows all lenses
            ui_actions=False,
        )

    screen.open("/dash", timeout=30)
    _wait_for_source(screen.selenium, "Map")
    time.sleep(2)  # let atlas render

    # Panel order: Map, Repair, Console, Composer, Record
    # Each entry: (panel_key, [(lens_key, lens_wait_text), ...])
    panels = [
        ("map", [
            ("map", "UMAP"),           # Map lens: UMAP plot
            ("tradeoffs", "Pareto"),   # Trade-offs lens: Pareto text
            ("gallery", "Gallery"),    # Gallery lens: Gallery text
        ]),
        ("repair", [
            ("defects", "Defects"),    # Defects lens: Defects table
            ("maturation", "Maturation"), # Maturation lens: Maturation tree
        ]),
        ("console", [("", "Console")]),  # No lenses
        ("composer", [("", "Composer")]),
        ("record", [
            ("history", "History"),    # History lens: History timeline
            ("ledger", "Ledger"),      # Ledger lens: Ledger tree
            ("lessons", "Lessons"),    # Lessons lens: Lessons list
        ]),
    ]

    for panel_key, lenses in panels:
        for lens_key, wait_text in lenses:
            holder["root"] = root
            if lens_key:
                screen.open(f"/dash#{{panel_key}}:{{lens_key}}", timeout=30)
            else:
                screen.open(f"/dash#{{panel_key}}", timeout=30)
            # Wait for lens-specific content to appear (proves hash restore worked)
            _wait_for_source(screen.selenium, wait_text)
            time.sleep(1)  # extra buffer for render
            png = screen.selenium.get_screenshot_as_png()
            suffix = f"_{{lens_key}}" if lens_key else ""
            (SCREENSHOT_DIR / f"{{panel_key}}{{suffix}}.png").write_bytes(png)
            print(f"  Saved {{panel_key}}{{suffix}}.png")

    print(f"All screenshots saved to {{SCREENSHOT_DIR}}")
'''

    # Write temp test file in the project's tests directory
    test_dir = Path("/home/me/computronium/tests")
    test_dir.mkdir(exist_ok=True)
    test_file_path = test_dir / "tmp_screenshots_test.py"
    test_file_path.write_text(test_code)

    try:
        # Run pytest with the screen fixture from project root
        import sys
        sys.path.insert(0, "/home/me/computronium")
        result = pytest.main([
            str(test_file_path),
            "-v",
            "-s",
            "--tb=short",
        ])
        print(f"Pytest exit code: {result}")
    finally:
        test_file_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("screenshots"))
    args = parser.parse_args()

    print(f"Generating screenshots in {args.output_dir}...")
    generate_screenshots(args.output_dir)


if __name__ == "__main__":
    main()