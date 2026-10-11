"""Lock: the admission gate (composability screen) rejects invalid combos before they reach the backend."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.execution.stage import StageId
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from scripts.run_experiment import _run_loop
from computronium.experiment.execution.backends import LocalBackend


@pytest.mark.asyncio
async def test_admission_gate_lock():
    """A known-invalid combo (recurrent + instantaneous + gradient) is screened by iter_candidates and never reaches the backend."""
    # This spec declares the exact combo that _composable rejects:
    # recurrent geometry + instantaneous dynamics + gradient credit
    spec = RunSpec(
        profile="admission-lock",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        stages=(
            StageId.S1_FRAME,
            StageId.S2_SPACE,
            StageId.S3_SCHEDULE,
            StageId.S4_GATE,
            StageId.S5_COMPOSE,
            StageId.S6_TRAIN,
            StageId.S7_MEASURE,
            StageId.S8_RECORD,
            StageId.S9_ATTRIBUTE,
            StageId.S10_DECIDE,
            StageId.S11_REPORT,
        ),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_seconds=10.0,
        param_budget=10000,
        policy="round_robin_grid",
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("recurrent",)),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=("instantaneous",)),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient",)),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
        ),
        seed=42,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = Path(tmpdir) / "admission_lock.db"
        deadline = Deadline.from_seconds(10.0)
        backend = LocalBackend(max_workers=1)
        device = "cpu"

        with RecordStore(StoreConfig(path=store_path)) as store:
            run_id = store.create_run(spec=spec)

            # The iter_candidates walker screens via _composable which calls SystemConfig.validate
            # The invalid combo (recurrent + instantaneous + gradient) is filtered out
            # So the runner should measure 0 cells
            await _run_loop(spec, store, run_id, deadline, backend, device)

            records = store.query_records(run_id=run_id)
            assert len(records) == 0, (
                f"admission gate failed: {len(records)} cell(s) measured for invalid combo "
                "that _composable should reject"
            )


if __name__ == "__main__":
    asyncio.run(test_admission_gate_lock())
    print("PASSED")
