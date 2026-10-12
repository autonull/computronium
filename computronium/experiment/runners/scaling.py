"""Scaling Runner: sweep depth, width, param_budget, settle_horizon.

Systematically varies architectural and dynamical hyperparameters to characterize
scaling laws. Produces scaling curves with statistical summaries.

Usage:
    uv run python -m computronium.experiment.runners.scaling \
      --vary hidden_dims param_budget settle_horizon \
      --base-config geometry=feedforward,dynamics=instantaneous,credit=gradient,update=euclidean \
      --budget 1h --seeds 5
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.pipeline import PipelineConfig, PipelineRunner
from computronium.experiment.execution.search_space import search_space_from_spec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec

if TYPE_CHECKING:
    from computronium.experiment.execution.policy import Policy


@dataclass(frozen=True, slots=True)
class ScalingSpec:
    """Specification for a scaling experiment.

    Args:
        vary: List of parameter names to sweep (e.g., ["hidden_dims", "param_budget", "settle_horizon"]).
        log_scale: Whether to use logarithmic spacing for numeric parameters.
        n_points_per_dim: Number of values per parameter dimension.
        base_config: Base coordinate with fixed axes.
        n_seeds: Number of seeds per configuration.
        budget_seconds: Total time budget.
        metric: Primary metric for analysis.
        task: Task to run scaling on.
    """

    vary: list[str] = field(
        default_factory=lambda: ["hidden_dims", "param_budget", "settle_horizon"]
    )
    log_scale: bool = True
    n_points_per_dim: int = 4
    base_config: Coordinate | None = None
    n_seeds: int = 5
    budget_seconds: float = 3600
    metric: str = "validation_accuracy"
    task: str | None = None


@dataclass(slots=True)
class ScalingResult:
    """Results of a scaling experiment."""

    vary_params: list[str]
    configurations: list[dict[str, Any]]  # Per-parameter combination results with stats
    walltime_s: float


# Default ranges for scaling parameters
_DEFAULT_RANGES: dict[str, tuple[float, float]] = {
    "hidden_dims": (16, 512),
    "param_budget": (1000, 100000),
    "settle_horizon": (1, 50),
    "num_layers": (1, 8),
    "max_steps": (3, 100),
    "beta": (0.1, 2.0),
}


class ScalingRunner:
    """Runs scaling experiments sweeping architectural/dynamical parameters.

    For each combination of the varied parameters, runs `n_seeds` evaluations
    with all other axes fixed to the base_config. Aggregates results with mean/std.
    """

    def __init__(
        self,
        spec: ScalingSpec,
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
        self.run_id = f"scaling_{int(time.time())}"

    def _generate_parameter_grid(self) -> list[dict[str, Any]]:
        """Generate the grid of parameter values to sweep."""
        import math

        grid = [{}]
        for param in self.spec.vary:
            lo, hi = _DEFAULT_RANGES.get(param, (1, 10))
            if self.spec.log_scale:
                values = [
                    lo * (hi / lo) ** (i / (self.spec.n_points_per_dim - 1))
                    for i in range(self.spec.n_points_per_dim)
                ]
                if param in {"hidden_dims", "param_budget", "num_layers", "max_steps", "settle_horizon"}:
                    values = [int(round(v)) for v in values]
            else:
                values = [
                    lo + (hi - lo) * i / (self.spec.n_points_per_dim - 1)
                    for i in range(self.spec.n_points_per_dim)
                ]
                if param in {"hidden_dims", "param_budget", "num_layers", "max_steps", "settle_horizon"}:
                    values = [int(round(v)) for v in values]

            new_grid = []
            for g in grid:
                for v in values:
                    new_g = g.copy()
                    new_g[param] = v
                    new_grid.append(new_g)
            grid = new_grid
        return grid

    def _build_run_spec(self, param_values: dict[str, Any]) -> RunSpec:
        """Build a RunSpec with the given parameter values."""
        from computronium.experiment.schema.axis import AXES_REGISTRIES

        # Determine fixed axes from base_config
        fixed_axes: dict[StructuralAxis, str] = {}
        if self.spec.base_config:
            for axis in StructuralAxis:
                val = getattr(self.spec.base_config, axis.value, None)
                if val is not None:
                    fixed_axes[axis] = val

        # Build axis selections
        axes: list[AxisSelection] = []
        for axis in StructuralAxis:
            if axis in fixed_axes:
                axes.append(AxisSelection(axis=axis, primitives=(fixed_axes[axis],)))
            else:
                registry = AXES_REGISTRIES[axis]
                primitives = tuple(
                    sorted(n for n, s in registry.items() if s.available)
                )
                axes.append(
                    AxisSelection(axis=axis, primitives=primitives if primitives else None)
                )

        task = self.spec.task or "digits"
        param_budget = param_values.get("param_budget", 10000)

        return RunSpec(
            profile=f"scaling_{'_'.join(self.spec.vary)}",
            task=task,
            tasks=(),
            objectives=(self.spec.metric, "walltime_total"),
            fidelity="L1",
            n_seeds=self.spec.n_seeds,
            epochs=1,
            batch_limit=2,
            budget_seconds=self.spec.budget_seconds,
            param_budget=param_budget,
            axes=tuple(axes),
            seed=0,
            device="auto",
        )

    def _build_coordinate_with_params(
        self, base_coord: Coordinate, param_values: dict[str, Any]
    ) -> Coordinate:
        """Create a coordinate with the scaling parameters applied."""
        params = dict(base_coord.params)
        params.update(param_values)
        return Coordinate(
            substrate=base_coord.substrate,
            geometry=base_coord.geometry,
            dynamics=base_coord.dynamics,
            plasticity=base_coord.plasticity,
            credit=base_coord.credit,
            update=base_coord.update,
            params=params,
        )

    async def run(self) -> ScalingResult:
        """Execute the scaling experiment."""
        start_time = time.monotonic()

        # Generate parameter grid
        param_grid = self._generate_parameter_grid()

        # Build base coordinate
        if self.spec.base_config is None:
            base_coord = Coordinate(
                substrate="digital",
                geometry="feedforward",
                dynamics="instantaneous",
                plasticity="null",
                credit="gradient",
                update="euclidean",
                params={},
            )
        else:
            base_coord = self.spec.base_config

        results = []

        # Open store once for the entire scaling run
        with self.store:
            for i, param_values in enumerate(param_grid):
                # Build coordinate with these parameters
                coord = self._build_coordinate_with_params(base_coord, param_values)

                # Build RunSpec
                run_spec = self._build_run_spec(param_values)
                variant_run_id = f"{self.run_id}_variant_{i}"

                # Register the run
                self.store.create_run(run_id=variant_run_id, spec=run_spec)

                runner = PipelineRunner(
                    config=PipelineConfig(
                        run_id=variant_run_id,
                        run_spec=run_spec,
                        deadline=Deadline.from_seconds(self.spec.budget_seconds),
                        backend=self.backend,
                        policy=self.policy,
                    ),
                    store=self.store,
                )

                try:
                    records = await runner.run()
                    aggregated = self._aggregate_records(records, param_values)
                    results.append(aggregated)
                except Exception as e:
                    results.append({
                        "params": param_values,
                        "error": str(e),
                        "mean": None,
                        "std": None,
                        "n_seeds": 0,
                    })

        walltime_s = time.monotonic() - start_time

        return ScalingResult(
            vary_params=self.spec.vary,
            configurations=results,
            walltime_s=walltime_s,
        )

    def _aggregate_records(
        self, records: list, param_values: dict[str, Any]
    ) -> dict[str, Any]:
        """Aggregate records across seeds for one parameter combination."""
        if not records:
            return {
                "params": param_values,
                "mean": None,
                "std": None,
                "n_seeds": 0,
            }

        from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

        obj_spec = OBJECTIVES_REGISTRY.get(self.spec.metric)
        payload_key = (
            obj_spec.metric_key
            if obj_spec and obj_spec.metric_key
            else self.spec.metric
        )

        values = []
        for record in records:
            val = record.payload.get(payload_key)
            if val is not None:
                values.append(float(val))

        if not values:
            return {
                "params": param_values,
                "mean": None,
                "std": None,
                "n_seeds": len(records),
            }

        import statistics

        return {
            "params": param_values,
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "n_seeds": len(values),
            "raw_values": values,
        }

    def print_results(self, result: ScalingResult) -> None:
        """Pretty-print scaling results."""
        print(f"\n{'=' * 80}")
        print(f"Scaling Results: {', '.join(result.vary_params)}")
        print(f"{'=' * 80}")
        print(f"Total configurations: {len(result.configurations)}")
        print(f"Walltime: {result.walltime_s:.1f}s")
        print(f"{'-' * 80}")

        # Print header
        param_names = result.vary_params
        header = " | ".join(f"{p:>12}" for p in param_names) + " |  Mean      Std       N"
        print(header)
        print(f"{'-' * 80}")

        for config in result.configurations:
            params = config["params"]
            mean = config["mean"]
            std = config["std"]
            n = config["n_seeds"]

            param_str = " | ".join(f"{params.get(p, 'N/A'):>12}" for p in param_names)
            if mean is not None:
                print(f"{param_str} | {mean:>8.4f} {std:>8.4f} {n:>4}")
            else:
                print(f"{param_str} | {'ERROR':>8} {'N/A':>8} {n:>4}")

        print(f"{'=' * 80}")


# CLI entry point
async def _run_scaling_cli(
    vary: list[str],
    base_config: dict[str, str],
    budget: float,
    seeds: int,
    metric: str,
    task: str | None,
    log_scale: bool,
    n_points: int,
) -> ScalingResult:
    """Run scaling from CLI arguments."""
    from computronium.experiment.schema.axis import StructuralAxis

    base_coord = None
    if base_config:
        base_coord = Coordinate(
            substrate=base_config.get("substrate", "digital"),
            geometry=base_config.get("geometry", "feedforward"),
            dynamics=base_config.get("dynamics", "instantaneous"),
            plasticity=base_config.get("plasticity", "null"),
            credit=base_config.get("credit", "gradient"),
            update=base_config.get("update", "euclidean"),
            params={},
        )

    spec = ScalingSpec(
        vary=vary,
        log_scale=log_scale,
        n_points_per_dim=n_points,
        base_config=base_coord,
        n_seeds=seeds,
        budget_seconds=budget,
        metric=metric,
        task=task,
    )

    runner = ScalingRunner(spec)
    result = await runner.run()
    runner.print_results(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run scaling experiment")
    parser.add_argument(
        "--vary", action="append", default=[], help="Parameters to sweep"
    )
    parser.add_argument(
        "--base-config", action="append", default=[], help="Base config axis=value pairs"
    )
    parser.add_argument("--budget", type=float, default=3600, help="Budget in seconds")
    parser.add_argument("--seeds", type=int, default=5, help="Seeds per configuration")
    parser.add_argument(
        "--metric", default="validation_accuracy", help="Primary metric"
    )
    parser.add_argument("--task", help="Task name")
    parser.add_argument("--log-scale", action="store_true", default=True, help="Log scale")
    parser.add_argument(
        "--linear-scale", action="store_false", dest="log_scale", help="Linear scale"
    )
    parser.add_argument(
        "--n-points", type=int, default=4, help="Points per dimension"
    )

    args = parser.parse_args()

    base_config_dict = {}
    for pair in args.base_config:
        if "=" in pair:
            k, v = pair.split("=", 1)
            base_config_dict[k] = v

    vary_params = args.vary if args.vary else ["hidden_dims", "param_budget", "settle_horizon"]

    asyncio.run(
        _run_scaling_cli(
            vary=vary_params,
            base_config=base_config_dict,
            budget=args.budget,
            seeds=args.seeds,
            metric=args.metric,
            task=args.task,
            log_scale=args.log_scale,
            n_points=args.n_points,
        )
    )