"""Repair Bench component (M1.6) — defect funnel with statuses and copy buttons.

Lenses: Defects (table), Maturation (tree: campaign → maturity → cells).
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS, MAX_RENDERED_ROWS
from computronium.ui.mode_toggle import BasePanel

if TYPE_CHECKING:
    from pathlib import Path

    from computronium.autoscientist.defects import DefectRecord


@dataclass(frozen=True, slots=True)
class DefectRow:
    """A row in the repair bench."""

    defect_id: str
    count: int
    cells: int
    status: str  # "open" | "fixed" | "back_in_service"
    error_class: str
    last_seen: float
    message: str


@dataclass(frozen=True, slots=True)
class MaturationNode:
    """A node in the maturation tree."""

    level: str  # "l0" | "l1" | "l2"
    campaign: str
    cells: list[str]  # cell keys at this maturity level
    count: int


class RepairBench(BasePanel):
    """Repair Bench panel: defect funnel with reframed statuses and copy buttons.

    Lenses:
    - Defects: defect funnel table with copy commands
    - Maturation: campaign → maturity → cells tree
    """

    def __init__(
        self,
        *,
        rows: list[DefectRow] | None = None,
        maturation_nodes: list[MaturationNode] | None = None,
    ) -> None:
        super().__init__(
            panel_key="repair_bench",
            plain_explanation=(
                "This panel shows crashes that need fixing. Each row is a unique defect. "
                "Click 'Copy' to get the unquarantine command."
            ),
            why_explanation=(
                "Defects are crashes we can fix (not ontology boundaries). "
                "Fixing them lets the campaign continue exploring."
            ),
            expert_explanation=(
                "Defect funnel from live_atlas.defect_funnel_rows(). "
                "Statuses: open → fixed → back_in_service. "
                "Structural voids (gate-rejected) never appear here. "
                "Copy button generates: `comp unquarantine --root ROOT --defect-id ID`"
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/repair.html",
        )
        self.rows = rows or []
        self.maturation_nodes = maturation_nodes or []

        # Lens state
        self._active_lens = "defects"  # "defects" | "maturation"
        self._lens_tabs: Any = None
        self._tab_defects: Any = None
        self._tab_maturation: Any = None
        self._lens_containers: dict[str, ui.element] = {}

    def render(self) -> ui.element:
        """Render the Repair Bench panel with lens tabs."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("repair")

            # Lens tabs
            with ui.tabs().classes("w-full") as tabs:
                self._tab_defects = ui.tab(
                    "Defects", icon=ICONS.get("defects", "bug_report")
                )
                self._tab_maturation = ui.tab(
                    "Maturation", icon=ICONS.get("maturation", "account_tree")
                )

            self._lens_tabs = tabs

            with ui.tab_panels(
                tabs, value=self._get_tab_for_lens(self._active_lens)
            ).classes("w-full"):
                # Defects lens
                with ui.tab_panel(self._tab_defects):
                    self._lens_containers["defects"] = ui.column().classes("w-full")
                    with self._lens_containers["defects"]:
                        self._render_defects_lens()

                # Maturation lens
                with ui.tab_panel(self._tab_maturation):
                    self._lens_containers["maturation"] = ui.column().classes("w-full")
                    with self._lens_containers["maturation"]:
                        self._render_maturation_lens()

        return panel

    def _get_tab_for_lens(self, lens: str) -> Any:
        """Get the tab element for a lens."""
        tab_map = {
            "defects": getattr(self, "_tab_defects", None),
            "maturation": getattr(self, "_tab_maturation", None),
        }
        return tab_map.get(lens)

    def _render_defects_lens(self) -> None:
        """Render the Defects lens (table)."""
        if not self.rows:
            ui.label(self.tr("no_defects")).classes("text-grey text-center p-4")
            return

        total = len(self.rows)
        for row in self.rows[:MAX_RENDERED_ROWS]:
            self._render_defect_row(row)
        if total > MAX_RENDERED_ROWS:
            ui.label(
                f"{self.tr('showing_first')}: {MAX_RENDERED_ROWS} / {total}"
            ).classes("text-caption text-grey")

    def _render_maturation_lens(self) -> None:
        """Render the Maturation lens (tree: campaign → maturity → cells)."""
        if not self.maturation_nodes:
            ui.label(
                "No maturation data yet. Campaigns need to progress through maturity gates."
            ).classes("text-grey text-center p-8")
            return

        # Group by campaign
        from collections import defaultdict

        campaigns: dict[str, list[MaturationNode]] = defaultdict(list)
        for node in self.maturation_nodes:
            campaigns[node.campaign].append(node)

        with ui.column().classes("w-full gap-4"):
            for campaign, nodes in campaigns.items():
                with ui.card().classes("w-full").props("flat"):
                    ui.label(campaign).classes("text-bold text-lg mb-2")
                    # Sort by level: l0, l1, l2
                    level_order = {"l0": 0, "l1": 1, "l2": 2}
                    nodes_sorted = sorted(
                        nodes, key=lambda n: level_order.get(n.level, 99)
                    )
                    for node in nodes_sorted:
                        self._render_maturation_node(node)

    def _render_maturation_node(self, node: MaturationNode) -> None:
        """Render a single maturation tree node."""
        level_labels = {
            "l0": "L0 — Mapping fidelity (1 epoch, 1 seed)",
            "l1": "L1 — Promoted (3 epochs)",
            "l2": "L2 — Claim-grade (10 epochs, 3 seeds)",
        }
        level_colors = {
            "l0": "primary",
            "l1": "warning",
            "l2": "positive",
        }
        label = level_labels.get(node.level, node.level)
        color = level_colors.get(node.level, "grey")

        with ui.row().classes("w-full items-center gap-4 pl-4"):
            ui.icon("chevron_right").classes(f"text-{color}")
            ui.badge(label, color=color).classes("text-sm")
            ui.label(f"{node.count} cells").classes("text-sm text-grey")
            if node.cells:
                with ui.expansion("Cells").classes("w-full"):
                    for cell_key in node.cells[:MAX_RENDERED_ROWS]:
                        ui.label(cell_key).classes("font-mono text-xs text-grey")
                    if len(node.cells) > MAX_RENDERED_ROWS:
                        ui.label(
                            f"Showing {MAX_RENDERED_ROWS} / {len(node.cells)}"
                        ).classes("text-caption text-grey")

    def _render_defect_row(self, row: DefectRow) -> None:
        """Render a single defect row."""
        is_open = row.status == "open"
        is_fixed = row.status == "fixed"
        is_back = row.status == "back_in_service"

        with ui.card().classes("w-full").props("flat bordered"):  # ruff: ignore[multiple-with-statements]
            with ui.row().classes("w-full items-center gap-4"):
                # Status badge
                status_labels = {
                    "open": self.tr("arrived"),
                    "fixed": self.tr("diagnosed"),
                    "back_in_service": self.tr("back_in_service"),
                }
                status_colors = {
                    "open": "negative",
                    "fixed": "warning",
                    "back_in_service": "positive",
                }
                ui.badge(
                    status_labels.get(row.status, row.status),
                    color=status_colors.get(row.status, "grey"),
                ).classes("text-sm")

                # Defect ID
                ui.label(row.defect_id).classes("font-mono text-sm flex-1")

                # Error class
                ui.label(row.error_class).classes("text-xs text-grey font-mono")

                # Count & cells
                ui.label(f"{row.count} hits, {row.cells} cells").classes(
                    "text-xs text-grey"
                )

                # Copy unquarantine command button
                if is_fixed or is_back:
                    cmd = f"comp unquarantine --root ROOT --defect-id {row.defect_id}"
                    ui.button(
                        self.tr("copy"),
                        icon=ICONS["copy"],
                        on_click=lambda _=None, c=cmd: ui.clipboard.write(c),
                    ).props("flat dense size=sm").tooltip(
                        self.tr("copy_unquarantine_cmd")
                    )

                # Toggle status (for demo)
                if is_open:
                    ui.button(
                        self.tr("mark_fixed"),
                        on_click=lambda _=None, r=row: self._update_status(r, "fixed"),
                    ).props("flat dense size=sm color=warning")
                elif is_fixed:
                    ui.button(
                        self.tr("mark_back_in_service"),
                        on_click=lambda _=None, r=row: self._update_status(
                            r, "back_in_service"
                        ),
                    ).props("flat dense size=sm color=positive")

    def _update_status(self, row: DefectRow, new_status: str) -> None:
        """Update defect status (placeholder - would call API)."""
        for i, r in enumerate(self.rows):
            if r.defect_id == row.defect_id:
                self.rows[i] = DefectRow(
                    defect_id=r.defect_id,
                    count=r.count,
                    cells=r.cells,
                    status=new_status,
                    error_class=r.error_class,
                    last_seen=r.last_seen,
                    message=r.message,
                )
                break
        # Re-render would be triggered by parent

    def update_rows(self, rows: list[DefectRow]) -> None:
        """Update rows and re-render."""
        self.rows = rows

    def update_data(
        self,
        data: object | None = None,
        *,
        rows: list[DefectRow] | None = None,
        maturation_nodes: list[MaturationNode] | None = None,
    ) -> None:
        """Push adapter RepairBenchData (or explicit rows) into the panel."""
        if rows is None and data is not None:
            rows = list(data.defects)  # type: ignore[attr-defined]
        if rows is not None:
            self.rows = rows
        if maturation_nodes is not None:
            self.maturation_nodes = maturation_nodes

    def set_lens(self, lens: str) -> None:
        """Set active lens (Defects/Maturation)."""
        if lens not in {"defects", "maturation"}:
            lens = "defects"
        self._active_lens = lens
        if self._lens_tabs:
            tab = self._get_tab_for_lens(lens)
            if tab:
                self._lens_tabs.value = tab

    def _refresh(self) -> None:
        """Refresh on mode change."""
        with suppress(AssertionError, RuntimeError):
            # Refresh is handled by parent re-rendering
            pass


def create_repair_rows_from_defects(defects_path: str) -> list[DefectRow]:
    """Create DefectRow objects from defects JSONL."""
    from pathlib import Path

    from computronium.autoscientist.defects import read_defects

    by_id: dict[str, list[DefectRecord]] = {}
    for record in read_defects(Path(defects_path)):
        by_id.setdefault(record.defect_id, []).append(record)

    rows = []
    for did, group in by_id.items():
        last = max(group, key=lambda r: r.timestamp)
        rows.append(
            DefectRow(
                defect_id=did,
                count=len(group),
                cells=len({r.cell for r in group}),
                status=last.status,
                error_class=last.error_class,
                last_seen=round(last.timestamp, 1),
                message=last.message[:80],
            )
        )

    rows.sort(key=lambda r: (0 if r.status == "open" else 1, -r.count))
    return rows


def create_maturation_nodes_from_atlas(root: Path) -> list[MaturationNode]:
    """Create MaturationNode objects from live_atlas maturation data.

    Returns a flat list of nodes grouped by campaign and maturity level.
    """
    from computronium.visualization.live_atlas import maturation_rows

    maturation_data = maturation_rows(root)
    nodes = []

    # Group by campaign (for now, single campaign)
    # In multi-root, we'd need to distinguish campaigns
    campaign_name = root.name

    for row in maturation_data:
        level = str(row.get("level", "")).removeprefix("maturity:")
        count_raw = row.get("count", 0)
        count = int(count_raw) if isinstance(count_raw, int | float | str) else 0

        if level in {"l0", "l1", "l2"}:
            nodes.append(
                MaturationNode(
                    level=level,
                    campaign=campaign_name,
                    cells=[],  # Would need KB query to get actual cell keys
                    count=count,
                )
            )

    return nodes


__all__ = [
    "DefectRow",
    "MaturationNode",
    "RepairBench",
    "create_maturation_nodes_from_atlas",
    "create_repair_rows_from_defects",
]
