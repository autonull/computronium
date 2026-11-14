"""TODO92 §3.7: does a local credit match backprop on MNIST at claim grade?

Discovery (seeds 42-46, L2/20, 10k held out, CPU) measured gradient
0.9755 ± 0.0023 against PEPITA 0.9751 ± 0.0020 on the same
digital/feedforward/instantaneous/null/adam cell: paired difference -0.0004,
95% CI [-0.0051, +0.0044], p=0.84. That is a cost-adjusted parity, not a win.

This probe runs the pre-registered confirmation in
``configs/preregistrations/t92_pepita_mnist.json``: new seeds 47-56 on both
arms, decision by ``PairedComparison.passes_equivalence(0.01)``. The anchors
are the discovery records, rebuilt from their stores, so the only differences
in a cell are the credit and the seed.

Measured discovery cost: gradient 359 s/seed, PEPITA 412 s/seed (CPU, L2/20).

Run: uv run python scripts/probes/t92_pepita_mnist.py
     uv run python scripts/probes/t92_pepita_mnist.py --report-only
Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import time
from dataclasses import asdict, replace
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
    EquivalenceRegistration,
    paired_comparison,
)

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "experiments/t92_pepita_mnist.duckdb"
REGISTRATION = ROOT / "configs/preregistrations/t92_pepita_mnist.json"
SEEDS = tuple(range(47, 57))
ARMS = {
    "gradient": ("experiments/experiment_20261109_103319.duckdb", "bfab4794"),
    "pepita": ("experiments/experiment_20261109_165912.duckdb", "9a54fb36"),
}


def _locate(arm: str) -> tuple[Coordinate, Schedule]:
    store_name, anchor = ARMS[arm]
    with RecordStore(StoreConfig(path=ROOT / store_name, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(anchor):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {anchor} in {store_name}"
    raise LookupError(msg)


def _code_sha() -> str:
    return git_sha() or "local"


def _provenance(run_id: str) -> Provenance:
    env = {
        key: value
        for key, value in os.environ.items()
        if key.startswith(("CUDA", "TORCH", "OMP", "OPENBLAS"))
    }
    env.setdefault("python", platform.python_version())
    return Provenance(
        env=env,
        dataset="mnist",
        dataset_version="probe",
        code_sha=_code_sha(),
        policy="t92_pepita_mnist",
        links={"run_id": run_id},
    )


def _check_matched(arms: dict[str, tuple[Coordinate, Schedule]]) -> None:
    reference_arm, (reference_coordinate, reference_schedule) = next(iter(arms.items()))
    for arm, (coordinate, schedule) in arms.items():
        if arm == reference_arm:
            continue
        reference_axes = {
            key: value
            for key, value in asdict(reference_coordinate).items()
            if key != "credit"
        }
        axes = {
            key: value for key, value in asdict(coordinate).items() if key != "credit"
        }
        if axes != reference_axes:
            msg = f"{arm} coordinate differs beyond credit: {axes} != {reference_axes}"
            raise ValueError(msg)
        if asdict(schedule) != asdict(reference_schedule):
            msg = f"{arm} schedule differs from {reference_arm}"
            raise ValueError(msg)
        print(f"matched: {reference_arm} vs {arm} differ only in credit")


def _values(store: RecordStore, run_id: str) -> dict[str, dict[int, float]]:
    values: dict[str, dict[int, float]] = {arm: {} for arm in ARMS}
    for record in store.query_records(run_id=run_id):
        if record.credit not in values:
            continue
        seed = record.schedule.seed
        if seed not in SEEDS:
            continue
        if record.status.gate_verdict.value != "PASS":
            print(
                f"{record.credit} seed={seed}: gate={record.status.gate_verdict.value} "
                f"defect={record.status.defect}"
            )
            continue
        values[record.credit][seed] = float(record.payload["val_acc"])
    return values


def _report(values: dict[str, dict[int, float]]) -> int:
    registration = EquivalenceRegistration.load(REGISTRATION)
    complete = {
        arm: [values[arm][seed] for seed in SEEDS if seed in values[arm]]
        for arm in ARMS
    }
    for arm, seeds in complete.items():
        print(
            f"{arm:9}: n={len(seeds)} mean={statistics.mean(seeds):.4f} "
            f"sd={statistics.stdev(seeds) if len(seeds) > 1 else 0.0:.4f}"
        )
    if len(complete["gradient"]) < len(SEEDS) or len(complete["pepita"]) < len(SEEDS):
        print(
            f"incomplete: {len(complete['gradient'])}/{len(SEEDS)} and "
            f"{len(complete['pepita'])}/{len(SEEDS)} seeds recorded"
        )
        return 2
    result = paired_comparison(complete["pepita"], complete["gradient"], seed=0)
    equivalent = result.passes_equivalence(registration)
    print(
        f"paired PEPITA - gradient: {result.mean_diff:+.4f} "
        f"95% CI [{result.ci_lower:+.4f}, {result.ci_upper:+.4f}] "
        f"p={result.p_value:.4f} dz={result.cohens_dz:.2f}"
    )
    print(
        f"verdict: {'EQUIVALENT' if equivalent else 'NOT-EQUIVALENT'} "
        f"(margin=±{registration.margin:.4f}, alpha={registration.alpha})"
    )
    return 0 if equivalent else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Read recorded seeds and decide without training",
    )
    args = parser.parse_args(argv)

    arms = {arm: _locate(arm) for arm in ARMS}
    _check_matched(arms)

    with RecordStore(StoreConfig(path=STORE)) as store:
        runs = store.query_runs(limit=1)
        run_id = runs[0].run_id if runs else store.create_run()
        print(f"run {run_id[:8]} store {STORE.relative_to(ROOT)}")
        if not args.report_only:
            provenance = _provenance(run_id)
            for arm, (coordinate, schedule) in arms.items():
                for seed in SEEDS:
                    started = time.perf_counter()
                    record = cell_record(
                        coordinate, replace(schedule, seed=seed), provenance
                    )
                    store.append(record)
                    value = record.payload.get("val_acc")
                    print(
                        f"{arm:9} seed={seed}: val_acc={value} "
                        f"gate={record.status.gate_verdict.value} "
                        f"({time.perf_counter() - started:.1f}s)",
                        flush=True,
                    )
        values = _values(store, run_id)

    return _report(values)


if __name__ == "__main__":
    raise SystemExit(main())
