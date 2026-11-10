"""SimpleSurvey: Minimal adaptive experiment system.

Replaces the complex multi-stage pipeline with a single parallel evaluation script.
Adaptivity comes from offline importance sampling using prior runs, not online policy.
"""

from __future__ import annotations

# Disable CUDA before ANY torch import if --device cpu is in argv
# Must run before any module that imports torch at module level
import os
import sys

if "--device" in sys.argv:
    try:
        idx = sys.argv.index("--device")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1] == "cpu":
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
    except ValueError, IndexError:
        pass

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from computronium.core.logging import get_logger
from computronium.core.utils.device import get_device
from computronium.domains._task_registry import get_fidelity_tasks
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Schedule,
)
from computronium.experiment.schema.run_spec import Fidelity, RunSpec

# Import shared wave functionality
from computronium.experiment.wave import (
    CostModel,
    StaticPlanner,
    _axis_overrides,
    _build_spec,
    _default_store_path,
    _estimate_cell_count,
    _format_error,
    _load_cost_model,
    _measure_cost_model,
    _pretty_print_dry_run,
    _run_self_test,
    _SpecParams,
    run_waves,
)

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class SimpleSurveyResult:
    """Result of a SimpleSurvey run."""

    run_id: str
    store_path: str
    cells_evaluated: int
    cells_passed: int
    cells_failed: int
    walltime_s: float


def _generate_cells(
    spec: RunSpec,
    fidelity: str,
    tasks: Sequence[str],
    seed: int,
    promote_from: str | None,
    promote_top: int,
    model: CostModel,
    resume_from: str | None = None,
) -> list[tuple[Coordinate, Schedule]]:
    """Generate cells for the survey."""
    search_space = search_space_from_spec(spec, tasks=tasks)

    import random

    random.seed(seed)
    budget_seconds = int(spec.budget_seconds or 0)
    n_cells = _estimate_cell_count(budget_seconds, model)

    logger.info(
        "Budget %ds -> ~%d cells (%.1fs/cell %s, %.0fs startup)",
        budget_seconds,
        n_cells,
        model.cost_per_cell_s,
        model.source,
        model.startup_s,
    )

    planner = StaticPlanner(
        spec=spec,
        fidelity=fidelity,
        tasks=tasks,
        seed=seed,
        search_space=search_space,
        promote_from=promote_from,
        promote_top=promote_top,
        resume_from=resume_from,
    )

    cells = planner.propose(n_cells, seen=set())

    logger.info("Generated %d valid cells", len(cells))
    return cells


def run_simple_survey(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] - experiment config requires many parameters
    hours: float,
    fidelity: Fidelity = "L0",
    tasks: Sequence[str] | None = None,
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
    verbose: bool = False,
    cpu_threads: int = 1,
    resume: bool = False,
    ladder: bool = False,
    policy: str = "tpe",
) -> dict[str, Any]:
    """Run a SimpleSurvey experiment.

    Args:
        hours: Time budget in hours; evaluation stops when it is spent.
        fidelity: Fidelity level (L0, L1, L2).
        tasks: Task names to use (defaults to fidelity-appropriate tasks).
        store_path: Path to DuckDB store.
        promote_from: Path to prior store for importance sampling.
        promote_top: Number of top cells to promote from prior run.
        seed: Random seed.
        dry_run: If True, only generate cells and return them without evaluation.
        device: Device to run on.
        param_budget: Parameter budget ceiling.
        n_seeds: Number of seeds per cell.
        epochs: Number of epochs.
        batch_limit: Batch limit (0 for full dataset).
        axes: Axis selections (axis -> primitives).
        hyperparameters: Hyperparameter domains.
        objectives: Objective names.
        verbose: Verbose progress output.
        cpu_threads: Torch threads (1 avoids CPU oversubscription).
        resume: If True, skip cells already measured in store_path.

    Returns:
        If dry_run: {"cells": list[(coord, schedule)], "n": int, "tasks": list[str],
        "model": CostModel}
        If evaluation: {"run_id": str, "store_path": str, "cells_evaluated": int, ...}
    """

    # Resolve device string for CUDA control
    device_obj = get_device(device)
    device_str = device_obj.type

    # 1. Determine tasks to use, then build the RunSpec from them so the
    # spec's own task cycle is non-empty.
    if tasks is None:
        tasks = get_fidelity_tasks(fidelity)

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
    )
    spec = _build_spec(params)
    budget_seconds = int(spec.budget_seconds or 0)

    model = _load_cost_model(device_str, fidelity)

    # 3. Generate cells. Only the dry run previews here: proposing also marks
    # the cells seen, so a preview before a real run would leave the wave loop
    # with nothing new to plan.
    if dry_run:
        search_space = search_space_from_spec(spec, tasks=tasks)
        planner = StaticPlanner(
            spec=spec,
            fidelity=fidelity,
            tasks=tasks,
            seed=seed,
            search_space=search_space,
            promote_from=promote_from,
            promote_top=promote_top,
            resume_from=store_path if resume else None,
        )
        cells = planner.propose(_estimate_cell_count(budget_seconds, model), seen=set())
        return {
            "cells": cells,
            "n": len(cells),
            "tasks": list(tasks),
            "fidelity": fidelity,
            "model": model,
        }

    planner = StaticPlanner(
        spec=spec,
        fidelity=fidelity,
        tasks=tasks,
        seed=seed,
        search_space=search_space_from_spec(spec, tasks=tasks),
        promote_from=promote_from,
        promote_top=promote_top,
        resume_from=store_path if resume else None,
    )

    # 4. Run waves via shared executor
    summary = run_waves(
        spec=spec,
        planner=planner,
        budget_seconds=budget_seconds,
        store_path=store_path,
        fidelity=fidelity,
        verbose=verbose,
        cpu_threads=cpu_threads,
        device_str=device_str,
        dry_run=False,
    )

    # 5. Update the cost cache from the cells that actually finished
    if summary.cells_evaluated > 0:
        from computronium.experiment.evidence.store import RecordStore
        from computronium.experiment.evidence.store._models import StoreConfig

        with RecordStore(StoreConfig(path=Path(store_path))) as store:
            measured_records = store.query_records(run_id=summary.run_id)
        _measure_cost_model(device_str, fidelity, store_path, measured_records, model)

    return {
        "run_id": summary.run_id,
        "store_path": summary.store_path,
        "cells_evaluated": summary.cells_evaluated,
        "cells_passed": summary.cells_passed,
        "cells_failed": summary.cells_failed,
        "cells_skipped": summary.cells_skipped,
        "walltime_s": summary.walltime_s,
        "report": summary.report,
    }


def main() -> None:  # ruff: ignore[too-many-statements, too-many-locals, too-many-branches, complex-structure] - CLI entry point handles many arguments
    """CLI entry point for simple_survey."""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    parser = argparse.ArgumentParser(
        description="SimpleSurvey - Minimal adaptive experiment system"
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
        "--cpu-threads",
        type=int,
        default=1,
        help="Torch threads (default 1)",
    )
    parser.add_argument(
        "--store",
        default=None,
        help="DuckDB store path (default: experiments/experiment_YYYYMMDD_HHMMSS.duckdb)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing store, skip measured cells",
    )
    parser.add_argument(
        "--ladder",
        action="store_true",
        help="Run fidelity ladder L0→L1→L2 (learning mode only)",
    )
    parser.add_argument(
        "--policy",
        default="tpe",
        choices=["tpe", "nsga2", "random"],
        help="Sampler policy (learning mode only)",
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

    args = parser.parse_args()

    if args.doctor:
        from computronium.experiment.environment.diagnostics import (
            print_diagnostics,
            run_diagnostics,
        )

        result = run_diagnostics(device="cpu", hours=0.001)
        print_diagnostics(result)
        sys.exit(0 if result.errors == [] else 1)

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

    tasks = args.tasks.split(",") if args.tasks else None
    axes = _axis_overrides(args.axes, digital=args.digital)
    hyperparameters = json.loads(args.hyperparameters) if args.hyperparameters else None
    objectives = tuple(args.objectives.split(",")) if args.objectives else ()

    # ruff: ignore[too-many-statements-in-try-clause] - CLI entry point, single try for all execution paths
    try:
        result = run_simple_survey(
            hours=args.hours,
            fidelity=args.fidelity,
            tasks=tasks,
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
                _pretty_print_dry_run(
                    result,
                    hours=args.hours,
                    fidelity=args.fidelity,
                    model=result["model"],
                )
            else:  # summary
                n = result.get("n", 0)
                tasks_str = ", ".join(result.get("tasks", []))
                model: CostModel = result["model"]
                total_est = model.startup_s + n * model.cost_per_cell_s
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
        # Friendly error handling
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
