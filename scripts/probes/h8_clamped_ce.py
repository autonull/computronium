"""H8 probe (TODO12b): is GradientCredit's loss the CLAMPED-output CE?

Verdict (2026-09-06): CONFIRMED at the code level; distortion quantified
as SMALL — one-line caveat on bp baselines, no re-runs needed.

Code path: pipeline.py computes the NUDGED loss on the settle output,
whose final layer is `out + beta*(onehot - out)` (_dynamics.py, the
instantaneous nudge). GradientCredit then takes autograd through that
blended surface.

Measured (2-layer 784-128-10 CE net, batch 64, seed 0):
- beta=0.1: cos(first)=1.0000 cos(last)=0.9997 scale(last)=0.886
- beta=0.5: cos(first)=0.9993 cos(last)=0.9901 scale(last)=0.461
    (≈ 1-beta on the output weight, chain rule through the blend)
- beta=1.0: cos=0.0000 scale=0.0000 — output fully clamped to the
  one-hot, the loss is CONSTANT w.r.t. params, the gradient is EXACTLY
  ZERO. beta=1.0 is not "target-pulling", it is a dead loss surface.

Conclusion: bp baselines at HEAD are (1-beta)-scaled target-blended
backprop; at the default beta=0.5 the direction is preserved
(cos >= 0.99) and the scale is halved on the output weight. Relative
margins between arms sharing the pipeline are unaffected; absolute bp
numbers carry a ~2x last-layer scale caveat. NEVER set beta=1.0 with
GradientCredit — the pseudo-gradient is exactly zero.
"""

import time

import torch
from torch import nn


def _probe(beta: float) -> tuple[float, float, float]:
    torch.manual_seed(0)
    net = nn.Sequential(nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))
    x = torch.randn(64, 784)
    y = torch.randint(0, 10, (64,))
    ce = nn.CrossEntropyLoss()
    free = net(x)
    onehot = torch.nn.functional.one_hot(y, 10).float()
    clamped = free + beta * (onehot - free)
    g_free = torch.autograd.grad(ce(free, y), list(net.parameters()), retain_graph=True)
    g_clamp = torch.autograd.grad(ce(clamped, y), list(net.parameters()))
    cosines = [
        torch.dot(a.flatten(), b.flatten()) / (a.norm() * b.norm() + 1e-12)
        for a, b in zip(g_free, g_clamp, strict=True)
    ]
    scales = [
        b.norm() / (a.norm() + 1e-12) for a, b in zip(g_free, g_clamp, strict=True)
    ]
    return cosines[0].item(), cosines[-1].item(), scales[-1].item()


def main() -> None:
    t0 = time.perf_counter()
    for beta in (0.1, 0.5, 1.0):
        cos_first, cos_last, scale_last = _probe(beta)
        print(
            f"beta={beta}: cos(first)={cos_first:.4f} cos(last)={cos_last:.4f} "
            f"scale(last)={scale_last:.4f} (1-beta={1 - beta:.2f})"
        )
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
