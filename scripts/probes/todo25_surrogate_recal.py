"""F6 (TODO25): surrogate-vs-campaign rank comparison at a certified
operating point.

Round 2 re-scored H24.2 on flat_classification (20ep, 1 seed/row) and
measured Spearman rho = 0.418 with saturation censoring (6/10 rows at
1.0). Round 3 (``todo25_recal_record.py``) runs the closed-loop
equivalent on flat_classification_hard through ``ceec.run.run_experiment``;
this probe remains the standalone comparator for any registered task:

- candidate rows come from ``MechanismCandidate.trainable_on`` (TODO25
  D.1) — no exception-driven skipping;
- ``spearman_rho`` (average-rank ties) comes from
  ``computronium.validation.statistics`` (TODO25 D.4).

Usage: uv run python scripts/probes/todo25_surrogate_recal.py \
          [--task flat_classification] [--epochs 20] [--seed 0]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from computronium_lab import Lab
from computronium_lab.research.autopoiesis import (
    CampaignFitness,
    CoordinateGenome,
    SurrogateFitness,
)
from computronium_lab.research.corpus import problem_class_defaults
from computronium_lab.synthesis.catalog import CATALOG

from computronium.validation.statistics import spearman_rho

DEFAULT_TASK = "flat_classification"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", default=DEFAULT_TASK)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    torch.set_num_threads(4)
    defaults = problem_class_defaults(args.task)
    spec = Lab().specify(
        args.task,
        str(defaults["dataset"]),
        input_dim=int(defaults.get("input_dim", 32)),
        num_classes=int(defaults.get("num_classes", 4)),
    )
    rows = [c.name for c in CATALOG if c.trainable_on_task(args.task)]
    surrogate = SurrogateFitness(spec)
    fitness = CampaignFitness(spec)
    lab = Lab(seed=args.seed)
    surrogate_scores: dict[str, float] = {}
    campaign_acc: dict[str, float] = {}
    for name in rows:
        genome = CoordinateGenome.seed(name, spec)
        surrogate_scores[name] = surrogate.screen(genome)
        evaluation = fitness.evaluate(
            genome, lab, seeds=(args.seed,), epochs=args.epochs
        )
        acc = float(evaluation.objectives.get("accuracy", 0.0))
        campaign_acc[name] = acc
        print(
            f"{name}: surrogate={surrogate_scores[name]:.3f} campaign={acc:.3f}",
            flush=True,
        )

    names = sorted(campaign_acc)
    rho = spearman_rho(
        [surrogate_scores[n] for n in names], [campaign_acc[n] for n in names]
    )
    agreement = sum(
        1
        for a, b in zip(
            sorted(names, key=lambda n: -surrogate_scores[n])[:3],
            sorted(names, key=lambda n: -campaign_acc[n])[:3],
            strict=True,
        )
        if a == b
    )
    saturated = [n for n, a in campaign_acc.items() if a >= 0.995]
    report: dict[str, Any] = {
        "task": args.task,
        "operating_point": {"epochs": args.epochs, "seed": args.seed},
        "rows": names,
        "surrogate_scores": surrogate_scores,
        "campaign_accuracy": campaign_acc,
        "spearman_rho": rho,
        "top3_agreement": agreement,
        "saturated_rows": saturated,
    }
    out = Path(f"scratch/todo25_surrogate_recal_{args.task}.json")
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        json.dumps(
            {"spearman_rho": rho, "top3_agreement": agreement, "saturated": saturated},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
