#!/usr/bin/env python3
"""Does the quest get answered? (TODO68)

Adopting a cell as a quest used to write a file and stop there: the question
was on disk, and nothing was going to measure the cell. This probe opens the
dashboard on a store with one measured cell, adopts a gap as a quest, and
reads what the page, the registry and the queue say happened — the
registration, the campaign, and the run that campaign would write into.

Usage:
    uv run python scripts/probes/probe_dashboard_quest.py
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


def _gap_on_screen(page) -> dict | None:
    """The legal cell nearest the camera that no panel covers."""
    return page.evaluate(
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


def probe(port: int, registry: Path, queue) -> dict[str, object]:
    """Adopt a gap as a quest, and read what happened."""
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
                let legal = 0;
                let measured = 0;
                for (const cell of dbg.discoveryMap.cellDataMap.values()) {
                    if (cell.status === 'legal') legal += 1;
                    if (cell.status === 'measured') measured += 1;
                }
                return legal > 0 && measured > 0;
            }""",
            timeout=60000,
        )
        page.wait_for_timeout(1500)

        runs_before = page.evaluate(
            """() => {
                const select = document.getElementById('legend-run-picker');
                return {
                    options: select ? select.options.length : 0,
                    selected: select ? select.value : '',
                    detail: document.getElementById('legend-run')?.innerText ?? '',
                };
            }"""
        )

        target = _gap_on_screen(page)
        if not target:
            browser.close()
            return {"error": "no legal cell on the page", "runs": runs_before}

        page.mouse.move(target["x"], target["y"])
        page.wait_for_timeout(400)
        page.mouse.click(target["x"], target["y"])
        page.wait_for_timeout(900)

        page.click('.drawer-btn[data-action="quest"]')
        # The verb writes a file and queues a campaign; the page says when it
        # is done, and "Working…" is not an answer.
        page.wait_for_function(
            """() => {
                const text = document.getElementById('drawer-status')?.textContent ?? '';
                return text.trim().length > 0 && !text.includes('Working');
            }""",
            timeout=60000,
        )

        status = page.evaluate(
            "() => document.getElementById('drawer-status')?.textContent?.trim() ?? ''"
        )

        written = (
            sorted(p.name for p in registry.glob("*.json")) if registry.exists() else []
        )
        registration = {}
        if written:
            registration = json.loads(
                (registry / written[0]).read_text(encoding="utf-8")
            )

        queued = [
            {
                "name": entry.spec.name,
                "run_id": entry.spec.runs[0].run_id,
                "spec_file": entry.spec.runs[0].spec_file,
                "status": entry.status.value,
            }
            for entry in queue._queue
        ]

        shot = SHOT_DIR / "dashboard-quest.png"
        page.screenshot(path=str(shot))

        browser.close()
        return {
            "runs": runs_before,
            "target": target,
            "status": status,
            "registered": written,
            "registration": registration,
            "queued": queued,
            "page_errors": errors,
            "shot": str(shot),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8143)
    args = parser.parse_args()

    from computronium.experiment.execution.campaign_queue import CampaignQueue

    work = Path(tempfile.mkdtemp(prefix="computronium-quest-"))
    store_path = work / "probe.duckdb"
    registry = work / "preregistrations"
    run_id = build_store(store_path)
    logger.info("store %s holds run %s", store_path, run_id)

    # A queue that never starts a campaign: the probe reads what was queued.
    queue = CampaignQueue(max_concurrent=0)

    with serving_dashboard(
        store_path,
        args.port,
        registration_dir=registry,
        queue=queue,
    ):
        result = probe(args.port, registry, queue)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
