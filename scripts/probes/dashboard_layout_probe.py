#!/usr/bin/env python3
"""Does the dashboard's layout host keep its promises? (TODO73 P10)

The layout is the thing the plan rewrites, so the probe measures what the
layout does rather than what the picture looks like: the stage's rectangle,
how many cells arrived, whether opening and closing a panel leaves the page
quiet, whether a resize reaches the canvas, and whether a reload comes back
without a new page error.

The probe also counts the listeners attached to ``window`` and ``document``
through CDP before and after a panel cycle. That is the leak signal for the
per-instance model: the gate asks for fifty create/destroy cycles that
return to the baseline.

Usage:
    uv run python scripts/probes/dashboard_layout_probe.py --store experiment.duckdb
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
            const debug = dbg.debug;
            let measured = 0;
            let stagePanelCount = 0;
            if (debug && typeof debug.measuredCells === 'function') {
                measured = debug.measuredCells();
                const instances = debug.instances ? debug.instances() : [];
                stagePanelCount = instances.filter(i => i.type === 'stage').length;
            }
            // Get workspace rect
            const workspace = document.getElementById('workspace');
            const wsRect = workspace ? workspace.getBoundingClientRect() : null;
            return {
                ready: true,
                hasLayoutHost: Boolean(dbg.layoutHost),
                hasCommands: Boolean(dbg.commands),
                workspace: wsRect && {
                    x: wsRect.x, y: wsRect.y,
                    width: wsRect.width, height: wsRect.height,
                },
                measuredCells: measured,
                stagePanelCount: stagePanelCount,
                wsState: dbg.wsClient?.state ?? null,
            };
        }"""
    )


def _panel_cycle(page) -> dict[str, object]:
    """Open and close panels through the Dockview layoutHost."""
    return page.evaluate(
        """async () => {
            const dbg = window.__DASHBOARD__;
            const host = dbg.layoutHost;
            if (!host || typeof host.open !== 'function') {
                return {mode: 'none', error: 'no layoutHost.open'};
            }
            const runs = (dbg.runSelection?.runs ?? []).map(([id]) => id);
            const id1 = await host.open('hud', {runId: runs[0] ?? null});
            const duplicate = typeof host.duplicate === 'function'
                ? await host.duplicate(id1) : null;
            if (duplicate && typeof host.setState === 'function') {
                await host.setState(duplicate, {runId: runs[1] ?? null});
            }
            const list = typeof host.list === 'function' ? await host.list() : [];
            const views = document.querySelectorAll(
                '[data-component="hud"]'
            ).length;
            // Check for duplicate IDs in Dockview panels
            const allIds = [...document.querySelectorAll('[id]')].map(node => node.id);
            const duplicates = allIds.filter(
                (value, index) => allIds.indexOf(value) !== index
            );
            const types = (dbg.definitions?.list?.() ?? [])
                .map(definition => definition.type);
            const openedAll = [];
            for (const type of types) {
                try {
                    openedAll.push(await host.open(type));
                } catch (e) {
                    openedAll.push(null);
                }
            }
            if (typeof host.close === 'function') {
                for (const opened of openedAll) {
                    if (opened) await host.close(opened);
                }
                if (duplicate) await host.close(duplicate);
                await host.close(id1);
            }
            return {
                mode: 'layout-host',
                opened: id1,
                duplicate,
                list: list.length,
                views,
                states: list.map(meta => meta.state),
                definitionTypes: types,
                allViews: openedAll.filter(o => o).length,
                duplicateIds: duplicates,
            };
        }"""
    )


def _fifty_cycles(page) -> dict[str, object]:
    """Run 50 create/destroy cycles to check for listener leaks."""
    listener_counts = []
    cdp = page.context.new_cdp_session(page)

    for i in range(50):
        if i % 10 == 0:
            listener_counts.append(_listener_count(cdp))
        result = page.evaluate(
            """async (i) => {
                const dbg = window.__DASHBOARD__;
                const host = dbg.layoutHost;
                if (!host || typeof host.open !== 'function') return {error: 'no host'};
                const id = await host.open('hud');
                if (typeof host.close === 'function') {
                    await host.close(id);
                }
                return {ok: true, iteration: i};
            }""",
            i,
        )
        if result.get("error"):
            return {"error": result["error"], "listener_counts": listener_counts}

    listener_counts.append(_listener_count(cdp))
    return {"listener_counts": listener_counts}


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
        page.wait_for_selector("#workspace", state="attached", timeout=30000)
        page.wait_for_function(
            "() => Boolean(window.__DASHBOARD__?.layoutHost?.mountComplete)",
            timeout=30000,
        )
        mount_error = page.evaluate(
            "() => window.__DASHBOARD__?.layoutHost?.mountError?.message || null"
        )
        if mount_error:
            raise RuntimeError(f"DockviewHost mount failed: {mount_error}")

        # Wait for measured cells
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

        # Resize test
        page.set_viewport_size({"width": 1024, "height": 768})
        page.wait_for_timeout(800)
        resized = _dashboard_state(page)

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(800)
        restored = _dashboard_state(page)

        # Reload test
        page.reload(wait_until="load")
        page.wait_for_selector("#workspace", state="attached", timeout=30000)
        page.wait_for_function(
            "() => Boolean(window.__DASHBOARD__?.layoutHost?.mountComplete)",
            timeout=30000,
        )
        page.wait_for_timeout(1500)
        reloaded = _dashboard_state(page)
        reload_errors = list(errors)
        listeners_reload = _listener_count(cdp)

        # 50-cycle leak test
        logger.info("Running 50 create/destroy cycles...")
        leak_test = _fifty_cycles(page)

        browser.close()
        return {
            "initial": initial,
            "cycle": cycle,
            "listeners": {
                "before": listeners_before,
                "after_cycle": listeners_after,
                "after_reload": listeners_reload,
                "leak_test": leak_test,
            },
            "resized": resized,
            "restored": restored,
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
