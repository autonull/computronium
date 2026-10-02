"""The promotion stage: maturity is a measurement, not a default (TODO48 Q2, E4).

Every record is written with ``maturity=L0``. Two writes are earned, in order:

- **L1 — eligibility.** A cell that achieved the spec's seed count at its
  declared fidelity with a ``PASS`` gate. This is arithmetic on the store, not
  a judgment.
- **L2 — replay.** The eligible cell re-measured through the replay path (the
  evaluator, same coordinate and schedule) reproduces its claimed metrics
  within the registered tolerance. This is the maturity ladder's first rung
  that means *independently reproducible*.

``promoted``, ``filter_promoted`` and the report's promotion-history section
read ``status.maturity`` — after this stage they are measurements.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from computronium.experiment.evidence.claims import replication_key
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.record import (
    Maturity,
    ReproducibilityClass,
)

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import RunSpec

logger = logging.getLogger(__name__)


def _claimed_metrics(record: Record) -> dict[str, float]:
    """The record's task-axis metrics — what a claim states and replay checks.

    Cost metrics (walltime, memory) are properties of the machine that ran the
    cell, not of the claim: a replay on different hardware can never reproduce
    them, so gating them would make every promotion a false negative.
    """
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    metric_keys = {
        objective.metric_key
        for objective in OBJECTIVES_REGISTRY.values()
        if objective.axis_tag == "task" and objective.metric_key is not None
    }
    return {
        key: float(value)
        for key, value in record.payload.items()
        if key in metric_keys
        and isinstance(value, (int, float))
        and not isinstance(value, bool)
    }


def eligible_cells(records: list[Record], n_seeds: int) -> dict[str, list[Record]]:
    """Cells that achieved the spec's seed count with a ``PASS`` gate.

    Grouped by replication key; a cell's records are its achieved seeds at the
    fidelity the schedule declared.
    """
    cells: dict[str, list[Record]] = {}
    for record in records:
        if record.status.gate_verdict.value != "PASS" or record.status.quarantine:
            continue
        cells.setdefault(replication_key(record), []).append(record)
    return {
        key: group
        for key, group in cells.items()
        if len({r.schedule.seed for r in group}) >= n_seeds
    }


def _coordinate(record: Record) -> Coordinate:
    """The cell a record measured, rebuilt from the record's own axes."""
    return Coordinate(
        substrate=record.substrate,
        geometry=record.geometry,
        dynamics=record.dynamics,
        plasticity=record.plasticity,
        credit=record.credit,
        update=record.update,
        params=record.params,
    )


def replay_survives(record: Record, tolerance: float) -> bool:
    """Whether the cell re-measured reproduces its claimed numeric metrics.

    The replay path is the evaluator itself: the same coordinate and schedule,
    a fresh measurement. A claimed metric that the replay cannot reproduce
    within the registered tolerance fails the gate.
    """
    from computronium.experiment.execution.evaluate import cell_record

    claimed = _claimed_metrics(record)
    if not claimed:
        return False
    replayed = cell_record(
        _coordinate(record),
        record.schedule,
        record.provenance,
    )
    replay_metrics = _claimed_metrics(replayed)
    for key, value in claimed.items():
        replay_value = replay_metrics.get(key)
        if replay_value is None:
            return False
        if abs(replay_value - value) > tolerance * max(abs(value), 1e-12):
            return False
    return True


def promote_run(
    store: RecordStore,
    run_id: str,
    spec: RunSpec,
    *,
    tolerance: float,
) -> list[dict[str, object]]:
    """Earn maturity for the run's cells; return the promotion history.

    L1 is written per eligible cell; L2 only where the replay gate passes.
    """
    records = store.query_records(run_id=run_id)
    history: list[dict[str, object]] = []
    for key, group in eligible_cells(records, spec.n_seeds).items():
        cell_key = group[0].cell_key
        for record in group:
            store.set_cell_maturity(run_id, record.cell_key, Maturity.L1)
        representative = min(group, key=lambda r: r.schedule.seed)
        survived = replay_survives(representative, tolerance)
        if survived:
            # The replay verdict is the reproducibility measurement: a claim
            # that re-measured is computationally reproducible by definition.
            store.set_cell_maturity(
                run_id,
                cell_key,
                Maturity.L2,
                ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE,
            )
            history.append({
                "cell_key": cell_key,
                "replication_key": key,
                "maturity": Maturity.L2.value,
                "replay": "pass",
            })
        else:
            logger.warning(
                "Cell %s is L1-eligible but its replay did not reproduce "
                "the claimed metrics within tolerance %.2f",
                cell_key,
                tolerance,
            )
            history.append({
                "cell_key": cell_key,
                "replication_key": key,
                "maturity": Maturity.L1.value,
                "replay": "fail",
            })
    return history
