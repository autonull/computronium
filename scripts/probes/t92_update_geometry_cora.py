"""TODO92 §3.10: does the update rule pay differently on graph vs feedforward?

Second interaction. 2x2 geometry {``graph``, ``feedforward``} x update
{``adam``, ``muon``} on the Cora anchor (node classification, 500-node public
split, majority 0.316):

    interaction(seed) = (muon - adam)_graph - (muon - adam)_feedforward

Anchored on record ``6328d4d4`` (digital/graph/null/gradient/adam,
step_size 0.01, L2/100, cuda). Seeds 47-51 are fresh; the pre-registration is
``configs/preregistrations/t92_update_geometry_cora.json``.

Measured (2026-11-14, RTX 3080, 1 epoch, seed 42): graph+muon 0.47 s,
feedforward+adam 0.02 s, feedforward+muon 0.01 s, so the 2x2 is minutes.

Run: uv run python scripts/probes/t92_update_geometry_cora.py
     uv run python scripts/probes/t92_update_geometry_cora.py --report-only
Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import time
from dataclasses import replace
from pathlib import Path

from computronium.core.utils.git import git_sha
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import cell_record
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)
from computronium.validation.preregistration import (
    ThresholdRegistration,
    paired_comparison,
)

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "experiments/t92_update_geometry_cora.duckdb"
REGISTRATION = ROOT / "configs/preregistrations/t92_update_geometry_cora.json"
ANCHOR_STORE = ROOT / "experiments/t88_g6_cora_claim_l1.duckdb"
ANCHOR = "6328d4d4"
SEEDS = (47, 48, 49, 50, 51)
ARMS = (
    ("graph", "adam"),
    ("graph", "muon"),
    ("feedforward", "adam"),
    ("feedforward", "muon"),
)


def _locate() -> tuple[Coordinate, Schedule]:
    with RecordStore(StoreConfig(path=ANCHOR_STORE, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(ANCHOR):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {ANCHOR} in {ANCHOR_STORE}"
    raise LookupError(msg)


def _provenance(run_id: str) -> Provenance:
    env = {
        key: value
        for key, value in os.environ.items()
        if key.startswith(("CUDA", "TORCH", "OMP", "OPENBLAS"))
    }
    env.setdefault("python", platform.python_version())
    return Provenance(
        env=env,
        dataset="cora",
        dataset_version="probe",
        code_sha=git_sha() or "local",
        policy="t92_update_geometry_cora",
        links={"run_id": run_id},
    )


def _schedule(anchor: Schedule) -> Schedule:
    return replace(
        anchor,
        fidelity="L2",
        budget_id="L2_initial",
        epochs=100,
        n_seeds=len(SEEDS),
        seed=SEEDS[0],
    )


def _values(store: RecordStore, run_id: str) -> dict[tuple[str, str], dict[int, float]]:
    values: dict[tuple[str, str], dict[int, float]] = {arm: {} for arm in ARMS}
    for record in store.query_records(run_id=run_id):
        arm = (record.geometry, record.update)
        if arm not in values or record.schedule.seed not in SEEDS:
            continue
        if record.status.gate_verdict.value != "PASS":
            print(
                f"{arm[0]} + {arm[1]} seed={record.schedule.seed}: "
                f"gate={record.status.gate_verdict.value} defect={record.status.defect}"
            )
            continue
        values[arm][record.schedule.seed] = float(record.payload["val_acc"])
    return values


def _cell_cost(store: RecordStore, run_id: str) -> dict[tuple[str, str], float]:
    cost: dict[tuple[str, str], float] = {}
    for record in store.query_records(run_id=run_id):
        arm = (record.geometry, record.update)
        if arm in ARMS:
            cost[arm] = cost.get(arm, 0.0) + float(
                record.payload.get("walltime_s", 0.0)
            )
    return cost


def _report(
    values: dict[tuple[str, str], dict[int, float]],
    cost: dict[tuple[str, str], float],
) -> int:
    registration = ThresholdRegistration.load(REGISTRATION)
    for arm in ARMS:
        measured = [values[arm][seed] for seed in SEEDS if seed in values[arm]]
        if not measured:
            print(f"{arm[0]:13} + {arm[1]:5}: no PASS seed")
            continue
        print(
            f"{arm[0]:13} + {arm[1]:5}: n={len(measured)} "
            f"mean={statistics.mean(measured):.4f} "
            f"sd={statistics.stdev(measured) if len(measured) > 1 else 0.0:.4f} "
            f"cost={cost.get(arm, 0.0):.1f}s"
        )
    if not all(len(values[arm]) == len(SEEDS) for arm in ARMS):
        print(
            "incomplete: "
            + ", ".join(f"{a[0]}+{a[1]} {len(values[a])}/{len(SEEDS)}" for a in ARMS)
        )
        return 2
    interaction = [
        (values["graph", "muon"][seed] - values["graph", "adam"][seed])
        - (values["feedforward", "muon"][seed] - values["feedforward", "adam"][seed])
        for seed in SEEDS
    ]
    result = paired_comparison(interaction, [0.0] * len(interaction), seed=0)
    print(
        f"interaction (muon - adam): graph - feedforward = "
        f"{result.mean_diff:+.4f} 95% CI [{result.ci_lower:+.4f}, "
        f"{result.ci_upper:+.4f}] p={result.p_value:.4f}"
    )
    verdict = (
        "INTERACTION"
        if result.passes(registration)
        else ("NULL" if result.ci_lower <= 0.0 <= result.ci_upper else "NEGATIVE")
    )
    print(
        f"verdict: {verdict} (threshold={registration.threshold:+.4f}, "
        f"alpha={registration.alpha})"
    )
    return 0 if verdict == "INTERACTION" else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Read recorded seeds and decide without training",
    )
    args = parser.parse_args(argv)

    anchor_coordinate, anchor_schedule = _locate()
    schedule = _schedule(anchor_schedule)
    coordinates = {
        arm: replace(anchor_coordinate, geometry=arm[0], update=arm[1]) for arm in ARMS
    }

    with RecordStore(StoreConfig(path=STORE)) as store:
        runs = store.query_runs(limit=1)
        run_id = runs[0].run_id if runs else store.create_run()
        print(f"run {run_id[:8]} store {STORE.relative_to(ROOT)}")
        if not args.report_only:
            provenance = _provenance(run_id)
            done = {
                (record.geometry, record.update, record.schedule.seed)
                for record in store.query_records(run_id=run_id)
            }
            for geometry, update in ARMS:
                for seed in SEEDS:
                    if (geometry, update, seed) in done:
                        print(
                            f"{geometry:13} + {update:5} seed={seed}: already recorded"
                        )
                        continue
                    started = time.perf_counter()
                    record = cell_record(
                        coordinates[geometry, update],
                        replace(schedule, seed=seed),
                        provenance,
                    )
                    store.append(record)
                    print(
                        f"{geometry:13} + {update:5} seed={seed}: "
                        f"val_acc={record.payload.get('val_acc')} "
                        f"gate={record.status.gate_verdict.value} "
                        f"({time.perf_counter() - started:.1f}s)",
                        flush=True,
                    )
        values = _values(store, run_id)
        cost = _cell_cost(store, run_id)

    return _report(values, cost)


if __name__ == "__main__":
    raise SystemExit(main())
