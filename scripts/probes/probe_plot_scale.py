#!/usr/bin/env python3
"""Probe the Pareto chart's axis range (TODO68).

Regime measured (2026-10-20): the dashboard serves a store with 20 demo
records whose val_acc spans 0.078..0.65. The chart used to show 0.072..0.136
— the window of the first, partial dataset it had seen, because uPlot's
automatic range only ever widens and never follows a new dataset.

    uv run python scripts/probes/probe_plot_scale.py

Exits non-zero when an axis does not cover the data it plots.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PORT = 8105
STORE = REPO_ROOT / "experiment.duckdb"


def wait_for_http(port: int, timeout: float = 60.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/status", timeout=2
            ) as response:
                if response.status == 200:
                    return True
        except urllib.error.URLError, OSError:
            pass
        time.sleep(0.5)
    return False


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
            args=[
                "--use-gl=angle",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--no-sandbox",
            ],
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"http://localhost:{PORT}/", wait_until="load")
        page.wait_for_function(
            """() => {
                const plot = window.__DASHBOARD__?.plotter?.paretoPlot;
                return plot && plot.data[0].length > 0;
            }""",
            timeout=60000,
        )
        page.wait_for_timeout(1500)

        state = page.evaluate(
            """() => {
                const plot = window.__DASHBOARD__.plotter.paretoPlot;
                const ys = plot.data[1].filter(Number.isFinite);
                const xs = plot.data[0].filter(Number.isFinite);
                return {
                    n: plot.data[0].length,
                    y: [plot.scales.y.min, plot.scales.y.max],
                    x: [plot.scales.x.min, plot.scales.x.max],
                    dataY: [Math.min(...ys), Math.max(...ys)],
                    dataX: [Math.min(...xs), Math.max(...xs)],
                };
            }"""
        )
        print(json.dumps(state, indent=2))

        covers = (
            state["y"][0] <= state["dataY"][0]
            and state["y"][1] >= state["dataY"][1]
            and state["x"][0] <= state["dataX"][0]
            and state["x"][1] >= state["dataX"][1]
        )
        browser.close()

    if not covers:
        print("FAIL: an axis does not cover the data it plots")
        return 1
    print("OK: both axes cover their data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
