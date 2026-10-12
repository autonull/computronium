"""Ablation Runner: single-axis sweeps holding other axes fixed.

Compares the effect of varying one structural axis while holding all others
constant. Produces statistical summaries across seeds for rigorous comparison.

Usage:
    uv run python -m computronium.experiment.runners.ablation \
      --vary update --fix geometry=feedforward dynamics=instantaneous \
      --budget 1h --seeds 5
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec

if TYPE_CHECKING:
    from computronium.experiment.execution.policy import Policy


@dataclass(frozen=True, slots=True)
class AblationSpec:
    """Specification for an ablation experiment.

    Args:
        vary: The structural axis to sweep.
        fix: Fixed values for other axes (axis_name -> primitive_name).
        n_seeds: Number of seeds per configuration for statistical rigor.
        budget_seconds: Total time budget for the ablation.
        metric: Primary metric for comparison (e.g., "validation_accuracy").
        task: Task to run ablation on (defaults to first task in profile).
        base_config: Optional base RunSpec to derive from.
    """

    vary: StructuralAxis
    fix: dict[StructuralAxis, str]
    n_seeds: int = 5
    budget_seconds: float = 3600
    metric: str = "validation_accuracy"
    task: str | None = None
    base_config: RunSpec | None = None


@dataclass(slots=True)
class AblationResult:
    """Results of an ablation experiment."""

    vary_axis: StructuralAxis
    configurations: list[dict[str, Any]]  # Per-primitive results with stats
    best_primitive: str
    best_value: float
    walltime_s: float


class AblationRunner:
    """Runs single-axis ablation experiments.

    For each primitive on the `vary` axis, runs `n_seeds` evaluations with all
    other axes fixed to the values in `fix`. Aggregates results with mean/std
    and identifies the best performing primitive.
    """

    def __init__(
        self,
        spec: AblationSpec,
        *,
        store: RecordStore | None = None,
        backend: LocalBackend | None = None,
        policy: Policy | None = None,
        checkpoint_dir: str | None = None,
    ) -> None:
        self.spec = spec
        self.store = store or RecordStore(StoreConfig(path=Path(":memory:")))
        self.backend = backend or LocalBackend(max_workers=4)

        # Create default policy if none provided
        if policy is None:
            from computronium.experiment.execution.policy import create_policy

            self.policy = create_policy("round_robin_grid")
        else:
            self.policy = policy

        self.checkpoint_dir = checkpoint_dir

        if self.spec.base_config is not None:
            self.base_spec = self.spec.base_config
        else:
            # Create a minimal RunSpec from the ablation spec
            self.base_spec = self._build_base_spec()

        self.run_id = f"ablation_{self.spec.vary.value}_{int(time.time())}"

    def _build_base_spec(self) -> RunSpec:
        """Build a RunSpec from the ablation specification."""

        # Determine task
        task = self.spec.task or "digits"

        # Build axis selections
        axes: list[AxisSelection] = []
        for axis in StructuralAxis:
            if axis == self.spec.vary:
                # Vary axis: include all available primitives
                from computronium.experiment.schema.axis import AXES_REGISTRIES

                registry = AXES_REGISTRIES[axis]
                primitives = tuple(
                    sorted(n for n, s in registry.items() if s.available)
                )
            elif axis in self.spec.fix:
                # Fixed axis: only the specified primitive
                primitives = (self.spec.fix[axis],)
            else:
                # Unspecified axis: use all available
                from computronium.experiment.schema.axis import AXES_REGISTRIES

                registry = AXES_REGISTRIES[axis]
                primitives = tuple(
                    sorted(n for n, s in registry.items() if s.available)
                )

            axes.append(
                AxisSelection(axis=axis, primitives=primitives if primitives else None)
            )

        return RunSpec(
            profile=f"ablation_{self.spec.vary.value}",
            task=task,
            tasks=(),
            objectives=("validation_accuracy", "walltime_total"),
            fidelity="L1",
            n_seeds=self.spec.n_seeds,
            epochs=1,
            batch_limit=2,
            budget_seconds=self.spec.budget_seconds,
            param_budget=10000,
            axes=tuple(axes),
            seed=0,
            device="auto",
        )

    async def run(self) -> AblationResult:
        """Execute the ablation experiment."""
        start_time = time.monotonic()

        # Build search space from base spec
        search_space = search_space_from_spec(self.base_spec)

        # Get the primitives for the vary axis
        vary_primitives = search_space.primitives(self.spec.vary)

        # Open store once for the entire ablation
        with self.store:
            # For each primitive on the vary axis, run evaluation
            results = []
            for primitive in vary_primitives:
                # Create a RunSpec with this primitive fixed
                config = self._build_variant_spec(primitive)
                variant_run_id = f"{self.run_id}_{primitive}"

                # Register the run with the correct run_id
                self.store.create_run(run_id=variant_run_id, spec=config)

                runner = PipelineRunner(
                    config=PipelineConfig(
                        run_id=variant_run_id,
                        run_spec=config,
                        deadline=Deadline.from_seconds(self.spec.budget_seconds),
                        backend=self.backend,
                        policy=self.policy,
                    ),
                    store=self.store,
                )

                try:
                    records = await runner.run()
                    # Aggregate metrics across seeds
                    aggregated = self._aggregate_records(records, primitive)
                    results.append(aggregated)
                except Exception as e:
                    results.append({
                        "primitive": primitive,
                        "error": str(e),
                        "mean": None,
                        "std": None,
                        "n_seeds": 0,
                    })

        # Find best primitive
        valid_results = [r for r in results if r["mean"] is not None]
        if valid_results:
            best = max(valid_results, key=lambda r: r["mean"])
            best_primitive = best["primitive"]
            best_value = best["mean"]
        else:
            best_primitive = ""
            best_value = float("-inf")

        walltime_s = time.monotonic() - start_time

        return AblationResult(
            vary_axis=self.spec.vary,
            configurations=results,
            best_primitive=best_primitive,
            best_value=best_value,
            walltime_s=walltime_s,
        )

    def _build_variant_spec(self, primitive: str) -> RunSpec:
        """Build a RunSpec with the vary axis fixed to one primitive."""
        axes: list[AxisSelection] = []
        for axis in StructuralAxis:
            if axis == self.spec.vary:
                axes.append(AxisSelection(axis=axis, primitives=(primitive,)))
            elif axis in self.spec.fix:
                axes.append(AxisSelection(axis=axis, primitives=(self.spec.fix[axis],)))
            else:
                from computronium.experiment.schema.axis import AXES_REGISTRIES

                registry = AXES_REGISTRIES[axis]
                primitives = tuple(
                    sorted(n for n, s in registry.items() if s.available)
                )
                axes.append(
                    AxisSelection(
                        axis=axis, primitives=primitives if primitives else None
                    )
                )

        return RunSpec(
            profile=f"ablation_{self.spec.vary.value}_{primitive}",
            task=self.base_spec.task_names[0],
            tasks=(),
            objectives=("validation_accuracy", "walltime_total"),
            fidelity="L1",
            n_seeds=self.spec.n_seeds,
            epochs=1,
            batch_limit=2,
            budget_seconds=self.spec.budget_seconds,
            param_budget=10000,
            axes=tuple(axes),
            seed=self.base_spec.seed,
            device="auto",
        )

    def _aggregate_records(self, records: list, primitive: str) -> dict[str, Any]:
        """Aggregate records across seeds for one primitive."""
        if not records:
            return {
                "primitive": primitive,
                "mean": None,
                "std": None,
                "n_seeds": 0,
            }

        # Map objective name to payload key
        from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

        obj_spec = OBJECTIVES_REGISTRY.get(self.spec.metric)
        payload_key = (
            obj_spec.metric_key
            if obj_spec and obj_spec.metric_key
            else self.spec.metric
        )

        # Extract the primary metric from each record
        values = []
        for record in records:
            val = record.payload.get(payload_key)
            if val is not None:
                values.append(float(val))

        if not values:
            return {
                "primitive": primitive,
                "mean": None,
                "std": None,
                "n_seeds": len(records),
            }

        import statistics

        return {
            "primitive": primitive,
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "n_seeds": len(values),
            "raw_values": values,
        }

    def print_results(self, result: AblationResult) -> None:
        """Pretty-print ablation results."""
        print(f"\n{'=' * 60}")
        print(f"Ablation Results: {result.vary_axis.value}")
        print(f"{'=' * 60}")
        print(f"Best: {result.best_primitive} ({result.best_value:.4f})")
        print(f"Walltime: {result.walltime_s:.1f}s")
        print(f"{'-' * 60}")
        print(f"{'Primitive':<30} {'Mean':>10} {'Std':>10} {'N':>4}")
        print(f"{'-' * 60}")
        for config in result.configurations:
            prim = config["primitive"]
            mean = config["mean"]
            std = config["std"]
            n = config["n_seeds"]
            if mean is not None:
                marker = " *" if prim == result.best_primitive else ""
                print(f"{prim:<30} {mean:>10.4f} {std:>10.4f} {n:>4}{marker}")
            else:
                print(f"{prim:<30} {'ERROR':>10} {'N/A':>10} {n:>4}")
        print(f"{'=' * 60}")


# CLI entry point
async def _run_ablation_cli(
    vary: str,
    fix: dict[str, str],
    budget: float,
    seeds: int,
    metric: str,
    task: str | None,
) -> AblationResult:
    """Run ablation from CLI arguments."""
    vary_axis = StructuralAxis(vary)
    fix_axes = {StructuralAxis(k): v for k, v in fix.items()}

    spec = AblationSpec(
        vary=vary_axis,
        fix=fix_axes,
        n_seeds=seeds,
        budget_seconds=budget,
        metric=metric,
        task=task,
    )

    runner = AblationRunner(spec)
    result = await runner.run()
    runner.print_results(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ablation experiment")
    parser.add_argument("--vary", required=True, help="Axis to vary")
    parser.add_argument(
        "--fix", action="append", default=[], help="Fixed axis=value pairs"
    )
    parser.add_argument("--budget", type=float, default=3600, help="Budget in seconds")
    parser.add_argument("--seeds", type=int, default=5, help="Seeds per configuration")
    parser.add_argument(
        "--metric", default="validation_accuracy", help="Primary metric"
    )
    parser.add_argument("--task", help="Task name")

    args = parser.parse_args()

    fix_dict = {}
    for pair in args.fix:
        if "=" in pair:
            k, v = pair.split("=", 1)
            fix_dict[k] = v

    asyncio.run(
        _run_ablation_cli(
            vary=args.vary,
            fix=fix_dict,
            budget=args.budget,
            seeds=args.seeds,
            metric=args.metric,
            task=args.task,
        )
    )
