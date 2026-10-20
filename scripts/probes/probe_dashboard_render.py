#!/usr/bin/env python3
"""Probe: verify the dashboard page boots three.js and renders in headless Chromium.

Measures WebGL availability, console errors, and whether the canvas is
non-blank. Run with the dashboard already serving on --port.

    uv run python scripts/probes/probe_dashboard_render.py --port 8099
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from pathlib import Path

from playwright.async_api import async_playwright


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()

    url = f"http://localhost:{args.port}/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--use-gl=angle",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--enable-webgl",
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})

        console: list[str] = []
        page.on("console", lambda m: console.append(f"{m.type}: {m.text}"))
        page.on("pageerror", lambda e: console.append(f"pageerror: {e}"))

        await page.goto(url, wait_until="load")
        await page.wait_for_timeout(4000)

        shot = Path(tempfile.gettempdir()) / "computronium-dashboard-probe.png"
        await page.screenshot(path=str(shot))

        report = await page.evaluate(
            """() => {
                const canvas = document.getElementById('dashboard-canvas');
                const gl = canvas && (canvas.getContext('webgl2') || canvas.getContext('webgl'));
                const dbg = window.__DASHBOARD__;
                return {
                    hasCanvas: !!canvas,
                    canvasSize: canvas ? [canvas.width, canvas.height] : null,
                    hasWebGL: !!gl,
                    renderer: gl ? gl.getParameter(gl.RENDERER) : null,
                    hasDashboard: !!dbg,
                    components: dbg ? Object.keys(dbg) : [],
                    bodyBg: getComputedStyle(document.body).backgroundColor,
                    overlayChildren: document.getElementById('ui-overlay')?.children.length ?? -1,
                };
            }"""
        )

        await browser.close()

    from PIL import Image

    image = Image.open(shot).convert("RGB")
    colors = image.getcolors(maxcolors=1_000_000) or []
    report["screenshot"] = str(shot)
    report["distinctColors"] = len(colors)
    report["topColors"] = sorted(colors, reverse=True)[:5]
    report["nonBackgroundPixels"] = sum(
        count for count, color in colors if color not in {(10, 14, 20), (0, 0, 0)}
    )

    print(json.dumps(report, indent=2))
    print("--- console ---")
    for line in console[:40]:
        print(line)

    ok = report["hasWebGL"] and report["distinctColors"] > 3
    print("RESULT:", "RENDER_OK" if ok else "RENDER_FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
