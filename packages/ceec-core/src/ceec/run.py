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

__all__ = ["ExperimentRun", "ProbeResult", "record_result", "run_experiment"]

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


def record_result(
    store: CEECStore,
    experiment: models.Experiment,
    result: ProbeResult,
) -> tuple[str, str, str | None]:
    """One-call ingest (TODO26 T26.C.3): artifact → evidence → calibration.

    Returns ``(artifact_id, evidence_id, calibration_id)``; the caller
    owns experiment status transitions and gate evaluation.
    """
    from ceec.builders import gate_evidence
    from ceec.calibration import record_experiment_outcome

    artifact = store.ingest_artifact(
        json.dumps(dict(result.payload), sort_keys=True, default=str).encode(),
        "experiment_payload",
        {
            "experiment_id": experiment.id,
            "mechanisms": sorted(mechanisms_of_design(experiment.design)),
            "code_commit": _code_commit(),
            "seed_policy": experiment.design.get("seed_plan"),
            "evaluation_policy": experiment.design.get("evaluation_policy"),
            "deviations": experiment.design.get("deviations", []),
            "config_hash": _config_hash(experiment.design),
        },
    )
    evidence = gate_evidence(
        store,
        experiment.scope,
        axes=result.axes,
        values=result.values,
        values_ref=result.values_ref or f"artifact:{artifact.id}",
        artifact_refs=[artifact.id],
        notes=result.notes,
        **dict(result.quality),
    )
    calibration = record_experiment_outcome(
        store,
        experiment.id,
        outcome=result.label,
        outcome_boolean=result.outcome_boolean,
        notes=result.notes,
    )
    return artifact.id, evidence.id, calibration.id if calibration else None


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
            + "; ".join(
                f"{c.name} ({c.detail})"
                for c in check_hard_constraints(store, registered)
                if not c.passed
            )
        )
    decision = decide(
        store,
        None,
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

    artifact_id, evidence_id, calibration_id = record_result(store, registered, result)
    store.set_experiment_status(experiment_id, "completed")
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
        artifact_id=artifact_id,
        evidence_id=evidence_id,
        calibration_id=calibration_id,
        evaluation=evaluation,
        outcome=result.label,
    )


def _code_commit() -> str | None:
    import os
    import subprocess  # noqa: S404  git provenance stamp is intentional

    if os.environ.get("CEEC_CODE_COMMIT"):
        return os.environ["CEEC_CODE_COMMIT"]
    try:
        return subprocess.run(  # noqa: S607  pinned read-only git probe
            [  # noqa: S607  pinned read-only git probe
                "git",
                "rev-parse",
                "--short",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        return None


def _config_hash(design: Mapping[str, object]) -> str:
    import hashlib

    blob = json.dumps(dict(design), sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


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
