"""CEEC ledger audit (Phase H.3).

Audits detect violations; they never mutate the ledger.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ceec import models
from ceec.gates import effective_status
from ceec.store import StoreError

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
    findings.extend(_ledger_role_scope(store))
    findings.extend(_single_seed_promotion_attempt(store))
    findings.extend(_untested_lever_boundary(store))
    findings.extend(_silent_scalarization(store))
    return findings


def _single_seed_promotion_attempt(store: CEECStore) -> list[Finding]:
    """§27 anti-pattern: promotion from evidence with fewer than 3 seeds."""
    out = []
    for belief_id in store.beliefs_by_status("promoted"):
        seeds = []
        justified = False
        for ref in _belief_evidence(store, belief_id):
            evidence = store.get_evidence(ref)
            seeds.append(int(evidence.quality.get("seeds", 0)))
            justified = (
                justified or evidence.quality.get("multi_seed_justified") is True
            )
        if seeds and max(seeds) < 3 and not justified:
            out.append(
                Finding(
                    "single_seed_promotion_attempt",
                    "violation",
                    f"{belief_id} promoted with max seeds={max(seeds)}",
                )
            )
    return out


def _untested_lever_boundary(store: CEECStore) -> list[Finding]:
    """§27 anti-pattern: boundary declared without known_levers_exhausted."""
    out = []
    for belief_id in store.beliefs_by_status("boundary"):
        exhausted = any(
            store.get_evidence(ref).quality.get("known_levers_exhausted") is True
            for ref in _belief_evidence(store, belief_id)
        )
        if not exhausted:
            out.append(
                Finding(
                    "untested_lever_boundary_declaration",
                    "warning",
                    f"{belief_id} at boundary without known_levers_exhausted",
                )
            )
    return out


def _silent_scalarization(store: CEECStore) -> list[Finding]:
    """§27 anti-pattern: structured evidence whose payload is scalar-only."""
    out = []
    rows = store._conn.execute(
        "SELECT id FROM evidence WHERE kind IN ('vector','tensor','curve')"
    ).fetchall()
    for r in rows:
        evidence = store.get_evidence(r["id"])
        for artifact_id in store.evidence_artifacts(evidence.id):
            artifact = store.get_artifact(artifact_id)
            from pathlib import Path

            try:
                payload = json.loads(Path(artifact.uri).read_text(encoding="utf-8"))
            except Exception:  # ruff: ignore[try-except-continue]  unreadable payloads flagged by missing-artifact audit
                continue
            values = _payload_numeric_rows(payload)
            if values and all(not isinstance(v, dict) for v in values):
                out.append(
                    Finding(
                        "silent_scalarization",
                        "warning",
                        f"{evidence.id} kind={evidence.kind} payload is "
                        "scalar-only (structured kind reduced to scalar)",
                    )
                )
    return out


def _payload_numeric_rows(payload: object) -> list[object]:
    if isinstance(payload, dict):
        rows = payload.get("rows") or payload.get("values")
        return rows if isinstance(rows, list) else []
    return payload if isinstance(payload, list) else []


def _belief_evidence(store: CEECStore, belief_id: str) -> list[str]:
    rows = store._conn.execute(
        "SELECT evidence_id FROM belief_evidence WHERE belief_id = ?", (belief_id,)
    ).fetchall()
    return [r["evidence_id"] for r in rows]


def _ledger_role_scope(store: CEECStore) -> list[Finding]:
    """TODO26 T26.A.2: campaign ledgers may not gate against instruments."""
    if store.role.value != "campaign":
        return []
    out = []
    for experiment in [
        *store.experiments_by_status("running"),
        *store.experiments_by_status("completed"),
    ]:
        instruments = experiment.design.get("instruments", [])
        if instruments:
            out.append(
                Finding(
                    "campaign_ledger_instrument_gating",
                    "violation",
                    f"{experiment.id} gates against instruments {instruments} "
                    "in a campaign ledger",
                )
            )
    return out


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
        if not scope.domain or len(scope.dims) <= 1:
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


_UNRESOLVED_STATUSES = {"draft", "pre_registered", "running"}


def _audit_one_decision(
    store: CEECStore,
    row: Any,
    experiment_mechanisms: dict[str, set[str]],
    blocks: list[tuple[str, str]],
    counters: dict[str, int],
) -> list[Finding]:
    decision_id = row["id"]
    findings: list[Finding] = []
    selected = row["selected_experiment"]
    if selected:
        try:
            status = store.get_experiment(selected).status
        except StoreError:
            findings.append(
                Finding(
                    "selected_experiment_missing",
                    "violation",
                    f"{decision_id} selected missing experiment {selected!r}",
                )
            )
            return findings
        if status in _UNRESOLVED_STATUSES:
            counters["unresolved"] += 1
            findings.append(
                Finding(
                    "selected_experiment_unresolved",
                    "warning",
                    f"{decision_id} selected {selected} still {status!r}",
                )
            )
    for override in json.loads(row["overrides"]):
        if not override.get("rationale"):
            counters["unjustified"] += 1
            findings.append(
                Finding(
                    "override_without_rationale",
                    "violation",
                    f"{decision_id} override without rationale",
                )
            )
    for candidate in json.loads(row["candidate_experiments"]):
        mechanisms = experiment_mechanisms.get(candidate, set())
        blocked = [
            created
            for created, mechanism in blocks
            if mechanism in mechanisms and created > row["timestamp"]
        ]
        if blocked:
            counters["blocked"] += 1
            findings.append(
                Finding(
                    "candidate_overlaps_measurement_block",
                    "warning",
                    f"{decision_id} candidate {candidate} blocked by a later "
                    f"measurement_block ({blocked[0]})",
                )
            )
    return findings


def mechanisms_of_design(design: dict[str, Any]) -> set[str]:
    """Mechanism names referenced by an experiment design (any nesting)."""
    mechanisms: set[str] = set()

    def _walk(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"mechanism", "contenders"}:
                    if isinstance(value, str):
                        mechanisms.add(value)
                    elif isinstance(value, list):
                        mechanisms.update(str(v) for v in value)
                _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(design)
    return mechanisms


def _measurement_block_mechanisms(store: CEECStore) -> list[tuple[str, str]]:
    """(created_at, mechanism) pairs from ``measurement_block`` artifacts."""
    from pathlib import Path

    rows = store._conn.execute(
        "SELECT created_at, uri FROM artifacts WHERE type = 'measurement_block'"
    ).fetchall()
    out = []
    for r in rows:
        try:
            payload = json.loads(Path(r["uri"]).read_text(encoding="utf-8"))
        except Exception:  # ruff: ignore[try-except-continue]  unreadable payloads are flagged by the missing-artifact audit
            continue
        mechanism = payload.get("mechanism") if isinstance(payload, dict) else None
        if mechanism:
            out.append((r["created_at"], str(mechanism)))
    return out


def audit_decisions(
    store: CEECStore, *, record: bool = False
) -> tuple[list[Finding], dict[str, object]]:
    """Decision quality audit (TODO25 C.2), per §22 Decision:

    - did the selected experiment resolve to a terminal status?
    - is every override justified?
    - does the candidate set overlap later ``measurement_block`` payloads
      (a candidate that was structurally unmeasurable)?

    Audits are read-only by convention; ``record=True`` additionally
    records a ``decision_quality`` Derived with the summary (the
    append-only ledger keeps every audit run).
    """
    findings: list[Finding] = []
    decisions = store._conn.execute(
        "SELECT id, timestamp, selected_experiment, overrides, "
        "candidate_experiments FROM decisions ORDER BY timestamp"
    ).fetchall()
    experiment_mechanisms = {
        e.id: mechanisms_of_design(e.design) for e in store.all_experiments()
    }
    blocks = _measurement_block_mechanisms(store)
    counters = {"unresolved": 0, "unjustified": 0, "blocked": 0}
    for row in decisions:
        findings.extend(
            _audit_one_decision(store, row, experiment_mechanisms, blocks, counters)
        )
    summary: dict[str, object] = {
        "decisions": len(decisions),
        "findings": len(findings),
        "selected_unresolved": counters["unresolved"],
        "unjustified_overrides": counters["unjustified"],
        "candidate_block_overlap": counters["blocked"],
        "by_check": {
            check: sum(1 for f in findings if f.check == check)
            for check in sorted({f.check for f in findings})
        },
    }
    if record:
        derived = store.record_derived(
            type_="decision_quality",
            operator="audit_decisions_v1",
            inputs={},
            scope=models.Scope.of(domain="audit", extra={"check": "decision_quality"}),
            value=summary,
            provenance={"decisions": [row["id"] for row in decisions]},
        )
        summary["derived_ref"] = derived.id
    return findings, summary
