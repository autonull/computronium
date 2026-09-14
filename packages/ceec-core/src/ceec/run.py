"""Closed-loop experiment runner (TODO25 C.4).

``run_experiment`` makes "every certified measurement is pre-registered
with a recorded Decision" structural rather than procedural: pre-register
(a builder draft or an existing pre-registered experiment) → §22 decision
→ probe execution → artifact/evidence ingestion → calibration outcome →
optional boundary/promotion evaluation.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from ceec.audit import mechanisms_of_design
from ceec.store import StoreError

if TYPE_CHECKING:
    from ceec import models
    from ceec.gates import Evaluation
    from ceec.store import CEECStore

__all__ = ["ExperimentRun", "ProbeResult", "run_experiment"]

Probe = Callable[["models.Experiment"], "ProbeResult"]


@dataclass(frozen=True, slots=True)
class ProbeResult:
    """Probe output ingested by :func:`run_experiment`.

    ``payload`` becomes the artifact; ``quality``/``axes``/``values``/
    ``values_ref`` feed :func:`ceec.builders.gate_evidence` spelling.
    """

    label: str
    outcome_boolean: bool
    payload: Mapping[str, object]
    axes: tuple[str, ...] = ()
    values: tuple[float, ...] = ()
    values_ref: str = ""
    quality: Mapping[str, object] = field(default_factory=dict[str, object])
    notes: str | None = None


@dataclass(frozen=True, slots=True)
class ExperimentRun:
    """Ledger record of one closed-loop execution."""

    experiment_id: str
    status: Literal["completed", "failed"]
    decision_id: str
    artifact_id: str
    evidence_id: str
    calibration_id: str | None
    evaluation: Evaluation | None
    outcome: str
    error: str | None = None


def run_experiment(
    store: CEECStore,
    experiment: str | models.Experiment,
    probe: Probe,
    *,
    evaluate: Literal["boundary", "promotion"] | None = None,
    decision_rationale: str | None = None,
) -> ExperimentRun:
    """Execute one pre-registered measurement end-to-end.

    ``experiment`` is either a draft built by ``ceec.builders.experiment``
    (pre-registered here) or the id of an already pre-registered
    experiment. The §22 decision is recorded against the single-candidate
    pool before the probe runs; a probe exception records ``failed``
    status, ``missing`` evidence, and a failed calibration outcome
    instead of raising.
    """
    from ceec.builders import gate_evidence
    from ceec.calibration import record_experiment_outcome
    from ceec.gates import declare_boundary, promote
    from ceec.selection import check_hard_constraints, decide

    if isinstance(experiment, str):
        registered = store.get_experiment(experiment)
        if registered.status != "pre_registered":
            raise StoreError(
                f"experiment {experiment} is {registered.status!r}; "
                "run_experiment requires a pre_registered experiment"
            )
    else:
        if experiment.status != "draft":
            raise StoreError(
                f"experiment {experiment.id} is {experiment.status!r}; "
                "run_experiment pre-registers draft experiments only"
            )
        registered = store.pre_register_experiment(experiment)
    experiment_id = registered.id

    failed = [c for c in check_hard_constraints(store, registered) if not c.passed]
    if failed:
        raise StoreError(
            f"experiment {experiment_id} failed hard constraints: "
            + "; ".join(f"{c.constraint} ({c.detail})" for c in failed)
        )
    decision = decide(
        store,
        {},
        decision_rationale
        or f"run_experiment: single pre-registered candidate {experiment_id}",
        candidate_ids=[experiment_id],
        overrides=[
            {
                "rationale": (
                    "closed-loop run: the pre-registered experiment is the "
                    "only candidate in this decision's pool"
                ),
                "select_experiment": experiment_id,
            }
        ],
    )

    store.set_experiment_status(experiment_id, "running")
    try:
        result = probe(registered)
    except Exception as exc:
        store.set_experiment_status(experiment_id, "failed")
        failure_artifact = _failure_artifact(store, registered, exc)
        evidence = gate_evidence(
            store,
            registered.scope,
            artifact_refs=[failure_artifact],
            axes=("probe",),
            values_ref=f"artifact:{failure_artifact}",
            seeds=0,
            matched_control=False,
            evaluation_policy=str(registered.design.get("evaluation_policy", "")),
            defect_audit="fail",
            integrity_checks="fail",
            notes=f"probe raised {type(exc).__name__}: {exc}",
        )
        record_experiment_outcome(
            store,
            experiment_id,
            outcome=f"failed:{type(exc).__name__}",
            outcome_boolean=False,
            notes="probe exception; outcome scored False by construction",
        )
        return ExperimentRun(
            experiment_id=experiment_id,
            status="failed",
            decision_id=decision.id,
            artifact_id=failure_artifact,
            evidence_id=evidence.id,
            calibration_id=None,
            evaluation=None,
            outcome=f"failed:{type(exc).__name__}",
            error=str(exc),
        )

    artifact = store.ingest_artifact(
        json.dumps(dict(result.payload), sort_keys=True, default=str).encode(),
        "experiment_payload",
        {
            "experiment_id": experiment_id,
            "mechanisms": sorted(mechanisms_of_design(registered.design)),
        },
    )
    evidence = gate_evidence(
        store,
        registered.scope,
        axes=result.axes,
        values=result.values,
        values_ref=result.values_ref or f"artifact:{artifact.id}",
        artifact_refs=[artifact.id],
        notes=result.notes,
        **dict(result.quality),
    )
    store.set_experiment_status(experiment_id, "completed")
    calibration = record_experiment_outcome(
        store,
        experiment_id,
        outcome=result.label,
        outcome_boolean=result.outcome_boolean,
        notes=result.notes,
    )
    evaluation = None
    if evaluate is not None:
        if not registered.target_beliefs:
            raise StoreError(
                f"evaluate={evaluate!r} requires target_beliefs on {experiment_id}"
            )
        belief_id = registered.target_beliefs[0]
        evaluation = (
            declare_boundary(store, belief_id, f"run_experiment {experiment_id}")
            if evaluate == "boundary"
            else promote(store, belief_id, f"run_experiment {experiment_id}")
        )
    return ExperimentRun(
        experiment_id=experiment_id,
        status="completed",
        decision_id=decision.id,
        artifact_id=artifact.id,
        evidence_id=evidence.id,
        calibration_id=calibration.id if calibration else None,
        evaluation=evaluation,
        outcome=result.label,
    )


def _failure_artifact(
    store: CEECStore, experiment: models.Experiment, exc: Exception
) -> str:
    from ceec.store import now

    return store.ingest_artifact(
        json.dumps(
            {
                "experiment_id": experiment.id,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "at": now(),
            },
            sort_keys=True,
        ).encode(),
        "experiment_failure",
        {"experiment_id": experiment.id},
    ).id
