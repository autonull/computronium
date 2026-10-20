"""Minimal Console Dashboard for Debugging (TODO68).

Text-based live monitoring dashboard using rich for terminal UI.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.execution.campaign_queue import CampaignQueue

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from computronium.experiment.evidence.serializers import serializer
from computronium.experiment.evidence.store import RecordStore, StoreConfig

logger = logging.getLogger(__name__)


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

    def _make_layout(self) -> Layout:
        """Create the dashboard layout."""
        layout = Layout(name="root")

        layout.split(
            Layout(name="header", size=3),
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
            Text(f"{status} | Store: {store} | {queue_status}", style="dim"),
            border_style="dim",
        )

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

        table.add_row("⏳ Queued", str(queued), f"waiting for resources")
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

        table.add_row("GPU", f"{gpu*100:.0f}%", bar(gpu))
        table.add_row("CPU", f"{cpu*100:.0f}%", bar(cpu))
        table.add_row("MEM", f"{mem*100:.0f}%", bar(mem))

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
        lines.append(Text(f"📈 Pareto Frontier: {pareto_count}/{total_records} records", style="bold yellow"))

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
                    lines.append(Text(f"  {arm[:12]}: {mean:.3f}±{std:.3f} (n={len(values)})", style="cyan"))

        content = Text().join(lines) if lines else Text("No metrics yet", style="dim")
        return Panel(content, title="📈 Metrics", border_style="yellow")

    def _render_records(self) -> Panel:
        """Render the recent records panel."""
        records = self._latest_metrics.get("records", [])
        if not records:
            return Panel(Text("No records yet", style="dim"), title="📝 Recent Records", border_style="magenta")

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
                f"{params/1000:.1f}K",
                "⭐" if is_pareto else "",
            )

        return Panel(table, title="📝 Top Records", border_style="magenta")

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
                    self._latest_resources = await self.config.campaign_queue.get_resource_usage()

                # Fetch campaign metrics from store
                if self.config.store_path:
                    try:
                        store = RecordStore(StoreConfig(path=Path(self.config.store_path), read_only=True))
                        with store:
                            runs = list(store.query_runs())
                            if runs:
                                # Get most recent run with records
                                for run in reversed(runs):
                                    records = list(store.query_records(run_id=run.run_id))
                                    if records:
                                        # Compute Pareto
                                        from computronium.experiment.analysis import compute_pareto_frontier

                                        pareto_points, _ = compute_pareto_frontier(records, ["val_acc", "walltime_s"])
                                        pareto_ids = {p["record_id"] for p in pareto_points}

                                        # Get ablation groups
                                        from computronium.experiment.surface.report import ReportGenerator
                                        generator = ReportGenerator(store)
                                        ablation_groups = generator.get_ablation_groups(run.run_id)

                                        self._latest_metrics = {
                                            "total_records": len(records),
                                            "pareto_count": len(pareto_ids),
                                            "pareto": [r.record_id in pareto_ids for r in records],
                                            "records": [serializer.to_api_dict(r) for r in records],
                                            "ablation_groups": ablation_groups,
                                            "best_record": max(records, key=lambda r: r.payload.get("val_acc", 0))
                                            if records
                                            else None,
                                        }
                                        break
                    except Exception as e:
                        logger.debug(f"Error fetching metrics: {e}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception("Error in console dashboard update loop")
                await asyncio.sleep(5)

    def _render(self, layout: Layout) -> Layout:
        """Render all panels into the layout."""
        layout["header"].update(self._render_header())
        layout["footer"].update(self._render_footer())
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
            with Live(self._render(layout), console=self.console, refresh_per_second=4, screen=True) as live:
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