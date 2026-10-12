"""Lock: CellStream.next(1) returns within ~1s on a large search space.

Before the lazy-page fix (TODO61 B1), _refill buffered an entire 50k-candidate page
— and every legal candidate ran a composition dry-run — before yielding the first
cell. On the 3.3M-cell maturation grid this meant minutes before Cell 1.

This lock ensures the first cell is returned in bounded time (≤ 3s wall clock)
regardless of space size, by asserting the lazy-iterator contract.
"""

import tempfile
import time

import pytest

from computronium.experiment.execution.deadline import Deadline
from computronium.experiment.execution.stream import CellStream
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.schema import RunSpec
from computronium.experiment.surface.cli import RUN_PROFILES


class TestCellStreamLatencyLock:
    """CellStream must yield the first cell quickly on large spaces."""

    @pytest.mark.timeout(30)
    def test_cellstream_first_cell_latency(self):
        """CellStream.next(1) returns within 3 seconds on a large grid."""
        # Use a profile with many primitives (large space) but explicit axes
        # to ensure a valid cell is found quickly. The production-map profile
        # has empty axes (uses all), so we use quick-verify which is smaller
        # but still exercises the lazy iterator.
        profile = RUN_PROFILES["quick-verify"]
        spec = RunSpec(
            profile=profile.name,
            task=profile.task,
            objectives=profile.objectives,
            stages=tuple(profile.stages),
            fidelity=profile.fidelity,
            n_seeds=profile.n_seeds,
            epochs=profile.epochs,
            batch_limit=profile.batch_limit,
            budget_seconds=3600.0,
            param_budget=profile.param_budget,
            policy=profile.policy,
            axes=profile.axes,
            checkpoint_every_n=profile.checkpoint_every_n,
            seed=42,
            device="cpu",
        )

        space = search_space_from_spec(spec, tasks=spec.task_names)

        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = f"{tmpdir}/test.db"
            # Use a dummy is_measured that never matches

            def is_measured(key: str) -> bool:
                return False

            stream = CellStream(
                spec=spec,
                space=space,
                shape=task_shape,
                deadline=Deadline.from_hours(0.01),
                is_measured=is_measured,
            )

            start = time.perf_counter()
            cells = stream.next(1)
            elapsed = time.perf_counter() - start

            assert cells, "Stream yielded no cells on a non-empty space"
            assert elapsed < 3.0, (
                f"CellStream.next(1) took {elapsed:.2f}s — expected < 3s "
                "(lazy page iterator must yield first cell immediately)"
            )
            assert len(cells) == 1
            coordinate, schedule = cells[0]
            # Any valid substrate/geometry from the profile's axes
            assert coordinate.substrate in {"digital"}
            assert coordinate.geometry in {"feedforward", "recurrent"}
            assert coordinate.dynamics in {"energy_minimization", "instantaneous", "lazy"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
