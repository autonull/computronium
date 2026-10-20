#!/usr/bin/env python3
"""Look at the stage's views without re-running the campaign (TODO69 Phase 5).

The tour (scripts/capture_dashboard_tour.py) runs the demo campaign and the
dashboard in one process, which costs the campaign's minute on every look at
the picture. This probe reads a store that already holds a finished demo run,
switches the stage through its views, and photographs each one.

Usage:
    uv run python scripts/probes/probe_dashboard_views.py --output /tmp/views
"""

from __future__ import annotations

import argparse
import logging
import tempfile
import threading
from pathlib import Path

from dashboard_probe import CHROMIUM_ARGS, wait_for_http

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]

# The views, in the order the number keys pick them.
VIEWS = ("space", "terrain", "frontier", "matrix", "convergence")


def capture(port: int, output: Path) -> int:
    """Photograph every view of the stage."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=list(CHROMIUM_ARGS))
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.on("pageerror", lambda e: logger.warning("pageerror: %s", e))
        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
        page.wait_for_function(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.discoveryMap) return false;
                for (const cell of dbg.discoveryMap.cellDataMap.values()) {
                    if (cell.status === 'measured' && cell.metrics?.n_seeds) return true;
                }
                return false;
            }""",
            timeout=60000,
        )
        output.mkdir(parents=True, exist_ok=True)
        for index, view in enumerate(VIEWS, start=1):
            page.keyboard.press(str(index))
            page.wait_for_function(
                """(viewId) => {
                    const dbg = window.__DASHBOARD__;
                    if (!dbg || !dbg.viewSwitcher) return false;
                    if (dbg.viewSwitcher.activeId !== viewId) return false;
                    return dbg.viewSwitcher.isReady(viewId);
                }""",
                arg=view,
                timeout=30000,
            )
            page.wait_for_timeout(1500)
            path = output / f"view-{view}.png"
            page.screenshot(path=str(path))
            logger.info("Wrote %s", path)
        browser.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8141)
    parser.add_argument("--store", type=Path, default=REPO_ROOT / "experiment.duckdb")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(tempfile.gettempdir()) / "computronium" / "views",
        help="Where the pictures are written.",
    )
    args = parser.parse_args()

    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )

    dashboard = WebDashboard(
        DashboardConfig(
            host="127.0.0.1",
            port=args.port,
            store_path=str(args.store),
        )
    )

    def serve() -> None:
        import asyncio

        asyncio.run(dashboard.run())

    threading.Thread(target=serve, daemon=True).start()
    if not wait_for_http(args.port):
        logger.error("Dashboard did not start")
        return 1
    return capture(args.port, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
