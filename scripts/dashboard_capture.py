"""The machinery the dashboard capture scripts share (TODO69).

The hero shot, the tour and the recording all need the same thing: a
dashboard serving a store, a campaign writing into that store, and a browser
pointed at the result. That machinery lives here, once, so each script holds
only what makes it different — the shots it takes, or the film it records.

The dashboard, the campaign and the capture run in ONE process on purpose: the
campaign holds the store, and the capture wants the records the campaign has
just written. (A dashboard in another process would see them too, through the
mirror the writer publishes — but one process has no such gap to fall
through.)
"""

from __future__ import annotations

import html
import json
import logging
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Page, Playwright, ViewportSize

REPO_ROOT = Path(__file__).resolve().parents[1]

# Every shot is taken at this size: the pictures in the docs are one size, and
# a dashboard that is legible in a screenshot is legible in a browser.
VIEWPORT: ViewportSize = {"width": 1920, "height": 1080}

# Chromium with the software rasterizer: the capture has to work on a machine
# with no GPU, and it has to produce the same picture every time.
CHROMIUM_ARGS = (
    "--use-gl=angle",
    "--use-angle=swiftshader",
    "--enable-unsafe-swiftshader",
    "--enable-webgl",
    "--ignore-gpu-blocklist",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--force-device-scale-factor=1",
)

logger = logging.getLogger("dashboard_capture")

# A run in one of these states is still going.
_RUNNING = frozenset({"running", "pending", "queued"})


def wait_for_http(port: int, timeout: float = 60.0) -> bool:
    """Wait for the dashboard HTTP server to answer."""
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


def wait_for_records(port: int, min_records: int, timeout: float = 180.0) -> str:
    """Wait for a run to land records; return its run id.

    The dashboard is asked, not the store: DuckDB gives one writer the file,
    and a second connection to it fails while the campaign is writing. The
    newest run with enough records is the one the dashboard is about, so that
    is the one that comes back.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{port}/api/runs", timeout=5
            ) as response:
                payload = json.loads(response.read())
            measured = [
                str(run["run_id"])
                for run in payload.get("runs", [])
                if run.get("records", 0) >= min_records
            ]
            if measured:
                logger.info("Run %s has %d records", measured[-1], min_records)
                return measured[-1]
        except (urllib.error.URLError, OSError, ValueError) as exc:
            logger.debug("Runs not readable yet: %s", exc)
        time.sleep(1.0)
    msg = f"no run reached {min_records} records in {timeout}s"
    raise TimeoutError(msg)


def _run_status(port: int, run_id: str) -> str:
    """The run's status, as the dashboard sees it."""
    with urllib.request.urlopen(
        f"http://localhost:{port}/api/runs", timeout=5
    ) as response:
        payload = json.loads(response.read())
    for run in payload.get("runs", []):
        if run.get("run_id") == run_id:
            return str(run.get("status") or "")
    return ""


def latest_run(port: int) -> str:
    """The run the dashboard is about: the newest one with records."""
    with urllib.request.urlopen(
        f"http://localhost:{port}/api/runs", timeout=5
    ) as response:
        payload = json.loads(response.read())
    measured = [
        str(run["run_id"])
        for run in payload.get("runs", [])
        if run.get("records", 0) > 0
    ]
    return measured[-1] if measured else ""


def wait_for_run_to_finish(
    port: int,
    run_id: str,
    timeout: float = 900.0,
) -> str:
    """Wait for the run to stop running; return its final status."""
    deadline = time.time() + timeout
    status = ""
    while time.time() < deadline:
        try:
            status = _run_status(port, run_id)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            logger.debug("Runs not readable yet: %s", exc)
        if status and status.lower() not in _RUNNING:
            return status
        time.sleep(1.0)
    return status or "unknown"


def start_dashboard(
    port: int,
    store_path: Path,
) -> tuple[Any, threading.Thread, list[BaseException]]:
    """Start the dashboard on a thread; return it, the thread and its errors."""
    from computronium.experiment.execution.dashboard.web import (
        DashboardConfig,
        WebDashboard,
    )

    dashboard = WebDashboard(
        DashboardConfig(
            host="127.0.0.1",
            port=port,
            store_path=str(store_path),
        )
    )
    errors: list[BaseException] = []

    def serve() -> None:
        import asyncio

        try:
            asyncio.run(dashboard.run())
        except BaseException as exc:  # ruff: ignore[blind-except] - reported to the main thread
            errors.append(exc)

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    return dashboard, thread, errors


def clear_store(store_path: Path) -> None:
    """Remove the store and the mirror the writer publishes.

    The mirror is a copy of the store, and it outlives the store it was
    published from: a capture that leaves the old mirror behind reads the
    last run's records as if they were this run's.
    """
    from computronium.experiment.evidence.mirror import mirror_path

    for path in (store_path, mirror_path(store_path)):
        if path.exists():
            path.unlink()
            logger.info("Removed %s", path)


def run_demo_campaign(store_path: Path) -> int:
    """Run the demo campaign in this process; return its exit code."""
    from computronium.experiment.surface.cli import (
        RUN_PROFILES,
        execute_spec,
        spec_from_profile,
    )

    spec = spec_from_profile(RUN_PROFILES["demo"])
    return execute_spec(spec, store_path=str(store_path))


def launch_browser(playwright: Playwright) -> Browser:
    """A browser that renders the dashboard the same way on any machine."""
    return playwright.chromium.launch(headless=True, args=list(CHROMIUM_ARGS))


def open_dashboard(browser: Browser, port: int) -> Page:
    """Open the dashboard and wait for its scene."""
    page = browser.new_page(viewport=VIEWPORT)
    page.on("console", lambda m: logger.debug("console %s: %s", m.type, m.text))
    page.on("pageerror", lambda e: logger.warning("pageerror: %s", e))
    page.goto(f"http://localhost:{port}/", wait_until="load")
    page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
    return page


def mirror_shot(source: Path, mirror: Path) -> None:
    """Copy a shot to the second place the docs keep it."""
    if source.resolve() == mirror.resolve():
        return
    mirror.parent.mkdir(parents=True, exist_ok=True)
    mirror.write_bytes(source.read_bytes())
    logger.info("Mirrored to %s", mirror)


# A terminal window, as a page the browser can photograph. The tour needs
# pictures of things that are not the dashboard, and the console dashboard is
# one of them.
TERMINAL_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * { box-sizing: border-box; }
  body { margin: 0; background: #05080c; }
  .bar { display: flex; align-items: center; gap: 10px; padding: 12px 18px;
         background: #161d28; color: #8b98a8;
         font: 14px 'DejaVu Sans Mono', 'Noto Sans Mono', monospace; }
  .dot { width: 12px; height: 12px; border-radius: 50%; }
  pre { margin: 0; padding: 18px 22px; color: #e8ecf0;
        font: 14px/1.32 'DejaVu Sans Mono', 'Noto Sans Mono', monospace;
        white-space: pre; }
</style></head><body>
  <div class="bar"><span class="dot" style="background:#f85149"></span>\
<span class="dot" style="background:#d29922"></span>\
<span class="dot" style="background:#3fb950"></span>\
<span style="margin-left:10px">$title</span></div>
  <pre>$body</pre>
</body></html>"""


def terminal_page(title: str, body: str) -> str:
    """A terminal window showing text, as a page the browser can shoot."""
    return Template(TERMINAL_HTML).substitute(
        title=html.escape(title),
        body=html.escape(body),
    )


def shoot_terminal(page: Page, title: str, body: str, path: Path) -> None:
    """Show text in a terminal window and take the picture."""
    page.set_content(terminal_page(title, body), wait_until="load")
    page.wait_for_timeout(300)
    page.screenshot(path=str(path))


__all__ = [
    "CHROMIUM_ARGS",
    "REPO_ROOT",
    "VIEWPORT",
    "clear_store",
    "latest_run",
    "launch_browser",
    "mirror_shot",
    "open_dashboard",
    "run_demo_campaign",
    "shoot_terminal",
    "start_dashboard",
    "terminal_page",
    "wait_for_http",
    "wait_for_records",
    "wait_for_run_to_finish",
]
