#!/usr/bin/env python3
"""Record the dashboard, live (TODO69 Phase 3).

A short film of a real session: the campaign runs, the live rail carries the
events as they happen, the caption narrates them, and the map lights up with
the evidence when the run lands its records.

The film is a ``.webm`` and it is **not committed** — it is large, and it is
a picture of one run rather than a claim about the system. It is written to
``docs/recordings/``, which ``*.webm`` ignores, so ``git status`` stays
clean.

The frames come from the browser's own screencast (CDP) and are encoded by
``ffmpeg``. Playwright's own recorder is not used: it needs a particular
``ffmpeg`` build, and a machine without that build would silently record
nothing.

Usage:
    uv run python scripts/capture_dashboard_video.py
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import] - ffmpeg is called with a fixed command
import threading
import time
from pathlib import Path

from dashboard_capture import (
    REPO_ROOT,
    clear_store,
    latest_run,
    launch_browser,
    run_demo_campaign,
    start_dashboard,
    wait_for_http,
    wait_for_run_to_finish,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Where the film goes: inside the repository, where it can be found, and
# ignored by `*.webm`, so `git status` stays clean.
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "recordings" / "dashboard-session.webm"

# The gap between two photographs of the session.
FRAME_INTERVAL = 0.25


def capture_frames(
    page,
    port: int,
    max_seconds: float,
    hold_seconds: float,
    interval: float = FRAME_INTERVAL,
) -> tuple[list[bytes], float]:
    """Photograph the page until the run has landed its evidence.

    The browser's own screencast is not used: in headless Chromium it only
    fires when the compositor is woken, which a WebGL scene does not do
    often enough to make a film. Photographs are slower and honest.

    The film ends when the run's evidence has landed and the picture has
    settled — not when a timer says so, because the machine's speed is not
    the session's length.

    Returns the frames and how long they took, so the film can be played at
    the speed the session happened.
    """
    frames: list[bytes] = []
    started = time.time()
    deadline = started + max_seconds
    landed_at: float | None = None
    while time.time() < deadline:
        frames.append(page.screenshot())
        if landed_at is None:
            if latest_run(port):
                landed_at = time.time()
        elif time.time() - landed_at >= hold_seconds:
            break
        time.sleep(interval)
    return frames, time.time() - started


def encode(frames: list[bytes], output: Path, elapsed: float) -> Path:
    """Write the frames out as a webm."""
    if not frames:
        msg = "the browser sent no frames"
        raise RuntimeError(msg)
    if shutil.which("ffmpeg") is None:
        msg = "ffmpeg is not on the path: the film cannot be written"
        raise RuntimeError(msg)

    output.parent.mkdir(parents=True, exist_ok=True)
    fps = len(frames) / max(elapsed, 1.0)
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "image2pipe",
        "-framerate",
        f"{fps:.3f}",
        "-i",
        "-",
        "-c:v",
        "libvpx-vp9",
        "-b:v",
        "2500k",
        "-deadline",
        "realtime",
        "-cpu-used",
        "8",
        "-pix_fmt",
        "yuv420p",
        str(output),
    ]
    logger.info("Encoding %d frames at %.2f fps", len(frames), fps)
    process = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - the command is fixed
        command,
        input=b"".join(frames),
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        msg = f"ffmpeg failed: {process.stderr.decode(errors='replace')[:500]}"
        raise RuntimeError(msg)
    return output


def record(
    port: int,
    output: Path,
    max_seconds: float,
    hold_seconds: float,
    ready: threading.Event,
) -> Path:
    """Film the dashboard; return the film's path.

    The event is set once the page is on screen, so the campaign starts
    against a dashboard that is already watching.
    """
    from playwright.sync_api import sync_playwright

    frames: list[bytes] = []
    elapsed = 0.0
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        page.on("pageerror", lambda error: logger.warning("pageerror: %s", error))
        page.goto(f"http://localhost:{port}/", wait_until="load")
        page.wait_for_selector("#dashboard-canvas", state="visible", timeout=30000)
        ready.set()
        logger.info("Filming the dashboard")
        frames, elapsed = capture_frames(page, port, max_seconds, hold_seconds)
        context.close()
        browser.close()

    logger.info("The camera took %d frames in %.1f seconds", len(frames), elapsed)
    return encode(frames, output, elapsed)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8082)
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "experiment-video.duckdb",
        help="Store the campaign writes and the dashboard reads.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Where the film is written. It is not committed.",
    )
    parser.add_argument(
        "--max-seconds",
        type=float,
        default=300.0,
        help="How long the film may run. It ends when the run's evidence lands.",
    )
    parser.add_argument(
        "--hold-seconds",
        type=float,
        default=15.0,
        help="How long the film stays on the finished run before it ends.",
    )
    args = parser.parse_args()

    store_path = args.store
    clear_store(store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)

    _dashboard, _thread, server_error = start_dashboard(args.port, store_path)
    if not wait_for_http(args.port):
        logger.error("Dashboard server did not start")
        return 1
    logger.info("Dashboard serving on port %d", args.port)

    filming = threading.Event()
    film: list[Path] = []
    film_error: list[BaseException] = []

    def run_film() -> None:
        try:
            film.append(
                record(
                    args.port,
                    args.output,
                    args.max_seconds,
                    args.hold_seconds,
                    filming,
                )
            )
        except BaseException as exc:  # ruff: ignore[blind-except] - reported to the main thread
            logger.exception("The filming failed")
            film_error.append(exc)

    film_thread = threading.Thread(target=run_film, daemon=True)
    film_thread.start()
    if not filming.wait(timeout=120):
        logger.error("The film never started")
        return 1

    logger.info("Running the demo campaign in-process...")
    exit_code = run_demo_campaign(store_path)

    film_thread.join(timeout=300)
    if film_error:
        return 1
    if server_error:
        logger.error("The dashboard failed: %s", server_error[0])
        return 1
    if not film:
        logger.error("The film was never written")
        return 1

    run_id = latest_run(args.port)
    status = wait_for_run_to_finish(args.port, run_id) if run_id else "unknown"
    logger.info("The run finished as %s", status)
    print(
        json.dumps({
            "video": str(film[0]),
            "bytes": film[0].stat().st_size,
            "campaign_exit": exit_code,
        })
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
