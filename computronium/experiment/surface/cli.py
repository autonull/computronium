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
from dataclasses import asdict, dataclass, replace
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
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilitySpec,
)
from computronium.experiment.schema.run_spec import (
    BROAD_PARAM_BUDGET,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    Fidelity,
    RunSpec,
)
from computronium.experiment.surface.report import (
    ReportGenerator,
    RunSummary,
    export_to_json,
    export_to_parquet,
    generate_run_report,
)
from computronium.visualization.gallery import render_gallery

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
    axes: tuple[AxisSelection, ...] = ()


# Run profiles as data — single source of truth for CLI behavior
RUN_PROFILES: dict[str, RunProfile] = {
    "quick-verify": RunProfile(
        name="quick-verify",
        description="Fast sanity check: L0 smoke + L1 evidence on few seeds",
        stages=[
            "s1_frame",
            "s2_space",
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
        ],
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
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(
                axis=StructuralAxis.GEOMETRY, primitives=("feedforward", "recurrent")
            ),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=("energy_minimization", "instantaneous", "lazy"),
            ),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=(
                    "gradient",
                    "thermodynamic_contrast",
                    "random_projections",
                    "pepita",
                    "local_goodness",
                ),
            ),
            AxisSelection(
                axis=StructuralAxis.UPDATE, primitives=("euclidean", "adam", "muon")
            ),
        ),
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
        param_budget=BROAD_PARAM_BUDGET,
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
        param_budget=BROAD_PARAM_BUDGET,
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
        param_budget=BROAD_PARAM_BUDGET,
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
    p_run = sub.add_parser("run", help="Execute a run profile or a spec file")
    p_run.add_argument(
        "profile",
        nargs="?",
        choices=list(RUN_PROFILES.keys()),
        help="Run profile to execute (omit when --spec names the run)",
    )
    p_run.add_argument("--store", default="experiment.duckdb", help="DuckDB store path")
    p_run.add_argument(
        "--run-id",
        default=None,
        help=(
            "Resume this run: the store is the checkpoint, so a relaunch "
            "measures only what the run has not"
        ),
    )
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
    p_report.add_argument(
        "--axis-coverage",
        action="store_true",
        help="Show per-axis stratification of records (R18 axis-coverage section)",
    )

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
    p_status.add_argument(
        "--detailed",
        action="store_true",
        help="Show campaign economics: cost per record, projected completion",
    )

    # Gallery command
    p_gallery = sub.add_parser(
        "gallery", help="Render gallery figures from demo records"
    )
    p_gallery.add_argument(
        "--records-dir",
        default="docs/figures/run_records",
        help="Directory containing demo run records",
    )
    p_gallery.add_argument(
        "--output-dir",
        default="docs/figures/gallery",
        help="Output directory for gallery figures",
    )

    # Hypothesis campaign command
    p_hypothesis = sub.add_parser(
        "hypothesis-campaign",
        help="Run hypothesis templates over campaign records (population-level assertions)",
    )
    p_hypothesis.add_argument(
        "--store", default="experiment.duckdb", help="DuckDB store path"
    )
    p_hypothesis.add_argument(
        "--run-id", default=None, help="Run ID to evaluate (latest if omitted)"
    )
    p_hypothesis.add_argument(
        "--templates", required=True, help="JSON file with hypothesis templates"
    )
    p_hypothesis.add_argument(
        "--output", default=None, help="Output file for results (JSON)"
    )
    p_hypothesis.add_argument(
        "--bind",
        action="append",
        default=[],
        help="Parameter bindings for templates (format: template_name:param=value)",
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
        axes=overrides.get("axes", profile.axes),
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

    # The price, the stop point, and the primitives no legal cell reaches
    # (TODO48b R2): every fixture-sizing guess a session makes by trial is a
    # print here instead.
    from computronium.experiment.execution.pricing import price_plan

    lines.append("")
    lines.extend(f"  {line}" for line in price_plan(spec, space).render().splitlines())
    return "\n".join(lines)


def _resolve_spec(args: argparse.Namespace) -> RunSpec:
    """The run's declaration: the spec file's, or a profile's.

    A file is the whole declaration, so the profile-shaped flags that would
    edit it (``--overrides``, ``--task``) are refused rather than silently
    dropped: a run whose stored spec differs from the file it was given is a
    run nobody can reproduce.
    """
    if args.spec is not None:
        ignored = [
            flag
            for flag, value in (("--overrides", args.overrides), ("--task", args.task))
            if value is not None
        ]
        if ignored:
            raise ValueError(
                f"--spec is the run's declaration; {', '.join(ignored)} cannot edit it"
            )
        return RunSpec.load(args.spec)

    if args.profile is None:
        raise ValueError(
            "comp run needs a profile or --spec; profiles: "
            f"{', '.join(RUN_PROFILES)}, or a spec file"
        )
    profile = _apply_overrides(
        RUN_PROFILES[args.profile], _load_overrides(args.overrides)
    )
    logger.info(f"Executing profile: {profile.name}")
    logger.info(f"  Task: {profile.task}, Stages: {profile.stages}")
    logger.info(
        f"  Fidelity: {profile.fidelity}, n_seeds: {profile.n_seeds},"
        f" Epochs: {profile.epochs}"
    )
    logger.info(f"  Objectives: {profile.objectives}")
    return RunSpec(
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
        axes=profile.axes,
    )


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute a run from a spec file or a named profile."""
    spec = _resolve_spec(args)
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
        from computronium.experiment.execution.evaluate import task_shape

        policy = create_policy(
            policy_name, **policy_context(spec, policy_name, shape=task_shape)
        )

        # Create pipeline config — the spec supplies stages, seed and policy
        # If S10 Decide stage is not in the pipeline, limit to 1 round to avoid
        # infinite loop (no decision to continue/stop without S10)
        max_rounds = None
        if spec.stages and StageId.S10_DECIDE not in spec.stages:
            max_rounds = 1

        pipeline_config = PipelineConfig(
            run_id=run_id,
            run_spec=spec,
            budget=budget,
            cost_model=SimpleCostModel(),
            policy=policy,
            backend=LocalBackend(),
            seed=spec.seed,
            max_rounds=max_rounds,
        )

        # Run pipeline
        runner = PipelineRunner(pipeline_config, store)
        try:
            outcomes = asyncio.run(runner.run())
        except KeyboardInterrupt:
            logger.info("Interrupted; run can be resumed with --run-id %s", run_id)
            if runner._state.budget is not None:
                budget_consumed = runner._state.budget.elapsed_seconds()
                store.finish_run(
                    run_id, "interrupted", budget_consumed_s=budget_consumed
                )
            return 130
        except Exception as e:
            logger.error("Pipeline failed: %s", e, exc_info=True)
            if runner._state.budget is not None:
                budget_consumed = runner._state.budget.elapsed_seconds()
                store.finish_run(run_id, "failed", budget_consumed_s=budget_consumed)
            else:
                store.finish_run(run_id, "failed")
            return 1

        # The promotion stage runs after measuring, on the run's own store:
        # maturity is earned from what landed, not declared up front.
        from computronium.experiment.execution.promotion import promote_run
        from computronium.experiment.schema.record import Maturity
        from computronium.experiment.schema.registries import (
            REPLAY_METRIC_TOLERANCE,
        )

        history = promote_run(store, run_id, spec, tolerance=REPLAY_METRIC_TOLERANCE)
        logger.info(
            "Promotion: %d cell(s) assessed, %d earned L2",
            len(history),
            sum(1 for entry in history if entry["maturity"] == Maturity.L2.value),
        )

        # E1: Compute and store uncertainty from across-seed measurements
        from computronium.experiment.evidence.claims import (
            compute_and_store_uncertainty,
        )

        uncertainty = compute_and_store_uncertainty(
            store, run_id, min_seeds=spec.n_seeds
        )
        logger.info(
            "Uncertainty: computed for %d cell(s) with >=%d seeds",
            len(uncertainty),
            spec.n_seeds,
        )

        budget_consumed = (
            runner._state.budget.elapsed_seconds() if runner._state.budget else None
        )
        store.finish_run(run_id, "completed", budget_consumed_s=budget_consumed)
        logger.info(
            f"Run {run_id} completed with {len(outcomes)} outcomes in {budget_consumed:.1f}s"
        )
        return 0


def _cmd_report(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches]
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

        if args.axis_coverage:
            generator = ReportGenerator(store)
            coverage = generator.axis_coverage(run_id)
            lines = ["Axis Coverage (per-axis stratification):"]
            for axis, counts in sorted(coverage.items()):
                lines.append(f"  {axis}:")
                for value, count in sorted(counts.items()):
                    lines.append(f"    {value}: {count}")
            report_text = "\n".join(lines)
            if args.output:
                Path(args.output).write_text(report_text, encoding="utf-8")
                logger.info(f"Report written to {args.output}")
            else:
                print(report_text)
            return 0

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
            if args.detailed:
                _print_detailed_status(summary)
            else:
                # A slots dataclass has no __dict__: reading one is the crash
                # §3.7 gate 4 exists to catch, in the branch that reports a run.
                print(json.dumps(asdict(summary), default=str, indent=2))
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


def _print_detailed_status(summary: RunSummary) -> None:
    """Print detailed status with campaign economics."""
    print(f"Run: {summary.run_id}")
    print(f"Status: {summary.status}")
    print(f"Started: {summary.started_at}")
    print(f"Finished: {summary.finished_at or 'N/A'}")
    print(f"Budget Consumed: {summary.budget_consumed_s or 0:.1f}s")
    print(f"Replay Hash: {summary.replay_hash or 'N/A'}")
    print(f"Spec Version: {summary.spec_version}")
    print()
    print("Record Statistics:")
    print(f"  Total Records: {summary.record_count}")
    print(f"  Claim Eligible: {summary.claim_eligible_count}")
    print(f"  Promoted: {summary.promoted_count}")
    print(f"  Declared Cells: {summary.declared_cells}")
    print()

    # Campaign Economics
    if summary.record_count > 0 and summary.budget_consumed_s is not None:
        cost_per_record = summary.budget_consumed_s / summary.record_count
        print("Campaign Economics:")
        print(f"  Cost per Record: {cost_per_record:.3f}s")

        if summary.declared_cells > 0:
            projected_total = cost_per_record * summary.declared_cells
            remaining_cells = summary.declared_cells - summary.record_count
            projected_remaining = cost_per_record * remaining_cells
            print(
                f"  Projected Total: {projected_total:.1f}s ({projected_total / 60:.1f}m)"
            )
            print(
                f"  Remaining: {projected_remaining:.1f}s ({projected_remaining / 60:.1f}m)"
            )
            progress = (summary.record_count / summary.declared_cells) * 100
            print(
                f"  Progress: {progress:.1f}% ({summary.record_count}/{summary.declared_cells})"
            )
    elif summary.declared_cells > 0:
        print("Campaign Economics:")
        print(f"  Declared Cells: {summary.declared_cells}")
        print(f"  Records Measured: {summary.record_count}")
        print("  Cost per Record: N/A (no budget consumed yet)")


def _cmd_gallery(args: argparse.Namespace) -> int:
    """Render gallery figures from demo records."""
    records_dir = Path(args.records_dir)
    output_dir = Path(args.output_dir)

    if not records_dir.exists():
        logger.error(f"Records directory not found: {records_dir}")
        return 1

    logger.info(f"Rendering gallery from {records_dir} to {output_dir}")
    try:
        metas = render_gallery(records_dir, output_dir)
    except Exception:
        logger.exception("Gallery rendering failed")
        return 1
    else:
        logger.info(f"Rendered {len(metas)} gallery figures")
        for meta in metas:
            logger.info(f"  {meta.figure_png} (data_sha256={meta.data_sha256[:16]}...)")
        return 0


def _cmd_hypothesis_campaign(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches, too-many-statements, too-many-locals]
    """Run hypothesis templates over campaign records."""
    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        # Determine run_id
        run_id = args.run_id
        if run_id is None:
            # Query all records to find the latest run_id
            all_records = list(store.query_records())
            if not all_records:
                logger.error("No records found in store")
                return 1
            run_ids: set[str] = set()
            for r in all_records:
                rid = r.provenance.links.get("run_id")
                if rid is not None:
                    run_ids.add(rid)
            if not run_ids:
                logger.error("No valid run_id found in records")
                return 1
            run_id = max(run_ids)  # Use latest by string comparison
            logger.info(f"Auto-selected run_id: {run_id}")
        else:
            # Verify run exists by querying records
            all_records = list(store.query_records(run_id=run_id))
            if not all_records:
                logger.error(f"No records found for run_id: {run_id}")
                return 1

        logger.info(f"Evaluating hypothesis templates for run: {run_id}")

        # Load templates
        import contextlib
        import json

        templates_path = Path(args.templates)
        if not templates_path.exists():
            logger.error(f"Templates file not found: {templates_path}")
            return 1

        with templates_path.open(encoding="utf-8") as f:
            templates_data = json.load(f)

        # Parse bindings
        bindings: dict[str, dict[str, Any]] = {}
        for bind_str in args.bind:
            if ":" not in bind_str or "=" not in bind_str:
                logger.error(
                    f"Invalid binding format: {bind_str} (expected template:param=value)"
                )
                return 1
            template_name, param_value = bind_str.split(":", 1)
            param, value = param_value.split("=", 1)
            # Try to parse value as JSON
            with contextlib.suppress(json.JSONDecodeError):
                value = json.loads(value)
            bindings.setdefault(template_name, {})[param] = value

        # Query all records for the run
        records = list(store.query_records(run_id=run_id))
        if not records:
            logger.warning(f"No records found for run {run_id}")
            return 0

        # Create campaign context
        from computronium.experiment.legality.dsl import (
            CampaignContext,
            Diff,
            Exists,
            ForAll,
            Max,
            Mean,
            Min,
            Ratio,
            Std,
            expr_from_json,
        )

        campaign_ctx = CampaignContext(records)

        # Evaluate each template
        results = {}
        for template_data in templates_data:
            template_name = template_data.get("name")
            if not template_name:
                logger.warning("Template missing name, skipping")
                continue

            template_expr = expr_from_json(template_data["expr"])

            # Apply bindings if any
            if template_name in bindings:
                # For now, we just note the bindings - full template binding
                # would require substituting variables in the expression
                logger.info(
                    f"Template {template_name} has bindings: {bindings[template_name]}"
                )

            # Evaluate based on expression type
            result = None
            if isinstance(template_expr, ForAll):
                result = campaign_ctx.eval_forall(
                    template_expr.filter, template_expr.body
                )
            elif isinstance(template_expr, Exists):
                result = campaign_ctx.eval_exists(
                    template_expr.filter, template_expr.body
                )
            elif isinstance(template_expr, Mean):
                result = campaign_ctx.eval_aggregation(
                    "Mean", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Max):
                result = campaign_ctx.eval_aggregation(
                    "Max", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Min):
                result = campaign_ctx.eval_aggregation(
                    "Min", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Std):
                result = campaign_ctx.eval_aggregation(
                    "Std", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Diff):
                result = campaign_ctx.eval_diff(template_expr.left, template_expr.right)
            elif isinstance(template_expr, Ratio):
                result = campaign_ctx.eval_ratio(
                    template_expr.left, template_expr.right
                )
            else:
                logger.warning(
                    f"Template {template_name}: unsupported expression type {type(template_expr).__name__}"
                )
                continue

            # Convert result to JSON-serializable format
            def to_serializable(obj):
                if isinstance(obj, dict):
                    return {str(k): to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [to_serializable(v) for v in obj]
                elif isinstance(obj, (int, float, str, bool)) or obj is None:
                    return obj
                else:
                    return str(obj)

            results[template_name] = {
                "result": to_serializable(result),
                "template_type": type(template_expr).__name__,
            }

        # Output results
        output_data = {
            "run_id": run_id,
            "record_count": len(records),
            "results": results,
        }

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(
                json.dumps(output_data, indent=2, default=str), encoding="utf-8"
            )
            logger.info(f"Results written to {output_path}")
        else:
            print(json.dumps(output_data, indent=2, default=str))

        return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Console-script entry point for surface CLI."""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)
    args = _build_parser().parse_args(argv)
    command_handlers = {
        "run": _cmd_run,
        "report": _cmd_report,
        "export": _cmd_export,
        "conformance": _cmd_conformance,
        "status": _cmd_status,
        "gallery": _cmd_gallery,
        "hypothesis-campaign": _cmd_hypothesis_campaign,
    }
    try:
        handler = command_handlers.get(args.command)
        if handler is None:
            return 2
        return handler(args)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        # A refused declaration is the user's input, not an internal fault: a
        # traceback here reads as a crash of the tool rather than of the run.
        print(f"comp {args.command}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
