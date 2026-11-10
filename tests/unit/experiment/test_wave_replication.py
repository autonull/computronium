"""The seed plan is the replication unit: N seeds yield N records.

Claim eligibility reads achieved seeds, so a schedule that declares three seeds
must reach the evaluator as three single-seed schedules. Before this lock, the
survey evaluated the declared schedule once and wrote one record labelled
``n_seeds=3`` — a replication the store never held.
"""

from __future__ import annotations

from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.wave import _expand_replicates


def _coordinate() -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params={},
    )


def _schedule(n_seeds: int) -> Schedule:
    return Schedule(
        fidelity="L1",
        seed=42,
        n_seeds=n_seeds,
        epochs=5,
        batch_limit=0,
        budget_id="L1_initial",
        task_id="xor",
    )


def test_seed_plan_expands_to_one_cell_per_seed():
    cells = _expand_replicates([(_coordinate(), _schedule(3))])

    assert [schedule.seed for _coordinate, schedule in cells] == [42, 43, 44]
    assert all(schedule.n_seeds == 1 for _coordinate, schedule in cells)


def test_single_seed_schedule_is_unchanged():
    coordinate = _coordinate()
    schedule = _schedule(1)

    assert _expand_replicates([(coordinate, schedule)]) == [(coordinate, schedule)]
