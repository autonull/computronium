"""LearningSurvey: Adaptive experiment system with policy-driven exploration.

Reuses SimpleSurvey's spec builder, evaluator, wave executor, store schema and report.
Replaces the static planner with propose → measure → observe using ModelBasedPolicy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.core.logging import get_logger
from computronium.core.utils.device import get_device
from computronium.domains._task_registry import get_fidelity_tasks
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.simple_survey import _unavailable_declarations

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium.experiment.schema.run_spec import Fidelity

# Import shared wave functionality
from computronium.experiment.wave import (
    PolicyPlanner,
    _build_spec,
    _load_cost_model,
    _measure_cost_model,
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


def run_learning_survey(  # ruff: ignore[too-many-branches, too-many-arguments, too-many-locals, too-many-statements, too-many-positional-arguments] - experiment orchestration inherently complex
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
    n_seeds: int | None = None,
    epochs: int | None = None,
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
    max_workers: int = 1,
    log_steps: int = 0,
) -> dict[str, Any]:
    """Run a LearningSurvey experiment.

    Args:
        hours: Time budget in hours; evaluation stops when it is spent.
        fidelity: Fidelity level (L0, L1, L2). Used as starting fidelity if ladder=True.
        tasks: Task names to use (defaults to fidelity-appropriate tasks).
        store_path: Path to DuckDB store.
        promote_from: Path to prior store for warm-start (learning mode) or importance sampling.
        promote_top: Number of top cells to promote from prior run.
        seed: Random seed.
        dry_run: If True, only generate wave-0 cells and return them without evaluation.
        device: Device to run on.
        param_budget: Parameter budget ceiling.
        n_seeds: Seeds per cell; ``None`` follows the fidelity ladder.
        epochs: Epochs per cell; ``None`` follows the fidelity ladder.
        batch_limit: Batch limit (0 for full dataset).
        axes: Axis selections (axis -> primitives).
        hyperparameters: Hyperparameter domains.
        objectives: Objective names.
        axis_objectives: Axis-aligned objectives for multi-objective optimization (e.g., NSGA-II).
        verbose: Verbose progress output.
        cpu_threads: Torch threads (1 avoids CPU oversubscription).
        resume: If True, warm-start policy from store_path records.
        ladder: If True, run L0→L1→L2 promotion in one invocation.
        policy: Sampler policy: "tpe", "nsga2", or "random".
        max_workers: Cells evaluated concurrently within a wave (1 = serial).
        log_steps: Trainer steps between progress logs (0 = epoch only).

    Returns:
        If dry_run: {"cells": list[(coord, schedule)], "n": int, "tasks": list[str],
        "model": CostModel, "wave": 0}
        If evaluation: {"run_id": str, "store_path": str, "cells_evaluated": int, ...}
    """

    # Resolve device string for CUDA control
    device_obj = get_device(device)
    device_str = device_obj.type

    # 1. Determine tasks to use (must be before spec building for task_cycle)
    if tasks is None:
        tasks = get_fidelity_tasks(fidelity)

    # 2. Build RunSpec
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
    budget_seconds = int(spec.budget_seconds or 0)

    model = _load_cost_model(device_str, fidelity)

    # 3. Create search space
    search_space = search_space_from_spec(spec, tasks=tasks)

    # 4. Create planner
    # Warm-start from --promote-from (takes precedence over --resume for learning mode)
    warm_start_path = promote_from if promote_from else (store_path if resume else None)
    if ladder:
        # Ladder mode: start at L0, promote to L1, then L2
        logger.info("Ladder mode enabled: will promote L0→L1→L2")
        planner: Any = PolicyPlanner(
            spec=spec,
            fidelity=fidelity,
            tasks=tasks,
            seed=seed,
            search_space=search_space,
            policy=policy,
            n_startup_trials=10,  # More startup trials for ladder
            min_samples_per_combo=3,
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
            min_samples_per_combo=3,
            resume_from=warm_start_path,
            promote_top=promote_top,
        )

    # 5. Propose the startup wave for the dry-run preview only. Proposing also
    # marks the cells seen, so previewing before a real run would rob the wave
    # loop of the very cells it should measure.
    if dry_run:
        n_startup = getattr(planner._policy, "n_startup_trials", 3)
        startup_cells = planner.propose(n_startup, seen=set())
        result = {
            "cells": startup_cells,
            "n": len(startup_cells),
            "tasks": list(tasks),
            "fidelity": fidelity,
            "model": model,
            "wave": 0,
            "unavailable": _unavailable_declarations(spec),
        }
        if ladder:
            result["budget_split"] = {"L0": 0.6, "L1": 0.3, "L2": 0.1}
            result["ladder"] = True
        return result

    # 6. Run waves via shared executor
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
        ladder=ladder,
        max_workers=max_workers,
        log_steps=log_steps,
    )

    # 7. Update the cost cache from the cells that actually finished
    if summary.cells_evaluated > 0:
        from computronium.experiment.evidence.store import RecordStore
        from computronium.experiment.evidence.store._models import StoreConfig

        with RecordStore(StoreConfig(path=Path(store_path))) as store:
            measured_records = store.query_records(run_id=summary.run_id)
        _save_cost_model(
            device_str,
            fidelity,
            _measure_cost_model(
                device_str, fidelity, store_path, measured_records, model
            ),
        )

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
