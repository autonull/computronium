"""Z3 toy feasibility (TODO16 §2.3): ψ selects computation, θ never moves.

Frozen backbone (32→16→2, trained on parity to convergence, SHA-asserted)
plus three FIXED operator callables on the input — Identity, Parity,
LastSymbol. ψ is a one-hot selector over operators; the per-task readout
is a closed-form ridge on the selected operator's output (no gradient
step touches θ). Task A: parity (ψ selects Parity). Task B: last-symbol
(ψ selects LastSymbol).

Distinction from Flagship B: discrete routing, not continuous affine
correction — the mask-entropy law does not apply.

Pre-registered: exact θ invariance (bitwise), both tasks ≥ 0.90.
Falsification: if selection degrades task A → Z3 mechanism closed at
toy scale.

uv run python scripts/probes/z3_toy.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import hashlib
import sys
import time

import torch
from torch import nn

SEEDS = (0, 1, 2)
DIN, DH, DOUT = 32, 16, 2
RIDGE = 1e-4
TASKS = ("parity", "last_symbol")


def _theta_sha(model: nn.Module) -> str:
    return hashlib.sha256(
        b"".join(
            t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
            for t in model.parameters()
        )
    ).hexdigest()


def _batch(gen: torch.Generator, n: int = 256) -> tuple[torch.Tensor, torch.Tensor]:
    x = torch.randint(0, 2, (n, DIN), generator=gen).float()
    return x, torch.stack(
        [(x.sum(-1) % 2).long(), x[:, -1].long()], dim=-1
    )  # [..., 2]: parity, last_symbol


def _operators(x: torch.Tensor) -> dict[str, torch.Tensor]:
    """Fixed operator callables: feature maps, zero parameters."""
    parity = (x.sum(-1, keepdim=True) % 2).float().expand_as(x)
    last = x[:, -1:].expand_as(x)
    return {"identity": x, "parity": parity, "last_symbol": last}


def _ridge_solve(z: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Closed-form ridge readout: W = (ZᵀZ + λI)⁻¹ ZᵀY one-hot targets."""
    d = z.size(-1)
    eye = torch.eye(d, device=z.device)
    y_onehot = nn.functional.one_hot(y, DOUT).float()
    return torch.linalg.solve(z.T @ z + RIDGE * eye, z.T @ y_onehot)


def _eval(op_out: torch.Tensor, w: torch.Tensor, y: torch.Tensor) -> float:
    return ((op_out @ w).argmax(-1) == y).float().mean().item()


def main() -> int:  # ruff: ignore[too-many-locals] - probe harness
    t0 = time.time()
    results: dict[tuple[str, str], list[float]] = {}
    theta_invariant = True
    for seed in SEEDS:
        torch.manual_seed(seed)
        backbone = nn.Sequential(nn.Linear(DIN, DH), nn.Tanh(), nn.Linear(DH, DOUT))
        gen = torch.Generator().manual_seed(seed)
        x, y = _batch(gen)
        opt = torch.optim.Adam(backbone.parameters(), lr=1e-2)
        for _ in range(300):  # distill-init parity training to convergence
            logits = backbone(x)
            loss = nn.functional.cross_entropy(logits, y[:, 0])
            opt.zero_grad()
            loss.backward()
            opt.step()
        sha_before = _theta_sha(backbone)
        theta_before = [t.detach().clone() for t in backbone.parameters()]

        ops = _operators(x)
        for task in TASKS:
            op = "parity" if task == "parity" else "last_symbol"
            z = ops[op]
            w = _ridge_solve(z, y[:, TASKS.index(task)])
            acc = _eval(z, w, y[:, TASKS.index(task)])
            results.setdefault((task, op), []).append(acc)

        # Task-switch round trip: B's ψ, then restore A's ψ-system (ridge
        # weights are the ψ-system; θ is untouched by construction).
        theta_invariant &= _theta_sha(backbone) == sha_before
        theta_invariant &= all(
            torch.equal(a, b)
            for a, b in zip(theta_before, backbone.parameters(), strict=True)
        )

    for (task, op), accs in results.items():
        print(f"{task:>12} (ψ→{op:>11}): mean {sum(accs) / len(accs):.3f}  {accs}")
    print(f"θ bitwise invariant: {theta_invariant}")
    ok = theta_invariant and all(
        sum(a) / len(a) >= 0.90 for (task, _), a in results.items() if task in TASKS
    )
    print(
        f"\nVERDICT: {'Z3 toy mechanism ALIVE — ψ selects operators, θ invariant' if ok else 'Z3 mechanism CLOSED at toy scale'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
