"""Probe the v1 exit pipeline's real state: allocator promotions + ceec_link.

Informed tests/acceptance/test_v1_exit.py (TODO65 §7 items 3-4). Run:

    uv run python scripts/probes/exit_state_probe.py
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.execution import (
    Budget,
    EvidenceDrivenAllocator,
    LocalBackend,
    PipelineConfig,
    PipelineRunner,
    StratifiedRandomPolicy,
)
from computronium.experiment.schema import (
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    RunSpec,
    seed_all_registries,
)


def _spec() -> RunSpec:
    return RunSpec(
        profile="probe",
        task="digits",
        objectives=("validation_accuracy", "walltime_total"),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=120.0,
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=MEASURED_BATCH_LIMIT,
        code_sha="probe",
        dataset="digits",
        dataset_version="1.0",
    )


def main() -> None:
    seed_all_registries()
    with tempfile.TemporaryDirectory() as d:
        store = RecordStore(StoreConfig(path=Path(d) / "probe.duckdb"))
        with store:
            spec = _spec()
            run_id = store.create_run(spec=spec)
            config = PipelineConfig(
                run_id=run_id,
                run_spec=spec,
                budget=Budget.from_duration("120s"),
                policy=StratifiedRandomPolicy(seed=42),
                allocator=EvidenceDrivenAllocator(promotion_threshold=0.05),
                backend=LocalBackend(),
                seed=spec.seed,
                max_rounds=2,
                min_rounds=1,
            )
            runner = PipelineRunner(config, store)
            records = asyncio.run(runner.run())
            print("deadline:", config.deadline)
            print("records:", len(records))
            print("allocator_promotions:", len(runner._state.allocator_promotions))
            ceec = [r.status.ceec_link for r in records if r.status.ceec_link]
            print("ceec_links recorded:", len(ceec))
            print("sample ceec_link:", ceec[:2])

            from collections import Counter

            print(
                "maturity:",
                Counter(r.status.maturity.value for r in records),
            )
            from computronium.experiment.evidence.ceec_export import (
                export_claims_to_ceec,
                export_statistical_result_to_ceec,
            )

            try:
                link = export_claims_to_ceec(store, run_id)
                print("export_claims_to_ceec ->", link)
            except Exception as exc:
                print("export_claims_to_ceec RAISED:", type(exc).__name__, exc)
            try:
                link2 = export_statistical_result_to_ceec(store, run_id)
                print("export_statistical_result_to_ceec ->", link2)
            except Exception as exc:
                print(
                    "export_statistical_result_to_ceec RAISED:", type(exc).__name__, exc
                )


if __name__ == "__main__":
    main()
