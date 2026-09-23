"""Repair Bench component (M1.6) — defect funnel with statuses and copy buttons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.design_tokens import ICONS, MAX_RENDERED_ROWS
from computronium.ui.mode_toggle import BasePanel

if TYPE_CHECKING:
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


class RepairBench(BasePanel):
    """Repair Bench panel: defect funnel with reframed statuses and copy buttons."""

    def __init__(
        self,
        *,
        rows: list[DefectRow] | None = None,
    ) -> None:
        super().__init__(
            panel_key="repair_bench",
            plain_explanation=(
                "This is the repair bench. It shows crashes that need fixing. "
                "Each row is a unique defect. Click 'Copy' to get the unquarantine command."
            ),
            why_explanation=(
                "Defects are crashes we can fix (not ontology boundaries). "
                "Fixing them lets the campaign continue exploring."
            ),
            expert_explanation=(
                "Defect funnel from live_atlas.defect_funnel_rows(). "
                "Statuses: Arrived (open) → Diagnosed (fixed) → Back in service. "
                "Structural voids (gate-rejected) never appear here. "
                "Copy button generates: `comp unquarantine --root ROOT --defect-id ID`"
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/repair.html",
        )
        self.rows = rows or []

    def render(self) -> ui.element:
        """Render the Repair Bench panel."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("repair")

            if not self.rows:
                ui.label(self.tr("no_defects")).classes("text-grey text-center p-4")
                return panel

            total = len(self.rows)
            for row in self.rows[:MAX_RENDERED_ROWS]:
                self._render_defect_row(row)
            if total > MAX_RENDERED_ROWS:
                ui.label(
                    f"{self.tr('showing_first')}: {MAX_RENDERED_ROWS} / {total}"
                ).classes("text-caption text-grey")

        return panel

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
        self, data: object | None = None, *, rows: list[DefectRow] | None = None
    ) -> None:
        """Push adapter RepairBenchData (or explicit rows) into the panel."""
        if rows is None and data is not None:
            rows = list(data.defects)  # type: ignore[attr-defined]
        if rows is not None:
            self.rows = rows

    def _refresh(self) -> None:
        """Refresh on mode change."""


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
