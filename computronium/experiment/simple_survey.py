"""SimpleSurvey: Minimal adaptive experiment system.

Replaces the complex multi-stage pipeline with a single parallel evaluation script.
Adaptivity comes from offline importance sampling using prior runs, not online policy.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import random
import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import] - used for git SHA lookup with validated path
import sys
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

from computronium.core.logging import get_logger
from computronium.domains._task_registry import get_fidelity_tasks
from computronium.experiment.evidence.store import RecordStore
from computronium.experiment.evidence.store._models import StoreConfig
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


# Fidelity cost estimates (seconds per cell)
FIDELITY_COSTS: dict[str, int] = {
    "L0": 5,  # ~5s per cell (1 epoch, 1 seed)
    "L1": 30,  # ~30s per cell (3 epochs, 2 seeds)
    "L2": 300,  # ~300s per cell (10 epochs, 5 seeds)
}

# Structural axes in mutation order
MUTATION_AXES: list[StructuralAxis] = [
    StructuralAxis.SUBSTRATE,
    StructuralAxis.GEOMETRY,
    StructuralAxis.DYNAMICS,
    StructuralAxis.PLASTICITY,
    StructuralAxis.CREDIT,
    StructuralAxis.UPDATE,
]


def _schedule_from_spec(spec: RunSpec, task: str, fidelity: str) -> Schedule:
    """Create a Schedule from a RunSpec for a given task and fidelity."""
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
    git_path = shutil.which("git")
    code_sha = "unknown"
    if git_path:
        with contextlib.suppress(Exception):
            code_sha = subprocess.check_output(  # ruff: ignore[subprocess-without-shell-equals-true] - git_path validated via shutil.which
                [git_path, "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
            ).strip()
        with contextlib.suppress(Exception):
            if code_sha == "unknown":
                code_sha = subprocess.check_output(  # ruff: ignore[subprocess-without-shell-equals-true] - git_path validated via shutil.which
                    [git_path, "rev-parse", "--short", "HEAD"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                ).strip()

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


def _check_coord_compatibility(coord: Coordinate) -> bool:
    """Check if a coordinate passes the compatibility matrix."""
    violations = check_compatibility_matrix(
        coord.substrate,
        coord.geometry,
        coord.dynamics,
        coord.plasticity,
        coord.credit,
        coord.update,
    )
    return not violations


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

    for coord in top_coords:
        for _ in range(per_coord):
            if len(mutated_cells) >= n:
                break

            # Mutate 1-2 axes
            k = random.randint(1, 2)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
            axes_to_mutate = random.sample(MUTATION_AXES, k)  # ruff: ignore[suspicious-non-cryptographic-random-usage]

            new_values = {
                "substrate": coord.substrate,
                "geometry": coord.geometry,
                "dynamics": coord.dynamics,
                "plasticity": coord.plasticity,
                "credit": coord.credit,
                "update": coord.update,
            }

            for axis in axes_to_mutate:
                primitives = search_space.primitives(axis)
                if primitives:
                    new_values[axis.value] = random.choice(primitives)  # ruff: ignore[suspicious-non-cryptographic-random-usage]

            mutated_coord = Coordinate(
                substrate=new_values["substrate"],
                geometry=new_values["geometry"],
                dynamics=new_values["dynamics"],
                plasticity=new_values["plasticity"],
                credit=new_values["credit"],
                update=new_values["update"],
                params=dict(coord.params),
            )

            if not _check_coord_compatibility(mutated_coord):
                continue

            task = random.choice(tasks)  # ruff: ignore[suspicious-non-cryptographic-random-usage]
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

    for coord, schedule in iter_candidates(
        spec,
        search_space,
        shape=task_shape,
        max_scan=50000,
        check_composable=True,
    ):
        if len(cells) >= n:
            break

        if not _check_coord_compatibility(coord):
            continue

        cell_schedule = schedule
        if schedule.fidelity != fidelity:
            cell_schedule = _schedule_from_spec(spec, schedule.task_id, fidelity)
        cells.append((coord, cell_schedule))

    return cells


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
            logger.debug(
                "Prior store unavailable, falling back to random exploration: %s",
                exc,
            )

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

    valid_records = [r for r in records if r.payload.get("val_acc") is not None]
    valid_records.sort(key=lambda r: r.payload.get("val_acc", 0.0), reverse=True)

    coords = []
    for record in valid_records[:k]:
        coord = Coordinate.from_record(record)
        coords.append(coord)
    return coords


def _evaluate_one(
    cell: tuple[Coordinate, Schedule],
    fidelity: str,
    store_path: str,
    provenance: Provenance,
):
    """Evaluate a single cell (for ProcessPoolExecutor)."""
    coord, schedule = cell
    try:
        return cell_record(
            coordinate=coord,
            schedule=schedule,
            provenance=provenance,
        )
    except Exception:
        logger.exception(
            "Cell evaluation failed: %s/%s/%s/%s/%s/%s",
            coord.substrate,
            coord.geometry,
            coord.dynamics,
            coord.plasticity,
            coord.credit,
            coord.update,
        )
        raise


@dataclass(frozen=True, slots=True)
class _SpecParams:
    """Parameters for building a RunSpec."""

    hours: float
    fidelity: str
    tasks: Sequence[str] | None
    seed: int
    device: str
    param_budget: int
    n_seeds: int
    epochs: int
    batch_limit: int
    axes: dict[str, tuple[str, ...]] | None
    hyperparameters: dict[str, Any] | None
    objectives: tuple[str, ...]


def _build_spec(params: _SpecParams) -> RunSpec:
    """Build RunSpec from survey parameters."""
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.run_spec import AxisSelection
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()

    axis_selections = []
    if params.axes:
        for axis_name, primitives in params.axes.items():
            axis_enum = getattr(StructuralAxis, axis_name.upper())
            axis_selections.append(AxisSelection(axis=axis_enum, primitives=primitives))

    spec = RunSpec(
        profile="simple_survey",
        task=params.tasks[0] if params.tasks else "auto",
        tasks=tuple(params.tasks) if params.tasks else (),
        objectives=params.objectives or ("validation_accuracy", "energy_per_step"),
        fidelity=params.fidelity,
        n_seeds=params.n_seeds,
        epochs=params.epochs,
        batch_limit=params.batch_limit,
        seed=params.seed,
        budget_seconds=int(params.hours * 3600),
        param_budget=params.param_budget,
        device=params.device,
        axes=tuple(axis_selections),
        hyperparameters=params.hyperparameters or {},
        fidelity_seeds={"L0": 1, "L1": 2, "L2": 5},
        fidelity_epochs={"L0": 1, "L1": 3, "L2": 10},
    )
    return spec


def _generate_cells(
    spec: RunSpec,
    fidelity: str,
    tasks: Sequence[str],
    seed: int,
    promote_from: str | None,
    promote_top: int,
) -> list[tuple[Coordinate, Schedule]]:
    """Generate cells for the survey."""
    search_space = search_space_from_spec(spec, tasks=tasks)

    random.seed(seed)
    n_cells = _estimate_cell_count(spec.budget_seconds, fidelity)

    logger.info(
        "SimpleSurvey: budget=%ds, fidelity=%s, cost_per_cell=%ds, estimated_cells=%d",
        spec.budget_seconds,
        fidelity,
        FIDELITY_COSTS.get(fidelity, 30),
        n_cells,
    )

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
    return cells


def _estimate_cell_count(budget_seconds: int, fidelity: str) -> int:
    """Estimate number of cells from budget and fidelity."""
    cost_per_cell = FIDELITY_COSTS.get(fidelity, 30)
    return max(1, int(budget_seconds // cost_per_cell))


def _evaluate_cells_parallel(
    cells: list[tuple[Coordinate, Schedule]],
    fidelity: str,
    store_path: str,
    provenance: Provenance,
    max_workers: int,
    verbose: bool,
) -> list:
    """Evaluate cells in parallel using ProcessPoolExecutor."""
    n_total = len(cells)
    results: list = []

    logger.info("Evaluating %d cells with %d workers...", n_total, max_workers)

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(_evaluate_one, cell, fidelity, store_path, provenance)
            for cell in cells
        ]
        for i, future in enumerate(as_completed(futures), 1):
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

    return results


def _store_results(store_path: str, run_id: str, spec: RunSpec, results: list) -> None:
    """Store evaluation results in the record store."""
    store_config = StoreConfig(path=Path(store_path))
    with RecordStore(store_config) as store:
        store.create_run(run_id, spec)
        for record in results:
            store.append(record)


def _generate_report(store_path: str, run_id: str) -> dict:
    """Generate report from stored results."""
    from computronium.experiment.surface.report import ReportGenerator

    store_config = StoreConfig(path=Path(store_path))
    with RecordStore(store_config) as store:
        generator = ReportGenerator(store)
        return generator.run_summary(run_id)


def run_simple_survey(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] - experiment config requires many parameters
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
        verbose: Verbose progress output.

    Returns:
        If dry_run: {"cells": list[(coord, schedule)], "n": int, "tasks": list[str]}
        If evaluation: {"run_id": str, "store_path": str, "cells_evaluated": int, ...}
    """
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
    )
    spec = _build_spec(params)

    # 2. Determine tasks to use
    if tasks is None:
        tasks = get_fidelity_tasks(fidelity)

    # 3. Generate cells
    cells = _generate_cells(
        spec=spec,
        fidelity=fidelity,
        tasks=tasks,
        seed=seed,
        promote_from=promote_from,
        promote_top=promote_top,
    )

    if dry_run:
        return {
            "cells": cells,
            "n": len(cells),
            "tasks": list(tasks),
            "fidelity": fidelity,
        }

    # 4. Parallel evaluate
    run_id = str(uuid.uuid4())[:8]
    provenance = _build_provenance(spec, run_id)

    results = _evaluate_cells_parallel(
        cells=cells,
        fidelity=fidelity,
        store_path=store_path,
        provenance=provenance,
        max_workers=max_workers,
        verbose=verbose,
    )

    # 5. Store results
    _store_results(store_path, run_id, spec, results)

    # 6. Generate report
    report = _generate_report(store_path, run_id)

    passed = sum(1 for r in results if r.status.gate_verdict.value == "PASS")
    failed = len(results) - passed
    total_walltime = sum(r.payload.get("walltime_s", 0) for r in results)

    logger.info(
        "Done: %d evaluated, %d passed, %d failed, %.1fs walltime",
        len(results),
        passed,
        failed,
        total_walltime,
    )

    return {
        "run_id": run_id,
        "store_path": store_path,
        "cells_evaluated": len(results),
        "cells_passed": passed,
        "cells_failed": failed,
        "walltime_s": total_walltime,
        "report": report,
    }


@dataclass(frozen=True, slots=True)
class _SelfTestConfig:
    """Configuration for self-test."""

    min_python: tuple[int, int] = (3, 14)  # Match pyproject.toml requires-python
    dry_run_hours: float = 0.001
    dry_run_fidelity: str = "L0"
    dry_run_device: str = "cpu"


def _check_python_version(config: _SelfTestConfig) -> bool:
    """Check Python version meets minimum."""
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    logger.info("Python: %s", py_version)
    if sys.version_info < config.min_python:
        logger.error("Python %s+ required, got %s", config.min_python, py_version)
        return False
    return True


def _check_uv_available() -> bool:
    """Check uv is available."""
    uv_path = shutil.which("uv")
    if uv_path is None:
        logger.error("uv not found in PATH")
        return False
    try:
        result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true] - uv_path validated via shutil.which
            [uv_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        logger.exception("uv check failed")
        return False
    else:
        if result.returncode != 0:
            logger.error("uv not found")
            return False
        logger.info("uv: %s", result.stdout.strip())
        return True


def _check_stdlib_modules() -> bool:
    """Check core stdlib modules are available."""
    for mod in [
        "json",
        "uuid",
        "pathlib",
        "dataclasses",
        "concurrent.futures",
        "random",
    ]:
        try:
            __import__(mod)
        except ImportError:
            logger.exception("stdlib %s missing", mod)
            return False
    logger.info("stdlib OK")
    return True


def _check_torch() -> bool:
    """Check torch is available and functional."""
    try:
        import torch

    except ImportError:
        logger.exception("torch import failed")
        logger.exception("Fix: uv sync --dev --all-extras")
        return False
    except Exception:
        logger.exception("torch import crashed")
        logger.exception("This may indicate a CUDA driver/library mismatch")
        logger.exception("Try: export CUDA_VISIBLE_DEVICES='' to force CPU mode")
        return False
    else:
        logger.info("Torch: %s", torch.__version__)
        cuda_available = False
        try:
            cuda_available = torch.cuda.is_available()
        except Exception as e:
            logger.warning("CUDA check failed: %s", e)
            logger.warning("Forcing CPU mode")

        logger.info("CUDA available: %s", cuda_available)
        if cuda_available:
            try:
                logger.info("GPU: %s", torch.cuda.get_device_name(0))
                logger.info(
                    "GPU memory: %.1f GB",
                    torch.cuda.get_device_properties(0).total_memory / 1e9,
                )
            except Exception as e:
                logger.warning("GPU query failed: %s", e)

        # Test basic tensor ops
        _test_tensor_ops()

        return True


def _test_tensor_ops() -> None:
    """Test basic tensor operations."""
    import torch

    x = torch.tensor([1.0, 2.0])
    y = x * 2
    if y.tolist() != [2.0, 4.0]:
        msg = "tensor ops produced unexpected result"
        raise AssertionError(msg)
    logger.info("Tensor ops: OK")


def _check_computronium_modules() -> bool:
    """Check computronium modules are importable."""
    required = [
        "computronium.core.logging",
        "computronium.domains._task_registry",
        "computronium.experiment.evidence.store",
        "computronium.experiment.evidence.store._models",
        "computronium.experiment.execution.pipeline._budget_constants",
        "computronium.experiment.kernel.evaluate",
        "computronium.experiment.kernel.search_space",
        "computronium.experiment.schema.axis",
        "computronium.experiment.schema.coordinate",
        "computronium.experiment.schema.run_spec",
        "computronium.ontology.system",
    ]
    failed = []
    for mod in required:
        try:
            __import__(mod)
        except Exception:
            logger.exception("%s import failed", mod)
            failed.append(mod)

    if failed:
        logger.error("Failed imports (%d): %s", len(failed), ", ".join(failed))
        logger.error("Fix: uv sync --dev --all-extras")
        return False

    logger.info("All %d modules OK", len(required))
    return True


def _check_dry_run(config: _SelfTestConfig) -> bool:
    """Run dry-run functional test."""
    try:
        result = run_simple_survey(
            config.dry_run_hours,
            fidelity=config.dry_run_fidelity,
            dry_run=True,
            device=config.dry_run_device,
        )
    except Exception:
        logger.exception("dry-run crashed")
        import traceback
        traceback.print_exc()
        return False
    else:
        n_cells = result.get("n", 0)
        logger.info("Dry-run generated %d cells", n_cells)
        if n_cells == 0:
            logger.error("dry-run generated 0 cells - search space may be empty or over-constrained")
            logger.error("Try: --fidelity L0 --device cpu --no-self-test")
            return False
        return True


def _run_self_test() -> bool:
    """Run environment self-tests. Returns True if all pass."""
    logger.info("Checking environment...")
    config = _SelfTestConfig()

    checks = [
        ("Python version", lambda: _check_python_version(config)),
        ("uv available", _check_uv_available),
        ("stdlib modules", _check_stdlib_modules),
        ("torch", _check_torch),
        ("computronium modules", _check_computronium_modules),
        ("dry-run", lambda: _check_dry_run(config)),
    ]

    for idx, (name, check) in enumerate(checks, 1):
        logger.info("Test %d/%d: %s...", idx, len(checks), name)
        if not check():
            logger.error("FAIL: %s", name)
            return False

    logger.info("ALL TESTS PASSED")
    return True


def main() -> None:  # ruff: ignore[too-many-statements] - CLI entry point handles many arguments
    """CLI entry point for simple_survey."""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(message)s", force=True)

    parser = argparse.ArgumentParser(
        description="SimpleSurvey - Minimal adaptive experiment system"
    )
    parser.add_argument("hours", type=float, nargs="?", help="Time budget in hours (required unless --doctor)")
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
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose progress output"
    )
    parser.add_argument(
        "--no-self-test", action="store_true", help="Skip environment self-test"
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

    if not args.no_self_test:
        logger.info("Running self-test...")
        try:
            if not _run_self_test():
                logger.error("Self-test failed. Use --no-self-test to skip.")
                sys.exit(1)
        except Exception:
            logger.exception("Self-test CRASHED")
            import traceback

            traceback.print_exc()
            sys.exit(1)
        logger.info("Self-test passed")

    tasks = args.tasks.split(",") if args.tasks else None
    axes = json.loads(args.axes) if args.axes else None
    hyperparameters = json.loads(args.hyperparameters) if args.hyperparameters else None
    objectives = tuple(args.objectives.split(",")) if args.objectives else ()

    try:
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
    except Exception:
        logger.exception("FATAL")
        sys.exit(1)


if __name__ == "__main__":
    main()
