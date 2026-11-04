"""Task scheduler for smart-survey profile.

Cycles through cheap tasks at L0, expands to medium at L1, includes expensive at L2.
Uses ruler-relative normalization for cross-task comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from computronium.domains._task_registry import (
    CHEAP_TASKS,
    EXPENSIVE_TASKS,
    MEDIUM_TASKS,
    get_baseline,
    get_fidelity_tasks,
    get_task_cycle,
    normalize_score,
)


@dataclass(frozen=True, slots=True)
class TaskScheduler:
    """Multi-task scheduler for smart-survey profile.

    Cycles through cheap tasks at L0, expands to medium at L1, includes expensive at L2.
    Uses ruler-relative normalization for cross-task comparison.
    """

    # Task cost classes (exposed for test compatibility)
    CHEAP_TASKS: tuple[str, ...] = CHEAP_TASKS
    MEDIUM_TASKS: tuple[str, ...] = MEDIUM_TASKS
    EXPENSIVE_TASKS: tuple[str, ...] = EXPENSIVE_TASKS

    # Per-fidelity task selection (lazy init)
    _fidelity_tasks: dict[str, tuple[str, ...]] = field(default=None, init=False)  # type: ignore[assignment]

    def __post_init__(self):
        if self._fidelity_tasks is None:
            object.__setattr__(
                self,
                "_fidelity_tasks",
                {
                    "L0": CHEAP_TASKS,
                    "L1": CHEAP_TASKS + MEDIUM_TASKS,
                    "L2": CHEAP_TASKS + MEDIUM_TASKS + EXPENSIVE_TASKS,
                },
            )

    def get_tasks_for_fidelity(self, fidelity: str) -> tuple[str, ...]:
        """Get the tasks to use for a given fidelity level."""
        return get_fidelity_tasks(fidelity)

    def get_task_cycle(self, fidelity: str, max_tasks: int | None = None) -> list[str]:
        """Get a cycling list of tasks for the given fidelity.

        Args:
            fidelity: The fidelity level (L0, L1, L2).
            max_tasks: Optional maximum number of tasks to include.

        Returns:
            List of task names to cycle through.
        """
        return get_task_cycle(fidelity, max_tasks)

    def normalize_score(
        self, score: float, task_name: str, baseline: float = 0.0
    ) -> float:
        """Normalize a score relative to a task's baseline (ruler-relative).

        Args:
            score: The raw score (e.g., validation accuracy).
            task_name: The task name.
            baseline: The baseline score for this task (random/majority class).

        Returns:
            Normalized score where 0 = baseline, 1 = perfect.
        """
        return normalize_score(score, task_name, baseline)

    def get_baseline(self, task_name: str) -> float:
        """Get the baseline accuracy for a task (random guess / majority class).

        Args:
            task_name: The task name.

        Returns:
            Baseline accuracy (e.g., 0.1 for 10-class, 0.5 for binary).
        """
        return get_baseline(task_name)
