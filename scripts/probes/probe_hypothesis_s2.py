"""Probe: verify hypothesis evaluation works in a tiny loop run.

Informs TODO64 S2 (First Governed Claim): the acceptance test requires a
preregistered hypothesis (H1_credit_efficiency) to be evaluated and reach
a definitive verdict (CONFIRMED/REJECTED). This probe runs one explore cycle
on ``xor`` with hypothesis evaluation enabled and prints the hypothesis
status so the failure mode is legible without running the ~35min acceptance
fixture.
"""

from __future__ import annotations

import tempfile
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
        policy="round_robin_grid",
        hyperparameters={},
        checkpoint_every_n=0,
        device="cpu",
        master_seed=42,
        hours=0.1,
        cycles=1,
        n_seeds=1,
        explore_fidelity="L0",
        exploit_fidelity="L1",
        explore_hours=0.05,
        exploit_hours=0.05,
        explore_sweep_steps=4,
        exploit_sweep_steps=3,
        epochs_explore=1,
        epochs_exploit=1,
        cell_workers=2,
        task_schedule=("xor",),
        hypothesis_ids=("H1_credit_efficiency",),
        hypothesis_registry_path=state_dir / "hypotheses.json",
        use_icu_guided=False,
    )
    LoopDriver(cfg).run(dry_run=False)

    # Check hypothesis registry
    import json

    registry_path = state_dir / "hypotheses.json"
    if registry_path.exists():
        with registry_path.open() as f:
            data = json.load(f)
        for hyp in data.get("hypotheses", []):
            if hyp["id"] == "H1_credit_efficiency":
                print(f"Hypothesis: {hyp['id']}")
                print(f"  Status: {hyp.get('status', 'unknown')}")
                print(f"  Tested at: {hyp.get('tested_at', 'never')}")
                if hyp.get("result"):
                    result = hyp["result"]
                    print(f"  p_value: {result.get('p_value')}")
                    print(f"  effect_size: {result.get('effect_size')}")
                    print(f"  significant: {result.get('significant')}")
                    print(f"  n_samples: {result.get('n_samples')}")
                    print(f"  groups_tested: {result.get('groups_tested')}")
                break

    # Check store records
    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        for run in store.query_runs():
            recs = store.query_records(run_id=run.run_id)
            print(f"\nRUN {run.run_id[:8]} n={len(recs)}")
            from collections import Counter

            print("  credits:", dict(Counter(r.credit for r in recs)))
            print("  maturity:", dict(Counter(r.status.maturity.value for r in recs)))
            print("  verdict:", dict(Counter(r.status.gate_verdict.name for r in recs)))

    tmp.cleanup()


if __name__ == "__main__":
    main()
