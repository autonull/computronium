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
from computronium.experiment.execution.policy import (
    create_policy,
    policy_context,
)
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilitySpec,
)
from computronium.experiment.schema.run_spec import (
    MEASURED_PARAM_BUDGET,
    Fidelity,
    RunSpec,
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
    fidelity: Fidelity  # L0, L1, L2
    task: str  # The task this profile measures
    n_seeds: int
    epochs: int
    budget_seconds: float | None
    param_budget: int  # Parameter ceiling for derived geometry sizing
    objectives: tuple[str, ...]  # Names from the OBJECTIVES registry
    policy: str  # Name from the POLICY catalog
    promotion_threshold: float  # Pareto frontier promotion threshold
    maturation: bool  # Whether to run maturation after
    deep_tier: bool  # Whether to run deep-tier claim-grade


# Run profiles as data — single source of truth for CLI behavior
RUN_PROFILES: dict[str, RunProfile] = {
    "quick-verify": RunProfile(
        name="quick-verify",
        description="Fast sanity check: L0 smoke + L1 evidence on few seeds",
        stages=["s1_frame", "s2_space", "s3_schedule", "s4_gate", "s5_compose"],
        fidelity="L1",
        n_seeds=1,
        epochs=3,
        budget_seconds=300.0,
        task="digits",
        policy="round_robin_grid",
        param_budget=MEASURED_PARAM_BUDGET,
        objectives=("validation_accuracy", "walltime_total"),
        promotion_threshold=0.5,
        maturation=False,
        deep_tier=False,
    ),
    "production-map": RunProfile(
        name="production-map",
        description="Full broad mapping: L0→L1→L2 maturation with multi-objective Pareto",
        stages=[
            "s1_frame",
            "s2_space",
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
            "s11_report",
        ],
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=3600.0,
        task="digits",
        policy="model_based",
        param_budget=MEASURED_PARAM_BUDGET,
        objectives=(
            "validation_accuracy",
            "walltime_total",
            "param_count",
        ),
        promotion_threshold=0.7,
        maturation=True,
        deep_tier=True,
    ),
    "maturation": RunProfile(
        name="maturation",
        description="Re-run front cells at higher fidelity (L1→L2)",
        stages=[
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
        ],
        fidelity="L2",
        n_seeds=5,
        epochs=10,
        budget_seconds=7200.0,
        task="digits",
        policy="evolution",
        param_budget=MEASURED_PARAM_BUDGET,
        objectives=("validation_accuracy", "walltime_total", "param_count"),
        promotion_threshold=0.8,
        maturation=False,
        deep_tier=False,
    ),
    "claim": RunProfile(
        name="claim",
        description="Claim-grade L2 re-runs with CEEC governance (N≥10 seeds)",
        stages=["s8_record", "s9_attribute", "s10_decide", "s11_report"],
        fidelity="L2",
        n_seeds=10,
        epochs=20,
        budget_seconds=None,
        task="digits",
        policy="evolution",
        param_budget=MEASURED_PARAM_BUDGET,
        objectives=(
            "validation_accuracy",
            "walltime_total",
            "param_count",
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
    p_run.add_argument(
        "--task", default=None, help="Override the profile's task (ignored with --spec)"
    )
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


def _duration_str(seconds: float) -> str:
    """Seconds as the duration string ``Budget.from_duration`` parses."""
    if seconds >= 3600:
        return f"{int(seconds / 3600)}h"
    if seconds >= 60:
        return f"{int(seconds / 60)}m"
    return f"{int(seconds)}s"


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
        task=overrides.get("task", profile.task),
        n_seeds=overrides.get("n_seeds", profile.n_seeds),
        epochs=overrides.get("epochs", profile.epochs),
        budget_seconds=overrides.get("budget_seconds", profile.budget_seconds),
        objectives=tuple(overrides.get("objectives", profile.objectives)),
        param_budget=int(overrides.get("param_budget", profile.param_budget)),
        policy=overrides.get("policy", profile.policy),
        promotion_threshold=overrides.get(
            "promotion_threshold", profile.promotion_threshold
        ),
        maturation=overrides.get("maturation", profile.maturation),
        deep_tier=overrides.get("deep_tier", profile.deep_tier),
    )


def _open_store(path: str) -> RecordStore | None:
    """Open an existing store read-only, or report its absence and return None.

    A read command against a store that was never created has nothing to say;
    duckdb's own failure for it is an IO traceback, which reads as a crash
    rather than as the absence it is.
    """
    store_path = Path(path)
    if not store_path.exists():
        print(f"No store at {store_path} \u2014 nothing to read.", file=sys.stderr)
        return None
    return RecordStore(StoreConfig(path=store_path, read_only=True))


def _dry_run_report(spec: RunSpec, *, policy_name: str, limit: int = 5) -> str:
    """The plan a run would execute: space, policy, and the first cells.

    Computed from the spec through the same builders the runner uses, so a dry
    run is evidence the spec is executable rather than a restatement of it.
    """
    from computronium.experiment.execution.evaluate import task_shape
    from computronium.experiment.execution.pipeline import _resolve_tasks
    from computronium.experiment.execution.search_space import (
        iter_candidates,
        search_space_from_spec,
    )
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.harvest import AXIS_KIND_ORDER

    tasks = _resolve_tasks(PipelineConfig(run_id="dry-run", run_spec=spec))
    space = search_space_from_spec(spec, tasks=tasks)
    lines = [
        f"profile: {spec.profile}",
        f"task(s): {', '.join(tasks)}",
        f"fidelity: {spec.fidelity}  epochs: {spec.epochs}  seeds: {spec.n_seeds}",
        f"batch_limit: {spec.batch_limit}  param_budget: {spec.param_budget}",
        f"budget: {spec.budget_seconds if spec.budget_seconds is not None else 'none'}",
        f"policy: {policy_name}",
        f"objectives: {', '.join(spec.objectives) or 'all'}",
        f"spec version: {spec.version}",
    ]
    for axis in StructuralAxis:
        names = space.primitives(axis)
        lines.append(
            f"axis {axis.value}: {len(names)} \u2014 {', '.join(names) or 'none'}"
        )

    cells: list[str] = []
    for coordinate, schedule in iter_candidates(spec, space, shape=task_shape):
        swept = (
            ", ".join(f"{k}={v:.4g}" for k, v in sorted(coordinate.params.items()))
            or "no swept params"
        )
        selection = ", ".join(
            f"{axis.value}={getattr(coordinate, axis.value)}"
            for axis in AXIS_KIND_ORDER
        )
        cells.append(
            f"  cell {len(cells) + 1}: {schedule.fidelity} seed={schedule.seed} "
            f"{selection} [{swept}]"
        )
        if len(cells) >= limit:
            break
    lines.append(f"first {len(cells)} legal cell(s):")
    lines.extend(cells)
    return "\n".join(lines)


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute a run profile."""
    profile = RUN_PROFILES[args.profile]
    overrides = _load_overrides(args.overrides)
    profile = _apply_overrides(profile, overrides)

    logger.info(f"Executing profile: {profile.name}")
    logger.info(f"  Task: {profile.task}, Stages: {profile.stages}")
    logger.info(
        f"  Fidelity: {profile.fidelity}, n_seeds: {profile.n_seeds},"
        f" Epochs: {profile.epochs}"
    )
    logger.info(f"  Objectives: {profile.objectives}")

    # The spec is the run's single declaration: a file's, or the profile's.
    if args.spec:
        spec = RunSpec.load(args.spec)
    else:
        spec = RunSpec(
            profile=profile.name,
            task=args.task or profile.task,
            objectives=profile.objectives,
            stages=tuple(profile.stages),
            fidelity=profile.fidelity,
            n_seeds=profile.n_seeds,
            epochs=profile.epochs,
            budget_seconds=profile.budget_seconds,
            param_budget=profile.param_budget,
            policy=profile.policy,
        )

    policy_name = spec.policy or "round_robin_grid"

    # A dry run writes nothing: not a store, not a run row, not a checkpoint.
    if args.dry_run:
        print(_dry_run_report(spec, policy_name=policy_name))
        return 0

    store_config = StoreConfig(path=Path(args.store))
    with RecordStore(store_config) as store:
        run_id = args.run_id or store.create_run(spec=spec)
        logger.info(f"Run ID: {run_id}")

        budget = (
            Budget.from_duration(_duration_str(spec.budget_seconds))
            if spec.budget_seconds is not None
            else None
        )

        # The spec is the only place a policy's arguments come from, so the
        # sampler learns on the run's objectives and its own swept domains.
        policy = create_policy(policy_name, **policy_context(spec, policy_name))

        # Create pipeline config — the spec supplies stages, seed and policy
        pipeline_config = PipelineConfig(
            run_id=run_id,
            run_spec=spec,
            budget=budget,
            cost_model=SimpleCostModel(),
            policy=policy,
            backend=LocalBackend(),
            checkpoint_dir=Path(f"checkpoints/{run_id}"),
            seed=spec.seed,
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
    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        # Determine run_id
        run_id = args.run_id
        if run_id is None:
            run_id = store.latest_run_id()
            if run_id is None:
                logger.error("No runs found in store")
                return 1

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
    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        if args.format == "json":
            export_to_json(store, args.output, args.run_id)
        elif args.format == "parquet":
            export_to_parquet(store, args.output, args.run_id)
        logger.info(f"Export completed: {args.output}")
    return 0


def _cmd_conformance(args: argparse.Namespace) -> int:
    """Check capability conformance."""
    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
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
    _ = spec  # evidence is currently run-scoped, not capability-scoped
    return store.count_passing_records(run_id) > 0


def _cmd_status(args: argparse.Namespace) -> int:
    """Show run/store status."""
    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
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
