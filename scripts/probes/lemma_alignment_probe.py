"""LEMMA redemption diagnostic (TODO15 §11 follow-up): is the LEMMA
pseudo-gradient a suppressed-but-real learning direction, or noise?

Method: per batch, compute (a) LEMMA pseudo-gradients
(LocalGoodnessCredit, local_objective="pepita", fixed-B, the rung that
measured 0.306 × Muon) and (b) true BP gradients (autograd CE through
the same instantaneous forward); track per-layer cosine alignment over
30 batches on width-64×2 MNIST.

Decision (pre-registered):
- mean hidden-layer cos > 0.15, stable → real signal suppressed by
  construction; redemption path is per-layer credit_norm / orthogonal
  B / local errors — run one cell.
- cos ≈ 0 or sign-oscillating → update direction is noise; LEMMA
  closure upgraded from config-bound to mechanism-bound.

uv run python scripts/probes/lemma_alignment_probe.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time
from itertools import islice

import torch
from torch import Tensor, nn

sys.path.insert(0, "scripts/probes")

from computronium import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalGoodnessCredit,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    create_task,
)
from computronium.ontology.credit import Phase

WIDTH = 64
DEPTH = 2
BATCHES = 30


def main() -> int:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # D8 trap: seed BEFORE the loader draw
    data = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in islice(task.get_dataloader("train"), BATCHES)
    ]

    torch.manual_seed(0)
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784, output_dim=10, hidden_dims=(WIDTH,) * DEPTH
        )
    )
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = LocalGoodnessCredit(
        CreditAssignmentConfig.local_goodness(
            feedback_scale=0.01, local_objective="pepita"
        )
    )
    linear_names = [
        f"{i}.weight" for i, m in enumerate(geometry._layers) if isinstance(m, nn.Linear)
    ]

    def bp_grads(x: Tensor, y: Tensor) -> dict[str, Tensor]:
        h = x
        for i, module in enumerate(geometry._layers):
            if isinstance(module, nn.Linear):
                w = geometry.params[f"{i}.weight"]
                b = geometry.params[f"{i}.bias"]
                h = h @ w.T + b
            else:
                h = module(h)
        loss = nn.functional.cross_entropy(h, y)
        grads = torch.autograd.grad(loss, [geometry.params[n] for n in linear_names])
        return dict(zip(linear_names, grads, strict=True))

    cos_hist: list[list[float]] = []
    for x, y in data:
        free = dynamics.settle(SystemState(x=x, y=y), geometry, substrate, None)
        nudged = dynamics.settle(SystemState(x=x, y=y), geometry, substrate, y)
        states = {Phase.FREE: free, Phase.NUDGED: nudged}
        lemma = credit.compute_pseudo_gradient(states, None, geometry)
        bp = bp_grads(x, y)
        row = []
        for n, g_bp in zip(linear_names, bp.values(), strict=False):
            g_lm = dict(zip(linear_names, lemma, strict=True))[n]
            row.append(
                nn.functional.cosine_similarity(
                    g_lm.flatten().float(), g_bp.flatten().float(), dim=0
                ).item()
            )
        cos_hist.append(row)

    per_layer = list(zip(*cos_hist, strict=True))
    for i, layer in enumerate(per_layer):
        mean = sum(layer) / len(layer)
        print(
            f"layer {i}: cos mean {mean:+.3f}  first {layer[0]:+.3f}  last {layer[-1]:+.3f}",
            flush=True,
        )
    hidden = per_layer[1:]
    hidden_mean = sum(sum(v) / len(v) for v in hidden) / max(len(hidden), 1)
    if hidden_mean > 0.15:
        verdict = (
            f"REAL SIGNAL (hidden cos {hidden_mean:+.3f} > 0.15) — "
            "suppressed direction; run normalization redemption cell"
        )
    elif hidden_mean < 0.05:
        verdict = (
            f"NOISE (hidden cos {hidden_mean:+.3f} < 0.05) — "
            "LEMMA closure upgraded to mechanism-bound"
        )
    else:
        verdict = (
            f"BORDERLINE (hidden cos {hidden_mean:+.3f}) — "
            "weak signal; one normalization cell decides"
        )
    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
