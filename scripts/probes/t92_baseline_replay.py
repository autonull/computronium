"""TODO92 §3.0: re-execute the cells each baseline row rests on.

A row located in the corpus is a record, not a measurement of the current
system. This probe reads the record by ``measurement_key``, rebuilds its
coordinate and schedule from the record, and trains it again through
``kernel.evaluate_cell`` — the same evaluator the record came from. The anchor
seed replays the record's exact schedule, so its recomputed
``measurement_key`` must match the recorded one; the other seeds widen the
ruler the claim needs.

Other seeds are the claim's ruler, not the record's: wine n=3 (the §2 row
quotes n=3), Cora n=3, PROTEINS n=5 (marginal), MNIST n=3. Every run prints its
recomputed ``measurement_key``, so a row's replay is identifiable from the log;
``evaluate_cell`` emits ``val_acc`` but not the record's ``normalized_metric``.

Measured (2026-11-14, RTX 3080, recorded devices):
* wine L2/20ep          1.7 s/seed
* cora L1/100ep          0.7 s/seed
* proteins L1/100ep     39.2 s/seed
* mnist L2/20ep (cpu)  278 s/seed — the record's device; no GPU replay

Run: uv run python scripts/probes/t92_baseline_replay.py [--only wine,cora]
Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import statistics
import time
from dataclasses import dataclass, replace
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import evaluate_cell
from computronium.experiment.schema.coordinate import Coordinate, Schedule

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Case:
    """One located baseline cell: where its record lives and the seeds to run."""

    label: str
    store: str
    key_prefix: str
    seeds: tuple[int, ...]
    metric: str
    recorded: float


CASES = (
    Case(
        label="wine",
        store="experiments/experiment_20261109_194501.duckdb",
        key_prefix="b7eadd6b",
        seeds=(42, 43, 44),
        metric="val_acc",
        recorded=0.9722,
    ),
    Case(
        label="cora",
        store="experiments/t88_g6_cora_claim_l1.duckdb",
        key_prefix="6328d4d4",
        seeds=(42, 43, 44),
        metric="val_acc",
        recorded=0.7820,
    ),
    Case(
        label="proteins",
        store="experiments/t88_r1b_proteins_confirm.duckdb",
        key_prefix="24803890",
        seeds=(42, 43, 44, 45, 46),
        metric="val_acc",
        recorded=0.6637,
    ),
    Case(
        label="mnist",
        store="experiments/experiment_20261109_095412.duckdb",
        key_prefix="e4f41051",
        seeds=(46, 45, 44),
        metric="val_acc",
        recorded=0.9792,
    ),
)


def _locate(case: Case) -> tuple[Coordinate, Schedule]:
    path = ROOT / case.store
    with RecordStore(StoreConfig(path=path, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(case.key_prefix):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {case.key_prefix} in {case.store}"
    raise LookupError(msg)


def replay(case: Case) -> None:
    coordinate, schedule = _locate(case)
    values: list[float] = []
    started = time.perf_counter()
    for seed in case.seeds:
        run = replace(schedule, seed=seed)
        computed = coordinate.measurement_key(run)
        identity = (
            " key-match"
            if computed.startswith(case.key_prefix)
            else f" key={computed[:8]}"
        )
        t0 = time.perf_counter()
        result = evaluate_cell(coordinate, run)
        walltime = time.perf_counter() - t0
        value = result.metrics[case.metric]
        values.append(value)
        extra = ""
        if case.metric != "val_acc" and "val_acc" in result.metrics:
            extra = f" val_acc={result.metrics['val_acc']:.4f}"
        print(
            f"{case.label} seed={seed}: {case.metric}={value:.4f}{extra} "
            f"{walltime:.1f}s{identity}"
        )
    mean = statistics.mean(values)
    spread = statistics.stdev(values) if len(values) > 1 else 0.0
    print(
        f"{case.label}: n={len(values)} mean={mean:.4f} sd={spread:.4f} "
        f"anchor recorded={case.recorded:.4f} seeds={list(case.seeds)} "
        f"({time.perf_counter() - started:.1f}s)\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default="", help="Comma-separated case labels")
    args = parser.parse_args(argv)
    wanted = {name.strip() for name in args.only.split(",") if name.strip()}
    for case in CASES:
        if not wanted or case.label in wanted:
            replay(case)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
