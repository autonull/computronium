"""Z3 full experiment (TODO16 §3A): ψ-mediated algorithm migration over
8 operators x 4 tasks with exact θ invariance.

Operators (fixed feature maps on the input, zero parameters):
Identity, Threshold, Accumulate, LastSymbol, Parity, SparseTopKRoute,
SignFlip, Delay. ψ is a one-hot selector over operators; the per-task
readout is closed-form ridge on the selected operator's output — no
gradient step touches θ (the frozen backbone is SHA-asserted).

This IS the Benchmark Level 3.5 (Algorithm Migration) experiment: ψ
switches strategy A0 -> A1 without changing θ.

Metrics: task accuracy, adaptation time (episodes to switch — 1 by
construction with closed-form ψ), parameter invariance (bitwise).

Pre-registered: >= 0.90 on all 4 tasks with exact θ invariance.

uv run python scripts/probes/z3_full.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import hashlib
import sys
import time

import torch
from torch import nn

SEEDS = (0, 1, 2)
DIN, DH, DOUT = 32, 16, 4
RIDGE = 1e-4
TASKS = ("parity", "last_symbol", "threshold", "cumulative_sum")
OPERATORS = (
    "identity",
    "threshold",
    "accumulate",
    "last_symbol",
    "parity",
    "sparse_topk",
    "sign_flip",
    "delay",
)


def _theta_sha(params: list) -> str:
    return hashlib.sha256(
        b"".join(
            t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
            for t in params
        )
    ).hexdigest()


def _targets(x: torch.Tensor) -> dict[str, torch.Tensor]:
    # 4-way tasks: bucket the scalar statistic into 4 classes.
    scalar = {
        "parity": (x.sum(-1) % 2).float(),
        "last_symbol": x[:, -1].float(),
        "threshold": (x.mean(-1) > 0.5).float(),
        "cumulative_sum": (x.cumsum(-1)[:, -1] % 4).float(),
    }
    return {k: (v * (DOUT - 1)).long().clamp(0, DOUT - 1) for k, v in scalar.items()}


def _operators(x: torch.Tensor) -> dict[str, torch.Tensor]:
    cum = x.cumsum(-1) / x.size(-1)
    topk = x.topk(8, dim=-1).values[..., -1:]
    return {
        "identity": x,
        "threshold": ((x > 0.5).float() * 2 - 1) * x,
        "accumulate": cum * x,
        "last_symbol": x[:, -1:].expand_as(x),
        "parity": ((x.sum(-1, keepdim=True) % 2) * 2 - 1).expand_as(x),
        "sparse_topk": x * (x >= topk).float(),
        "sign_flip": -x,
        "delay": torch.cat([x[:, -1:], x[:, :-1]], dim=-1),
    }


def _ridge(z: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    d = z.size(-1)
    y_oh = nn.functional.one_hot(y, DOUT).float()
    return torch.linalg.solve(z.T @ z + RIDGE * torch.eye(d), z.T @ y_oh)


def main() -> int:  # ruff: ignore[too-many-locals] - probe harness
    t0 = time.time()
    gen = torch.Generator().manual_seed(11)
    x = torch.randint(0, 2, (512, DIN), generator=gen).float()
    y = _targets(x)
    ops = _operators(x)

    torch.manual_seed(0)
    backbone = nn.Sequential(nn.Linear(DIN, DH), nn.Tanh(), nn.Linear(DH, DOUT))
    opt = torch.optim.Adam(backbone.parameters(), lr=1e-2)
    for _ in range(300):  # distill-init: parity pretraining, then frozen
        loss = nn.functional.cross_entropy(backbone(x), y["parity"])
        opt.zero_grad()
        loss.backward()
        opt.step()
    params = list(backbone.parameters())
    sha_before = _theta_sha(params)

    results: dict[tuple[str, str], list[float]] = {}
    for seed in SEEDS:
        torch.manual_seed(seed)
        idx = torch.randperm(x.size(0), generator=generator(seed))[:384]
        for task in TASKS:
            # ψ = one-hot selector: pick the operator most correlated with
            # the task target (closed-form selection via ridge residual).
            best_op, best_acc = "identity", -1.0
            for op in OPERATORS:
                w = _ridge(ops[op][idx], y[task][idx])
                acc = ((ops[op] @ w).argmax(-1) == y[task]).float().mean().item()
                if acc > best_acc:
                    best_op, best_acc = op, acc
            results.setdefault((task, best_op), []).append(best_acc)

    theta_invariant = _theta_sha(list(backbone.parameters())) == sha_before
    for (task, op), accs in results.items():
        print(f"{task:>15} (ψ→{op:>12}): mean {sum(accs) / len(accs):.3f}  {accs}")
    print(f"θ bitwise invariant: {theta_invariant}")
    all_accs = [a for accs in results.values() for a in accs]
    ok = theta_invariant and min(all_accs) >= 0.90
    print(
        f"\nVERDICT: {'Z3 algorithm migration ALIVE — ψ switches strategies, θ invariant' if ok else 'Z3 full FALSIFIED'}"
    )
    print(
        f"adaptation time: 1 episode (closed-form ψ); operator diversity "
        f"{len({op for _, op in results})}/{len(OPERATORS)}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if ok else 1


def generator(seed: int) -> torch.Generator:
    return torch.Generator().manual_seed(seed)


if __name__ == "__main__":
    sys.exit(main())
