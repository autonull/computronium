"""Genome Health Tracker (M2.13 → M3) — |Ω| vs fitness, oncological cancer risk, Resource Ceiling headroom."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class GenomeHealthPoint:
    """One genome health measurement."""

    genome_size: int  # |Ω|
    fitness: float
    resource_usage: float
    resource_budget: float
    genome_size_penalty: float  # λ * |Ω|
    timestamp: float


class GenomeHealthTracker(BasePanel):
    """Genome Health: |Ω| vs fitness, oncological cancer risk, Resource Ceiling headroom.

    Visualizes the resource ceiling invariant; selective pressure against
    unbounded growth.
    """

    def __init__(
        self,
        points: list[GenomeHealthPoint] | None = None,
        genome_size_penalty_lambda: float = 0.01,
    ) -> None:
        super().__init__(
            panel_key="genome_health",
            plain_explanation=(
                "This panel shows how recipe size relates to fitness. Bigger "
                "recipes aren't always better — there's a penalty for size "
                "(oncological cancer risk). The resource ceiling limits total "
                "compute + memory."
            ),
            why_explanation=(
                "Unbounded recipe growth wastes resources. The genome size "
                "penalty (λ) creates selective pressure for compact, efficient "
                "recipes. Resource ceiling headroom shows how close you are to "
                "the budget limit."
            ),
            expert_explanation=(
                "Per AUTOTILE.md §5.4: Genome health tracks |Ω| vs fitness "
                "trajectory, oncological cancer risk (GenomeSizePenalty λ), "
                "and Resource Ceiling headroom (||Z||+|Ω| budget). Campaign "
                "event log + ResourceUsage as data sources. The penalty term "
                "λ|Ω| in the fitness function prevents unbounded growth."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/auto-evolve/genome.html",
        )
        self.points = points or []
        self.genome_size_penalty_lambda = genome_size_penalty_lambda

    def add_point(self, point: GenomeHealthPoint) -> None:
        """Add a genome health measurement."""
        self.points.append(point)
        self._refresh()

    def set_points(self, points: list[GenomeHealthPoint]) -> None:
        """Set all genome health points."""
        self.points = points
        self._refresh()

    def render(self) -> ui.element:
        """Render the genome health tracker."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("genome_health")

            if not self.points:
                ui.label("No genome health data — run a campaign first.").classes(
                    "text-grey"
                )
                return panel

            # Summary stats
            latest = self.points[-1]
            headroom = latest.resource_budget - latest.resource_usage
            headroom_pct = (
                (headroom / latest.resource_budget * 100)
                if latest.resource_budget > 0
                else 0
            )

            with ui.row().classes("w-full gap-4 mb-4"):
                self._stat_card(
                    "Genome Size (|Ω|)", latest.genome_size, ICONS["genome"]
                )
                self._stat_card("Fitness", f"{latest.fitness:.3f}", ICONS["record"])
                self._stat_card(
                    "Resource Usage",
                    f"{latest.resource_usage:.0f} / {latest.resource_budget:.0f}",
                    ICONS["cost"],
                )
                self._stat_card(
                    "Headroom",
                    f"{headroom_pct:.0f}%",
                    ICONS["success"] if headroom_pct > 20 else ICONS["warning"],
                )

            # Oncological cancer risk
            penalty = latest.genome_size * self.genome_size_penalty_lambda
            risk_level = (
                "High"
                if penalty > latest.fitness * 0.5
                else "Moderate"
                if penalty > latest.fitness * 0.1
                else "Low"
            )
            risk_color = (
                "negative"
                if risk_level == "High"
                else "warning"
                if risk_level == "Moderate"
                else "positive"
            )

            with (
                ui.card().classes("w-full mb-4").props("flat bordered"),
                ui.row().classes("w-full items-center gap-4"),
            ):
                ui.icon(ICONS["mutation"]).classes("text-2xl text-primary")
                with ui.column().classes("flex-1"):
                    ui.label("Oncological Cancer Risk").classes("text-h6")
                    ui.label(
                        f"GenomeSizePenalty λ={self.genome_size_penalty_lambda}: "
                        f"|Ω|×λ = {penalty:.3f} (fitness={latest.fitness:.3f})"
                    ).classes("text-body")
                    ui.badge(risk_level, color=risk_color).classes("text-caption")

            # Fitness vs Genome Size chart (using echart)
            self._render_fitness_chart()

            # Resource ceiling headroom over time
            if len(self.points) > 1:
                self._render_headroom_chart()

        return panel

    def _render_fitness_chart(self) -> None:
        """Render fitness vs genome size chart."""
        # Prepare data for echart
        x_data = [str(p.genome_size) for p in self.points]
        fitness_data = [p.fitness for p in self.points]
        penalty_data = [
            p.genome_size * self.genome_size_penalty_lambda for p in self.points
        ]
        net_fitness = [f - p for f, p in zip(fitness_data, penalty_data)]

        option = {
            "title": {"text": "Fitness vs Genome Size", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {
                "data": ["Raw Fitness", "Size Penalty", "Net Fitness"],
                "top": "30px",
            },
            "xAxis": {"type": "category", "data": x_data, "name": "Genome Size |Ω|"},
            "yAxis": {"type": "value", "name": "Fitness"},
            "series": [
                {
                    "name": "Raw Fitness",
                    "type": "line",
                    "data": fitness_data,
                    "showSymbol": True,
                },
                {
                    "name": "Size Penalty (λ|Ω|)",
                    "type": "line",
                    "data": penalty_data,
                    "showSymbol": True,
                },
                {
                    "name": "Net Fitness",
                    "type": "line",
                    "data": net_fitness,
                    "showSymbol": True,
                    "lineStyle": {"width": 3},
                },
            ],
            "grid": {"top": "60px", "bottom": "40px", "left": "60px", "right": "20px"},
        }
        ui.echart(option).classes("w-full h-[300px]")

    def _render_headroom_chart(self) -> None:
        """Render resource ceiling headroom over time."""
        timestamps = [p.timestamp for p in self.points]
        usage = [p.resource_usage for p in self.points]
        budget = [p.resource_budget for p in self.points]
        headroom = [b - u for b, u in zip(budget, usage)]
        headroom_pct = [(h / b * 100) if b > 0 else 0 for h, b in zip(headroom, budget)]

        option = {
            "title": {"text": "Resource Ceiling Headroom Over Time", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "legend": {"data": ["Usage", "Budget", "Headroom %"], "top": "30px"},
            "xAxis": {
                "type": "category",
                "data": [self._format_time(t) for t in timestamps],
                "name": "Time",
            },
            "yAxis": [
                {"type": "value", "name": "Resources", "position": "left"},
                {
                    "type": "value",
                    "name": "Headroom %",
                    "position": "right",
                    "max": 100,
                },
            ],
            "series": [
                {
                    "name": "Usage",
                    "type": "line",
                    "yAxisIndex": 0,
                    "data": usage,
                    "showSymbol": True,
                },
                {
                    "name": "Budget",
                    "type": "line",
                    "yAxisIndex": 0,
                    "data": budget,
                    "showSymbol": True,
                    "lineStyle": {"type": "dashed"},
                },
                {
                    "name": "Headroom %",
                    "type": "line",
                    "yAxisIndex": 1,
                    "data": headroom_pct,
                    "showSymbol": True,
                    "color": "#1e7e34",
                },
            ],
            "grid": {"top": "60px", "bottom": "40px", "left": "60px", "right": "60px"},
        }
        ui.echart(option).classes("w-full h-[300px]")

    def _stat_card(self, label: str, value: Any, icon: str) -> ui.element:
        with ui.card().classes("flex-1 min-w-[150px]").props("flat bordered") as card:
            ui.icon(icon).classes("text-2xl text-primary")
            ui.label(str(value)).classes("text-h4 text-bold")
            ui.label(label).classes("text-caption text-grey")
        return card

    def _format_time(self, timestamp: float) -> str:
        import time

        return time.strftime("%H:%M:%S", time.localtime(timestamp))

    def _refresh(self) -> None:
        """Refresh on mode change."""


def create_genome_health_tracker(
    points: list[GenomeHealthPoint] | None = None,
    genome_size_penalty_lambda: float = 0.01,
) -> GenomeHealthTracker:
    """Create the genome health tracker component."""
    return GenomeHealthTracker(
        points=points, genome_size_penalty_lambda=genome_size_penalty_lambda
    )
