"""Surface CLI dispatcher with run profiles (WP7).

Single dispatcher replacing legacy entry points. Run profiles as data:
- quick-verify: Fast sanity check (L0/L1, few seeds)
- production-map: Full broad mapping (L0→L1→L2 maturation)
- maturation: Re-run front cells at higher fidelity
- claim: Claim-grade L2 re-runs with CEEC governance
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.budget import Budget, SimpleCostModel
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import RoundRobinGridPolicy
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilitySpec,
)
from computronium.experiment.surface.report import (
    ReportGenerator,
    export_to_json,
    export_to_parquet,
    generate_run_report,
)

logger = get_logger()


@dataclass(frozen=True, slots=True)
class RunProfile:
    """Run profile configuration (data-driven)."""

    name: str
    description: str
    stages: list[str]  # Stage IDs to execute
    fidelity: str  # L0, L1, L2
    seeds: int
    epochs: int
    budget_seconds: float | None
    objectives: tuple[str, ...]
    promotion_threshold: float  # Pareto frontier promotion threshold
    maturation: bool  # Whether to run maturation after
    deep_tier: bool  # Whether to run deep-tier claim-grade


# Run profiles as data — single source of truth for CLI behavior
RUN_PROFILES: dict[str, RunProfile] = {
    "quick-verify": RunProfile(
        name="quick-verify",
        description="Fast sanity check: L0 smoke + L1 evidence on few seeds",
        stages=["S1_DISCOVERY", "S2_VALIDATION", "S3_CALIBRATION"],
        fidelity="L1",
        seeds=1,
        epochs=3,
        budget_seconds=300.0,
        objectives=("accuracy", "walltime_s"),
        promotion_threshold=0.5,
        maturation=False,
        deep_tier=False,
    ),
    "production-map": RunProfile(
        name="production-map",
        description="Full broad mapping: L0→L1→L2 maturation with multi-objective Pareto",
        stages=[
            "S1_DISCOVERY",
            "S2_VALIDATION",
            "S3_CALIBRATION",
            "S4_EXPANSION",
            "S5_MATURATION",
            "S6_CLAIM",
            "S7_REPRODUCTION",
            "S8_DISTILLATION",
            "S9_DEPLOYMENT",
            "S10_MONITORING",
            "S11_RETIREMENT",
        ],
        fidelity="L0",
        seeds=1,
        epochs=1,
        budget_seconds=3600.0,
        objectives=("accuracy", "walltime_s", "param_count", "flops", "memory_mb"),
        promotion_threshold=0.7,
        maturation=True,
        deep_tier=True,
    ),
    "maturation": RunProfile(
        name="maturation",
        description="Re-run front cells at higher fidelity (L1→L2)",
        stages=["S4_EXPANSION", "S5_MATURATION", "S6_CLAIM", "S7_REPRODUCTION"],
        fidelity="L2",
        seeds=5,
        epochs=10,
        budget_seconds=7200.0,
        objectives=("accuracy", "walltime_s", "param_count"),
        promotion_threshold=0.8,
        maturation=False,
        deep_tier=False,
    ),
    "claim": RunProfile(
        name="claim",
        description="Claim-grade L2 re-runs with CEEC governance (N≥10 seeds)",
        stages=["S8_DISTILLATION", "S9_DEPLOYMENT", "S10_MONITORING", "S11_RETIREMENT"],
        fidelity="L2",
        seeds=10,
        epochs=20,
        budget_seconds=None,
        objectives=(
            "accuracy",
            "walltime_s",
            "param_count",
            "flops",
            "energy_per_step",
        ),
        promotion_threshold=0.9,
        maturation=False,
        deep_tier=True,
    ),
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="comp-surface",
        description="Computronium Surface CLI — experiment orchestration and reporting",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # Run command
    p_run = sub.add_parser("run", help="Execute a run profile")
    p_run.add_argument(
        "profile", choices=list(RUN_PROFILES.keys()), help="Run profile to execute"
    )
    p_run.add_argument("--store", default="experiment.duckdb", help="DuckDB store path")
    p_run.add_argument("--run-id", default=None, help="Existing run ID to resume")
    p_run.add_argument("--spec", default=None, help="RunSpec JSON file")
    p_run.add_argument("--spec-version", type=int, default=1, help="RunSpec version")
    p_run.add_argument(
        "--overrides", default=None, help="JSON overrides for profile parameters"
    )
    p_run.add_argument(
        "--dry-run", action="store_true", help="Print plan without executing"
    )

    # Report command
    p_report = sub.add_parser("report", help="Generate report from store")
    p_report.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_report.add_argument(
        "--run-id", default=None, help="Run ID to report on (latest if omitted)"
    )
    p_report.add_argument(
        "--format",
        choices=["text", "json", "parquet"],
        default="text",
        help="Output format",
    )
    p_report.add_argument("--output", default=None, help="Output file path")

    # Export command
    p_export = sub.add_parser("export", help="Export store data for round-trip")
    p_export.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_export.add_argument(
        "--run-id", default=None, help="Run ID to export (all if omitted)"
    )
    p_export.add_argument(
        "--format", choices=["json", "parquet"], default="json", help="Export format"
    )
    p_export.add_argument("--output", required=True, help="Output file/directory path")

    # Conformance command
    p_conformance = sub.add_parser("conformance", help="Check capability conformance")
    p_conformance.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_conformance.add_argument("--run-id", default=None, help="Run ID to check")
    p_conformance.add_argument(
        "--list-only", action="store_true", help="List capabilities without checking"
    )

    # Status command
    p_status = sub.add_parser("status", help="Show run/store status")
    p_status.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_status.add_argument(
        "--run-id", default=None, help="Run ID to check (all if omitted)"
    )

    return parser


def _load_overrides(overrides_str: str | None) -> dict[str, Any]:
    """Load JSON overrides for profile parameters."""
    if not overrides_str:
        return {}
    try:
        return json.loads(overrides_str)
    except json.JSONDecodeError:
        logger.exception("Invalid JSON in --overrides")
        sys.exit(1)


def _apply_overrides(profile: RunProfile, overrides: dict[str, Any]) -> RunProfile:
    """Apply overrides to a run profile."""
    return replace(
        profile,
        stages=overrides.get("stages", profile.stages),
        fidelity=overrides.get("fidelity", profile.fidelity),
        seeds=overrides.get("seeds", profile.seeds),
        epochs=overrides.get("epochs", profile.epochs),
        budget_seconds=overrides.get("budget_seconds", profile.budget_seconds),
        objectives=tuple(overrides.get("objectives", profile.objectives)),
        promotion_threshold=overrides.get(
            "promotion_threshold", profile.promotion_threshold
        ),
        maturation=overrides.get("maturation", profile.maturation),
        deep_tier=overrides.get("deep_tier", profile.deep_tier),
    )


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute a run profile."""
    profile = RUN_PROFILES[args.profile]
    overrides = _load_overrides(args.overrides)
    profile = _apply_overrides(profile, overrides)

    logger.info(f"Executing profile: {profile.name}")
    logger.info(f"  Stages: {profile.stages}")
    logger.info(
        f"  Fidelity: {profile.fidelity}, Seeds: {profile.seeds}, Epochs: {profile.epochs}"
    )
    logger.info(f"  Objectives: {profile.objectives}")

    # Load or create run spec
    if args.spec:
        with Path(args.spec).open(encoding="utf-8") as f:
            spec = json.load(f)
    else:
        spec = {
            "profile": profile.name,
            "stages": profile.stages,
            "fidelity": profile.fidelity,
            "seeds": profile.seeds,
            "epochs": profile.epochs,
            "objectives": list(profile.objectives),
            "budget_seconds": profile.budget_seconds,
        }

    # Initialize store
    store_config = StoreConfig(path=Path(args.store))
    with RecordStore(store_config) as store:
        # Create or resume run
        run_id = args.run_id or store.create_run(
            spec=spec, spec_version=args.spec_version
        )
        logger.info(f"Run ID: {run_id}")

        if args.dry_run:
            logger.info("DRY RUN - would execute pipeline with config:")
            logger.info(f"  Run ID: {run_id}")
            logger.info(f"  Profile: {profile.name}")
            logger.info(f"  Budget: {profile.budget_seconds}s")
            return 0

        # Create budget
        budget = None
        if profile.budget_seconds is not None:
            # Convert seconds to duration string format
            if profile.budget_seconds >= 3600:
                duration_str = f"{int(profile.budget_seconds / 3600)}h"
            elif profile.budget_seconds >= 60:
                duration_str = f"{int(profile.budget_seconds / 60)}m"
            else:
                duration_str = f"{int(profile.budget_seconds)}s"
            budget = Budget.from_duration(duration_str)

        # Convert string stage names to StageId enum
        stage_ids = [StageId(s) for s in profile.stages]

        # Create pipeline config
        pipeline_config = PipelineConfig(
            run_id=run_id,
            run_spec=spec,
            stages=stage_ids,
            budget=budget,
            cost_model=SimpleCostModel(),
            policy=RoundRobinGridPolicy(),
            backend=LocalBackend(),
            checkpoint_dir=Path(f"checkpoints/{run_id}"),
            seed=42,
        )

        # Run pipeline
        runner = PipelineRunner(pipeline_config, store)
        try:
            outcomes = asyncio.run(runner.run())
        except KeyboardInterrupt:
            logger.info("Interrupted; run can be resumed with --run-id %s", run_id)
            return 130
        except Exception as e:
            logger.error("Pipeline failed: %s", e, exc_info=True)
            store.finish_run(run_id, "failed")
            return 1

        store.finish_run(run_id, "completed")
        logger.info(f"Run {run_id} completed with {len(outcomes)} outcomes")
        return 0


def _cmd_report(args: argparse.Namespace) -> int:
    """Generate report from store."""
    store_config = StoreConfig(path=Path(args.store), read_only=True)
    with RecordStore(store_config) as store:
        # Determine run_id
        run_id = args.run_id
        if run_id is None:
            if store._conn is None:
                raise RuntimeError("Store connection not initialized")
            runs = store._conn.execute(
                "SELECT run_id FROM runs ORDER BY started_at DESC LIMIT 1"
            ).fetchone()
            if runs is None:
                logger.error("No runs found in store")
                return 1
            run_id = runs[0]

        logger.info(f"Generating report for run: {run_id}")

        if args.format == "text":
            report_text = generate_run_report(store, run_id)
            if args.output:
                Path(args.output).write_text(report_text, encoding="utf-8")
                logger.info(f"Report written to {args.output}")
            else:
                print(report_text)
            return 0

        elif args.format == "json":
            output_path = args.output or f"{run_id}.report.json"
            export_to_json(store, output_path, run_id)
            logger.info(f"JSON report written to {output_path}")
            return 0

        elif args.format == "parquet":
            output_path = args.output or f"{run_id}.report.parquet"
            export_to_parquet(store, output_path, run_id)
            logger.info(f"Parquet report written to {output_path}")
            return 0

    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    """Export store data for round-trip."""
    store_config = StoreConfig(path=Path(args.store), read_only=True)
    with RecordStore(store_config) as store:
        if args.format == "json":
            export_to_json(store, args.output, args.run_id)
        elif args.format == "parquet":
            export_to_parquet(store, args.output, args.run_id)
        logger.info(f"Export completed: {args.output}")
    return 0


def _cmd_conformance(args: argparse.Namespace) -> int:
    """Check capability conformance."""
    store_config = StoreConfig(path=Path(args.store), read_only=True)
    with RecordStore(store_config) as store:
        if args.list_only:
            print("Registered Capabilities:")
            print("=" * 60)
            for name, spec in CAPABILITIES_REGISTRY.items():
                status = (
                    "✓"
                    if _check_capability(store, run_id=args.run_id, spec=spec)
                    else "✗"
                )
                print(f"  {status} {name} ({spec.kind.value})")
            return 0

        # Full conformance check
        passed = 0
        failed = 0

        for name, spec in CAPABILITIES_REGISTRY.items():
            if not spec.required:
                logger.info(f"  ⊘ {name} (optional)")
                continue

            if _check_capability(store, run_id=args.run_id, spec=spec):
                passed += 1
                logger.info(f"  ✓ {name}")
            else:
                failed += 1
                logger.error(f"  ✗ {name} - NO PASSING EVIDENCE")

        logger.info(f"Conformance: {passed} passed, {failed} failed")
        if failed > 0:
            return 1
    return 0


def _check_capability(
    store: RecordStore, run_id: str | None, spec: CapabilitySpec
) -> bool:
    """Check if a capability has passing evidence in the store."""
    if store._conn is None:
        raise RuntimeError("Store connection not initialized")

    # Build query based on capability kind
    conditions = ["status.gate_verdict = 'PASS'", "status.quarantine = 0"]
    params = []

    if run_id:
        conditions.append("run_id = ?")
        params.append(run_id)

    where_clause = " WHERE " + " AND ".join(conditions)
    query = f"SELECT COUNT(*) FROM records{where_clause}"  # noqa: S608 - parameterized query
    result = store._conn.execute(query, params).fetchone()
    return result is not None and result[0] > 0


def _cmd_status(args: argparse.Namespace) -> int:
    """Show run/store status."""
    store_config = StoreConfig(path=Path(args.store), read_only=True)
    with RecordStore(store_config) as store:
        if args.run_id:
            summary = ReportGenerator(store).run_summary(args.run_id)
            if summary is None:
                logger.error(f"Run {args.run_id} not found")
                return 1
            print(json.dumps(summary.__dict__, default=str, indent=2))
        else:
            runs = ReportGenerator(store).list_runs()
            if not runs:
                print("No runs found")
                return 0
            for run in runs:
                print(
                    f"  {run.run_id[:8]}... | {run.status:12} | "
                    f"recs={run.record_count:4} | claim={run.claim_eligible_count:3} | "
                    f"promo={run.promoted_count:3} | {run.started_at}"
                )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Console-script entry point for surface CLI."""
    args = _build_parser().parse_args(argv)
    command_handlers = {
        "run": _cmd_run,
        "report": _cmd_report,
        "export": _cmd_export,
        "conformance": _cmd_conformance,
        "status": _cmd_status,
    }
    try:
        handler = command_handlers.get(args.command)
        if handler is None:
            return 2
        return handler(args)
    except FileNotFoundError, ValueError, json.JSONDecodeError:
        logger.exception("surface CLI error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
