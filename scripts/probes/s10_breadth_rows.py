"""Measure the breadth rows the gate needs: one L2/n>=5 cell per (credit, task).

The breadth exit (AGENTS, ``comp gate breadth``) reads *records*, not the map:
every error-aware credit needs a legal, bar-cleared L2/n>=5 cell on >=2 task
domains. The P0 screens wrote the map at L0/1 seed, so nine credits held no
qualifying record. This probe runs one cell per row at the row's own box
(``screen_coordinate``), at the family's declared base schedule, and writes the
five seed records to a store the gate reads.

Measured 2026-11-21 (five seeds each, own box, base schedule; 2 threads per
process, 12 concurrent): the mnist rows clear the 0.106 bar —
``forward_tangent`` 0.1302–0.2293, ``hybrid`` 0.6606–0.728, ``local_supervision``
0.7716–0.7891, ``score_function`` 0.6519–0.7582, ``surrogate`` 0.8947–0.9067,
``zeroth_order`` 0.1444–0.2354. The second families clear their bars —
char_ngram ppl 22.36–23.95 (``forward_tangent``), ppl 4.28–10.20 (``hybrid``),
ppl 22.34–23.57 (``zeroth_order``); copy_task 0.1555–0.1715
(``local_supervision``); iris 0.6667–0.8333 (``score_function``), 0.9667–1.0
(``surrogate``). ``zeroth_order`` on copy_task is **marginal**: 3/5 seeds clear
0.125 (0.112–0.132), so memory is not counted as its second family.

Scout first (``--seeds 1``, no ``--write``), then the five-seed run
(``--write --store ...``).

Run: ``uv run python scripts/probes/s10_breadth_rows.py --credit zeroth_order \\
    --task char_ngram --seeds 5 --write --store experiments/breadth_zeroth_order_char_ngram.duckdb``
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import cell_record, task_shape
from computronium.experiment.sec_census import build_census
from computronium.experiment.sec_loop import (
    _is_legal,
    _provenance,
    base_schedule,
    screen_coordinate,
)
from computronium.experiment.sec_pilot import base_family, refusal_for

AXIS = "credit"
MAP = Path("results/sec/map.json")


def _row(credit: str) -> dict:
    row = json.loads(MAP.read_text(encoding="utf-8"))["primitives"][
        f"primitive.credit_assignment.{credit}"
    ]
    return row


def _entry(credit: str):
    return next(
        e for e in build_census() if e.id == f"primitive.credit_assignment.{credit}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credit", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--store", default="experiments/experiment_breadth.duckdb")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    row = _row(args.credit)
    coordinate = screen_coordinate(row["box"], AXIS, args.credit)
    family = base_family(args.task) or args.task
    schedule = base_schedule(args.task, "cpu")
    if schedule is None:
        raise SystemExit(f"{args.task} declares no base box")
    schedule = replace(
        schedule, fidelity="L2", n_seeds=args.seeds, seed=0, batch_size=32
    )

    reason = refusal_for(_entry(args.credit), args.task)
    legal, why = _is_legal(coordinate, args.task, task_shape(args.task, "cpu"))
    print(
        f"{args.credit} on {args.task}: family={family} "
        f"legal={legal} refusal={reason or why or '-'}"
    )
    if args.dry_run or not legal or reason:
        print(
            f"  clock={schedule.fidelity}/{schedule.n_seeds} epochs={schedule.epochs}"
        )
        return

    records = []
    for seed in range(args.seeds):
        record = cell_record(
            coordinate,
            replace(schedule, seed=seed),
            _provenance(args.task, row["box"], "s10-breadth"),
        )
        payload = record.payload
        key = payload.get("primary_metric", "val_acc")
        print(
            f"  seed={seed} {key}={payload.get(key)}"
            f" cleared={payload.get('pass_bar_cleared')}"
            f" wall={payload.get('walltime_s', 0):.1f}s"
            f" verdict={record.status.gate_verdict.value}"
        )
        records.append(record)
    if args.write:
        with RecordStore(StoreConfig(path=Path(args.store), read_only=False)) as store:
            for run_id in {
                str(record.provenance.links.get("run_id", "")) for record in records
            }:
                store.create_run(run_id=run_id)
            store.append_batch(records)


if __name__ == "__main__":
    main()
