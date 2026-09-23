"""Lineage Viewer component (M1.13) — Ω phylogeny from comp scientist phylogeny."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class LineageNode:
    """A node in the lineage graph (a genome)."""

    genome_id: str
    tier: int  # 1=structural, 2=algorithmic, 3=meta
    fitness: float
    episode: int
    parent_id: str | None
    mutation_type: str | None = None
    slope: float = 0.0


@dataclass(frozen=True, slots=True)
class LineageEdge:
    """An edge in the lineage graph (a mutation)."""

    from_genome: str
    to_genome: str
    mutation_type: str
    slope: float
    accepted: bool


class LineageViewer(BasePanel):
    """Lineage Viewer: visualize Ω phylogeny from comp scientist phylogeny."""

    TIER_COLORS: ClassVar[dict[int, str]] = {
        1: "#1f77b4",  # structural - blue
        2: "#ff7f0e",  # algorithmic - orange
        3: "#2ca02c",  # meta - green
    }
    TIER_LABELS: ClassVar[dict[int, str]] = {
        1: "Structural",
        2: "Algorithmic",
        3: "Meta",
    }

    def __init__(
        self,
        *,
        nodes: list[LineageNode] | None = None,
        edges: list[LineageEdge] | None = None,
    ) -> None:
        super().__init__(
            panel_key="lineage_viewer",
            plain_explanation=(
                "This is the recipe family tree. Each node is a recipe (genome). "
                "Lines show mutations. Colors show the type of change."
            ),
            why_explanation=(
                "The lineage shows which mutations survived selection and why. "
                "Slope values show the learning speed improvement."
            ),
            expert_explanation=(
                "Reconstructs identical graph from event log replay (UX-L10). "
                "Nodes = genomes from comp scientist phylogeny. "
                "Edges = mutations (DuplicateAndPerturb, SpliceOperator, CoordinateSwap). "
                "Tier colors: 1=structural, 2=algorithmic, 3=meta. "
                "Tooltips show adaptation probe slope."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/lineage.html",
        )
        self.nodes = nodes or []
        self.edges = edges or []
        self._graph_container: ui.element = ui.column().classes("w-full")

    def render(self) -> ui.element:
        """Render the Lineage Viewer."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("lineage_viewer")

            # Legend
            with ui.row().classes("w-full gap-4 flex-wrap"):
                for tier in [1, 2, 3]:
                    with ui.row().classes("items-center gap-1"):
                        ui.icon(ICONS["info"]).classes("text-sm").style(
                            f"color: {self.TIER_COLORS[tier]}"
                        )
                        ui.label(self.TIER_LABELS[tier]).classes("text-sm text-grey")

            # Graph container
            self._graph_container = ui.column().classes("w-full")
            with self._graph_container:
                self._render_graph()

        return panel

    def _render_graph(self) -> None:
        """Render the lineage graph (using mermaid or custom SVG)."""
        self._graph_container.clear()
        with self._graph_container:
            if not self.nodes:
                ui.label(self.tr("no_lineage_data")).classes(
                    "text-grey text-center p-8"
                )
                return

            # For now, render as a table with hierarchy
            # In production, this would use mermaid.js or a custom D3 visualization
            with ui.card().classes("w-full").props("flat"):
                ui.label(self.tr("phylogeny_table")).classes("text-bold mb-2")

                rows = []
                for node in self.nodes:
                    tier_label = self.TIER_LABELS.get(node.tier, "Unknown")
                    parent = node.parent_id or "—"
                    rows.append({
                        "genome": node.genome_id,
                        "tier": f"{tier_label} ({node.tier})",
                        "fitness": f"{node.fitness:.3f}",
                        "episode": str(node.episode),
                        "parent": parent,
                        "mutation": node.mutation_type or "—",
                        "slope": f"{node.slope:.3f}",
                    })

                columns = [
                    {
                        "name": "genome",
                        "label": self.tr("genome_id"),
                        "field": "genome",
                        "sortable": True,
                    },
                    {
                        "name": "tier",
                        "label": self.tr("tier"),
                        "field": "tier",
                        "sortable": True,
                    },
                    {
                        "name": "fitness",
                        "label": self.tr("fitness"),
                        "field": "fitness",
                        "sortable": True,
                    },
                    {
                        "name": "episode",
                        "label": self.tr("episode"),
                        "field": "episode",
                        "sortable": True,
                    },
                    {
                        "name": "parent",
                        "label": self.tr("parent"),
                        "field": "parent",
                        "sortable": True,
                    },
                    {
                        "name": "mutation",
                        "label": self.tr("mutation_type"),
                        "field": "mutation",
                        "sortable": True,
                    },
                    {
                        "name": "slope",
                        "label": self.tr("slope"),
                        "field": "slope",
                        "sortable": True,
                    },
                ]

                ui.table(rows=rows, columns=columns, row_key="genome").classes(
                    "w-full"
                ).props("dense flat bordered")

    def update_data(
        self,
        data: object | None = None,
        *,
        nodes: list[LineageNode] | None = None,
        edges: list[LineageEdge] | None = None,
    ) -> None:
        """Update lineage data."""
        if nodes is None and data is not None:
            nodes = list(data.nodes)  # type: ignore[attr-defined]
            edges = list(data.edges)  # type: ignore[attr-defined]
        if nodes is not None:
            self.nodes = nodes
        if edges is not None:
            self.edges = edges
        self._render_graph()

    def _refresh(self) -> None:
        """Refresh on mode change."""
        self._render_graph()


def create_lineage_from_phylogeny(
    phylogeny_output: str,
) -> tuple[list[LineageNode], list[LineageEdge]]:
    """Parse comp scientist phylogeny output into nodes and edges.

    This is a placeholder - actual implementation would parse the phylogeny JSON.
    """
    # Placeholder implementation
    return [], []
