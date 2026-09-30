"""E1 store-overhead harness (K7/K9): append cost vs evaluation walltime.

Measured regime (2026-09-30, CPU, DuckDB embedded, single-writer):
200 appends, mean=3.03ms p95=4.43ms → 0.15%/0.22% of 2 s reference eval.
OVERHEAD_OK (< 1% criterion).
Binding criterion: mean append overhead < 1% of median evaluation walltime;
evaluations run 1-10 s, so the harness uses a 2 s synthetic reference eval
and requires mean/p95 append fractions below 1%.

Informs WP13 E1 (Definition of Done: overhead fraction recorded < 1%).
"""

from __future__ import annotations

import statistics
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.coordinate import (
    Coordinate,
    DataOrigin,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)

N_APPENDS = 200
REFERENCE_EVAL_S = 2.0
BUDGET_FRACTION = 0.01


def _record(run_id: str, idx: int) -> Record:
    coord = Coordinate(
        substrate="Digital",
        geometry="Feedforward",
        dynamics="Instantaneous",
        plasticity="NullPlasticity",
        credit="Backprop",
        update="Euclidean",
        params={"probe_idx": idx},
    )
    return Record.create(
        run_id=run_id,
        coordinate=coord,
        schedule=Schedule(
            fidelity="L2",
            seed=idx,
            n_seeds=200,
            epochs=10,
            batch_limit=100,
            budget_id="overhead",
            task_id="probe",
        ),
        provenance=Provenance(
            env={},
            dataset="probe",
            dataset_version="1.0",
            code_sha="sha",
            policy="probe",
            links={},
            data_origin=DataOrigin.EXPLORATION,
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L2,
            uncertainty={},
            reproducibility=ReproducibilityClass.COMPUTATIONALLY_REPRODUCIBLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload={"accuracy": 0.9},
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        store = RecordStore(StoreConfig(path=Path(tmp) / "overhead.duckdb"))
        with store:
            run_id = store.create_run(spec={"kind": "overhead-probe"})
            store.append(_record(run_id, N_APPENDS))
            latencies: list[float] = []
            for idx in range(N_APPENDS):
                start = time.perf_counter()
                store.append(_record(run_id, idx))
                latencies.append(time.perf_counter() - start)
    mean_s = statistics.fmean(latencies)
    p95_s = sorted(latencies)[int(0.95 * len(latencies))]
    mean_frac = mean_s / REFERENCE_EVAL_S
    p95_frac = p95_s / REFERENCE_EVAL_S
    print(f"appends={N_APPENDS} mean={mean_s * 1e3:.2f}ms p95={p95_s * 1e3:.2f}ms")
    print(
        f"reference_eval={REFERENCE_EVAL_S}s mean_frac={mean_frac:.4%} p95_frac={p95_frac:.4%}"
    )
    ok = mean_frac < BUDGET_FRACTION and p95_frac < BUDGET_FRACTION
    print("OVERHEAD_OK" if ok else "OVERHEAD_FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
