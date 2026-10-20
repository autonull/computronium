#!/usr/bin/env python3
"""What the terrain's columns say (TODO69 Phase 5).

A diagnostic for the terrain: the surface it draws is a column per (x, y)
pair, collapsed over z, and a column is a crater when every cell in it is
refused. When the terrain does not look like the space, this prints the
columns it builds — their status and their accuracy — and the meshes it
drew, so the cause is in the numbers rather than in the picture.

Usage:
    uv run python scripts/probes/probe_terrain_columns.py
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

from dashboard_probe import CHROMIUM_ARGS, wait_for_http

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    from playwright.sync_api import sync_playwright

    port = 8143
    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )

    dashboard = WebDashboard(
        DashboardConfig(
            host="127.0.0.1",
            port=port,
            store_path=str(REPO_ROOT / "experiment.duckdb"),
        )
    )

    def serve() -> None:
        import asyncio

        asyncio.run(dashboard.run())

    threading.Thread(target=serve, daemon=True).start()
    if not wait_for_http(port):
        logger.error("Dashboard did not start")
        return 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=list(CHROMIUM_ARGS))
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
        page.wait_for_timeout(8000)
        report = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                const switcher = dbg.viewSwitcher;
                const views = switcher.views.map((view) => view.id);
                const terrain = switcher.views.find((v) => v.id === 'terrain');
                const built = terrain.columns();
                const counts = {measured: 0, gap: 0, void: 0};
                built.columns.forEach((column) => { counts[column.status] += 1; });
                const group = terrain.group;
                const meshes = [];
                group.traverse((child) => {
                    if (child.isMesh) {
                        meshes.push({
                            name: child.type,
                            vertices: child.geometry.attributes.position
                                ? child.geometry.attributes.position.count : 0,
                            index: child.geometry.index
                                ? child.geometry.index.count : 0,
                            visible: child.visible,
                        });
                    }
                });
                return {
                    views,
                    xValues: built.xValues,
                    yValues: built.yValues,
                    counts,
                    columns: built.columns.map((c) => [c.status, c.accuracy, c.arm]),
                    meshes,
                };
            }"""
        )
        print(json.dumps(report, indent=2)[:4000])
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
