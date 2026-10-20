#!/usr/bin/env python3
"""Capture the dashboard hero screenshot (TODO68 Phase 5).

The dashboard, the campaign and the capture run in ONE process on purpose: the
campaign holds the store, and the capture wants the records the campaign has
just written. (A dashboard in another process would see them too, through the
mirror the writer publishes — but one process has no such gap to fall
through.)

Flow:
1. Start the dashboard server on a thread.
2. Start the demo campaign on the main thread (it installs signal handlers).
3. On a capture thread, wait for records to land, drive Chromium through
   Playwright, and write the 1920x1080 hero image.

Usage:
    uv run python scripts/capture_dashboard_screenshot.py
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]


def wait_for_http(port: int, timeout: float = 60.0) -> bool:
    """Wait for the dashboard HTTP server to answer."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/status", timeout=2
            ) as r:
                if r.status == 200:
                    return True
        except urllib.error.URLError, OSError:
            pass
        time.sleep(0.5)
    return False


def wait_for_records(port: int, min_records: int, timeout: float = 180.0) -> str:
    """Wait for a run to land records; return its run id.

    The dashboard is asked, not the store: DuckDB gives one writer the file,
    and a second connection to it fails while the campaign is writing.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/runs", timeout=5
            ) as response:
                payload = json.loads(response.read())
            for run in payload.get("runs", []):
                if run.get("records", 0) >= min_records:
                    logger.info("Run %s has %d records", run["run_id"], run["records"])
                    return str(run["run_id"])
        except (urllib.error.URLError, OSError, ValueError) as exc:
            logger.debug("Runs not readable yet: %s", exc)
        time.sleep(1.0)
    raise TimeoutError(f"no run reached {min_records} records in {timeout}s")


def capture(
    port: int,
    run_id: str,
    output: Path,
    min_records: int,
    timeout_ms: int,
) -> int:
    """Drive Chromium, wait for the scene to show measured cells, screenshot."""
    from playwright.sync_api import sync_playwright

    url = f"http://localhost:{port}/"
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--use-gl=angle",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--force-device-scale-factor=1",
            ],
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.on("console", lambda m: logger.debug("console %s: %s", m.type, m.text))
        page.on("pageerror", lambda e: logger.warning("pageerror: %s", e))

        page.goto(url, wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)

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
    if store_path.exists():
        store_path.unlink()
        logger.info("Removed existing store: %s", store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)

    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )
    from computronium.experiment.surface.cli import (
        RUN_PROFILES,
        execute_spec,
        spec_from_profile,
    )

    dashboard = WebDashboard(
        DashboardConfig(
            host="127.0.0.1",
            port=args.port,
            store_path=str(store_path),
        )
    )

    server_error: list[BaseException] = []

    def serve() -> None:
        import asyncio

        try:
            asyncio.run(dashboard.run())
        except BaseException as exc:  # ruff: ignore[BLE001] - reported to the main thread
            server_error.append(exc)

    server_thread = threading.Thread(target=serve, daemon=True)
    server_thread.start()

    if not wait_for_http(args.port):
        logger.error("Dashboard server did not start")
        return 1
    logger.info("Dashboard serving on port %d", args.port)

    capture_result: list[int] = []

    def run_capture() -> None:
        try:
            run_id = wait_for_records(args.port, args.min_records)
            capture_result.append(
                capture(args.port, run_id, args.output, args.min_records, args.timeout)
            )
        except Exception as exc:  # ruff: ignore[BLE001] - reported to the main thread
            logger.exception("Capture failed")
            capture_result.append(1)

    capture_thread = threading.Thread(target=run_capture, daemon=True)
    capture_thread.start()

    logger.info("Running the demo campaign in-process...")
    spec = spec_from_profile(RUN_PROFILES["demo"])
    exit_code = execute_spec(spec, store_path=str(store_path))

    capture_thread.join(timeout=180)
    if not capture_result:
        logger.error("Capture produced no image")
        return 1

    if capture_result[0] != 0:
        return 1

    if args.mirror != args.output:
        args.mirror.parent.mkdir(parents=True, exist_ok=True)
        args.mirror.write_bytes(args.output.read_bytes())
        logger.info("Mirrored to %s", args.mirror)

    print(json.dumps({"screenshot": str(args.output), "campaign_exit": exit_code}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
