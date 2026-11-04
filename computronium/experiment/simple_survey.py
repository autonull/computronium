"""SimpleSurvey: Minimal adaptive experiment system.

Replaces the complex multi-stage pipeline with a single parallel evaluation script.
Adaptivity comes from offline importance sampling using prior runs, not online policy.
"""

from __future__ import annotations

import concurrent.futures
import json
import random
import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.core.logging import get_logger
from computronium.domains._task_registry import get_fidelity_tasks
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.evidence.store._models import StoreConfig
from computronium.experiment.execution.pipeline._budget_constants import (
    estimate_cell_counts,
)
from computronium.experiment.kernel.evaluate import (
    cell_record,
    task_shape,
)
from computronium.experiment.kernel.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.run_spec import RunSpec
from computronium.ontology.system import check_compatibility_matrix

if TYPE_CHECKING:
    from collections.abc import Sequence
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.record import Record

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


def _schedule_from_spec(spec: RunSpec, task: str, fidelity: str) -> Schedule:
    """Create a Schedule from a RunSpec for a given task and fidelity."""
    # Get fidelity-specific settings
    fidelity_seeds = spec.fidelity_seeds or {}
    fidelity_epochs = spec.fidelity_epochs or {}

    return Schedule(
        fidelity=fidelity,
        seed=spec.seed,
        n_seeds=fidelity_seeds.get(fidelity, spec.n_seeds),
        epochs=fidelity_epochs.get(fidelity, spec.epochs),
        batch_limit=spec.batch_limit,
        budget_id=f"{fidelity}_initial",
        task_id=task,
        param_budget=spec.param_budget,
        device=spec.device,
        deterministic=spec.deterministic,
        num_workers=spec.num_workers,
        precision=spec.precision,
        checkpoint_every_n=spec.checkpoint_every_n,
        early_stopping_patience=spec.early_stopping_patience,
    )


def _build_provenance(spec: RunSpec, run_id: str) -> Provenance:
    """Build provenance metadata for records."""
    import os

    git_path = shutil.which("git")
    code_sha = "unknown"
    if git_path:
        try:
            code_sha = subprocess.check_output(
                [git_path, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
            ).strip()
        except Exception:
            try:
                code_sha = subprocess.check_output(
                    [git_path, "rev-parse", "--short", "HEAD"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()
            except Exception:
                pass

    # Use actual dataset from the first task
    dataset = spec.dataset if spec.dataset != "unknown" else "digits"
    dataset_version = spec.dataset_version if spec.dataset_version != "1.0" else "1.0"

    return Provenance(
        env={
            k: v
            for k, v in os.environ.items()
            if k.startswith(("CUDA", "TORCH", "OMP"))
        },
        dataset=dataset,
        dataset_version=dataset_version,
        code_sha=code_sha,
        policy="simple_survey",
        links={"run_id": run_id},
        data_origin=DataOrigin.EXPLORATION,
    )


def _generate_valid_cells(
    n: int,
    fidelity: str,
    tasks: Sequence[str],
    seed: int,
    spec: RunSpec,
    search_space,
    promote_from: str | None = None,
    promote_top: int = 20,
) -> list[tuple[Coordinate, Schedule]]:
    """Generate N valid cells with optional importance sampling from prior runs."""
    cells: list[tuple[Coordinate, Schedule]] = []

    # 1. Exploitation: bias toward prior winners (if prior run exists)
    if promote_from:
        try:
            prior_store = RecordStore(promote_from)
            top_coords = _get_top_coordinates(prior_store, fidelity, promote_top)
            if top_coords:
                cells.extend(
                    _mutate_around(
                        top_coords, n // 2, fidelity, tasks, spec, search_space
                    )
                )
        except Exception as exc:
            logger.debug("Prior store unavailable, falling back to random exploration: %s", exc)

    # 2. Exploration: random valid cells
    remaining = n - len(cells)
    if remaining > 0:
        cells.extend(
            _random_explore(remaining, fidelity, tasks, seed, spec, search_space)
        )

    return cells[:n]


def _get_top_coordinates(store: RecordStore, fidelity: str, k: int) -> list[Coordinate]:
    """Get top-k coordinates by val_acc from a prior store."""
    from computronium.experiment.schema.record import GateVerdict

    try:
        records = store.query_records(
            fidelity=fidelity,
            gate_verdict=GateVerdict.PASS_,
            quarantine=False,
        )
    except Exception:
        return []

    # Sort by val_acc descending
    valid_records = [r for r in records if r.payload.get("val_acc") is not None]
    valid_records.sort(key=lambda r: r.payload.get("val_acc", 0.0), reverse=True)

    coords = []
    for record in valid_records[:k]:
        coord = Coordinate.from_record(record)
        coords.append(coord)
    return coords


def _mutate_around(
    top_coords: list[Coordinate],
    n: int,
    fidelity: str,
    tasks: Sequence[str],
    spec: RunSpec,
    search_space,
) -> list[tuple[Coordinate, Schedule]]:
    """Mutate 1-2 axes of top performers to explore neighborhood."""
    mutated_cells: list[tuple[Coordinate, Schedule]] = []

    if not top_coords:
        return mutated_cells

    per_coord = max(1, n // len(top_coords))
    axes_order = [
        StructuralAxis.SUBSTRATE,
        StructuralAxis.GEOMETRY,
        StructuralAxis.DYNAMICS,
        StructuralAxis.PLASTICITY,
        StructuralAxis.CREDIT,
        StructuralAxis.UPDATE,
    ]

    for coord in top_coords:
        for _ in range(per_coord):
            if len(mutated_cells) >= n:
                break

            # Mutate 1-2 axes
            k = random.randint(1, 2)  # ruff: ignore[S311]
            axes_to_mutate = random.sample(axes_order, k)  # ruff: ignore[S311]

            new_params = dict(coord.params)
            new_values = {
                "substrate": coord.substrate,
                "geometry": coord.geometry,
                "dynamics": coord.dynamics,
                "plasticity": coord.plasticity,
                "credit": coord.credit,
                "update": coord.update,
            }

            for axis in axes_to_mutate:
                # Get valid primitives for this axis from search space
                primitives = search_space.primitives(axis)
                if primitives:
                    new_values[axis.value] = random.choice(primitives)  # ruff: ignore[S311]

            mutated_coord = Coordinate(
                substrate=new_values["substrate"],
                geometry=new_values["geometry"],
                dynamics=new_values["dynamics"],
                plasticity=new_values["plasticity"],
                credit=new_values["credit"],
                update=new_values["update"],
                params=new_params,
            )

            # Check compatibility
            violations = check_compatibility_matrix(
                mutated_coord.substrate,
                mutated_coord.geometry,
                mutated_coord.dynamics,
                mutated_coord.plasticity,
                mutated_coord.credit,
                mutated_coord.update,
            )
            if violations:
                continue

            # Pick a task and create schedule
            task = random.choice(tasks)  # ruff: ignore[S311]
            schedule = _schedule_from_spec(spec, task, fidelity)
            mutated_cells.append((mutated_coord, schedule))

    return mutated_cells


def _random_explore(
    n: int,
    fidelity: str,
    tasks: Sequence[str],
    seed: int,
    spec: RunSpec,
    search_space,
) -> list[tuple[Coordinate, Schedule]]:
    """Random valid cells from iter_candidates."""
    cells: list[tuple[Coordinate, Schedule]] = []

    # Use iter_candidates with a reasonable max_scan
    for coord, schedule in iter_candidates(
        spec,
        search_space,
        shape=task_shape,
        max_scan=50000,
        check_composable=True,
    ):
        if len(cells) >= n:
            break

        violations = check_compatibility_matrix(
            coord.substrate,
            coord.geometry,
            coord.dynamics,
            coord.plasticity,
            coord.credit,
            coord.update,
        )
        if violations:
            continue

        # The schedule from iter_candidates already has the correct task_id
        # But we need to ensure it matches our fidelity settings
        cell_schedule = schedule
        if schedule.fidelity != fidelity:
            cell_schedule = _schedule_from_spec(spec, schedule.task_id, fidelity)
        cells.append((coord, cell_schedule))

    return cells


def _evaluate_one(
    cell: tuple[Coordinate, Schedule],
    fidelity: str,
    store_path: str,
    provenance: Provenance,
) -> Record:
    """Evaluate a single cell (for ProcessPoolExecutor)."""
    coord, schedule = cell
    try:
        return cell_record(
            coordinate=coord,
            schedule=schedule,
            provenance=provenance,
        )
    except Exception as e:
        logger.exception(
            "Cell evaluation failed: %s | %s/%s/%s/%s/%s/%s",
            e,
            coord.substrate,
            coord.geometry,
            coord.dynamics,
            coord.plasticity,
            coord.credit,
            coord.update,
        )
        raise


def run_simple_survey(  # noqa: PLR0913, PLR0915
    hours: float,
    fidelity: str = "L0",
    tasks: Sequence[str] | None = None,
    max_workers: int = 4,
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
) -> dict[str, Any]:
    """Run a SimpleSurvey experiment.

    Args:
        hours: Time budget in hours.
        fidelity: Fidelity level (L0, L1, L2).
        tasks: Task names to use (defaults to fidelity-appropriate tasks).
        max_workers: Number of parallel workers.
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

    Returns:
        If dry_run: {"cells": list[(coord, schedule)], "n": int, "tasks": list[str]}
        If evaluation: {"run_id": str, "store_path": str, "cells_evaluated": int, ...}
    """
    # 1. Budget -> cell count
    # For single-fidelity runs, use full budget for that fidelity
    budget_s = int(hours * 3600)
    cell_counts = estimate_cell_counts(budget_s)
    # Use full budget for the selected fidelity, not split
    fidelity_costs = {
        "L0": 5,    # ~5s per cell (1 epoch, 1 seed)
        "L1": 30,   # ~30s per cell (3 epochs, 2 seeds)
        "L2": 300,  # ~300s per cell (10 epochs, 5 seeds)
    }
    cost_per_cell = fidelity_costs.get(fidelity, 30)
    n_cells = max(1, budget_s // cost_per_cell)

    logger.info(
        "SimpleSurvey: budget=%.2fh (%ds), fidelity=%s, cost_per_cell=%ds, estimated_cells=%d",
        hours,
        budget_s,
        fidelity,
        cost_per_cell,
        n_cells,
    )

    # 2. Build RunSpec
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.run_spec import AxisSelection
    from computronium.experiment.schema.seed_registries import seed_all_registries

    # Ensure registries are seeded
    seed_all_registries()

    axis_selections = []
    if axes:
        for axis_name, primitives in axes.items():
            axis_enum = getattr(StructuralAxis, axis_name.upper())
            axis_selections.append(AxisSelection(axis=axis_enum, primitives=primitives))

    spec = RunSpec(
        profile="simple_survey",
        task=tasks[0] if tasks else "auto",
        tasks=tuple(tasks) if tasks else (),
        objectives=objectives or ("validation_accuracy", "energy_per_step"),
        fidelity=fidelity,
        n_seeds=n_seeds,
        epochs=epochs,
        batch_limit=batch_limit,
        seed=seed,
        budget_seconds=budget_s,
        param_budget=param_budget,
        device=device,
        axes=tuple(axis_selections),
        hyperparameters=hyperparameters or {},
        fidelity_seeds={"L0": 1, "L1": 2, "L2": 5},
        fidelity_epochs={"L0": 1, "L1": 3, "L2": 10},
    )

    # 3. Build search space
    search_space = search_space_from_spec(spec, tasks=spec.task_names)

    # 4. Determine tasks to use
    if tasks is None:
        tasks = get_fidelity_tasks(fidelity)

    # 5. Generate cells
    random.seed(seed)
    cells = _generate_valid_cells(
        n_cells,
        fidelity,
        tasks,
        seed,
        spec,
        search_space,
        promote_from,
        promote_top,
    )

    logger.info("Generated %d valid cells", len(cells))

    if dry_run:
        return {
            "cells": cells,
            "n": len(cells),
            "tasks": list(tasks),
            "fidelity": fidelity,
        }

    # 6. Parallel evaluate
    run_id = str(uuid.uuid4())[:8]
    provenance = _build_provenance(spec, run_id)

    # Create store and run
    store_config = StoreConfig(path=Path(store_path))
    with RecordStore(store_config) as store:
        store.create_run(run_id, spec)

        results: list[Record] = []
        n_total = len(cells)
        logger.info("Evaluating %d cells with %d workers...", n_total, max_workers)
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as pool:
            futures = [
                pool.submit(_evaluate_one, cell, fidelity, store_path, provenance)
                for cell in cells
            ]
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                try:
                    record = future.result()
                    results.append(record)
                    if verbose or i % max(1, n_total // 10) == 0 or i == n_total:
                        gate = record.status.gate_verdict.value
                        val_acc = record.payload.get("val_acc", "N/A")
                        logger.info(
                            "  [%d/%d] %s | val_acc=%s | %s/%s/%s/%s/%s/%s",
                            i,
                            n_total,
                            gate,
                            f"{val_acc:.4f}" if isinstance(val_acc, float) else val_acc,
                            record.substrate,
                            record.geometry,
                            record.dynamics,
                            record.plasticity,
                            record.credit,
                            record.update,
                        )
                except Exception as e:
                    logger.exception("Cell evaluation failed: %s", e)

        # 7. Store results
        for record in results:
            store.append(record)

        # 8. Generate report
        from computronium.experiment.surface.report import ReportGenerator

        generator = ReportGenerator(store)
        report = generator.run_summary(run_id)

    passed = sum(1 for r in results if r.status.gate_verdict.value == "PASS")
    failed = len(results) - passed

    logger.info(
        "Done: %d evaluated, %d passed, %d failed, %.1fs walltime",
        len(results),
        passed,
        failed,
        sum(r.payload.get("walltime_s", 0) for r in results),
    )

    return {
        "run_id": run_id,
        "store_path": store_path,
        "cells_evaluated": len(results),
        "cells_passed": passed,
        "cells_failed": failed,
        "walltime_s": sum(r.payload.get("walltime_s", 0) for r in results),
        "report": report,
    }


def main() -> None:
    """CLI entry point for simple_survey."""
    import argparse
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    parser = argparse.ArgumentParser(
        description="SimpleSurvey - Minimal adaptive experiment system"
    )
    parser.add_argument("hours", type=float, help="Time budget in hours")
    parser.add_argument("--fidelity", default="L0", choices=["L0", "L1", "L2"])
    parser.add_argument(
        "--tasks", default="", help="Comma-separated task names (default: auto)"
    )
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--store", default="experiment.duckdb")
    parser.add_argument("--promote-from", default=None)
    parser.add_argument("--promote-top", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--param-budget", type=int, default=0)
    parser.add_argument("--n-seeds", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-limit", type=int, default=0)
    parser.add_argument("--axes", default="", help="JSON: axis -> [primitives]")
    parser.add_argument("--hyperparameters", default="", help="JSON: hyperparameters")
    parser.add_argument("--objectives", default="", help="Comma-separated objectives")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose progress output")

    args = parser.parse_args()

    tasks = args.tasks.split(",") if args.tasks else None
    axes = json.loads(args.axes) if args.axes else None
    hyperparameters = json.loads(args.hyperparameters) if args.hyperparameters else None
    objectives = tuple(args.objectives.split(",")) if args.objectives else ()

    result = run_simple_survey(
        hours=args.hours,
        fidelity=args.fidelity,
        tasks=tasks,
        max_workers=args.max_workers,
        store_path=args.store,
        promote_from=args.promote_from,
        promote_top=args.promote_top,
        seed=args.seed,
        dry_run=args.dry_run,
        device=args.device,
        param_budget=args.param_budget,
        n_seeds=args.n_seeds,
        epochs=args.epochs,
        batch_limit=args.batch_limit,
        axes=axes,
        hyperparameters=hyperparameters,
        objectives=objectives,
        verbose=args.verbose,
    )

    print(json.dumps(result, default=str, indent=2))


if __name__ == "__main__":
    main()
