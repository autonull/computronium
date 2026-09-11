"""CEEC ledger audit (Phase H.3).

Audits detect violations; they never mutate the ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ceec import models
from ceec.gates import effective_status

if TYPE_CHECKING:
    from ceec.store import CEECStore


@dataclass(frozen=True, slots=True)
class Finding:
    check: str
    severity: str  # "violation" | "warning"
    detail: str


def run_audit(store: CEECStore) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_beliefs_without_evidence(store))
    findings.extend(_beliefs_without_scope(store))
    findings.extend(_scalar_only_structured_evidence(store))
    findings.extend(_status_changes_without_gates(store))
    findings.extend(_decisions_without_rationale(store))
    findings.extend(_quarantined_dependencies_in_active_experiments(store))
    findings.extend(_missing_artifacts_for_evidence(store))
    findings.extend(_missing_calibration_outcomes(store))
    return findings


def _all_belief_ids(store: CEECStore) -> list[str]:
    return [r["id"] for r in store._conn.execute("SELECT id FROM beliefs").fetchall()]


def _beliefs_without_evidence(store: CEECStore) -> list[Finding]:
    out = []
    for belief_id in _all_belief_ids(store):
        has = store._conn.execute(
            "SELECT 1 FROM belief_evidence WHERE belief_id = ? "
            "UNION SELECT 1 FROM belief_derived WHERE belief_id = ? LIMIT 1",
            (belief_id, belief_id),
        ).fetchone()
        if has is None:
            out.append(Finding("belief_without_evidence", "violation", f"{belief_id}"))
    return out


def _beliefs_without_scope(store: CEECStore) -> list[Finding]:
    out = []
    for belief_id in _all_belief_ids(store):
        belief = store.get_belief(belief_id)
        scope = belief.scope
        if not scope.domain or not (
            scope.substrate or scope.geometry or scope.credit or scope.extra
        ):
            out.append(
                Finding(
                    "belief_without_scope",
                    "violation",
                    f"{belief_id}: domain={scope.domain!r}",
                )
            )
    return out


def _scalar_only_structured_evidence(store: CEECStore) -> list[Finding]:
    out = []
    rows = store._conn.execute(
        "SELECT id, kind, axes, values_ref FROM evidence"
    ).fetchall()
    for r in rows:
        if r["kind"] in models.STRUCTURED_KINDS and not (r["axes"] and r["values_ref"]):
            out.append(
                Finding(
                    "scalar_only_structured_evidence",
                    "violation",
                    f"{r['id']} kind={r['kind']} missing axes/values_ref",
                )
            )
    return out


def _status_changes_without_gates(store: CEECStore) -> list[Finding]:
    rows = store._conn.execute(
        "SELECT id, belief_id, to_status, gate_refs FROM status_changes"
    ).fetchall()
    out = []
    for r in rows:
        if r["to_status"] in {"promoted", "boundary"} and not r["gate_refs"]:
            out.append(
                Finding(
                    "status_change_without_gates",
                    "violation",
                    f"{r['id']} -> {r['to_status']} with no gate refs",
                )
            )
    return out


def _decisions_without_rationale(store: CEECStore) -> list[Finding]:
    rows = store._conn.execute(
        "SELECT id, rationale, selected_experiment FROM decisions"
    ).fetchall()
    return [
        Finding(
            "decision_without_rationale",
            "violation",
            f"{r['id']} selected={r['selected_experiment']!r} with empty rationale",
        )
        for r in rows
        if r["selected_experiment"] and not r["rationale"]
    ]


def _quarantined_dependencies_in_active_experiments(store: CEECStore) -> list[Finding]:
    out = []
    for experiment in [
        *store.experiments_by_status("running"),
        *store.experiments_by_status("completed"),
    ]:
        for belief_id in experiment.target_beliefs:
            eff = effective_status(store, belief_id)
            if eff.effective == "quarantined":
                out.append(
                    Finding(
                        "quarantined_dependency_in_active_experiment",
                        "violation",
                        f"{experiment.id} targets quarantined {belief_id}",
                    )
                )
    return out


def _missing_artifacts_for_evidence(store: CEECStore) -> list[Finding]:
    rows = store._conn.execute(
        "SELECT evidence_id, artifact_id FROM evidence_artifacts"
    ).fetchall()
    out = []
    for r in rows:
        artifact = store.get_artifact(r["artifact_id"])
        from pathlib import Path

        if not Path(artifact.uri).exists():
            out.append(
                Finding(
                    "missing_artifact_file",
                    "violation",
                    f"evidence {r['evidence_id']} references missing {artifact.uri}",
                )
            )
    return out


def _missing_calibration_outcomes(store: CEECStore) -> list[Finding]:
    out = []
    for experiment in store.experiments_by_status("completed"):
        if experiment.prediction_probability is None:
            continue
        recorded = store._conn.execute(
            "SELECT 1 FROM calibration_records WHERE experiment_id = ? LIMIT 1",
            (experiment.id,),
        ).fetchone()
        if recorded is None:
            out.append(
                Finding(
                    "missing_calibration_outcome",
                    "warning",
                    f"{experiment.id} completed with prediction probability "
                    "but no calibration record",
                )
            )
    return out
