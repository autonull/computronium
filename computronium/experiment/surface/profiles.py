"""Run-spec profiles, including question-first entry (WP11.5, R43).

A profile turns a practitioner's question — an objective plus an
operating point — into a ``RunSpec`` consumable by ``PipelineConfig``.
The ``Synthesis`` policy frames the question (S1 Frame) before any
search runs.
"""

from __future__ import annotations

from typing import Any

from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema.run_spec import RunSpec

__all__ = [
    "QUESTION_FIRST_STAGES",
    "question_first",
]

QUESTION_FIRST_STAGES: tuple[str, ...] = tuple(s.value for s in StageId)
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
    known = {"budget_seconds", "fidelity", "n_seeds", "epochs", "seed"}
    point = dict(operating_point or {})
    unknown = sorted(set(point) - known)
    if unknown:
        msg = (
            f"operating_point names unknown field(s) {unknown}; known: {sorted(known)}"
        )
        raise ValueError(msg)
    return RunSpec(
        profile="question_first",
        task=task,
        objectives=(objective,),
        operating_points=point,
        policy="synthesis",
        stages=QUESTION_FIRST_STAGES,
        fidelity=point.get("fidelity", "L1"),
        n_seeds=point.get("n_seeds", 3),
        epochs=point.get("epochs", 1),
        seed=point.get("seed", 0),
        budget_seconds=point.get("budget_seconds"),
    )
