#!/usr/bin/env python3
"""Look at one view of the stage, on the store the last run left (TODO69).

A fast loop for the views: the dashboard serves the store that is already
there, the browser opens it, a key picks a view, and the picture is taken.
No campaign, no tour — just the one picture, to see whether the view draws
what it is supposed to draw.

Usage:
    uv run python scripts/probes/todo69_stage_view.py --view layers
"""

from __future__ import annotations

import argparse
import logging
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dashboard_capture import (  # ruff: ignore[module-import-not-at-top-of-file]
    REPO_ROOT,
    launch_browser,
    open_dashboard,
    start_dashboard,
    wait_for_http,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("stage-view")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--view", default="layers")
    parser.add_argument("--key", default="")
    parser.add_argument("--port", type=int, default=8099)
    parser.add_argument("--store", type=Path, default=REPO_ROOT / "experiment.duckdb")
    parser.add_argument("--out", type=Path, default=Path(tempfile.mkdtemp()))
    args = parser.parse_args()

    _dashboard, _thread, errors = start_dashboard(args.port, args.store)
    if not wait_for_http(args.port):
        logger.error("the dashboard did not start")
        return 1

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        page = open_dashboard(browser, args.port)
        page.wait_for_timeout(6000)
        if args.key:
            page.keyboard.press(args.key)
        else:
            page.select_option("#view-picker", args.view)
        page.wait_for_timeout(4000)
        path = args.out / f"{args.view}.png"
        page.screenshot(path=str(path))
        logger.info("shot %s", path)
        browser.close()

    if errors:
        logger.error("the dashboard failed: %s", errors[0])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
