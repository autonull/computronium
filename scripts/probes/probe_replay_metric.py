"""Which task-axis metric moves when a promotion replay re-measures a cell.

Informs TODO107 W35. The in-run replay gate (`promotion.replay_survives`)
reported `replay=fail` on 4 of 8 cells of a serial `digits`/`iris`/`spiral`/
`wine` run whose fresh-process replay (`comp repro --device cpu`) passes, so
the gate and the replay command disagree about the same cell.

Usage:
    uv run python scripts/probes/probe_replay_metric.py <store> <run_id>
"""

from __future__ import annotations

import sys
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.promotion import (
    _claimed_metrics,
    _coordinate,
    replay_survives,
)
from computronium.experiment.kernel.evaluate import cell_record
from computronium.experiment.schema import seed_all_registries
from computronium.experiment.schema.registries import REPLAY_METRIC_TOLERANCE


def main(store_path: str, run_id: str) -> None:
    seed_all_registries()
    store = RecordStore(StoreConfig(path=Path(store_path), read_only=True))
    with store:
        records = store.query_records(run_id=run_id)
    for record in records:
        claimed = _claimed_metrics(record)
        replayed = _claimed_metrics(
            cell_record(
                _coordinate(record),
                record.schedule,
                record.provenance,
            )
        )
        moved = {
            key: (value, replayed.get(key))
            for key, value in claimed.items()
            if replayed.get(key) is None
            or abs(replayed[key] - value)
            > REPLAY_METRIC_TOLERANCE * max(abs(value), 1e-12)
        }
        print(
            f"{record.schedule.task_id:7s} {record.credit:20s} "
            f"seed={record.schedule.seed} survives={replay_survives(record, REPLAY_METRIC_TOLERANCE)} "
            f"moved={moved}"
        )


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
