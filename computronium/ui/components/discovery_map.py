"""Discovery Map component (M1.4) — UMAP atlas with fog-of-war, region labels, shape encoding.

Lenses: Map (UMAP scatter), Trade-offs (Pareto front), Gallery (figure cards).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nicegui import ui

from computronium.ui.components.campaign_card import CampaignCardGallery
from computronium.ui.components.tradeoffs_panel import TradeoffsPanel
from computronium.ui.design_tokens import (
    ICONS,
    MAX_RENDERED_ROWS,
)
from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from pathlib import Path  # ruff: ignore[typing-only-standard-library-import]

    from plotly.graph_objects import Figure as go_Figure

    from computronium.ui.adapters import DiscoveryMapData


@dataclass(frozen=True, slots=True)
class MapSpecimen:
    """A single specimen (cell) on the map."""

    key: str
    x: float
    y: float
    dynamics: str
    credit: str
    update: str
    topology: str
    accuracy: float
    bp_deficit: float
    outcome: str
    is_void: bool = False
    is_pareto: bool = False


@dataclass(frozen=True, slots=True)
class MapRegion:
    """A labeled region on the map (auto-generated from dominant axes)."""

    name: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    dominant_dynamics: str
    dominant_credit: str
    specimen_count: int
    coverage_pct: float


class DiscoveryMap(BasePanel):
    """Discovery Map panel with fog-of-war, region labels, and shape-redundant markers.

    Lenses:
    - Map: UMAP scatter with region labels, shape = outcome
    - Trade-offs: Pareto front + dominated points, objective selector
    - Gallery: Figure cards (thumbnail + metadata)
    """

    def __init__(
        self,
        *,
        specimens: list[MapSpecimen] | None = None,
        regions: list[MapRegion] | None = None,
        fog_coverage_pct: float = 0.0,
        atlas_figure: go_Figure | None = None,
        # Trade-offs data
        pareto_cells: list | None = None,
        ruler_metrics: dict[str, float] | None = None,
        # Gallery data
        campaigns_dir: Path | str | None = None,
    ) -> None:
        super().__init__(
            panel_key="discovery_map",
            plain=(
                "This map shows all measured configurations as dots. Similar configurations "
                "are close together. Grey areas show unmeasured regions."
            ),
            why=(
                "The map reveals patterns: which configurations work well, which "
                "regions are unmeasured, and where to explore next."
            ),
            expert=(
                "UMAP embedding of one-hot encoded ontology axes (S×G×D×P) "
                "concatenated with physics metrics (accuracy, bp_deficit). "
                "Grey area coverage = KB coverage of planned regions. "
                "Markers: shape=dynamics family, color=BP-deficit (viridis). "
                "Voids shown as grey X markers (gate-rejected, not failures)."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/map.html",
        )

        self.specimens = specimens or []
        self.regions = regions or []
        self.fog_coverage_pct = fog_coverage_pct
        self.atlas_figure = atlas_figure

        # Lens state
        self._active_lens = "map"  # "map" | "tradeoffs" | "gallery"

        # Trade-offs data
        self._tradeoffs_panel = TradeoffsPanel(
            cells=pareto_cells or [],
            ruler_metrics=ruler_metrics or {},
        )

        # Gallery data
        self._gallery = CampaignCardGallery(campaigns_dir) if campaigns_dir else None

        # Map view state
        self._show_table = False

    def render(self) -> ui.element:
        """Render the Discovery Map panel with lens tabs (fresh UI every call)."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("Map")

            # Lens tabs
            with ui.tabs().classes("w-full") as tabs:
                tab_map = ui.tab("Map", icon=ICONS.get("map", "map"))
                tab_tradeoffs = ui.tab(
                    "Trade-offs", icon=ICONS.get("tradeoffs", "balance")
                )
                tab_gallery = ui.tab(
                    "Gallery", icon=ICONS.get("gallery", "photo_library")
                )

            with ui.tab_panels(
                tabs, value=self._get_tab_for_lens(tab_map, tab_tradeoffs, tab_gallery)
            ).classes("w-full"):
                # Map lens
                with ui.tab_panel(tab_map):
                    self._render_map_lens()

                # Trade-offs lens
                with ui.tab_panel(tab_tradeoffs):
                    self._tradeoffs_panel.render()

                # Gallery lens
                with ui.tab_panel(tab_gallery):
                    if self._gallery:
                        self._gallery.render()
                    else:
                        ui.label("No campaign gallery available.").classes(
                            "text-grey text-center p-8"
                        )

        return panel

    def _get_tab_for_lens(self, t_map: Any, t_tradeoffs: Any, t_gallery: Any) -> Any:
        """Get the tab element for the active lens (defaults to Map)."""
        tabs = {"map": t_map, "tradeoffs": t_tradeoffs, "gallery": t_gallery}
        return tabs.get(self._active_lens, t_map)

    def _render_map_lens(self) -> None:
        """Render the Map lens (UMAP + table toggle)."""
        # Fog-of-war banner
        with ui.row().classes("w-full items-center gap-2"):
            ui.icon(ICONS["fog"]).classes("text-2xl")
            ui.label(
                f"{'Unexplored Territory'}: {'Charted'} {self.fog_coverage_pct:.0f}%"
            ).classes("text-body")
            if self.fog_coverage_pct < 100:
                ui.label(
                    f"({100 - self.fog_coverage_pct:.0f}% {'Unexplored Territory'})"
                ).classes("text-caption text-grey-8")

        # View toggle: Map / Table
        with ui.row().classes("w-full items-center justify-between"):
            ui.label().classes("flex-1")  # Spacer
            with ui.row().classes("items-center gap-2"):
                ui.label("View").classes("text-sm text-grey-8")
                ui.switch(
                    value=self._show_table,
                    on_change=lambda e: self._toggle_view(bool(e.value)),
                ).props(f'size="sm" aria-label="{"View"}"')

        # Map view container
        figure_container = ui.column().classes("w-full")
        if self._show_table:
            figure_container.classes(add="hidden")

        with figure_container:
            self._render_map()

        # Table view container
        table_container = ui.column().classes("w-full hidden")
        if self._show_table:
            table_container.classes(remove="hidden")

        with table_container:
            self._render_table()

    def _toggle_view(self, show_table: bool) -> None:
        """Toggle between map and table view."""
        self._show_table = show_table
        # Next render() call will reflect the new state

    def _render_map(self) -> None:
        """Render the Plotly map figure."""
        if self.atlas_figure is not None:
            ui.plotly(self.atlas_figure).classes("w-full")
            # Instrument honesty caption
            ui.label(
                "UMAP layout: recomputed embedding, not a trajectory. "
                "Markers use shape encoding (never color-only)."
            ).classes("text-caption text-grey-8 mt-1")
        else:
            with ui.card().classes("w-full p-8 items-center"):
                ui.icon(ICONS["map"]).classes("text-6xl text-grey-8")
                ui.label("Map loading...").classes("text-grey-8")

    def _table_rows(self) -> list[dict[str, str]]:
        """Table rows for the current specimens, capped at MAX_RENDERED_ROWS."""
        rows = []
        for s in self.specimens[:MAX_RENDERED_ROWS]:
            rows.append({
                "key": s.key[:30],
                "dynamics": s.dynamics,
                "credit": s.credit,
                "update": s.update,
                "topology": s.topology,
                "accuracy": f"{s.accuracy:.3f}",
                "bp_deficit": f"{s.bp_deficit:.3f}",
                "outcome": s.outcome,
                "pareto": "★" if s.is_pareto else "",
                "void": "✗" if s.is_void else "",
            })
        return rows

    def _render_table(self) -> None:
        """Render sortable table alternative (100% map info, capped rows)."""
        total = len(self.specimens)
        rows = self._table_rows()

        if not rows:
            ui.label("No data available").classes("text-grey")
            return

        columns = [
            {
                "name": "key",
                "label": "One measured recipe",
                "field": "key",
                "sortable": True,
            },
            {
                "name": "dynamics",
                "label": "Learning dynamics",
                "field": "dynamics",
                "sortable": True,
            },
            {
                "name": "credit",
                "label": "Credit assignment",
                "field": "credit",
                "sortable": True,
            },
            {
                "name": "update",
                "label": "Parameter update",
                "field": "update",
                "sortable": True,
            },
            {
                "name": "topology",
                "label": "Network topology",
                "field": "topology",
                "sortable": True,
            },
            {
                "name": "accuracy",
                "label": "Accuracy",
                "field": "accuracy",
                "sortable": True,
            },
            {
                "name": "bp_deficit",
                "label": "Gap vs. backprop baseline",
                "field": "bp_deficit",
                "sortable": True,
            },
            {
                "name": "outcome",
                "label": "Outcome",
                "field": "outcome",
                "sortable": True,
            },
            {
                "name": "pareto",
                "label": "Best trade-off",
                "field": "pareto",
                "sortable": True,
            },
            {
                "name": "void",
                "label": "Ontology boundary (not a bug)",
                "field": "void",
                "sortable": True,
            },
        ]

        ui.table(rows=rows, columns=columns, row_key="key").classes("w-full").props(
            "dense flat bordered"
        )
        if total > MAX_RENDERED_ROWS:
            ui.label(f"{'Showing first rows'}: {len(rows)} / {total}").classes(
                "text-caption text-grey"
            )

    def _refresh(self) -> None:
        """No-op since render() creates fresh UI."""
        # The next render() call will create fresh UI with current data

    def update_data(
        self,
        data: DiscoveryMapData | None = None,
        *,
        specimens: list[MapSpecimen] | None = None,
        regions: list[MapRegion] | None = None,
        fog_coverage_pct: float | None = None,
        atlas_figure: go_Figure | None = None,
        # Trade-offs data
        pareto_cells: list | None = None,
        ruler_metrics: dict[str, float] | None = None,
        # Gallery data
        campaigns_dir: Path | str | None = None,
    ) -> None:
        """Update panel data (no UI manipulation - next render() will reflect changes)."""
        if data is not None:
            specimens = data.specimens
            regions = data.regions
            fog_coverage_pct = data.fog_coverage_pct
            atlas_figure = data.atlas_figure
            pareto_cells = getattr(data, "pareto_cells", None)
            ruler_metrics = getattr(data, "ruler_metrics", None)
            campaigns_dir = getattr(data, "campaigns_dir", None)
        if specimens is not None:
            self.specimens = specimens
        if regions is not None:
            self.regions = regions
        if fog_coverage_pct is not None:
            self.fog_coverage_pct = fog_coverage_pct
        if atlas_figure is not None:
            self.atlas_figure = atlas_figure
        if pareto_cells is not None:
            self._tradeoffs_panel.update_cells(pareto_cells)
        if ruler_metrics is not None:
            self._tradeoffs_panel.ruler_metrics = ruler_metrics
        if campaigns_dir is not None and self._gallery:
            self._gallery = CampaignCardGallery(campaigns_dir)
        # No _refresh() call - UI updates on next render()

    def set_lens(self, lens: str) -> None:
        """Set active lens (Map/Trade-offs/Gallery)."""
        if lens not in {"map", "tradeoffs", "gallery"}:
            lens = "map"
        self._active_lens = lens


def create_discovery_map_from_atlas(
    df,  # pandas DataFrame from atlas.load_cells
    voids_df,  # pandas DataFrame from atlas.load_voids
    fog_coverage_pct: float = 0.0,
    pareto_keys: set[str] | None = None,
) -> tuple[list[MapSpecimen], list[MapRegion]]:
    """Create specimens and regions from atlas DataFrames (columnar, O(n)).

    ``pareto_keys`` marks front membership directly — avoids a second
    specimen rebuild in the adapter.
    """
    n = len(df)
    if n == 0:
        return [], _generate_regions(df, voids_df)

    dyn = df["dynamics"].tolist()
    cred = df["credit"].tolist()
    upd = df["update"].tolist()
    topo = df["topology"].tolist() if "topology" in df.columns else ["feedforward"] * n
    acc = df["accuracy"].tolist() if "accuracy" in df.columns else [0.0] * n
    bp = df["bp_deficit"].tolist() if "bp_deficit" in df.columns else [0.0] * n
    xs = df["x"].tolist() if "x" in df.columns else [0.0] * n
    ys = df["y"].tolist() if "y" in df.columns else [0.0] * n
    void_flags = df["is_void"].tolist() if "is_void" in df.columns else [False] * n
    nan_flags = df["nan_loss"].tolist() if "nan_loss" in df.columns else [False] * n
    raw_keys = df["key"].tolist() if "key" in df.columns else [None] * n

    specimens = []
    for i in range(n):
        key = str(raw_keys[i]) if raw_keys[i] else f"{dyn[i]}|{cred[i]}|{upd[i]}"
        specimens.append(
            MapSpecimen(
                key=key,
                x=float(xs[i]),
                y=float(ys[i]),
                dynamics=str(dyn[i]),
                credit=str(cred[i]),
                update=str(upd[i]),
                topology=str(topo[i]),
                accuracy=float(acc[i]),
                bp_deficit=float(bp[i]),
                outcome=_outcome_from_values(void_flags[i], nan_flags[i], acc[i]),
                is_void=bool(void_flags[i]),
                is_pareto=bool(pareto_keys) and key in pareto_keys,
            )
        )

    # Generate region labels from dominant axes in local neighborhoods
    regions = _generate_regions(df, voids_df)

    return specimens, regions


def _outcome_from_values(is_void: object, nan_loss: object, accuracy: float) -> str:
    """Generate plain-language outcome label from columnar cell values."""
    if is_void:
        return "structural_void"
    if nan_loss:
        return "diverged"
    if accuracy >= 0.5:
        return "learned"
    if accuracy >= 0.15:
        return "marginal"
    return "chance"


def _generate_regions(df, voids_df) -> list[MapRegion]:
    """Auto-generate region labels from dominant axes (numpy masks)."""
    from collections import Counter

    import numpy as np

    if df.empty:
        return []

    x = np.asarray(df["x"], dtype=float)
    y = np.asarray(df["y"], dtype=float)
    dyn = np.asarray(df["dynamics"], dtype=object)
    cred = np.asarray(df["credit"], dtype=object)
    eps = 1e-6  # degenerate bounds (all points coincide) still form one region
    x_min, x_max = float(x.min()) - eps, float(x.max()) + eps
    y_min, y_max = float(y.min()) - eps, float(y.max()) + eps
    total = len(df)

    def _cell_region(i: int, j: int, grid: int) -> MapRegion | None:
        rx_min = x_min + (x_max - x_min) * i / grid
        rx_max = x_min + (x_max - x_min) * (i + 1) / grid
        ry_min = y_min + (y_max - y_min) * j / grid
        ry_max = y_min + (y_max - y_min) * (j + 1) / grid

        mask = (x >= rx_min) & (x < rx_max) & (y >= ry_min) & (y < ry_max)
        count = int(mask.sum())
        if count == 0:
            return None

        dyn_counter = Counter(dyn[mask])
        credit_counter = Counter(cred[mask])
        dom_dyn = dyn_counter.most_common(1)[0][0]
        dom_credit = credit_counter.most_common(1)[0][0]

        return MapRegion(
            name=f"{dom_dyn} × {dom_credit}",
            x_min=rx_min,
            x_max=rx_max,
            y_min=ry_min,
            y_max=ry_max,
            dominant_dynamics=dom_dyn,
            dominant_credit=dom_credit,
            specimen_count=count,
            coverage_pct=100.0 * count / total,
        )

    grid_size = 3
    regions = [
        region
        for i in range(grid_size)
        for j in range(grid_size)
        if (region := _cell_region(i, j, grid_size)) is not None
    ]

    return regions


# Shape encoding for dynamics families (never color-only)
DYNAMICS_SHAPES: dict[str, str] = {
    "EnergyMinimization": "circle",
    "PredictiveSettling": "triangle-up",
    "InstantaneousPass": "square",
    "SpikeIntegration": "diamond",
    "Diffusion": "cross",
    "NullPlasticity": "star",
    "RoutingPlasticity": "hexagram",
    "FastWeightPlasticity": "triangle-down",
    "SubstrateCoupledPlasticity": "bowtie",
    "RuleStatePlasticity": "hourglass",
    "ClosedFormRidgePlasticity": "pentagon",
    "TemporalPsiPlasticity": "hexagon",
}


def get_dynamics_shape(dynamics: str) -> str:
    """Get shape for dynamics family (for shape-redundant encoding)."""
    return DYNAMICS_SHAPES.get(dynamics, "circle")


def get_outcome_style(outcome: str) -> tuple[str, str, str]:
    """Get (icon, color, label) for outcome - shape + color redundant."""
    from computronium.visualization.live_atlas import OutcomeBadge, outcome_style

    badge_map = {
        "learned": OutcomeBadge.LEARNED,
        "marginal": OutcomeBadge.MARGINAL,
        "chance": OutcomeBadge.CHANCE,
        "diverged": OutcomeBadge.DIVERGED,
        "structural_void": OutcomeBadge.VOID,
    }
    badge = badge_map.get(outcome, OutcomeBadge.CHANCE)
    style = outcome_style(badge)
    return style.icon, style.color, style.label
