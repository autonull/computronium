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

FOLLOW-UP (2026-09-10, TODO17 close-out residuals):
- --task=cifar10 (flat 3072-256-10 head): bp 0.378, pepita γ=0.05 0.362,
  pepita×muon 0.227 — parity replicates on the CIFAR-10 head (gap 0.015);
  Muon harm replicates. The input-modulation family's home is fixed-input
  tasks, now measured on two datasets.
- --ablation=rebatch (B redrawn per batch): 0.897 vs bp 0.890 — parity
  HOLDS without a fixed B.
- --ablation=ortho (orthogonal B): 0.894 — parity HOLDS with orthogonal B.
  VERDICT (mechanism-bound): neither B fixedness nor B orthogonality is
  load-bearing at this scale; the mechanism is the modulated second pass
  under an exact gradient of a real objective. B statistics are free.
- --task=cora r2 (train split CYCLED to the 150-batch budget — the
  first run trained on ~3 batches and was ill-posed for every arm):
  bp/adam 0.556, pepita/adam γ=0.05 0.328, pepita/muon 0.522. PARITY
  DOES NOT REPLICATE on flattened graph-node features — a genuine gap,
  and Muon nearly closes it (0.522 vs 0.556), consistent with the
  graph row of the I(C,U) map ("graph stays with Muon"). The
  input-modulation family's fixed-input home is classification on
  image-like inputs; graph-feature parity is optimizer-conditional.
"""

from __future__ import annotations

import argparse
import time

import torch
from torch import nn

from computronium import create_task

BATCHES = 150
SEEDS = (0, 1, 2)
GAMMA = 0.05  # paper's regime — parity knob (see §11.2, TODO15)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# task -> (input_dim, hidden_dim, num_classes) (TODO16 §1.3 breadth)
TASK_DIMS = {
    "mnist": (784, 256, 10),
    "cifar10": (3072, 256, 10),
    "cora": (1433, 64, 7),
}


def _net(seed: int, dims: tuple[int, int, int]) -> nn.Sequential:
    din, h, dout = dims
    torch.manual_seed(seed)
    return nn.Sequential(
        nn.Linear(din, h),
        nn.ReLU(),
        nn.Linear(h, dout),
    ).to(DEVICE)


def _eval(net: nn.Sequential, batches) -> float:
    ok = tot = 0
    with torch.no_grad():
        for xb, yb in batches:
            out = net(xb.to(DEVICE).view(xb.size(0), -1))
            ok += (out.argmax(1) == yb.to(DEVICE)).sum().item()
            tot += yb.size(0)
    return ok / tot


def _train(
    rule: str,
    seed: int,
    train_data,
    lr: float = 1e-3,
    gamma: float = GAMMA,
    dims: tuple[int, int, int] = TASK_DIMS["mnist"],
) -> nn.Sequential:
    torch.manual_seed(seed)
    net = _net(seed, dims)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    b_fixed = torch.randn(dims[2], dims[0], generator=gen, device=DEVICE)
    if rule == "pepita_ortho":
        b_fixed = torch.linalg.qr(b_fixed.T).Q.T.contiguous()
    for xb, yb in train_data:
        x = xb.to(DEVICE).view(xb.size(0), -1)
        y = yb.to(DEVICE)
        logits1 = net(x)
        if rule == "bp":
            loss = nn.functional.cross_entropy(logits1, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
        else:  # faithful pepita (+ paper ablations)
            with torch.no_grad():
                delta = torch.nn.functional.one_hot(y, dims[2]).float() - torch.softmax(
                    logits1, dim=-1
                )
            b = b_fixed
            if rule == "pepita_rebatch":
                # paper ablation: B redrawn every iteration (no fixed B)
                b = torch.randn(dims[2], dims[0], generator=gen, device=DEVICE)
            x_tilde = x + gamma * (delta @ b)
            loss2 = nn.functional.cross_entropy(net(x_tilde), y)
            opt.zero_grad()
            loss2.backward()
            opt.step()
    return net


def _train_muon_pepita(
    seed: int,
    train_data,
    gamma: float = GAMMA,
    dims: tuple[int, int, int] = TASK_DIMS["mnist"],
) -> nn.Sequential:
    torch.manual_seed(seed)
    net = _net(seed, dims)
    weights = [p for p in net.parameters() if p.ndim == 2]
    from jpc_ortho_adam import _OrthoAdamWeights

    opt = _OrthoAdamWeights(weights, lr=0.02)
    gen = torch.Generator(device=DEVICE).manual_seed(seed)
    b_fixed = torch.randn(dims[2], dims[0], generator=gen, device=DEVICE)
    for xb, yb in train_data:
        x = xb.to(DEVICE).view(xb.size(0), -1)
        y = yb.to(DEVICE)
        with torch.no_grad():
            logits1 = net(x)
            delta = torch.nn.functional.one_hot(y, dims[2]).float() - torch.softmax(
                logits1, dim=-1
            )
        x_tilde = (x + gamma * (delta @ b_fixed)).requires_grad_(True)
        loss2 = nn.functional.cross_entropy(net(x_tilde), y)
        grads = torch.autograd.grad(loss2, weights)
        opt.step([g.detach() for g in grads])
    return net


def _cora_split(batch: int = 64):
    """Flattened node features on the Planetoid train/val masks (no graph)."""
    from torch_geometric.datasets import Planetoid

    data = Planetoid(root="./data", name="Cora")[0]
    idx = data.train_mask.nonzero(as_tuple=True)[0]
    perm = torch.randperm(idx.size(0))
    epoch = [
        (data.x[idx[perm[i : i + batch]]], data.y[idx[perm[i : i + batch]]])
        for i in range(0, idx.size(0), batch)
    ]
    # 140 train nodes -> ~3 batches/epoch; cycle to the full budget
    # (batches_seen >= budget rule, TODO15 §14.1)
    train = [epoch[i % len(epoch)] for i in range(BATCHES)]
    test = [
        (data.x[data.val_mask | data.test_mask], data.y[data.val_mask | data.test_mask])
    ]
    return train, test


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gamma", type=float, default=GAMMA)
    parser.add_argument("--task", choices=sorted(TASK_DIMS), default="mnist")
    parser.add_argument(
        "--ablation",
        choices=("none", "rebatch", "ortho"),
        default="none",
        help="paper-ablation variant of the pepita/adam arm: rebatch = B "
        "redrawn per batch; ortho = orthogonal B (paper's B-initialization "
        "ablation)",
    )
    args = parser.parse_args()
    t0 = time.time()
    dims = TASK_DIMS[args.task]
    task = create_task(args.task, device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)
    if args.task == "cora":
        train_data, test_batches = _cora_split()
        train_data = [(xb.to(DEVICE), yb.to(DEVICE)) for xb, yb in train_data]
        test_batches = [
            (xb.view(xb.size(0), -1).to(DEVICE), yb.to(DEVICE))
            for xb, yb in test_batches
        ]
    else:
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
        net = _train("bp", seed, train_data, dims=dims)
        accs.setdefault("bp/adam", []).append(_eval(net, test_batches))
        if args.ablation == "none":
            net = _train("pepita", seed, train_data, gamma=args.gamma, dims=dims)
            accs.setdefault("pepita/adam", []).append(_eval(net, test_batches))
            net = _train_muon_pepita(seed, train_data, gamma=args.gamma, dims=dims)
            accs.setdefault("pepita/muon.02", []).append(_eval(net, test_batches))
        else:
            rule = f"pepita_{args.ablation}"
            net = _train(rule, seed, train_data, gamma=args.gamma, dims=dims)
            accs.setdefault(f"{rule}/adam", []).append(_eval(net, test_batches))

    for name, a in accs.items():
        mean = sum(a) / len(a)
        print(f"{name:>16}: {mean:.3f}  {[f'{x:.3f}' for x in a]}", flush=True)

    if args.ablation != "none":
        bp = sum(accs["bp/adam"]) / 3
        pp = sum(accs[f"pepita_{args.ablation}/adam"]) / 3
        print(
            f"\nVERDICT (ablation {args.ablation}): pepita {pp:.3f} vs bp "
            f"{bp:.3f} — paper parity anchor is 0.884 (fixed random B); "
            "ablation >= anchor → B-detail not load-bearing; below → it is",
            flush=True,
        )
        print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
        return 0

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
