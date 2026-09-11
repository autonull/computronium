"""CEEC-Core quickstart: ledger init, evidence, belief, experiment, audit."""

from __future__ import annotations

import tempfile
from pathlib import Path

from ceec.audit import run_audit
from ceec.store import now

from ceec import CEECStore, models


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        with CEECStore(root / "ceec.sqlite3", root / "artifacts") as store:
            artifact = store.ingest_artifact(b"probe results", "probe_output")
            scope = models.Scope(
                domain="credit", credit=("random_projections",), budget="quick"
            )
            evidence = store.record_evidence(
                kind="vector",
                scope=scope,
                artifact_refs=[artifact.id],
                axes=["improvement_per_norm"],
                values_ref=artifact.id,
                notes="quickstart probe evidence",
            )
            belief = store.create_belief(
                statement="Adaptive feedback improves local descent quality",
                type_="mechanism",
                scope=scope,
                evidence_refs=[evidence.id],
            )
            experiment = store.pre_register_experiment(
                models.Experiment(
                    id="X-QUICKSTART-001",
                    question="Does the improvement persist at 3 seeds?",
                    rationale="quickstart demo",
                    scope=scope,
                    target_beliefs=[belief.id],
                    target_goals=[],
                    design={"seeds": 3},
                    prediction="mean improvement >= 0.10 across seeds",
                    controls=["fixed_random_feedback"],
                    metrics=["improvement_per_norm"],
                    budget="quick",
                    falsification_criterion="No consistent improvement across seeds.",
                    overturn_criterion="n/a (demo)",
                    hard_gates=["coordinate_valid"],
                    status="draft",
                    created_at=now(),
                )
            )
            store.set_experiment_status(experiment.id, "completed")
            findings = run_audit(store)
            print(f"artifact: {artifact.id}")
            print(f"evidence: {evidence.id}")
            print(f"belief: {belief.id}")
            print(f"experiment: {experiment.id} (completed)")
            print(f"audit: {len(findings)} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
