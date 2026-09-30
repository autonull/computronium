"""Run-spec profiles, including question-first entry (WP11.5, R43).

A profile turns a practitioner's question — an objective plus an
operating point — into a RunSpec dict consumable by ``PipelineConfig``.
The ``Synthesis`` policy frames the question (S1 Frame) before any
search runs.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "QUESTION_FIRST_STAGES",
    "question_first",
]

QUESTION_FIRST_STAGES: tuple[str, ...] = (
    "s1_frame",
    "s2_space",
    "s3_schedule",
    "s4_gate",
    "s5_compose",
    "s6_train",
    "s7_measure",
    "s8_record",
    "s9_attribute",
    "s10_decide",
    "s11_report",
)
"""Canonical StageIds for a question-first run (S1 Frame first)."""


def question_first(
    objective: str,
    operating_point: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a RunSpec from an objective + operating point (R43).

    Args:
        objective: Objective id from the OBJECTIVES registry
            (e.g. ``"accuracy"``, ``"bp_deficit"``).
        operating_point: Declared operating constraints, e.g.
            ``{"budget_seconds": 600, "fidelity": "L1", "n_seeds": 3}``.

    Returns:
        RunSpec dict with the framing question, the ``synthesis``
        policy, canonical stages, and the S3 data-origin allocation
        (exploration/calibration quotas) plus contrast quota (L19).
    """
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    if objective not in OBJECTIVES_REGISTRY:
        raise KeyError(f"Unknown objective: {objective!r}")
    point = dict(operating_point or {})
    return {
        "kind": "question_first",
        "question": f"How do coordinates trade off {objective} "
        f"at operating point {point or 'default'}?",
        "objectives": [objective],
        "operating_point": point,
        "policy": "synthesis",
        "stages": list(QUESTION_FIRST_STAGES),
        "fidelity": point.get("fidelity", "L1"),
        "n_seeds": point.get("n_seeds", 3),
        "budget_seconds": point.get("budget_seconds"),
        "data_origin_allocation": {
            "exploration": 0.6,
            "calibration": 0.2,
            "test": 0.2,
        },
        "contrast_quota": 0.1,
    }
