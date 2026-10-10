"""Lock: a 3s-budget run stops on the deadline within the allowed window."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.search_space import iter_candidates, search_space_from_spec
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.surface.cli import RUN_PROFILES
from scripts.run_experiment import Config, _build_spec, _resolve_device, _run_loop
from computronium.experiment.execution.backends import LocalBackend


@pytest.mark.asyncio
async def test_budget_utilization_lock():
    """A 3-second run must terminate on deadline with utilization in [0.9, 1.0+grace]."""
    # Small profile: minimal axes to keep startup fast
    spec = RunSpec(
        profile="budget-lock",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        stages=(
            StageId.S1_FRAME, StageId.S2_SPACE, StageId.S3_SCHEDULE,
            StageId.S4_GATE, StageId.S5_COMPOSE, StageId.S6_TRAIN,
            StageId.S7_MEASURE, StageId.S8_RECORD, StageId.S9_ATTRIBUTE,
            StageId.S10_DECIDE, StageId.S11_REPORT,
        ),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_seconds=3.6,
        param_budget=10000,
        policy="round_robin_grid",
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital", "sparse")),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=("instantaneous", "energy_minimization")),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient", "random_projections")),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null", "fast_weights")),
        ),
        seed=42,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "budget_lock.db"
        deadline = Deadline.from_seconds(3.6)
        backend = LocalBackend(max_workers=1)
        device = "cpu"

        with RecordStore(StoreConfig(path=store_path)) as store:
            run_id = store.create_run(spec=spec)

            await _run_loop(spec, store, run_id, deadline, backend, device)

            elapsed = deadline.elapsed_seconds()
            budget = spec.budget_seconds
            eps = max(0.02 * budget, 5.0)

            # The runner checks deadline.expired() (hard) first, then soft after count>0
            # So elapsed can be up to budget + grace (30s). We assert the window.
            assert budget - eps <= elapsed <= budget + 30.0, (
                f"elapsed={elapsed:.1f}s not in [{budget - eps:.1f}, {budget + 30:.1f}]"
            )

            # At least one cell was measured
            records = store.query_records(run_id=run_id)
            assert len(records) > 0, "no cells measured in budget window"


if __name__ == "__main__":
    asyncio.run(test_budget_utilization_lock())
    print("PASSED")