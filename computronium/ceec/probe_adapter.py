"""Adapter converting probe outputs into CEEC artifacts, evidence, and derived.

Probe output contract (E.1):

    {
        "status": "ok" | "inert" | "missing",   # inert=invalid coordinate,
                                                # missing=infrastructure failure
        "kind": <evidence kind>,                # structured kinds preserved
        "scope": {...},                         # Scope fields
        "axes": [...],                          # required for structured kinds
        "values": <json-serializable data>,     # structured payload
        "quality": {...},                       # seeds, matched_control, ...
        "defects": [...],
        "notes": str,
        "summary": {...},                       # optional scalar summary -> derived
        "summary_operator": str,                # default "scalar_summary"
    }
"""

from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from computronium.ceec import bootstrap as _bootstrap
from computronium.ceec import models
from computronium.ceec.store import CEECStore, StoreError

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from computronium.ceec import audit, gates


@dataclass(frozen=True, slots=True)
class ProbeEvidence:
    artifact: models.Artifact
    evidence: models.Evidence
    derived: models.Derived | None


def probe_scope(probe_output: dict[str, Any]) -> models.Scope:
    scope = probe_output.get("scope", {})
    return models.Scope(
        domain=scope.get("domain", "probe"),
        substrate=tuple(scope.get("substrate", ())),
        geometry=tuple(scope.get("geometry", ())),
        credit=tuple(scope.get("credit", ())),
        budget=scope.get("budget"),
        code_commit=scope.get("code_commit"),
        extra={
            k: v
            for k, v in scope.items()
            if k
            not in {
                "domain",
                "substrate",
                "geometry",
                "credit",
                "budget",
                "code_commit",
            }
        },
    )


def _evidence_kind(probe_output: dict[str, Any]) -> str:
    status = probe_output.get("status", "ok")
    if status == "inert":
        return "inert"
    if status == "missing":
        return "missing"
    kind = probe_output.get("kind", "scalar")
    if kind not in models.STRUCTURED_KINDS and kind not in {"scalar", "interval"}:
        raise StoreError(f"unknown probe evidence kind {kind!r}")
    return kind


def record_probe_result(
    store: CEECStore,
    probe_output: dict[str, Any],
    probe_name: str,
    id_: str | None = None,
) -> ProbeEvidence:
    kind = _evidence_kind(probe_output)
    scope = probe_scope(probe_output)
    payload = json.dumps(
        {"probe": probe_name, "values": probe_output.get("values")},
        sort_keys=True,
    ).encode()
    artifact = store.ingest_artifact(
        payload,
        "probe_result",
        {"probe": probe_name, "status": probe_output.get("status")},
    )
    status = probe_output.get("status", "ok")
    notes = probe_output.get("notes")
    if status in {"inert", "missing"} and not notes:
        notes = f"probe {probe_name} returned {status}"
    evidence = store.record_evidence(
        kind=kind,
        scope=scope,
        artifact_refs=[artifact.id],
        axes=probe_output.get("axes") if kind in models.STRUCTURED_KINDS else None,
        values_ref=artifact.uri,
        quality=dict(probe_output.get("quality", {})),
        defects=list(probe_output.get("defects", [])),
        notes=notes,
        id_=id_,
    )
    derived = None
    if probe_output.get("summary") is not None:
        derived = store.record_derived(
            type_="scalar_summary",
            operator=probe_output.get("summary_operator", "aggregate"),
            inputs={"evidence": [evidence.id]},
            scope=scope,
            value=probe_output["summary"],
            checks=["derived from structured primary evidence"],
        )
    return ProbeEvidence(artifact, evidence, derived)


def load_probe_output(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True, slots=True)
class IngestVerdict:
    """Result of the shared post-probe governance loop (``ingest_verdict``)."""

    probe: ProbeEvidence
    evaluation: gates.Evaluation
    calibration: models.CalibrationRecord | None
    violations: Sequence[audit.Finding]


def ingest_verdict(  # ruff: ignore[too-many-arguments]
    store: CEECStore,
    *,
    probe_name: str,
    probe_output: dict[str, Any],
    belief_id: str,
    new_interval: tuple[float, float],
    rationale: str,
    outcome: str,
    outcome_boolean: bool | None,
    notes: str,
    evidence_weight: str = "medium",
    experiment_config: Path | None = None,
) -> IngestVerdict:
    """Link probe evidence → belief revision → gates → calibration → audit.

    The shared governance loop previously copy-pasted into each
    ``scripts/probes/x_*.py`` (see TODO19 improvement notes). When
    ``experiment_config`` is given, the probe's pre-registration YAML is
    registered if missing (idempotent) BEFORE any evidence write — the
    X-TPC-002 root-cause lesson. Selection (``decide``) stays at the round
    level, outside this helper.
    """
    from computronium.ceec import audit, calibration, gates

    if experiment_config is not None:
        experiment = _bootstrap.experiment_from_config(experiment_config)
        with contextlib.suppress(StoreError):
            store.pre_register_experiment(experiment)

    probe_result = record_probe_result(store, probe_output, probe_name)
    store._link(
        store._conn,
        "belief_evidence",
        "belief_id",
        belief_id,
        "evidence_id",
        [probe_result.evidence.id],
    )
    store._conn.commit()
    store.update_belief(
        belief_id,
        models.Probability(
            low=new_interval[0],
            high=new_interval[1],
            method="heuristic_interval_based_on_gate_evidence",
        ),
        "medium",
        evidence_weight,
        "narrow",
        "open",
        f"{probe_name}: {rationale}",
    )
    evaluation = gates.evaluate_promotion(store, belief_id)
    record = calibration.record_experiment_outcome(
        store, probe_name, outcome, outcome_boolean, notes=notes
    )
    violations = [f for f in audit.run_audit(store) if f.severity == "violation"]
    return IngestVerdict(probe_result, evaluation, record, violations)
