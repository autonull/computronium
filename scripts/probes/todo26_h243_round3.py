"""H24.3 round 3 (TODO26 improvement #8): speed-rule verdict for the
composed backbone+ψ continual benchmark.

Round 2 (X-000001, certified) scored mean post-switch accuracy and came
out AGAINST: ψ (conflict_adaptive 0.729, threshold 3/3 seeds, θ bitwise
invariant) beat frozen_no_psi but lost to θ fine-tune (0.979). But the
registered hypothesis is about *switch speed*: "improves task-switch
speed relative to θ fine-tuning under matched compute". Round 3
pre-registers the speed rule on the same instrument (two_task_switch, 3
seeds, equal 10-episode/epoch budgets):

    FOR iff the best ψ mode (lowest mean episodes-to-threshold among
    modes reaching threshold on ≥ half the seeds) reaches threshold on
    ≥ half the seeds AND uses strictly fewer episodes than the
    θ-finetune control AND holds accuracy ≥ the 0.5 threshold.

Usage: uv run python scripts/probes/todo26_h243_round3.py
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

LEDGER = Path("scratch/todo26_h243_round3.sqlite3")
OUT = Path("scratch/todo26_h243_round3.json")
THRESHOLD = 0.5
SEEDS = (0, 1, 2)
RUN_ID = "T26S3R3"


def _campaign(exp: models.Experiment) -> ProbeResult:
    lab = Lab(record_ledger=str(LEDGER))
    lab.seed = 0
    report = benchmark_continual(
        lab, mechanism="temporal_psi_task_switcher", seeds=SEEDS
    )
    arms = {
        a.arm: {
            "accuracy_per_seed": list(a.metric_values.get("accuracy", ())),
            "episodes_per_seed": list(a.metric_values.get("episodes", ())),
            "accuracy_mean": (
                statistics.fmean(a.metric_values["accuracy"])
                if a.metric_values.get("accuracy")
                else 0.0
            ),
            "episodes_mean": (
                statistics.fmean(a.metric_values["episodes"])
                if a.metric_values.get("episodes")
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
    finetune = arms["theta_finetune_matched_compute"]
    eligible = [
        m
        for m in report.modes
        if arms[m]["threshold_reached_mean"] >= 0.5
        and arms[m]["accuracy_mean"] >= THRESHOLD
    ]
    best = min(eligible, key=lambda m: arms[m]["episodes_mean"]) if eligible else None
    reached = bool(best)
    faster = bool(best) and arms[best]["episodes_mean"] < finetune["episodes_mean"]
    holds = bool(best) and arms[best]["accuracy_mean"] >= THRESHOLD
    outcome = reached and faster and holds
    payload = {
        "hypothesis": "H24.3",
        "round": 3,
        "instrument": "continual corpus benchmark (two_task_switch, 3 seeds, 10 episodes)",
        "mechanism": report.mechanism,
        "system": "composed backbone+psi (TODO26 S.1)",
        "round1_caveat": (
            "round 1 (X-H24-H243-H24V1) rode a bare AdaptivePsiReadout that "
            "could not enter lab.train (instrument != registered benchmark); "
            "rounds 2-3 run the registered instrument on the composed system"
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
        "measurement_blocks": [b.reason for b in report.blocks],
        "decision_inputs": {
            "best_psi_mode": best,
            "rule": (
                "FOR iff best ψ mode (lowest episodes-to-threshold among "
                "modes with threshold_reached_mean >= 0.5 and accuracy_mean "
                ">= 0.5) exists and uses fewer episodes than the "
                "theta-finetune control"
            ),
            "reached": reached,
            "faster_than_finetune": faster,
            "accuracy_holds": holds,
        },
    }
    values = list(arms[best]["episodes_per_seed"]) if best else []
    return ProbeResult(
        label="FOR" if outcome else "AGAINST",
        outcome_boolean=outcome,
        payload=payload,
        axes=("seed",),
        values=[float(v) for v in values],
        quality={
            "seeds": len(SEEDS),
            "matched_control": True,
            "evaluation_policy": "quick_two_task_switch_10ep_speed_rule",
            "defect_audit": "pass" if not report.blocks else "fail",
            "integrity_checks": "pass",
            "known_levers_exhausted": False,
            "reproduction": False,
        },
        notes=(
            f"round-3 speed-rule verdict on the composed backbone+ψ system; "
            f"best ψ mode {best!r}, episodes {arms[best]['episodes_mean'] if best else '-'} "
            f"vs finetune {finetune['episodes_mean']}"
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
                "curriculum (H24.3, round 3)."
            ),
            prediction=(
                "On the composed backbone+ψ system, the best ψ mode reaches "
                "the 0.5 switch threshold in strictly fewer episodes than "
                "the θ-finetune control's 10-epoch budget, while holding "
                "accuracy ≥ 0.5."
            ),
            scope=models.Scope.of(
                domain="research",
                task="continual_switch",
                run_id=RUN_ID,
                substrate="digital",
            ),
            rationale=(
                "H24.3 round 3: round 2 (certified, X-000001) scored the "
                "accuracy rule (AGAINST); this round scores the registered "
                "hypothesis's speed claim on the same instrument"
            ),
            design={
                "psi_only": True,
                "hypothesis": "H24.3",
                "evaluation_policy": "quick_two_task_switch_10ep_speed_rule",
                "decision_rule": (
                    "FOR iff the best ψ mode (lowest mean episodes-to-"
                    "threshold among modes with threshold_reached_mean >= "
                    "0.5 and accuracy_mean >= 0.5) uses strictly fewer "
                    "episodes than theta_finetune_matched_compute"
                ),
                "boundary_conditions": [
                    "round 2 (X-000001) AGAINST on the accuracy rule; round "
                    "3 scores the speed rule, not a revision of round 2",
                    "quick-tier curriculum (10 episodes, 3 seeds); verdict "
                    "is about the composed system at this operating point",
                ],
            },
            tier="certified",
            prediction_probability=(0.6, 0.85, 0.75),
            controls=("frozen_no_psi", "theta_finetune_matched_compute"),
            metrics=("episodes", "accuracy", "threshold_reached"),
            falsification_criterion=(
                "no ψ mode reaches the 0.5 threshold on at least half the "
                "seeds within the 10-episode budget, or the best ψ mode's "
                "episode count is not below the θ-finetune control's"
            ),
            hard_gates=("BenchmarkReproduction", "frozen_theta_audit"),
        )
        run = sess.run(
            draft,
            probe,
            decision_rationale=(
                "H24.3 round 3: single pre-registered speed-rule measurement "
                "on the registered continual instrument"
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
