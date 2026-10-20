#!/usr/bin/env python3
"""Does the dashboard's interaction actually work? (TODO68)

The picture can look right while the thing behind it is dead: a drawer that
never opens, a tooltip that never appears. This probe drives the page the way
a person would — move the mouse over a pillar, click it, hover a chart point —
and reports what the DOM says happened.

Usage:
    uv run python scripts/probes/probe_dashboard_interaction.py
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
from pathlib import Path

from dashboard_probe import (
    CHROMIUM_ARGS,
    SHOT_DIR,
    wait_for_http,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]


def probe(port: int) -> dict[str, object]:
    """Click a measured pillar and hover a chart point; report what happened."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=CHROMIUM_ARGS,
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        errors: list[str] = []
        shots: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
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
        page.wait_for_timeout(2000)

        # Where is a measured pillar on the screen? A pillar can hide behind
        # another cell, so the cursor has to land on the one the probe means.
        candidates = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const found = [];
                for (const [key, cell] of dbg.discoveryMap.cellDataMap.entries()) {
                    if (cell.status !== 'measured') continue;
                    const mesh = dbg.discoveryMap.cells.get(key);
                    if (!mesh) continue;
                    const point = mesh.position.clone();
                    point.y += 1.0;
                    point.project(dbg.camera);
                    found.push({
                        key,
                        x: (point.x * 0.5 + 0.5) * window.innerWidth,
                        y: (-point.y * 0.5 + 0.5) * window.innerHeight,
                    });
                }
                return found;
            }"""
        )
        target = None
        for candidate in candidates:
            page.mouse.move(candidate["x"], candidate["y"])
            page.wait_for_timeout(250)
            hovered = page.evaluate(
                "() => window.__DASHBOARD__.discoveryMap.hoveredCell"
            )
            if hovered == candidate["key"]:
                target = candidate
                break

        drawer_before = page.evaluate(
            "() => getComputedStyle(document.getElementById('cell-drawer')).transform"
        )
        hover_state: dict[str, object] = {}
        if target:
            page.mouse.move(target["x"], target["y"])
            page.wait_for_timeout(400)
            frame_a = page.evaluate("() => window.__DASHBOARD__.hud.animationTime")
            page.wait_for_timeout(600)
            frame_b = page.evaluate("() => window.__DASHBOARD__.hud.animationTime")
            hover_state = page.evaluate(
                """() => {
                    const dbg = window.__DASHBOARD__;
                    const map = dbg.discoveryMap;
                    const hits = map.raycaster.intersectObjects(
                        [...map.cells.values()], true);
                    return {
                        hovered: map.hoveredCell,
                        mouse: {x: map.mouse.x, y: map.mouse.y},
                        cells: map.cells.size,
                        cameraType: map.camera.type,
                        cameraPosition: map.camera.position.toArray(),
                        rayHits: hits.length,
                        firstHit: hits[0] ? hits[0].object.userData.cellKey : null,
                        firstHitParent: hits[0]
                            ? hits[0].object.parent?.userData?.cellKey
                            : null,
                        measured: [...map.cellDataMap.entries()]
                            .filter(([, c]) => c.status === 'measured')
                            .map(([k]) => k),
                    };
                }"""
            )
            hover_state["frame_clock"] = [frame_a, frame_b]
            page.mouse.click(target["x"], target["y"])
            page.wait_for_timeout(900)
        drawer_after = page.evaluate(
            """() => {
                const drawer = document.getElementById('cell-drawer');
                const style = getComputedStyle(drawer);
                return {
                    transform: style.transform,
                    text: drawer.innerText.replace(/\\s+/g, ' ').slice(0, 220),
                    hudRight: document.getElementById('hud').style.right,
                };
            }"""
        )
        drawer_shot = SHOT_DIR / "dashboard-drawer.png"
        page.screenshot(path=str(drawer_shot))
        shots.append(str(drawer_shot))

        # Escape closes it again.
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        drawer_closed = page.evaluate(
            "() => getComputedStyle(document.getElementById('cell-drawer')).transform"
        )

        # Hover a Pareto point: the tooltip must name it.
        point = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const plot = dbg.plotter.paretoPlot;
                if (!plot) return null;
                const pts = dbg.plotter.paretoXData.map((x, i) => ({
                    x: plot.valToPos(x, 'x'),
                    y: plot.valToPos(dbg.plotter.paretoYData[i], 'y'),
                })).filter(p => Number.isFinite(p.x) && Number.isFinite(p.y));
                if (!pts.length) return null;
                const canvas = plot.ctx.canvas.getBoundingClientRect();
                const box = plot.bbox;
                return {
                    x: canvas.left + box.left + pts[0].x,
                    y: canvas.top + box.top + pts[0].y,
                };
            }"""
        )
        tooltip = {"display": "none", "text": ""}
        if point:
            page.mouse.move(point["x"], point["y"])
            page.wait_for_timeout(600)
            tooltip = page.evaluate(
                """() => {
                    const tip = document.getElementById('plotter-tooltip');
                    if (!tip) return {display: 'missing', text: ''};
                    return {display: getComputedStyle(tip).display, text: tip.innerText};
                }"""
            )

        # The other two charts must name their arms.
        for tab in ("ablation", "variability"):
            page.click(f'.plotter-tab[data-tab="{tab}"]')
            page.wait_for_timeout(1200)
            axis = page.evaluate(
                """() => {
                    const panel = document.getElementById('plotter-ablation');
                    const wrap = panel.querySelector('.u-wrap');
                    const axisCanvas = wrap?.querySelector('.u-axis');
                    return axisCanvas ? 'drawn' : 'missing';
                }"""
            )
            logger.info("tab %s: axis %s", tab, axis)
            state = page.evaluate(
                """() => {
                    const plot = window.__DASHBOARD__.plotter.ablationPlot;
                    if (!plot) return null;
                    return {
                        xMin: plot.scales.x.min,
                        xMax: plot.scales.x.max,
                        yMin: plot.scales.y.min,
                        yMax: plot.scales.y.max,
                        data: plot.data,
                        pos0: plot.valToPos(0, 'x'),
                        pos1: plot.valToPos(1, 'x'),
                        splits: plot.axes[0].splits
                            ? plot.axes[0].splits(plot, 0, 'x')
                            : null,
                    };
                }"""
            )
            logger.info("tab %s state: %s", tab, state)
            shot = SHOT_DIR / f"dashboard-{tab}.png"
            shots.append(str(shot))
            page.screenshot(path=str(shot))

        # The keyboard shortcuts the docs promise.
        page.keyboard.press("2")
        page.wait_for_timeout(600)
        tab = page.evaluate(
            "() => document.querySelector('.plotter-tab.active')?.dataset.tab"
        )
        page.keyboard.press("h")
        page.wait_for_timeout(300)
        hud_hidden = page.evaluate(
            "() => getComputedStyle(document.getElementById('hud')).display"
        )
        page.keyboard.press("h")
        page.keyboard.press("1")
        page.wait_for_timeout(300)
        logger.info(
            "shortcuts: tab after '2' is %s, hud after 'h' is %s", tab, hud_hidden
        )

        browser.close()
        return {
            "target": target,
            "hover": hover_state,
            "drawer_before": drawer_before,
            "drawer_after": drawer_after,
            "drawer_closed": drawer_closed,
            "tooltip": tooltip,
            "page_errors": errors,
            "shots": shots,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8139)
    parser.add_argument("--store", type=Path, default=REPO_ROOT / "experiment.duckdb")
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

    result = probe(args.port)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
