"""H2 probe (TODO12b): do biases ever train in this repo?

Verdict (2026-09-06): CONFIRMED — biases are frozen in EVERY arm,
including the bp baseline (code-read: `_learnable_weight_names` at
ontology/utils/params.py filters to 2-D "weight" tensors; GradientCredit
and all credits inherit that contract; apply_pseudo_gradients is the
single choke point that passes biases through untouched). Impact
sized below: small but real.

Measured (pure-torch reference, mlp 784-128-10, SGD lr 0.1, 150
MNIST-quick batches, seed 0):
- weights+biases trained: acc 0.904
- weights-only (repo contract): acc 0.904
- delta = 0.000 on this cell — the freeze is a REAL contract defect
  (biases never receive gradients in any arm, bp included) with
  NEGLIGIBLE impact on MNIST-quick at this scale. All "backprop"
  baselines in the repo are technically weights-only backprop; every
  margin quoted at HEAD carries that caveat. No re-runs warranted at
  demo scale; re-size only if a stubborn-gap investigation lands on a
  bias-sensitive cell (deep/thin-width).
"""

import time

import torch
from torch import nn


def _train(train_bias: bool) -> float:
    torch.manual_seed(0)
    from computronium import create_task

    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    net = nn.Sequential(nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 10))
    ce = nn.CrossEntropyLoss()
    seen = 0
    for xb, yb in task.get_dataloader("train"):
        opt = torch.optim.SGD(
            [p for p in net.parameters() if train_bias or p.ndim == 2], lr=0.1
        )
        loss = ce(net(xb.view(xb.size(0), -1)), yb)
        opt.zero_grad()
        loss.backward()
        opt.step()
        seen += 1
        if seen >= 150:
            break
    correct = total = 0
    with torch.no_grad():
        for xb, yb in task.get_dataloader("test"):
            pred = net(xb.view(xb.size(0), -1)).argmax(1)
            correct += (pred == yb).sum().item()
            total += yb.size(0)
    return correct / total


def main() -> None:
    t0 = time.perf_counter()
    live = _train(True)
    frozen = _train(False)
    print(
        f"weights+biases: {live:.3f}  weights-only: {frozen:.3f}  delta={live - frozen:.3f}"
    )
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
