#!/usr/bin/env python3
"""Probe the dashboard's plot scales and cell drawer (TODO68).

Regime measured (2026-10-20): the dashboard reads a store with 20 demo
records (4 credit arms x 5 seeds, val_acc 0.078..0.65) and the page is
driven headless.

    uv run python scripts/probes/probe_dashboard_plot_drawer.py

Prints the Pareto chart's data and scale, every measured cell's accuracy and
curve length, and writes logs/probe-drawer.png with the cell drawer open —
so a stale chart or an empty sparkline is visible without squinting at a
screenshot.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

from dashboard_probe import CHROMIUM_ARGS, wait_for_http

REPO_ROOT = Path(__file__).resolve().parents[2]
PORT = 8100
STORE = REPO_ROOT / "experiment.duckdb"


def main() -> int:
    from playwright.sync_api import sync_playwright

    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )

    dashboard = WebDashboard(
        DashboardConfig(host="127.0.0.1", port=PORT, store_path=str(STORE))
    )

    def serve() -> None:
        import asyncio

        asyncio.run(dashboard.run())

    threading.Thread(target=serve, daemon=True).start()
    if not wait_for_http(PORT):
        print("dashboard did not start")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=CHROMIUM_ARGS,
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        page.on("console", lambda m: errors.append(f"console {m.type}: {m.text}"))
        page.goto(f"http://localhost:{PORT}/", wait_until="load")
        page.wait_for_function(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg) return false;
                for (const cell of dbg.discoveryMap.cellDataMap.values()) {
                    if (cell.status === 'measured') return true;
                }
                return false;
            }""",
            timeout=60000,
        )
        page.wait_for_timeout(1500)

        state = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const plot = dbg.plotter.paretoPlot;
                const cells = [];
                for (const [key, cell] of dbg.discoveryMap.cellDataMap) {
                    if (cell.status === 'measured') cells.push({
                        key,
                        val_acc: cell.metrics?.val_acc,
                        curvePoints: cell.curve?.length ?? 0,
                        chance: cell.chance,
                    });
                }
                return {
                    yScale: plot ? plot.scales.y.min + '..' + plot.scales.y.max : null,
                    xScale: plot ? plot.scales.x.min + '..' + plot.scales.x.max : null,
                    dataLen: plot ? plot.data[0].length : 0,
                    cells,
                };
            }"""
        )
        print(json.dumps(state, indent=2, default=str))

        # Open the drawer on the strongest cell and photograph it.
        page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                let best = null;
                for (const [key, cell] of dbg.discoveryMap.cellDataMap) {
                    if (cell.status !== 'measured') continue;
                    if (!best || (cell.metrics?.val_acc ?? 0) > (best[1].metrics?.val_acc ?? 0)) {
                        best = [key, cell];
                    }
                }
                if (best) window.dispatchEvent(new CustomEvent('cell-selected', { detail: best[1] }));
            }"""
        )
        page.wait_for_timeout(1500)
        shot = REPO_ROOT / "logs" / "probe-drawer.png"
        shot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(shot))
        print("page errors:", errors)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
