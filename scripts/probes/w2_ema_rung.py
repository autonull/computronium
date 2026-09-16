"""W2-P3 probe: does EMA (momentum) credit normalization lift the depth wall?

VERDICT (2026-09-07, 150-step regime, 784-128^k-10, seeds 0-2,
scalar per-layer EMA of mean(gw^2), per-element-displacement lr):

- **P3 CONFIRMED.** Where instantaneous (unit-RMS) normalization
  stays collapsed at high lr (d2 ~0.52, d4 ~0.19-0.20 across the whole
  1e-3..0.1 grid), the EMA rung lifts cleanly:
    d2 EMA lr 0.3 → 0.824  (raw-LR reference 0.827 — parity)
    d4 EMA lr 0.3 → 0.757  (raw reference 0.764 — within noise)
    d8 EMA lr 0.3 → 0.512  (first training ever at depth 8 in this
                            class; chance = 0.10, instantaneous 0.10-0.16)
- Mechanism confirmed: satisfied-gate near-zero gradients decay
  smoothly under the EMA denominator instead of being re-amplified
  into destructive steps. EMA needs the HIGH-lr regime (0.1-0.3) to
  pay off; at 1e-3-0.01 normalized rungs are just slow (~0.5 d2).
- Depth scaling under EMA: 0.824 → 0.757 → 0.512 (d2/d4/d8) —
  graceful, not walled. Open follow-ups: longer budgets at d8,
  matrix-EMA vs scalar-EMA, beta sweep, stream-norm interaction.
- Harness note: negatives must be wrong-label (onehot.roll(1,0),
  Hinton/b4), NOT 1-pos — the hybrid negative kills the goodness
  contrast (whole grid at chance until fixed). Bias-correct the EMA
  (ema/(1-beta^t)) — raw EMA ~0 at t=1 explodes the first step.

Pre-registered (TODO13b W2 build spec item 3, written before any run):
- P3: EMA-normalized credit gradients lift depth-4 accuracy ABOVE the
  instantaneous-collapse floor (d4 raw = 0.764, b4 reference; the d2→d4
  wall 0.827→0.764 is the known boundary of the class).
- Falsified → the depth wall survives the last untried repair in this
  class; name it honestly (TODO13b §6 branch logic).

Mechanism under test: instantaneous normalization of the goodness
gradient collapses learning (b4: d8 ~0.10-0.16, not an lr artifact —
a layer whose softplus gate is satisfied has near-zero gradient;
renormalizing re-amplifies it into a full-size destructive step every
batch). The EMA rung keeps a momentum estimate of per-layer gradient
magnitude: step = norm_lr * gw / sqrt(ema_sq + eps), ema_sq updated
with decay beta. Satisfied gates then decay SLOWLY instead of being
re-amplified — the one repair instantaneous norm cannot make.

Reference pattern: scripts/probes/b4_per_layer_ff.py verbatim (per-layer
recompute, Hinton stream normalization, softplus-gated goodness
contrast). Numbers cite TODO13b W2 / future D-table.
"""

import itertools
import time
from typing import TYPE_CHECKING, cast

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor, nn

if TYPE_CHECKING:
    from computronium.domains.base import DomainTask

from computronium.domains.factory import create_task

STEPS = 150
THRESHOLD = 2.0
LR = 0.5
N_CLASSES = 10


def _data() -> tuple[list, list]:
    task = cast("DomainTask", create_task("mnist", device="cpu", quick_mode=True))
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in itertools.islice(task.get_dataloader("train"), STEPS)
    ]
    test = [
        (xb.view(xb.size(0), -1), yb)
        for xb, yb in task.get_dataloader("test")
        if xb.size(0) == 32
    ]
    return train, test


def _label_input(x: Tensor, y: Tensor, good: bool) -> Tensor:
    onehot = F.one_hot(y, N_CLASSES).float()
    if not good:
        onehot = onehot.roll(1, 0)  # wrong-label negative (Hinton/b4 recipe)
    z = torch.cat([x, onehot], dim=-1)
    return z / (z.norm(dim=-1, keepdim=True) + 1e-12) * z.shape[-1] ** 0.5


class PerLayerFF(nn.Module):
    def __init__(self, dims: tuple[int, ...]):
        super().__init__()
        self.linears = nn.ModuleList(
            nn.Linear(a, b) for a, b in itertools.pairwise(dims)
        )
        self.readout = nn.Linear(dims[-1], N_CLASSES)

    @property
    def layers(self) -> list[nn.Linear]:
        return cast("list[nn.Linear]", list(self.linears))

    @torch.no_grad()
    def _stream_input(self, x: Tensor, upto: int) -> Tensor:
        a = x
        for lin in self.layers[:upto]:
            a = F.relu(lin(a))
            a = a / (a.norm(dim=-1, keepdim=True) + 1e-12) * a.shape[-1] ** 0.5
        return a

    def local_grads(self, x_pos: Tensor, x_neg: Tensor) -> list[Tensor]:
        grads = []
        for i, lin in enumerate(self.layers):
            in_pos = self._stream_input(x_pos, i)
            in_neg = self._stream_input(x_neg, i)
            g_pos = F.relu(lin(in_pos)).pow(2).mean()
            g_neg = F.relu(lin(in_neg)).pow(2).mean()
            loss = F.softplus(THRESHOLD - (g_pos - g_neg))
            (gw,) = torch.autograd.grad(loss, lin.weight, retain_graph=False)
            grads.append(gw)
        return grads

    def features(self, x: Tensor) -> Tensor:
        a = x
        for lin in self.layers:
            a = F.relu(lin(a))
            a = a / (a.norm(dim=-1, keepdim=True) + 1e-12) * a.shape[-1] ** 0.5
        return a


def train_acc(
    hidden: tuple[int, ...],
    seed: int,
    beta: float,
    norm_lr: float,
    train: list[tuple[Tensor, Tensor]],
    test: list[tuple[Tensor, Tensor]],
) -> float:
    torch.manual_seed(seed)
    net = PerLayerFF((784 + N_CLASSES, *hidden))
    ro_opt = torch.optim.SGD(net.readout.parameters(), lr=0.1)
    ema_sq = [torch.zeros_like(lin.weight) for lin in net.layers]
    for step, (x, y) in enumerate(train[:STEPS], start=1):
        x_pos = _label_input(x, y, True)
        x_neg = _label_input(x, y, False)
        for i, (lin, gw) in enumerate(
            zip(net.layers, net.local_grads(x_pos, x_neg), strict=True)
        ):
            with torch.no_grad():
                ema_sq[i].mul_(beta).add_(gw.pow(2), alpha=1 - beta)
                bias = 1 - beta**step  # Adam-style warmup: raw EMA ~0 at t=1
                lin.weight -= norm_lr * gw / (ema_sq[i] / bias + 1e-12).sqrt()
        ro_opt.zero_grad()
        F.cross_entropy(net.readout(net.features(x_pos).detach()), y).backward()
        ro_opt.step()
    correct = total = 0
    with torch.no_grad():
        for x, y in test:
            feats = net.features(_label_input(x, y, True))
            correct += (net.readout(feats).argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total


def main() -> int:
    t0 = time.perf_counter()
    train, test = _data()
    print(
        "=== W2-P3: EMA credit normalizer (pre-registered: d4 > 0.764 floor) ===",
        flush=True,
    )
    for depth, hidden in (("d2", (128, 128)), ("d4", (128,) * 4)):
        for beta in (0.99, 0.999):
            for norm_lr in (1e-3, 3e-3):
                accs = [
                    train_acc(hidden, s, beta, norm_lr, train, test) for s in (0, 1, 2)
                ]
                print(
                    f"P3 {depth} beta {beta} norm_lr {norm_lr}: "
                    f"mean {sum(accs) / 3:.3f} seeds {[round(a, 3) for a in accs]}",
                    flush=True,
                )
    print(f"walltime {time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
