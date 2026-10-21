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

import base64
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

# The credit rules the second campaign measures: the demo campaign measures
# four others, so the two runs' cells do not overlap.
SECOND_CREDIT = ("homeostatic", "temporal_trace")


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
    """The run the dashboard is about: the newest one with records.

    A dashboard that is busy reading the store may not answer in time; a
    reader that is watching for a run to appear must not die when it does.
    """
    try:
        with urllib.request.urlopen(
            f"http://localhost:{port}/api/runs", timeout=20
        ) as response:
            payload = json.loads(response.read())
    except (urllib.error.URLError, OSError, ValueError) as exc:
        logger.debug("Runs not readable yet: %s", exc)
        return ""
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


def run_second_campaign(store_path: Path) -> int:
    """Run a second campaign in this process; return its exit code.

    The multi-run space needs two runs in one store, and the second one has
    to reach cells the first did not: the picture claims that the runs went
    different places, and two runs over the same cells would not say that.
    So the second campaign measures two credit rules the demo does not, with
    the same five axes fixed, and the two runs' cells sit apart in the same
    space.
    """
    import dataclasses

    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.surface.cli import (
        RUN_PROFILES,
        execute_spec,
        spec_from_profile,
    )

    profile = RUN_PROFILES["demo"]
    axes = tuple(
        selection.model_copy(update={"primitives": SECOND_CREDIT})
        if selection.axis is StructuralAxis.CREDIT
        else selection
        for selection in profile.axes
    )
    spec = spec_from_profile(
        dataclasses.replace(profile, name="demo-second", axes=axes)
    )
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
  body { margin: 0; background: #05080c; height: 100vh; display: flex;
         flex-direction: column; }
  .bar { display: flex; align-items: center; gap: 10px; padding: 12px 18px;
         background: #161d28; color: #8b98a8;
         font: 14px 'DejaVu Sans Mono', 'Noto Sans Mono', monospace; }
  .dot { width: 12px; height: 12px; border-radius: 50%; }
  pre { margin: 0; padding: 18px 22px; color: #e8ecf0; flex: 1;
        display: flex; align-items: center;
        font-size: $size px; line-height: 1.34;
        font-family: 'DejaVu Sans Mono', 'Noto Sans Mono', monospace;
        white-space: pre; }
</style></head><body>
  <div class="bar"><span class="dot" style="background:#f85149"></span>\
<span class="dot" style="background:#d29922"></span>\
<span class="dot" style="background:#3fb950"></span>\
<span style="margin-left:10px">$title</span></div>
  <pre>$body</pre>
</body></html>"""

# The terminal's own furniture: the title bar and the padding around the text.
TERMINAL_CHROME = 110

# A monospace advance is a little over half the font's size.
TERMINAL_ADVANCE = 0.62

# The largest a terminal's own text is drawn: a short answer is still an
# answer, and it is read at a distance.
TERMINAL_MAX_SIZE = 22


def terminal_font_size(body: str, width: int = 1920, height: int = 1080) -> int:
    """The font size that lets the whole text fit the window.

    A terminal frame that cuts its text off is a picture of half an answer:
    the reader cannot tell what the command said after the cut.
    """
    lines = body.splitlines() or [""]
    longest = max(len(line) for line in lines)
    by_height = int((height - TERMINAL_CHROME) / (1.34 * len(lines)))
    by_width = int((width - 50) / (TERMINAL_ADVANCE * max(longest, 1)))
    return max(8, min(TERMINAL_MAX_SIZE, by_height, by_width))


def terminal_page(title: str, body: str, size: int = 14) -> str:
    """A terminal window showing text, as a page the browser can shoot."""
    return Template(TERMINAL_HTML).substitute(
        title=html.escape(title),
        body=html.escape(body),
        size=size,
    )


def shoot_terminal(page: Page, title: str, body: str, path: Path) -> None:
    """Show text in a terminal window and take the picture."""
    size = terminal_font_size(body)
    page.set_content(terminal_page(title, body, size), wait_until="load")
    page.wait_for_timeout(300)
    page.screenshot(path=str(path))


# A figure with its caption and its provenance, as a page the browser can
# photograph. The system has pictures that are not the dashboard: the
# gallery's figures, the report's plots, the analyses' outputs. They are
# pictures of the same evidence, and they are worth the docs as much as the
# dashboard is.
FIGURE_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * { box-sizing: border-box; }
  body { margin: 0; height: 100vh; background: #0a0e14; color: #e8ecf0;
         font: 16px 'DejaVu Sans Mono', 'Noto Sans Mono', monospace;
         display: flex; align-items: center; justify-content: center; }
  figure { margin: 0; display: flex; flex-direction: column; align-items: center;
           gap: 16px; max-width: 1500px; }
  img { max-width: 1400px; max-height: 830px; }
  figcaption { color: #8b98a8; font-size: 16px; text-align: center; }
  .provenance { color: #5a6a7a; font-size: 12px; text-align: center; }
</style></head><body>
  <figure>
    <img src="$image">
    <figcaption>$caption</figcaption>
    <div class="provenance">$provenance</div>
  </figure>
</body></html>"""


def figure_page(image: str, caption: str, provenance: str) -> str:
    """A figure with its caption and its provenance, as a page."""
    return Template(FIGURE_HTML).substitute(
        image=image,
        caption=html.escape(caption),
        provenance=html.escape(provenance),
    )


def shoot_figure(
    page: Page,
    image_path: Path,
    caption: str,
    provenance: str,
    path: Path,
) -> None:
    """Show a figure with its caption and provenance, and take the picture."""
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    page.set_content(
        figure_page(f"data:image/png;base64,{encoded}", caption, provenance),
        wait_until="load",
    )
    page.wait_for_timeout(400)
    page.screenshot(path=str(path))


# A plot the report drew, on a page of its own. The report's charts are
# interactive HTML, not pictures, so the frame is the chart's own markup:
# a page that holds one chart, with its caption and its provenance under it.
PLOT_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * { box-sizing: border-box; }
  body { margin: 0; height: 100vh; background: #0a0e14; color: #e8ecf0;
         font: 16px 'DejaVu Sans Mono', 'Noto Sans Mono', monospace;
         display: flex; align-items: center; justify-content: center; }
  figure { margin: 0; display: flex; flex-direction: column; align-items: center;
           gap: 14px; max-width: 1600px; }
  .chart { background: #ffffff; border-radius: 6px; padding: 8px;
           box-shadow: 0 8px 32px rgba(0, 0, 0, 0.55); width: 1500px; }
  figcaption { color: #8b98a8; font-size: 16px; text-align: center; }
  .provenance { color: #5a6a7a; font-size: 12px; text-align: center; }
</style></head><body>
  <figure>
    <div class="chart">$plot</div>
    <figcaption>$caption</figcaption>
    <div class="provenance">$provenance</div>
  </figure>
</body></html>"""


def plot_page(plot: str, caption: str, provenance: str) -> str:
    """A page holding one chart, with its caption and its provenance."""
    return Template(PLOT_HTML).substitute(
        plot=plot,
        caption=html.escape(caption),
        provenance=html.escape(provenance),
    )


def shoot_plot(
    page: Page,
    source: str,
    selector: str,
    caption: str,
    provenance: str,
    path: Path,
) -> None:
    """Photograph one chart of a page, on a page of its own.

    The chart is taken out of its page and given a window of its own: a
    report's plot is a picture of one thing, and a picture of one thing
    deserves the whole frame.
    """
    page.goto(source, wait_until="load")
    page.wait_for_timeout(2000)
    markup = page.evaluate(
        """(selector) => {
            const element = document.querySelector(selector);
            if (!element) return null;
            return element.parentElement.outerHTML;
        }""",
        selector,
    )
    if not markup:
        msg = f"no chart matched {selector}"
        raise ValueError(msg)
    page.set_content(plot_page(markup, caption, provenance), wait_until="load")
    page.wait_for_timeout(2500)
    page.screenshot(path=str(path))


__all__ = [
    "CHROMIUM_ARGS",
    "REPO_ROOT",
    "SECOND_CREDIT",
    "VIEWPORT",
    "clear_store",
    "figure_page",
    "latest_run",
    "launch_browser",
    "mirror_shot",
    "open_dashboard",
    "plot_page",
    "run_demo_campaign",
    "run_second_campaign",
    "shoot_figure",
    "shoot_plot",
    "shoot_terminal",
    "start_dashboard",
    "terminal_font_size",
    "terminal_page",
    "wait_for_http",
    "wait_for_records",
    "wait_for_run_to_finish",
]
