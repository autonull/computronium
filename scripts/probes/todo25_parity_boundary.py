"""F5 (TODO25): certify the sequence-parity boundary as a CEEC boundary belief.

Protocol (TODO24 §9 / CEEC-Core §19):
1. Defect hunt — the task pipeline is shared with last_symbol
   (0.918-0.922 @ 120ep recorded), so the generator is sound; the
   parity-specific shuffle control rides the corpus ``::shuffled`` arm.
2. Lever sweep — equal-compute lr sweep at a short budget; any lever
   breaking chance refutes the boundary.
3. Certified confirm — recorded operating point (120 ep x 3 seeds) must
   sit at chance.

Informs the boundary declaration in ``docs/research/todo24/cookbook.md``;
the belief + evidence + ``declare_boundary`` record is assembled from the
JSON result once the campaign is green.

Usage: uv run python scripts/probes/todo25_parity_boundary.py
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import torch
from ceec.builders import chance_verdict
from computronium_lab.research.corpus import _row
from computronium_lab.sequential import train_sequence
from computronium_lab.synthesis.spec import Constraints, ProblemSpec

SEEDS = (0, 1, 2)
CERT_EPOCHS = 120
SWEEP_EPOCHS = 20
# recorded val split: 32 episodes; the chance band is 2 x binomial SE over
# that split (sqrt(0.25/32) x 2 = 0.177) — derived from the eval size,
# never fixed (TODO25 D.4: the B.1 statistics now live in ceec.builders).
N_EVAL = 32
OUT = Path("scratch/todo25_parity_boundary.json")


def _run(mechanism: str, *, lr: float, epochs: int, seed: int) -> float:
    spec = ProblemSpec(
        task="sequence_parity",
        dataset="synthetic_sequences",
        constraints=Constraints(),
        input_dim=8,
        num_classes=2,
    )
    torch.manual_seed(seed)
    random.seed(seed)
    system = _row(mechanism).build(spec)
    result = train_sequence(system, "parity", epochs=epochs, seed=seed, lr=lr)
    return float(result.accuracy)


def main() -> int:
    torch.set_num_threads(4)
    report: dict[str, object] = {
        "defect_hunt": {
            "note": (
                "task pipeline shared with last_symbol (0.918-0.922 @ "
                "120ep recorded), so the generator itself is sound; "
                "parity-specific shuffle control = corpus `::shuffled` arm"
            )
        }
    }

    levers = [{"mechanism": "ntm_classifier", "lr": lr} for lr in (0.1, 0.01, 0.3)]
    sweep = []
    for lever in levers:
        acc = _run(lever["mechanism"], lr=lever["lr"], epochs=SWEEP_EPOCHS, seed=0)
        verdict = chance_verdict([acc], n_eval=N_EVAL)
        sweep.append({
            **lever,
            "accuracy": acc,
            "at_chance": bool(verdict.per_seed_in_band[0]),
        })
        print(f"sweep {lever} -> {acc:.3f}", flush=True)
    report["lever_sweep"] = sweep
    levers_exhausted = all(s["at_chance"] for s in sweep)
    report["levers_exhausted"] = levers_exhausted

    certified = []
    for seed in SEEDS:
        acc = _run("ntm_classifier", lr=0.1, epochs=CERT_EPOCHS, seed=seed)
        certified.append(acc)
        print(f"certified seed {seed} -> {acc:.3f}", flush=True)
    verdict = chance_verdict(certified, n_eval=N_EVAL)
    at_chance, mean = verdict.at_chance, verdict.mean
    report["certified"] = {
        "epochs": CERT_EPOCHS,
        "seeds": list(SEEDS),
        "accuracies": certified,
        "mean": mean,
        "per_seed_band": verdict.per_seed_band,
        "at_chance": at_chance,
        "verdict_rule": "abs(mean - 0.5) <= 2 * SE(n=3) (ceec.builders.chance_verdict)",
    }

    boundary_supported = levers_exhausted and at_chance
    report["boundary_supported"] = boundary_supported
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["certified"], indent=2), flush=True)
    print(f"boundary_supported={boundary_supported}", flush=True)
    return 0 if boundary_supported else 1


if __name__ == "__main__":
    raise SystemExit(main())
