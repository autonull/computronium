"""W39: what the from-scratch loop promotes, one task, two cycles.

Replicates the acceptance fixture's loop config on `xor` alone and dumps every
record's gate, maturity and seed, so the promotion gap is read from the store
instead of guessed from a 366 s shard.

Informs TODO107 W39.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.registry.loop import LoopConfig, LoopDriver
from computronium.experiment.schema import seed_all_registries


def main() -> None:
    seed_all_registries()
    tmpdir = tempfile.TemporaryDirectory()
    state_dir = Path(tmpdir.name) / "loop_state"
    store_path = Path(tmpdir.name) / "loop.duckdb"
    state_dir.mkdir(parents=True, exist_ok=True)

    config = LoopConfig(
        store_path=store_path,
        state_dir=state_dir,
        stages=(
            "s1_frame",
            "s2_space",
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
            "s11_report",
        ),
        param_budget=10000,
        policy="model_based",
        hyperparameters={},
        checkpoint_every_n=0,
        device="cpu",
        master_seed=42,
        hours=0.2,
        cycles=2,
        n_seeds=2,
        explore_fidelity="L0",
        exploit_fidelity="L1",
        explore_hours=0.015,
        exploit_hours=0.015,
        explore_sweep_steps=10,
        exploit_sweep_steps=5,
        epochs_explore=1,
        epochs_exploit=3,
        cell_workers=1,
        task_schedule=("xor", "xor"),
        hypothesis_ids=(),
        use_icu_guided=False,
    )
    driver = LoopDriver(config)
    driver.run(dry_run=False)

    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        for run in store.query_runs():
            print(f"\n### run {run.run_id} task={run.spec.task if run.spec else '?'}")
            records = store.query_records(run_id=run.run_id)
            groups: dict[tuple[str, str], list] = {}
            for record in records:
                key = (record.credit, record.dynamics)
                groups.setdefault(key, []).append(record)
            for (credit, dynamics), group in sorted(groups.items()):
                outcomes = " ".join(
                    f"{r.schedule.seed}:{r.status.gate_verdict.value}"
                    f"/{r.status.maturity.value}"
                    for r in group
                )
                print(f"{credit:22s} {dynamics:22s} {outcomes}")
            promoted = [
                r
                for r in records
                if r.status.maturity.value in {"L1", "L2"} and not r.status.quarantine
            ]
            print(
                "promoted credits:",
                sorted({r.credit for r in promoted}) or "none",
                f"({len(promoted)}/{len(records)})",
            )
    tmpdir.cleanup()


if __name__ == "__main__":
    main()
