#!/usr/bin/env python3
"""Can a researcher see a gap, and act on it? (TODO68)

The discovery map used to show only the cells the run had measured, so a gap
in the picture was invisible: there was nothing to click and nothing to
adopt. This probe opens the dashboard on a store with one measured cell, asks
the page what the grid holds, clicks a cell nobody measured, and presses the
button that writes the question down — then reads what the DOM and the
filesystem say happened.

Usage:
    uv run python scripts/probes/probe_dashboard_space.py
"""

from __future__ import annotations

import argparse
import json
import logging
import tempfile
import threading
from pathlib import Path

from dashboard_probe import (
    CHROMIUM_ARGS,
    SHOT_DIR,
    build_store,
    wait_for_http,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def probe(port: int, registry: Path) -> dict[str, object]:
    """Read the grid, click a gap, and press the button that acts on it."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=CHROMIUM_ARGS,
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)

        # The grid holds the declared space once the space has arrived.
        page.wait_for_function(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.discoveryMap) return false;
                const cells = dbg.discoveryMap.cellDataMap;
                let legal = 0;
                let measured = 0;
                for (const cell of cells.values()) {
                    if (cell.status === 'legal') legal += 1;
                    if (cell.status === 'measured') measured += 1;
                }
                return legal > 0 && measured > 0;
            }""",
            timeout=60000,
        )
        page.wait_for_timeout(1500)

        grid = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const map = dbg.discoveryMap;
                const counts = { measured: 0, legal: 0, void: 0 };
                for (const cell of map.cellDataMap.values()) {
                    counts[cell.status] = (counts[cell.status] || 0) + 1;
                }
                const voidMesh = map.voidMesh;
                return {
                    counts,
                    cells: map.cellDataMap.size,
                    void_vertices: voidMesh
                        ? voidMesh.geometry.getAttribute('position').count
                        : 0,
                    camera: {
                        position: dbg.camera.position.toArray(),
                        target: dbg.controls.target.toArray(),
                        distance: dbg.camera.position.distanceTo(
                            dbg.controls.target,
                        ),
                    },
                    legend: document.getElementById('legend-axes')?.innerText ?? '',
                };
            }"""
        )

        # The gap nearest the camera, so the click is not occluded — and not
        # behind a panel, which would swallow the click.
        target = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const map = dbg.discoveryMap;
                const panels = ['discovery-legend', 'plotter', 'hud', 'live-rail']
                    .map((id) => document.getElementById(id))
                    .filter((el) => el)
                    .map((el) => el.getBoundingClientRect());
                const covered = (x, y) =>
                    panels.some(
                        (r) => x >= r.left - 8 && x <= r.right + 8 && y >= r.top - 8 && y <= r.bottom + 8,
                    );
                const candidates = [];
                for (const [key, cell] of map.cellDataMap.entries()) {
                    if (cell.status !== 'legal') continue;
                    const mesh = map.cells.get(key);
                    if (!mesh) continue;
                    const point = mesh.position.clone();
                    point.y += 0.4;
                    point.project(dbg.camera);
                    const x = (point.x * 0.5 + 0.5) * window.innerWidth;
                    const y = (-point.y * 0.5 + 0.5) * window.innerHeight;
                    if (x < 40 || y < 40 || x > window.innerWidth - 40 || y > window.innerHeight - 40) continue;
                    if (covered(x, y)) continue;
                    candidates.push({ key, x, y, distance: mesh.position.distanceTo(dbg.camera.position) });
                }
                candidates.sort((a, b) => a.distance - b.distance);
                return candidates[0] ?? null;
            }"""
        )
        if not target:
            browser.close()
            return {"error": "no legal cell on the page", "grid": grid}

        page.mouse.move(target["x"], target["y"])
        page.wait_for_timeout(400)
        page.mouse.click(target["x"], target["y"])
        page.wait_for_timeout(900)

        drawer = page.evaluate(
            """() => {
                const panel = document.getElementById('cell-drawer');
                return {
                    transform: getComputedStyle(panel).transform,
                    text: panel.innerText.replace(/\\s+/g, ' ').slice(0, 220),
                    buttons: [...panel.querySelectorAll('.drawer-btn[data-action]')].map(
                        (b) => ({
                            action: b.dataset.action,
                            label: b.textContent.trim(),
                            disabled: b.disabled,
                        })
                    ),
                };
            }"""
        )

        page.click('.drawer-btn[data-action="quest"]')
        page.wait_for_timeout(1500)
        status = page.evaluate(
            "() => document.getElementById('drawer-status')?.textContent?.trim() ?? ''"
        )

        written = (
            sorted(p.name for p in registry.glob("*.json")) if registry.exists() else []
        )
        payload = {}
        if written:
            payload = json.loads((registry / written[0]).read_text(encoding="utf-8"))

        shot = SHOT_DIR / "dashboard-space.png"
        page.screenshot(path=str(shot))

        browser.close()
        return {
            "grid": grid,
            "target": target,
            "drawer": drawer,
            "status": status,
            "registered": written,
            "registration": payload,
            "page_errors": errors,
            "shot": str(shot),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8142)
    args = parser.parse_args()

    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )

    work = Path(tempfile.mkdtemp(prefix="computronium-space-"))
    store_path = work / "probe.duckdb"
    registry = work / "preregistrations"
    run_id = build_store(store_path)
    logger.info("store %s holds run %s", store_path, run_id)

    dashboard = WebDashboard(
        DashboardConfig(
            host="127.0.0.1",
            port=args.port,
            store_path=str(store_path),
            registration_dir=registry,
        )
    )

    def serve() -> None:
        import asyncio

        asyncio.run(dashboard.run())

    threading.Thread(target=serve, daemon=True).start()
    if not wait_for_http(args.port):
        logger.error("Dashboard did not start")
        return 1

    result = probe(args.port, registry)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
