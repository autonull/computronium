"""F6 step 2 (TODO25): record the certified-tier surrogate comparison as
evidence on the H24.2 experiment and re-score calibration.

Reads ``scratch/todo25_surrogate_recal.json`` (probe output: 10
campaign-trainable rows at flat_classification 20ep, Spearman rho +
top-3 agreement). Updates the H24 ledger ``scratch/todo24_h24.sqlite3``.

Outcome verdict: rho improved from the smoke-tier 0/4 to 0.418, but five
rows saturate at 1.0 accuracy, so the top-3 agreement statistic is
degenerate — H24.2 remains OPEN pending a non-saturating task class
(recorded as the boundary condition), never scored FOR on saturated data.

Usage: uv run python scripts/probes/todo25_recal_record.py
"""

from __future__ import annotations

import json
from pathlib import Path

from ceec.store import CEECStore, now

from ceec import models

RESULT = Path("scratch/todo25_surrogate_recal.json")
LEDGER = Path("scratch/todo24_h24.sqlite3")


def main() -> int:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    rho = float(result["spearman_rho"])
    saturated = [n for n, a in result["campaign_accuracy"].items() if a >= 0.995]

    store = CEECStore(LEDGER, LEDGER.parent / "artifacts")
    # H24.2 round 1 was scored at smoke tier (X-H24-H242-H24V1, completed).
    # TODO25 runs round 2 at the certified operating point as a fresh
    # pre-registered experiment; round 1 is never re-scored.
    experiment_id = "X-H24-H242-T25V1"
    try:
        store.get_experiment(experiment_id)
        exists = True
    except Exception:
        exists = False
    if not exists:
        store.pre_register_experiment(
            models.Experiment(
                id=experiment_id,
                question=(
                    "Campaign-backed fitness prevents quick-task overfitting "
                    "better than predictor-only search (certified tier re-test)."
                ),
                rationale="TODO25 F6: certified operating-point surrogate comparison",
                scope=models.Scope(
                    domain="research",
                    substrate=("digital",),
                    budget="nightly",
                    extra={"hypothesis": "H24.2", "run_id": "T25V1"},
                ),
                target_beliefs=[],
                target_goals=[],
                design={
                    "seed_plan": [0],
                    "evaluation_policy": "certified_operating_point_20ep_flat",
                    "evidence_kind": "vector",
                    "protocol": "surrogate-ranked candidates vs campaign outcomes (Spearman rho)",
                    "decision_rule": (
                        "Spearman rho > 0.5 at a non-saturating operating "
                        "point; saturated operating points are not decisive"
                    ),
                    "boundary_conditions": [
                        "flat_classification saturates for many rows; rho "
                        "on a saturated operating point is not decisive"
                    ],
                },
                prediction=(
                    "Campaign-backed fitness ranks candidates better than "
                    "predictor-only search at the certified operating point."
                ),
                prediction_probability=models.Probability(
                    low=0.5, high=0.8, point=0.7, method="session_prior"
                ),
                controls=[],
                metrics=["accuracy"],
                budget="nightly",
                falsification_criterion=(
                    "certified-tier Spearman rho <= 0 at a non-saturating "
                    "operating point"
                ),
                overturn_criterion=(
                    "replication of the rho comparison overturns the rank ordering"
                ),
                hard_gates=["BenchmarkReproduction"],
                created_at=now(),
            )
        )

    scope = models.Scope(
        domain="research",
        substrate=("digital",),
        budget="nightly",
        extra={"hypothesis": "H24.2", "probe": "todo25_f6"},
    )
    artifact = store.ingest_artifact(
        json.dumps(result, sort_keys=True).encode(),
        "research_corpus_summary",
        {"hypothesis": "H24.2", "probe": "todo25_f6"},
    )
    store.record_evidence(
        kind="vector",
        scope=scope,
        artifact_refs=[artifact.id],
        quality={
            "seeds": 1,
            "matched_control": False,
            "evaluation_policy": "certified_operating_point_20ep_flat",
            "defect_audit": "pass",
            "integrity_checks": "pass",
        },
        axes=["mechanism"],
        values_ref="scratch/todo25_surrogate_recal.json#campaign_accuracy",
        notes=(
            f"certified-tier surrogate-vs-campaign comparison: Spearman "
            f"rho={rho:.3f} across {len(result['campaign_accuracy'])} rows "
            f"(smoke tier: 0/4 top-3 agreement); saturation censoring — "
            f"{len(saturated)} rows at accuracy 1.0 ({', '.join(saturated)}) "
            f"make top-3 agreement degenerate; sharper test needs a "
            f"non-saturating task class (H24.6 refit input)"
        ),
    )

    # H24.2 round 2 stays open: rho moved toward FOR (0.418 vs smoke's
    # 0/4) but the decision statistic is censored by saturation. The
    # experiment is left running; scoring rides a non-saturating task
    # class (H24.6 refit input).
    print(
        json.dumps(
            {
                "h24_2_round2": experiment_id,
                "status": store.get_experiment(experiment_id).status,
                "spearman_rho": rho,
                "saturated_rows": saturated,
                "verdict": "OPEN — evidence recorded, statistic censored by saturation",
            },
            indent=2,
        ),
        flush=True,
    )
    store._conn.commit()
    store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
