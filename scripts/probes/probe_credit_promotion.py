"""Probe: which credits appear and get promoted in a tiny loop run.

Informs TODO64 S1 (From-Scratch Test): the acceptance test requires a local
credit (thermodynamic_contrast/random_projections/pepita/local_goodness) to
reach L1/L2. This probe runs one explore cycle on ``xor`` and prints the
credit/maturity/verdict distribution so the failure mode is legible without
running the ~1h acceptance fixture.
"""

from __future__ import annotations

import tempfile
from collections import Counter
from pathlib import Path

from computronium.experiment.evidence import RecordStore, StoreConfig
from computronium.experiment.registry.loop import LoopConfig, LoopDriver
from computronium.experiment.schema import seed_all_registries


def main() -> None:
    seed_all_registries()
    tmp = tempfile.TemporaryDirectory()
    state_dir = Path(tmp.name) / "s"
    store_path = Path(tmp.name) / "l.duckdb"
    state_dir.mkdir(parents=True, exist_ok=True)
    cfg = LoopConfig(
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
        ),
        param_budget=10000,
        policy="model_based",
        hyperparameters={},
        checkpoint_every_n=0,
        device="cpu",
        master_seed=42,
        hours=0.2,
        cycles=1,
        n_seeds=1,
        explore_fidelity="L0",
        exploit_fidelity="L1",
        explore_hours=0.05,
        exploit_hours=0.05,
        explore_sweep_steps=10,
        exploit_sweep_steps=5,
        epochs_explore=1,
        epochs_exploit=1,
        cell_workers=2,
        task_schedule=("xor",),
    )
    LoopDriver(cfg).run(dry_run=False)
    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        for run in store.query_runs():
            recs = store.query_records(run_id=run.run_id)
            print(f"RUN {run.run_id[:8]} n={len(recs)}")
            print("  credits:", dict(Counter(r.credit for r in recs)))
            print("  maturity:", dict(Counter(r.status.maturity.value for r in recs)))
            print("  verdict:", dict(Counter(r.status.gate_verdict.name for r in recs)))
    tmp.cleanup()


if __name__ == "__main__":
    main()
