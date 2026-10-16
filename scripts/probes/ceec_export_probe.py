"""Probe the CEEC export with real measured L2 records (first real invocation).

Informs TODO65 §3.W3 / §7.4 (ceec_link recording). Run:

    uv run python scripts/probes/ceec_export_probe.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.evidence.ceec_export import export_claims_to_ceec
from computronium.experiment.kernel import cell_record
from computronium.experiment.schema import (
    MEASURED_PARAM_BUDGET,
    Coordinate,
    Provenance,
    RunSpec,
    Schedule,
    seed_all_registries,
)

_TASK = "digits"
_BATCHES = 2
_SEEDS = 5


def _coordinate() -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit="local_contrastive",
        update="euclidean",
        params={},
    )


def _schedule(seed: int) -> Schedule:
    return Schedule(
        fidelity="L2",
        seed=seed,
        n_seeds=_SEEDS,
        epochs=1,
        batch_limit=_BATCHES,
        budget_id="ceec-probe",
        task_id=_TASK,
        param_budget=MEASURED_PARAM_BUDGET,
    )


def main() -> None:
    seed_all_registries()
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        with RecordStore(StoreConfig(path=base / "probe.duckdb")) as store:
            spec = RunSpec(
                task=_TASK,
                objectives=("validation_accuracy",),
                fidelity="L2",
                n_seeds=_SEEDS,
                epochs=1,
                batch_limit=_BATCHES,
                param_budget=MEASURED_PARAM_BUDGET,
            )
            run_id = store.create_run(spec=spec)
            for seed in range(_SEEDS):
                record = cell_record(
                    _coordinate(),
                    _schedule(seed),
                    Provenance(
                        env={"python": "3.14", "platform": "probe"},
                        dataset=_TASK,
                        dataset_version="1.0",
                        code_sha="probe",
                        policy="probe",
                        links={"run_id": run_id},
                    ),
                )
                store.append(record)

            records = store.query_records(run_id=run_id)
            from collections import Counter

            print("verdicts:", Counter(r.status.gate_verdict.value for r in records))
            print("fidelities:", Counter(r.schedule.fidelity for r in records))

            link = export_claims_to_ceec(
                store,
                run_id,
                ceec_ledger_path=base / "ceec.sqlite3",
                ceec_artifacts_dir=base / "ceec_artifacts",
            )
            print("export link ->", link)

            after = store.query_records(run_id=run_id)
            recorded = [r.status.ceec_link for r in after if r.status.ceec_link]
            print("ceec_link recorded on:", len(recorded), "of", len(after))


if __name__ == "__main__":
    main()
