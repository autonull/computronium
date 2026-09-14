"""Ledger rollup report (TODO26 T26.D.2, migrated from the lab layer)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ceec.store import CEECStore


def render_ledger(
    store: CEECStore, *, record_rollups: bool = False
) -> tuple[str, dict[str, object]]:
    """Ledger rollup — experiments, beliefs, calibration, decisions (T25.C.3).

    Returns ``(markdown, data)``; the calibration section carries the §24
    ``review_flags`` and per-belief Brier drift, the decisions section the
    ``audit_decisions`` findings. Read-only by default: ``record_rollups``
    additionally records a recomputable ``summary`` Derived row (T26.F.4).
    """
    from ceec.audit import audit_decisions
    from ceec.calibration import belief_drift, calibration_report, review_flags

    experiments: dict[str, list[str]] = {}
    for experiment in store.all_experiments():
        experiments.setdefault(experiment.status, []).append(experiment.id)
    beliefs: dict[str, list[str]] = {}
    belief_rows = store._conn.execute("SELECT id FROM beliefs").fetchall()
    for row in belief_rows:
        beliefs.setdefault(store.current_status(row["id"]), []).append(row["id"])
    calibration = dict(calibration_report(store))
    flags = review_flags(calibration)
    calibration["review_flags"] = flags
    drift = {
        belief_id: {"drift": entry["drift"], "flagged": entry["flagged"]}
        for belief_id, entry in belief_drift(store).items()
        if entry["flagged"]
    }
    findings, audit_summary = audit_decisions(store)
    decision_rows = store._conn.execute(
        "SELECT id, selected_experiment, rationale FROM decisions ORDER BY timestamp"
    ).fetchall()
    data: dict[str, object] = {
        "experiments": experiments,
        "beliefs": beliefs,
        "calibration": calibration,
        "belief_drift": drift,
        "decisions": {
            "count": len(decision_rows),
            "audit": audit_summary,
            "findings": [
                {"check": f.check, "severity": f.severity, "detail": f.detail}
                for f in findings
            ],
        },
    }
    lines = ["# Ledger Report", ""]
    lines.append("## Experiments")
    lines.append("")
    for status in sorted(experiments):
        lines.append(
            f"- **{status}** ({len(experiments[status])}): "
            + ", ".join(experiments[status])
        )
    lines.extend(["", "## Beliefs", ""])
    for status in sorted(beliefs):
        lines.append(
            f"- **{status}** ({len(beliefs[status])}): " + ", ".join(beliefs[status])
        )
    lines.extend(["", "## Calibration", ""])
    lines.append(
        f"- records: {calibration['calibration_records']} "
        f"(scored {calibration['scored_records']}), "
        f"mean Brier {calibration['mean_brier']}"
    )
    lines.append(
        f"- promotions {calibration['promotions']}, boundaries "
        f"{calibration['boundaries']}, quarantines {calibration['quarantines']}, "
        f"override rate {calibration['override_rate']:.2f}"
    )
    lines.append(f"- review flags: {flags or 'none'}")
    lines.append(
        "- Brier drift > tau: "
        + (
            ", ".join(f"{b} ({e['drift']:.2f})" for b, e in drift.items())
            if drift
            else "none"
        )
    )
    lines.extend(["", "## Decisions", ""])
    lines.append(
        f"- {audit_summary['decisions']} decisions; audit findings: "
        f"{audit_summary['findings']}"
    )
    for finding in data["decisions"]["findings"]:  # type: ignore[index]
        lines.append(
            f"  - [{finding['severity']}] {finding['check']}: {finding['detail']}"
        )
    lines.append("")
    if record_rollups:
        from ceec.models import Scope

        derived = store.record_derived(
            type_="summary",
            operator="ledger_rollup_v1",
            inputs={},
            scope=Scope.of(domain="report"),
            value=data,
            provenance={"recomputable": True, "rollup": True},
        )
        data["rollup_derived"] = derived.id
    return "\n".join(lines), data
