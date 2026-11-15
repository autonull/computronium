"""TODO92 §3.2: does the graph readout move the marginal row?

PROTEINS re-measured 0.7013 ± 0.0164 (SD, n=5, 223 held out, majority 0.5964):
0.08σ above the 0.70 bar, so the claim rule calls it marginal. Capacity was
excluded by a pre-registered arm; the builder already reads ``geometry.pooling``
(``mean``/``sum``) but no run declares it, so the readout is the last graph
lever. This probe runs the pre-registered paired comparison in
``configs/preregistrations/t92_graph_pooling.json`` (committed before the run):
treatment = ``geometry.pooling "sum"``; control = ``"mean"``; same coordinate,
schedule and seeds, so the difference is the readout alone.

The graph pipeline lock proves sum pooling is addition, not a mean in disguise
(``tests/property/test_graph_pipeline_lock.py``).

Run: uv run python scripts/probes/t92_graph_pooling.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import statistics
import time
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import Any

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import evaluate_cell
from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.validation.preregistration import (
    ThresholdRegistration,
    paired_comparison,
)

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "experiments/t88_r1b_proteins_confirm.duckdb"
ANCHOR = "24803890"
SEEDS = (42, 43, 44, 45, 46)
TREATMENT: dict[str, Any] = {"geometry.pooling": "sum"}
REGISTRATION = ROOT / "configs/preregistrations/t92_graph_pooling.json"


def _locate() -> tuple[Coordinate, Schedule]:
    with RecordStore(StoreConfig(path=STORE, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(ANCHOR):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {ANCHOR} in {STORE}"
    raise LookupError(msg)


def _arm(
    coordinate: Coordinate, schedule: Schedule, params: Mapping[str, Any]
) -> list[float]:
    run_coordinate = replace(coordinate, params={**coordinate.params, **params})
    values: list[float] = []
    for seed in SEEDS:
        started = time.perf_counter()
        result = evaluate_cell(run_coordinate, replace(schedule, seed=seed))
        value = result.metrics["val_acc"]
        values.append(value)
        print(
            f"{params!s:31} seed={seed}: val_acc={value:.4f} "
            f"({time.perf_counter() - started:.1f}s)"
        )
    return values


def main() -> int:
    coordinate, schedule = _locate()
    control = _arm(coordinate, schedule, {})
    treatment = _arm(coordinate, schedule, TREATMENT)
    registration = ThresholdRegistration.load(REGISTRATION)
    result = paired_comparison(treatment, control, seed=0)
    print(
        f"control: n={len(control)} mean={statistics.mean(control):.4f} "
        f"sd={statistics.stdev(control):.4f}"
    )
    print(
        f"treatment: n={len(treatment)} mean={statistics.mean(treatment):.4f} "
        f"sd={statistics.stdev(treatment):.4f}"
    )
    print(
        f"paired: mean_diff={result.mean_diff:+.4f} "
        f"CI=[{result.ci_lower:+.4f}, {result.ci_upper:+.4f}] "
        f"p={result.p_value:.4f} dz={result.cohens_dz:.2f}"
    )
    print(
        f"verdict: {'PASS' if result.passes(registration) else 'FAIL'} "
        f"(threshold={registration.threshold:+.4f}, alpha={registration.alpha})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
