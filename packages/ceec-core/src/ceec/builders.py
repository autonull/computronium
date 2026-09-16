"""Payload builders for CEEC experiments and gate evidence (TODO25 C.1).

Retires the hand-assembled-payload failure mode measured while landing
TODO25 B.1/B.2 (required-field discovery by failure, misspelled quality
flags, per-probe statistics): ``experiment``, ``gate_evidence``, and
``chance_verdict`` are the single construction surface for §22 experiments
and §18/§19 gate evidence. Tier strings follow the lab RESEARCH3 E-1
ladder (smoke/quick/certified); ceec stays Computronium-free, so lab
callers pass ``BudgetTier.<X>.value``.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal, cast

from ceec import models
from ceec.store import now

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ceec.store import CEECStore

_CeecBudget = Literal["quick", "standard", "nightly"]

__all__ = [
    "DEFAULT_HARD_GATES",
    "ChanceVerdict",
    "chance_verdict",
    "experiment",
    "gate_evidence",
    "quality_flags",
]

DEFAULT_HARD_GATES: tuple[str, ...] = ("BenchmarkReproduction", "StabilityCertificate")

_DEFAULT_DESIGN: dict[str, Any] = {
    "seed_plan": [0, 1, 2],
    "evaluation_policy": "single_cycle_v1",
    "evidence_kind": "vector",
    "equal_compute": True,
}

_FALSIFICATION_DEFAULT = (
    "the pre-registered prediction fails its recorded decision rule"
)
_OVERTURN_DEFAULT = "replication under the recorded protocol overturns the outcome"


def _probability(
    spec: models.Probability | tuple[float, float] | tuple[float, float, float],
) -> models.Probability:
    if isinstance(spec, models.Probability):
        return spec
    low, high = spec[0], spec[1]
    point = spec[2] if len(spec) > 2 else None
    return models.Probability(low=low, high=high, point=point, method="session_prior")


def experiment(  # ruff: ignore[too-many-arguments]  mirrors the Experiment field surface
    *,
    id_: str,
    question: str,
    prediction: str,
    scope: models.Scope,
    rationale: str = "TODO25 builder-constructed experiment",
    design: Mapping[str, Any] | None = None,
    tier: str = "quick",
    budget: str | None = None,
    prediction_probability: (
        models.Probability | tuple[float, float] | tuple[float, float, float] | None
    ) = None,
    target_beliefs: Sequence[str] = (),
    target_goals: Sequence[str] = (),
    controls: Sequence[str] = ("seed_catalog_baseline",),
    metrics: Sequence[str] = ("accuracy",),
    falsification_criterion: str | None = None,
    overturn_criterion: str | None = None,
    hard_gates: Sequence[str] = DEFAULT_HARD_GATES,
) -> models.Experiment:
    """Build a draft ``Experiment`` with every required field populated.

    ``design`` is merged over defaults that satisfy the §22 hard
    constraints (``seed_plan``/``evaluation_policy``/``evidence_kind``);
    ``tier`` is the budget literal; tier ladders resolve through
    ``Session``/``Profile.tier_budget`` before reaching the builder. Pre-register the returned draft via
    ``CEECStore.pre_register_experiment`` or ``ceec.run.run_experiment``.
    """
    merged_design: dict[str, Any] = {**_DEFAULT_DESIGN, **dict(design or {})}
    return models.Experiment(
        id=id_,
        question=question,
        rationale=rationale,
        scope=scope,
        target_beliefs=list(target_beliefs),
        target_goals=list(target_goals),
        design=merged_design,
        prediction=prediction,
        prediction_probability=(
            _probability(prediction_probability) if prediction_probability else None
        ),
        controls=list(controls),
        metrics=list(metrics),
        budget=budget or cast("_CeecBudget", tier),
        falsification_criterion=falsification_criterion or _FALSIFICATION_DEFAULT,
        overturn_criterion=overturn_criterion or _OVERTURN_DEFAULT,
        hard_gates=list(DEFAULT_HARD_GATES if hard_gates is None else hard_gates),
        created_at=now(),
    )


def quality_flags(  # ruff: ignore[too-many-arguments]  one parameter per §18/§19 gate flag
    *,
    seeds: int = 0,
    matched_control: bool = False,
    evaluation_policy: str = "",
    defect_audit: str = "pass",
    integrity_checks: str = "pass",
    known_levers_exhausted: bool | None = None,
    reproduction: bool | None = None,
    multi_seed_justified: bool | None = None,
    multi_seed_infeasible: bool | None = None,
    extra: Mapping[str, Any] | None = None,
    **open_flags: Any,
) -> dict[str, Any]:
    """Assemble the §18/§19 evidence ``quality`` dict.

    Flag spellings and alphabets are enforced by ``Profile.quality`` at
    ``record_evidence`` (TODO26 T26.B.2); ``None`` flags are omitted.
    """
    flags: dict[str, Any] = {
        "seeds": seeds,
        "matched_control": matched_control,
        "evaluation_policy": evaluation_policy,
        "defect_audit": defect_audit,
        "integrity_checks": integrity_checks,
    }
    for name, value in (
        ("known_levers_exhausted", known_levers_exhausted),
        ("reproduction", reproduction),
        ("multi_seed_justified", multi_seed_justified),
        ("multi_seed_infeasible", multi_seed_infeasible),
    ):
        if value is not None:
            flags[name] = value
    if extra:
        flags.update(extra)
    flags.update(open_flags)
    return flags


def gate_evidence(
    store: CEECStore,
    scope: models.Scope,
    *,
    axes: Sequence[str] = (),
    values: Sequence[float] = (),
    values_ref: str | None = None,
    artifact_refs: Sequence[str] = (),
    notes: str | None = None,
    **flags: Any,
) -> models.Evidence:
    """Record gate-ready evidence: quality flags via :func:`quality_flags`,
    ``vector`` kind when ``values`` are given (payload artifact ingested),
    ``event`` otherwise.

    Exactly one of ``values`` (with ``axes`` + ``values_ref``) or
    ``artifact_refs`` must be supplied.
    """
    quality = quality_flags(**flags)
    if values:
        if not (axes and values_ref):
            raise ValueError("vector gate evidence requires axes and values_ref")
        payload = [
            dict(zip(axes, row, strict=False))
            for row in [
                values[i : i + len(axes)] for i in range(0, len(values), len(axes))
            ]
        ]
        artifact = store.ingest_artifact(
            json.dumps(payload, sort_keys=True).encode(),
            "evidence_payload",
            {"axes": list(axes), "values_ref": values_ref},
        )
        refs = [artifact.id, *artifact_refs]
        return store.record_evidence(
            kind="vector",
            scope=scope,
            artifact_refs=refs,
            quality=quality,
            axes=list(axes),
            values_ref=values_ref,
            notes=notes,
        )
    if not (artifact_refs and axes and values_ref):
        raise ValueError(
            "non-vector gate evidence requires artifact_refs, axes, and values_ref"
        )
    return store.record_evidence(
        kind="event",
        scope=scope,
        artifact_refs=list(artifact_refs),
        quality=quality,
        axes=list(axes),
        values_ref=values_ref,
        notes=notes,
    )


# chance_verdict lives in ceec.stats (TODO26 §2.5); re-exported here.
from ceec.stats import ChanceVerdict, chance_verdict  # ruff: ignore[module-import-not-at-top-of-file]
