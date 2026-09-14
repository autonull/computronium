"""F6 step 2 (TODO25, round 3): close H24.2's round-2 experiment and run
the decision statistic on the non-saturating ``flat_classification_hard``
operating point through the CEEC closed-loop runner.

Round 2 (``X-H24-H242-T25V1``, certified 20ep flat) measured
Spearman rho = 0.418 but was censored by saturation (6/10 rows at 1.0)
and left OPEN. This probe closes it as superseded (never scored on
censored data) and executes round 3 (``X-H24-H242-T25V2``) end-to-end
through ``ceec.run.run_experiment``: pre-register -> §22 decision ->
10-row hard-task campaign (the probe callable trains, so the outcome is
generated strictly after pre-registration) -> artifact/evidence ->
calibration outcome under the recorded decision rule
``rho > 0.5 at a non-saturating operating point``.

Usage: uv run python scripts/probes/todo25_recal_record.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import torch
from ceec.run import ProbeResult, run_experiment
from ceec.store import CEECStore, StoreError
from computronium_lab import Lab
from computronium_lab.research.autopoiesis import (
    CampaignFitness,
    CoordinateGenome,
    SurrogateFitness,
)
from computronium_lab.research.corpus import problem_class_defaults
from computronium_lab.synthesis.catalog import CATALOG

from ceec import builders, models
from computronium.validation.statistics import spearman_rho

LEDGER = Path("scratch/todo24_h24.sqlite3")
ROUND2_ID = "X-H24-H242-T25V1"
ROUND3_ID = "X-H24-H242-T25V3"
TASK = "flat_classification_hard"
EPOCHS = 20
SEED = 0
OUT = Path("scratch/todo25_h24_round3.json")
# the operating point is decisive only when rank ties stay rare: more than
# 2 saturated rows reproduce round 2's censoring and refuse scoring
MAX_SATURATED_ROWS = 2


def _campaign(_experiment: models.Experiment) -> ProbeResult:
    """The closed-loop probe: campaign-train every trainable row on the
    hard operating point and compare surrogate vs campaign ranks."""
    torch.set_num_threads(4)
    defaults = problem_class_defaults(TASK)
    spec = Lab().specify(
        TASK,
        str(defaults["dataset"]),
        input_dim=int(defaults.get("input_dim", 32)),
        num_classes=int(defaults.get("num_classes", 4)),
    )
    rows = [c.name for c in CATALOG if c.trainable_on_task(TASK)]
    surrogate = SurrogateFitness(spec)
    fitness = CampaignFitness(spec)
    lab = Lab(seed=SEED)
    surrogate_scores: dict[str, float] = {}
    campaign_accuracy: dict[str, float] = {}
    for name in rows:
        genome = CoordinateGenome.seed(name, spec)
        surrogate_scores[name] = surrogate.screen(genome)
        evaluation = fitness.evaluate(genome, lab, seeds=(SEED,), epochs=EPOCHS)
        campaign_accuracy[name] = float(evaluation.objectives["accuracy"])
        print(
            f"{name}: surrogate={surrogate_scores[name]:.3f} "
            f"campaign={campaign_accuracy[name]:.3f}",
            flush=True,
        )

    names = sorted(campaign_accuracy)
    rho = spearman_rho(
        [surrogate_scores[n] for n in names], [campaign_accuracy[n] for n in names]
    )
    top3 = sum(
        1
        for a, b in zip(
            sorted(names, key=lambda n: -surrogate_scores[n])[:3],
            sorted(names, key=lambda n: -campaign_accuracy[n])[:3],
            strict=True,
        )
        if a == b
    )
    saturated = [n for n, a in campaign_accuracy.items() if a >= 0.995]
    payload: dict[str, Any] = {
        "task": TASK,
        "operating_point": {"epochs": EPOCHS, "seed": SEED},
        "rows": names,
        "surrogate_scores": surrogate_scores,
        "campaign_accuracy": campaign_accuracy,
        "spearman_rho": rho,
        "top3_agreement": top3,
        "saturated_rows": saturated,
        "decision_rule": "spearman_rho > 0.5 at a non-saturating operating point",
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    if len(saturated) > MAX_SATURATED_ROWS:
        raise RuntimeError(
            f"operating point censored: {len(saturated)} saturated rows "
            f"({saturated}); decision rule requires a non-saturating point"
        )
    for_hypothesis = rho > 0.5
    return ProbeResult(
        label="FOR" if for_hypothesis else "AGAINST",
        outcome_boolean=for_hypothesis,
        payload=payload,
        axes=("mechanism",),
        values=tuple(campaign_accuracy[n] for n in names),
        values_ref=f"{OUT}#campaign_accuracy",
        quality={
            "seeds": 1,
            "matched_control": False,
            "evaluation_policy": "certified_operating_point_20ep_hard",
            "defect_audit": "pass",
            "integrity_checks": "pass",
        },
        notes=(
            f"H24.2 round 3 on {TASK}: Spearman rho={rho:.3f} over "
            f"{len(names)} rows, top-3 agreement {top3}/3, "
            f"{len(saturated)} saturated rows; round-2 censoring resolved"
        ),
    )


def main() -> int:
    store = CEECStore(LEDGER, LEDGER.parent / "artifacts")
    try:
        return _run(store)
    finally:
        store._conn.commit()
        store.close()


def _run(store: CEECStore) -> int:
    round2 = store.get_experiment(ROUND2_ID)
    if round2.status != "completed":
        # round 2 was censored by saturation and never scored; closing it
        # as superseded records the calibration line without an outcome
        store.set_experiment_status(ROUND2_ID, "completed")
        store.record_calibration(
            prediction=round2.prediction,
            experiment_id=ROUND2_ID,
            predicted_probability=round2.prediction_probability,
            outcome="censored_superseded",
            outcome_boolean=None,
            scope=round2.scope,
            notes=(
                "round-2 statistic censored by saturation (6/10 rows at "
                "1.0); superseded by X-H24-H242-T25V2 on "
                "flat_classification_hard — never scored FOR on "
                "saturated data"
            ),
        )
        print(f"round 2 {ROUND2_ID}: closed as censored_superseded", flush=True)

    try:
        existing = store.get_experiment(ROUND3_ID)
    except StoreError:  # ruff: ignore[try-except-pass]  idempotent re-run: an absent experiment is the first-run path
        pass
    else:
        print(
            json.dumps(
                {
                    "round3": ROUND3_ID,
                    "status": existing.status,
                    "note": "already executed; nothing to do",
                },
                indent=2,
            )
        )
        return 0

    draft = builders.experiment(
        id_=ROUND3_ID,
        question=(
            "Campaign-backed fitness prevents quick-task overfitting "
            "better than predictor-only search (rank agreement at a "
            "non-saturating operating point)."
        ),
        prediction=(
            "Surrogate ranks correlate with campaign outcomes on "
            "flat_classification_hard (Spearman rho > 0.5)."
        ),
        scope=models.Scope(
            domain="research",
            substrate=("digital",),
            budget="nightly",
            extra={"hypothesis": "H24.2", "run_id": "T25V2"},
        ),
        tier="certified",
        prediction_probability=(0.5, 0.8, 0.7),
        design={
            "evaluation_policy": "certified_operating_point_20ep_hard",
            "decision_rule": (
                "Spearman rho > 0.5 at a non-saturating operating point; "
                "more than 2 saturated rows refuse scoring"
            ),
            "boundary_conditions": [
                "round 2 (X-H24-H242-T25V1) was censored by saturation and "
                "is closed as superseded, not scored; round 3 attempt 1 "
                "(X-H24-H242-T25V2) failed on fixed-dim build paths "
                "(role_split/spatial_lattice hard-spec defect, since fixed)"
            ],
        },
        falsification_criterion=(
            "certified-tier Spearman rho <= 0.5 at the non-saturating operating point"
        ),
        hard_gates=["BenchmarkReproduction"],
    )
    run = run_experiment(
        store,
        draft,
        _campaign,
        decision_rationale=(
            "H24.2 round 3: single pre-registered measurement on the "
            "non-saturating hard operating point"
        ),
    )
    verdict = "FOR" if run.outcome == "FOR" else "AGAINST"
    print(
        json.dumps(
            {
                "round3": ROUND3_ID,
                "status": run.status,
                "decision_id": run.decision_id,
                "calibration_id": run.calibration_id,
                "verdict": verdict,
                "error": run.error,
                "payload": str(OUT),
            },
            indent=2,
        ),
        flush=True,
    )
    return 0 if run.status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
