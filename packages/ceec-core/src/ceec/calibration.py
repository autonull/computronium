"""Calibration tracker and report (CEEC Phase H)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ceec.store import StoreError

if TYPE_CHECKING:
    from ceec import models
    from ceec.store import CEECStore


def record_experiment_outcome(
    store: CEECStore,
    experiment_id: str,
    outcome: str,
    outcome_boolean: bool | None,
    notes: str | None = None,
) -> models.CalibrationRecord | None:
    """Close the loop: compare a completed experiment's pre-registered
    prediction probability with the observed outcome.

    Returns None when the experiment carried no explicit probability.
    """
    store._require("experiments", experiment_id)
    experiment = store.get_experiment(experiment_id)
    if experiment.prediction_probability is None:
        return None
    return store.record_calibration(
        prediction=experiment.prediction,
        experiment_id=experiment_id,
        belief_id=experiment.target_beliefs[0] if experiment.target_beliefs else None,
        predicted_probability=experiment.prediction_probability,
        outcome=outcome,
        outcome_boolean=outcome_boolean,
        scope=experiment.scope,
        notes=notes,
    )


def calibration_report(store: CEECStore) -> dict[str, Any]:
    records = store.calibration_records()
    scored = [r for r in records if r.brier_score is not None]
    predicted = [r for r in records if r.outcome_boolean is not None]
    observed_rate = (
        sum(1 for r in predicted if r.outcome_boolean) / len(predicted)
        if predicted
        else None
    )
    promotions = _status_change_count(store, to_status="promoted")
    reversals = _status_change_count(
        store, from_status="promoted", to_status__ne="promoted"
    )
    boundaries = _status_change_count(store, to_status="boundary")
    reopens = _status_change_count(store, from_status="boundary", to_status="open")
    quarantines = _status_change_count(store, to_status="quarantined")
    decisions = store._conn.execute("SELECT overrides FROM decisions").fetchall()
    total_overrides = sum(len(_json_loads(r["overrides"])) for r in decisions)
    total_decisions = len(decisions)
    return {
        "calibration_records": len(records),
        "scored_records": len(scored),
        "mean_brier": _mean([
            r.brier_score for r in scored if r.brier_score is not None
        ]),
        "mean_log_score": _mean([
            r.log_score for r in records if r.log_score is not None
        ]),
        "predicted_outcomes": len(predicted),
        "observed_success_rate": observed_rate,
        "promotions": promotions,
        "promotion_reversal_rate": reversals / promotions if promotions else 0.0,
        "boundaries": boundaries,
        "boundary_reopen_rate": reopens / boundaries if boundaries else 0.0,
        "quarantines": quarantines,
        "override_rate": (
            total_overrides / total_decisions if total_decisions else 0.0
        ),
    }


def _status_change_count(
    store: CEECStore,
    to_status: str | None = None,
    from_status: str | None = None,
    to_status__ne: str | None = None,
) -> int:
    clauses, params = [], []
    if to_status:
        clauses.append("to_status = ?")
        params.append(to_status)
    if to_status__ne:
        clauses.append("to_status != ?")
        params.append(to_status__ne)
    if from_status:
        clauses.append("from_status = ?")
        params.append(from_status)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT COUNT(*) AS n FROM status_changes {where}"  # ruff: ignore[hardcoded-sql-expression]  clause built internally
    row = store._conn.execute(sql, params).fetchone()
    return row["n"]


def _json_loads(text: str) -> Any:
    import json

    return json.loads(text)


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def review_flags(report: dict[str, Any]) -> list[str]:
    """Calibration review triggers (docs/ceec/CALIBRATION_POLICY.md)."""
    flags = []
    if report["promotion_reversal_rate"] > 0.20:
        flags.append("promotion_reversal_rate_high")
    if report["boundary_reopen_rate"] > 0.20:
        flags.append("boundary_reopen_rate_high")
    if report["override_rate"] > 0.20:
        flags.append("override_rate_high")
    if report["quarantines"] >= 3:
        flags.append("quarantine_rate_spike")
    return flags


DRIFT_TAU = 0.15


def belief_drift(
    store: CEECStore, *, tau: float = DRIFT_TAU
) -> dict[str, dict[str, Any]]:
    """§24 drift review cadence (TODO25 C.5): per-belief Brier drift
    across calibration rounds, chronologically ordered.

    A belief whose Brier spread exceeds ``tau`` is flagged for review;
    the review itself is recorded via :func:`review_belief`.
    """
    series: dict[str, list[tuple[str, float]]] = {}
    for record in store.calibration_records():
        if record.belief_id and record.brier_score is not None:
            series.setdefault(record.belief_id, []).append((
                record.created_at,
                record.brier_score,
            ))
    out: dict[str, dict[str, Any]] = {}
    for belief_id, points in sorted(series.items()):
        points.sort()
        values = [b for _, b in points]
        drift = max(values) - min(values)
        out[belief_id] = {
            "brier_series": values,
            "drift": drift,
            "flagged": drift > tau,
        }
    return out


def review_belief(
    store: CEECStore,
    belief_id: str,
    *,
    action: str,
    reason: str,
    actor: str | None = None,
    trigger: str | None = None,
    evidence_refs: list[str] | None = None,
) -> models.StatusChange | models.InstrumentNote:
    """Record a drift review's outcome (TODO25 C.5).

    ``action="acknowledge"`` notes the review on the belief (an open
    belief has no legal status transition); ``"reopen"``/``"quarantine"``
    move the belief through the gated status machine, which records the
    reviewed state as a ``StatusChange``.
    """
    store._require("beliefs", belief_id)
    if action == "acknowledge":
        return store.record_instrument_note(
            belief_id,
            f"drift review ({actor or 'reviewer'}): {reason}",
            kind="hygiene",
        )
    from ceec.gates import quarantine, reopen

    if action == "reopen":
        if trigger is None:
            raise StoreError("reopen review requires a trigger")
        return reopen(store, belief_id, trigger, reason, evidence_refs=evidence_refs)
    if action == "quarantine":
        if trigger is None:
            raise StoreError("quarantine review requires a trigger")
        return quarantine(
            store, belief_id, trigger, reason, evidence_refs=evidence_refs
        )[0]
    raise ValueError(f"unknown review action {action!r}")
