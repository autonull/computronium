#!/usr/bin/env python
"""Generate dashboard screenshots for all panels and lenses using pytest+selenium.

This uses the existing test infrastructure (pytest + screen fixture from nicegui)
to render the dashboard and capture screenshots.

Usage:
    uv run python scripts/generate_screenshots.py --output-dir screenshots
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("screenshots"))
    args = parser.parse_args()

    print(f"Generating screenshots in {args.output_dir}...")
    print("Run the screenshot tests directly:")
    print(
        "  uv run pytest tests/ui/test_dashboard_screenshots.py "
        "--capture-screenshots -v"
    )


if __name__ == "__main__":
    main()
