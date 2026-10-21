"""Turning a profile into a spec, and a spec into a run."""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import argparse

    from computronium.experiment.schema.record import Record

from computronium.core.logging import get_logger
from computronium.experiment.evidence.mirror import mirror_path
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.policy import create_policy, policy_context
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import RunSpec

from ._profiles import RUN_PROFILES, RunProfile

logger = get_logger()

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
        hyperparameters=overrides.get("hyperparameters", profile.hyperparameters),
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
    from computronium.experiment.execution.pipeline import _resolve_tasks
    from computronium.experiment.kernel.evaluate import task_shape
    from computronium.experiment.kernel.search_space import (
        iter_candidates,
        search_space_from_spec,
    )
    from computronium.experiment.schema.harvest import AXIS_KIND_ORDER

    tasks = _resolve_tasks(PipelineConfig(run_id="dry-run", run_spec=spec))
    space = search_space_from_spec(spec, tasks=tasks)
    lines = [
        "space:",
        f"  profile: {spec.profile}",
        f"  task(s): {', '.join(tasks)}",
        f"  fidelity: {spec.fidelity}  epochs: {spec.epochs}  seeds: {spec.n_seeds}",
        f"  batch_limit: {spec.batch_limit}  param_budget: {spec.param_budget}",
        f"  policy: {policy_name}",
        f"  objectives: {', '.join(spec.objectives) or 'all'}",
        f"  spec version: {spec.version}",
    ]
    for axis in StructuralAxis:
        names = space.primitives(axis)
        lines.append(
            f"  axis {axis.value}: {len(names)} \u2014 {', '.join(names) or 'none'}"
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

    # The price, the stop point, and the primitives no legal cell reaches
    # (TODO48b R2): every fixture-sizing guess a session makes by trial is a
    # print here instead.
    from computronium.experiment.execution.pricing import price_plan

    plan = price_plan(spec, space)
    budget = f"{spec.budget_seconds:g}s" if spec.budget_seconds is not None else "none"
    lines.append("")
    lines.append("price:")
    lines.extend(f"  {line}" for line in plan.render_price())
    lines.extend(["", "budget:", f"  declared: {budget}", f"  {plan.render_budget()}"])
    lines.extend(["", f"first cells ({len(cells)} of {plan.legal_cells} legal):"])
    lines.extend(cells)
    return "\n".join(lines)


def spec_from_profile(
    profile: RunProfile,
    *,
    task: str | None = None,
    device: str | None = "auto",
) -> RunSpec:
    """Build the run declaration a profile names.

    The single mapping from a profile to a spec, so every path that runs a
    profile — the CLI, the dashboard screenshot pipeline — declares the same
    run.

    Args:
        profile: The named profile to declare.
        task: Task override; the profile's own when omitted.
        device: Device for the run.

    Returns:
        The run declaration.
    """
    return RunSpec(
        profile=profile.name,
        task=task or profile.task,
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
        hyperparameters=dict(profile.hyperparameters),
        checkpoint_every_n=profile.checkpoint_every_n,
        device=device,
    )


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
    return spec_from_profile(profile, task=args.task, device=args.device)


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

    from computronium.experiment.execution.deadline import Deadline

    policy_name = spec.policy or "round_robin_grid"

    with RecordStore(
        StoreConfig(path=Path(store_path), mirror_path=mirror_path(Path(store_path)))
    ) as store:
        run = run_id or store.create_run(spec=spec)
        logger.info("Run ID: %s", run)

        deadline = (
            Deadline.from_seconds(spec.budget_seconds)
            if spec.budget_seconds is not None
            else None
        )

        # The spec is the only place a policy\'s arguments come from, so the
        # sampler learns on the run\'s objectives and its own swept domains.
        from computronium.experiment.kernel.evaluate import task_shape

        policy = create_policy(
            policy_name,
            **policy_context(spec, policy_name, shape=task_shape, deadline=deadline),
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
                deadline=deadline,
                cost_model=None,
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
    """Seconds the run's deadline reports elapsed, or ``None`` if it had none."""
    deadline = runner._state.deadline
    if deadline is not None:
        return deadline.elapsed_seconds()
    return None


def _settle_maturity(store: RecordStore, run_id: str, spec: RunSpec) -> None:
    """Post-measurement bookkeeping: promotion, then across-seed uncertainty.

    Maturity is earned from what landed, not declared up front, so this runs
    on the run's own store after the rounds are done.

    Uses statistical promotion gates (L1: superiority, CI width, train/val gap,
    rho band; L2: replay) with config-driven thresholds.
    """
    from dataclasses import replace

    from computronium.experiment.evidence.claims import compute_and_store_uncertainty
    from computronium.experiment.execution.statistical_promotion import (
        GateThresholds,
        promote_with_stats,
    )
    from computronium.experiment.kernel import cell_record
    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.experiment.schema.record import Maturity
    from computronium.experiment.schema.registries import REPLAY_METRIC_TOLERANCE

    # Use statistical gates with thresholds adapted to the run's seed count
    # For low-seed runs, use relaxed thresholds; statistical gates need n>=5
    min_seeds = max(spec.n_seeds, 5) if spec.n_seeds >= 3 else spec.n_seeds
    thresholds = GateThresholds(
        min_seeds_for_stats=min_seeds,
        superiority_margin_sigma=1.0 if spec.n_seeds < 5 else 2.0,
        ci_width_threshold=0.1 if spec.n_seeds < 5 else 0.05,
    )
    baselines = _resolve_baselines(store, run_id, spec)

    def confirmation_evaluator(
        cell_records: list[Record], confirmation_seeds: list[int]
    ) -> list[Record]:
        base = cell_records[0]
        coordinate = Coordinate.from_record(base)
        confirmed: list[Record] = []
        for seed in confirmation_seeds:
            record = cell_record(
                coordinate=coordinate,
                schedule=replace(base.schedule, seed=seed),
                provenance=base.provenance,
            )
            store.append(record)
            confirmed.append(record)
        return confirmed

    history = promote_with_stats(
        store,
        run_id,
        spec,
        tolerance=REPLAY_METRIC_TOLERANCE,
        thresholds=thresholds,
        baselines=baselines,
        confirmation_evaluator=confirmation_evaluator,
    )
    logger.info(
        "Promotion: %d cell(s) assessed, %d earned L2",
        len(history),
        sum(1 for entry in history if entry["maturity"] == Maturity.L2.value),
    )
    for entry in history:
        gates = entry.get("statistical_gates", {})
        passed = gates.get("all_passed", False)
        logger.info(
            "  Cell %s: maturity=%s, replay=%s, stats_gates_passed=%s",
            entry["cell_key"][:12],
            entry["maturity"],
            entry["replay"],
            passed,
        )
    uncertainty = compute_and_store_uncertainty(store, run_id, min_seeds=spec.n_seeds)
    logger.info(
        "Uncertainty: computed for %d cell(s) with >=%d seeds",
        len(uncertainty),
        spec.n_seeds,
    )


def _resolve_baselines(
    store: RecordStore, run_id: str, spec: RunSpec
) -> dict[str, Any] | None:
    """The same-task backprop ruler for this run's eligible cells, if present.

    Read from the store by the same registry call the loop driver makes: the
    run's own ``gradient × instantaneous`` cells are the ruler when they exist.
    Absent a ruler the superiority gate is skipped rather than failed.
    """
    from computronium.experiment.execution.promotion import eligible_cells
    from computronium.experiment.registry.baseline import BaselineRegistry

    if spec.budget_seconds is None or not spec.task_names:
        return None
    registry = BaselineRegistry(store=store)
    try:
        fingerprint = registry.compute_hardware_fingerprint()
    except Exception as exc:  # ruff: ignore[blind-except] - fingerprint is best-effort
        logger.warning("Hardware fingerprint unavailable: %s", exc)
        return None
    baseline = registry.get_baseline(
        spec.task_names[0], fingerprint, spec.budget_seconds, spec.n_seeds
    )
    if baseline is None:
        return None
    keys = eligible_cells(store.query_records(run_id=run_id), spec.n_seeds).keys()
    return dict.fromkeys(keys, baseline)
