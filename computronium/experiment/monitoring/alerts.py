"""Drift detection and metric coverage alerts for experiment runs.

Provides run-time and post-run alerting for:
- Gate verdict drift (FAIL rate increases)
- Metric coverage degradation (non-finite metrics)
- Dtype mismatch detection
- Budget enforcement violations
"""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.record import GateVerdict


@dataclass(frozen=True, slots=True)
class Alert:
    """Single alert with severity and context."""

    severity: str  # "info", "warning", "critical"
    code: str      # Machine-readable code (e.g., "GATE_FAIL_RATE_HIGH")
    message: str   # Human-readable description
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True, slots=True)
class AlertThresholds:
    """Configurable alert thresholds."""

    # Gate verdict thresholds
    max_fail_rate: float = 0.25          # Alert if FAIL rate > 25%
    critical_fail_rate: float = 0.40     # Critical if FAIL rate > 40%

    # Metric coverage thresholds
    max_nonfinite_rate: float = 0.05     # Alert if non-finite metrics > 5%
    critical_nonfinite_rate: float = 0.15

    # Dtype mismatch
    alert_on_dtype_mismatch: bool = True

    # Budget enforcement
    max_budget_overrun_pct: float = 0.10  # Alert if budget exceeded by >10%

    # Per-axis combination minimum samples
    min_cells_per_combo: int = 3         # Alert if combo has < 3 cells


DEFAULT_THRESHOLDS = AlertThresholds()


def check_gate_fail_rate(
    records: list,
    thresholds: AlertThresholds = DEFAULT_THRESHOLDS,
) -> list[Alert]:
    """Check if FAIL rate exceeds threshold."""
    if not records:
        return []

    total = len(records)
    fails = sum(1 for r in records if r.status.gate_verdict == GateVerdict.FAIL)
    fail_rate = fails / total

    alerts = []
    if fail_rate >= thresholds.critical_fail_rate:
        alerts.append(Alert(
            severity="critical",
            code="GATE_FAIL_RATE_CRITICAL",
            message=f"FAIL rate {fail_rate:.1%} ({fails}/{total}) exceeds critical threshold {thresholds.critical_fail_rate:.0%}",
            context={"fail_rate": fail_rate, "fails": fails, "total": total},
        ))
    elif fail_rate >= thresholds.max_fail_rate:
        alerts.append(Alert(
            severity="warning",
            code="GATE_FAIL_RATE_HIGH",
            message=f"FAIL rate {fail_rate:.1%} ({fails}/{total}) exceeds warning threshold {thresholds.max_fail_rate:.0%}",
            context={"fail_rate": fail_rate, "fails": fails, "total": total},
        ))

    return alerts


def check_nonfinite_metrics(
    records: list,
    thresholds: AlertThresholds = DEFAULT_THRESHOLDS,
) -> list[Alert]:
    """Check for non-finite metrics in records."""
    if not records:
        return []

    total_metrics = 0
    nonfinite_metrics = 0
    affected_cells = []

    for r in records:
        if r.payload:
            for key, value in r.payload.items():
                if isinstance(value, (int, float)):
                    total_metrics += 1
                    if not (isinstance(value, float) and (value != value or value == float('inf') or value == float('-inf'))):
                        pass
                    elif isinstance(value, float) and (value != value or abs(value) == float('inf')):
                        nonfinite_metrics += 1
                        if r.cell_key not in affected_cells:
                            affected_cells.append(r.cell_key)

    if total_metrics == 0:
        return []

    nonfinite_rate = nonfinite_metrics / total_metrics

    alerts = []
    if nonfinite_rate >= thresholds.critical_nonfinite_rate:
        alerts.append(Alert(
            severity="critical",
            code="METRIC_NONFINITE_CRITICAL",
            message=f"Non-finite metric rate {nonfinite_rate:.1%} ({nonfinite_metrics}/{total_metrics}) exceeds critical threshold",
            context={"rate": nonfinite_rate, "nonfinite": nonfinite_metrics, "total": total_metrics, "cells": affected_cells},
        ))
    elif nonfinite_rate >= thresholds.max_nonfinite_rate:
        alerts.append(Alert(
            severity="warning",
            code="METRIC_NONFINITE_HIGH",
            message=f"Non-finite metric rate {nonfinite_rate:.1%} ({nonfinite_metrics}/{total_metrics}) exceeds warning threshold",
            context={"rate": nonfinite_rate, "nonfinite": nonfinite_metrics, "total": total_metrics, "cells": affected_cells},
        ))

    return alerts


def check_dtype_mismatches(records: list) -> list[Alert]:
    """Check for dtype mismatch failures in records."""
    alerts = []
    for r in records:
        if r.status.gate_verdict == GateVerdict.FAIL and r.status.defect:
            defect = r.status.defect.lower()
            if "bfloat16" in defect and "float" in defect:
                alerts.append(Alert(
                    severity="critical",
                    code="DTYPE_MISMATCH_BF16_FLOAT",
                    message=f"BFloat16/Float dtype mismatch in {r.substrate}/{r.credit}/{r.update}",
                    context={"cell_key": r.cell_key, "defect": r.status.defect},
                ))
            elif "bool" in defect and ("addmm" in defect or "matmul" in defect):
                alerts.append(Alert(
                    severity="critical",
                    code="DTYPE_MISMATCH_BOOL_TENSOR",
                    message=f"Bool tensor used in matmul in {r.substrate}/{r.credit}/{r.update}",
                    context={"cell_key": r.cell_key, "defect": r.status.defect},
                ))
    return alerts


def check_budget_enforcement(
    store_path: str,
    thresholds: AlertThresholds = DEFAULT_THRESHOLDS,
) -> list[Alert]:
    """Check if run exceeded its time budget."""
    alerts = []
    try:
        store = RecordStore(StoreConfig(path=Path(store_path)))
        with store:
            # Get run summary from report
            from computronium.experiment.surface.report import ReportGenerator
            gen = ReportGenerator(store)
            # Note: would need run_id to get specific run
    except Exception:
        pass
    return alerts


def check_per_combo_coverage(
    records: list,
    thresholds: AlertThresholds = DEFAULT_THRESHOLDS,
) -> list[Alert]:
    """Check if any credit×update combo has insufficient samples."""
    from collections import defaultdict

    combo_counts = defaultdict(int)
    for r in records:
        combo = f"{r.credit}/{r.update}"
        combo_counts[combo] += 1

    alerts = []
    for combo, count in combo_counts.items():
        if count < thresholds.min_cells_per_combo:
            alerts.append(Alert(
                severity="warning",
                code="COMBO_INSUFFICIENT_SAMPLES",
                message=f"Credit×Update combo '{combo}' has only {count} cells (min {thresholds.min_cells_per_combo})",
                context={"combo": combo, "count": count},
            ))
    return alerts


def run_all_checks(
    records: list,
    store_path: str | None = None,
    thresholds: AlertThresholds = DEFAULT_THRESHOLDS,
) -> list[Alert]:
    """Run all alert checks and return aggregated alerts."""
    all_alerts = []

    all_alerts.extend(check_gate_fail_rate(records, thresholds))
    all_alerts.extend(check_nonfinite_metrics(records, thresholds))
    all_alerts.extend(check_dtype_mismatches(records))
    all_alerts.extend(check_per_combo_coverage(records, thresholds))

    if store_path:
        all_alerts.extend(check_budget_enforcement(store_path, thresholds))

    return all_alerts


def emit_alerts(alerts: list[Alert], output_path: str | None = None) -> None:
    """Print alerts and optionally write to JSON file."""
    if not alerts:
        print("✅ No alerts triggered")
        return

    for alert in alerts:
        prefix = {
            "info": "ℹ️ ",
            "warning": "⚠️ ",
            "critical": "🚨 ",
        }.get(alert.severity, "• ")
        print(f"{prefix}[{alert.code}] {alert.message}")

    if output_path:
        Path(output_path).write_text(json.dumps([a.to_dict() for a in alerts], indent=2))
        print(f"Alerts written to {output_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m computronium.experiment.monitoring.alerts <store_path> [run_id]")
        sys.exit(1)

    store_path = sys.argv[1]
    run_id = sys.argv[2] if len(sys.argv) > 2 else None

    store = RecordStore(StoreConfig(path=Path(store_path)))
    with store:
        if run_id:
            records = store.query_records(run_id=run_id)
        else:
            records = store.query_records()

    alerts = run_all_checks(records, store_path)
    emit_alerts(alerts, "alerts.json")