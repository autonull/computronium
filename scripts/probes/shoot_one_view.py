"""Photograph one stage view of the dashboard, while it changes.

A view is judged by looking at it, and looking at it means opening the
dashboard on a store that holds what the view draws and pressing its
key. This probe does that for one view: it starts the dashboard on the
tour's store, presses the key, and writes the picture.

It is the tool the multi-run view was drawn with: the picture was looked
at after every change to the view, the ground, the labels and the frame.

Run: uv run python scripts/probes/shoot_one_view.py u /tmp/view.png
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dashboard_capture import (  # ruff: ignore[module-import-not-at-top-of-file]
    launch_browser,
    open_dashboard,
    start_dashboard,
    wait_for_http,
)

PORT = 8093
STORE = Path("/tmp/opencode/tour.duckdb")


def main() -> int:
    """Open the dashboard, press the key, and write the picture."""
    from playwright.sync_api import sync_playwright

    key = sys.argv[1] if len(sys.argv) > 1 else "1"
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp/opencode/view.png")

    _dashboard, _thread, errors = start_dashboard(PORT, STORE)
    if not wait_for_http(PORT):
        print("the dashboard did not start", errors)
        return 1
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        page = open_dashboard(browser, PORT)
        page.wait_for_timeout(4000)
        page.keyboard.press(key)
        deadline = time.time() + 60
        while time.time() < deadline:
            active = page.evaluate(
                "() => { const d = window.__DASHBOARD__;"
                " return d && d.viewSwitcher ? d.viewSwitcher.activeId : null; }"
            )
            if active:
                break
            time.sleep(0.5)
        page.wait_for_timeout(2500)
        page.screenshot(path=str(out))
        browser.close()
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
