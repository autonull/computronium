"""Task registry with cost classes and metadata.

Single source of truth for task definitions, cost classes, baselines,
and other task metadata used across the codebase.

This module derives its data from the enriched task registry in
`experiment.registry.task_registry`, which is the authoritative source.
"""

from __future__ import annotations

from dataclasses import dataclass

from computronium.experiment.registry.task_registry import TaskRegistry


@dataclass(frozen=True, slots=True)
class TaskInfo:
    """Metadata for a single task."""

    name: str
    cost_class: str  # "cheap", "medium", "expensive"
    baseline: float  # Random guess / majority class accuracy
    num_classes: int | None = None
    input_shape: tuple[int, ...] | None = None


def _build_task_definitions() -> dict[str, TaskInfo]:
    """Build task definitions from the enriched registry."""
    registry = TaskRegistry()
    definitions = {}
    for task in registry:
        # Get baseline from the enriched registry's baseline (1/output_dim for classification)
        baseline = (
            1.0 / task.output_dim if task.output_dim and task.output_dim > 1 else 0.0
        )
        definitions[task.name] = TaskInfo(
            name=task.name,
            cost_class=task.cost_class.value,
            baseline=baseline,
            num_classes=task.output_dim,
            input_shape=task.input_shape,
        )
    return definitions


# Task definitions - derived from the enriched registry (single source of truth)
_TASK_DEFINITIONS: dict[str, TaskInfo] = _build_task_definitions()


def get_task_info(task_name: str) -> TaskInfo | None:
    """Get task info by name."""
    return _TASK_DEFINITIONS.get(task_name)


def get_tasks_by_cost_class(cost_class: str) -> list[str]:
    """Get all task names for a given cost class."""
    return [
        name
        for name, info in _TASK_DEFINITIONS.items()
        if info.cost_class == cost_class
    ]


def get_all_task_names() -> list[str]:
    """Get all registered task names."""
    return list(_TASK_DEFINITIONS.keys())


# Cost class constants for easy access
CHEAP_TASKS: tuple[str, ...] = tuple(get_tasks_by_cost_class("cheap"))
MEDIUM_TASKS: tuple[str, ...] = tuple(get_tasks_by_cost_class("medium"))
EXPENSIVE_TASKS: tuple[str, ...] = tuple(get_tasks_by_cost_class("expensive"))

# Baseline accuracies for ruler-relative normalization
TASK_BASELINES: dict[str, float] = {
    name: info.baseline for name, info in _TASK_DEFINITIONS.items()
}

DEFAULT_BASELINE: float = 0.1  # default for 10-class


def get_fidelity_tasks(fidelity: str) -> tuple[str, ...]:
    """Get tasks available at a given fidelity level.

    Args:
        fidelity: "L0", "L1", or "L2"

    Returns:
        Tuple of task names available at that fidelity.
    """
    if fidelity == "L0":
        return CHEAP_TASKS
    elif fidelity == "L1":
        return CHEAP_TASKS + MEDIUM_TASKS
    elif fidelity == "L2":
        return CHEAP_TASKS + MEDIUM_TASKS + EXPENSIVE_TASKS
    else:
        return CHEAP_TASKS


def get_task_cycle(fidelity: str, max_tasks: int | None = None) -> list[str]:
    """Get a cycling list of tasks for the given fidelity.

    Args:
        fidelity: The fidelity level (L0, L1, L2).
        max_tasks: Optional maximum number of tasks to include.

    Returns:
        List of task names to cycle through.
    """
    tasks = list(get_fidelity_tasks(fidelity))
    if max_tasks:
        tasks = tasks[:max_tasks]
    return tasks


def normalize_score(score: float, task_name: str, baseline: float = 0.0) -> float:
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


def get_baseline(task_name: str) -> float:
    """Get the baseline accuracy for a task (random guess / majority class).

    Args:
        task_name: The task name.

    Returns:
        Baseline accuracy (e.g., 0.1 for 10-class, 0.5 for binary).
    """
    return TASK_BASELINES.get(task_name, DEFAULT_BASELINE)


__all__ = [
    "CHEAP_TASKS",
    "DEFAULT_BASELINE",
    "EXPENSIVE_TASKS",
    "MEDIUM_TASKS",
    "TASK_BASELINES",
    "TaskInfo",
    "get_all_task_names",
    "get_baseline",
    "get_fidelity_tasks",
    "get_task_cycle",
    "get_task_info",
    "get_tasks_by_cost_class",
    "normalize_score",
]
