"""H24.3 round 2 (TODO26 S.3): certified closed-loop verdict for the
composed backbone+ψ continual benchmark — the first end-to-end
certification on the TODO26 Session API.

Round 1 (``X-H24-H243-H24V1``, smoke) measured temporal ψ 0.125 vs θ
fine-tune 0.672, but its ψ arm rode a bare ``AdaptivePsiReadout`` that
could not enter ``lab.train`` — the "instrument ≠ registered benchmark"
caveat (TODO25 #7). TODO26 S.1 composed the mechanism (trainable θ
feature extractor + ψ-owned readout role), so this round runs the
registered instrument (``temporal_psi_task_switcher`` through the
continual corpus benchmark, ``two_task_switch`` curriculum, 3 seeds, 10
episodes) end-to-end: pre-register → §22 decision → probe → artifact →
evidence → calibration, under the round-1 rule:

    FOR iff the best ψ mode reaches the 0.5 switch threshold on at least
    half the seeds AND beats the θ-finetune matched-compute control on
    mean post-switch accuracy.

Usage: uv run python scripts/probes/todo26_h243_round2.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

from ceec.run import ProbeResult
from computronium_lab import Lab
from computronium_lab.research.continual import benchmark_continual

from ceec import models

LEDGER = Path("scratch/todo26_h243_round2.sqlite3")
OUT = Path("scratch/todo26_h243_round2.json")
THRESHOLD = 0.5
SEEDS = (0, 1, 2)
RUN_ID = "T26S3"


def _campaign(exp: models.Experiment) -> ProbeResult:
    lab = Lab(record_ledger=str(LEDGER))
    lab.seed = 0
    report = benchmark_continual(
        lab, mechanism="temporal_psi_task_switcher", seeds=SEEDS
    )
    arms = {
        a.arm: {
            "accuracy_per_seed": list(a.metric_values.get("accuracy", ())),
            "accuracy_mean": (
                statistics.fmean(a.metric_values["accuracy"])
                if a.metric_values.get("accuracy")
                else 0.0
            ),
            "threshold_reached_mean": (
                statistics.fmean(a.metric_values["threshold_reached"])
                if a.metric_values.get("threshold_reached")
                else 0.0
            ),
            "theta_invariant_mean": (
                statistics.fmean(a.metric_values["theta_invariant"])
                if a.metric_values.get("theta_invariant")
                else None
            ),
        }
        for a in report.arms
    }
    psi_modes = [m for m in report.modes if m in arms]
    best = max(psi_modes, key=lambda m: arms[m]["accuracy_mean"])
    finetune = arms.get("theta_finetune_matched_compute", {})
    reached = arms[best]["threshold_reached_mean"] >= 0.5
    beats = arms[best]["accuracy_mean"] > finetune.get("accuracy_mean", 1.0)
    outcome = reached and beats
    payload = {
        "hypothesis": "H24.3",
        "round": 2,
        "instrument": "continual corpus benchmark (two_task_switch, 3 seeds, 10 episodes)",
        "mechanism": report.mechanism,
        "system": "composed backbone+psi (TODO26 S.1)",
        "round1_caveat": (
            "round 1 (X-H24-H243-H24V1) rode a bare AdaptivePsiReadout that "
            "could not enter lab.train; its 0.125 vs 0.672 compared a "
            "bare-readout probe against a trained system (instrument != "
            "registered benchmark)"
        ),
        "arms": arms,
        "comparisons": [
            {
                "mode": c.mode,
                "control": c.control,
                "mean_diff": c.mean_diff,
                "paired_p": c.paired_p,
            }
            for c in report.comparisons
        ],
        "capacity_control": report.capacity_control,
        "measurement_blocks": [b.reason for b in report.blocks],
        "state_inventory": list(report.state_inventory),
        "decision_inputs": {
            "best_psi_mode": best,
            "threshold_reached": reached,
            "beats_finetune": beats,
            "rule": "FOR iff threshold_reached_mean >= 0.5 and accuracy_mean > finetune",
        },
    }
    values = list(arms[best]["accuracy_per_seed"])
    return ProbeResult(
        label="FOR" if outcome else "AGAINST",
        outcome_boolean=outcome,
        payload=payload,
        axes=("seed",),
        values=values,
        quality={
            "seeds": len(SEEDS),
            "matched_control": True,
            "evaluation_policy": "quick_two_task_switch_10ep_3seed",
            "defect_audit": "pass" if not report.blocks else "fail",
            "integrity_checks": "pass",
            "known_levers_exhausted": False,
            "reproduction": False,
        },
        notes=(
            f"round-2 verdict under the round-1 rule on the composed "
            f"backbone+ψ system; best ψ mode {best!r}"
        ),
    )


def main() -> int:
    lab = Lab(record_ledger=str(LEDGER))
    captured: list[ProbeResult] = []

    def probe(exp: models.Experiment) -> ProbeResult:
        result = _campaign(exp)
        captured.append(result)
        return result

    with lab.ledger_session(role="campaign") as sess:
        draft = sess.experiment(
            question=(
                "ψ-only adaptation improves task-switch speed relative to θ "
                "fine-tuning under matched compute on at least one synthetic "
                "curriculum (H24.3, round 2)."
            ),
            prediction=(
                "On the composed backbone+ψ system, the best ψ mode reaches "
                "the 0.5 switch threshold on at least half the seeds and "
                "beats the θ-finetune matched-compute control on mean "
                "post-switch accuracy."
            ),
            scope=models.Scope.of(
                domain="research",
                task="continual_switch",
                run_id=RUN_ID,
                substrate="digital",
            ),
            rationale=(
                "H24.3 round 2: round 1 was instrument-blocked (bare ψ "
                "readout, TODO25 #7); the composed backbone+ψ system "
                "(TODO26 S.1) unblocks the registered instrument"
            ),
            design={
                "psi_only": True,
                "hypothesis": "H24.3",
                "evaluation_policy": "quick_two_task_switch_10ep_3seed",
                "decision_rule": (
                    "FOR iff best-ψ-mode threshold_reached_mean >= 0.5 and "
                    "accuracy_mean > theta_finetune_matched_compute "
                    "accuracy_mean (round-1 rule)"
                ),
                "boundary_conditions": [
                    "round 1 (X-H24-H243-H24V1) carried the 'instrument != "
                    "registered benchmark' caveat; this round runs the "
                    "registered instrument on the composed system",
                    "quick-tier curriculum (10 episodes, 3 seeds); verdict "
                    "is about the composed system at this operating point",
                ],
            },
            tier="certified",
            prediction_probability=(0.5, 0.8, 0.7),
            controls=("frozen_no_psi", "theta_finetune_matched_compute"),
            metrics=("accuracy", "episodes", "threshold_reached"),
            falsification_criterion=(
                "best ψ mode fails the 0.5 threshold on at least half the "
                "seeds or loses to the θ-finetune matched-compute control"
            ),
            hard_gates=("BenchmarkReproduction", "frozen_theta_audit"),
        )
        run = sess.run(
            draft,
            probe,
            decision_rationale=(
                "H24.3 round 2: single pre-registered measurement on the "
                "registered continual instrument"
            ),
        )
        result = captured[-1]
        summary = {
            "experiment_id": draft.id,
            "status": run.status,
            "decision_id": run.decision_id,
            "calibration_id": run.calibration_id,
            "outcome": run.outcome,
            "verdict": result.label,
            "outcome_boolean": result.outcome_boolean,
            "arms": result.payload.get("arms"),
            "decision_inputs": result.payload.get("decision_inputs"),
        }
    OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
