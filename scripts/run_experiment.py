#!/usr/bin/env python
"""Minimal time-boxed experiment runner.

One loop: while deadline not hit, propose next cell, train it, store it.
Nothing else.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import torch

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.execution.search_space import iter_candidates, search_space_from_spec
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES
from computronium.experiment.execution.pipeline import _resolve_tasks


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
    axes = tuple(
        AxisSelection(axis=_AXIS_BY_FLAG[flag], primitives=tuple(prims))
        for flag, prims in (config.axes or {}).items()
    ) or profile.axes

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


async def _run_loop(spec: RunSpec, store: RecordStore, run_id: str, deadline: Deadline, backend, device: str) -> int:
    """Run cells until deadline. Return records stored."""
    # Build search space
    tasks = spec.task_names
    space = search_space_from_spec(spec, tasks=tasks)

    # Get cells from the iterator (already screened for composability)
    cell_iter = iter_candidates(
        spec, space, shape=task_shape, check_composable=True
    )

    # Track already-measured keys from store
    completed = {r.measurement_key for r in store.query_records(run_id=run_id)}

    count = 0
    for coord, sched in cell_iter:
        # Hard stop: grace period expired
        if deadline.expired():
            print(f"Hard deadline (with grace) reached, stopping after {count} cells")
            break

        # Soft stop: only stop if we already measured something
        if deadline.soft_expired() and count > 0:
            print(f"Soft deadline reached after {count} cells, stopping")
            break

        key = coord.measurement_key(sched)
        if key in completed:
            continue

        print(f"  Cell {count + 1}: {coord.cell_key()} (seed={sched.seed})")

        # Train single cell
        from computronium.experiment.schema.coordinate import Provenance
        prov = Provenance(env={}, dataset="unknown", dataset_version="1.0", code_sha="unknown", policy=spec.policy or "unknown", links={"run_id": run_id})
        params = {}
        records = await backend.submit(coord, sched, prov, params, store)
        for r in records:
            store.append(r)
            completed.add(r.measurement_key)
        count += 1

    return count


async def main() -> int:
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

    axes = {
        flag: [v.strip() for v in getattr(args, flag).split(",") if v.strip()]
        for flag in _AXIS_BY_FLAG
        if getattr(args, flag)
    }

    config = Config(
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

    device = _resolve_device(config.device)
    spec = _build_spec(config, device)

    if args.dry_run:
        print(f"DRY RUN: profile={spec.profile} budget={spec.budget_seconds:.1f}s")
        print(f"  task={spec.task} policy={spec.policy} epochs={spec.epochs}")
        return 0

    Path(config.store).parent.mkdir(parents=True, exist_ok=True)

    with RecordStore(StoreConfig(path=Path(config.store))) as store:
        run_id = store.create_run(spec=spec)
        print(f"Run {run_id}: {config.hours}h ({config.hours*3600:.0f}s) on {device}")

        # Deadline starts AFTER store setup, so startup time doesn't eat the budget
        deadline = Deadline.from_hours(config.hours)
        backend = LocalBackend(max_workers=1)

        start = time.time()
        n = await _run_loop(spec, store, run_id, deadline, backend, device)
        elapsed = time.time() - start

        store.finish_run(run_id, "completed", budget_consumed_s=elapsed)

    # Quick summary
    budget = spec.budget_seconds
    util = elapsed / budget
    print(f"\n{'='*50}")
    print(f"Run {run_id} done in {elapsed:.1f}s (budget {budget:.1f}s, {util:.1%})")
    print(f"Cells measured: {n}")

    # Budget check
    eps = max(0.02 * budget, 5.0)
    if budget - eps <= elapsed <= budget + 30.0:
        print("✅ Budget window: PASS")
    else:
        print(f"❌ Budget window: FAIL (eps={eps:.1f}s, grace=30s)")

    return 0


if __name__ == "__main__":
    import asyncio
    sys.exit(asyncio.run(main()))