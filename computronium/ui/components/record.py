"""Record component — trust & remember view with History, Ledger, Lessons lenses."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS, MAX_RENDERED_ROWS
from computronium.ui.mode_toggle import BasePanel


class RecordLens(StrEnum):
    """Available lenses in the Record panel."""

    HISTORY = "history"
    LEDGER = "ledger"
    LESSONS = "lessons"


@dataclass(frozen=True, slots=True)
class HistoryEvent:
    """A single history event (milestone or cell completion)."""

    timestamp: float
    kind: str  # "milestone" | "cell_completed" | "burst_finished" | "alert"
    campaign: str
    message: str
    cell_key: str | None = None
    metrics: dict[str, float] | None = None
    severity: str = "info"  # "info" | "positive" | "negative" | "warning"


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    """A ledger entry: experiment → belief → gate."""

    timestamp: float
    experiment: str  # cell key or batch
    belief: str  # what was claimed
    gate: str  # "promoted" | "rejected" | "pending"
    evidence_refs: list[str]  # links to evidence
    calibration: float | None = None  # BP parity if available


@dataclass(frozen=True, slots=True)
class LessonEntry:
    """A negative result lesson (one-line)."""

    timestamp: float
    cell_key: str
    lesson: str  # one-line negative result
    context: dict[str, Any]  # full context for drill-down


@dataclass(frozen=True, slots=True)
class RecordData:
    """Data for Record panel."""

    history: list[HistoryEvent]
    ledger: list[LedgerEntry]
    lessons: list[LessonEntry]
    active_lens: RecordLens = RecordLens.HISTORY


class Record(BasePanel):
    """Record panel: three lenses — History (timeline), Ledger (evidence chains),
    Lessons (negative results). Lens tabs at top + palette deep-links."""

    def __init__(
        self,
        *,
        data: RecordData | None = None,
        on_lens_change: Any | None = None,
    ) -> None:
        super().__init__(
            panel_key="record",
            plain_explanation=(
                "The Record stores campaign history. History shows what "
                "happened when. Ledger shows the evidence chain for every "
                "claim. Lessons captures failed configurations so you don't repeat them."
            ),
            why_explanation=(
                "Traceability requires evidence. The ledger links every claim "
                "to its evidence. Failed configurations prevent repeating failed approaches."
            ),
            expert_explanation=(
                "History = timeline from event_history + front_history_rows. "
                "Ledger = CEEC evidence chains (experiment → belief → gate). "
                "Lessons = negative results from graveyard_rows + void_summary_rows "
                "with one-line summaries. Lens switcher = segmented tabs + "
                "palette deep-links (⌘K 'ledger' → Record:Ledger). "
                "Register-aware defaults: Simple → History; Lab → Ledger."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/record.html",
        )
        self.data = data or RecordData(history=[], ledger=[], lessons=[])
        self._on_lens_change = on_lens_change

        self._lens_tabs: Any = None
        self._lens_panels: dict[RecordLens, Any] = {}
        self._active_lens = self.data.active_lens

    def render(self) -> ui.element:
        """Render the Record panel with lens tabs."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("record")

            # Lens tabs
            with ui.tabs().classes("w-full") as tabs:
                self._tab_history = ui.tab(
                    "History", icon=ICONS.get("history", "history")
                )
                self._tab_ledger = ui.tab(
                    "Ledger", icon=ICONS.get("ledger", "receipt_long")
                )
                self._tab_lessons = ui.tab(
                    "Lessons", icon=ICONS.get("lessons", "school")
                )

            self._lens_tabs = tabs

            with ui.tab_panels(
                tabs, value=self._get_tab_for_lens(self._active_lens)
            ).classes("w-full"):
                with ui.tab_panel(self._tab_history):
                    self._lens_panels[RecordLens.HISTORY] = ui.column().classes(
                        "w-full"
                    )
                    with self._lens_panels[RecordLens.HISTORY]:
                        self._render_history()

                with ui.tab_panel(self._tab_ledger):
                    self._lens_panels[RecordLens.LEDGER] = ui.column().classes("w-full")
                    with self._lens_panels[RecordLens.LEDGER]:
                        self._render_ledger()

                with ui.tab_panel(self._tab_lessons):
                    self._lens_panels[RecordLens.LESSONS] = ui.column().classes(
                        "w-full"
                    )
                    with self._lens_panels[RecordLens.LESSONS]:
                        self._render_lessons()

        return panel

    def _get_tab_for_lens(self, lens: RecordLens) -> Any:
        """Get the tab element for a lens."""
        # Return the appropriate tab element based on lens
        tab_map = {
            RecordLens.HISTORY: getattr(self, "_tab_history", None),
            RecordLens.LEDGER: getattr(self, "_tab_ledger", None),
            RecordLens.LESSONS: getattr(self, "_tab_lessons", None),
        }
        return tab_map.get(lens)

    def _render_history(self) -> None:
        """Render the History lens (timeline/tree)."""
        if not self.data.history:
            ui.label("No history yet. Launch a campaign to see milestones.").classes(
                "text-grey text-center p-8"
            )
            return

        # Timeline view
        with ui.column().classes("w-full gap-2"):
            for event in self.data.history[:MAX_RENDERED_ROWS]:
                self._render_history_event(event)

            if len(self.data.history) > MAX_RENDERED_ROWS:
                ui.label(
                    f"Showing {MAX_RENDERED_ROWS} / {len(self.data.history)} events"
                ).classes("text-caption text-grey")

    def _render_history_event(self, event: HistoryEvent) -> None:
        """Render a single history event."""
        severity_colors = {
            "info": "primary",
            "positive": "positive",
            "negative": "negative",
            "warning": "warning",
        }
        color = severity_colors.get(event.severity, "primary")

        from datetime import datetime

        dt = datetime.fromtimestamp(event.timestamp)
        with (
            ui.card().classes("w-full").props("flat"),
            ui.row().classes("w-full items-start gap-3"),
        ):
            # Timestamp
            ui.label(dt.strftime("%H:%M:%S")).classes(
                "font-mono text-xs text-grey w-20 shrink-0"
            )

            # Event icon + kind
            ui.badge(event.kind.replace("_", " ").title(), color=color).classes(
                "shrink-0"
            )

            # Message
            with ui.column().classes("flex-1 gap-1"):
                ui.label(event.message).classes("text-body")
                if event.cell_key:
                    ui.label(f"Cell: {event.cell_key}").classes(
                        "font-mono text-xs text-grey"
                    )
                if event.metrics:
                    metrics_str = " · ".join(
                        f"{k}={v:.3f}" for k, v in event.metrics.items()
                    )
                    ui.label(metrics_str).classes("font-mono text-xs text-grey")

    def _render_ledger(self) -> None:
        """Render the Ledger lens (evidence chains)."""
        if not self.data.ledger:
            ui.label(
                "No ledger entries yet. Claims appear as campaigns progress."
            ).classes("text-grey text-center p-8")
            return

        with ui.column().classes("w-full gap-2"):
            for entry in self.data.ledger[:MAX_RENDERED_ROWS]:
                self._render_ledger_entry(entry)

            if len(self.data.ledger) > MAX_RENDERED_ROWS:
                ui.label(
                    f"Showing {MAX_RENDERED_ROWS} / {len(self.data.ledger)} entries"
                ).classes("text-caption text-grey")

    def _render_ledger_entry(self, entry: LedgerEntry) -> None:
        """Render a single ledger entry."""
        gate_colors = {
            "promoted": "positive",
            "rejected": "negative",
            "pending": "warning",
        }
        gate_color = gate_colors.get(entry.gate, "primary")

        from datetime import datetime

        dt = datetime.fromtimestamp(entry.timestamp)
        with (
            ui.card().classes("w-full").props("flat"),
            ui.row().classes("w-full items-start gap-3"),
        ):
            # Timestamp
            ui.label(dt.strftime("%H:%M:%S")).classes(
                "font-mono text-xs text-grey w-20 shrink-0"
            )

            # Gate badge
            ui.badge(entry.gate.upper(), color=gate_color).classes("shrink-0")

            # Content
            with ui.column().classes("flex-1 gap-1"):
                ui.label(f"Experiment: {entry.experiment}").classes("font-mono text-sm")
                ui.label(f"Belief: {entry.belief}").classes("text-body")
                if entry.evidence_refs:
                    refs = ", ".join(entry.evidence_refs[:3])
                    if len(entry.evidence_refs) > 3:
                        refs += f" +{len(entry.evidence_refs) - 3} more"
                    ui.label(f"Evidence: {refs}").classes(
                        "text-caption text-grey font-mono"
                    )
                if entry.calibration is not None:
                    cal_color = (
                        "text-positive"
                        if entry.calibration > 0.9
                        else "text-warning"
                        if entry.calibration > 0.7
                        else "text-negative"
                    )
                    ui.label(f"BP Calibration: {entry.calibration:.1%}").classes(
                        f"text-sm font-mono {cal_color}"
                    )

    def _render_lessons(self) -> None:
        """Render the Lessons lens (negative results)."""
        if not self.data.lessons:
            ui.label(
                "No lessons yet. Failed experiments appear here automatically."
            ).classes("text-grey text-center p-8")
            return

        with ui.column().classes("w-full gap-2"):
            for lesson in self.data.lessons[:MAX_RENDERED_ROWS]:
                self._render_lesson(lesson)

            if len(self.data.lessons) > MAX_RENDERED_ROWS:
                ui.label(
                    f"Showing {MAX_RENDERED_ROWS} / {len(self.data.lessons)} lessons"
                ).classes("text-caption text-grey")

    def _render_lesson(self, lesson: LessonEntry) -> None:
        """Render a single lesson entry."""
        from datetime import datetime

        dt = datetime.fromtimestamp(lesson.timestamp)
        with (
            ui.card().classes("w-full").props("flat"),
            ui.row().classes("w-full items-start gap-3"),
        ):
            # Timestamp
            ui.label(dt.strftime("%H:%M:%S")).classes(
                "font-mono text-xs text-grey w-20 shrink-0"
            )

            # Lesson icon
            ui.icon(ICONS.get("lessons", "school")).classes("text-warning shrink-0")

            # Content
            with ui.column().classes("flex-1 gap-1"):
                ui.label(lesson.lesson).classes("text-body")
                ui.label(f"Cell: {lesson.cell_key}").classes(
                    "font-mono text-xs text-grey"
                )
                # Expandable context
                with ui.expansion("Context").classes("w-full"):
                    for k, v in lesson.context.items():
                        ui.label(f"{k}: {v}").classes("font-mono text-xs text-grey")

    def set_lens(self, lens: str) -> None:
        """Switch to a specific lens."""
        try:
            lens_enum = RecordLens(lens)
        except ValueError:
            lens_enum = RecordLens.HISTORY
        self._active_lens = lens_enum
        self.data = RecordData(
            history=self.data.history,
            ledger=self.data.ledger,
            lessons=self.data.lessons,
            active_lens=lens_enum,
        )
        if self._on_lens_change:
            self._on_lens_change(lens_enum)

    def update_data(
        self,
        data: RecordData | None = None,
        *,
        history: list[HistoryEvent] | None = None,
        ledger: list[LedgerEntry] | None = None,
        lessons: list[LessonEntry] | None = None,
        active_lens: RecordLens | None = None,
    ) -> None:
        """Update panel data."""
        if data is not None:
            self.data = data
            self._active_lens = data.active_lens
        else:
            self.data = RecordData(
                history=history if history is not None else self.data.history,
                ledger=ledger if ledger is not None else self.data.ledger,
                lessons=lessons if lessons is not None else self.data.lessons,
                active_lens=active_lens
                if active_lens is not None
                else self.data.active_lens,
            )
            self._active_lens = self.data.active_lens


__all__ = [
    "HistoryEvent",
    "LedgerEntry",
    "LessonEntry",
    "Record",
    "RecordData",
    "RecordLens",
]
