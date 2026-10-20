#!/usr/bin/env python3
"""Capture the dashboard hero screenshot (TODO68 Phase 5).

The dashboard, the campaign and the capture run in ONE process on purpose: the
campaign holds the store, and the capture wants the records the campaign has
just written. (A dashboard in another process would see them too, through the
mirror the writer publishes — but one process has no such gap to fall
through.)

The machinery — the server on a thread, the campaign, the Chromium that
renders without a GPU — lives in ``scripts/dashboard_capture.py``, which the
tour and the recording share.

Usage:
    uv run python scripts/capture_dashboard_screenshot.py
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
from pathlib import Path

from dashboard_capture import (
    REPO_ROOT,
    clear_store,
    launch_browser,
    mirror_shot,
    open_dashboard,
    run_demo_campaign,
    start_dashboard,
    wait_for_http,
    wait_for_records,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def capture(port: int, run_id: str, output: Path, timeout_ms: int) -> int:
    """Drive Chromium, wait for the scene to show measured cells, screenshot."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = launch_browser(p)
        page = open_dashboard(browser, port)

        # The discovery map lights a cell when a record for it arrives.
        page.wait_for_function(
            """(runId) => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.discoveryMap) return false;
                const cells = dbg.discoveryMap.cellDataMap;
                let measured = 0;
                for (const cell of cells.values()) {
                    if (cell.status === 'measured' && cell.metrics?.n_seeds) measured++;
                }
                return measured > 0;
            }""",
            arg=run_id,
            timeout=timeout_ms,
        )
        logger.info("Discovery map shows measured cells")

        # Let the plotter and the live rail fill in.
        page.wait_for_timeout(4000)

        output.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(output))
        browser.close()

    logger.info("Screenshot written to %s", output)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "experiment.duckdb",
        help="Store the campaign writes and the dashboard reads.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "readme" / "assets" / "dashboard-hero.png",
    )
    parser.add_argument(
        "--mirror",
        type=Path,
        default=REPO_ROOT / "docs" / "screenshots" / "dashboard-hero.png",
    )
    parser.add_argument(
        "--min-records",
        type=int,
        default=20,
        help="Records to wait for before the shot: the demo campaign's full set.",
    )
    parser.add_argument("--timeout", type=int, default=90000)
    args = parser.parse_args()

    store_path = args.store
    clear_store(store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)

    _dashboard, _thread, server_error = start_dashboard(args.port, store_path)
    if not wait_for_http(args.port):
        logger.error("Dashboard server did not start")
        return 1
    logger.info("Dashboard serving on port %d", args.port)

    capture_result: list[int] = []
    capture_error: list[BaseException] = []

    def run_capture() -> None:
        try:
            run_id = wait_for_records(args.port, args.min_records)
            capture_result.append(capture(args.port, run_id, args.output, args.timeout))
        except BaseException as exc:  # ruff: ignore[blind-except] - reported to the main thread
            logger.exception("Capture failed")
            capture_error.append(exc)

    capture_thread = threading.Thread(target=run_capture, daemon=True)
    capture_thread.start()

    logger.info("Running the demo campaign in-process...")
    exit_code = run_demo_campaign(store_path)

    capture_thread.join(timeout=180)
    if capture_error:
        return 1
    if server_error:
        logger.error("The dashboard failed: %s", server_error[0])
        return 1
    if not capture_result:
        logger.error("Capture produced no image")
        return 1

    if capture_result[0] != 0:
        return 1

    mirror_shot(args.output, args.mirror)

    print(json.dumps({"screenshot": str(args.output), "campaign_exit": exit_code}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
