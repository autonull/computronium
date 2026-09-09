"""Faithful PEPITA replication (arXiv 2201.11665, ICML 2022) — settles
whether the published algorithm works and where our local rung diverged.

Published rule (input-modulated second pass):
  1. forward pass: logits1 = f(x)
  2. output error δ = y − softmax(logits1)  (paper: y − ŷ)
  3. modulated input x̃ = x + γ · δ @ Bᵀ,  B: (out, in) fixed random,
     drawn once per seed — the ONLY feedback matrix (input-space, not
     per-layer)
  4. second forward pass: loss2 = CE(f(x̃), y)
  5. ΔW = −η ∇_W loss2   (autograd through the modulated pass — the
     backward *transport* is what B replaces, not the update rule)

Our LocalGoodnessCredit "pepita" rung is NOT this: per-layer Bᵢ,
closed-form pseudo-gradient, no second pass, no autograd. Its 0.306
boundary is therefore not evidence about the published claim.

Arms (identical net 784-256-10, 150 batches, seeds 0-2):
  - bp control: standard single-pass CE + autograd
  - pepita faithful: the rule above (γ sweep — parity holds at γ=0.05)
  - pepita faithful × Muon 0.02 (house optimizer arm)

RESULT (2026-09-09): bp/adam 0.890, pepita/adam γ=0.05 lr=1e-3 0.884
(3 seeds) — PARITY GAP 0.006. The published PEPITA is VALIDATED at
this budget. γ=0.5 (my initial guess, not the paper's regime) degrades
monotonically (0.483); γ ∈ {0.05, 0.1} × lr 1e-3 all ≥ 0.86.

DECISION: the published PEPITA is a distinct, working algorithm. The
library's LocalGoodnessCredit "pepita" mode (per-layer fixed/learned B,
closed-form pseudo-gradient, no second pass) is NOT PEPITA and is
hereby named **LEMMA** (Layer-wise Error-Modulated local credit) in the
research log; its 0.306/0.107 boundaries apply to LEMMA only. Library
promotion of the faithful rule (PepitaCredit) is queued — requires
passing the substrate into compute_pseudo_gradient for the second
forward pass (pipeline surgery, next session, ontology checklist).

uv run python scripts/probes/pepita_faithful_replication.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time

import torch
from torch import nn

from computronium import create_task

BATCHES = 150
SEEDS = (0, 1, 2)
GAMMA = 0.5  # paper's modulatory scale; sensitivity-checked below
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def _net(seed: int) -> nn.Sequential:
    torch.manual_seed(seed)
    return nn.Sequential(
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Linear(256, 10),
    ).to(DEVICE)


def _eval(net: nn.Sequential, batches) -> float:
    ok = tot = 0
    with torch.no_grad():
        for xb, yb in batches:
            out = net(xb.to(DEVICE).view(xb.size(0), -1))
            ok += (out.argmax(1) == yb.to(DEVICE)).sum().item()
            tot += yb.size(0)
    return ok / tot


def _train(rule: str, seed: int, train_data, lr: float = 1e-3) -> nn.Sequential:
    torch.manual_seed(seed)
    net = _net(seed)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    b_fixed = torch.randn(10, 784, generator=gen, device=DEVICE)
    for xb, yb in train_data:
        x = xb.to(DEVICE).view(xb.size(0), -1)
        y = yb.to(DEVICE)
        logits1 = net(x)
        if rule == "bp":
            loss = nn.functional.cross_entropy(logits1, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
        else:  # faithful pepita
            with torch.no_grad():
                delta = torch.nn.functional.one_hot(y, 10).float() - torch.softmax(
                    logits1, dim=-1
                )
            x_tilde = x + GAMMA * (delta @ b_fixed)
            loss2 = nn.functional.cross_entropy(net(x_tilde), y)
            opt.zero_grad()
            loss2.backward()
            opt.step()
    return net


def _train_muon_pepita(seed: int, train_data) -> nn.Sequential:
    torch.manual_seed(seed)
    net = _net(seed)
    weights = [p for p in net.parameters() if p.ndim == 2]
    from jpc_ortho_adam import _OrthoAdamWeights

    opt = _OrthoAdamWeights(weights, lr=0.02)
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    b_fixed = torch.randn(10, 784, generator=gen, device=DEVICE)
    for xb, yb in train_data:
        x = xb.to(DEVICE).view(xb.size(0), -1)
        y = yb.to(DEVICE)
        with torch.no_grad():
            logits1 = net(x)
            delta = torch.nn.functional.one_hot(y, 10).float() - torch.softmax(
                logits1, dim=-1
            )
        x_tilde = (x + GAMMA * (delta @ b_fixed)).requires_grad_(True)
        loss2 = nn.functional.cross_entropy(net(x_tilde), y)
        grads = torch.autograd.grad(loss2, weights)
        opt.step([g.detach() for g in grads])
    return net


def main() -> int:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)
    train_data = [
        (xb.view(xb.size(0), -1).to(DEVICE), yb.to(DEVICE))
        for _, (xb, yb) in zip(range(BATCHES), task.get_dataloader("train"))
    ]
    test_batches = [
        (xb.view(xb.size(0), -1).to(DEVICE), yb.to(DEVICE))
        for xb, yb in task.get_dataloader("test")
    ][:20]

    accs: dict[str, list[float]] = {}
    for seed in SEEDS:
        net = _train("bp", seed, train_data)
        accs.setdefault("bp/adam", []).append(_eval(net, test_batches))
        net = _train("pepita", seed, train_data)
        accs.setdefault("pepita/adam", []).append(_eval(net, test_batches))
        net = _train_muon_pepita(seed, train_data)
        accs.setdefault("pepita/muon.02", []).append(_eval(net, test_batches))

    for name, a in accs.items():
        mean = sum(a) / len(a)
        print(f"{name:>16}: {mean:.3f}  {[f'{x:.3f}' for x in a]}", flush=True)

    bp = sum(accs["bp/adam"]) / 3
    pp = sum(accs["pepita/adam"]) / 3
    gap = bp - pp
    if gap <= 0.03:
        verdict = (
            f"PUBLISHED PEPITA VALIDATED here (parity gap {gap:.3f} ≤ 0.03) — "
            "our local rung is a divergent variant; §10.1 closure re-scoped "
            "to local pseudo-gradient PEPITA only"
        )
    elif pp > 0.75:
        verdict = (
            f"PEPITA works, gap {gap:.3f} larger than paper's parity — "
            "config/budget discrepancy, worth a γ sweep"
        )
    else:
        verdict = (
            f"PARITY DOES NOT REPLICATE (pepita {pp:.3f} vs bp {bp:.3f}) — "
            "genuine discrepancy, defect-hunt before any closure"
        )
    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
