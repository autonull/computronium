#!/usr/bin/env python3
"""Do the drawer's actions actually do something? (TODO68)

The drawer used to carry three disabled buttons. A disabled button cannot be
wrong, but it also cannot be right, so this probe opens the dashboard on a
store with a measured cell, clicks the pillar, and presses the buttons the way
a person would — then reads what the DOM and the filesystem say happened.

Usage:
    uv run python scripts/probes/probe_dashboard_actions.py
"""

from __future__ import annotations

import argparse
import json
import logging
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
SHOT_DIR = Path(tempfile.gettempdir()) / "computronium"

COORDINATE = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}


def wait_for_http(port: int, timeout: float = 60.0) -> bool:
    """Wait for the dashboard HTTP server to answer."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/status", timeout=2
            ) as r:
                if r.status == 200:
                    return True
        except urllib.error.URLError, OSError:
            pass
        time.sleep(0.5)
    return False


def build_store(path: Path) -> str:
    """A store holding one run with five measured seeds of one cell."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.schema.coordinate import (
        Coordinate,
        Provenance,
        Schedule,
    )
    from computronium.experiment.schema.record import (
        FailureCause,
        GateVerdict,
        Maturity,
        Record,
        ReproducibilityClass,
        Severity,
        Status,
    )
    from computronium.experiment.schema.run_spec import RunSpec
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    spec = RunSpec(
        profile="demo",
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L1",
        n_seeds=5,
        epochs=1,
        budget_seconds=120.0,
    )

    with RecordStore(StoreConfig(path=path)) as store:
        run_id = store.create_run(spec=spec)
        for seed in range(5):
            store.append(
                Record.create(
                    run_id=run_id,
                    coordinate=Coordinate(**COORDINATE, params={}),
                    schedule=Schedule(
                        fidelity="L1",
                        seed=seed,
                        n_seeds=1,
                        epochs=1,
                        batch_limit=0,
                        budget_id="probe",
                        task_id="digits",
                        param_budget=0,
                    ),
                    provenance=Provenance(
                        env={"python": "3.14", "platform": "linux"},
                        dataset="digits",
                        dataset_version="1.0",
                        code_sha="probe",
                        policy="probe",
                        links={"run_id": run_id},
                    ),
                    status=Status(
                        gate_verdict=GateVerdict.PASS_,
                        defect="",
                        cause=FailureCause.UNKNOWN,
                        severity=Severity.LOW,
                        quarantine=False,
                        maturity=Maturity.L1,
                        uncertainty={},
                        reproducibility=ReproducibilityClass.REPLAYABLE,
                        assessment_procedure_version="1.0",
                        ceec_link=None,
                    ),
                    payload={
                        "val_acc": 0.40 + 0.02 * seed,
                        "walltime_s": 3.0,
                        "param_count": 1024,
                    },
                )
            )
    return run_id


def probe(port: int, registry: Path) -> dict[str, object]:
    """Open the drawer, press a button, and report what happened."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--use-gl=angle",
                "--use-angle=swiftshader",
                "--enable-unsafe-swiftshader",
                "--enable-webgl",
                "--ignore-gpu-blocklist",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--force-device-scale-factor=1",
            ],
        )
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
        page.wait_for_function(
            """() => {
                const dbg = window.__DASHBOARD__;
                if (!dbg || !dbg.discoveryMap) return false;
                for (const cell of dbg.discoveryMap.cellDataMap.values()) {
                    if (cell.status === 'measured' && cell.metrics?.n_seeds) return true;
                }
                return false;
            }""",
            timeout=60000,
        )
        page.wait_for_timeout(1500)

        target = page.evaluate(
            """() => {
                const dbg = window.__DASHBOARD__;
                for (const [key, cell] of dbg.discoveryMap.cellDataMap.entries()) {
                    if (cell.status !== 'measured') continue;
                    const mesh = dbg.discoveryMap.cells.get(key);
                    if (!mesh) continue;
                    mesh.geometry.computeBoundingBox();
                    const box = mesh.geometry.boundingBox;
                    const point = mesh.position.clone();
                    point.y += (box.min.y + box.max.y) / 2;
                    point.project(dbg.camera);
                    return {
                        key,
                        x: (point.x * 0.5 + 0.5) * window.innerWidth,
                        y: (-point.y * 0.5 + 0.5) * window.innerHeight,
                    };
                }
                return null;
            }"""
        )
        if not target:
            browser.close()
            return {"error": "no measured pillar on the page"}

        page.mouse.move(target["x"], target["y"])
        page.wait_for_timeout(300)
        page.mouse.click(target["x"], target["y"])
        page.wait_for_timeout(900)

        drawer = page.evaluate(
            """() => {
                const panel = document.getElementById('cell-drawer');
                return {
                    transform: getComputedStyle(panel).transform,
                    text: panel.innerText.replace(/\\s+/g, ' ').slice(0, 160),
                };
            }"""
        )

        buttons = page.evaluate(
            """() => {
                const panel = document.getElementById('cell-drawer');
                return [...panel.querySelectorAll('.drawer-btn[data-action]')].map(
                    (b) => ({
                        action: b.dataset.action,
                        label: b.textContent.trim(),
                        disabled: b.disabled,
                    })
                );
            }"""
        )

        # The confirmation: register the effect the cell showed.
        if buttons:
            page.click('.drawer-btn[data-action="preregister"]')
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

        shot = SHOT_DIR / "dashboard-actions.png"
        page.screenshot(path=str(shot))

        browser.close()
        return {
            "target": target,
            "drawer": drawer,
            "buttons": buttons,
            "status": status,
            "registered": written,
            "registration": payload,
            "page_errors": errors,
            "shot": str(shot),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8141)
    args = parser.parse_args()

    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )

    work = Path(tempfile.mkdtemp(prefix="computronium-actions-"))
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
