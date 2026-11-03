"""Task scheduler for smart-survey profile extracted from evaluate.py."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping


# Task cost classes (from domains.registry)
CHEAP_TASKS: tuple[str, ...] = (
    "xor",
    "spiral",
    "circles",
    "digits",
    "copy_task",
    "iris",
    "wine",
    "breast_cancer",
    "synthetic_forecast",
)
MEDIUM_TASKS: tuple[str, ...] = (
    "mnist",
    "fashion_mnist",
    "sequential_mnist",
    "char_ngram",
    "cora",
    "citeseer",
    "pubmed",
    "kmnist",
    "usps",
)
EXPENSIVE_TASKS: tuple[str, ...] = (
    "cifar10",
    "tiny_shakespeare",
    "pendulum",
    "acrobot",
    "cartpole",
    "graph_classification",
)

# Baseline accuracies for ruler-relative normalization (random guess / majority class)
TASK_BASELINES: dict[str, float] = {
    # 10-class classification
    "digits": 0.1,
    "mnist": 0.1,
    "fashion_mnist": 0.1,
    "kmnist": 0.1,
    "usps": 0.1,
    "cifar10": 0.1,
    "sequential_mnist": 0.1,
    # Binary classification
    "xor": 0.5,
    "spiral": 0.5,
    "circles": 0.5,
    "breast_cancer": 0.5,
    "graph_classification": 0.5,
    # 3-class
    "pubmed": 0.33,
    "iris": 0.33,
    "wine": 0.33,
    # 6-7 class
    "cora": 0.14,  # 7 classes
    "citeseer": 0.16,  # 6 classes
    # Sequence / continuous
    "copy_task": 0.0,
    "char_ngram": 0.01,
    "tiny_shakespeare": 0.01,
    "synthetic_forecast": 0.0,
    "pendulum": 0.0,
    "acrobot": 0.0,
    "cartpole": 0.0,
}

DEFAULT_BASELINE = 0.1  # default 10-class


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

    # Per-fidelity task selection
    fidelity_tasks: dict[str, tuple[str, ...]] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.fidelity_tasks is None:
            object.__setattr__(
                self,
                "fidelity_tasks",
                {
                    "L0": self.CHEAP_TASKS,
                    "L1": self.CHEAP_TASKS + self.MEDIUM_TASKS,
                    "L2": self.CHEAP_TASKS + self.MEDIUM_TASKS + self.EXPENSIVE_TASKS,
                },
            )

    def get_tasks_for_fidelity(self, fidelity: str) -> tuple[str, ...]:
        """Get the tasks to use for a given fidelity level."""
        return self.fidelity_tasks.get(fidelity, self.CHEAP_TASKS)

    def get_task_cycle(self, fidelity: str, max_tasks: int | None = None) -> list[str]:
        """Get a cycling list of tasks for the given fidelity.

        Args:
            fidelity: The fidelity level (L0, L1, L2).
            max_tasks: Optional maximum number of tasks to include.

        Returns:
            List of task names to cycle through.
        """
        tasks = list(self.get_tasks_for_fidelity(fidelity))
        if max_tasks:
            tasks = tasks[:max_tasks]
        return tasks

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
        if baseline >= 1.0:
            return 0.0
        return (score - baseline) / (1.0 - baseline)

    def get_baseline(self, task_name: str) -> float:
        """Get the baseline accuracy for a task (random guess / majority class).

        Args:
            task_name: The task name.

        Returns:
            Baseline accuracy (e.g., 0.1 for 10-class, 0.5 for binary).
        """
        return TASK_BASELINES.get(task_name, DEFAULT_BASELINE)