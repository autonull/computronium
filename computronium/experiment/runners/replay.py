"""Replay Runner: regression testing from previous experiment database.

Re-runs known-good cells from a previous experiment database and checks
for metric regression beyond a tolerance threshold.

Usage:
    uv run python -m computronium.experiment.runners.replay \
      --source-db experiments/previous_run.db \
      --check-metrics validation_accuracy,walltime_total \
      --tolerance 0.02
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.backends import LocalBackend
from computronium.experiment.schema.coordinate import Coordinate

if TYPE_CHECKING:
    from computronium.experiment.execution.policy import Policy


@dataclass(frozen=True, slots=True)
class ReplaySpec:
    """Specification for a replay/regression experiment.

    Args:
        source_db: Path to the source experiment database.
        check_metrics: List of metrics to check for regression.
        tolerance: Relative tolerance for regression (e.g., 0.02 = 2%).
        budget_seconds: Total time budget for replay.
        task: Task to run replay on (defaults to tasks in source DB).
        filter_status: Only replay cells with this status (measured, void, failed).
    """

    source_db: str
    check_metrics: list[str] = field(
        default_factory=lambda: ["validation_accuracy", "walltime_total"]
    )
    tolerance: float = 0.02
    budget_seconds: float = 3600
    task: str | None = None
    filter_status: str = "measured"


@dataclass(slots=True)
class ReplayResult:
    """Results of a replay experiment."""

    total_cells: int
    regressed: list[dict[str, Any]]
    improved: list[dict[str, Any]]
    stable: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    walltime_s: float


class ReplayRunner:
    """Replays cells from a previous experiment database for regression testing."""

    def __init__(
        self,
        spec: ReplaySpec,
        *,
        store: RecordStore | None = None,
        backend: LocalBackend | None = None,
        policy: Policy | None = None,
        checkpoint_dir: str | None = None,
    ) -> None:
        self.spec = spec
        self.store = store or RecordStore(StoreConfig(path=Path(":memory:")))
        self.backend = backend or LocalBackend(max_workers=4)
        self.policy = policy
        self.checkpoint_dir = checkpoint_dir

        self.run_id = f"replay_{int(time.time())}"
        self._source_store: RecordStore | None = None

    def _connect_source(self) -> RecordStore:
        """Connect to the source database."""
        if self._source_store is None:
            self._source_store = RecordStore(
                StoreConfig(path=Path(self.spec.source_db), read_only=True)
            )
        return self._source_store

    async def run(self) -> ReplayResult:
        """Execute the replay experiment."""
        start_time = time.monotonic()

        # Load source records
        source_store = self._connect_source()
        source_records = list(source_store.query_records())

        # Filter by status
        filtered_records = [
            r
            for r in source_records
            if r.status.gate_verdict.value == "PASS"  # Only successful cells
        ]

        if self.spec.task:
            filtered_records = [
                r for r in filtered_records if r.schedule.task_id == self.spec.task
            ]

        results = {
            "regressed": [],
            "improved": [],
            "stable": [],
            "errors": [],
        }

        # Replay each cell
        for record in filtered_records:
            try:
                # Reconstruct coordinate from record fields
                coordinate = Coordinate(
                    substrate=record.substrate,
                    geometry=record.geometry,
                    dynamics=record.dynamics,
                    plasticity=record.plasticity,
                    credit=record.credit,
                    update=record.update,
                    params=record.params,
                )
                result = await self._replay_cell(record, coordinate)
                results[result["category"]].append(result)
            except Exception as e:
                results["errors"].append({
                    "cell_key": record.cell_key[:12],
                    "error": str(e),
                })

        walltime_s = time.monotonic() - start_time

        return ReplayResult(
            total_cells=len(filtered_records),
            regressed=results["regressed"],
            improved=results["improved"],
            stable=results["stable"],
            errors=results["errors"],
            walltime_s=walltime_s,
        )

    async def _replay_cell(self, record, coordinate: Coordinate) -> dict[str, Any]:
        """Replay a single cell from the source database."""
        from computronium.experiment.execution.evaluate import evaluate_cell

        schedule = record.schedule

        # Update schedule with current run_id and budget
        from dataclasses import replace

        new_schedule = replace(schedule, budget_id=self.run_id)

        # Evaluate the cell
        evaluation = evaluate_cell(
            coordinate=coordinate,
            schedule=new_schedule,
            geometry=None,
            checkpoint_dir=self.checkpoint_dir,
        )

        # Compare metrics
        current_metrics = evaluation.metrics
        original_metrics = record.payload

        regressed_metrics = []
        improved_metrics = []
        stable_metrics = []

        for metric in self.spec.check_metrics:
            current_val = current_metrics.get(metric)
            original_val = original_metrics.get(metric)

            if current_val is None or original_val is None:
                continue

            current_val = float(current_val)
            original_val = float(original_val)

            if original_val == 0:
                continue

            relative_change = (current_val - original_val) / abs(original_val)

            if relative_change < -self.spec.tolerance:
                regressed_metrics.append({
                    "metric": metric,
                    "original": original_val,
                    "current": current_val,
                    "change": relative_change,
                })
            elif relative_change > self.spec.tolerance:
                improved_metrics.append({
                    "metric": metric,
                    "original": original_val,
                    "current": current_val,
                    "change": relative_change,
                })
            else:
                stable_metrics.append({
                    "metric": metric,
                    "original": original_val,
                    "current": current_val,
                    "change": relative_change,
                })

        # Categorize
        if regressed_metrics:
            category = "regressed"
        elif improved_metrics:
            category = "improved"
        else:
            category = "stable"

        return {
            "cell_key": coordinate.cell_key()[:12],
            "coordinate": coordinate.to_dict(),
            "category": category,
            "regressed": regressed_metrics,
            "improved": improved_metrics,
            "stable": stable_metrics,
        }

    def print_results(self, result: ReplayResult) -> None:
        """Pretty-print replay results."""
        print(f"\n{'=' * 60}")
        print("Replay Regression Results")
        print(f"{'=' * 60}")
        print(f"Total cells replayed: {result.total_cells}")
        print(f"Regressed: {len(result.regressed)}")
        print(f"Improved: {len(result.improved)}")
        print(f"Stable: {len(result.stable)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Walltime: {result.walltime_s:.1f}s")
        print(f"{'-' * 60}")

        if result.regressed:
            print("REGRESSED:")
            for r in result.regressed:
                print(f"  {r['cell_key']}:")
                for m in r["regressed"]:
                    print(
                        f"    {m['metric']}: {m['original']:.4f} -> {m['current']:.4f} ({m['change'] * 100:+.1f}%)"
                    )

        if result.improved:
            print("IMPROVED:")
            for r in result.improved:
                print(f"  {r['cell_key']}:")
                for m in r["improved"]:
                    print(
                        f"    {m['metric']}: {m['original']:.4f} -> {m['current']:.4f} ({m['change'] * 100:+.1f}%)"
                    )

        if result.errors:
            print("ERRORS:")
            for e in result.errors:
                print(f"  {e['cell_key']}: {e['error']}")

        print(f"{'=' * 60}")


async def _run_replay_cli(
    source_db: str,
    check_metrics: list[str],
    tolerance: float,
    budget: float,
    task: str | None,
) -> ReplayResult:
    """Run replay from CLI arguments."""
    spec = ReplaySpec(
        source_db=source_db,
        check_metrics=check_metrics,
        tolerance=tolerance,
        budget_seconds=budget,
        task=task,
    )

    runner = ReplayRunner(spec)
    result = await runner.run()
    runner.print_results(result)
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run replay/regression experiment")
    parser.add_argument(
        "--source-db", required=True, help="Source experiment database path"
    )
    parser.add_argument(
        "--check-metrics",
        default="validation_accuracy,walltime_total",
        help="Comma-separated metrics",
    )
    parser.add_argument(
        "--tolerance", type=float, default=0.02, help="Regression tolerance (relative)"
    )
    parser.add_argument("--budget", type=float, default=3600, help="Budget in seconds")
    parser.add_argument("--task", help="Task name")

    args = parser.parse_args()

    check_metrics = [m.strip() for m in args.check_metrics.split(",")]

    asyncio.run(
        _run_replay_cli(
            source_db=args.source_db,
            check_metrics=check_metrics,
            tolerance=args.tolerance,
            budget=args.budget,
            task=args.task,
        )
    )
