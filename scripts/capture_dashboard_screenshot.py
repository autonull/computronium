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
    uv run python scripts/capture_dashboard_screenshot.py --reuse-store --port 8084
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
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

        # Open a stage panel if not already open
        page.evaluate(
            """(runId) => {
                const dbg = window.__DASHBOARD__;
                if (dbg && dbg.layoutHost && typeof dbg.layoutHost.open === 'function') {
                    // Check if any stage panel is already open
                    const instances = dbg.layoutHost.list?.() || [];
                    const hasStage = instances.some(i => i.type === 'stage');
                    if (!hasStage) {
                        dbg.layoutHost.open('stage', { runId });
                    }
                }
            }""",
            arg=run_id,
        )

        # Give the stage panel time to load and fetch space data
        page.wait_for_timeout(10000)

        # Wait for the stage to show measured cells using the new debug API
        # Poll with logging to see what's happening
        deadline = time.time() + timeout_ms / 1000
        while time.time() < deadline:
            try:
                cells = page.evaluate("""() => window.__DASHBOARD__?.debug?.measuredCells?.() ?? 0""")
                logger.info("Measured cells: %d", cells)
                if cells > 0:
                    break
            except Exception as exc:
                logger.debug("measuredCells check failed: %s", exc)
            time.sleep(2)
        else:
            logger.error("Timeout waiting for measured cells")
            # Debug: check what stage instances exist
            try:
                instances = page.evaluate("""() => window.__DASHBOARD__?.debug?.instances?.() ?? []""")
                logger.info("Stage instances: %s", json.dumps(instances))
            except Exception as exc:
                logger.debug("instances check failed: %s", exc)
            # Debug: check space store
            try:
                spaceDebug = page.evaluate("""() => {
                    const store = window.__DASHBOARD__?.spaceStore;
                    if (!store) return 'no spaceStore';
                    return { cacheSize: store.cache?.size ?? 0 };
                }""")
                logger.info("Space store debug: %s", spaceDebug)
            except Exception as exc:
                logger.debug("space store check failed: %s", exc)
            # Debug: check space view state
            try:
                viewDebug = page.evaluate("""() => {
                    const dbg = window.__DASHBOARD__;
                    if (!dbg || !dbg.layoutHost) return 'no layoutHost';
                    const api = dbg.layoutHost.getApi?.();
                    if (!api) return 'no api';
                    const panels = api.panels;
                    const stagePanels = panels.filter(p => p.component === 'stage');
                    return stagePanels.map(p => {
                        const params = p.api.getParameters?.();
                        return { id: p.id, component: p.component, params };
                    });
                }""")
                logger.info("Stage panels debug: %s", viewDebug)
            except Exception as exc:
                logger.debug("stage panels debug failed: %s", exc)
            return 1

        logger.info("Stage shows measured cells")

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
    parser.add_argument(
        "--reuse-store",
        action="store_true",
        help="Reuse existing store; do not clear or run a campaign.",
    )
    args = parser.parse_args()

    store_path = args.store
    if not args.reuse_store:
        clear_store(store_path)
        store_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        logger.info("Reusing existing store at %s", store_path)

    _dashboard, _thread, server_error = start_dashboard(args.port, store_path)
    if not wait_for_http(args.port):
        logger.error("Dashboard server did not start")
        return 1
    logger.info("Dashboard serving on port %d", args.port)

    capture_result: list[int] = []
    capture_error: list[BaseException] = []

    def run_capture() -> None:
        try:
            if args.reuse_store:
                # Find the newest run with records
                run_id = wait_for_records(args.port, 1)
            else:
                run_id = wait_for_records(args.port, args.min_records)
            capture_result.append(capture(args.port, run_id, args.output, args.timeout))
        except BaseException as exc:  # ruff: ignore[blind-except] - reported to the main thread
            logger.exception("Capture failed")
            capture_error.append(exc)

    capture_thread = threading.Thread(target=run_capture, daemon=True)
    capture_thread.start()

    if not args.reuse_store:
        logger.info("Running the demo campaign in-process...")
        exit_code = run_demo_campaign(store_path)
    else:
        logger.info("Skipping campaign (--reuse-store)")
        exit_code = 0

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
