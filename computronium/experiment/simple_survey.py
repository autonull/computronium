"""SimpleSurvey: Minimal adaptive experiment system.

Replaces the complex multi-stage pipeline with a single parallel evaluation script.
Adaptivity comes from offline importance sampling using prior runs, not online policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.core.logging import get_logger
from computronium.core.utils.device import get_device
from computronium.domains._task_registry import get_fidelity_tasks
from computronium.experiment.kernel.search_space import search_space_from_spec

if TYPE_CHECKING:
    from collections.abc import Sequence

    from computronium.experiment.schema.coordinate import Coordinate, Schedule
    from computronium.experiment.schema.run_spec import Fidelity, RunSpec

# Import shared wave functionality
from computronium.experiment.wave import (
    CostModel,
    StaticPlanner,
    _build_spec,
    _estimate_cell_count,
    _load_cost_model,
    _measure_cost_model,
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
    n_seeds: int | None = None,
    epochs: int | None = None,
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
        n_seeds: Seeds per cell; ``None`` follows the fidelity ladder.
        epochs: Epochs per cell; ``None`` follows the fidelity ladder.
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
