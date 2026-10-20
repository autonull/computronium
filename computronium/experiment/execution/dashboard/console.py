"""Minimal Console Dashboard for Debugging (TODO68).

Text-based live monitoring dashboard using rich for terminal UI.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Container, Mapping, Sequence

    from computronium.experiment.execution.campaign_queue import CampaignQueue
    from computronium.experiment.schema.record import Record

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from computronium.experiment.evidence.serializers import serializer
from computronium.experiment.schema.axis import StructuralAxis

logger = logging.getLogger(__name__)

# The axes the console shows, as a slice of the declared space: three free,
# the rest held at the value the run used.
FREE_AXES = (
    StructuralAxis.CREDIT,
    StructuralAxis.GEOMETRY,
    StructuralAxis.DYNAMICS,
)

# The marks the space is drawn with: what the run measured, what the system
# would measure and nobody has, and what the system refuses.
MARK_MEASURED = "█"
MARK_LEGAL = "·"
MARK_VOID = "×"


def measured_keys(records: Sequence[Record], axes: Sequence[str]) -> set[str]:
    """The cells the run measured, in the grid's own key form.

    The key is the cell's values on the axes the grid shows, joined the way
    the grid joins them, so a measured cell can be found among the space's
    cells without a second convention for naming one.
    """
    return {
        "|".join(str(getattr(record, axis, "")) for axis in axes) for record in records
    }


def _marks(
    space: Mapping[str, Any], measured: Container[str]
) -> dict[tuple[str, str, str], tuple[str, str]]:
    """What each cell of the space is: refused, measured, or a gap."""
    axes = list(space.get("axes", []))
    if len(axes) < 3:
        return {}
    x_axis, y_axis, z_axis = axes[0], axes[1], axes[2]

    marks: dict[tuple[str, str, str], tuple[str, str]] = {}
    for cell in space.get("cells", []):
        coordinate = cell.get("coordinate", {})
        key = (
            str(coordinate.get(x_axis, "")),
            str(coordinate.get(y_axis, "")),
            str(coordinate.get(z_axis, "")),
        )
        if cell.get("status") == "void":
            marks[key] = (MARK_VOID, "red")
        elif "|".join(key) in measured:
            marks[key] = (MARK_MEASURED, "green")
        else:
            marks[key] = (MARK_LEGAL, "yellow")
    return marks


def space_grid(space: Mapping[str, Any], measured: Container[str] = ()) -> Text:
    """Draw the declared space as a grid of marks.

    One block per value of the third axis, so a slice that holds several
    values is drawn in full rather than collapsed. The rows are the second
    axis, the columns the first, and every cell says what the system thinks
    of it — and whether the run has been there.
    """
    text = Text()
    axes: list[str] = list(space.get("axes", []))
    values: Mapping[str, list[str]] = space.get("values", {})
    if len(axes) < 3:
        return Text("the space names no axes", style="dim")

    x_axis, y_axis, z_axis = axes[0], axes[1], axes[2]
    x_values = list(values.get(x_axis, []))
    y_values = list(values.get(y_axis, []))
    z_values = list(values.get(z_axis, []))
    marks = _marks(space, measured)

    width = max((len(str(value)) for value in x_values), default=6) + 2
    for z_value in z_values:
        text.append(f"{z_axis}={z_value}\n", style="bold cyan")
        text.append(" " * 14)
        for x_value in x_values:
            text.append(str(x_value)[:width].ljust(width), style="dim")
        text.append("\n")
        for y_value in y_values:
            text.append(str(y_value)[:14].ljust(14), style="dim")
            for x_value in x_values:
                mark, style = marks.get(
                    (x_value, y_value, z_value),
                    (MARK_VOID, "dim"),
                )
                text.append(mark.ljust(width - 1), style=style)
            text.append("\n")
        text.append("\n")

    return text


@dataclass(frozen=True, slots=True)
class ConsoleDashboardConfig:
    """Configuration for the console dashboard."""

    store_path: str | None = None
    campaign_queue: CampaignQueue | None = None
    update_interval: float = 2.0


class ConsoleDashboard:
    """Console-based live monitoring dashboard.

    Provides real-time visibility into:
    - Campaign queue status
    - Resource utilization
    - Campaign metrics (Pareto, ablation, variability)
    - Recent records
    """

    def __init__(self, config: ConsoleDashboardConfig | None = None) -> None:
        self.config = config or ConsoleDashboardConfig()
        self.console = Console()
        self._running = False
        self._update_task: asyncio.Task | None = None
        self._latest_metrics: dict[str, any] = {}
        self._latest_queue: dict[str, any] = {}
        self._latest_resources: dict[str, any] = {}
        self._latest_space: dict[str, Any] | None = None
        self._latest_measured: set[str] = set()
        self._store_source = "none"

    def _make_layout(self) -> Layout:
        """Create the dashboard layout."""
        layout = Layout(name="root")

        layout.split(
            Layout(name="header", size=3),
            Layout(name="space", size=10),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )

        layout["main"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=1),
        )

        layout["left"].split(
            Layout(name="queue", ratio=1),
            Layout(name="metrics", ratio=2),
        )

        layout["right"].split(
            Layout(name="resources", ratio=1),
            Layout(name="records", ratio=2),
        )

        return layout

    def _render_header(self) -> Panel:
        """Render the header panel."""
        time_str = datetime.now().strftime("%H:%M:%S")
        title = Text("🖥️  Computronium Console Dashboard", style="bold cyan")
        subtitle = Text(f"Last update: {time_str}", style="dim")
        return Panel.fit(title + "\n" + subtitle, border_style="cyan")

    def _render_footer(self) -> Panel:
        """Render the footer panel."""
        status = "🟢 LIVE" if self._running else "🔴 STOPPED"
        store = Path(self.config.store_path).name if self.config.store_path else "none"
        queue_status = f"Queue: {self._latest_queue.get('queued', 0)} queued, {self._latest_queue.get('running', 0)} running"
        return Panel.fit(
            Text(
                f"{status} | Store: {store} ({self._store_source}) | {queue_status}",
                style="dim",
            ),
            border_style="dim",
        )

    def _render_space(self) -> Panel:
        """Render the declared space: what was measured, what is a gap, what is refused."""
        space = self._latest_space
        if not space:
            return Panel(
                Text("No declared space yet", style="dim"),
                title="🌌 Declared Space",
                border_style="blue",
            )

        counts = space.get("counts", {})
        rules = space.get("void_rules", {})
        refused = ", ".join(
            f"{rule.replace('_', ' ')} ({count})"
            for rule, count in sorted(rules.items(), key=lambda item: -item[1])[:3]
        )
        held = space.get("held", {})

        content = Text()
        content.append_text(space_grid(space, self._latest_measured))
        content.append(
            f"measured █ · legal gap · void ×   "
            f"({counts.get('legal', 0)} gaps, {counts.get('void', 0)} refused)\n",
            style="dim",
        )
        if held:
            content.append(
                "held: "
                + " · ".join(f"{axis}={value}" for axis, value in held.items()),
                style="dim",
            )
        if refused:
            content.append(f"\nrefused by: {refused}", style="dim red")

        return Panel(content, title="🌌 Declared Space", border_style="blue")

    def _render_queue(self) -> Panel:
        """Render the queue status panel."""
        table = Table(show_header=True, header_style="bold", box=None)
        table.add_column("Status", style="cyan", width=12)
        table.add_column("Count", justify="right", style="white")
        table.add_column("Details", style="dim")

        queued = self._latest_queue.get("queued", 0)
        running = self._latest_queue.get("running", 0)
        completed = self._latest_queue.get("completed", 0)
        max_concurrent = self._latest_queue.get("max_concurrent", 0)

        table.add_row("⏳ Queued", str(queued), "waiting for resources")
        table.add_row("🟢 Running", str(running), f"/ {max_concurrent} max concurrent")
        table.add_row("✅ Completed", str(completed), "finished campaigns")

        if self.config.campaign_queue:
            campaigns = self._latest_queue.get("campaigns", [])
            for c in campaigns[:5]:  # show top 5
                status_icon = {
                    "queued": "⏳",
                    "running": "🟢",
                    "completed": "✅",
                    "failed": "❌",
                }.get(c.get("status", ""), "?")
                table.add_row(
                    f"  {status_icon} {c.get('name', 'unknown')[:20]}",
                    c.get("status", "")[:10],
                    c.get("campaign_id", "")[:8],
                )

        return Panel(table, title="📋 Campaign Queue", border_style="blue")

    def _render_resources(self) -> Panel:
        """Render the resource utilization panel."""
        table = Table(show_header=True, header_style="bold", box=None)
        table.add_column("Resource", style="cyan", width=10)
        table.add_column("Usage", justify="right", style="white")
        table.add_column("Bar", width=20)

        gpu = self._latest_resources.get("gpu_utilization", 0)
        cpu = self._latest_resources.get("cpu_utilization", 0)
        mem = self._latest_resources.get("memory_utilization", 0)

        def bar(pct: float) -> str:
            filled = int(pct * 10)
            return "█" * filled + "░" * (10 - filled)

        table.add_row("GPU", f"{gpu * 100:.0f}%", bar(gpu))
        table.add_row("CPU", f"{cpu * 100:.0f}%", bar(cpu))
        table.add_row("MEM", f"{mem * 100:.0f}%", bar(mem))

        used_gpus = self._latest_resources.get("used_gpus", 0)
        max_gpus = self._latest_resources.get("max_gpus", 0)
        table.add_row("", "", f"GPUs: {used_gpus}/{max_gpus}")

        return Panel(table, title="📊 Resources", border_style="green")

    def _render_metrics(self) -> Panel:
        """Render the metrics panel (Pareto, ablation, variability)."""
        lines = []

        # Pareto info
        pareto_count = self._latest_metrics.get("pareto_count", 0)
        total_records = self._latest_metrics.get("total_records", 0)
        lines.append(
            Text(
                f"📈 Pareto Frontier: {pareto_count}/{total_records} records",
                style="bold yellow",
            )
        )

        # Best record
        best = self._latest_metrics.get("best_record")
        if best:
            acc = best.get("payload", {}).get("val_acc", 0)
            arm = best.get("coordinate", {}).get("credit", "unknown")
            lines.append(Text(f"  Best: {acc:.3f} ({arm})", style="green"))

        lines.append(Text(""))

        # Ablation summary
        ablation = self._latest_metrics.get("ablation_groups", [])
        if ablation:
            lines.append(Text("🔬 Ablation (credit arm):", style="bold magenta"))
            for group in ablation[:3]:
                metric = group.get("metrics", [{}])[0]
                for arm_data in metric.get("arms", [])[:4]:
                    val = arm_data.get("mean", 0)
                    std = arm_data.get("std", 0)
                    name = arm_data.get("value", "?")[:12]
                    at_chance = arm_data.get("at_chance", False)
                    style = "red" if at_chance else ("yellow" if val < 0.2 else "green")
                    lines.append(Text(f"  {name}: {val:.3f}±{std:.3f}", style=style))

        lines.append(Text(""))

        # Variability
        records = self._latest_metrics.get("records", [])
        if records:
            by_arm: dict[str, list[float]] = {}
            for r in records:
                arm = r.get("coordinate", {}).get("credit", "?")
                acc = r.get("payload", {}).get("val_acc")
                if acc is not None:
                    by_arm.setdefault(arm, []).append(acc)

            lines.append(Text("📊 Seed Variability:", style="bold blue"))
            for arm, values in list(by_arm.items())[:4]:
                if values:
                    mean = sum(values) / len(values)
                    std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
                    lines.append(
                        Text(
                            f"  {arm[:12]}: {mean:.3f}±{std:.3f} (n={len(values)})",
                            style="cyan",
                        )
                    )

        content = Text().join(lines) if lines else Text("No metrics yet", style="dim")
        return Panel(content, title="📈 Metrics", border_style="yellow")

    def _render_records(self) -> Panel:
        """Render the recent records panel."""
        records = self._latest_metrics.get("records", [])
        if not records:
            return Panel(
                Text("No records yet", style="dim"),
                title="📝 Recent Records",
                border_style="magenta",
            )

        table = Table(show_header=True, header_style="bold", box=None)
        table.add_column("Arm", style="cyan", width=14)
        table.add_column("Val Acc", justify="right", style="white", width=8)
        table.add_column("Time", justify="right", style="dim", width=8)
        table.add_column("Params", justify="right", style="dim", width=8)
        table.add_column("Pareto", justify="center", width=6)

        # Sort by val_acc descending
        sorted_records = sorted(
            records,
            key=lambda r: r.get("payload", {}).get("val_acc", 0),
            reverse=True,
        )

        pareto_flags = self._latest_metrics.get("pareto", [])

        for i, r in enumerate(sorted_records[:10]):
            coord = r.get("coordinate", {})
            payload = r.get("payload", {})
            arm = coord.get("credit", "?")[:12]
            acc = payload.get("val_acc", 0)
            wt = payload.get("walltime_s", 0)
            params = payload.get("param_count", 0)
            is_pareto = pareto_flags[i] if i < len(pareto_flags) else False

            table.add_row(
                arm,
                f"{acc:.3f}",
                f"{wt:.1f}s",
                f"{params / 1000:.1f}K",
                "⭐" if is_pareto else "",
            )

        return Panel(table, title="📝 Top Records", border_style="magenta")

    def _declared_space(self, run: Any, records: list[Any]) -> dict[str, Any] | None:
        """The declared space the run's evidence sits in.

        The same space the browser draws, read through the same rules: a gap
        the console cannot show is a gap a researcher cannot act on.
        """
        from computronium.experiment.execution.dashboard.space import declared_space

        spec = getattr(run, "spec", None)
        task = spec.task_names[0] if spec and spec.task_names else None
        if not task and records:
            task = records[0].schedule.task_id or None
        try:
            return declared_space(spec, records, FREE_AXES, task=task)
        except Exception as exc:  # ruff: ignore[blind-except] - the space is a convenience
            logger.debug("The declared space could not be read: %s", exc)
            return None

    async def _update_loop(self) -> None:
        """Background loop to fetch updates."""
        while self._running:
            try:
                await asyncio.sleep(self.config.update_interval)
                if not self._running:
                    break

                # Fetch queue status
                if self.config.campaign_queue:
                    queue = self.config.campaign_queue
                    self._latest_queue = {
                        "max_concurrent": queue.max_concurrent,
                        "queued": len(queue._queue),
                        "running": len(queue._running),
                        "completed": len(queue._completed),
                        "resource_usage": await queue.get_resource_usage(),
                    }

                # Fetch resource usage
                if self.config.campaign_queue:
                    self._latest_resources = (
                        await self.config.campaign_queue.get_resource_usage()
                    )

                # Fetch campaign metrics from store
                if self.config.store_path:
                    try:
                        from computronium.experiment.evidence.mirror import (
                            readable_store,
                        )

                        with readable_store(Path(self.config.store_path)) as view:
                            self._store_source = view.source
                            store = view.store
                            runs = list(store.query_runs())
                            if runs:
                                # Get most recent run with records
                                for run in reversed(runs):
                                    records = list(
                                        store.query_records(run_id=run.run_id)
                                    )
                                    if records:
                                        # Compute Pareto
                                        from computronium.experiment.analysis import (
                                            compute_pareto_frontier,
                                        )

                                        pareto_points, _ = compute_pareto_frontier(
                                            records, ["val_acc", "walltime_s"]
                                        )
                                        pareto_ids = {
                                            p["record_id"] for p in pareto_points
                                        }

                                        # Get ablation groups
                                        from computronium.experiment.surface.report import (
                                            ReportGenerator,
                                        )

                                        generator = ReportGenerator(store)
                                        ablation_groups = generator.get_ablation_groups(
                                            run.run_id
                                        )

                                        self._latest_metrics = {
                                            "total_records": len(records),
                                            "pareto_count": len(pareto_ids),
                                            "pareto": [
                                                r.record_id in pareto_ids
                                                for r in records
                                            ],
                                            "records": [
                                                serializer.to_api_dict(r)
                                                for r in records
                                            ],
                                            "ablation_groups": ablation_groups,
                                            # The panel reads the record the way
                                            # the API serves it: a mapping, not
                                            # a record object.
                                            "best_record": serializer.to_api_dict(
                                                max(
                                                    records,
                                                    key=lambda r: r.payload.get(
                                                        "val_acc", 0
                                                    ),
                                                )
                                            )
                                            if records
                                            else None,
                                        }
                                        self._latest_space = self._declared_space(
                                            run, records
                                        )
                                        self._latest_measured = measured_keys(
                                            records, FREE_AXES
                                        )
                                        break
                    except Exception as e:
                        logger.debug(f"Error fetching metrics: {e}")

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in console dashboard update loop")
                await asyncio.sleep(5)

    def _render(self, layout: Layout) -> Layout:
        """Render all panels into the layout."""
        layout["header"].update(self._render_header())
        layout["footer"].update(self._render_footer())
        layout["space"].update(self._render_space())
        layout["queue"].update(self._render_queue())
        layout["resources"].update(self._render_resources())
        layout["metrics"].update(self._render_metrics())
        layout["records"].update(self._render_records())
        return layout

    async def run(self) -> None:
        """Run the console dashboard (blocking)."""
        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())

        layout = self._make_layout()

        try:
            with Live(
                self._render(layout),
                console=self.console,
                refresh_per_second=4,
                screen=True,
            ) as live:
                while self._running:
                    await asyncio.sleep(self.config.update_interval)
                    live.update(self._render(layout))
        except KeyboardInterrupt:
            pass
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the dashboard."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass


async def run_console_dashboard(
    store_path: str | None = None,
    campaign_queue: CampaignQueue | None = None,
    update_interval: float = 2.0,
) -> None:
    """Convenience function to run the console dashboard."""
    config = ConsoleDashboardConfig(
        store_path=store_path,
        campaign_queue=campaign_queue,
        update_interval=update_interval,
    )
    dashboard = ConsoleDashboard(config)
    await dashboard.run()
