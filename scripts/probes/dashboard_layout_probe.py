#!/usr/bin/env python3
"""Does the dashboard's layout host keep its promises? (TODO72 P0)

The layout is the thing the plan rewrites, so the probe measures what the
layout does rather than what the picture looks like: the stage's rectangle,
how many cells arrived, whether opening and closing a panel leaves the page
quiet, whether a resize reaches the canvas, and whether a reload comes back
without a new page error.

The probe also counts the listeners attached to ``window`` and ``document``
through CDP before and after a panel cycle. That is the leak signal for the
per-instance model: the P1 gate asks for fifty create/destroy cycles that
return to the baseline.

Usage:
    uv run python scripts/probes/dashboard_layout_probe.py --store experiment.duckdb

Measured baseline (2026-10-25, ``experiment.duckdb``, 1920x1080): canvas rect
0,0 1920x1080; no layout host and no command bus; 0 measured cells after the
first load and 4 of 512 known after reload; listener count 33 before the panel
cycle, 33 after it, and 33 after reload; panel open/close through the legacy
registry; 24.97 s walltime; no page or console errors.
"""

from __future__ import annotations

import argparse
import json
import logging
import threading
import time
from pathlib import Path

from dashboard_probe import CHROMIUM_ARGS, wait_for_http

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
for _name in ("computronium", "aiohttp.access", "aiohttp.server"):
    logging.getLogger(_name).setLevel(logging.WARNING)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _listener_count(cdp) -> int:
    """Count event listeners on ``window`` and ``document``."""
    result = cdp.send("Runtime.evaluate", {"expression": "window"})
    window_id = result["result"]["objectId"]
    total = 0
    for object_id in (window_id,):
        listeners = cdp.send(
            "DOMDebugger.getEventListeners",
            {"objectId": object_id, "depth": 0, "pierce": True},
        )
        total += len(listeners.get("listeners", []))
    document = cdp.send("Runtime.evaluate", {"expression": "document"})
    listeners = cdp.send(
        "DOMDebugger.getEventListeners",
        {"objectId": document["result"]["objectId"], "depth": 0, "pierce": True},
    )
    total += len(listeners.get("listeners", []))
    return total


def _dashboard_state(page) -> dict[str, object]:
    """Read the stable pieces of ``__DASHBOARD__`` that the probe needs."""
    return page.evaluate(
        """() => {
            const dbg = window.__DASHBOARD__;
            if (!dbg) return {ready: false};
            const canvas = document.getElementById('dashboard-canvas');
            const rect = canvas ? canvas.getBoundingClientRect() : null;
            const cells = dbg.discoveryMap?.cellDataMap;
            const measured = cells
                ? [...cells.values()].filter(c => c.status === 'measured').length
                : 0;
            return {
                ready: true,
                hasLayoutHost: Boolean(dbg.layout?.open || dbg.layoutHost),
                hasCommands: Boolean(dbg.commands),
                canvas: rect && {
                    x: rect.x, y: rect.y,
                    width: rect.width, height: rect.height,
                },
                measuredCells: measured,
                knownCells: cells ? cells.size : 0,
                wsState: dbg.wsClient?.state ?? null,
                hiddenPanels: dbg.panels
                    ? dbg.panels.list()
                        .filter(p => !p.isOpen())
                        .map(p => p.id)
                    : [],
            };
        }"""
    )


def _panel_cycle(page) -> dict[str, object]:
    """Open and close a panel through whatever surface exists.

    Until P2 lands the only surface is the panel registry, which toggles the
    single legacy element. The P2 host exposes ``open``/``duplicate``/``close``
    and the probe uses it automatically.
    """
    return page.evaluate(
        """() => {
            const dbg = window.__DASHBOARD__;
            const host = dbg.layoutHost || dbg.layout;
            if (host && typeof host.open === 'function') {
                const id = host.open('hud');
                const duplicate = typeof host.duplicate === 'function'
                    ? host.duplicate(id) : null;
                const list = typeof host.list === 'function' ? host.list() : [];
                if (typeof host.close === 'function') {
                    if (duplicate) host.close(duplicate);
                    host.close(id);
                }
                return {mode: 'layout-host', opened: id, duplicate, list: list.length};
            }
            const panel = dbg.panels?.get('hud');
            if (!panel) return {mode: 'none'};
            const before = panel.isOpen();
            dbg.panels.toggle('hud');
            const opened = panel.isOpen();
            dbg.panels.toggle('hud');
            const closed = panel.isOpen();
            return {
                mode: 'panel-registry',
                duplicate: null,
                opened: opened !== before,
                closed: closed === before,
            };
        }"""
    )


def probe(port: int) -> dict[str, object]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=CHROMIUM_ARGS)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        console: list[dict[str, str]] = []
        errors: list[str] = []
        page.on(
            "console",
            lambda msg: console.append({"type": msg.type, "text": msg.text}),
        )
        page.on("pageerror", lambda error: errors.append(str(error)))

        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
        page.wait_for_function(
            "() => Boolean(window.__DASHBOARD__?.discoveryMap)",
            timeout=30000,
        )
        # Measured cells are the data signal, but the probe still reports the
        # layout when the page has none: a blank grid is a finding, not a
        # reason to hang.
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if _dashboard_state(page).get("measuredCells"):
                break
            page.wait_for_timeout(500)
        page.wait_for_timeout(1000)

        cdp = page.context.new_cdp_session(page)
        listeners_before = _listener_count(cdp)
        initial = _dashboard_state(page)
        cycle = _panel_cycle(page)
        page.wait_for_timeout(500)
        listeners_after = _listener_count(cdp)
        after_cycle = _dashboard_state(page)

        page.set_viewport_size({"width": 1024, "height": 768})
        page.wait_for_timeout(800)
        resized = _dashboard_state(page)

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.reload(wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
        page.wait_for_timeout(1500)
        reloaded = _dashboard_state(page)
        reload_errors = list(errors)
        listeners_reload = _listener_count(cdp)

        browser.close()
        return {
            "initial": initial,
            "cycle": cycle,
            "listeners": {
                "before": listeners_before,
                "after_cycle": listeners_after,
                "after_reload": listeners_reload,
            },
            "resized": resized,
            "reloaded": reloaded,
            "page_errors": reload_errors,
            "console_errors": [m for m in console if m["type"] == "error"],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8142)
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

    started = time.monotonic()
    result = probe(args.port)
    result["walltime_s"] = round(time.monotonic() - started, 2)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
