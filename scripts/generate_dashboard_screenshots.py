#!/usr/bin/env python
"""Generate dashboard screenshots for all panels and lenses.

Usage:
    uv run python scripts/generate_dashboard_screenshots.py --output-dir screenshots
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("screenshots"))
    args = parser.parse_args()

    # The proper way is to use pytest with the screen fixture
    # This script documents the approach; actual generation happens via pytest
    print("Screenshot generation uses pytest + selenium (see tests/ui/)")
    print(
        f"Run: uv run pytest tests/ui/test_dashboard_screenshots.py "
        f"--capture-screenshots --screenshots-dir={args.output_dir}"
    )


if __name__ == "__main__":
    main()
