#!/usr/bin/env python
"""Simplified Showcase v2 — Zero-Config, Full Search Space, Deadline Enforcement

Ideal experiment architecture:
- Runs until deadline OR space genuinely exhausted
- Round-robin grid policy for broad exploration (not nsga2 convergence)
- No component pre-filtering - let runtime validation handle invalid combos
- Proper round loop with S10_DECIDE that continues until deadline
- 100 cells per round, 5 epochs, 3 seeds = real budget utilization
"""

import argparse
import asyncio
import json
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import yaml

from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import RoundRobinGridPolicy
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema import RunSpec, StageId
from computronium.experiment.surface.cli import _CELL_WORKERS, _resolve_spec, _settle_maturity, create_policy, policy_context
from computronium.experiment.execution.evaluate import task_shape
from computronium.core.logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class ShowcaseV2Config:
    """Minimal config - no prediction, just deadline."""
    hours: float
    device: str
    store: str
    epochs: int = 5
    seeds: int = 3
    cells_per_round: int = 100
    max_parallel: int = 1


def _discover_all_components() -> dict[str, list[str]]:
    """Discover ALL available primitives from registries - no filtering."""
    from computronium.domains.registry import SUPPORTED_TASKS
    from computronium.experiment.schema.axis import GEOMETRY_REGISTRY, UPDATE_REGISTRY
    from computronium.ontology.dynamics import DYNAMICS_REGISTRY
    from computronium.ontology.substrate import SubstrateType

    return {
        "substrates": [s.value for s in SubstrateType],
        "geometries": list(GEOMETRY_REGISTRY.keys()),
        "credits": [
            "gradient", "equilibrium_prop", "feedback_alignment", "hebbian",
            "pepita", "local_contrastive", "random_projections", "temporal_trace",
            "target_inversion", "homeostatic", "pcalm", "lemma", "local_goodness",
        ],
        "dynamics": list(DYNAMICS_REGISTRY.keys()),
        "updates": list(UPDATE_REGISTRY.keys()),
        "plasticities": [
            "null", "routing", "fast_weights", "substrate_coupled",
            "rule_state", "temporal_psi", "conflict_adaptive",
        ],
        "tasks": sorted(SUPPORTED_TASKS),
    }


def _create_run_spec(config: ShowcaseV2Config, components: dict[str, list[str]]) -> RunSpec:
    """Create a RunSpec that explores the FULL search space."""
    return RunSpec(
        tasks=tuple(components["tasks"]),
        fidelity="L1",
        seed=42,
        n_seeds=config.seeds,
        epochs=config.epochs,
        batch_limit=100,
        param_budget=500000,
        device=config.device,
        deterministic=False,
        num_workers=0,
        precision="fp32",
        objectives=("validation_accuracy", "walltime_total", "param_count"),
        policy="round_robin_grid",  # Broad exploration, not nsga2 convergence
        stages=(
            StageId.S1_FRAME, StageId.S2_SPACE, StageId.S3_SCHEDULE,
            StageId.S4_GATE, StageId.S5_COMPOSE, StageId.S6_TRAIN,
            StageId.S7_MEASURE, StageId.S8_RECORD, StageId.S9_ATTRIBUTE,
            StageId.S10_DECIDE, StageId.S11_REPORT,
        ),
        budget_seconds=int(config.hours * 3600),
        hyperparameters={},
        sweep_steps=10,
    )


async def run_showcase_v2(config: ShowcaseV2Config) -> dict[str, Any]:
    """Run the showcase with deadline enforcement and full search space."""
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(130))
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(130))

    # Resolve device
    if config.device == "auto":
        resolved_device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        resolved_device = config.device

    # Discover ALL components
    components = _discover_all_components()
    
    print("=" * 70)
    print("COMPUTRONIUM SHOWCASE v2 — FULL SEARCH SPACE")
    print("=" * 70)
    print(f"Time budget: {config.hours}h (hard deadline)")
    print(f"Device: {config.device} ({resolved_device})")
    print(f"Store: {config.store}")
    print(f"Epochs: {config.epochs}, Seeds: {config.seeds}")
    print(f"Cells per round: {config.cells_per_round}")
    print()
    for axis, items in components.items():
        print(f"  {axis.capitalize()} ({len(items)}): {', '.join(items[:10])}{'...' if len(items) > 10 else ''}")
    print()

    # Create hard deadline
    deadline = Deadline.from_hours(config.hours)
    print(f"Hard deadline: {deadline.remaining_soft_seconds() / 3600:.2f}h from now")
    print()

    # Create run spec with FULL search space
    spec = _create_run_spec(config, components)
    
    # Create deadline from spec budget
    spec_deadline = Deadline.from_seconds(spec.budget_seconds) if spec.budget_seconds else deadline

    # Create policy - ROUND_ROBIN_GRID for broad exploration
    policy = RoundRobinGridPolicy(seed=42)

    # Create pipeline runner
    Path(config.store).parent.mkdir(parents=True, exist_ok=True)
    Path("artifacts").mkdir(exist_ok=True)

    with RecordStore(StoreConfig(path=Path(config.store))) as store:
        run_id = store.create_run(spec=spec)
        logger.info("Run ID: %s", run_id)

        runner = PipelineRunner(
            PipelineConfig(
                run_id=run_id,
                run_spec=spec,
                deadline=spec_deadline,
                cost_model=None,
                policy=policy,
                backend=LocalBackend(max_workers=_CELL_WORKERS),
                seed=spec.seed,
                max_rounds=None,  # UNLIMITED - run until deadline
            ),
            store,
        )

        print(f"Starting campaign at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        start_time = time.time()

        try:
            outcomes = await runner.run()
        except KeyboardInterrupt:
            logger.info("Interrupted; resume with --run-id %s", run_id)
            store.finish_run(run_id, "interrupted")
            return {"status": "interrupted", "run_id": run_id}

        elapsed = time.time() - start_time
        print(f"\nCampaign completed in {elapsed:.1f}s ({elapsed / 3600:.2f}h)")
        print(f"Total records: {len(outcomes)}")

        # Finalize
        _settle_maturity(store, run_id, spec)
        store.finish_run(run_id, "completed")

        # Generate report
        report_path = f"{Path(config.store).with_suffix('')}_report.html"
        _generate_report(store, run_id, config, components, elapsed, report_path, resolved_device)

        return {
            "status": "completed",
            "run_id": run_id,
            "records": len(outcomes),
            "elapsed_seconds": elapsed,
            "report": report_path,
        }


def _generate_report(
    store: RecordStore,
    run_id: str,
    config: ShowcaseV2Config,
    components: dict[str, list[str]],
    elapsed: float,
    report_path: str,
    device: str,
) -> None:
    """Generate a simple but complete HTML report."""
    from computronium.experiment.surface.report import ReportGenerator
    from datetime import datetime

    generator = ReportGenerator(store)
    
    # Get data
    axis_coverage = generator.axis_coverage(run_id)
    pareto = generator.pareto_frontier(run_id)
    failures = generator.failures_by_cause(run_id)
    
    # Count valid combinations explored
    records = store.query_records(run_id=run_id)
    valid_combos = len({r.cell_key for r in records})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Showcase v2 Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #2563eb; }}
        h2 {{ color: #1e40af; margin-top: 40px; }}
        .meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .meta-item {{ background: #f3f4f6; padding: 15px; border-radius: 8px; }}
        .metric {{ font-size: 2rem; font-weight: bold; color: #1a1a2e; }}
        .label {{ font-size: 0.875rem; color: #6b7280; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }}
        th {{ background: #f3f4f6; }}
        .success {{ color: #16a34a; }} .fail {{ color: #dc2626; }}
    </style>
</head>
<body>
    <h1>🌌 Computronium Showcase v2 Report</h1>
    <p><strong>Run ID:</strong> {run_id} | <strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

    <div class="meta">
        <div class="meta-item"><div class="label">Time Budget</div><div class="metric">{config.hours:.2f}h</div></div>
        <div class="meta-item"><div class="label">Actual Duration</div><div class="metric">{elapsed/3600:.2f}h</div></div>
        <div class="meta-item"><div class="label">Valid Combinations</div><div class="metric success">{valid_combos}</div></div>
        <div class="meta-item"><div class="label">Total Records</div><div class="metric">{len(records)}</div></div>
        <div class="meta-item"><div class="label">Pareto Points</div><div class="metric">{len(pareto)}</div></div>
        <div class="meta-item"><div class="label">Failure Types</div><div class="metric fail">{len(failures)}</div></div>
        <div class="meta-item"><div class="label">Device</div><div class="metric">{device}</div></div>
        <div class="meta-item"><div class="label">Epochs/Seeds</div><div class="metric">{config.epochs}/{config.seeds}</div></div>
    </div>

    <h2>📈 Coverage Matrix</h2>
    {_coverage_table(axis_coverage)}

    <h2>🎯 Pareto Frontier (Top 20)</h2>
    {_pareto_table(pareto[:20])}

    <h2>⚠️ Failure Taxonomy</h2>
    {_failure_table(failures)}

    <h2>🔁 Reproducibility</h2>
    <pre style="background: #1a1a2e; color: #e5e7eb; padding: 15px; border-radius: 8px;">
uv run scripts/showcase_v2.py --hours {config.hours} --device {config.device} --store {config.store}
    </pre>
</body>
</html>"""
    
    Path(report_path).write_text(html, encoding="utf-8")
    print(f"Report written to: {report_path}")


def _coverage_table(coverage: dict[str, dict[str, int]]) -> str:
    if not coverage:
        return "<p>No coverage data</p>"
    rows = ["<table><thead><tr><th>Axis</th><th>Primitives</th><th>Total Cells</th></tr></thead><tbody>"]
    for axis, primitives in sorted(coverage.items()):
        total = sum(primitives.values())
        rows.append(f"<tr><td><strong>{axis}</strong></td><td>{len(primitives)}</td><td>{total}</td></tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)


def _pareto_table(pareto: list[dict]) -> str:
    if not pareto:
        return "<p>No Pareto data</p>"
    rows = ["<table><thead><tr><th>#</th>"]
    for k in pareto[0].get("objectives", {}):
        rows[0] += f"<th>{k}</th>"
    for k in pareto[0].get("coordinate", {}):
        rows[0] += f"<th>{k}</th>"
    rows[0] += "</tr></thead><tbody>"
    for i, p in enumerate(pareto):
        rows.append(f"<tr><td>{i+1}</td>")
        for v in p.get("objectives", {}).values():
            rows[-1] += f"<td>{v:.4g}</td>"
        for v in p.get("coordinate", {}).values():
            rows[-1] += f"<td>{v}</td>"
        rows[-1] += "</tr>"
    rows.append("</tbody></table>")
    return "\n".join(rows)


def _failure_table(failures: dict[str, int]) -> str:
    if not failures:
        return "<p class='success'>No failures</p>"
    rows = ["<table><thead><tr><th>Cause</th><th>Count</th></tr></thead><tbody>"]
    for cause, count in sorted(failures.items(), key=lambda x: -x[1]):
        rows.append(f"<tr><td>{cause}</td><td class='fail'>{count}</td></tr>")
    rows.append("</tbody></table>")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Showcase v2 - Full search space, deadline enforcement")
    parser.add_argument("--hours", type=float, default=1.0, help="Time budget in hours")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--store", default="results/showcase_v2.db")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--cells-per-round", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config = ShowcaseV2Config(
        hours=args.hours,
        device=args.device,
        store=args.store,
        epochs=args.epochs,
        seeds=args.seeds,
        cells_per_round=args.cells_per_round,
    )

    if args.dry_run:
        components = _discover_all_components()
        spec = _create_run_spec(config, components)
        print("DRY RUN - would execute:")
        print(json.dumps({"hours": config.hours, "device": config.device, "epochs": config.epochs, 
                         "seeds": config.seeds, "components": {k: len(v) for k, v in components.items()}}, indent=2))
        return 0

    result = asyncio.run(run_showcase_v2(config))
    return 0 if result.get("status") == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())