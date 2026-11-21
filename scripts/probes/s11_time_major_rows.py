"""Measure the time-major rows the breadth exit needs: one L2/n>=5 cell per credit.

The three temporal credits (``eligibility_prop``, ``rtrl_reference``,
``unbiased_rtrl``) declare ``sequence + rl``. No flat task composes them
(``BATCH_LAYOUT_RULE`` refuses both directions), and their rl half is refused by
name (``rl_credit_must_be_error_blind``: the credits read error). ``delayed_cue``
is the one declared time-major task, and it declares ``sequence + continual``, so
one cell on it is a cell on two families.

The cell is the declared space's time-major selection (recurrent geometry,
instantaneous dynamics, null plasticity, adam) at the sequence family's base
schedule: ``sequence``'s base box is ``char_ngram`` (32/0/10), and this probe
swaps the flat base task for the time-major one instead of declaring a second
table. ``rtrl_reference`` re-derives the exact recurrent Jacobian per step
(O(time^2 * batch)), so its row runs the 2-epoch box that clears its bar.

Measured 2026-11-21 (five seeds each; val_acc toward the 0.10 chance bar): see
the TODO97 S11 paragraph for the numbers. The bar is the task's own
``primary_pass_bar``; ``pass_bar_cleared`` is the record's cached derivation.

Run: ``uv run python scripts/probes/s11_time_major_rows.py --credit eligibility_prop \\
    --seeds 5 --write``
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import cell_record
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.sec_loop import _provenance, base_schedule

AXES = {
    "substrate": "digital",
    "geometry": "recurrent",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "update": "adam",
}
TASK = "delayed_cue"
BASE_TASK = "char_ngram"
#: The reference credit's exact Jacobian is O(time^2 * batch) per step.
EPOCHS = {"rtrl_reference": 2}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--credit", required=True)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=0)
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--store", default="experiments/breadth_{credit}_delayed_cue.duckdb"
    )
    args = parser.parse_args()

    base = base_schedule(BASE_TASK, "cpu")
    if base is None:
        raise SystemExit(f"{BASE_TASK} declares no base box")
    epochs = args.epochs or EPOCHS.get(args.credit, base.epochs)
    schedule = replace(
        base,
        task_id=TASK,
        budget_id=f"base-sequence-{TASK}",
        fidelity="L2",
        n_seeds=args.seeds,
        epochs=epochs,
        batch_size=32,
    )
    coordinate = Coordinate(**AXES, credit=args.credit, params={})
    box = {"task_id": TASK, "budget_id": schedule.budget_id, "fidelity": "L2"}
    store = Path(
        args.store.format(credit=args.credit, task=TASK)
        if "{credit}" in args.store
        else args.store
    )
    records = []
    for seed in range(args.seeds):
        record = cell_record(
            coordinate,
            replace(schedule, seed=seed),
            _provenance(TASK, box, "s11-time-major"),
        )
        payload = record.payload
        print(
            f"{args.credit} seed={seed} epochs={epochs} "
            f"{payload.get('primary_metric')}="
            f"{payload.get(payload.get('primary_metric', 'val_acc'))} "
            f"cleared={payload.get('pass_bar_cleared')} "
            f"wall={payload.get('walltime_s', 0):.1f}s "
            f"verdict={record.status.gate_verdict.value}"
        )
        records.append(record)
    if args.write:
        with RecordStore(StoreConfig(path=store, read_only=False)) as records_store:
            for run_id in {
                str(record.provenance.links.get("run_id", "")) for record in records
            }:
                records_store.create_run(run_id=run_id)
            records_store.append_batch(records)


if __name__ == "__main__":
    main()
