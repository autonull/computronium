"""Progress Panel component (M2.7) — quests, badges, records with register-aware copy."""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel
from computronium.ui.recognition import Badge, Quest, Record


@dataclass(frozen=True, slots=True)
class ProgressData:
    """Data for the progress panel."""

    badges: list[Badge]
    quests: list[Quest]
    records: list[Record]


class ProgressPanel(BasePanel):
    """Progress Panel: quests, badges, records (Explorer/Lab registers)."""

    def __init__(
        self,
        *,
        data: ProgressData | None = None,
        gamify_enabled: bool = True,
    ) -> None:
        super().__init__(
            panel_key="progress",
            plain_explanation=(
                "Your journey so far. Badges mark verified achievements. "
                "Quests are optional checklists you opt into. Records are your personal bests."
            ),
            why_explanation=(
                "Recognition is evidence-linked, not points-based. "
                "Every badge has a receipt. Quests map to campaign milestones. "
                "Records show your best measurements per objective."
            ),
            expert_explanation=(
                "Badges: 8 ledger-linked (CEEC/KB). Quests: 6 opt-in, campaign-mapped. "
                "Records: personal bests from Pareto front + CEEC gates. "
                "Lab mode hides chrome by default. Kill switch: --gamify off. "
                "Integrity: UX-L2 replay lock, UX-L7 import lock."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/progress.html",
        )
        self.data = data or ProgressData(badges=[], quests=[], records=[])
        self.gamify_enabled = gamify_enabled
        self._badges_container: ui.element = ui.column().classes("w-full")
        self._quests_container: ui.element = ui.column().classes("w-full")
        self._records_container: ui.element = ui.column().classes("w-full")

    def render(self) -> ui.element:
        """Render the Progress Panel."""
        if not self.gamify_enabled or self.is_lab:
            # In Lab mode or gamify off, show minimal summary
            return self._render_minimal()

        with ui.column().classes("w-full gap-6") as panel:
            self.render_header("progress")

            # Badges section
            with ui.card().classes("w-full").props("flat bordered"):
                ui.label(self.tr("badges")).classes("text-h6 mb-4")
                self._badges_container = ui.column().classes("w-full gap-2")
                with self._badges_container:
                    self._render_badges()

            # Quests section
            with ui.card().classes("w-full").props("flat bordered"):
                with ui.row().classes("w-full items-center justify-between mb-4"):
                    ui.label(self.tr("quests")).classes("text-h6")
                    ui.button(
                        self.tr("opt_in_quest"),
                        icon="add",
                        on_click=self._show_quest_picker,
                    ).props("flat dense size=sm")

                self._quests_container = ui.column().classes("w-full gap-2")
                with self._quests_container:
                    self._render_quests()

            # Records section
            with ui.card().classes("w-full").props("flat bordered"):
                ui.label(self.tr("records")).classes("text-h6 mb-4")
                self._records_container = ui.column().classes("w-full gap-2")
                with self._records_container:
                    self._render_records()

        return panel

    def _render_minimal(self) -> ui.element:
        """Minimal view for Lab mode or gamify off."""
        with ui.column().classes("w-full gap-4") as panel:
            self.render_header("progress")

            if not self.gamify_enabled:
                ui.label(self.tr("gamify_disabled")).classes(
                    "text-grey text-center p-8"
                )
            elif self.is_lab:
                badge_count = len(self.data.badges)
                quest_count = len([q for q in self.data.quests if q.completed])
                record_count = len(self.data.records)

                with ui.row().classes("w-full gap-4"):
                    self._stat_card(self.tr("badges"), str(badge_count), ICONS["award"])
                    self._stat_card(
                        self.tr("quests_completed"), str(quest_count), ICONS["flag"]
                    )
                    self._stat_card(
                        self.tr("records"), str(record_count), ICONS["trending_up"]
                    )

        return panel

    def _stat_card(self, label: str, value: str, icon: str) -> ui.element:
        with (
            ui.card().classes("flex-1 items-center py-4").props("flat bordered") as card
        ):
            ui.icon(icon).classes("text-3xl")
            ui.label(value).classes("text-h4 font-bold")
            ui.label(label).classes("text-caption text-grey")
        return card

    def _render_badges(self) -> None:
        """Render earned badges."""
        if not self.data.badges:
            ui.label(self.tr("no_badges_yet")).classes("text-grey text-center py-4")
            return

        with ui.row().classes("w-full gap-2 flex-wrap"):
            for badge in self.data.badges:
                self._render_badge_card(badge)

    def _render_badge_card(self, badge: Badge) -> None:
        """Render a single badge card."""
        with ui.card().classes("w-32 h-32").props("flat bordered"):  # noqa: SIM117
            with ui.column().classes("w-full items-center justify-center gap-1"):
                ui.label(badge.icon).classes("text-4xl")
                ui.label(self.tr(badge.id)).classes("text-bold text-center")
                if self.is_lab:
                    ui.label(badge.register_lab).classes(
                        "text-xs text-grey text-center"
                    )
                else:
                    ui.label(badge.register_explorer).classes(
                        "text-xs text-grey text-center"
                    )

    def _render_quests(self) -> None:
        """Render quest progress."""
        active_quests = [q for q in self.data.quests if q.opted_in]
        available_quests = [q for q in self.data.quests if not q.opted_in]

        if active_quests:
            ui.label(self.tr("active_quests")).classes("text-bold text-sm mb-2")
            for quest in active_quests:
                self._render_quest_card(quest)

        if available_quests:
            ui.separator().classes("my-2")
            ui.label(self.tr("available_quests")).classes("text-bold text-sm mb-2")
            for quest in available_quests:
                self._render_quest_card(quest, available=True)

        if not self.data.quests:
            ui.label(self.tr("no_quests_yet")).classes("text-grey text-center py-4")

    def _render_quest_card(self, quest: Quest, available: bool = False) -> None:
        """Render a single quest card."""
        progress_pct = (
            (quest.progress_current / quest.progress_target * 100)
            if quest.progress_target > 0
            else 0
        )

        with ui.card().classes("w-full").props("flat bordered"):
            with ui.row().classes("w-full items-center gap-2"):
                ui.label(quest.icon).classes("text-xl")
                with ui.column().classes("flex-1"):
                    ui.label(self.tr(quest.id)).classes("text-bold")
                    if self.is_lab:
                        ui.label(quest.objective).classes("text-xs text-grey")
                if available:
                    ui.button(
                        self.tr("opt_in"),
                        on_click=partial(self._opt_in_quest, quest.id),
                    ).props("flat dense size=sm color=primary")
                elif not quest.completed:
                    ui.linear_progress(
                        value=progress_pct / 100, show_value=False
                    ).classes("w-24")
                    ui.label(f"{progress_pct:.0f}%").classes("text-xs text-grey w-12")

            if quest.completed:
                msg = (
                    quest.completion_message_explorer
                    if self.is_explorer
                    else quest.completion_message_lab
                )
                ui.label(f"✓ {msg}").classes("text-green text-sm mt-1")

    def _render_records(self) -> None:
        """Render personal best records."""
        if not self.data.records:
            ui.label(self.tr("no_records_yet")).classes("text-grey text-center py-4")
            return

        # Group by objective
        from collections import defaultdict

        by_objective: dict[str, list[Record]] = defaultdict(list)
        for record in self.data.records:
            by_objective[record.objective].append(record)

        for objective, records in by_objective.items():
            # Show only the best record per objective
            best = records[0]
            with ui.row().classes("w-full items-center gap-2 py-1"):
                if self.is_explorer:
                    ui.label(best.register_explorer).classes("flex-1")
                else:
                    ui.label(f"{objective}: {best.value:.6f}").classes(
                        "font-mono flex-1"
                    )
                    ui.label(f"({best.scope})").classes("text-grey text-sm")
                    ui.label(best.cell_key[:16]).classes(
                        "text-xs text-primary font-mono"
                    )

    def _show_quest_picker(self) -> None:
        """Show dialog to opt in to available quests."""
        available = [q for q in self.data.quests if not q.opted_in]
        if not available:
            return

        with ui.dialog() as dialog, ui.card().classes("w-96"):
            ui.label(self.tr("choose_quest")).classes("text-h6 mb-4")
            for quest in available:
                with ui.card().classes("w-full mb-2").props("flat"):  # noqa: SIM117
                    with ui.row().classes("w-full items-center justify-between"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(quest.icon).classes("text-xl")
                            ui.label(self.tr(quest.id)).classes("text-bold")
                            ui.label(quest.objective).classes("text-grey text-sm")
                        ui.button(
                            self.tr("opt_in"),
                            on_click=partial(self._opt_in_and_close, quest.id, dialog),
                        ).props("flat dense color=primary")
            dialog.open()

    def _opt_in_and_close(self, quest_id: str, dialog: ui.dialog) -> None:
        """Opt in to a quest and close the dialog."""
        self._opt_in_quest(quest_id)
        dialog.close()

    def _opt_in_quest(self, quest_id: str) -> None:
        """Opt in to a quest (updates local data)."""
        for i, quest in enumerate(self.data.quests):
            if quest.id == quest_id:
                self.data.quests[i] = Quest(**{**quest.__dict__, "opted_in": True})
                break
        self._render_quests()

    def update_data(self, *, data: ProgressData | None = None) -> None:
        """Update progress data."""
        if data is not None:
            self.data = data
        self._render_badges()
        self._render_quests()
        self._render_records()

    def _refresh(self) -> None:
        """Refresh on mode change."""
        self._render_badges()
        self._render_quests()
        self._render_records()


def create_progress_data_from_state(
    badges: list[Badge],
    quests: list[Quest],
    records: list[Record],
) -> ProgressData:
    """Create ProgressData from recognition state."""
    return ProgressData(badges=badges, quests=quests, records=records)
