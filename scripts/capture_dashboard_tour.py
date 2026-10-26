#!/usr/bin/env python3
"""Capture a comprehensive tour of the dashboard (TODO73 P10.5).

Captures:
- 4 presets (full dashboard shots)
- 27 stage views (crops)
- 10 panel types (full panel shots)

Each capture waits for readiness, crops appropriately, and diffs vs prior.
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

# Output directory for tour shots
TOUR_OUTPUT = REPO_ROOT / "docs" / "screenshots" / "tour"

# Presets to tour
PRESETS = ["watch", "audit", "drive", "free"]

# All 27 registered stage views
STAGE_VIEWS = [
    "space", "ledger", "timeline", "landscape", "basin", "spectrum",
    "trajectory", "flow", "frontier", "contrast", "convergence",
    "uncertainty", "effect", "spread", "matrix", "layers", "slices",
    "small-multiples", "terrain", "claim-cost", "multirun",
    "trained-trajectory", "trained-basin", "trained-landscape",
    "trained-spectrum", "plot2d", "ramp",
]

# Panel types (from layout/definitions.ts imports in main.ts)
PANEL_TYPES = [
    "discovery-legend",
    "control-panel",
    "hud",
    "pareto-chart",
    "ablation-chart",
    "variability-chart",
    "control-bar",
    "caption",
    "live-rail",
    "cell-drawer",
]

# Panel display names for filenames
PANEL_NAMES = {
    "discovery-legend": "panel-legend",
    "control-panel": "panel-control-panel",
    "hud": "panel-hud",
    "pareto-chart": "panel-pareto",
    "ablation-chart": "panel-ablation",
    "variability-chart": "panel-variability",
    "control-bar": "panel-control-bar",
    "caption": "panel-caption",
    "live-rail": "panel-live-rail",
    "cell-drawer": "panel-cell-drawer",
}


def wait_for_stage_view(page, instance_id: str, expected_view: str, timeout: float = 30.0) -> dict:
    """Wait for stage debug info to report the expected view with rendered canvas."""
    deadline = time.time() + timeout
    last_rect = None
    stable_count = 0

    data_views = {"space"}

    while time.time() < deadline:
        debug = page.evaluate(
            """(id) => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug || !dbg.debug.getStageDebug) return null;
                return dbg.debug.getStageDebug(id);
            }""",
            instance_id,
        )

        if debug and debug.get("view") == expected_view:
            canvas = debug.get("canvas", {})
            if canvas.get("w", 0) > 0 and canvas.get("h", 0) > 0:
                if expected_view in data_views and not debug.get("ready"):
                    pass
                else:
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
                                return debug
                        else:
                            stable_count = 0
                        last_rect = rect

        time.sleep(0.3)

    debug = page.evaluate(
        """(id) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.debug || !dbg.debug.getStageDebug) return null;
            return dbg.debug.getStageDebug(id);
        }""",
        instance_id,
    )
    raise TimeoutError(f"Stage {instance_id} view {expected_view} not ready in {timeout}s: {json.dumps(debug)}")


def wait_for_panel_ready(page, instance_id: str, timeout: float = 15.0) -> dict:
    """Wait for a panel to be ready (has content rendered)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        debug = page.evaluate(
            """(id) => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug) return null;
                const instances = dbg.debug.instances ? dbg.debug.instances() : [];
                const panel = instances.find(i => i.id === id);
                return panel ? {type: panel.type, title: panel.title} : null;
            }""",
            instance_id,
        )
        if debug:
            # Give it a moment to render content
            page.wait_for_timeout(500)
            return debug
        time.sleep(0.2)
    raise TimeoutError(f"Panel {instance_id} not ready in {timeout}s")


def filter_console_errors(console_messages: list[dict]) -> list[dict]:
    """Filter out known benign console errors."""
    filtered = []
    for msg in console_messages:
        if msg["type"] == "error":
            text = msg["text"]
            if "favicon.ico" in text or "Failed to load resource" in text:
                continue
            if "Failed to fetch dynamically imported module" in text and "layout.js" in text:
                continue
            filtered.append(msg)
    return filtered


def check_duplicate_ids(page) -> tuple[int, list[str]]:
    """Count duplicate DOM ids."""
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


def apply_preset(page, preset: str) -> bool:
    """Apply a layout preset."""
    result = page.evaluate(
        """(preset) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.layout || !dbg.layout.applyPreset) return false;
            dbg.layout.applyPreset(preset);
            return true;
        }""",
        preset,
    )
    return result


def open_panel(page, panel_type: str) -> str | None:
    """Open a panel via layoutHost.open."""
    instance_id = page.evaluate(
        """async (type) => {
            const host = window.__DASHBOARD__?.layoutHost;
            if (!host || !host.open) throw new Error("No layoutHost");
            return await host.open(type);
        }""",
        panel_type,
    )
    return instance_id


def close_panel(page, instance_id: str) -> bool:
    """Close a panel via layoutHost.close."""
    result = page.evaluate(
        """(id) => {
            const host = window.__DASHBOARD__?.layoutHost;
            if (!host || !host.close) return false;
            host.close(id);
            return true;
        }""",
        instance_id,
    )
    return result


def crop_panel_screenshot(page, instance_id: str, output: Path) -> dict:
    """Crop a panel's rectangle from a full-page screenshot."""
    rect = page.evaluate(
        """(id) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.debug || !dbg.debug.stageRect) return null;
            return dbg.debug.stageRect(id);
        }""",
        instance_id,
    )
    if not rect:
        raise RuntimeError(f"Could not get rect for {instance_id}")

    full_path = output.with_suffix(".full.png")
    page.screenshot(path=str(full_path))

    from PIL import Image
    img = Image.open(full_path)
    cropped = img.crop((rect["x"], rect["y"], rect["x"] + rect["width"], rect["y"] + rect["height"]))
    cropped.save(output)
    full_path.unlink()

    return rect


def full_dashboard_screenshot(page, output: Path) -> dict:
    """Capture full dashboard screenshot."""
    page.wait_for_timeout(500)
    page.screenshot(path=str(output))
    return {"width": VIEWPORT["width"], "height": VIEWPORT["height"]}


def image_diff_pct(img1: Path, img2: Path) -> float:
    """Calculate percentage difference between two images."""
    from PIL import Image
    import numpy as np

    a = np.array(Image.open(img1).convert("RGB"))
    b = np.array(Image.open(img2).convert("RGB"))

    if a.shape != b.shape:
        return 100.0

    diff = np.abs(a.astype(float) - b.astype(float))
    return float(np.mean(diff) / 255.0 * 100)


def capture_tour(port: int, store_path: Path, output_dir: Path, skip_campaigns: bool = False) -> list[dict]:
    """Capture the comprehensive dashboard tour."""
    from playwright.sync_api import sync_playwright

    console_messages: list[dict] = []
    page_errors: list[str] = []

    output_dir.mkdir(parents=True, exist_ok=True)
    report = []

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text}))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#workspace", state="attached", timeout=30000)

        page.wait_for_function(
            "() => Boolean(window.__DASHBOARD__?.layoutHost?.mountComplete)",
            timeout=30000,
        )

        previous_crop = None

        # ========== 1. PRESET FULL DASHBOARD SHOTS ==========
        logger.info("=== Capturing Presets (full dashboard) ===")
        for preset in PRESETS:
            logger.info(f"Applying preset: {preset}")
            apply_preset(page, preset)
            page.wait_for_timeout(1500)

            # Full dashboard shot
            output_path = output_dir / f"dashboard-{preset}.png"
            full_dashboard_screenshot(page, output_path)

            diff = 0.0
            if previous_crop:
                diff = image_diff_pct(previous_crop, output_path)
            previous_crop = output_path

            report.append({
                "type": "preset-full",
                "preset": preset,
                "path": str(output_path.relative_to(REPO_ROOT)),
                "diff_pct": diff,
            })
            logger.info(f"  {preset}: full dashboard, diff={diff:.1f}%")

        # ========== 2. STAGE VIEWS (crops) ==========
        logger.info("=== Capturing Stage Views (crops) ===")
        # Use the last preset's stage instance
        instance_id = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug) return null;
                const instances = dbg.debug.instances ? dbg.debug.instances() : [];
                const stage = instances.find(i => i.type === 'stage');
                return stage?.id || null;
            }"""
        )

        if instance_id:
            for view in STAGE_VIEWS:
                logger.info(f"Switching to view: {view}")
                page.evaluate(
                    """(view) => {
                        const dbg = window.__DASHBOARD__;
                        if (!dbg || !dbg.debug || !dbg.debug.setStageView) return;
                        dbg.debug.setStageView(view);
                    }""",
                    view,
                )
                page.wait_for_timeout(500)

                debug = wait_for_stage_view(page, instance_id, view)
                crop_path = output_dir / f"stage-{view}.png"
                rect = crop_panel_screenshot(page, instance_id, crop_path)

                diff = 0.0
                if previous_crop:
                    diff = image_diff_pct(previous_crop, crop_path)
                previous_crop = crop_path

                report.append({
                    "type": "stage-view",
                    "view": view,
                    "instance_id": instance_id,
                    "rect": rect,
                    "ready": debug.get("ready"),
                    "measured": debug.get("measured"),
                    "path": str(crop_path.relative_to(REPO_ROOT)),
                    "diff_pct": diff,
                })
                logger.info(f"  {view}: {rect['width']}x{rect['height']}, measured={debug.get('measured')}, diff={diff:.1f}%")

        # ========== 3. PANEL TYPES (full panel shots) ==========
        logger.info("=== Capturing Panel Types ===")
        for panel_type in PANEL_TYPES:
            panel_name = PANEL_NAMES.get(panel_type, panel_type)
            logger.info(f"Opening panel: {panel_type}")

            # Open panel as floating to capture cleanly
            instance_id = open_panel(page, panel_type)
            if not instance_id:
                logger.warning(f"  Failed to open {panel_type}")
                continue

            try:
                wait_for_panel_ready(page, instance_id)
                output_path = output_dir / f"{panel_name}.png"
                rect = crop_panel_screenshot(page, instance_id, output_path)

                diff = 0.0
                if previous_crop:
                    diff = image_diff_pct(previous_crop, output_path)
                previous_crop = output_path

                report.append({
                    "type": "panel",
                    "panel_type": panel_type,
                    "panel_name": panel_name,
                    "instance_id": instance_id,
                    "rect": rect,
                    "path": str(output_path.relative_to(REPO_ROOT)),
                    "diff_pct": diff,
                })
                logger.info(f"  {panel_name}: {rect['width']}x{rect['height']}, diff={diff:.1f}%")
            finally:
                close_panel(page, instance_id)

        # Check for errors
        console_errors = filter_console_errors(console_messages)
        duplicate_ids, duplicate_id_list = check_duplicate_ids(page)

        if console_errors:
            raise RuntimeError(f"Console errors: {console_errors}")
        if page_errors:
            raise RuntimeError(f"Page errors: {page_errors}")
        if duplicate_ids > 0:
            raise RuntimeError(f"Duplicate DOM ids: {duplicate_ids} ({duplicate_id_list})")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8085)
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "experiment.duckdb",
        help="Store the campaign writes and the dashboard reads.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=TOUR_OUTPUT,
        help="Where tour screenshots are written.",
    )
    parser.add_argument(
        "--skip-campaigns",
        action="store_true",
        help="Reuse existing store (skip campaign run).",
    )
    args = parser.parse_args()

    if not args.skip_campaigns:
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

    run_id = wait_for_records(args.port, min_records=5, timeout=180.0)
    logger.info(f"Run {run_id} has measured records")

    try:
        report = capture_tour(args.port, args.store, args.output, args.skip_campaigns)
        print(json.dumps(report, indent=2))
        return 0
    except Exception as e:
        logger.exception("Tour capture failed")
        return 1
    finally:
        if server_error:
            logger.error(f"Dashboard failed: {server_error[0]}")


if __name__ == "__main__":
    sys.exit(main())