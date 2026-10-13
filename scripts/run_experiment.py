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
from computronium.experiment.execution.stream import CellStream
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import (
    declared_cell_count,
    search_space_from_spec,
)
from computronium.experiment.reporters import (
    JSONReportConfig,
    ReportConfig,
    generate_html_report,
    generate_json_report,
)
from computronium.experiment.schema import RunSpec, harvest_schema
from computronium.experiment.schema.axis import AxisKind, StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES
from computronium.experiment.surface.report import ReportGenerator


@dataclass(frozen=True, slots=True)
class Config:
    hours: float
    device: str
    store: str
    policy: str = "model_based"
    profile: str = "production-map"
    seed: int = 42
    epochs: int | None = None
    n_seeds: int | None = None
    param_budget: int | None = None
    axes: dict[str, list[str]] | None = None
    verbose: bool = False
    fidelity: str | None = None
    batch_limit: int | None = None
    sweep_steps: int | None = None


_shutdown_requested = [False]
_shutdown_signum = [0]


def _signal_handler(signum, frame):
    _shutdown_requested[0] = True
    _shutdown_signum[0] = signum


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
        fidelity=config.fidelity or profile.fidelity,
        n_seeds=config.n_seeds or profile.n_seeds,
        epochs=config.epochs or profile.epochs,
        batch_limit=config.batch_limit if config.batch_limit is not None else profile.batch_limit,
        budget_seconds=config.hours * 3600.0,
        param_budget=config.param_budget or profile.param_budget,
        policy=config.policy,
        axes=axes,
        hyperparameters=dict(profile.hyperparameters),
        checkpoint_every_n=profile.checkpoint_every_n,
        seed=config.seed,
        device=device,
        sweep_steps=config.sweep_steps if config.sweep_steps is not None else 5,
    )


def _print_experiment(spec: RunSpec, space) -> None:
    """Name the experiment being run and its search space, before any cell."""
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


def _format_hp(value: object) -> str:
    """Compact, readable rendering of one hyperparameter value."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int | float):
        return f"{value:.4g}"
    return str(value)


async def _run_loop(  # ruff: ignore[complex-structure, too-many-locals]
    spec: RunSpec,
    store: RecordStore,
    run_id: str,
    deadline: Deadline,
    backend,
    device: str,
    verbose: bool = False,
) -> int:
    """Run cells until deadline. Return records stored."""
    tasks = spec.task_names
    space = search_space_from_spec(spec, tasks=tasks)

    _print_experiment(spec, space)

    completed = {r.measurement_key for r in store.query_records(run_id=run_id)}

    # Use CellStream for proper paging through all candidates
    cell_stream = CellStream(
        spec=spec,
        space=space,
        shape=task_shape,
        deadline=deadline,
        is_measured=lambda key: key in completed,
    )

    count = 0
    while not deadline.soft_expired() and not cell_stream.is_exhausted:
        if _shutdown_requested[0]:
            if _shutdown_signum[0]:
                print(
                    f"\nSignal {_shutdown_signum[0]} received, requesting graceful shutdown...",
                    flush=True,
                )
            else:
                print("Shutdown requested, stopping...", flush=True)
            break

        # Get next batch of cells (up to 10 at a time)
        cells = cell_stream.next(10)
        if not cells:
            break

        for coord, sched in cells:
            if deadline.expired():
                print(
                    f"Hard deadline (with grace) reached, stopping after {count} cells",
                    flush=True,
                )
                return count

            key = coord.measurement_key(sched)
            if key in completed:
                continue

            # Show EVERY hyperparameter the cell actually uses: the swept
            # overrides plus each active knob's resolved value (prior/default).
            # Structural knobs (input_dim/output_dim) are task-derived, not
            # chosen, so they are excluded — showing their default of 1 would
            # misrepresent the shape the geometry actually builds.
            active = harvest_schema().active(coord)
            structural = {
                f"{s.axis_name}.{s.name}"
                for s in active.specs
                if s.axis_kind is AxisKind.STRUCTURAL
            }
            effective = {
                k: v
                for k, v in {**active.values, **coord.params}.items()
                if k not in structural
            }
            hp_items = ", ".join(
                f"{k}={_format_hp(v)}" for k, v in sorted(effective.items())
            )

            print(
                f"  Cell {count + 1}: substrate={coord.substrate} geometry={coord.geometry} "
                f"dynamics={coord.dynamics} credit={coord.credit} update={coord.update} "
                f"plasticity={coord.plasticity} (seed={sched.seed})",
                flush=True,
            )
            print(f"      hp: {hp_items or '[none]'}", flush=True)

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
            try:  # ruff: ignore[too-many-statements-in-try-clause]
                records = await backend.submit(coord, sched, prov, params, store)
                for r in records:
                    store.append(r)
                    completed.add(r.measurement_key)
                    cell_stream.add_rejected_key(r.measurement_key)
                    # Print results for this cell
                    m = r.payload
                    acc = m.get("val_acc", 0.0)
                    loss = m.get("val_loss", 0.0)
                    time_s = m.get("walltime_s", 0.0)
                    params = m.get("param_count", 0)
                    spectral = m.get("spectral_radius", 0.0)
                    lyap = m.get("lyapunov_exponent", 0.0)
                    verdict = r.status.gate_verdict.value
                    if verbose:
                        print(
                            f"    → {verdict} | val_acc={acc:.4f} val_loss={loss:.4f} "
                            f"walltime={time_s:.2f}s params={params} "
                            f"ρ={spectral:.4f} λ={lyap:.4f}",
                            flush=True,
                        )
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
        verbose=args.verbose,
        fidelity=args.fidelity,
        batch_limit=args.batch_limit,
        sweep_steps=args.sweep_steps,
    )


def _print_dry_run(spec: RunSpec) -> None:
    print(
        f"DRY RUN: profile={spec.profile} budget={spec.budget_seconds:.1f}s", flush=True
    )
    print(f"  task={spec.task} policy={spec.policy} epochs={spec.epochs}", flush=True)


def _run_experiment(
    config: Config, device: str, spec: RunSpec
) -> tuple[str, float, int, bool]:
    """Run experiment. Returns (run_id, elapsed, n_cells, was_interrupted)."""
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
        interrupted = False
        try:
            n = asyncio.run(_run_loop(spec, store, run_id, deadline, backend, device, config.verbose))
        except Exception as e:
            print(f"Experiment crashed: {e}", flush=True)
            traceback.print_exc()
            store.finish_run(run_id, "crashed", budget_consumed_s=time.time() - start)
            raise
        elapsed = time.time() - start

        # Check if we were interrupted by signal
        if _shutdown_requested[0]:
            interrupted = True
            print("Run interrupted by signal, marking as interrupted", flush=True)
            store.finish_run(run_id, "interrupted", budget_consumed_s=elapsed)
        else:
            store.finish_run(run_id, "completed", budget_consumed_s=elapsed)

    return run_id, elapsed, n, interrupted


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
        html_config = ReportConfig(output_dir=str(report_path.parent))
        generate_html_report(store, run_id, html_config)
        print(f"HTML report:      {report_path}", flush=True)

        # Also generate JSON report
        json_path = Path(config.store).with_suffix(".json")
        json_config = JSONReportConfig(output_dir=str(json_path.parent))
        generate_json_report(store, run_id, json_config)
        print(f"JSON report:      {json_path}", flush=True)

    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal time-boxed experiment runner")
    parser.add_argument("--hours", type=float, required=True)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--store", default="results/experiment.db")
    parser.add_argument("--policy", default="model_based")
    parser.add_argument("--verbose", action="store_true", help="Show detailed per-cell results")
    parser.add_argument("--profile", default="production-map")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--n-seeds", type=int, default=None)
    parser.add_argument("--param-budget", type=int, default=None)
    parser.add_argument("--fidelity", choices=["L0", "L1", "L2"], default=None)
    parser.add_argument("--batch-limit", type=int, default=None)
    parser.add_argument("--sweep-steps", type=int, default=None, help="Number of diagonal steps through hyperparameter space")
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
        run_id, elapsed, n, interrupted = _run_experiment(config, device, spec)
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

    # On interrupt, still generate report but skip budget window check
    if not interrupted:
        _check_budget(budget, elapsed)
    else:
        print("⚠️  Run was interrupted; skipping budget window check", flush=True)

    _generate_report(config, run_id)

    return 0


if __name__ == "__main__":
    sys.exit(main())
