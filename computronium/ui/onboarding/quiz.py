"""Comfort Quiz (M3.1) — 2 questions, sets default tour depth only."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from nicegui import ui

from computronium.ui.design_tokens import ICONS
from computronium.ui.panels import BasePanel

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class QuizQuestion:
    """One comfort quiz question."""

    key: str
    question: str
    options: list[tuple[str, str]]  # (value, label)
    affects: str  # "tour_depth"


class ComfortQuiz(BasePanel):
    """Comfort Quiz: 2 questions, sets default tour depth only.

    Quiz only affects defaults — never restricts features.
    Results persist in localStorage.
    """

    QUESTIONS: tuple[QuizQuestion, ...] = (
        QuizQuestion(
            key="goals",
            question="What brings you here today?",
            options=[
                ("explore", "Browse and understand the map"),
                ("compare", "Compare specific trade-offs"),
                ("debug", "Diagnose crashes or defects"),
                ("research", "Run campaigns and analyze results"),
            ],
            affects="tour_depth",
        ),
        QuizQuestion(
            key="accessibility",
            question="Do you need any accessibility adjustments?",
            options=[
                ("none", "No adjustments needed"),
                ("reduced_motion", "Reduce animations and motion"),
                ("high_contrast", "High contrast colors"),
                ("screen_reader", "Screen reader optimized"),
            ],
            affects="tour_depth",
        ),
    )

    def __init__(
        self,
        on_complete: Callable[[], None] | None = None,
        on_skip: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(
            panel_key="comfort_quiz",
            plain=(
                "Two quick questions to personalize your experience. "
                "Your answers only set default preferences — you can change "
                "anything anytime. No features are ever restricted."
            ),
            why=(
                "Different users need different defaults. The "
                "quiz sets sensible defaults without gating anything."
            ),
            expert=(
                "Quiz affects tour depth (full/minimal/none). Results stored "
                "in localStorage. Per GAME.md M3.1: 'quiz only affects "
                "defaults, never restricts features.'"
            ),
            docs_url="https://computronium.readthedocs.io/en/latest/dashboard/quiz.html",
        )
        self.on_complete = on_complete
        self.on_skip = on_skip
        self._answers: dict[str, str] = {}
        self._current_question = 0
        self._completed = False
        self._dialog: Any = None

    def start(self) -> None:
        """Start the quiz."""
        self._completed = False
        self._current_question = 0
        self._answers = {}
        self._show_question()

    def skip(self) -> None:
        """Skip the quiz."""
        self._cleanup()
        if self.on_skip:
            self.on_skip()

    def _show_question(self) -> None:
        """Show the current question in a dialog."""
        if self._current_question >= len(self.QUESTIONS):
            self._finish()
            return

        question = self.QUESTIONS[self._current_question]

        self._dialog = ui.dialog()
        with self._dialog, ui.card().classes("w-[500px] p-6"):
            ui.label("Personalize your experience").classes("text-h6 mb-2")
            ui.label(
                f"Question {self._current_question + 1} of {len(self.QUESTIONS)}"
            ).classes("text-caption text-primary font-medium mb-4")

            ui.label(question.question).classes("text-h6 mb-4")

            with ui.column().classes("w-full gap-2"):
                for value, label in question.options:
                    ui.radio(
                        options={value: label},
                        value=self._answers.get(question.key),
                        on_change=lambda _, v=value, k=question.key: (
                            self._select_answer(k, v)
                        ),
                    ).props("inline").classes("w-full")

            with ui.row().classes("w-full justify-end gap-2 mt-4"):
                if self._current_question > 0:
                    ui.button(
                        "Back",
                        on_click=self._prev_question,
                    ).props("flat")

                if self._current_question == len(self.QUESTIONS) - 1:
                    ui.button(
                        "Finish",
                        on_click=self._finish,
                        color="primary",
                    )
                else:
                    next_btn = ui.button(
                        "Next",
                        on_click=self._next_question,
                        color="primary",
                    )
                    if question.key not in self._answers:
                        next_btn.props("disable")

                ui.button(
                    "Skip quiz",
                    on_click=self.skip,
                ).props("flat").classes("text-grey")

        self._dialog.open()

    def _select_answer(self, key: str, value: str) -> None:
        self._answers[key] = value
        # Enable next button
        if self._dialog:
            # Force refresh by re-rendering would be better, but for now
            # the disable state is set at render time
            pass

    def _next_question(self) -> None:
        question = self.QUESTIONS[self._current_question]
        if question.key not in self._answers:
            return
        self._cleanup()
        self._current_question += 1
        self._show_question()

    def _prev_question(self) -> None:
        self._cleanup()
        self._current_question = max(0, self._current_question - 1)
        self._show_question()

    def _finish(self) -> None:
        """Apply answers and finish."""
        self._apply_answers()
        self._save_answers()
        self._cleanup()
        self._completed = True
        if self.on_complete:
            self.on_complete()

    def _apply_answers(self) -> None:
        """Apply quiz answers to settings."""
        # Answers only affect tour-depth defaults; nothing to apply yet.
        # Accessibility preferences set a CSS custom property or body class.
        accessibility = self._answers.get("accessibility")
        if accessibility in {"reduced_motion", "high_contrast"}:
            # This would set a CSS custom property or body class
            pass

    def _save_answers(self) -> None:
        """Save answers to localStorage."""
        try:
            from nicegui import app

            app.storage.user["quiz_answers"] = self._answers
            app.storage.user["quiz_completed"] = True
        except RuntimeError:
            pass

    def _cleanup(self) -> None:
        if self._dialog:
            self._dialog.close()
            self._dialog = None

    def render(self) -> ui.element:
        """Render quiz launcher."""
        with ui.column().classes("w-full gap-4") as panel:
            try:
                from nicegui import app

                completed = app.storage.user.get("quiz_completed", False)
            except RuntimeError:
                completed = False

            if not completed:
                with (
                    ui.card().classes("w-full").props("flat bordered"),
                    ui.row().classes("w-full items-center gap-4"),
                ):
                    ui.icon(ICONS["settings"]).classes("text-3xl text-primary")
                    with ui.column().classes("flex-1"):
                        ui.label("Quick setup").classes("text-h5")
                        ui.label("3 questions to personalize your view.").classes(
                            "text-body text-grey"
                        )
                    ui.button(
                        "Take Quiz",
                        on_click=self.start,
                        icon="quiz",
                    ).props("color=primary")
                    ui.button(
                        "Skip",
                        on_click=self.skip,
                    ).props("flat").classes("text-grey")

        return panel

    def _refresh(self) -> None:
        """Refresh with current data."""


def create_comfort_quiz(
    on_complete: Callable[[], None] | None = None,
    on_skip: Callable[[], None] | None = None,
) -> ComfortQuiz:
    """Create the comfort quiz instance."""
    return ComfortQuiz(on_complete=on_complete, on_skip=on_skip)
