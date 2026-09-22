"""Field Reports component (M1.9) — retyped toasts as field reports with deep links."""

from __future__ import annotations

from dataclasses import dataclass

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel


@dataclass(frozen=True, slots=True)
class FieldReport:
    """A field report (re-typed toast)."""

    icon: str
    color: str
    sentence: str
    deep_link: str | None = None
    unread: bool = True


class FieldReports(BasePanel):
    """Field Reports: tray with icon + sentence + deep link, batched with unread badge."""

    def __init__(
        self,
        *,
        reports: list[FieldReport] | None = None,
        max_reports: int = 20,
    ) -> None:
        super().__init__(
            panel_key="field_reports",
            plain_explanation=(
                "Field reports are important messages from the campaign. "
                "Each has a one-sentence summary and a link to details."
            ),
            why_explanation=(
                "Breakthrough alerts are scoped (e.g., 'New best correctness among similar size'). "
                "No bare 'state of the art' language. Deep links go to the evidence."
            ),
            expert_explanation=(
                "Re-typed from live_atlas alert toasts. "
                "Categories: breakthrough (new Pareto front), cascade (divergence wave), "
                "completion (campaign target reached). "
                "Batched tray with unread badge. Lab mode hides by default."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/field_reports.html",
        )
        self.reports = reports or []
        self.max_reports = max_reports
        self._tray_container: ui.element = ui.column().classes("w-full")
        self._badge_label: ui.label | None = None

    def render(self) -> ui.element:
        """Render the Field Reports panel."""
        with ui.column().classes("w-full gap-4") as panel:
            # Header with unread badge
            with ui.row().classes("w-full items-center justify-between"):
                self.render_header("events")
                self._badge_label = (
                    ui.badge("0", color="primary").props("outline").classes("text-sm")
                )

            # Report tray
            self._tray_container = ui.column().classes("w-full")
            with self._tray_container:
                self._render_tray()

        return panel

    def _render_tray(self) -> None:
        """Render the report tray."""
        self._tray_container.clear()
        unread_count = sum(1 for r in self.reports if r.unread)
        if self._badge_label:
            self._badge_label.set_text(str(unread_count))

        with self._tray_container:
            if not self.reports:
                ui.label(self.tr("no_field_reports")).classes(
                    "text-grey text-center p-4"
                )
                return

            for report in self.reports[-self.max_reports :]:
                with ui.card().classes("w-full").props("flat"):
                    with ui.row().classes("w-full items-start gap-3"):
                        # Unread indicator
                        if report.unread:
                            ui.icon(ICONS["circle"]).classes(
                                "text-primary text-sm mt-1"
                            )

                        # Icon
                        ui.label(report.icon).classes("text-lg")

                        # Sentence + deep link
                        with ui.column().classes("flex-1 gap-1"):
                            ui.label(report.sentence).classes("text-body")
                            if report.deep_link:
                                ui.link(
                                    self.tr("see_evidence"),
                                    report.deep_link,
                                ).props("target=_blank").classes("text-primary text-sm")

    def add_report(self, report: FieldReport) -> None:
        """Add a field report."""
        self.reports.append(report)
        if len(self.reports) > self.max_reports:
            self.reports = self.reports[-self.max_reports :]
        self._render_tray()

    def _refresh(self) -> None:
        """Refresh on mode change."""
        self._render_tray()
