"""Probe: a declared hypothesis constrains the loop's search arms.

TODO107 W30 (acceptance `test_cross_domain_evaluation`): the loop sampled the
whole credit space, so a governed hypothesis was evaluated on credits it never
declared. This probe runs one explore cycle on ``xor`` at the acceptance
fixture's budget and prints the credits per run, the hypothesis status, and the
samples per declared arm. Measured: one cycle writes 10 records split across
``gradient`` and ``thermodynamic_contrast`` only.
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
        hours=0.03,
        cycles=1,
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
        task_schedule=("xor", "iris", "digits"),
        hypothesis_ids=("H1_credit_efficiency",),
        hypothesis_registry_path=state_dir / "hypotheses.json",
        use_icu_guided=False,
    )
    LoopDriver(cfg).run(dry_run=False)

    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        for run in store.query_runs():
            recs = store.query_records(run_id=run.run_id)
            credits = Counter(r.credit for r in recs)
            print(f"RUN {run.run_id[:8]} n={len(recs)} credits={dict(credits)}")
    tmp.cleanup()


if __name__ == "__main__":
    main()
