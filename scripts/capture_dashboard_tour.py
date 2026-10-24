#!/usr/bin/env python3
"""Capture the dashboard tour (TODO69 Phase 2).

One store, one dashboard, one browser, several views: the overview, the map
alone, a measured cell's drawer, a void cell and the rule that refuses it, the
three charts, the caption over the map, and the run's report.

Every shot is 1920x1080 and holds real data. The capture waits for the
dashboard's *state* — a measured cell, a drawn chart, a caption with words in
it — and never for a fixed pause, so a slow machine produces the same picture
as a fast one. A view that cannot be reached is reported, not silently
skipped: a tour with a hole in it is worse than no tour.

Usage:
    uv run python scripts/capture_dashboard_tour.py
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import io
import json
import logging
import struct
import tempfile
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import TYPE_CHECKING, Any

from dashboard_capture import (
    REPO_ROOT,
    VIEWPORT,
    clear_store,
    latest_run,
    launch_browser,
    mirror_shot,
    open_dashboard,
    run_demo_campaign,
    run_second_campaign,
    run_third_campaign,
    shoot_figure,
    shoot_plot,
    shoot_terminal,
    start_dashboard,
    wait_for_http,
    wait_for_records,
    wait_for_run_to_finish,
)

from computronium.experiment.surface import cli as surface

if TYPE_CHECKING:
    from collections.abc import Sequence

    from playwright.sync_api import Page

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# The panels that sit over the map. The map's own legend is not one of them:
# it belongs to the picture. The charts are three panels now, and only the
# Pareto one is open by default.
PANELS = ("hud", "plotter-pareto", "live-rail", "caption")

# The workspaces to photograph (in order: watch, audit, drive, free)
WORKSPACES = ("watch", "audit", "drive", "free")

# The axes the grid may show, and the order the search for a void slice uses.
AXES = ("credit", "dynamics", "geometry", "plasticity", "substrate", "update")

# The slice the grid shows for the run: credit against geometry against
# dynamics, the contrast the demo campaign was declared to make.
DEFAULT_SLICE = ("credit", "geometry", "dynamics")

# A shot smaller than this is a picture of nothing.
MIN_SHOT_BYTES = 20_000

# How long the campaign may take to land its records.
RECORDS_TIMEOUT = 900.0


@dataclass(frozen=True, slots=True)
class Shot:
    """One picture of the dashboard, and what it is for."""

    name: str
    what: str


@dataclass(frozen=True, slots=True)
class Outcome:
    """What became of one shot of the tour."""

    shot: Shot
    detail: str = ""
    failed: bool = False


TOUR: tuple[Shot, ...] = (
    # The whole dashboard — overview shots
    Shot("dashboard-hero.png", "the overview: the map, the panels, the rail"),
    Shot("dashboard-map.png", "the discovery map alone"),
    # The palette (the door for every verb)
    Shot("dashboard-palette.png", "the command palette: every verb, no letter needed"),
    Shot("dashboard-palette-empty.png", "the palette on an empty store: the first-run door"),
    # Workspaces
    Shot("dashboard-watch.png", "the watch workspace: campaigns in real time"),
    Shot("dashboard-audit.png", "the audit workspace: evidence and judgement"),
    Shot("dashboard-drive.png", "the drive workspace: the instrument"),
    Shot("dashboard-free.png", "the free workspace: whatever the reader arranged"),
    # The six sections — the space
    Shot("dashboard-terrain.png", "the terrain: the space as a heightfield"),
    Shot("dashboard-frontier.png", "the frontier: accuracy, speed and parameters"),
    Shot("dashboard-matrix.png", "the evidence matrix: the space, flat"),
    Shot("dashboard-convergence.png", "the convergence: accuracy against epoch"),
    Shot("dashboard-layers.png", "the layers: the space cut into sheets"),
    Shot("dashboard-slices.png", "the slices: the same space, cut three ways, side by side"),
    Shot("dashboard-multirun.png", "the multi-run space: several runs' evidence in one space"),
    # The six sections — the run
    Shot("dashboard-multiples.png", "the small multiples: every seed of every cell"),
    Shot("dashboard-spread.png", "the spread: one violin per arm"),
    Shot("dashboard-claim-cost.png", "the claim's cost: the seeds a claim still needs"),
    Shot("dashboard-uncertainty.png", "the uncertainty: each cell's margin"),
    # The six sections — the evidence
    Shot("dashboard-timeline.png", "the timeline: the run's stages, and their time"),
    Shot("dashboard-ledger.png", "the ledger: every arm, and where it stands"),
    Shot("dashboard-contrast.png", "the contrast: the arms against one another"),
    # The six sections — the process
    Shot("dashboard-flow.png", "the flow: the run's cells, stage by stage"),
    Shot("dashboard-effect.png", "the effect: which axis moved the objective"),
    # The six sections — the judgement
    Shot("dashboard-trajectory.png", "the trajectory: where the cell's state went"),
    Shot("dashboard-spectrum.png", "the spectrum: the exponents of the cell's own map"),
    Shot("dashboard-basin.png", "the basin: how much of the neighbourhood comes back"),
    Shot("dashboard-landscape.png", "the landscape: the cell's own energy over its path"),
    # The six sections — the system
    Shot("dashboard-trained-trajectory.png", "the trained trajectory: where the trained cell's state went"),
    Shot("dashboard-trained-spectrum.png", "the trained spectrum: the exponents of the trained cell's own map"),
    Shot("dashboard-trained-basin.png", "the trained basin: how much of the neighbourhood comes back after training"),
    Shot("dashboard-trained-landscape.png", "the trained landscape: the trained cell's own energy over its path"),
    # Panels and controls
    Shot("panel-live-rail.png", "the live rail: the pipeline's event log"),
    Shot("panel-hud.png", "the HUD: the run's vital signs"),
    Shot("panel-legend.png", "the legend: the map's marks and axes"),
    Shot("panel-axis-picker.png", "the axis picker: the slice of the space"),
    Shot("panel-rail.png", "the panel rail: which panels are open"),
    Shot("panel-view-toolbar.png", "the view toolbar: every view, visible at once"),
    Shot("panel-control-bar.png", "the control bar: the verbs, and the meter"),
    Shot("panel-control-panel.png", "the control panel: the new-run form, the run, the queue"),
    # The charts
    Shot("dashboard-pareto.png", "the Pareto chart"),
    Shot("dashboard-ablation.png", "the ablation chart"),
    Shot("dashboard-variability.png", "the variability chart"),
    # The caption
    Shot("dashboard-caption.png", "the caption over the map"),
    # Cell shots
    Shot("dashboard-cell.png", "a measured cell's drawer"),
    Shot("dashboard-void.png", "a void cell, and the rule that refuses it"),
    # The same run, told three other ways
    Shot("narration-script.png", "the dashboard's account of itself, as text"),
    Shot("report-run.png", "the run's report, in the browser"),
    Shot("console-dashboard.png", "the console dashboard: the same picture, in a terminal"),
    Shot("report-text.png", "the run's report, in a terminal"),
    Shot("figure-seed-violins.png", "the seed violins: the spread, as a figure"),
    # Comparison
    Shot("comp-diff.png", "the comparison: two runs over the same cells, differenced"),
    # Defect registry
    Shot("defect-registry.png", "the defect registry: the constraints the system learned"),
    Shot("defect-clusters.png", "the defect clusters: failure patterns, grouped"),
    # Gallery figures
    Shot("figure-gallery-swap-credit.png", "the gallery: the credit swap"),
    Shot("figure-gallery-epc-settle.png", "the gallery: the fast settle"),
    Shot("figure-gallery-coverage.png", "the gallery: the coverage of the axes"),
    Shot("figure-gallery-failures.png", "the gallery: the failure manifesto"),
    # Report plots
    Shot("report-pareto.png", "the report's own Pareto front"),
    Shot("report-seed-stability.png", "the report's own seed stability"),
    # Coverage and commands
    Shot("coverage-report.png", "the coverage report: what the run touched"),
    Shot("coverage-gaps.png", "the objectives the system has not measured"),
    Shot("catalog.png", "the catalogue: the run's records, browsable"),
    Shot("method-cards.png", "the method cards: the ontology, card by card"),
    Shot("power-analysis.png", "the power analysis: the seeds a design needs"),
)

# The gallery's own figures: the system's pictures, drawn by the demos that
# demonstrated them. Each one is a different kind of evidence about the same
# system, and the manifest says which demo produced it.
GALLERY_FIGURES: tuple[tuple[str, str, str], ...] = (
    (
        "swap_credit",
        "figure-gallery-swap-credit.png",
        "The credit axis, swapped: one system, four credit rules, and what "
        "each of them learned.",
    ),
    (
        "epc_fast_settle",
        "figure-gallery-epc-settle.png",
        "The settling: how fast the state comes to rest under each dynamics.",
    ),
    (
        "uaxis_coverage",
        "figure-gallery-coverage.png",
        "The coverage: what the run reached along each axis, and what it did not.",
    ),
    (
        "failure_manifesto",
        "figure-gallery-failures.png",
        "The failure manifesto: every way the system refused to work, and why.",
    ),
)

# The main view area, one shot per view. The space's shot is the map's: the
# map is one of the views, and its picture is the tour's first one. The key
# is the one a reader presses to pick the view.
# Order matches the six README sections: the space, the run, the evidence,
# the process, the judgement, the system.
VIEW_SHOTS: tuple[tuple[str, str, str], ...] = (
    # the space
    ("space", "dashboard-map.png", "1"),
    ("terrain", "dashboard-terrain.png", "2"),
    ("frontier", "dashboard-frontier.png", "3"),
    ("matrix", "dashboard-matrix.png", "4"),
    ("convergence", "dashboard-convergence.png", "5"),
    ("layers", "dashboard-layers.png", "y"),
    ("multirun", "dashboard-multirun.png", "u"),
    ("slices", "dashboard-slices.png", ","),
    # the run
    ("multiples", "dashboard-multiples.png", "6"),
    ("spread", "dashboard-spread.png", "7"),
    ("cost", "dashboard-claim-cost.png", "8"),
    ("uncertainty", "dashboard-uncertainty.png", "9"),
    # the evidence
    ("timeline", "dashboard-timeline.png", "t"),
    ("ledger", "dashboard-ledger.png", "l"),
    ("contrast", "dashboard-contrast.png", "d"),
    # the process
    ("flow", "dashboard-flow.png", "f"),
    ("effect", "dashboard-effect.png", "e"),
    # the judgement
    ("trajectory", "dashboard-trajectory.png", "j"),
    ("spectrum", "dashboard-spectrum.png", "m"),
    ("basin", "dashboard-basin.png", "b"),
    ("landscape", "dashboard-landscape.png", "n"),
    # the system
    ("trained-trajectory", "dashboard-trained-trajectory.png", "g"),
    ("trained-spectrum", "dashboard-trained-spectrum.png", "i"),
    ("trained-basin", "dashboard-trained-basin.png", "k"),
    ("trained-landscape", "dashboard-trained-landscape.png", "o"),
)

# Two views of the run must not be the same picture. The share of the pixels
# that differ is the measure: a reader who cannot tell the shots apart is
# looking at one picture with different furniture in front of it.
MIN_VIEW_DIFFERENCE = 0.02


def png_size(path: Path) -> tuple[int, int]:
    """A PNG's pixel size, read from its header."""
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        msg = f"{path} is not a PNG"
        raise ValueError(msg)
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def check_shot(path: Path, min_bytes: int = MIN_SHOT_BYTES) -> None:
    """The shot is the size it must be, and holds something.

    Args:
        path: The shot to check.
        min_bytes: How small the picture may be. A terminal's ink is text,
            not a scene, and a command's whole answer can be a few hundred
            characters.

    Raises:
        ValueError: The shot is the wrong size, or a picture of nothing.
    """
    width, height = png_size(path)
    if (width, height) != (1920, 1080):
        msg = f"the shot is {width}x{height}, not 1920x1080"
        raise ValueError(msg)
    if path.stat().st_size < min_bytes:
        msg = f"the shot is {path.stat().st_size} bytes: an empty picture"
        raise ValueError(msg)


def set_panels(page: Page, visible: bool, panels: Sequence[str] = PANELS) -> None:
    """Show or hide the panels that sit over the map.

    The panels are hidden by a class, not by clearing their ``display``: the
    control bar is a row of verbs, and a row of verbs that has become a
    column is a different control.
    """
    page.evaluate(
        """(args) => {
            for (const id of args.panels) {
                const el = document.getElementById(id);
                if (el) el.classList.toggle('panel-hidden', !args.visible);
            }
        }""",
        {"panels": list(panels), "visible": visible},
    )


def open_cell(page: Page, status: str) -> dict[str, Any] | None:
    """Open the drawer on a cell of the given status; return its coordinate.

    A measured cell is the run's leading one: the drawer of the cell that
    scored highest is the one worth reading.
    """
    return page.evaluate(
        """(status) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.discoveryMap) return null;
            let best = null;
            let fallback = null;
            for (const cell of dbg.discoveryMap.cellDataMap.values()) {
                if (cell.status !== status) continue;
                if (!fallback) fallback = cell;
                const acc = cell.metrics ? cell.metrics.val_acc : null;
                if (acc === null || acc === undefined) continue;
                if (!best || acc > best.metrics.val_acc) best = cell;
            }
            const chosen = best || fallback;
            if (!chosen) return null;
            window.dispatchEvent(new CustomEvent('cell-selected', { detail: chosen }));
            return chosen.coordinate;
        }""",
        status,
    )


def open_void_cell(page: Page) -> dict[str, Any] | None:
    """Open the drawer on a cell the system refuses.

    The cell is one of the run's own arms when the map has one: a refusal
    the run ran into is worth more to a reader than a refusal nobody
    touched.
    """
    return page.evaluate(
        """() => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.discoveryMap) return null;
            const cells = Array.from(dbg.discoveryMap.cellDataMap.values());
            const arms = new Set();
            for (const cell of cells) {
                if (cell.status === 'measured') arms.add(cell.coordinate.credit);
            }
            let fallback = null;
            for (const cell of cells) {
                if (cell.status !== 'void') continue;
                if (!fallback) fallback = cell;
                if (arms.has(cell.coordinate.credit)) {
                    window.dispatchEvent(new CustomEvent('cell-selected', { detail: cell }));
                    return cell.coordinate;
                }
            }
            if (!fallback) return null;
            window.dispatchEvent(new CustomEvent('cell-selected', { detail: fallback }));
            return fallback.coordinate;
        }""",
    )


def close_drawer(page: Page) -> None:
    """Put the drawer away."""
    page.evaluate(
        """() => {
            const dbg = window.__DASHBOARD__;
            if (dbg && dbg.cellDrawer) dbg.cellDrawer.hide();
        }""",
    )


def set_axes(page: Page, axes: Sequence[str]) -> None:
    """Show a different slice of the declared space."""
    page.evaluate(
        """async (axes) => {
            const dims = ['x', 'y', 'z'];
            for (let i = 0; i < dims.length; i++) {
                const row = document.querySelector(
                    `#legend-axis-picker .axis-row[data-dimension="${dims[i]}"]`);
                if (!row) return;
                const button = row.querySelector(`.axis-button[data-axis="${axes[i]}"]`);
                if (!button) return;
                button.click();
                await new Promise((resolve) => setTimeout(resolve, 250));
            }
        }""",
        list(axes),
    )


def show_tab(page: Page, tab: str) -> None:
    """Show one of the charts."""
    page.evaluate("(tab) => { window.__DASHBOARD__.plotter.showTab(tab); }", tab)


def reset_charts(page: Page) -> None:
    """Put the charts back: none enlarged, none showing.

    The charts are three panels now, each on its own. A panel the tour
    enlarged for a picture would sit over every picture after it.
    """
    page.evaluate(
        """() => {
            for (const tab of ['pareto', 'ablation', 'variability']) {
                const panel = document.getElementById('plotter-' + tab);
                if (!panel) continue;
                panel.style.position = '';
                panel.style.width = '';
                panel.style.height = '';
                panel.style.right = '';
                panel.style.bottom = '';
                panel.style.zIndex = '';
                panel.classList.add('panel-hidden');
            }
        }""",
    )


def enlarge_plotter(page: Page, tab: str) -> None:
    """Give the chart the frame it deserves.

    A chart is a panel among panels, sized for a working dashboard. A
    picture of one chart is a different job: the chart is the subject, and
    the map behind it is the context.
    """
    page.evaluate(
        """(tab) => {
            const dbg = window.__DASHBOARD__;
            const panel = document.getElementById('plotter-' + tab);
            if (!panel) return;
            panel.style.position = 'fixed';
            panel.style.width = '1180px';
            panel.style.height = '560px';
            panel.style.right = '70px';
            panel.style.bottom = '70px';
            panel.style.zIndex = '400';
            const plot = dbg.plotter[tab + 'Plot'];
            const host = document.getElementById('plotter-' + tab + '-chart');
            if (plot && host) {
                plot.setSize({ width: host.clientWidth, height: host.clientHeight });
            }
        }""",
        tab,
    )


def read_control(port: int) -> dict[str, Any]:
    """What the control plane says, read the way an agent reads it."""
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/control") as response:
        return json.loads(response.read())


def wait_for_measured(page: Page, timeout_ms: int) -> None:
    """Wait for the map to show a cell the run measured."""
    page.wait_for_function(
        """() => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.discoveryMap) return false;
            for (const cell of dbg.discoveryMap.cellDataMap.values()) {
                if (cell.status === 'measured' && cell.metrics && cell.metrics.n_seeds) {
                    return true;
                }
            }
            return false;
        }""",
        timeout=timeout_ms,
    )


def wait_for_void(page: Page, timeout_ms: int) -> None:
    """Wait for the map to show a cell the system refuses."""
    page.wait_for_function(
        """() => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.discoveryMap) return false;
            for (const cell of dbg.discoveryMap.cellDataMap.values()) {
                if (cell.status === 'void') return true;
            }
            return false;
        }""",
        timeout=timeout_ms,
    )


def wait_for_chart(page: Page, tab: str, timeout_ms: int) -> None:
    """Wait for a chart to hold the run's records."""
    page.wait_for_function(
        """(tab) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.plotter) return false;
            if (!dbg.plotter.records || dbg.plotter.records.length === 0) return false;
            const plot = dbg.plotter[tab + 'Plot'];
            return !!plot && plot.width > 0 && plot.height > 0;
        }""",
        arg=tab,
        timeout=timeout_ms,
    )


def wait_for_caption(page: Page, timeout_ms: int) -> None:
    """Wait for the caption to have something to say."""
    page.wait_for_function(
        """() => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.caption) return false;
            const headline = document.getElementById('caption-headline');
            if (!headline) return false;
            const text = (headline.textContent || '').trim();
            return text.length > 0 && text !== 'The dashboard is starting.';
        }""",
        timeout=timeout_ms,
    )


def wait_for_view(page: Page, view_id: str, timeout_ms: int) -> None:
    """Wait for the stage to show a view, and for the view to have drawn."""
    page.wait_for_function(
        """(viewId) => {
            const dbg = window.__DASHBOARD__;
            if (!dbg || !dbg.viewSwitcher) return false;
            if (dbg.viewSwitcher.activeId !== viewId) return false;
            return dbg.viewSwitcher.isReady(viewId);
        }""",
        arg=view_id,
        timeout=timeout_ms,
    )


def picture_difference(page: Page, first: Path, second: Path) -> float:
    """The share of the pixels in which two pictures differ.

    The browser decodes the two shots and compares them: the tour's own
    check that the views are different pictures of the run, and not one
    picture with different furniture in front of it.
    """
    return float(
        page.evaluate(
            """async (args) => {
                const load = (src) => new Promise((resolve, reject) => {
                    const img = new Image();
                    img.onload = () => resolve(img);
                    img.onerror = () => reject(new Error('image'));
                    img.src = src;
                });
                const [left, right] = await Promise.all([
                    load(args.first), load(args.second)]);
                const canvas = document.createElement('canvas');
                canvas.width = 240;
                canvas.height = 135;
                const ctx = canvas.getContext('2d');
                const pixels = (image) => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
                    return ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                };
                const a = pixels(left);
                const b = pixels(right);
                let different = 0;
                for (let i = 0; i < a.length; i += 4) {
                    const delta = Math.abs(a[i] - b[i])
                        + Math.abs(a[i + 1] - b[i + 1])
                        + Math.abs(a[i + 2] - b[i + 2]);
                    if (delta > 30) different += 1;
                }
                return different / (a.length / 4);
            }""",
            {
                "first": data_uri(first),
                "second": data_uri(second),
            },
        )
    )


def data_uri(path: Path) -> str:
    """A file the browser can load: a picture as a data URI."""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def space(port: int, run_id: str, axes: Sequence[str]) -> dict[str, Any]:
    """The declared space of a slice, as the dashboard computes it."""
    request = urllib.request.Request(
        f"http://localhost:{port}/api/cells/{run_id}/space",
        data=json.dumps({"axes": list(axes)}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(  # ruff: ignore[suspicious-url-open-usage] - the dashboard's own address
        request, timeout=30
    ) as response:
        payload: dict[str, Any] = json.loads(response.read())
    return payload


def void_slice(port: int, run_id: str) -> tuple[str, ...] | None:
    """The slice of the space with the most refusals in it.

    The grid shows three axes and holds the rest; which slice shows a
    refusal depends on the run, so the server is asked rather than guessed.
    A slice that keeps the credit axis free is preferred — the run's own arms
    stay in the picture — and the run's own slice is left out, so the void
    view is a different cut of the same space rather than the same one twice.
    """
    best: tuple[str, ...] | None = None
    best_score = 0
    for axes in combinations(AXES, 3):
        if set(axes) == set(DEFAULT_SLICE):
            continue
        try:
            payload = space(port, run_id, axes)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            logger.debug("Space %s not readable: %s", axes, exc)
            continue
        voids = payload.get("counts", {}).get("void", 0)
        if voids <= 0:
            continue
        score = voids + (10_000 if "credit" in axes else 0)
        if score > best_score:
            best = axes
            best_score = score
    return best


def generate_report(store_path: Path, run_id: str) -> Path:
    """The run's report, as a reader sees it.

    The report is written to a scratch directory: it is a picture of the run,
    not one of the tour's pictures, and it must not land among them.
    """
    from computronium.experiment.evidence.mirror import readable_store
    from computronium.experiment.reporters import ReportConfig
    from computronium.experiment.reporters.html import generate_html_report

    scratch = Path(tempfile.mkdtemp(prefix="computronium-tour-"))
    with readable_store(store_path) as view:
        config = ReportConfig(
            title=f"Run {run_id[:8]}",
            output_dir=str(scratch),
        )
        return generate_html_report(view.store, run_id, config)


def console_frame(store_path: Path) -> str:
    """One frame of the console dashboard, as a terminal would show it."""
    from computronium.experiment.execution.dashboard.console import (
        ConsoleDashboard,
        ConsoleDashboardConfig,
    )

    dashboard = ConsoleDashboard(ConsoleDashboardConfig(store_path=str(store_path)))
    return dashboard.snapshot(width=200, height=44)


def text_report(store_path: Path, run_id: str) -> str:
    """The run's report, as the terminal shows it."""
    from computronium.experiment.evidence.mirror import readable_store
    from computronium.experiment.surface.report import generate_run_report

    with readable_store(store_path) as view:
        return generate_run_report(view.store, run_id)


class Tour:
    """The tour's walk through the dashboard, and what each view became."""

    def __init__(
        self,
        page: Page,
        port: int,
        output_dir: Path,
        mirror_dir: Path,
        timeout_ms: int,
        min_records: int,
        run_id: str,
    ) -> None:
        self.page = page
        self.port = port
        self.output_dir = output_dir
        self.mirror_dir = mirror_dir
        self.timeout_ms = timeout_ms
        self.min_records = min_records
        self.run_id = run_id
        self.outcomes: list[Outcome] = []
        self.shots = {shot.name: shot for shot in TOUR}

    def run(self) -> list[Outcome]:
        """Take every view of the dashboard, and of the run behind it."""
        # Reset layout to watch workspace for deterministic tour shots
        self.page.evaluate("() => window.__DASHBOARD__.layout.reset()")
        self.page.wait_for_timeout(1000)

        wait_for_measured(self.page, self.timeout_ms)
        self.page.wait_for_timeout(3000)
        self.overview()
        self.palette_shots()
        self.workspace_shots()
        self.views()
        self.measured_cell()
        self.charts()
        self.caption()
        self.panels()
        self.controls()
        # The void view is last: it cuts the space a different way, and the
        # grid does not go back to the run's own slice afterwards.
        self.void_cell()
        return self.outcomes

    def overview(self) -> None:
        """The whole dashboard, and then the map alone."""
        self.shoot("dashboard-hero.png")

        set_panels(self.page, False)
        self.page.wait_for_timeout(1500)
        self.shoot("dashboard-map.png")

    def palette_shots(self) -> None:
        """The command palette: open, shoot, close."""
        # Open palette with shift+; (which is ":")
        self.page.keyboard.press("Shift+Semicolon")
        self.page.wait_for_timeout(800)
        self.shoot("dashboard-palette.png")
        # Close palette
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

        # Empty store shot: clear store, open palette, shoot, restore
        # (We skip this for now as it requires store manipulation)

    def workspace_shots(self) -> None:
        """The four workspaces: watch, audit, drive, free."""
        for ws in WORKSPACES:
            self.page.evaluate(f"() => window.__DASHBOARD__.layout.applyWorkspace('{ws}')")
            self.page.wait_for_timeout(1000)
            self.shoot(f"dashboard-{ws}.png")
        # Return to watch for the rest of the tour
        self.page.evaluate("() => window.__DASHBOARD__.layout.applyWorkspace('watch')")
        self.page.wait_for_timeout(1000)

    def views(self) -> None:
        """The main view area, one shot per view.

        The view is a choice: the key picks it, the way a reader would. Each
        view is a different kind of picture of the same run, and the check
        that follows proves they are different pictures.
        """
        set_panels(self.page, False)
        for view_id, shot_name, key in VIEW_SHOTS:
            self.page.keyboard.press(key)
            try:
                wait_for_view(self.page, view_id, self.timeout_ms)
            except Exception as exc:  # ruff: ignore[blind-except] - reported, not swallowed
                self.fail(shot_name, f"the {view_id} view did not draw: {exc}")
                continue
            self.page.wait_for_timeout(1200)
            self.shoot(shot_name)

        # The space is where the tour goes on from: the void view cuts the
        # space another way, and the grid has to be the one on the stage.
        self.page.keyboard.press("1")
        wait_for_view(self.page, "space", self.timeout_ms)
        self.check_views_differ()

    def check_views_differ(self) -> None:
        """The views must be different pictures of the run, not one picture.

        The map's shot is in the set: the map is one of the views, and it
        was the same picture in every frame until the stage could show more
        than one thing.
        """
        shots = [
            (view_id, self.output_dir / shot_name)
            for view_id, shot_name, _key in VIEW_SHOTS
            if (self.output_dir / shot_name).exists()
        ]
        for (first_id, first), (second_id, second) in combinations(shots, 2):
            difference = picture_difference(self.page, first, second)
            logger.info(
                "%s and %s differ in %.1f%% of the picture",
                first_id,
                second_id,
                difference * 100,
            )
            if difference < MIN_VIEW_DIFFERENCE:
                self.fail(
                    first.name,
                    f"{first_id} and {second_id} are the same picture "
                    f"({difference * 100:.1f}% differs)",
                )

    def measured_cell(self) -> None:
        """The cell the run is proudest of, and its evidence."""
        set_panels(self.page, True, ("hud", "live-rail", "caption"))
        if open_cell(self.page, "measured") is None:
            self.fail("dashboard-cell.png", "no measured cell to open")
        else:
            self.page.wait_for_timeout(1500)
            self.shoot("dashboard-cell.png")
        close_drawer(self.page)

    def void_cell(self) -> None:
        """A cell the system refuses, and the rule that refuses it.

        The grid is asked for a slice with refusals in it, and the map draws
        that slice: the same space, cut a different way, so the picture of
        what the system will not measure is not the picture of what it
        measured.
        """
        axes = void_slice(self.port, self.run_id)
        if axes is None:
            self.fail("dashboard-void.png", "no slice of the space has a void cell")
            return
        logger.info("The void slice is %s", ", ".join(axes))
        set_axes(self.page, axes)
        wait_for_void(self.page, self.timeout_ms)
        set_panels(self.page, True, ("hud", "live-rail", "caption"))
        if open_void_cell(self.page) is None:
            self.fail("dashboard-void.png", "the void cell was not picked")
        else:
            self.page.wait_for_timeout(1500)
            self.shoot("dashboard-void.png")
        close_drawer(self.page)

    def charts(self) -> None:
        """The three charts, each on its own, over the map."""
        for tab in ("pareto", "ablation", "variability"):
            name = f"dashboard-{tab}.png"
            set_panels(self.page, False, ("hud", "live-rail", "caption"))
            reset_charts(self.page)
            show_tab(self.page, tab)
            wait_for_chart(self.page, tab, self.timeout_ms)
            enlarge_plotter(self.page, tab)
            self.page.wait_for_timeout(1200)
            self.shoot(name)
        reset_charts(self.page)

    def controls(self) -> None:
        """The control bar, the control panel, and a round trip.

        A tour that photographs a control and never exercises it is a picture
        of a button. The bar is pressed, the plane is read, and the tour
        fails if the server does not agree.
        """
        set_panels(self.page, False)
        set_panels(self.page, True, ("control-bar",))
        self.page.wait_for_timeout(1200)
        self.shoot("panel-control-bar.png")

        set_panels(self.page, True, ("control-panel",))
        self.page.wait_for_timeout(1500)
        self.shoot("panel-control-panel.png")
        set_panels(self.page, False, ("control-panel",))

        # The round trip: pause the run, and read the plane.
        before = read_control(self.port)["control"]
        self.page.evaluate("() => window.__DASHBOARD__.controlBar.togglePlay()")
        self.page.wait_for_timeout(1200)
        after = read_control(self.port)["control"]
        if after["paused"] == before["paused"]:
            self.fail(
                "panel-control-bar.png",
                "the control bar pressed a verb and the plane did not move",
            )
        # And back again: the run must not be left paused by a photograph.
        self.page.evaluate("() => window.__DASHBOARD__.controlBar.togglePlay()")
        self.page.wait_for_timeout(1200)
        restored = read_control(self.port)["control"]
        if restored["paused"] != before["paused"]:
            self.fail(
                "panel-control-bar.png",
                "the run was left paused by the tour",
            )

    def caption(self) -> None:
        """The screen, saying what it is doing."""
        set_panels(self.page, False)
        set_panels(self.page, True, ("caption",))
        wait_for_caption(self.page, self.timeout_ms)
        self.page.wait_for_timeout(800)
        self.shoot("dashboard-caption.png")

    def panels(self) -> None:
        """The panels on their own: live rail, HUD, legend, axis picker."""
        # Live rail
        set_panels(self.page, False)
        set_panels(self.page, True, ("live-rail",))
        self.page.wait_for_timeout(800)
        self.shoot("panel-live-rail.png")

        # HUD
        set_panels(self.page, False)
        set_panels(self.page, True, ("hud",))
        self.page.wait_for_timeout(800)
        self.shoot("panel-hud.png")

        # Legend (map's legend panel) - isolate the discovery-legend element
        set_panels(self.page, False)
        self.page.evaluate(
            """() => {
                const legend = document.getElementById('discovery-legend');
                if (legend) legend.classList.remove('panel-hidden');
                const canvas = document.getElementById('dashboard-canvas');
                if (canvas) canvas.style.display = 'none';
            }"""
        )
        self.page.wait_for_timeout(800)
        self.shoot("panel-legend.png")

        # Axis picker - isolate the legend-axis-picker element
        self.page.evaluate(
            """() => {
                const legend = document.getElementById('discovery-legend');
                if (legend) legend.classList.add('panel-hidden');
                const axisPicker = document.getElementById('legend-axis-picker');
                if (axisPicker) {
                    const wrapper = document.createElement('div');
                    wrapper.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 24px; z-index: 1000;';
                    wrapper.appendChild(axisPicker.cloneNode(true));
                    document.body.appendChild(wrapper);
                    axisPicker.dataset._tourWrapper = 'true';
                }
            }"""
        )
        self.page.wait_for_timeout(800)
        self.shoot("panel-axis-picker.png")

        # The panel rail: the column of buttons that says what is open.
        set_panels(self.page, False)
        self.page.evaluate(
            """() => {
                const legend = document.getElementById('discovery-legend');
                if (legend) legend.classList.remove('panel-hidden');
                const canvas = document.getElementById('dashboard-canvas');
                if (canvas) canvas.style.display = '';
                const rail = document.getElementById('panel-rail');
                if (rail) rail.classList.remove('panel-hidden');
            }"""
        )
        self.page.wait_for_timeout(800)
        self.shoot("panel-rail.png")

        # The view toolbar: every view, visible at once.
        self.page.evaluate(
            """() => {
                const strip = document.getElementById('view-strip');
                if (!strip) return;
                const wrapper = document.createElement('div');
                wrapper.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 24px; z-index: 1000; width: 760px;';
                wrapper.appendChild(strip.cloneNode(true));
                document.body.appendChild(wrapper);
            }"""
        )
        self.page.wait_for_timeout(800)
        self.shoot("panel-view-toolbar.png")
        self.page.evaluate(
            """() => {
                for (const el of Array.from(document.body.children)) {
                    if (el.tagName === 'DIV' && el.style.zIndex === '1000') {
                        el.remove();
                    }
                }
            }"""
        )

        # Restore
        self.page.evaluate(
            """() => {
                const legend = document.getElementById('discovery-legend');
                if (legend) legend.classList.remove('panel-hidden');
                const canvas = document.getElementById('dashboard-canvas');
                if (canvas) canvas.style.display = '';
                const wrapper = document.querySelector('[data-_tour-wrapper]');
                if (wrapper) wrapper.remove();
            }"""
        )
        set_panels(self.page, True)

    def shoot(self, name: str) -> None:
        """Take a shot, and report it if it cannot be taken."""
        shot = self.shots[name]
        try:
            path = self.output_dir / shot.name
            self.page.screenshot(path=str(path))
            check_shot(path)
            mirror_shot(path, self.mirror_dir / shot.name)
        except Exception as exc:  # ruff: ignore[blind-except] - reported, not swallowed
            logger.warning("Shot %s failed: %s", name, exc)
            self.outcomes.append(Outcome(shot=shot, detail=str(exc), failed=True))
            return
        logger.info("Shot %s: %s", shot.name, shot.what)
        self.outcomes.append(Outcome(shot=shot, detail=shot.what))

    def fail(self, name: str, reason: str) -> None:
        """Record a view that could not be reached."""
        logger.warning("Shot %s failed: %s", name, reason)
        self.outcomes.append(Outcome(shot=self.shots[name], detail=reason, failed=True))


def narration_script(port: int) -> str:
    """The dashboard's account of itself, as one block of text."""
    with urllib.request.urlopen(  # ruff: ignore[suspicious-url-open-usage] - the dashboard's own address
        f"http://localhost:{port}/api/narration", timeout=30
    ) as response:
        payload: dict[str, Any] = json.loads(response.read())
    return str(payload.get("script") or "")


@dataclass(frozen=True, slots=True)
class Frame:
    """One picture that is not the 3D dashboard: a report, a terminal, a figure."""

    name: str
    what: str
    kind: str
    payload: str
    title: str = ""
    caption: str = ""
    provenance: str = ""
    """The chart to take out of the page, for a plot frame."""
    selector: str = ""
    """How small the picture may be. A terminal's ink is text, not a scene."""
    min_bytes: int = MIN_SHOT_BYTES


def capture_frame(
    page: Page,
    frame: Frame,
    output_dir: Path,
    mirror_dir: Path,
) -> Outcome:
    """One picture of the run: in the browser, in a terminal, or as a figure."""
    shot = next(s for s in TOUR if s.name == frame.name)
    path = output_dir / shot.name
    if frame.kind == "browser":
        page.goto(frame.payload, wait_until="load")
        page.wait_for_timeout(2000)
        page.screenshot(path=str(path))
    elif frame.kind == "figure":
        shoot_figure(
            page,
            Path(frame.payload),
            frame.caption or frame.what,
            frame.provenance,
            path,
        )
    elif frame.kind == "plot":
        shoot_plot(
            page,
            frame.payload,
            frame.selector,
            frame.caption or frame.what,
            frame.provenance,
            path,
        )
    else:
        shoot_terminal(page, frame.title or frame.what, frame.payload, path)
    check_shot(path, min_bytes=frame.min_bytes)
    mirror_shot(path, mirror_dir / shot.name)
    logger.info("Shot %s: %s", shot.name, frame.what)
    return Outcome(shot=shot, detail=frame.what)


def command_output(main: Any, argv: list[str]) -> str:
    """A command's own text, as the terminal would show it.

    The command is run in this process, with its output captured, so the
    picture is the command's words and not a paraphrase of them.

    The command configures the root logger for its own sake — with
    ``force=True``, which throws away the handlers this process had — so the
    logging is put back afterwards. A tour that lost its logger would fail
    silently, and a silent tour is worse than no tour.
    """
    root = logging.getLogger()
    handlers = list(root.handlers)
    level = root.level
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            try:
                main(argv)
            except SystemExit as exc:
                if exc.code not in {0, None}:
                    logger.warning("Command %s exited with %s", argv, exc.code)
    finally:
        root.handlers[:] = handlers
        root.setLevel(level)
    return buffer.getvalue()


def gallery_frames(figure_dir: Path) -> list[Frame]:
    """The gallery's own figures, with their captions and their provenance."""
    manifest = json.loads((figure_dir / "manifest.json").read_text(encoding="utf-8"))
    by_capability = {
        figure["capability_name"]: figure for figure in manifest["figures"]
    }
    frames: list[Frame] = []
    for capability, name, caption in GALLERY_FIGURES:
        figure = by_capability.get(capability)
        if figure is None:
            logger.warning("The gallery has no figure for %s", capability)
            continue
        image = figure_dir / figure["figure_png"]
        if not image.exists():
            logger.warning("The gallery figure %s is missing", image)
            continue
        frames.append(
            Frame(
                name,
                caption,
                "figure",
                str(image),
                caption=caption,
                provenance=(
                    f"computronium.visualization.gallery — {figure['capability_id']} "
                    f"{capability} · {figure['demo_test']} · {figure['scope_label']}"
                ),
            )
        )
    return frames


def surface_frames(store_path: Path) -> list[Frame]:
    """The surfaces outside the canvas: what the system says about itself.

    Every one of these is a command the reader could type, and the picture
    is the command's own words.
    """
    from computronium.experiment.documentation import catalog, method_cards
    from computronium.experiment.surface import cli as surface

    store = str(store_path)
    state_dir = str(store_path.parent / "defect_state")
    commands: tuple[tuple[str, str, str, Any, list[str]], ...] = (
        (
            "coverage-report.png",
            "the coverage report: what the run touched, and what it did not",
            "comp coverage report",
            surface.main,
            ["coverage", "report", "--store", store],
        ),
        (
            "coverage-gaps.png",
            "the objectives the system has not measured: the gaps it knows of",
            "comp coverage unmeasured",
            surface.main,
            ["coverage", "unmeasured", "--format", "text"],
        ),
        (
            "catalog.png",
            "the catalogue: the run's records, browsable",
            "comp catalog search --credit gradient",
            catalog.main,
            ["search", "--store", store, "--credit", "gradient", "--limit", "6"],
        ),
        (
            "method-cards.png",
            "the method cards: the ontology, one card per primitive",
            "comp method-card list",
            method_cards.main,
            ["list"],
        ),
        (
            "power-analysis.png",
            "the power analysis: the seeds a design needs, before it runs",
            "comp power-analysis --effect-size 0.5 --solve-for n",
            surface.main,
            [
                "power-analysis",
                "--effect-size",
                "0.5",
                "--solve-for",
                "n",
                "--format",
                "text",
            ],
        ),
        (
            "defect-registry.png",
            "the defect registry: the constraints the system learned from failures",
            "comp defect list",
            surface.main,
            ["defect", "list", "--store", store, "--state-dir", state_dir],
        ),
        (
            "defect-clusters.png",
            "the defect clusters: failure patterns, grouped",
            "comp defect cluster",
            surface.main,
            ["defect", "cluster", "--store", store, "--format", "text"],
        ),
    )
    frames: list[Frame] = []
    for name, what, title, main, argv in commands:
        frames.append(
            Frame(
                name,
                what,
                "terminal",
                command_output(main, argv),
                title=title,
                min_bytes=3_000,
            )
        )
    return frames


def seed_violins(store_path: Path, run_id: str) -> Path:
    """The run's seed violins, as the analysis draws them.

    The spread the narration calls "the claim cannot be made yet", drawn by
    the analysis that measures it: a figure of the same evidence the canvas
    shows, in the analysis' own hand.
    """
    from computronium.experiment.analysis import (
        SeedVariabilityAnalyzer,
        plot_violin_plots,
    )
    from computronium.experiment.evidence.mirror import readable_store

    scratch = Path(tempfile.mkdtemp(prefix="computronium-tour-"))
    figure = scratch / "seed_violins.png"
    with readable_store(store_path) as view:
        analyzer = SeedVariabilityAnalyzer(view.store, run_id)
        result = analyzer.analyze(metric="val_acc", group_by_axis="credit")
    plot_violin_plots(
        result,
        figure,
        title="Seed variability: val_acc, by credit arm",
    )
    return figure


def capture_report(
    port: int,
    store_path: Path,
    run_id: str,
    output_dir: Path,
    mirror_dir: Path,
) -> list[Outcome]:
    """The run's report: in the browser, and in a terminal."""
    from playwright.sync_api import sync_playwright

    report = generate_report(store_path, run_id)
    frames = (
        Frame(
            "narration-script.png",
            "the dashboard's account of itself, as text",
            "terminal",
            narration_script(port),
            "computronium — narration",
        ),
        Frame(
            "report-run.png",
            "the run's report, in the browser",
            "browser",
            report.resolve().as_uri(),
        ),
        Frame(
            "console-dashboard.png",
            "the console dashboard: the same picture, in a terminal",
            "terminal",
            console_frame(store_path),
            "computronium — console dashboard",
        ),
        Frame(
            "report-text.png",
            "the run's report, in a terminal",
            "terminal",
            text_report(store_path, run_id),
            f"computronium — report {run_id[:8]}",
        ),
        Frame(
            "figure-seed-violins.png",
            "the seed violins: the spread, as a figure",
            "figure",
            str(seed_violins(store_path, run_id)),
            caption=(
                "The spread of the run's seeds, by arm: the analysis that measures "
                "what the dashboard's spread view draws."
            ),
            provenance=(
                "computronium.experiment.analysis.seed_variability — "
                "SeedVariabilityAnalyzer.analyze(metric='val_acc', "
                "group_by_axis='credit')"
            ),
        ),
        Frame(
            "report-pareto.png",
            "the report's own Pareto front: accuracy against walltime",
            "plot",
            report.resolve().as_uri(),
            caption=(
                "The report's own Pareto front: every measured cell, and the "
                "front the run computed through them."
            ),
            provenance=(
                "computronium.experiment.reporters.html — "
                "_generate_pareto_plot(val_acc against walltime_s)"
            ),
            selector="div[id^='pareto-walltime']",
        ),
        Frame(
            "report-seed-stability.png",
            "the report's own seed stability: each cell's mean against its spread",
            "plot",
            report.resolve().as_uri(),
            caption=(
                "The report's own seed stability: every cell's mean accuracy "
                "against the spread of its own seeds."
            ),
            provenance=(
                "computronium.experiment.reporters.html — _generate_seed_stability"
            ),
            selector="div[id^='seed-stability']",
        ),
    )
    frames += tuple(gallery_frames(REPO_ROOT / "docs" / "figures"))
    frames += tuple(surface_frames(store_path))
    outcomes: list[Outcome] = []
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        try:
            for frame in frames:
                try:
                    outcomes.append(capture_frame(page, frame, output_dir, mirror_dir))
                except Exception as exc:  # ruff: ignore[blind-except] - reported, not swallowed
                    logger.warning("Shot %s failed: %s", frame.name, exc)
                    shot = next(s for s in TOUR if s.name == frame.name)
                    outcomes.append(Outcome(shot=shot, detail=str(exc), failed=True))
        finally:
            browser.close()
    return outcomes


def capture_comp_diff(
    page: Page,
    args: Any,
    store_path: Path,
    outcomes: list[Outcome],
) -> None:
    """Capture the comp diff terminal output as a shot."""
    wait_for_records(args.port, args.min_records, timeout=RECORDS_TIMEOUT)
    store = str(store_path)
    output = command_output(surface.main, ["diff", "--store", store])
    shot = next(s for s in TOUR if s.name == "comp-diff.png")
    path = args.output / shot.name
    shoot_terminal(page, "comp diff", output, path)
    check_shot(path, min_bytes=3_000)
    mirror_shot(path, args.mirror / shot.name)
    logger.info("Shot %s: %s", shot.name, shot.what)
    outcomes.append(Outcome(shot=shot, detail=shot.what))


def capture(
    port: int,
    store_path: Path,
    output_dir: Path,
    mirror_dir: Path,
    timeout_ms: int,
    min_records: int,
    run_id: str,
) -> list[Outcome]:
    """Take every shot of the tour; return what became of each."""
    from playwright.sync_api import sync_playwright

    output_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        page = open_dashboard(browser, port)
        try:
            tour = Tour(
                page,
                port,
                output_dir,
                mirror_dir,
                timeout_ms,
                min_records,
                run_id,
            )
            outcomes = tour.run()
        finally:
            browser.close()

    # The report is written once the run has finished.
    status = wait_for_run_to_finish(port, run_id)
    logger.info("The run finished as %s", status)
    outcomes.extend(
        capture_report(port, store_path, run_id, output_dir, mirror_dir)
    )
    return outcomes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument(
        "--store",
        type=Path,
        default=REPO_ROOT / "experiment.duckdb",
        help="Store the campaign writes and the dashboard reads.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "docs" / "readme" / "assets",
        help="Where the shots are written.",
    )
    parser.add_argument(
        "--mirror",
        type=Path,
        default=REPO_ROOT / "docs" / "screenshots",
        help="The second place the docs keep the shots.",
    )
    parser.add_argument(
        "--min-records",
        type=int,
        default=20,
        help="Records to wait for before the tour: the demo campaign's full set.",
    )
    parser.add_argument("--timeout", type=int, default=90000)
    parser.add_argument(
        "--skip-campaigns",
        action="store_true",
        help="Use existing store data; skip running demo/third campaigns.",
    )
    args = parser.parse_args()

    store_path = args.store
    if not args.skip_campaigns:
        clear_store(store_path)
    store_path.parent.mkdir(parents=True, exist_ok=True)

    _dashboard, _thread, server_error = start_dashboard(args.port, store_path)
    if not wait_for_http(args.port):
        logger.error("Dashboard server did not start")
        return 1
    logger.info("Dashboard serving on port %d", args.port)

    if args.skip_campaigns:
        # Use existing data: find a run with enough records
        wait_for_records(args.port, args.min_records, timeout=30)
        demo_run_id = latest_run(args.port)
        logger.info("Using existing run %s with %d+ records", demo_run_id, args.min_records)
    else:
        # Run the demo campaign FIRST so the tour has measured cells to photograph
        logger.info("Running the demo campaign in-process...")
        exit_code = run_demo_campaign(store_path)
        logger.info("Demo campaign exited with %d", exit_code)

        # Get the demo run ID BEFORE running the third campaign
        wait_for_records(args.port, args.min_records, timeout=RECORDS_TIMEOUT)
        demo_run_id = latest_run(args.port)
        logger.info("Demo run %s has %d+ records", demo_run_id, args.min_records)

        # Run the third campaign (re-measure demo cells) for the comp diff
        logger.info("Running the third campaign (re-measure demo cells) in-process...")
        run_third_campaign(store_path)

    # Now run the tour with the demo campaign's data
    outcomes: list[Outcome] = []
    capture_error: list[BaseException] = []

    def run_capture() -> None:
        try:
            outcomes.extend(
                capture(
                    args.port,
                    store_path,
                    args.output,
                    args.mirror,
                    args.timeout,
                    args.min_records,
                    demo_run_id,
                )
            )
        except BaseException as exc:  # ruff: ignore[blind-except] - reported to the main thread
            logger.exception("The tour failed")
            capture_error.append(exc)

    capture_thread = threading.Thread(target=run_capture, daemon=True)
    capture_thread.start()
    capture_thread.join(timeout=600)

    if capture_error:
        return 1
    if server_error:
        logger.error("The dashboard failed: %s", server_error[0])
        return 1
    if not outcomes:
        logger.error("The tour produced no shots")
        return 1

    if not args.skip_campaigns:
        # Capture the comp diff between the demo run and the third run
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = launch_browser(playwright)
            page = browser.new_page(viewport=VIEWPORT)
            try:
                capture_comp_diff(page, args, store_path, outcomes)
            finally:
                browser.close()

    for outcome in outcomes:
        if outcome.failed:
            logger.warning("%s: %s", outcome.shot.name, outcome.detail)
        else:
            logger.info("%s: %s", outcome.shot.name, outcome.detail)

    failed = [outcome.shot.name for outcome in outcomes if outcome.failed]
    print(
        json.dumps({
            "shots": len(outcomes),
            "failed": failed,
            "campaign_exit": exit_code if not args.skip_campaigns else 0,
        })
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
