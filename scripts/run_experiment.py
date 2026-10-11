#!/usr/bin/env python
"""Minimal time-boxed experiment runner.

One loop: while deadline not hit, propose next cell, train it, store it.
Nothing else.
"""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

import torch

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.search_space import (
    declared_cell_count,
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES
from computronium.experiment.surface.report import ReportGenerator, generate_html_report


@dataclass(frozen=True, slots=True)
class Config:
    hours: float
    device: str
    store: str
    policy: str = "round_robin_grid"
    profile: str = "production-map"
    seed: int = 42
    epochs: int | None = None
    n_seeds: int | None = None
    param_budget: int | None = None
    axes: dict[str, list[str]] | None = None


_shutdown_requested = [False]


def _signal_handler(signum, frame):
    _shutdown_requested[0] = True
    print(f"\nSignal {signum} received, requesting graceful shutdown...", flush=True)


signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def _resolve_device(device: str) -> str:
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


_AXIS_BY_FLAG = {
    "substrates": StructuralAxis.SUBSTRATE,
    "geometries": StructuralAxis.GEOMETRY,
    "dynamics": StructuralAxis.DYNAMICS,
    "credits": StructuralAxis.CREDIT,
    "updates": StructuralAxis.UPDATE,
    "plasticities": StructuralAxis.PLASTICITY,
}


def _build_spec(config: Config, device: str) -> RunSpec:
    profile = RUN_PROFILES[config.profile]
    axes = (
        tuple(
            AxisSelection(axis=_AXIS_BY_FLAG[flag], primitives=tuple(prims))
            for flag, prims in (config.axes or {}).items()
        )
        or profile.axes
    )

    return RunSpec(
        profile=profile.name,
        task=profile.task,
        objectives=profile.objectives,
        stages=tuple(profile.stages),
        fidelity=profile.fidelity,
        n_seeds=config.n_seeds or profile.n_seeds,
        epochs=config.epochs or profile.epochs,
        batch_limit=profile.batch_limit,
        budget_seconds=config.hours * 3600.0,
        param_budget=config.param_budget or profile.param_budget,
        policy=config.policy,
        axes=axes,
        checkpoint_every_n=profile.checkpoint_every_n,
        seed=config.seed,
        device=device,
    )


def _print_experiment(spec: RunSpec, space) -> None:
    """Name the experiment being run and its search space, before any cell."""
    from computronium.experiment.schema.axis import StructuralAxis

    print("=" * 70, flush=True)
    print(f"EXPERIMENT  profile={spec.profile}  task={spec.task}", flush=True)
    print(
        f"  fidelity={spec.fidelity} epochs={spec.epochs} seeds={spec.n_seeds} "
        f"param_budget={spec.param_budget} policy={spec.policy}",
        flush=True,
    )
    for axis in StructuralAxis:
        primitives = space.primitives(axis)
        print(
            f"  {axis.value:<12} [{len(primitives)}] {', '.join(primitives)}",
            flush=True,
        )
    total = declared_cell_count(spec, space)
    print(f"  declared cells: {total:,}", flush=True)
    print("=" * 70, flush=True)


async def _run_loop(
    spec: RunSpec,
    store: RecordStore,
    run_id: str,
    deadline: Deadline,
    backend,
    device: str,
) -> int:
    """Run cells until deadline. Return records stored."""
    tasks = spec.task_names
    space = search_space_from_spec(spec, tasks=tasks)

    _print_experiment(spec, space)

    cell_iter = iter_candidates(
        spec, space, deadline=deadline, shape=task_shape, check_composable=True
    )

    completed = {r.measurement_key for r in store.query_records(run_id=run_id)}

    count = 0
    for coord, sched in cell_iter:
        if _shutdown_requested[0]:
            print("Shutdown requested, stopping...", flush=True)
            break

        if deadline.expired():
            print(
                f"Hard deadline (with grace) reached, stopping after {count} cells",
                flush=True,
            )
            break

        if deadline.soft_expired() and count > 0:
            print(f"Soft deadline reached after {count} cells, stopping", flush=True)
            break

        key = coord.measurement_key(sched)
        if key in completed:
            continue

        print(
            f"  Cell {count + 1}: substrate={coord.substrate} geometry={coord.geometry} "
            f"dynamics={coord.dynamics} credit={coord.credit} update={coord.update} "
            f"plasticity={coord.plasticity} (seed={sched.seed})",
            flush=True,
        )

        from computronium.experiment.schema.coordinate import Provenance

        prov = Provenance(
            env={},
            dataset="unknown",
            dataset_version="1.0",
            code_sha="unknown",
            policy=spec.policy or "unknown",
            links={"run_id": run_id},
        )
        params = {}
        try:
            records = await backend.submit(coord, sched, prov, params, store)
            for r in records:
                store.append(r)
                completed.add(r.measurement_key)
            count += 1
        except Exception as e:
            print(f"  Cell {count + 1} FAILED: {e}", flush=True)
            traceback.print_exc()
            # Continue to next cell

    return count


def _parse_axes(args: argparse.Namespace) -> dict[str, list[str]]:
    return {
        flag: [v.strip() for v in getattr(args, flag).split(",") if v.strip()]
        for flag in _AXIS_BY_FLAG
        if getattr(args, flag)
    }


def _build_config(args: argparse.Namespace, axes: dict[str, list[str]]) -> Config:
    return Config(
        hours=args.hours,
        device=args.device,
        store=args.store,
        policy=args.policy,
        profile=args.profile,
        seed=args.seed,
        epochs=args.epochs,
        n_seeds=args.n_seeds,
        param_budget=args.param_budget,
        axes=axes or None,
    )


def _print_dry_run(spec: RunSpec) -> None:
    print(
        f"DRY RUN: profile={spec.profile} budget={spec.budget_seconds:.1f}s", flush=True
    )
    print(f"  task={spec.task} policy={spec.policy} epochs={spec.epochs}", flush=True)


def _run_experiment(
    config: Config, device: str, spec: RunSpec
) -> tuple[str, float, int]:
    Path(config.store).parent.mkdir(parents=True, exist_ok=True)

    with RecordStore(StoreConfig(path=Path(config.store))) as store:
        run_id = store.create_run(spec=spec)
        print(
            f"Run '{spec.profile}/{spec.task}/{config.hours:g}h' "
            f"started on {device} (id={run_id[:8]})",
            flush=True,
        )

        deadline = Deadline.from_hours(config.hours)
        backend = LocalBackend(max_workers=1)

        start = time.time()
        try:
            n = asyncio.run(_run_loop(spec, store, run_id, deadline, backend, device))
        except Exception as e:
            print(f"Experiment crashed: {e}", flush=True)
            traceback.print_exc()
            store.finish_run(run_id, "crashed", budget_consumed_s=time.time() - start)
            raise
        elapsed = time.time() - start

        store.finish_run(run_id, "completed", budget_consumed_s=elapsed)

    return run_id, elapsed, n


def _check_budget(budget: float, elapsed: float) -> bool:
    eps = max(0.02 * budget, 5.0)
    if budget - eps <= elapsed <= budget + 30.0:
        print("✅ Budget window: PASS", flush=True)
        return True
    print(f"❌ Budget window: FAIL (eps={eps:.1f}s, grace=30s)", flush=True)
    return False


def _generate_report(config: Config, run_id: str) -> Path:
    with RecordStore(StoreConfig(path=Path(config.store), read_only=True)) as store:
        generator = ReportGenerator(store)

        distinct_cells = len({r.cell_key for r in store.query_records(run_id=run_id)})
        pareto = generator.pareto_frontier(run_id)
        coverage = generator.axis_coverage(run_id)
        failures = generator.failures_by_cause(run_id)

        print(f"Distinct cells:   {distinct_cells}", flush=True)
        print(f"Pareto points:    {len(pareto)}", flush=True)
        print(f"Coverage axes:    {len(coverage)}", flush=True)
        print(f"Failure taxonomy: {failures}", flush=True)

        report_path = Path(config.store).with_suffix(".html")
        generate_html_report(store, run_id, report_path)
        print(f"HTML report:      {report_path}", flush=True)

    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal time-boxed experiment runner")
    parser.add_argument("--hours", type=float, required=True)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--store", default="results/experiment.db")
    parser.add_argument("--policy", default="round_robin_grid")
    parser.add_argument("--profile", default="production-map")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--n-seeds", type=int, default=None)
    parser.add_argument("--param-budget", type=int, default=None)
    parser.add_argument("--substrates", type=str)
    parser.add_argument("--geometries", type=str)
    parser.add_argument("--dynamics", type=str)
    parser.add_argument("--credits", type=str)
    parser.add_argument("--updates", type=str)
    parser.add_argument("--plasticities", type=str)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    axes = _parse_axes(args)
    config = _build_config(args, axes)
    device = _resolve_device(config.device)
    spec = _build_spec(config, device)

    if args.dry_run:
        _print_dry_run(spec)
        return 0

    try:
        run_id, elapsed, n = _run_experiment(config, device, spec)
    except Exception as e:
        print(f"FATAL: {e}", flush=True)
        return 1

    budget = spec.budget_seconds
    util = elapsed / budget
    print(f"\n{'=' * 50}", flush=True)
    print(
        f"Run {run_id[:8]} done in {elapsed:.1f}s (budget {budget:.1f}s, {util:.1%})",
        flush=True,
    )
    print(f"Cells measured: {n}", flush=True)

    if n == 0:
        print(
            "FATAL: no cells measured — search space yielded nothing. "
            "Refusing to generate an empty report.",
            flush=True,
        )
        return 1

    _check_budget(budget, elapsed)
    _generate_report(config, run_id)

    return 0


if __name__ == "__main__":
    sys.exit(main())
