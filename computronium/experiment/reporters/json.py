"""Structured JSON Output Reporter for experiment results.

Machine-readable output for downstream analysis:
{
  "run_id": "exp_abc123",
  "profile": "geometry-coverage",
  "cells": [
    {
      "coordinate": {...},
      "metrics": {...},
      "status": "measured|void|failed",
      "failure_class": "critical|degraded|warning|void",
      "defect": "..." | null,
      "seed": 42,
      "walltime_s": 12.3
    }
  ],
  "pareto_frontier": [...],
  "axis_coverage": {...}
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


@dataclass(frozen=True, slots=True)
class JSONReportConfig:
    """Configuration for JSON report generation."""

    output_dir: str = "experiments/reports"
    include_pareto: bool = True
    include_axis_coverage: bool = True
    include_summary: bool = True
    pretty_print: bool = True


def _record_to_dict(record: Record) -> dict[str, Any]:
    """Convert a Record to a JSON-serializable dictionary."""
    # Determine failure class
    gate_verdict = record.status.gate_verdict.value
    if gate_verdict == "PASS":
        status = "measured"
        failure_class = None
    elif gate_verdict == "VOID":
        status = "void"
        failure_class = "void"
    else:
        status = "failed"
        # Map severity to failure class
        severity = record.status.severity.value
        if severity == "critical":
            failure_class = "critical"
        elif severity == "degraded":
            failure_class = "degraded"
        else:
            failure_class = "warning"

    coordinate = {
        "substrate": record.substrate,
        "geometry": record.geometry,
        "dynamics": record.dynamics,
        "plasticity": record.plasticity,
        "credit": record.credit,
        "update": record.update,
        "params": record.params,
    }

    return {
        "coordinate": coordinate,
        "metrics": record.payload,
        "status": status,
        "failure_class": failure_class,
        "defect": record.status.defect,
        "seed": record.schedule.seed,
        "walltime_s": record.payload.get("walltime_total", 0),
        "task_id": record.schedule.task_id,
        "fidelity": record.schedule.fidelity,
        "param_budget": record.schedule.param_budget,
        "measurement_key": record.measurement_key,
        "cell_key": record.cell_key,
    }


def _compute_pareto_frontier_json(
    records: list[Record],
    x_metric: str,
    y_metric: str,
    maximize_y: bool = True,
    minimize_x: bool = True,
) -> list[dict[str, Any]]:
    """Compute Pareto frontier for JSON output."""
    # Filter to measured cells with valid metrics
    valid = []
    for r in records:
        if r.status.gate_verdict.value != "PASS":
            continue
        x_val = r.payload.get(x_metric)
        y_val = r.payload.get(y_metric)
        if x_val is not None and y_val is not None:
            valid.append((r, float(x_val), float(y_val)))

    if not valid:
        return []

    # Sort by x metric
    valid.sort(key=lambda t: t[1], reverse=not minimize_x)

    pareto = []
    best_y = -float("inf") if maximize_y else float("inf")

    for r, x_val, y_val in valid:
        if maximize_y:
            if y_val > best_y:
                pareto.append({
                    "cell_key": r.cell_key,
                    "coordinate": {
                        "substrate": r.substrate,
                        "geometry": r.geometry,
                        "dynamics": r.dynamics,
                        "plasticity": r.plasticity,
                        "credit": r.credit,
                        "update": r.update,
                    },
                    x_metric: x_val,
                    y_metric: y_val,
                })
                best_y = y_val
        else:
            if y_val < best_y:
                pareto.append({
                    "cell_key": r.cell_key,
                    "coordinate": {
                        "substrate": r.substrate,
                        "geometry": r.geometry,
                        "dynamics": r.dynamics,
                        "plasticity": r.plasticity,
                        "credit": r.credit,
                        "update": r.update,
                    },
                    x_metric: x_val,
                    y_metric: y_val,
                })
                best_y = y_val

    return pareto


def _compute_axis_coverage_json(records: list[Record]) -> dict[str, Any]:
    """Compute axis coverage statistics."""
    axes = ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"]
    coverage = {}

    for axis in axes:
        measured_vals = set(
            getattr(r, axis) for r in records if r.status.gate_verdict.value == "PASS"
        )
        all_vals = set(getattr(r, axis) for r in records)
        void_vals = set(
            getattr(r, axis) for r in records if r.status.gate_verdict.value == "VOID"
        )
        failed_vals = set(
            getattr(r, axis) for r in records if r.status.gate_verdict.value == "FAIL"
        )

        coverage[axis] = {
            "measured": sorted(measured_vals),
            "void": sorted(void_vals),
            "failed": sorted(failed_vals),
            "total_available": sorted(all_vals),
            "coverage_ratio": len(measured_vals) / len(all_vals) if all_vals else 0,
        }

    return coverage


def _compute_summary_json(records: list[Record]) -> dict[str, Any]:
    """Compute summary statistics."""
    total = len(records)
    measured = sum(1 for r in records if r.status.gate_verdict.value == "PASS")
    void = sum(1 for r in records if r.status.gate_verdict.value == "VOID")
    failed = sum(1 for r in records if r.status.gate_verdict.value == "FAIL")

    # Group by coordinate (excluding seed) for seed statistics
    from collections import defaultdict
    coord_groups = defaultdict(list)
    for r in records:
        if r.status.gate_verdict.value == "PASS":
            key = (r.substrate, r.geometry, r.dynamics, r.plasticity, r.credit, r.update)
            # Use val_acc or validation_accuracy
            acc_val = r.payload.get("val_acc") or r.payload.get("validation_accuracy", 0)
            coord_groups[key].append(acc_val)

    multi_seed_coords = sum(1 for v in coord_groups.values() if len(v) > 1)
    total_coords = len(coord_groups)

    return {
        "total_cells": total,
        "measured_cells": measured,
        "void_cells": void,
        "failed_cells": failed,
        "measured_rate": measured / total if total > 0 else 0,
        "unique_coordinates": total_coords,
        "multi_seed_coordinates": multi_seed_coords,
    }


def generate_json_report(
    store: "RecordStore",
    run_id: str,
    config: JSONReportConfig | None = None,
) -> Path:
    """Generate a structured JSON report for a run."""
    config = config or JSONReportConfig()
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Query records
    records = store.query_records(run_id=run_id)
    if not records:
        raise ValueError(f"No records found for run_id: {run_id}")

    # Get run info
    run_info = store.query_run(run_id)

    # Build report
    cells = [_record_to_dict(r) for r in records]

    report = {
        "run_id": run_id,
        "generated_at": datetime.now().isoformat(),
        "run_info": {
            "run_id": run_info.run_id if run_info else run_id,
            "spec_version": run_info.spec_version if run_info else None,
            "status": run_info.status if run_info else "unknown",
            "budget_consumed_s": run_info.budget_consumed_s if run_info else None,
            "started_at": run_info.started_at.isoformat() if run_info and run_info.started_at else None,
            "finished_at": run_info.finished_at.isoformat() if run_info and run_info.finished_at else None,
        } if run_info else None,
    }

    if config.include_summary:
        report["summary"] = _compute_summary_json(records)

    if config.include_axis_coverage:
        report["axis_coverage"] = _compute_axis_coverage_json(records)

    if config.include_pareto:
        # Determine metric names from actual data
        accuracy_metric = "validation_accuracy"
        walltime_metric = "walltime_total"
        # Check first record for available metrics
        for r in records:
            if "val_acc" in r.payload:
                accuracy_metric = "val_acc"
            elif "validation_accuracy" in r.payload:
                accuracy_metric = "validation_accuracy"
            if "walltime_s" in r.payload:
                walltime_metric = "walltime_s"
            elif "walltime_total" in r.payload:
                walltime_metric = "walltime_total"
            break
        
        report["pareto_frontiers"] = {
            f"{accuracy_metric}_vs_{walltime_metric}": _compute_pareto_frontier_json(
                records, walltime_metric, accuracy_metric
            ),
            f"{accuracy_metric}_vs_params": _compute_pareto_frontier_json(
                records, "param_count", accuracy_metric
            ),
            f"{accuracy_metric}_vs_flops": _compute_pareto_frontier_json(
                records, "flops", accuracy_metric
            ),
            f"{walltime_metric}_vs_params": _compute_pareto_frontier_json(
                records, "param_count", walltime_metric, maximize_y=False
            ),
        }

    report["cells"] = cells

    # Write JSON
    indent = 2 if config.pretty_print else None
    output_path = output_dir / f"{run_id}_report.json"
    output_path.write_text(json.dumps(report, indent=indent))

    return output_path


def generate_json_report_from_db(
    db_path: str,
    run_id: str | None = None,
    output_dir: str = "experiments/reports",
    pretty_print: bool = True,
) -> Path:
    """Convenience function to generate JSON report directly from database."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    store = RecordStore(StoreConfig(path=Path(db_path), read_only=True))
    with store:
        if run_id is None:
            run_info = store.latest_run_id()
            if run_info is None:
                raise ValueError("No runs found in database")
            run_id = run_info
        config = JSONReportConfig(output_dir=output_dir, pretty_print=pretty_print)
        return generate_json_report(store, run_id, config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate JSON report from experiment database")
    parser.add_argument("--db", required=True, help="Path to experiment database")
    parser.add_argument("--run-id", help="Run ID (default: latest)")
    parser.add_argument("--output", default="experiments/reports", help="Output directory")
    parser.add_argument("--compact", action="store_true", help="Compact JSON output")

    args = parser.parse_args()

    path = generate_json_report_from_db(
        args.db, args.run_id, args.output, pretty_print=not args.compact
    )
    print(f"JSON report generated: {path}")