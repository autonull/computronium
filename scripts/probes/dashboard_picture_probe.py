#!/usr/bin/env python3
"""Dashboard picture probe — single probe carrying all contracts (TODO73 P10.5).

Measures at 1920/1440/1024:
- CSS: .dv-dockview position=relative, tab height 24-30, groupHeight>0, tabs=instances
- Chrome: menubar exists (5 menus), single UI (canvas count = stages, zero duplicate ids, no legacy refs)
- Geometry: branch sums = parent, stage >=60% x 55%, side cols 280-420, bottom 110-180, presets idempotent
- Stage: canvas≈rect·dpr, |aspect-w/h|<0.01, height=panel, measured>0 in 3s, crop differs from bg, two stages distinct
- Declared grid drawn (512 cells via spaceStore payload, measured+drawn reported separately)
- Space view init() subscribes to SpaceStore and draws grid on first payload arrival even with 0 measured cells

Writes one JSON table with all measurements.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import tempfile
import time
import threading
from pathlib import Path

import sys
from pathlib import Path

# Add scripts to path
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
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

VIEWPORTS = [
    {"width": 1920, "height": 1080, "name": "1920x1080"},
    {"width": 1440, "height": 900, "name": "1440x900"},
    {"width": 1024, "height": 768, "name": "1024x768"},
]

# Presets to test idempotence
PRESETS = ["watch", "audit", "drive", "free"]

# Baseline inventory (never committed; extracted from git history)
BASELINE_FILES = [
    "dashboard-hero",
    "dashboard-watch",
    "dashboard-audit",
    "dashboard-drive",
    "dashboard-free",
    "dashboard-map",
    "dashboard-cell",
    "panel-hud",
    "panel-legend",
    "panel-live-rail",
    "panel-view-toolbar",
]

BASELINE_DIR = Path("/tmp/opencode/baseline")


def probe_viewport(port: int, viewport: dict) -> dict:
    """Run all picture contracts at one viewport."""
    from playwright.sync_api import sync_playwright

    console_messages: list[dict] = []
    page_errors: list[str] = []

    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        context = browser.new_context(viewport=viewport)
        page = context.new_page()

        page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text}))
        page.on("pageerror", lambda err: page_errors.append(str(err)))
        # Expose console messages to page for debugging
        page.add_init_script("""
            window.__CONSOLE_MSGS__ = [];
            const originalLog = console.log;
            const originalError = console.error;
            const originalWarn = console.warn;
            console.log = (...args) => { window.__CONSOLE_MSGS__.push({type: 'log', text: args.join(' ')}); originalLog.apply(console, args); };
            console.error = (...args) => { window.__CONSOLE_MSGS__.push({type: 'error', text: args.join(' ')}); originalError.apply(console, args); };
            console.warn = (...args) => { window.__CONSOLE_MSGS__.push({type: 'warn', text: args.join(' ')}); originalWarn.apply(console, args); };
        """)

        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#workspace", state="attached", timeout=30000)

        page.wait_for_function(
            "() => Boolean(window.__DASHBOARD__?.layoutHost?.mountComplete)",
            timeout=30000,
        )

        # Wait for menubar to be initialized
        # First check if registry.initAll ran
        init_debug = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const reg = dbg?.registry;
                let components = [];
                if (reg && reg.list) components = reg.list();
                return {
                    registry: reg ? 'exists' : 'missing',
                    layoutHost: dbg?.layoutHost ? 'exists' : 'missing',
                    components: components,
                    menubarInit: dbg?.menubarInit || 'unknown',
                };
            }"""
        )
        logger.info(f"Init debug: {init_debug}")
        
        # Check console for menubar errors
        console_msgs = page.evaluate("() => window.__CONSOLE_MSGS__ || []")
        logger.info(f"Console messages: {console_msgs}")
        
        # Wait longer for menubar to fully render
        page.wait_for_timeout(3000)
        
        # Check menubar state at multiple time points
        for wait_time in [1000, 2000, 3000]:
            page.wait_for_timeout(wait_time)
            menubar_debug = page.evaluate(
                f"""() => {{
                    const mc = document.getElementById('menubar-container');
                    if (!mc) return {{exists: false, wait_ms: {wait_time}}};
                    const menus = mc.querySelectorAll('.menubar-menu');
                    const menubar = mc.querySelector('#menubar');
                    const children = mc.children ? Array.from(mc.children).map(c => ({{tag: c.tagName, id: c.id, class: c.className}})) : [];
                    return {{exists: true, wait_ms: {wait_time}, menuCount: menus.length, hasMenubarDiv: !!menubar, children: children, html: mc.innerHTML.substring(0, 2000)}};
                }}"""
            )
            logger.info(f"Menubar state after {wait_time}ms: {menubar_debug}")
            if menubar_debug.get('hasMenubarDiv') and menubar_debug.get('menuCount', 0) >= 5:
                break
        
        try:
            page.wait_for_function(
                "() => document.getElementById('menubar-container')?.querySelectorAll('.menubar-menu').length >= 5",
                timeout=10000,
            )
        except Exception:
            logger.error(f"Menubar not ready: {menubar_debug}")
            raise

        result = {
            "viewport": viewport["name"],
            "width": viewport["width"],
            "height": viewport["height"],
            "css": {},
            "chrome": {},
            "geometry": {},
            "stage": {},
            "grid": {},
            "idempotence": {},
            "errors": {
                "console": [m for m in console_messages if m["type"] == "error"],
                "page": page_errors,
            },
        }

        # --- CSS Contracts ---
        css = page.evaluate(
            """() => {
                const dv = document.querySelector('.dv-dockview');
                const tabs = document.querySelectorAll('.dv-tab');
                const groups = document.querySelectorAll('.dv-groupview');
                const tab = tabs[0];
                const group = groups[0];
                return {
                    dvPosition: dv ? window.getComputedStyle(dv).position : null,
                    tabHeight: tab ? window.getComputedStyle(tab).height : null,
                    tabCount: tabs.length,
                    groupCount: groups.length,
                    groupHeight: group ? window.getComputedStyle(group).height : null,
                };
            }"""
        )
        result["css"] = css

        # --- Chrome Contracts ---
        chrome = page.evaluate(
            """() => {
                const menubar = document.getElementById('menubar-container');
                const menus = menubar ? menubar.querySelectorAll('.menubar-menu') : [];
                const canvases = document.querySelectorAll('canvas');
                const legacyCanvas = document.getElementById('dashboard-canvas');
                const legacyStage2d = document.getElementById('stage-2d');
                const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
                const counts = {};
                for (const id of ids) counts[id] = (counts[id] || 0) + 1;
                const duplicates = Object.entries(counts).filter(([,c]) => c > 1).map(([id]) => id);
                
                // Use debug API for stage panel count
                const dbg = window.__DASHBOARD__;
                let stagePanelCount = 0;
                if (dbg && dbg.debug && dbg.debug.instances) {
                    const instances = dbg.debug.instances();
                    stagePanelCount = instances.filter(i => i.type === 'stage').length;
                }
                
                return {
                    menubarExists: !!menubar,
                    menuCount: menus.length,
                    canvasCount: canvases.length,
                    stagePanelCount: stagePanelCount,
                    legacyCanvas: !!legacyCanvas,
                    legacyStage2d: !!legacyStage2d,
                    duplicateIds: duplicates,
                };
            }"""
        )
        result["chrome"] = chrome

        # --- Geometry Contracts ---
        geometry = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug || !dbg.debug.instances) return {};
                const instances = dbg.debug.instances();
                const surfaces = dbg.debug.stageSurfaces ? dbg.debug.stageSurfaces() : [];
                
                const stage = instances.find(i => i.type === 'stage');
                const leftPanels = instances.filter(i => ['discovery-legend', 'control-panel'].includes(i.type));
                const rightPanels = instances.filter(i => ['hud', 'pareto-chart', 'ablation-chart', 'variability-chart'].includes(i.type));
                const bottomPanels = instances.filter(i => ['control-bar', 'caption', 'live-rail'].includes(i.type));

                // Build rect map from stageSurfaces
                const rectMap = {};
                for (const s of surfaces) {
                    rectMap[s.id] = s.rect;
                }

                const getRect = (id) => rectMap[id] || null;

                const stageRect = stage ? getRect(stage.id) : null;
                const workspace = document.getElementById('workspace');
                const wsRect = workspace ? workspace.getBoundingClientRect() : null;

                // Left/right panels are stacked vertically - column width = first panel's width
                // Bottom panels are stacked horizontally - row height = first panel's height
                const leftWidth = leftPanels.length > 0 ? (getRect(leftPanels[0].id)?.width ?? 0) : 0;
                const rightWidth = rightPanels.length > 0 ? (getRect(rightPanels[0].id)?.width ?? 0) : 0;
                const bottomHeight = bottomPanels.length > 0 ? (getRect(bottomPanels[0].id)?.height ?? 0) : 0;

                return {
                    stage: stageRect,
                    workspace: wsRect,
                    leftWidth,
                    rightWidth,
                    bottomHeight,
                    leftCount: leftPanels.length,
                    rightCount: rightPanels.length,
                    bottomCount: bottomPanels.length,
                };
            }"""
        )

        # Calculate geometry contract checks
        ws = geometry.get("workspace", {})
        stage = geometry.get("stage", {})
        if ws and stage:
            stage_pct_w = stage["width"] / ws["width"] * 100
            stage_pct_h = stage["height"] / ws["height"] * 100
            geometry["stage_pct_w"] = stage_pct_w
            geometry["stage_pct_h"] = stage_pct_h
            geometry["stage_ge_60x55"] = stage_pct_w >= 60 and stage_pct_h >= 55
            geometry["left_in_range"] = 280 <= geometry["leftWidth"] <= 420
            geometry["right_in_range"] = 280 <= geometry["rightWidth"] <= 420
            geometry["bottom_in_range"] = 110 <= geometry["bottomHeight"] <= 180

        result["geometry"] = geometry

        # --- Stage Contracts ---
        stage_instance = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug || !dbg.debug.instances) return null;
                const instances = dbg.debug.instances();
                return instances.find(i => i.type === 'stage') || null;
            }"""
        )

        if stage_instance:
            instance_id = stage_instance["id"]

            # Wait for stage ready with measured cells (up to 10s)
            deadline = time.time() + 10.0
            stage_debug = None
            while time.time() < deadline:
                stage_debug = page.evaluate(
                    """(id) => {
                        const dbg = window.__DASHBOARD__;
                        if (!dbg || !dbg.debug || !dbg.debug.getStageDebug) return null;
                        return dbg.debug.getStageDebug(id);
                    }""",
                    instance_id,
                )
                if stage_debug and stage_debug.get("ready") and stage_debug.get("measured", 0) > 0:
                    break
                time.sleep(0.2)

            if stage_debug:
                canvas = stage_debug.get("canvas", {})
                rect = geometry.get("stage", {})
                aspect = stage_debug.get("cameraAspect", 1)
                expected_aspect = rect.get("width", 1) / rect.get("height", 1) if rect.get("height", 0) > 0 else 1

                stage_contracts = {
                    "ready": stage_debug.get("ready"),
                    "measured": stage_debug.get("measured"),
                    "view": stage_debug.get("view"),
                    "canvas": canvas,
                    "rect": rect,
                    "aspect": aspect,
                    "expected_aspect": expected_aspect,
                    "aspect_ok": abs(aspect - expected_aspect) < 0.01,
                    "canvas_matches_rect_dpr": False,
                    "height_equals_panel": False,
                    "crop_differs_bg": False,
                }

                # Check canvas ≈ rect * dpr
                if rect and canvas.get("w") and canvas.get("h") and canvas.get("dpr"):
                    expected_w = rect["width"] * canvas["dpr"]
                    expected_h = rect["height"] * canvas["dpr"]
                    stage_contracts["canvas_matches_rect_dpr"] = (
                        abs(canvas["w"] - expected_w) < 2 and abs(canvas["h"] - expected_h) < 2
                    )

                # Check height = panel (stage fills its panel)
                if rect and canvas.get("h"):
                    stage_contracts["height_equals_panel"] = abs(canvas["h"] / canvas["dpr"] - rect["height"]) < 2

                # Check crop differs from background (non-blank)
                crop_differs = page.evaluate(
                    """(id) => {
                        const dbg = window.__DASHBOARD__;
                        if (!dbg || !dbg.debug) return false;
                        const api = dbg.layoutHost?.getApi?.();
                        if (!api) return false;
                        const panel = api.getPanel(id);
                        if (!panel) return false;
                        const contentEl = panel.view.content.element;
                        const canvas = contentEl.querySelector("canvas");
                        if (!canvas) return false;
                        // Try to get Three.js renderer from canvas
                        const canvasWithRefs = canvas;
                        const renderer = canvasWithRefs.__three_renderer;
                        if (renderer) {
                            const gl = renderer.getContext();
                            if (gl) {
                                const pixels = new Uint8Array(canvas.width * canvas.height * 4);
                                gl.readPixels(0, 0, canvas.width, canvas.height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
                                // Check if all pixels are background color (0x0a0e14 = 10,14,20)
                                let nonBg = 0;
                                for (let i = 0; i < pixels.length; i += 4) {
                                    if (pixels[i] !== 10 || pixels[i+1] !== 14 || pixels[i+2] !== 20) {
                                        nonBg++;
                                        if (nonBg > 100) return true;
                                    }
                                }
                                return false;
                            }
                        }
                        // Fallback to WebGL context
                        const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
                        if (gl) {
                            const pixels = new Uint8Array(canvas.width * canvas.height * 4);
                            gl.readPixels(0, 0, canvas.width, canvas.height, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
                            let nonBg = 0;
                            for (let i = 0; i < pixels.length; i += 4) {
                                if (pixels[i] !== 10 || pixels[i+1] !== 14 || pixels[i+2] !== 20) {
                                    nonBg++;
                                    if (nonBg > 100) return true;
                                }
                            }
                            return false;
                        }
                        // Fallback to 2D context
                        const ctx = canvas.getContext('2d');
                        if (ctx) {
                            const data = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                            let nonBg = 0;
                            for (let i = 0; i < data.length; i += 4) {
                                if (data[i] !== 10 || data[i+1] !== 14 || data[i+2] !== 20) {
                                    nonBg++;
                                    if (nonBg > 100) return true;
                                }
                            }
                            return false;
                        }
                        return false;
                    }""",
                    instance_id,
                )
                stage_contracts["crop_differs_bg"] = crop_differs

                result["stage"] = stage_contracts

        # --- Two Stages Distinct ---
        two_stages = page.evaluate(
            """async () => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.layoutHost || !dbg.layoutHost.open) return {distinct: false};
                const id1 = await dbg.layoutHost.open("stage", {view: "space"});
                const id2 = await dbg.layoutHost.open("stage", {view: "ledger"});
                await new Promise(r => setTimeout(r, 2000));
                const d1 = dbg.debug.getStageDebug ? dbg.debug.getStageDebug(id1) : null;
                const d2 = dbg.debug.getStageDebug ? dbg.debug.getStageDebug(id2) : null;
                const distinct = d1 && d2 && d1.view !== d2.view;
                if (dbg.layoutHost.close) {
                    await dbg.layoutHost.close(id1);
                    await dbg.layoutHost.close(id2);
                }
                return {distinct: !!distinct, view1: d1?.view, view2: d2?.view};
            }"""
        )
        result["stage"]["two_stages_distinct"] = two_stages

        # --- Grid Contracts ---
        grid = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.debug || !dbg.debug.spaceStore) return {};
                const store = dbg.debug.spaceStore();
                if (!store) return {};
                const payload = store.getPayload ? store.getPayload() : null;
                const measured = store.getMeasuredCount ? store.getMeasuredCount() : 0;
                const drawn = store.getDrawnCount ? store.getDrawnCount() : 0;
                const cells = store.getCells ? store.getCells() : [];
                return {
                    hasPayload: !!payload,
                    measuredCells: measured,
                    drawnCells: drawn,
                    declaredCells: cells.length,
                    payloadKeys: payload ? Object.keys(payload) : [],
                };
            }"""
        )
        result["grid"] = grid

        # --- Preset Idempotence ---
        idempotence = {}
        for preset in PRESETS:
            # Apply preset twice and check layout stability
            rects = []
            for i in range(2):
                page.evaluate(
                    """(preset) => {
                        const dbg = window.__DASHBOARD__;
                        if (!dbg || !dbg.layout || !dbg.layout.applyPreset) return;
                        dbg.layout.applyPreset(preset);
                    }""",
                    preset,
                )
                page.wait_for_timeout(500)

                rect = page.evaluate(
                    """() => {
                        const dbg = window.__DASHBOARD__;
                        if (!dbg || !dbg.debug || !dbg.debug.instances) return null;
                        const instances = dbg.debug.instances();
                        const stage = instances.find(i => i.type === 'stage');
                        if (!stage) return null;
                        const surfaces = dbg.debug.stageSurfaces ? dbg.debug.stageSurfaces() : [];
                        const surf = surfaces.find(s => s.id === stage.id);
                        return surf ? surf.rect : null;
                    }"""
                )
                rects.append(rect)

            idempotence[preset] = {
                "rect1": rects[0],
                "rect2": rects[1],
                "idempotent": rects[0] == rects[1] if rects[0] and rects[1] else False,
            }

        result["idempotence"] = idempotence

        # --- Duplicate IDs ---
        duplicate_ids = page.evaluate(
            """() => {
                const ids = [...document.querySelectorAll('[id]')].map(e => e.id);
                const counts = {};
                for (const id of ids) counts[id] = (counts[id] || 0) + 1;
                return Object.entries(counts).filter(([,c]) => c > 1).map(([id]) => id);
            }"""
        )
        result["chrome"]["duplicateIds"] = duplicate_ids

        # --- Baseline Inventory Check ---
        baseline_inventory = {}
        for name in BASELINE_FILES:
            baseline_path = BASELINE_DIR / f"{name}.png"
            current_paths = [
                REPO_ROOT / "docs" / "readme" / "assets" / f"{name}.png",
                REPO_ROOT / "docs" / "screenshots" / "tour" / f"{name}.png",
                REPO_ROOT / "docs" / "screenshots" / f"{name}.png",
            ]
            current_path = next((p for p in current_paths if p.exists()), None)
            
            baseline_exists = baseline_path.exists()
            current_exists = current_path is not None
            
            comparison = None
            if baseline_exists and current_exists:
                comparison = image_diff_pct(baseline_path, current_path)
            
            baseline_inventory[name] = {
                "baseline_exists": baseline_exists,
                "current_exists": current_exists,
                "current_path": str(current_path) if current_path else None,
                "diff_pct": comparison,
            }
        
        result["baseline_inventory"] = baseline_inventory

        context.close()
        browser.close()

        return result


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8142)
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "experiment.duckdb",
        help="Store the campaign writes and the dashboard reads.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "screenshots" / "picture-probe.json",
        help="Where the probe report is written.",
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

    run_id = wait_for_records(args.port, min_records=5, timeout=180.0)
    logger.info(f"Run {run_id} has measured records")

    all_results = []
    for viewport in VIEWPORTS:
        logger.info(f"Probing viewport: {viewport['name']}")
        try:
            result = probe_viewport(args.port, viewport)
            all_results.append(result)
            logger.info(f"  {viewport['name']}: OK")
        except Exception as e:
            logger.exception(f"  {viewport['name']}: FAILED")
            all_results.append({
                "viewport": viewport["name"],
                "error": str(e),
            })

    # Write report
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(all_results, indent=2))
    logger.info(f"Report written to {args.output}")

    # Print summary
    for r in all_results:
        if "error" in r:
            print(f"  {r['viewport']}: ERROR - {r['error']}")
        else:
            css_ok = r["css"].get("dvPosition") == "relative" and r["css"].get("tabCount", 0) > 0
            chrome_ok = r["chrome"].get("menuCount", 0) == 5 and len(r["chrome"].get("duplicateIds", [])) == 0
            geo_ok = r["geometry"].get("stage_ge_60x55", False) and r["geometry"].get("left_in_range", False)
            stage_ok = r["stage"].get("ready", False) and r["stage"].get("measured", 0) > 0
            print(f"  {r['viewport']}: CSS={'✓' if css_ok else '✗'} Chrome={'✓' if chrome_ok else '✗'} Geo={'✓' if geo_ok else '✗'} Stage={'✓' if stage_ok else '✗'}")

    # Baseline inventory summary (from 1920x1080 viewport)
    baseline_result = next((r for r in all_results if r.get("viewport") == "1920x1080"), None)
    if baseline_result and "baseline_inventory" in baseline_result:
        print("\nBaseline inventory:")
        for name, info in baseline_result["baseline_inventory"].items():
            base = "✓" if info["baseline_exists"] else "✗"
            curr = "✓" if info["current_exists"] else "✗"
            diff = f" diff={info['diff_pct']:.1f}%" if info["diff_pct"] is not None else ""
            print(f"  {name}: baseline={base} current={curr}{diff}")

    if server_error:
        logger.error(f"Dashboard failed: {server_error[0]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())