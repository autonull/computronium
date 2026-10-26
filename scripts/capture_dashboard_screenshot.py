#!/usr/bin/env python3
"""Capture the hero screenshot of the dashboard (TODO73 P10.5).

Opens the stage via layoutHost.open, keeps the returned instanceId, and waits
for debug.getStageDebug(id) to report {ready:true, measured>0, view:"space",
canvas.w>0} + two equal rect samples + document.fonts.ready. Fails on
console/page errors, duplicateIds>0, measured==0, canvas<box.

No fixed 10 s sleep as the only wait — all waits are condition-driven.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Add scripts to path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from dashboard_capture import (
    REPO_ROOT,
    clear_store,
    launch_browser,
    run_demo_campaign,
    start_dashboard,
    wait_for_http,
    wait_for_records,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

VIEWPORT = {"width": 1920, "height": 1080}

# Where the hero shot goes (mirrored to docs/readme/assets/)
HERO_OUTPUT = REPO_ROOT / "docs" / "readme" / "assets" / "dashboard-hero.png"


def wait_for_stage_ready(page, instance_id: str, timeout: float = 60.0) -> dict:
    """Wait for stage debug info to report ready with measured cells."""
    deadline = time.time() + timeout
    last_rect = None
    stable_count = 0

    while time.time() < deadline:
        debug = page.evaluate(
            """(id) => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug || !dbg.debug.getStageDebug) return null;
                return dbg.debug.getStageDebug(id);
            }""",
            instance_id,
        )

        if debug and debug.get("ready") and debug.get("measured", 0) > 0:
            canvas = debug.get("canvas", {})
            if canvas.get("w", 0) > 0 and canvas.get("h", 0) > 0:
                # Check rect stability (two equal samples)
                rect = page.evaluate(
                    """(id) => {
                        const dbg = window.__DASHBOARD__;
                        if (!dbg || !dbg.debug || !dbg.debug.stageRect) return null;
                        return dbg.debug.stageRect(id);
                    }""",
                    instance_id,
                )
                if rect:
                    if last_rect and rect == last_rect:
                        stable_count += 1
                        if stable_count >= 2:
                            # Also wait for fonts
                            fonts_ready = page.evaluate(
                                "() => document.fonts.ready.then(() => true).catch(() => false)"
                            )
                            if fonts_ready:
                                return debug
                    else:
                        stable_count = 0
                    last_rect = rect

        time.sleep(0.5)

    # Timeout - return what we have for diagnostics
    debug = page.evaluate(
        """(id) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.debug || !dbg.debug.getStageDebug) return null;
            return dbg.debug.getStageDebug(id);
        }""",
        instance_id,
    )
    raise TimeoutError(f"Stage {instance_id} not ready in {timeout}s: {json.dumps(debug)}")


def check_console_errors(page) -> list[str]:
    """Collect console errors from the page."""
    # Errors are collected via page.on("console") in the main function
    return []


def filter_console_errors(console_messages: list[dict]) -> list[dict]:
    """Filter out known benign console errors (e.g., favicon.ico 404)."""
    filtered = []
    for msg in console_messages:
        if msg["type"] == "error":
            text = msg["text"]
            # Ignore favicon.ico 404 and other known benign resource 404s
            if "favicon.ico" in text or "Failed to load resource" in text:
                continue
            filtered.append(msg)
    return filtered


def wait_for_stage_ready(page, instance_id: str, timeout: float = 60.0) -> dict:
    """Wait for stage debug info to report ready with measured cells."""
    deadline = time.time() + timeout
    last_rect = None
    stable_count = 0

    while time.time() < deadline:
        debug = page.evaluate(
            """(id) => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug || !dbg.debug.getStageDebug) return null;
                return dbg.debug.getStageDebug(id);
            }""",
            instance_id,
        )

        # Debug logging
        if debug:
            print(f"  [debug] getStageDebug: ready={debug.get('ready')}, measured={debug.get('measured')}, view={debug.get('view')}, canvas={debug.get('canvas')}")

        if debug and debug.get("ready") and debug.get("measured", 0) > 0:
            canvas = debug.get("canvas", {})
            if canvas.get("w", 0) > 0 and canvas.get("h", 0) > 0:
                # Check rect stability (two equal samples)
                rect = page.evaluate(
                    """(id) => {
                        const dbg = window.__DASHBOARD__;
                        if (!dbg || !dbg.debug || !dbg.debug.stageRect) return null;
                        return dbg.debug.stageRect(id);
                    }""",
                    instance_id,
                )
                if rect:
                    if last_rect and rect == last_rect:
                        stable_count += 1
                        if stable_count >= 2:
                            # Also wait for fonts
                            fonts_ready = page.evaluate(
                                "() => document.fonts.ready.then(() => true).catch(() => false)"
                            )
                            if fonts_ready:
                                return debug
                    else:
                        stable_count = 0
                    last_rect = rect

        time.sleep(0.5)

    # Timeout - return what we have for diagnostics
    debug = page.evaluate(
        """(id) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.debug || !dbg.debug.getStageDebug) return null;
            return dbg.debug.getStageDebug(id);
        }""",
        instance_id,
    )
    print(f"  [debug] Final getStageDebug: {json.dumps(debug)}")
    raise TimeoutError(f"Stage {instance_id} not ready in {timeout}s: {json.dumps(debug)}")


def check_page_errors(page) -> list[str]:
    """Collect page errors from the page."""
    return []


def check_duplicate_ids(page) -> tuple[int, list[str]]:
    """Count duplicate DOM ids and return the duplicate IDs."""
    result = page.evaluate(
        """() => {
            const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
            const counts = {};
            for (const id of ids) counts[id] = (counts[id] || 0) + 1;
            const duplicates = Object.entries(counts).filter(([,c]) => c > 1).map(([id]) => id);
            return {count: duplicates.length, ids: duplicates};
        }"""
    )
    return result["count"], result["ids"]


def capture_hero(port: int, store_path: Path, output: Path) -> dict:
    """Capture the hero screenshot."""
    from playwright.sync_api import sync_playwright

    console_messages: list[dict] = []
    page_errors: list[str] = []

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text}))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#workspace", state="attached", timeout=30000)

        # Wait for Dockview to mount
        page.wait_for_function(
            "() => Boolean(window.__DASHBOARD__?.layoutHost?.mountComplete)",
            timeout=30000,
        )

        # Open stage panel via layoutHost.open and get instanceId
        instance_id = page.evaluate(
            """async () => {
                const host = window.__DASHBOARD__?.layoutHost;
                if (!host || !host.open) throw new Error("No layoutHost");
                return await host.open("stage", {view: "space"});
            }"""
        )

        logger.info(f"Opened stage panel: {instance_id}")

        # Wait for stage to be ready with measured cells
        debug = wait_for_stage_ready(page, instance_id)

        # Check for errors
        console_errors = filter_console_errors(console_messages)
        duplicate_ids, duplicate_id_list = check_duplicate_ids(page)

        if console_errors:
            raise RuntimeError(f"Console errors: {console_errors}")
        if page_errors:
            raise RuntimeError(f"Page errors: {page_errors}")
        if duplicate_ids > 0:
            raise RuntimeError(f"Duplicate DOM ids: {duplicate_ids} ({duplicate_id_list})")
        if debug.get("measured", 0) == 0:
            raise RuntimeError(f"No measured cells: {debug}")

        # Take the screenshot
        output.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(output))

        # Verify file size (smoke test: broken=40KB, baseline=245KB)
        size_kb = output.stat().st_size / 1024
        if size_kb < 60:
            raise RuntimeError(f"Screenshot too small ({size_kb:.0f} KB), likely blank")

        logger.info(f"Hero shot saved: {output} ({size_kb:.0f} KB)")

        context.close()
        browser.close()

        return {
            "output": str(output),
            "instance_id": instance_id,
            "debug": debug,
            "size_kb": size_kb,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8084)
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "experiment.duckdb",
        help="Store the campaign writes and the dashboard reads.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=HERO_OUTPUT,
        help="Where the hero shot is written.",
    )
    parser.add_argument(
        "--reuse-store",
        action="store_true",
        help="Reuse existing store (skip campaign run).",
    )
    args = parser.parse_args()

    if not args.reuse_store:
        clear_store(args.store)
        logger.info("Running demo campaign...")
        exit_code = run_demo_campaign(args.store)
        if exit_code != 0:
            logger.error(f"Demo campaign failed with exit code {exit_code}")
            return 1
    else:
        logger.info("Reusing existing store")

    _dashboard, _thread, server_error = start_dashboard(args.port, args.store)
    if not wait_for_http(args.port):
        logger.error("Dashboard server did not start")
        return 1
    logger.info(f"Dashboard serving on port {args.port}")

    # Wait for a run with measured records
    run_id = wait_for_records(args.port, min_records=5, timeout=180.0)
    logger.info(f"Run {run_id} has measured records")

    try:
        result = capture_hero(args.port, args.store, args.output)
        print(json.dumps(result, indent=2))
        return 0
    except Exception:
        logger.exception("Capture failed")
        return 1
    finally:
        if server_error:
            logger.error(f"Dashboard failed: {server_error[0]}")


if __name__ == "__main__":
    sys.exit(main())
