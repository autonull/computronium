"""UX-L6 behavioral (C6): populated vs empty dashboard differ in grayscale.

One screenshot pair through a real browser → PIL grayscale → mean-abs-diff
above a generous floor. No committed pixel baselines (user directive
2026-09-23: agile, non-brittle tests).
"""

from __future__ import annotations

import io
import time
from typing import TYPE_CHECKING, Any

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    from pathlib import Path

# 0–255 grayscale mean abs diff; populated atlas vs empty state differ by far
# more than this — generous floor keeps the lock behavioral, not pixel-brittle.
GRAYSCALE_MEAN_DIFF_FLOOR = 5.0


def _grayscale_mean_abs_diff(first_png: bytes, second_png: bytes) -> float:
    first = np.asarray(Image.open(io.BytesIO(first_png)).convert("L"), dtype=np.float64)
    second = np.asarray(
        Image.open(io.BytesIO(second_png)).convert("L"), dtype=np.float64
    )
    if first.shape != second.shape:
        second = np.asarray(
            Image.fromarray(second.astype(np.uint8)).resize((
                first.shape[1],
                first.shape[0],
            )),
            dtype=np.float64,
        )
    return float(np.abs(first - second).mean())


def _wait_for_source(driver: Any, needle: str, timeout: float = 30.0) -> None:
    """Poll past the 4 s driver implicit wait (atlas fit can exceed it)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if needle in driver.page_source:
            return
        time.sleep(0.25)
    raise AssertionError(f'Page never contained "{needle}" within {timeout}s')


def test_populated_vs_empty_distinguishable_in_grayscale(
    screen: Any, tmp_path: Path
) -> None:
    from nicegui import ui

    from computronium.ui.dashboard import build_dashboard
    from tests.ui.fixture import seed_campaign_root

    # NiceGUI's session driver defaults to a 4 s page-load timeout; the
    # dashboard's first render (glossary + atlas + UMAP) can exceed it.
    screen.selenium.set_page_load_timeout(30)
    # language="en" requests a locale bundle NiceGUI doesn't ship for English.
    # Plotly throws resize error on hidden containers at teardown — external noise.
    screen.allowed_js_errors.extend([
        "lang/en.umd.prod.js",
        "Resize must be passed a displayed plot div",
    ])
    populated = tmp_path / "populated"
    seed_campaign_root(populated)
    empty = tmp_path / "empty"
    empty.mkdir()
    holder = {"root": populated}

    @ui.page("/ux_l6_pair", language="en")
    def _pair_page() -> None:
        build_dashboard(
            holder["root"],
            ui_mode="explorer",
            ui_actions=False,
        )

    screen.open("/ux_l6_pair", timeout=30)
    # Wait for the map panel to render
    _wait_for_source(screen.selenium, "Map")
    populated_png = screen.selenium.get_screenshot_as_png()

    holder["root"] = empty
    screen.open("/ux_l6_pair", timeout=30)
    _wait_for_source(screen.selenium, "Map")
    empty_png = screen.selenium.get_screenshot_as_png()

    diff = _grayscale_mean_abs_diff(populated_png, empty_png)
    print(
        f"UX-L6 grayscale mean-abs-diff: {diff:.2f} (floor {GRAYSCALE_MEAN_DIFF_FLOOR})"
    )
    assert diff > GRAYSCALE_MEAN_DIFF_FLOOR, (
        f"states are indistinguishable without color: mean-abs-diff={diff:.2f}"
    )
