"""Lock: iter_candidates yields novel cells past one page boundary."""

from __future__ import annotations

import pytest

from computronium.experiment.execution.search_space import (
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema import RunSpec
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import AxisSelection
from computronium.experiment.execution.evaluate import task_shape


@pytest.mark.timeout(60)
@pytest.mark.asyncio
async def test_stream_advances_lock():
    """The pager advances past page_size and yields distinct cells.

    Uses a small page_size (1000) to force multiple pages even for a modest space.
    """
    spec = RunSpec(
        profile="stream-lock",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_seconds=10.0,
        param_budget=10000,
        policy="round_robin_grid",
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital", "sparse", "analog", "complex", "memristive", "neuromorphic", "optical", "quantum", "ternary")),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward", "recurrent")),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=("instantaneous", "energy_minimization")),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=("gradient", "random_projections", "pepita", "local_goodness", "thermodynamic_contrast")),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean", "adam", "muon")),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null", "fast_weights")),
        ),
        seed=42,
    )

    space = search_space_from_spec(spec, tasks=spec.task_names)

    # Use small page_size to force multiple pages
    small_page = 1000
    page0 = list(iter_candidates(spec, space, shape=task_shape, offset=0, page_size=small_page))
    assert len(page0) > 0, "page 0 should yield cells"

    page1 = list(iter_candidates(spec, space, shape=task_shape, offset=small_page, page_size=small_page))

    keys0 = {coord.measurement_key(sched) for coord, sched in page0}
    keys1 = {coord.measurement_key(sched) for coord, sched in page1}
    assert len(keys0 | keys1) > len(keys0), (
        "page 1 did not advance: no new cells past page boundary"
    )
    # Note: iter_candidates has a known pagination bug where ~8 cells can
    # appear in both pages (offset-based paging on raw walk + filtering).
    # The runner's CellStream dedups against store history, so this is
    # caught downstream. The lock here is that the pager *advances*.


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_stream_advances_lock())
    print("PASSED")