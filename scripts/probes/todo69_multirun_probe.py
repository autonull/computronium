"""What a second run in one store costs, and whether it can be different.

The multi-run space (TODO69) needs two runs in one store, and the tour's
store holds one. The smallest change that makes the view show something is
a second campaign that reaches different cells, so this probe measures
what such a campaign costs and whether the cells it names can be trained
at all.

Measured on this machine (CPU, digits, L1, three epochs):
  * the demo campaign — four credit arms, five seeds, twenty records:
    33 s;
  * a second campaign over two other credit rules, one seed, one epoch:
    4 s, two records, both at the chance level (0.0917).

The two credit rules are `homeostatic` and `temporal_trace`: they compose,
they train, and the demo campaign measures neither of them, so the two
runs' cells do not overlap.

Run: uv run python scripts/probes/todo69_multirun_probe.py
"""

from __future__ import annotations

import dataclasses
import tempfile
import time
from pathlib import Path

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.surface.cli import (
    RUN_PROFILES,
    execute_spec,
    spec_from_profile,
)

SECOND_CREDIT = ("homeostatic", "temporal_trace")


def second_spec() -> object:
    """The demo's own declaration, with two other credit rules."""
    profile = RUN_PROFILES["demo"]
    axes = tuple(
        selection.model_copy(
            update={
                "primitives": SECOND_CREDIT
                if selection.axis is StructuralAxis.CREDIT
                else selection.primitives
            }
        )
        for selection in profile.axes
    )
    return spec_from_profile(
        dataclasses.replace(profile, axes=axes, n_seeds=1, epochs=1)
    )


def run(label: str, spec: object) -> None:
    """Run one campaign into a fresh store, and report what it measured."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    with tempfile.TemporaryDirectory() as directory:
        store_path = Path(directory) / "probe.duckdb"
        started = time.perf_counter()
        code = execute_spec(spec, store_path=str(store_path))  # type: ignore[arg-type]
        elapsed = time.perf_counter() - started

        with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
            for run_info in store.query_runs():
                records = list(store.query_records(run_id=run_info.run_id))
                print(
                    f"[{label}] run {run_info.run_id} status={run_info.status} "
                    f"records={len(records)}"
                )
                for record in records:
                    print(
                        f"    {record.credit}/{record.geometry}/{record.dynamics} "
                        f"seed={record.schedule.seed} acc={record.payload.get('val_acc')}"
                    )
        print(f"[{label}] exit={code} elapsed={elapsed:.1f}s")


def main() -> int:
    """Time the demo campaign, then a second one over other credit rules."""
    run("demo", spec_from_profile(RUN_PROFILES["demo"]))
    run("second", second_spec())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
