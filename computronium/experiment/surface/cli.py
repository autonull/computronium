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
    MEASURED_BATCH_LIMIT,
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
    generate_html_report,
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
    batch_limit: int
    budget_seconds: float | None
    param_budget: int  # Parameter ceiling for derived geometry sizing
    objectives: tuple[str, ...]  # Names from the OBJECTIVES registry
    policy: str  # Name from the POLICY catalog
    promotion_threshold: float  # Pareto frontier promotion threshold
    maturation: bool  # Whether to run maturation after
    deep_tier: bool  # Whether to run deep-tier claim-grade
    axes: tuple[AxisSelection, ...] = ()
    checkpoint_every_n: int = 0  # Save checkpoint every N epochs (0 = disabled)


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
        batch_limit=MEASURED_BATCH_LIMIT,
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
        checkpoint_every_n=1,
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
        batch_limit=MEASURED_BATCH_LIMIT,
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
            "s3_schedule",
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
        batch_limit=0,  # Full training
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
        stages=[
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
        fidelity="L2",
        n_seeds=10,
        epochs=20,
        batch_limit=0,  # Full training
        budget_seconds=86400.0,  # 24 hours
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


def _build_parser() -> argparse.ArgumentParser:  # ruff: ignore[too-many-statements]
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
        choices=["text", "json", "parquet", "html"],
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

    # Stability-plasticity campaign command
    p_sta = sub.add_parser(
        "stability-plasticity",
        help="Generate and run stability-plasticity frontier campaign",
    )
    p_sta.add_argument("--store", default="sta.duckdb", help="DuckDB store path")
    p_sta.add_argument(
        "--output-spec", default=None, help="Output path for generated RunSpec (JSON)"
    )
    p_sta.add_argument(
        "--rho",
        default="0.5,0.9,1.05",
        help="Rho (contraction) values (comma-separated)",
    )
    p_sta.add_argument(
        "--feedback-scale",
        default="0.1,0.5,1.0",
        help="Feedback scale (coupling) values (comma-separated)",
    )
    p_sta.add_argument(
        "--precision",
        default="float32,float16,bfloat16",
        help="Precision levels (comma-separated)",
    )
    p_sta.add_argument(
        "--noise-level",
        default="0.0,0.01,0.1",
        help="Noise level values (comma-separated)",
    )
    p_sta.add_argument(
        "--convergence-start",
        default="1,5,10",
        help="Convergence start (delay proxy) values (comma-separated)",
    )
    p_sta.add_argument("--seeds", type=int, default=3, help="Seeds per coordinate")
    p_sta.add_argument(
        "--epochs", type=int, default=3, help="Epochs per run (L1 fidelity)"
    )
    p_sta.add_argument(
        "--budget-seconds", type=float, default=3600.0, help="Budget in seconds"
    )
    p_sta.add_argument(
        "--run", action="store_true", help="Run the campaign after generating spec"
    )
    p_sta.add_argument(
        "--dry-run", action="store_true", help="Show plan without running"
    )
    p_sta.add_argument(
        "--run-id",
        default=None,
        help="Resume an existing run instead of starting a new one",
    )
    # Axis selection overrides (optional; defaults to stability-plasticity subset)
    p_sta.add_argument(
        "--axis-substrate",
        default=None,
        help="Substrate primitives (comma-separated; default: digital)",
    )
    p_sta.add_argument(
        "--axis-geometry",
        default=None,
        help="Geometry primitives (comma-separated; default: recurrent)",
    )
    p_sta.add_argument(
        "--axis-dynamics",
        default=None,
        help="Dynamics primitives (comma-separated; default: energy_minimization)",
    )
    p_sta.add_argument(
        "--axis-plasticity",
        default=None,
        help="Plasticity primitives (comma-separated; default: null)",
    )
    p_sta.add_argument(
        "--axis-credit",
        default=None,
        help="Credit primitives (comma-separated; default: thermodynamic_contrast)",
    )
    p_sta.add_argument(
        "--axis-update",
        default=None,
        help="Update primitives (comma-separated; default: euclidean)",
    )

    # Frozen-θ ψ benchmark command
    p_frozen = sub.add_parser(
        "frozen-theta-psi",
        help="Run frozen-θ ψ benchmarks at scale (multi-substrate, multi-plasticity)",
    )
    p_frozen.add_argument(
        "--store", default="frozen_psi.duckdb", help="DuckDB store path"
    )
    p_frozen.add_argument(
        "--output-dir",
        default="benchmark_results/frozen_theta_psi",
        help="Output directory for results",
    )
    p_frozen.add_argument(
        "--substrates",
        default="digital,memristive,neuromorphic,photonic,complex,analog,quantum",
        help="Substrates to test (comma-separated)",
    )
    p_frozen.add_argument(
        "--plasticity-types",
        default="null,routing,fast_weights,substrate_coupled",
        help="Plasticity types to test (comma-separated)",
    )
    p_frozen.add_argument(
        "--geometry",
        default="recurrent",
        help="Geometry primitive",
    )
    p_frozen.add_argument(
        "--dynamics",
        default="energy_minimization",
        help="Dynamics primitive",
    )
    p_frozen.add_argument(
        "--credit",
        default="thermodynamic_contrast",
        help="Credit primitive",
    )
    p_frozen.add_argument(
        "--update",
        default="euclidean",
        help="Update primitive",
    )
    p_frozen.add_argument(
        "--epochs", type=int, default=10, help="Pre-training epochs (L2 fidelity)"
    )
    p_frozen.add_argument(
        "--recovery-steps", type=int, default=20, help="Recovery training steps"
    )
    p_frozen.add_argument(
        "--damage-severity", type=float, default=0.3, help="Damage severity (0-1)"
    )
    p_frozen.add_argument("--seeds", type=int, default=3, help="Number of seeds")
    p_frozen.add_argument("--device", default="auto", help="Device (auto, cpu, cuda)")
    p_frozen.add_argument("--run", action="store_true", help="Run the benchmark")
    p_frozen.add_argument(
        "--dry-run", action="store_true", help="Show plan without running"
    )

    return parser


# Cells trained concurrently. Above this, cells contend for one device and each
# reports the walltime of all of them, which turns ``walltime_total`` into a
# measurement of the batch rather than of the cell.
_CELL_WORKERS = 4


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
        batch_limit=overrides.get("batch_limit", profile.batch_limit),
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
        batch_limit=profile.batch_limit,
        budget_seconds=profile.budget_seconds,
        param_budget=profile.param_budget,
        policy=profile.policy,
        axes=profile.axes,
        checkpoint_every_n=profile.checkpoint_every_n,
    )


def execute_spec(
    spec: RunSpec,
    *,
    store_path: str,
    run_id: str | None = None,
) -> int:
    """Execute one declared spec into one store, and close the run.

    The single execution path. A campaign command that builds its own runner
    duplicates this and drops the parts it did not copy: TODO51\'s
    ``stability-plasticity`` left every run row at ``status=running`` with no
    ``finished_at``, and minted a fresh ``run_id`` per launch so an interrupted
    campaign could not be resumed.

    Args:
        spec: The run declaration; the only source of policy and objectives.
        store_path: DuckDB path to run into.
        run_id: Resume an existing run instead of creating one.

    Returns:
        Process exit code: 0 completed, 1 failed, 130 interrupted.
    """
    import signal

    policy_name = spec.policy or "round_robin_grid"

    with RecordStore(StoreConfig(path=Path(store_path))) as store:
        run = run_id or store.create_run(spec=spec)
        logger.info("Run ID: %s", run)

        budget = (
            Budget.from_duration(_duration_str(spec.budget_seconds))
            if spec.budget_seconds is not None
            else None
        )

        # The spec is the only place a policy\'s arguments come from, so the
        # sampler learns on the run\'s objectives and its own swept domains.
        from computronium.experiment.execution.evaluate import task_shape

        policy = create_policy(
            policy_name, **policy_context(spec, policy_name, shape=task_shape)
        )

        # Without S10 Decide there is no decision to continue or stop on, so
        # the loop would run until the space is exhausted by some other means.
        max_rounds = None
        if spec.stages and StageId.S10_DECIDE not in spec.stages:
            max_rounds = 1

        runner = PipelineRunner(
            PipelineConfig(
                run_id=run,
                run_spec=spec,
                budget=budget,
                cost_model=SimpleCostModel(),
                policy=policy,
                backend=LocalBackend(max_workers=_CELL_WORKERS),
                seed=spec.seed,
                max_rounds=max_rounds,
            ),
            store,
        )

        # Handle both SIGINT (Ctrl-C) and SIGTERM (setsid background termination)
        # so that background campaigns close their run row properly.
        interrupted = {"flag": False}

        def _signal_handler(signum, _frame):
            logger.info("Received signal %s; finishing run %s", signum, run)
            interrupted["flag"] = True
            # Trigger graceful shutdown of runner (stops backend, saves checkpoints)
            runner.shutdown()

        old_sigint = signal.signal(signal.SIGINT, _signal_handler)
        old_sigterm = signal.signal(signal.SIGTERM, _signal_handler)

        try:
            outcomes = asyncio.run(runner.run())
        except KeyboardInterrupt:
            logger.info("Interrupted; resume with --run-id %s", run)
            store.finish_run(run, "interrupted", budget_consumed_s=_consumed(runner))
            return 130
        except Exception as exc:
            logger.error("Pipeline failed: %s", exc, exc_info=True)
            store.finish_run(run, "failed", budget_consumed_s=_consumed(runner))
            return 1
        finally:
            signal.signal(signal.SIGINT, old_sigint)
            signal.signal(signal.SIGTERM, old_sigterm)

        if interrupted["flag"]:
            logger.info("Run interrupted by signal; resume with --run-id %s", run)
            store.finish_run(run, "interrupted", budget_consumed_s=_consumed(runner))
            return 130

        _settle_maturity(store, run, spec)

        budget_consumed = _consumed(runner)
        store.finish_run(run, "completed", budget_consumed_s=budget_consumed)
        logger.info(
            "Run %s completed with %d records in %s",
            run,
            len(outcomes),
            f"{budget_consumed:.1f}s" if budget_consumed is not None else "no budget",
        )
        return 0


def _consumed(runner: PipelineRunner) -> float | None:
    """Seconds the run's budget reports it spent, or ``None`` if it had none."""
    budget = runner._state.budget
    return budget.elapsed_seconds() if budget is not None else None


def _settle_maturity(store: RecordStore, run_id: str, spec: RunSpec) -> None:
    """Post-measurement bookkeeping: promotion, then across-seed uncertainty.

    Maturity is earned from what landed, not declared up front, so this runs
    on the run\'s own store after the rounds are done.
    """
    from computronium.experiment.evidence.claims import compute_and_store_uncertainty
    from computronium.experiment.execution.promotion import promote_run
    from computronium.experiment.schema.record import Maturity
    from computronium.experiment.schema.registries import REPLAY_METRIC_TOLERANCE

    history = promote_run(store, run_id, spec, tolerance=REPLAY_METRIC_TOLERANCE)
    logger.info(
        "Promotion: %d cell(s) assessed, %d earned L2",
        len(history),
        sum(1 for entry in history if entry["maturity"] == Maturity.L2.value),
    )
    uncertainty = compute_and_store_uncertainty(store, run_id, min_seeds=spec.n_seeds)
    logger.info(
        "Uncertainty: computed for %d cell(s) with >=%d seeds",
        len(uncertainty),
        spec.n_seeds,
    )


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute a run from a spec file or a named profile."""
    spec = _resolve_spec(args)

    # A dry run writes nothing: not a store, not a run row, not a checkpoint.
    if args.dry_run:
        print(_dry_run_report(spec, policy_name=spec.policy or "round_robin_grid"))
        return 0

    return execute_spec(spec, store_path=args.store, run_id=args.run_id)


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

        elif args.format == "html":
            output_path = args.output or f"{run_id}.report.html"
            generate_html_report(store, run_id, output_path)
            logger.info(f"HTML report written to {output_path}")
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
    from computronium.visualization.gallery import render_gallery

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


def _cmd_stability_plasticity(args: argparse.Namespace) -> int:  # ruff: ignore[too-many-statements, too-many-locals, complex-structure]
    """Generate and optionally run a stability-plasticity frontier campaign."""
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.run_spec import (
        AxisSelection,
        Domain,
        RunSpec,
        Scale,
    )

    # Parse sweep parameters (using valid hyperparameter names)
    rho_vals = tuple(float(x) for x in args.rho.split(","))
    feedback_scale_vals = tuple(float(x) for x in args.feedback_scale.split(","))
    precision_vals = tuple(args.precision.split(","))
    noise_level_vals = tuple(float(x) for x in args.noise_level.split(","))
    # Replace 0.0 with a small positive value for log scale
    noise_level_vals = tuple(max(v, 1e-6) for v in noise_level_vals)
    convergence_start_vals = tuple(int(x) for x in args.convergence_start.split(","))

    # Create axis selections - use CLI overrides or defaults
    def _parse_axis(arg_value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
        if arg_value is None:
            return default
        return tuple(x.strip() for x in arg_value.split(","))

    substrate_prims = _parse_axis(args.axis_substrate, ("digital",))
    geometry_prims = _parse_axis(args.axis_geometry, ("recurrent",))
    dynamics_prims = _parse_axis(args.axis_dynamics, ("energy_minimization",))
    plasticity_prims = _parse_axis(args.axis_plasticity, ("null",))
    credit_prims = _parse_axis(args.axis_credit, ("thermodynamic_contrast",))
    update_prims = _parse_axis(args.axis_update, ("euclidean",))

    # Calculate total cells (axis primitive combinations × hyperparameter sweep)
    axis_combinations = (
        len(substrate_prims)
        * len(geometry_prims)
        * len(dynamics_prims)
        * len(plasticity_prims)
        * len(credit_prims)
        * len(update_prims)
    )
    hyperparameter_combinations = (
        len(rho_vals)
        * len(feedback_scale_vals)
        * len(precision_vals)
        * len(noise_level_vals)
        * len(convergence_start_vals)
    )
    total_cells = axis_combinations * hyperparameter_combinations

    print("Stability-Plasticity Campaign")
    print(f"  Rho (contraction): {rho_vals}")
    print(f"  Feedback scale (coupling): {feedback_scale_vals}")
    print(f"  Precision: {precision_vals}")
    print(f"  Noise level: {noise_level_vals}")
    print(f"  Convergence start (delay proxy): {convergence_start_vals}")
    print(
        f"  Axis primitives: substrate={substrate_prims}, geometry={geometry_prims}, "
        f"dynamics={dynamics_prims}, plasticity={plasticity_prims}, "
        f"credit={credit_prims}, update={update_prims}"
    )
    print(f"  Axis combinations: {axis_combinations}")
    print(f"  Hyperparameter combinations: {hyperparameter_combinations}")
    print(f"  Total coordinates: {total_cells}")
    print(f"  Seeds per coordinate: {args.seeds}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Budget: {args.budget_seconds}s")

    axes = (
        AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=substrate_prims),
        AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=geometry_prims),
        AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=dynamics_prims),
        AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=plasticity_prims),
        AxisSelection(axis=StructuralAxis.CREDIT, primitives=credit_prims),
        AxisSelection(axis=StructuralAxis.UPDATE, primitives=update_prims),
    )

    # Hyperparameters for the stability-plasticity sweep
    # Map to valid hyperparameter names from harvest
    def _make_domain(vals, scale=Scale.LINEAR, is_int=False):
        """Create Domain from values - categorical if single value, range otherwise."""
        if len(vals) == 1:
            # Keep native type for categorical domains
            return Domain(members=(vals[0],))
        if is_int:
            return Domain(lo=min(vals), hi=max(vals), scale=scale)
        return Domain(lo=min(vals), hi=max(vals), scale=scale)

    hyperparameters = {
        "rho": _make_domain(rho_vals, Scale.LOG),
        "feedback_scale": _make_domain(feedback_scale_vals, Scale.LOG),
        "precision": Domain(members=precision_vals),
        "noise_level": _make_domain(noise_level_vals, Scale.LOG),
        "convergence_start": _make_domain(
            convergence_start_vals, Scale.LINEAR, is_int=True
        ),
        # Constrain hidden_dim to respect param_budget for recurrent geometry
        # With param_budget=200000 and 25% tolerance, max params = 250000
        # For recurrent: 64*H + H + (L-1)*(H*H + H) + H*10 + 10
        # Max at L=4: 3*H^2 + 85*H + 10 <= 250000 => H <= ~270
        "hidden_dim": Domain(lo=32.0, hi=256.0, scale=Scale.LOG),
    }

    # Gate is a categorical sweep - we'll handle it via the grid
    # For now, we include it in operating_points for reference
    operating_points = {
        "rho_sweep": list(rho_vals),
        "feedback_scale_sweep": list(feedback_scale_vals),
        "precision_sweep": list(precision_vals),
        "noise_level_sweep": list(noise_level_vals),
        "convergence_start_sweep": list(convergence_start_vals),
    }

    # Axis-aligned objectives. The stability set is the campaign's subject:
    # rho, sigma_max and their ratio are the frontier's three axes, and
    # settle_steps is the horizon the step was measured against.
    axis_objectives = {
        "task": ("validation_accuracy",),
        "stability": (
            "spectral_radius",
            "max_singular_value",
            "nonnormality",
            "stability_margin",
            "lyapunov_exponent",
            "settle_steps",
        ),
        "cost": ("walltime_total", "param_count", "energy_per_step"),
    }

    # Create RunSpec. `objectives` is the union of the axis sets: the combined
    # study needs a direction per name, and the per-axis studies read the sets.
    objectives = tuple(
        dict.fromkeys(o for objs in axis_objectives.values() for o in objs)
    )

    spec = RunSpec(
        version=2,
        profile="stability-plasticity",
        task="digits",
        objectives=objectives,
        fidelity="L1",
        n_seeds=args.seeds,
        epochs=args.epochs,
        budget_seconds=args.budget_seconds,
        param_budget=500000,
        policy="model_based",
        axes=axes,
        hyperparameters=hyperparameters,
        operating_points=operating_points,
        axis_objectives=axis_objectives,
        deterministic=True,
        num_workers=0,
        sweep_steps=243,
    )

    # Output spec if requested
    if args.output_spec:
        output_path = Path(args.output_spec)
        output_path.write_text(json.dumps(spec.to_dict(), indent=2), encoding="utf-8")
        print(f"Spec written to {output_path}")

    # Dry run or run
    if args.dry_run:
        from computronium.experiment.execution.search_space import (
            iter_candidates,
            search_space_from_spec,
        )

        print("\nDry run - first 5 candidates:")
        search_space = search_space_from_spec(spec)
        for count, (coord, sched) in enumerate(iter_candidates(spec, search_space)):
            print(f"  {coord}")
            if count >= 4:
                break
        print(f"... (total {total_cells} coordinates)")
        return 0

    if not args.run:
        print("Spec generated. Use --run to execute or --dry-run to preview.")
        return 0

    # Run the campaign. Same executor every run uses, so the run row is closed,
    # maturity is settled, and --run-id resumes an interrupted campaign.
    print("Running campaign...")
    return execute_spec(spec, store_path=args.store, run_id=args.run_id)


def _cmd_frozen_theta_psi(args: argparse.Namespace) -> int:
    """Run frozen-θ ψ benchmarks at scale (multi-substrate, multi-plasticity)."""
    from pathlib import Path

    from computronium.benchmarks.joint.structural_robustness import (
        run_structural_robustness_suite,
    )

    substrates = (
        tuple(args.substrates.split(","))
        if args.substrates
        else (
            "digital",
            "memristive",
            "neuromorphic",
            "photonic",
            "complex",
            "analog",
            "quantum",
        )
    )
    plasticity_types = (
        tuple(args.plasticity_types.split(","))
        if args.plasticity_types
        else ("null", "routing", "fast_weights", "substrate_coupled")
    )

    # Generate coordinates for all combinations
    coordinates = []
    neuromorphic_plasticity = {"null", "routing"}
    no_substrate_coupled = {"photonic", "quantum"}
    for substrate in substrates:
        for plasticity in plasticity_types:
            # Skip invalid combinations
            if (
                substrate == "neuromorphic"
                and plasticity not in neuromorphic_plasticity
            ):
                continue  # Neuromorphic only supports null and routing
            if substrate in no_substrate_coupled and plasticity == "substrate_coupled":
                continue  # Substrate coupled not implemented for these yet

            coord = f"{substrate}/{args.geometry}/{args.dynamics}/{plasticity}/{args.credit}/{args.update}"
            coordinates.append(coord)

    print("Frozen-θ ψ Benchmark Campaign")
    print(f"  Substrates: {substrates}")
    print(f"  Plasticity types: {plasticity_types}")
    print(f"  Geometry: {args.geometry}")
    print(f"  Dynamics: {args.dynamics}")
    print(f"  Credit: {args.credit}")
    print(f"  Update: {args.update}")
    print(f"  Total coordinates: {len(coordinates)}")
    print(f"  Seeds per coordinate: {args.seeds}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Recovery steps: {args.recovery_steps}")
    print(f"  Damage severity: {args.damage_severity}")

    if args.dry_run:
        print("\nDry run - coordinates:")
        for coord in coordinates:
            print(f"  {coord}")
        return 0

    if not args.run:
        print("Plan generated. Use --run to execute or --dry-run to preview.")
        return 0

    print("Running benchmark...")
    output_dir = Path(args.output_dir)

    run_structural_robustness_suite(
        coordinates=coordinates,
        output_dir=output_dir,
        epochs=args.epochs,
        recovery_steps=args.recovery_steps,
        damage_severity=args.damage_severity,
        seeds=args.seeds,
        device=args.device,
    )

    print("Benchmark complete.")
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
        "stability-plasticity": _cmd_stability_plasticity,
        "frozen-theta-psi": _cmd_frozen_theta_psi,
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
