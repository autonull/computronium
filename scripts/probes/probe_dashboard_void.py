#!/usr/bin/env python3
"""Can a researcher read why a cell is void? (TODO68)

The void markers are one mesh, drawn and never picked, so the cursor could not
name one of them: the reason a cell is refused lived in the legend, counted
up, and nowhere near the cell. This probe opens the dashboard on a store with
a run, moves the mouse onto void markers the way a person would, and reads
what the page says under the cursor — then clicks one and reads the drawer.

Usage:
    uv run python scripts/probes/probe_dashboard_void.py
"""

from __future__ import annotations

import argparse
import json
import logging
import tempfile
from pathlib import Path

from dashboard_probe import (
    CHROMIUM_ARGS,
    SHOT_DIR,
    build_store,
    serving_dashboard,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def probe(port: int) -> dict[str, object]:
    """Hover a void marker, read the readout, and click it."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
        page.wait_for_function(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.discoveryMap) return false;
                return dbg.discoveryMap.voidMesh !== null;
            }""",
            timeout=60000,
        )
        page.wait_for_timeout(1500)

        # The void markers on the screen, nearest the camera first.
        candidates = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const mesh = dbg.discoveryMap.voidMesh;
                const positions = mesh.geometry.getAttribute('position');
                const panels = ['discovery-legend', 'plotter', 'hud', 'live-rail']
                    .map((id) => document.getElementById(id))
                    .filter((el) => el)
                    .map((el) => el.getBoundingClientRect());
                const covered = (x, y) =>
                    panels.some(
                        (r) => x >= r.left - 8 && x <= r.right + 8 &&
                               y >= r.top - 8 && y <= r.bottom + 8,
                    );
                const found = [];
                for (let i = 0; i + 3 < positions.count; i += 4) {
                    let x = 0, y = 0, z = 0;
                    for (let k = 0; k < 4; k += 1) {
                        x += positions.getX(i + k);
                        y += positions.getY(i + k);
                        z += positions.getZ(i + k);
                    }
                    const point = dbg.controls.target.clone().set(x / 4, y / 4, z / 4);
                    const distance = point.distanceTo(dbg.camera.position);
                    point.project(dbg.camera);
                    const sx = (point.x * 0.5 + 0.5) * window.innerWidth;
                    const sy = (-point.y * 0.5 + 0.5) * window.innerHeight;
                    if (sx < 40 || sy < 40) continue;
                    if (sx > window.innerWidth - 40 || sy > window.innerHeight - 40) continue;
                    if (covered(sx, sy)) continue;
                    found.push({ x: sx, y: sy, distance });
                }
                found.sort((a, b) => a.distance - b.distance);
                return found.slice(0, 12);
            }"""
        )
        if not candidates:
            browser.close()
            return {"error": "no void marker on the page"}

        readouts: list[dict[str, object]] = []
        chosen: dict[str, object] | None = None
        for candidate in candidates:
            page.mouse.move(candidate["x"], candidate["y"])
            page.wait_for_timeout(350)
            readout = page.evaluate(
                """() => {
                    const element = document.getElementById('cell-readout');
                    if (!element) return null;
                    return {
                        visible: getComputedStyle(element).display !== 'none',
                        text: element.innerText.replace(/\\s+/g, ' ').trim(),
                    };
                }"""
            )
            readouts.append({"at": candidate, "readout": readout})
            if (
                readout
                and readout.get("visible")
                and "Void" in str(readout.get("text"))
            ):
                chosen = candidate
                break

        drawer: dict[str, object] = {}
        if chosen:
            page.mouse.click(chosen["x"], chosen["y"])
            page.wait_for_timeout(900)
            drawer = page.evaluate(
                """() => {
                    const panel = document.getElementById('cell-drawer');
                    return {
                        transform: getComputedStyle(panel).transform,
                        text: panel.innerText.replace(/\\s+/g, ' ').slice(0, 260),
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

        shot = SHOT_DIR / "dashboard-void.png"
        page.screenshot(path=str(shot))
        browser.close()
        return {
            "candidates": len(candidates),
            "readouts": readouts,
            "chosen": chosen,
            "drawer": drawer,
            "page_errors": errors,
            "shot": str(shot),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8143)
    args = parser.parse_args()

    work = Path(tempfile.mkdtemp(prefix="computronium-void-"))
    store_path = work / "probe.duckdb"
    run_id = build_store(store_path)
    logger.info("store %s holds run %s", store_path, run_id)

    with serving_dashboard(store_path, args.port):
        result = probe(args.port)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
