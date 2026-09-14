"""F6 (TODO25): surrogate-vs-campaign rank comparison at the certified
operating point (flat_classification, 20 epochs, 1 seed per row).

Re-scores H24.2: TODO24 smoke found 0/4 rank agreement at 1 epoch
(noise-dominated); the certified operating point is the recorded
comparison that the hypothesis actually asks about.

Writes ``scratch/todo25_surrogate_recal.json``; informs a H24.6 refit.

Usage: uv run python scripts/probes/todo25_surrogate_recal.py
"""

from __future__ import annotations

import json
from pathlib import Path

import torch
from computronium_lab import Lab
from computronium_lab.research.autopoiesis import (
    CampaignFitness,
    CoordinateGenome,
    SurrogateFitness,
)
from computronium_lab.research.corpus import _row
from computronium_lab.synthesis.catalog import CATALOG
from computronium_lab.synthesis.spec import Constraints, ProblemSpec

EPOCHS = 20
SEED = 0
OUT = Path("scratch/todo25_surrogate_recal.json")


def _spearman(a: list[float], b: list[float]) -> float:
    def _ranks(xs: list[float]) -> list[float]:
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        ranks = [0.0] * len(xs)
        for rank, i in enumerate(order):
            ranks[i] = float(rank)
        return ranks

    ra, rb = _ranks(a), _ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb, strict=True))
    da = sum((x - ma) ** 2 for x in ra) ** 0.5
    db = sum((y - mb) ** 2 for y in rb) ** 0.5
    return num / (da * db) if da and db else 0.0


def main() -> int:
    torch.set_num_threads(4)
    spec = ProblemSpec(
        task="flat_classification",
        dataset="gaussian_blob",
        constraints=Constraints(),
        input_dim=32,
        num_classes=4,
    )
    surrogate = SurrogateFitness(spec)
    lab = Lab(seed=SEED)
    rows = [c.name for c in CATALOG if "digital" in c.substrates]
    rows = [r for r in rows if _constructible(r, spec)]
    surrogate_scores: dict[str, float] = {}
    campaign_acc: dict[str, float] = {}
    fitness = CampaignFitness(spec)
    for name in rows:
        genome = CoordinateGenome.seed(name, spec)
        surrogate_scores[name] = surrogate.screen(genome)
        try:
            evaluation = fitness.evaluate(genome, lab, seeds=(SEED,), epochs=EPOCHS)
        except Exception as exc:
            # Not campaign-trainable on this spec (e.g. psi-readout rows
            # without a geometry): excluded from the rank comparison,
            # like the evolution kernel's skipped candidates.
            print(f"{name}: campaign skipped ({type(exc).__name__})", flush=True)
            continue
        acc = float(evaluation.objectives.get("accuracy", 0.0))
        campaign_acc[name] = acc
        print(
            f"{name}: surrogate={surrogate_scores[name]:.3f} campaign={acc:.3f}",
            flush=True,
        )

    names = sorted(campaign_acc)
    rho = _spearman(
        [surrogate_scores[n] for n in names], [campaign_acc[n] for n in names]
    )
    agreement = sum(
        1
        for a, b in zip(
            sorted(names, key=lambda n: -surrogate_scores[n])[:3],
            sorted(names, key=lambda n: -campaign_acc[n])[:3],
        )
        if a == b
    )
    report = {
        "operating_point": {"epochs": EPOCHS, "seed": SEED},
        "rows": names,
        "surrogate_scores": surrogate_scores,
        "campaign_accuracy": campaign_acc,
        "spearman_rho": rho,
        "top3_agreement": agreement,
    }
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"spearman_rho": rho, "top3_agreement": agreement}, indent=2))
    return 0


def _constructible(name: str, spec: ProblemSpec) -> bool:
    try:
        _row(name).build(spec)
    except Exception as exc:
        print(f"{name}: not constructible ({type(exc).__name__})", flush=True)
        return False
    else:
        return True


if __name__ == "__main__":
    raise SystemExit(main())
