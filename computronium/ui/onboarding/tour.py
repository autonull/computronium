"""Guided Tour (M3.1) — 3 steps, skippable, resumable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.mode_toggle import BasePanel

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class TourStep:
    """One step in the guided tour."""

    key: str
    target_selector: str  # CSS selector for the element to highlight
    title: str
    content: str
    position: str = "bottom"  # top, bottom, left, right
    action: Callable[[], None] | None = None


class GuidedTour(BasePanel):
    """Guided tour: 3 steps, skippable, resumable.

    Steps:
    1. "Watch a measurement" — points to the active cell inspector
    2. "Read a trade-off" — points to the Pareto strip
    3. "See a repair" — points to the defect funnel
    """

    def __init__(
        self,
        steps: list[TourStep] | None = None,
        on_complete: Callable[[], None] | None = None,
        on_skip: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            panel_key="guided_tour",
            plain_explanation=(
                "A quick 3-step tour to help you get started. You can skip it "
                "anytime and come back later from the help menu."
            ),
            why_explanation=(
                "Newcomers need a gentle entry point. The tour highlights the "
                "three core actions: watching measurements, reading trade-offs, "
                "and seeing repairs. It never restricts features — just guides."
            ),
            expert_explanation=(
                "Tour steps target specific panel selectors. Completion state "
                "persists in localStorage. Steps are register-aware: Explorer "
                "sees plain language, Lab sees technical terms. Skippable and "
                "resumable per GAME.md M3.1."
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/tour.html",
        )
        self.steps = steps or self._default_steps()
        self.on_complete = on_complete
        self.on_skip = on_skip
        self._current_step = 0
        self._completed = False
        self._overlay: ui.element | None = None
        self._tooltip: ui.element | None = None

    def _default_steps(self) -> list[TourStep]:
        return [
            TourStep(
                key="step1_measurement",
                target_selector=".active-cell-inspector, [data-panel='active']",
                title="Watch a measurement",
                content=(
                    "This panel shows the currently training cell: its "
                    "coordinate, progress, resource usage, and live loss curve. "
                    "Watch how different recipes learn in real time."
                ),
                position="bottom",
            ),
            TourStep(
                key="step2_tradeoff",
                target_selector=".pareto-strip, [data-panel='pareto']",
                title="Read a trade-off",
                content=(
                    "The Pareto strip shows the best trade-offs between two "
                    "goals (like accuracy vs. speed). Use the selector to "
                    "compare different objective pairs."
                ),
                position="top",
            ),
            TourStep(
                key="step3_repair",
                target_selector=".defect-funnel, [data-panel='funnel']",
                title="See a repair",
                content=(
                    "The defect funnel lists crashes we can fix. Each row has "
                    "a 'Copy unquarantine command' button — run it to release "
                    "the cell after fixing the bug."
                ),
                position="top",
            ),
        ]

    def start(self) -> None:
        """Start the tour from the beginning or resume."""
        self._completed = False
        self._current_step = self._get_resume_step()
        self._show_step()

    def skip(self) -> None:
        """Skip the tour entirely."""
        self._cleanup()
        if self.on_skip:
            self.on_skip()

    def _get_resume_step(self) -> int:
        """Get the step to resume from (stored in localStorage)."""
        try:
            from nicegui import app

            stored = app.storage.user.get("tour_step")
            if isinstance(stored, int) and 0 <= stored < len(self.steps):
                return stored
        except RuntimeError:
            pass
        return 0

    def _save_step(self, step: int) -> None:
        """Save current step to localStorage."""
        try:
            from nicegui import app

            app.storage.user["tour_step"] = step
        except RuntimeError:
            pass

    def _mark_completed(self) -> None:
        """Mark tour as completed."""
        try:
            from nicegui import app

            app.storage.user["tour_completed"] = True
        except RuntimeError:
            pass

    def _show_step(self) -> None:
        """Show the current tour step."""
        if self._current_step >= len(self.steps):
            self._finish()
            return

        step = self.steps[self._current_step]
        self._save_step(self._current_step)

        # Create overlay
        self._overlay = ui.element("div").classes(
            "fixed inset-0 bg-black/50 z-[1000] pointer-events-none"
        )
        self._overlay.on("click", self._next_step)

        # Create tooltip near target
        self._tooltip = ui.element("div").classes(
            "fixed z-[1001] pointer-events-auto max-w-[400px] "
            "bg-white dark:bg-gray-800 rounded-lg shadow-xl p-4 "
            "border border-gray-200 dark:border-gray-700"
        )

        with self._tooltip, ui.row().classes("w-full items-start gap-2"):
            ui.icon(ICONS["map"]).classes("text-2xl text-primary shrink-0")

            with ui.column().classes("flex-1 gap-2"):
                # Step indicator
                ui.label(f"Step {self._current_step + 1} of {len(self.steps)}").classes(
                    "text-caption text-primary font-medium"
                )

                ui.label(self.tr(step.title)).classes("text-h6")

                ui.label(step.content).classes("text-body")

                # Navigation
                with ui.row().classes("w-full justify-end gap-2 mt-2"):
                    if self._current_step > 0:
                        ui.button(
                            "Back",
                            on_click=self._prev_step,
                        ).props("flat")

                    if self._current_step == len(self.steps) - 1:
                        ui.button(
                            "Finish",
                            on_click=self._finish,
                            color="primary",
                        )
                    else:
                        ui.button(
                            "Next",
                            on_click=self._next_step,
                            color="primary",
                        )

                    ui.button(
                        "Skip tour",
                        on_click=self.skip,
                    ).props("flat").classes("text-grey")

        # Position tooltip (simplified - in practice would use JS to position)
        self._tooltip.style("top: 50%; left: 50%; transform: translate(-50%, -50%);")

    def _next_step(self) -> None:
        self._cleanup()
        self._current_step += 1
        self._show_step()

    def _prev_step(self) -> None:
        self._cleanup()
        self._current_step = max(0, self._current_step - 1)
        self._show_step()

    def _finish(self) -> None:
        self._cleanup()
        self._mark_completed()
        self._completed = True
        if self.on_complete:
            self.on_complete()

    def _cleanup(self) -> None:
        if self._overlay:
            self._overlay.delete()
            self._overlay = None
        if self._tooltip:
            self._tooltip.delete()
            self._tooltip = None

    def render(self) -> ui.element:
        """Render tour launcher (button to start tour)."""
        with ui.column().classes("w-full gap-4") as panel:
            # Only show if not completed
            try:
                from nicegui import app

                completed = app.storage.user.get("tour_completed", False)
            except RuntimeError:
                completed = False

            if not completed:
                with (
                    ui.card().classes("w-full").props("flat bordered"),
                    ui.row().classes("w-full items-center gap-4"),
                ):
                    ui.icon(ICONS["map"]).classes("text-3xl text-primary")
                    with ui.column().classes("flex-1"):
                        ui.label("Welcome to Computronium!").classes("text-h5")
                        ui.label(
                            "Take a quick 3-step tour to learn the basics."
                        ).classes("text-body text-grey")
                    ui.button(
                        "Start Tour",
                        on_click=self.start,
                        icon="play_arrow",
                    ).props("color=primary")
                    ui.button(
                        "Skip",
                        on_click=self.skip,
                    ).props("flat").classes("text-grey")

        return panel

    def _refresh(self) -> None:
        """Refresh on mode change."""


def create_guided_tour(
    on_complete: Callable[[], None] | None = None,
    on_skip: Callable[[], None] | None = None,
) -> GuidedTour:
    """Create the guided tour instance."""
    return GuidedTour(on_complete=on_complete, on_skip=on_skip)
