"""Comparison Runner: A/B testing with statistical significance.

Compares two configurations (arms) with multiple seeds each, using
statistical tests (Mann-Whitney U, t-test, bootstrap) to determine
significance of differences.

Usage:
    uv run python -m computronium.experiment.runners.comparison \
      --arm-a geometry=feedforward,dynamics=instantaneous,credit=gradient \
      --arm-b geometry=recurrent,dynamics=energy_minimization,credit=thermodynamic_contrast \
      --seeds 10 --metric validation_accuracy
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
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec

if TYPE_CHECKING:
    from computronium.experiment.execution.policy import Policy


@dataclass(frozen=True, slots=True)
class ComparisonSpec:
    """Specification for a comparison (A/B) experiment.

    Args:
        arm_a: Coordinate for arm A (dict of axis -> primitive).
        arm_b: Coordinate for arm B (dict of axis -> primitive).
        n_seeds: Number of seeds per arm for statistical rigor.
        budget_seconds: Total time budget.
        metric: Primary metric for comparison.
        test: Statistical test ("mann_whitney_u", "t_test", "bootstrap").
        task: Task to run comparison on.
        base_config: Optional base RunSpec to derive from.
    """

    arm_a: dict[StructuralAxis, str]
    arm_b: dict[StructuralAxis, str]
    n_seeds: int = 10
    budget_seconds: float = 3600
    metric: str = "validation_accuracy"
    test: str = "mann_whitney_u"
    task: str | None = None
    base_config: RunSpec | None = None


@dataclass(slots=True)
class ComparisonResult:
    """Results of a comparison experiment."""

    arm_a_results: dict[str, Any]
    arm_b_results: dict[str, Any]
    p_value: float
    significant: bool
    test_used: str
    walltime_s: float


class ComparisonRunner:
    """Runs A/B comparison experiments with statistical testing."""

    def __init__(
        self,
        spec: ComparisonSpec,
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
            self.base_spec = self._build_base_spec()

        self.run_id = f"comparison_{int(time.time())}"

    def _build_base_spec(self) -> RunSpec:
        """Build a RunSpec from the comparison specification."""

        task = self.spec.task or "digits"

        axes: list[AxisSelection] = []
        for axis in StructuralAxis:
            if axis in self.spec.arm_a or axis in self.spec.arm_b:
                # Use the union of primitives from both arms
                primitives = set()
                if axis in self.spec.arm_a:
                    primitives.add(self.spec.arm_a[axis])
                if axis in self.spec.arm_b:
                    primitives.add(self.spec.arm_b[axis])
                axes.append(
                    AxisSelection(axis=axis, primitives=tuple(sorted(primitives)))
                )
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
            profile="comparison",
            task=task,
            tasks=(),
            objectives=(self.spec.metric, "walltime_total"),
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

    async def run(self) -> ComparisonResult:
        """Execute the comparison experiment."""
        start_time = time.monotonic()

        # Open store once for the entire comparison
        with self.store:
            # Run arm A
            arm_a_spec = self._build_arm_spec("A", self.spec.arm_a)
            arm_a_result = await self._run_arm("A", arm_a_spec)

            # Run arm B
            arm_b_spec = self._build_arm_spec("B", self.spec.arm_b)
            arm_b_result = await self._run_arm("B", arm_b_spec)

        # Statistical test
        p_value = self._statistical_test(
            arm_a_result["raw_values"],
            arm_b_result["raw_values"],
            self.spec.test,
        )
        significant = p_value < 0.05

        walltime_s = time.monotonic() - start_time

        return ComparisonResult(
            arm_a_results=arm_a_result,
            arm_b_results=arm_b_result,
            p_value=p_value,
            significant=significant,
            test_used=self.spec.test,
            walltime_s=walltime_s,
        )

    def _build_arm_spec(
        self, arm_name: str, arm_config: dict[StructuralAxis, str]
    ) -> RunSpec:
        """Build a RunSpec for one arm."""
        axes: list[AxisSelection] = []
        for axis in StructuralAxis:
            if axis in arm_config:
                axes.append(AxisSelection(axis=axis, primitives=(arm_config[axis],)))
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
            profile=f"comparison_arm_{arm_name}",
            task=self.base_spec.task_names[0],
            tasks=(),
            objectives=(self.spec.metric, "walltime_total"),
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

    async def _run_arm(self, arm_name: str, spec: RunSpec) -> dict[str, Any]:
        """Run one arm of the comparison."""
        run_id = f"{self.run_id}_arm_{arm_name}"
        # Store is already open from run()
        self.store.create_run(run_id=run_id, spec=spec)
        runner = PipelineRunner(
            config=PipelineConfig(
                run_id=run_id,
                run_spec=spec,
                deadline=Deadline.from_seconds(self.spec.budget_seconds),
                backend=self.backend,
                policy=self.policy,
            ),
            store=self.store,
        )

        records = await runner.run()
        return self._aggregate_records(records)

    def _aggregate_records(self, records: list) -> dict[str, Any]:
        """Aggregate records across seeds for one arm."""
        if not records:
            return {
                "mean": None,
                "std": None,
                "n_seeds": 0,
                "raw_values": [],
            }

        # Map objective name to payload key
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
                "mean": None,
                "std": None,
                "n_seeds": len(records),
                "raw_values": [],
            }

        import statistics

        return {
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "n_seeds": len(values),
            "raw_values": values,
        }

    def _statistical_test(
        self, values_a: list[float], values_b: list[float], test: str
    ) -> float:
        """Run statistical test and return p-value."""
        if not values_a or not values_b:
            return 1.0

        if test == "mann_whitney_u":
            from scipy import stats

            _, p = stats.mannwhitneyu(values_a, values_b, alternative="two-sided")
            return float(p)
        elif test == "t_test":
            from scipy import stats

            _, p = stats.ttest_ind(values_a, values_b)
            return float(p)
        elif test == "bootstrap":
            return self._bootstrap_test(values_a, values_b)
        else:
            raise ValueError(f"Unknown test: {test}")

    def _bootstrap_test(
        self, values_a: list[float], values_b: list[float], n_iter: int = 10000
    ) -> float:
        """Bootstrap test for difference in means."""
        import numpy as np

        observed_diff = np.mean(values_a) - np.mean(values_b)
        pooled = np.concatenate([values_a, values_b])
        n_a = len(values_a)

        count = 0
        for _ in range(n_iter):
            np.random.shuffle(pooled)
            diff = np.mean(pooled[:n_a]) - np.mean(pooled[n_a:])
            if abs(diff) >= abs(observed_diff):
                count += 1

        return count / n_iter

    def print_results(self, result: ComparisonResult) -> None:
        """Pretty-print comparison results."""
        a = result.arm_a_results
        b = result.arm_b_results

        print(f"\n{'=' * 60}")
        print("Comparison Results (A vs B)")
        print(f"{'=' * 60}")
        print(f"Arm A: mean={a['mean']:.4f}, std={a['std']:.4f}, n={a['n_seeds']}")
        print(f"Arm B: mean={b['mean']:.4f}, std={b['std']:.4f}, n={b['n_seeds']}")
        print(f"Test: {result.test_used}")
        print(f"P-value: {result.p_value:.6f}")
        print(f"Significant (p<0.05): {'YES' if result.significant else 'NO'}")
        print(f"Walltime: {result.walltime_s:.1f}s")
        print(f"{'=' * 60}")


async def _run_comparison_cli(
    arm_a: dict[StructuralAxis, str],
    arm_b: dict[StructuralAxis, str],
    seeds: int,
    budget: float,
    metric: str,
    test: str,
    task: str | None,
) -> ComparisonResult:
    """Run comparison from CLI arguments."""
    spec = ComparisonSpec(
        arm_a=arm_a,
        arm_b=arm_b,
        n_seeds=seeds,
        budget_seconds=budget,
        metric=metric,
        test=test,
        task=task,
    )

    runner = ComparisonRunner(spec)
    result = await runner.run()
    runner.print_results(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run comparison experiment")
    parser.add_argument("--arm-a", required=True, help="Arm A config (axis=value,...)")
    parser.add_argument("--arm-b", required=True, help="Arm B config (axis=value,...)")
    parser.add_argument("--seeds", type=int, default=10, help="Seeds per arm")
    parser.add_argument("--budget", type=float, default=3600, help="Budget in seconds")
    parser.add_argument(
        "--metric", default="validation_accuracy", help="Primary metric"
    )
    parser.add_argument(
        "--test",
        default="mann_whitney_u",
        choices=["mann_whitney_u", "t_test", "bootstrap"],
    )
    parser.add_argument("--task", help="Task name")

    args = parser.parse_args()

    def parse_arm(s: str) -> dict[StructuralAxis, str]:
        result = {}
        for pair in s.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                result[StructuralAxis(k)] = v
        return result

    arm_a = parse_arm(args.arm_a)
    arm_b = parse_arm(args.arm_b)

    asyncio.run(
        _run_comparison_cli(
            arm_a=arm_a,
            arm_b=arm_b,
            seeds=args.seeds,
            budget=args.budget,
            metric=args.metric,
            test=args.test,
            task=args.task,
        )
    )
