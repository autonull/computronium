#!/usr/bin/env python3
"""Capture dashboard hero screenshot using Playwright with WebGL support.

This script:
1. Starts a demo campaign (background)
2. Starts the dashboard server (background)
3. Waits for WebSocket connection and first records
4. Uses Playwright to navigate and capture 1920x1080 screenshot
5. Saves to docs/readme/assets/dashboard-hero.png
6. Cleans up subprocesses
"""

from __future__ import annotations

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def wait_for_dashboard(port: int, timeout: float = 60.0) -> bool:
    """Wait for dashboard HTTP server to be ready."""
    import aiohttp

    start = time.time()
    while time.time() - start < timeout:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/api/status") as resp:
                    if resp.status == 200:
                        logger.info("Dashboard HTTP server is ready")
                        return True
        except Exception:
            pass
        await asyncio.sleep(0.5)
    return False


async def wait_for_ws_and_records(
    port: int, run_id: str, timeout: float = 120.0
) -> bool:
    """Wait for WebSocket connection and first campaign_metrics broadcast."""
    import json

    import websockets

    start = time.time()
    while time.time() - start < timeout:
        try:
            async with websockets.connect(f"ws://localhost:{port}/ws") as ws:
                # Wait for campaign_metrics message
                async for msg in ws:
                    data = json.loads(msg)
                    if (
                        data.get("type") == "campaign_metrics"
                        and data.get("campaign_id") == run_id
                    ):
                        records = data.get("data", {}).get("records", [])
                        if records:
                            logger.info(
                                f"Received campaign_metrics with {len(records)} records"
                            )
                            return True
        except Exception as e:
            logger.debug(f"WebSocket not ready: {e}")
        await asyncio.sleep(1.0)
    return False


async def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    store_path = repo_root / "experiment.duckdb"
    dashboard_port = 8080
    output_path = repo_root / "docs" / "readme" / "assets" / "dashboard-hero.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Clean up any existing store
    if store_path.exists():
        store_path.unlink()
        logger.info(f"Removed existing store: {store_path}")

    processes: list[subprocess.Popen] = []

    def cleanup() -> None:
        logger.info("Cleaning up subprocesses...")
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        for proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    # Register cleanup on exit
    import atexit

    atexit.register(cleanup)

    try:
        # 1. Start campaign queue
        logger.info("Starting campaign queue...")
        queue_proc = subprocess.Popen(
            [sys.executable, "-m", "computronium.experiment.execution.campaign_queue"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        processes.append(queue_proc)
        await asyncio.sleep(2.0)

        # 2. Submit demo campaign
        logger.info("Submitting demo campaign...")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "computronium.cli.__main__",
                "run",
                "demo",
                "--store",
                str(store_path),
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=180,
        )

        if result.returncode != 0:
            logger.error(f"Campaign submission failed: {result.stderr}")
            return 1

        # Extract run_id
        run_id = None
        import re

        for line in result.stdout.splitlines():
            match = re.search(
                r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", line
            )
            if match:
                run_id = match.group(1)
                break

        if not run_id:
            from computronium.experiment.evidence.store import RecordStore, StoreConfig

            store = RecordStore(StoreConfig(path=store_path, read_only=True))
            with store:
                runs = list(store.query_runs())
                if runs:
                    run_id = runs[-1].run_id

        if not run_id:
            logger.error("Could not determine run_id")
            return 1

        logger.info(f"Campaign submitted: {run_id}")

        # 3. Start dashboard
        logger.info("Starting dashboard server...")
        dash_proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "computronium.cli.__main__",
                "dashboard",
                "--store",
                str(store_path),
                "--host",
                "0.0.0.0",
                "--port",
                str(dashboard_port),
            ],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        processes.append(dash_proc)

        # Wait for dashboard HTTP
        if not await wait_for_dashboard(dashboard_port):
            logger.error("Dashboard HTTP server did not start in time")
            return 1

        # Wait for WebSocket + records
        logger.info("Waiting for WebSocket and campaign metrics...")
        if not await wait_for_ws_and_records(dashboard_port, run_id):
            logger.error("WebSocket or campaign metrics not received in time")
            return 1

        # Give three.js time to render
        logger.info("Dashboard ready, waiting for three.js render...")
        await asyncio.sleep(3.0)

        # 4. Capture screenshot with Playwright
        logger.info("Capturing screenshot with Playwright...")
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            # Use chromium with WebGL support via angle
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--use-gl=angle",
                    "--enable-webgl",
                    "--enable-accelerated-2d-canvas",
                    "--disable-gpu-sandbox",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            page = await browser.new_page(viewport={"width": 1920, "height": 1080})

            # Navigate to dashboard
            await page.goto(
                f"http://localhost:{dashboard_port}", wait_until="networkidle"
            )

            # Wait for three.js canvas to be rendered
            await page.wait_for_selector(
                "#dashboard-canvas", state="visible", timeout=30000
            )

            # Additional wait for three.js first frame
            await page.wait_for_function(
                """() => {
                    const canvas = document.getElementById('dashboard-canvas');
                    const ctx = canvas.getContext('webgl2') || canvas.getContext('webgl');
                    return ctx && canvas.width > 0 && canvas.height > 0;
                }""",
                timeout=30000,
            )

            # Extra render frames
            await page.wait_for_timeout(1000)

            # Capture screenshot
            await page.screenshot(path=str(output_path), full_page=False)
            await browser.close()

        logger.info(f"✓ Screenshot saved to {output_path}")
        print(f"SCREENSHOT={output_path}")

        return 0

    except Exception as e:
        logger.exception(f"Screenshot capture failed: {e}")
        return 1
    finally:
        cleanup()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Interrupted")
        sys.exit(130)
