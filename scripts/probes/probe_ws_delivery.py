#!/usr/bin/env python3
"""Probe the browser's WebSocket delivery against the dashboard (TODO68).

Regime measured (2026-10-20): headless Chromium with the SwiftShader
rasterizer, a dashboard serving a store with 20 demo records on port 8104.

    uv run python scripts/probes/probe_ws_delivery.py

Answers one question: how long does the browser take to hand the frames the
server sends to the page? Software rendering used to starve the event loop
and the answer was "never" — the fix was a render profile that caps the
frame rate and drops shadows when no GPU is present.
"""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PORT = 8104
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
        page.wait_for_timeout(2000)
        page.evaluate(
            """() => {
                const router = window.__DASHBOARD__.router;
                window.__PROBE__ = {count: 0, types: {}};
                const original = router.dispatch.bind(router);
                router.dispatch = async (message) => {
                    window.__PROBE__.count++;
                    window.__PROBE__.types[message.type] =
                        (window.__PROBE__.types[message.type] || 0) + 1;
                    return original(message);
                };
            }"""
        )
        for wait_ms in (5000, 10000, 20000):
            page.wait_for_timeout(wait_ms)
            print(
                f"after {wait_ms}ms:",
                page.evaluate("() => window.__PROBE__"),
                flush=True,
            )

        print(
            "app socket:",
            page.evaluate(
                """() => {
                    const client = window.__DASHBOARD__.wsClient;
                    return {
                        state: client.connectionState,
                        readyState: client.ws && client.ws.readyState,
                    };
                }"""
            ),
        )
        browser.close()
    print(json.dumps({"done": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
