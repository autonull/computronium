#!/usr/bin/env python3
"""Look at the dashboard without re-running the campaign.

The capture script (scripts/capture_dashboard_screenshot.py) runs the demo
campaign and the dashboard in one process, because DuckDB gives one writer the
file. That costs the campaign's 34 seconds on every look at the picture, so
this probe reads a store that already holds a finished demo run and photographs
the dashboard reading it.

Usage:
    uv run python scripts/probes/probe_dashboard_look.py --output /tmp/look.png
"""

from __future__ import annotations

import argparse
import logging
import tempfile
import threading
from pathlib import Path

from dashboard_probe import (
    CHROMIUM_ARGS,
    wait_for_http,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]


def capture(port: int, output: Path, settle_ms: int) -> int:
    """Photograph the dashboard as it reads a finished run."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=CHROMIUM_ARGS,
        )
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
        page.wait_for_timeout(settle_ms)
        output.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(output))
        browser.close()
    logger.info("Wrote %s", output)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8137)
    parser.add_argument("--store", type=Path, default=REPO_ROOT / "experiment.duckdb")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(tempfile.gettempdir()) / "computronium" / "dashboard-look.png",
    )
    parser.add_argument("--settle", type=int, default=4000)
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
    return capture(args.port, args.output, args.settle)


if __name__ == "__main__":
    raise SystemExit(main())
