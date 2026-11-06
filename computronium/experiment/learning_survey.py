"""LearningSurvey: Adaptive experiment system with policy-driven exploration.

Reuses SimpleSurvey's spec builder, evaluator, wave executor, store schema and report.
Replaces the static planner with propose → measure → observe using ModelBasedPolicy.
"""

from __future__ import annotations

# Disable CUDA before ANY torch import if --device cpu is in argv
import os
import sys

import torch

if "--device" in sys.argv:
    try:
        idx = sys.argv.index("--device")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "cpu":
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
    except ValueError, IndexError:
        pass

import argparse
import json
import random
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Sequence

if TYPE_CHECKING:
    from collections.abc import Sequence

from computronium.core.logging import get_logger
from computronium.core.utils.device import get_device
from computronium.domains._task_registry import get_fidelity_tasks
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.evidence.store._models import StoreConfig
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate, DataOrigin, Schedule
from computronium.experiment.schema.record import GateVerdict
from computronium.experiment.schema.run_spec import RunSpec
from computronium.ontology.system import check_compatibility_matrix

# Import shared wave functionality
from computronium.experiment.wave import (
    CostModel,
    PolicyPlanner,
    StaticPlanner,
    _axis_overrides,
    _build_provenance,
    _build_spec,
    _default_store_path,
    _estimate_cell_count,
    _format_error,
    _load_cost_model,
    _pretty_print_dry_run,
    _resolve_max_workers,
    _run_self_test,
    _save_cost_model,
    _SpecParams,
    run_waves,
)

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class LearningSurveyResult:
    """Result of a LearningSurvey run."""

    run_id: str
    store_path: str
    cells_evaluated: int
    cells_passed: int
    cells_failed: int
    walltime_s: float
    report: dict
    waves_completed: int
    budget_split: dict[str, float]  # fidelity -> fraction of walltime


# Wave sizing bounds
MIN_WAVE = 1
MAX_WAVE = 64


def run_learning_survey(  # ruff: ignore[too-many-branches, too-many-arguments, too-many-locals, too-many-statements] - experiment orchestration inherently complex
    hours: float,
    fidelity: str = "L0",
    tasks: Sequence[str] | None = None,
    max_workers: int | str = "auto",
    store_path: str = "experiment.duckdb",
    promote_from: str | None = None,
    promote_top: int = 20,
    seed: int = 42,
    dry_run: bool = False,
    device: str = "auto",
    param_budget: int = 0,
    n_seeds: int = 1,
    epochs: int = 1,
    batch_limit: int = 0,
    axes: dict[str, tuple[str, ...]] | None = None,
    hyperparameters: dict[str, Any] | None = None,
    objectives: tuple[str, ...] = (),
    axis_objectives: dict[str, tuple[str, ...]] | None = None,
    verbose: bool = False,
    cpu_threads: int = 1,
    resume: bool = False,
    ladder: bool = False,
    policy: str = "tpe",
) -> dict[str, Any]:
    """Run a LearningSurvey experiment.

    Args:
        hours: Time budget in hours; evaluation stops when it is spent.
        fidelity: Fidelity level (L0, L1, L2). Used as starting fidelity if ladder=True.
        tasks: Task names to use (defaults to fidelity-appropriate tasks).
        max_workers: Number of parallel workers, or ``"auto"``.
        store_path: Path to DuckDB store.
        promote_from: Path to prior store for warm-start (learning mode) or importance sampling.
        promote_top: Number of top cells to promote from prior run.
        seed: Random seed.
        dry_run: If True, only generate wave-0 cells and return them without evaluation.
        device: Device to run on.
        param_budget: Parameter budget ceiling.
        n_seeds: Number of seeds per cell (1 = use fidelity ladder).
        epochs: Number of epochs (1 = use fidelity ladder).
        batch_limit: Batch limit (0 for full dataset).
        axes: Axis selections (axis -> primitives).
        hyperparameters: Hyperparameter domains.
        objectives: Objective names.
        axis_objectives: Axis-aligned objectives for multi-objective optimization (e.g., NSGA-II).
        verbose: Verbose progress output.
        cpu_threads: Torch threads per worker (1 avoids CPU oversubscription).
        resume: If True, warm-start policy from store_path records.
        ladder: If True, run L0→L1→L2 promotion in one invocation.
        policy: Sampler policy: "tpe", "nsga2", or "random".

    Returns:
        If dry_run: {"cells": list[(coord, schedule)], "n": int, "tasks": list[str],
        "model": CostModel, "workers": int, "wave": 0}
        If evaluation: {"run_id": str, "store_path": str, "cells_evaluated": int, ...}
    """

    # Resolve device string for worker init and CUDA control
    device_obj = get_device(device)
    device_str = device_obj.type

    # 1. Build RunSpec
    params = _SpecParams(
        hours=hours,
        fidelity=fidelity,
        tasks=tasks,
        seed=seed,
        device=device,
        param_budget=param_budget,
        n_seeds=n_seeds,
        epochs=epochs,
        batch_limit=batch_limit,
        axes=axes,
        hyperparameters=hyperparameters,
        objectives=objectives,
        axis_objectives=axis_objectives,
    )
    spec = _build_spec(params)

    # 2. Determine tasks to use
    if tasks is None:
        tasks = get_fidelity_tasks(fidelity)

    workers = _resolve_max_workers(max_workers, device_obj)
    model = _load_cost_model(device_str, fidelity, workers)

    # 3. Create search space
    search_space = search_space_from_spec(spec, tasks=tasks)

    # 4. Create planner
    # Warm-start from --promote-from (takes precedence over --resume for learning mode)
    warm_start_path = promote_from if promote_from else (store_path if resume else None)
    if ladder:
        # Ladder mode: start at L0, promote to L1, then L2
        logger.info(
            "Ladder mode enabled: will promote L0→L1→L2"
        )
        planner: Any = PolicyPlanner(
            spec=spec,
            fidelity=fidelity,
            tasks=tasks,
            seed=seed,
            search_space=search_space,
            policy=policy,
            n_startup_trials=10,  # More startup trials for ladder
            resume_from=warm_start_path,
            promote_top=promote_top,
        )
    else:
        planner = PolicyPlanner(
            spec=spec,
            fidelity=fidelity,
            tasks=tasks,
            seed=seed,
            search_space=search_space,
            policy=policy,
            resume_from=warm_start_path,
            promote_top=promote_top,
        )

    # 5. Generate initial wave (wave 0 = startup trials) for dry-run preview
    n_startup = getattr(planner._policy, "n_startup_trials", 3)
    startup_cells = planner.propose(n_startup * workers, seen=set())

    if dry_run:
        result = {
            "cells": startup_cells,
            "n": len(startup_cells),
            "tasks": list(tasks),
            "fidelity": fidelity,
            "model": model,
            "workers": workers,
            "wave": 0,
        }
        if ladder:
            result["budget_split"] = {"L0": 0.6, "L1": 0.3, "L2": 0.1}
            result["ladder"] = True
        return result

    # 6. Run waves via shared executor
    summary = run_waves(
        spec=spec,
        planner=planner,
        budget_seconds=spec.budget_seconds,
        workers=workers,
        store_path=store_path,
        fidelity=fidelity,
        verbose=verbose,
        cpu_threads=cpu_threads,
        device_str=device_str,
        dry_run=False,
        ladder=ladder,
    )

    # 7. Update cost model with measured costs
    if summary.cells_evaluated > 0:
        from computronium.experiment.evidence.store import RecordStore
        from computronium.experiment.evidence.store._models import StoreConfig

        store_config = StoreConfig(path=Path(store_path))
        with RecordStore(store_config) as store:
            records = store.query_records()

        from collections import defaultdict

        task_times: defaultdict[str, list[float]] = defaultdict(list)
        for r in records:
            task_id = r.payload.get("task_id")
            walltime = r.payload.get("walltime_s")
            if task_id and walltime:
                task_times[task_id].append(float(walltime))

        per_task = {}
        for task_id, times in task_times.items():
            if times:
                per_task[task_id] = sum(times) / len(times)

        measured = CostModel(
            cost_per_cell_s=max(0.01, summary.walltime_s * workers / summary.cells_evaluated),
            startup_s=0.0,
            measured=True,
            workers=workers,
            per_task=per_task,
        )
        logger.info(
            "Measured: %.1fs/cell, %.0fs startup (prior: %.1fs/cell)",
            measured.cost_per_cell_s,
            measured.startup_s,
            model.cost_per_cell_s,
        )
        _save_cost_model(device_str, fidelity, measured)

    return {
        "run_id": summary.run_id,
        "store_path": summary.store_path,
        "cells_evaluated": summary.cells_evaluated,
        "cells_passed": summary.cells_passed,
        "cells_failed": summary.cells_failed,
        "cells_skipped": summary.cells_skipped,
        "walltime_s": summary.walltime_s,
        "report": summary.report,
        "waves_completed": summary.waves_completed,
        "budget_split": summary.budget_split,
    }


def main() -> None:  # ruff: ignore[too-many-statements, too-many-locals, too-many-branches, complex-structure]
    """CLI entry point for learning_survey."""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    parser = argparse.ArgumentParser(
        description="LearningSurvey - Adaptive experiment system with policy-driven exploration"
    )
    parser.add_argument(
        "hours",
        type=float,
        nargs="?",
        help="Time budget in hours (required unless --doctor)",
    )
    parser.add_argument("--fidelity", default="L0", choices=["L0", "L1", "L2"])
    parser.add_argument(
        "--tasks", default="", help="Comma-separated task names (default: auto)"
    )
    parser.add_argument(
        "--max-workers", default="auto", help="Max workers (int or 'auto')"
    )
    parser.add_argument(
        "--cpu-threads",
        type=int,
        default=1,
        help="Torch threads per worker (default 1)",
    )
    parser.add_argument(
        "--store",
        default=None,
        help="DuckDB store path (default: experiments/experiment_YYYYMMDD_HHMMSS.duckdb)",
    )
    parser.add_argument("--promote-from", default=None)
    parser.add_argument("--promote-top", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--dry-run-format",
        choices=["json", "table", "summary"],
        default="table",
        help="Dry-run output format",
    )
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--param-budget", type=int, default=0)
    parser.add_argument("--n-seeds", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-limit", type=int, default=0)
    parser.add_argument("--axes", default="", help="JSON: axis -> [primitives]")
    parser.add_argument(
        "--digital", action="store_true", help="Restrict to digital substrate only"
    )
    parser.add_argument("--hyperparameters", default="", help="JSON: hyperparameters")
    parser.add_argument("--objectives", default="", help="Comma-separated objectives")
    parser.add_argument("--axis-objectives", default="", help="JSON: axis -> [objectives]")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose progress output"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run environment self-test before experiment",
    )
    parser.add_argument(
        "--no-self-test",
        action="store_true",
        help="Deprecated: use --self-test to enable instead",
    )
    parser.add_argument(
        "--doctor", action="store_true", help="Run environment diagnostics and exit"
    )
    parser.add_argument(
        "--resume", action="store_true", help="Warm-start policy from existing store"
    )
    parser.add_argument(
        "--ladder", action="store_true", help="Run L0→L1→L2 fidelity ladder"
    )
    parser.add_argument(
        "--policy",
        default="tpe",
        choices=["tpe", "nsga2", "random"],
        help="Sampler policy (default: tpe)",
    )

    args = parser.parse_args()

    if args.doctor:
        from computronium.experiment.environment.diagnostics import (
            print_diagnostics,
            run_diagnostics,
        )

        result = run_diagnostics(device="cpu", hours=0.001)
        print_diagnostics(result)
        sys.exit(0)

    if args.hours is None:
        parser.error("hours argument required (unless using --doctor)")

    # Handle self-test flags
    run_self_test = args.self_test
    if args.no_self_test and not args.self_test:
        logger.warning(
            "--no-self-test is deprecated; self-test is now opt-in with --self-test"
        )
    elif args.no_self_test and args.self_test:
        parser.error("Cannot use both --self-test and --no-self-test")

    # Resolve device early (before self-test) to avoid CUDA probe in CPU mode
    try:
        device = get_device(args.device)
        device_str = device.type
    except Exception as e:
        print(_format_error(f"Failed to resolve device: {e}", "Try --device cpu"))
        sys.exit(1)

    # Disable CUDA visibility for cpu mode BEFORE any torch.cuda access
    if device_str == "cpu":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    # Run self-test if requested
    if run_self_test:
        logger.info("Running self-test...")
        try:
            if not _run_self_test(device_str):
                print(
                    _format_error(
                        "Self-test failed",
                        "Run with --device cpu to skip CUDA checks, or fix the reported issue",
                    )
                )
                sys.exit(1)
        except Exception:
            logger.exception("Self-test CRASHED")
            import traceback

            traceback.print_exc()
            print(_format_error("Self-test crashed", "See traceback above for details"))
            sys.exit(1)
        logger.info("Self-test passed")

    # Determine verbosity: default to True for TTY unless --quiet
    verbose = args.verbose or (not args.quiet and sys.stdout.isatty())

    # Resolve store path
    store_path = args.store or _default_store_path()

    # Resolve max_workers
    max_workers = _resolve_max_workers(args.max_workers, device)

    tasks = args.tasks.split(",") if args.tasks else None
    axes = _axis_overrides(args.axes, digital=args.digital)
    hyperparameters = json.loads(args.hyperparameters) if args.hyperparameters else None
    objectives = tuple(args.objectives.split(",")) if args.objectives else ()
    axis_objectives = json.loads(args.axis_objectives) if args.axis_objectives else None

    try:  # ruff: ignore[too-many-nested-blocks] - main entry point try block is inherently complex
        result = run_learning_survey(
            hours=args.hours,
            fidelity=args.fidelity,
            tasks=tasks,
            max_workers=max_workers,
            store_path=store_path,
            promote_from=args.promote_from,
            promote_top=args.promote_top,
            seed=args.seed,
            dry_run=args.dry_run,
            device=device_str,
            param_budget=args.param_budget,
            n_seeds=args.n_seeds,
            epochs=args.epochs,
            batch_limit=args.batch_limit,
            axes=axes,
            hyperparameters=hyperparameters,
            objectives=objectives,
            axis_objectives=axis_objectives,
            verbose=verbose,
            cpu_threads=args.cpu_threads,
            resume=args.resume,
            ladder=args.ladder,
            policy=args.policy,
        )

        if args.dry_run:
            if args.dry_run_format == "json":
                print(json.dumps(result, default=str, indent=2))
            elif args.dry_run_format == "table":
                if result.get("ladder"):
                    # Ladder dry-run: show budget split per fidelity
                    budget_split = result.get("budget_split", {})
                    ladder_seeds = {"L0": 1, "L1": 3, "L2": 5}
                    ladder_epochs = {"L0": 1, "L1": 5, "L2": 20}
                    print("\n=== LearningSurvey Ladder Dry-Run ===")
                    print(
                        f"Budget: {args.hours}h ({int(args.hours * 3600)}s) | "
                        f"Starting Fidelity: {args.fidelity} | Tasks: {', '.join(result.get('tasks', []))}"
                    )
                    print(f"Ladder budget split: L0={budget_split.get('L0', 0.6)*100:.0f}% "
                          f"L1={budget_split.get('L1', 0.3)*100:.0f}% "
                          f"L2={budget_split.get('L2', 0.1)*100:.0f}%")
                    print(f"Estimated cells: {result.get('n', 0)} across {result.get('workers', 0)} workers")
                    print()
                    cells = result.get("cells", [])
                    for fid in ["L0", "L1", "L2"]:
                        fid_count = int(result.get("n", 0) * budget_split.get(fid, 0))
                        print(f"--- {fid} ({fid_count} cells, n_seeds={ladder_seeds[fid]}, epochs={ladder_epochs[fid]}) ---")
                        for i, (coord, _schedule) in enumerate(cells[:5], 1):
                            print(
                                f"  {i}  {coord.substrate:<15} {coord.geometry:<15} {coord.dynamics:<20} "
                                f"{coord.plasticity:<15} {coord.credit:<20} {coord.update:<15}"
                            )
                        if fid_count > 5:
                            print(f"  ... {fid_count - 5} more cells")
                        print()
                else:
                    _pretty_print_dry_run(
                        result,
                        hours=args.hours,
                        fidelity=args.fidelity,
                        model=result["model"],
                        workers=result["workers"],
                    )
            else:  # summary
                n = result.get("n", 0)
                tasks_str = ", ".join(result.get("tasks", []))
                model: CostModel = result["model"]
                total_est = model.startup_s + n * model.cost_per_cell_s / max(
                    1, result["workers"]
                )
                if result.get("ladder"):
                    budget_split = result.get("budget_split", {})
                    print(
                        f"Dry-run (ladder): {n} cells | L0/L1/L2 | {tasks_str} | "
                        f"split: L0={budget_split.get('L0',0.6)*100:.0f}% "
                        f"L1={budget_split.get('L1',0.3)*100:.0f}% "
                        f"L2={budget_split.get('L2',0.1)*100:.0f}% | "
                        f"~{model.cost_per_cell_s:.1f}s/cell ({model.source}) | "
                        f"~{total_est:.0f}s total"
                    )
                else:
                    print(
                        f"Dry-run: {n} cells | {args.fidelity} | {tasks_str} | "
                        f"~{model.cost_per_cell_s:.1f}s/cell ({model.source}) | "
                        f"~{total_est:.0f}s total"
                    )
        else:
            print(json.dumps(result, default=str, indent=2))

    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as e:
        error_msg = str(e)
        hint = None

        if "CUDA" in error_msg or "cuda" in error_msg.lower():
            hint = "Try --device cpu or export CUDA_VISIBLE_DEVICES=''"
        elif "search space" in error_msg.lower() or "no cells" in error_msg.lower():
            hint = "Try --fidelity L0 --device cpu, or check --axes constraints"
        elif "import" in error_msg.lower() or "module" in error_msg.lower():
            hint = "Run: uv sync --dev --all-extras"
        elif "permission" in error_msg.lower():
            hint = "Check file permissions for store path"
        elif "no space" in error_msg.lower() or "disk" in error_msg.lower():
            hint = "Free up disk space or use --store with a different path"

        print(_format_error(error_msg, hint))
        if verbose:
            logger.exception("Full traceback:")
        sys.exit(1)


if __name__ == "__main__":
    main()