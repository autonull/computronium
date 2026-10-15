"""Run-spec profiles, including question-first entry (WP11.5, R43).

A profile turns a practitioner's question — an objective plus an
operating point — into a ``RunSpec`` consumable by ``PipelineConfig``.
The ``Synthesis`` policy frames the question (S1 Frame) before any
search runs.

W1: Unified with ExperimentConfig for single config surface.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.unified_config import (
    QUESTION_FIRST_STAGES,
    ExperimentConfig,
)

if TYPE_CHECKING:
    from computronium.experiment.schema.run_spec import RunSpec

__all__ = [
    "QUESTION_FIRST_STAGES",
    "question_first",
    "question_first_from_config",
]

"""Canonical StageIds for a question-first run (S1 Frame first)."""


def question_first(
    objective: str,
    task: str,
    operating_point: dict[str, Any] | None = None,
) -> RunSpec:
    """Build a RunSpec from an objective + operating point (R43).

    Args:
        objective: Objective id from the OBJECTIVES registry
            (e.g. ``"validation_accuracy"``, ``"bp_deficit"``).
        task: The task to measure, from the task registry.
        operating_point: Declared operating constraints, e.g.
            ``{"budget_seconds": 600, "fidelity": "L1", "n_seeds": 3}``.

    Returns:
        A RunSpec with the ``synthesis`` policy and canonical stages.

    Raises:
        ValueError: The objective is unknown, or an operating point names a
            field the spec does not carry.
    """
    config = ExperimentConfig.from_question_first(objective, task, operating_point)
    return config.to_runspec()


def question_first_from_config(config: ExperimentConfig) -> RunSpec:
    """Build a RunSpec from ExperimentConfig for question-first entry.

    This is the unified entry point that uses the shared ExperimentConfig.
    """
    return config.to_runspec()
