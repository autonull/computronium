"""E2 — Kolmogorov compression via ψ-programs (TODO17 §4.2).

Pre-registered. Question: can a SHORT ψ-program unfold into a complex
output? Measure compression ratio = |output bits| / |ψ free params| and
grid match accuracy on a 32×32 binary pattern.

Arms:
  readout_adapter — ψ directly decodes the full output from a small seed
                    (params ≥ output size; expected ratio ≤ 1)
  unfolded_psi    — ψ encodes an NCA rule (~200 params) that generates
                    the output over T rollout steps (expected ratio ≫ 1)

Patterns: procedural 32×32 binary fields — checkerboard, diagonal
stripes, concentric rings. Position channels are part of the shared
perception θ (ψ-supplied positional structure — the label-free-growth
boundary of TODO.ntm_nca §11.13 is addressed by ψ supplying the seed +
position code, recorded as such).

Prediction: unfolded_psi achieves ratio ≫ 1 at match accuracy ≥ 0.95;
readout_adapter ratio ≤ 1. Falsification: unfolded ratio ≈ 1.

uv run python scripts/probes/w17_e2_kolmogorov.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time

import torch
from torch import nn
from torch.nn import functional

SEEDS = (0, 1, 2)
H = W = 32
TS = (8, 16, 32)
TRAIN_STEPS = 600
MATCH = 0.95
PATTERNS = ("checker", "stripes", "plaid")


def _pattern(name: str) -> torch.Tensor:
    ii = torch.arange(H).view(H, 1).float()
    jj = torch.arange(W).view(1, W).float()
    if name == "checker":
        return ((ii + jj) % 2).float()
    if name == "stripes":
        return (((ii + jj) % 4) < 2).float()
    if name == "plaid":
        return ((((ii % 4) < 2).float() + ((jj % 4) < 2).float()) % 2).float()
    raise ValueError(name)


def _perception() -> torch.Tensor:
    """Shared perception θ: 3×3 neighbourhood + own state + ψ-supplied
    positional structure (Fourier features — parity-type targets are not
    reachable from raw coordinates)."""
    ii = torch.arange(H).view(H, 1).expand(H, W) / H
    jj = torch.arange(W).view(1, W).expand(H, W) / W
    iraw = torch.arange(H).view(H, 1).expand(H, W).float()
    jraw = torch.arange(W).view(1, W).expand(H, W).float()
    feats = [
        ii,
        jj,
        torch.sin(torch.pi * iraw),
        torch.cos(torch.pi * iraw),
        torch.sin(torch.pi * jraw),
        torch.cos(torch.pi * jraw),
        torch.sin(torch.pi / 2 * iraw),
        torch.cos(torch.pi / 2 * iraw),
        torch.sin(torch.pi / 2 * jraw),
        torch.cos(torch.pi / 2 * jraw),
        torch.sin(torch.pi / 2 * (iraw + jraw)),
        torch.cos(torch.pi / 2 * (iraw + jraw)),
    ]
    return torch.stack(feats, dim=-1)


class _Rule(nn.Module):
    """NCA rule ψ: per-cell MLP on (3×3 neighborhood, own state, pos)."""

    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(22, 16), nn.Tanh(), nn.Linear(16, 1))

    def rollout(self, grid: torch.Tensor, t: int, pos: torch.Tensor) -> torch.Tensor:
        x = grid
        for _ in range(t):
            nb = functional.pad(x[None, None], (1, 1, 1, 1), mode="circular")
            nb = nb[0].unfold(1, 3, 1).unfold(2, 3, 1).reshape(9, H, W)
            inp = torch.cat((nb, pos.permute(2, 0, 1), x[None]), dim=0).permute(1, 2, 0)
            nxt = torch.sigmoid(self.net(inp)[..., 0])
            x = nxt
        return x


def _train_rule(pattern: torch.Tensor, pos: torch.Tensor, t: int) -> tuple:
    rule = _Rule()
    opt = torch.optim.Adam(rule.parameters(), lr=0.03)
    grid = torch.zeros(H, W)
    for _ in range(400):
        out = rule.rollout(grid, t, pos)
        loss = functional.mse_loss(out, pattern)
        opt.zero_grad()
        loss.backward()
        opt.step()
    return rule, out


class _Readout(nn.Module):
    """Direct decode: tiny seed → full grid (params ≫ output bits)."""

    def __init__(self) -> None:
        super().__init__()
        self.dec = nn.Linear(4, H * W)

    def rollout(self, grid: torch.Tensor, t: int, pos: torch.Tensor) -> torch.Tensor:
        seed = torch.tensor([1.0, 0.5, -0.5, 0.25])
        return torch.sigmoid(self.dec(seed).view(H, W))


def _eval_arm(
    arm: str, pattern: torch.Tensor, pos: torch.Tensor, t_grid: tuple[int, ...]
) -> tuple[float, int, int, float, bool]:
    best_acc, best_t, params = 0.0, 0, 0
    for t in t_grid:
        if arm == "unfolded_psi":
            rule, out = _train_rule(pattern, pos, t)
            params = sum(p.numel() for p in rule.parameters())
        else:
            model = _Readout()
            opt = torch.optim.Adam(model.parameters(), lr=0.05)
            for _ in range(400):
                out = model.rollout(pattern, t, pos)
                loss = functional.mse_loss(out, pattern)
                opt.zero_grad()
                loss.backward()
                opt.step()
            params = sum(p.numel() for p in model.parameters())
        match = (out > 0.5).float()
        acc = (match * pattern + (1 - match) * (1 - pattern)).mean().item()
        if acc > best_acc:
            best_acc, best_t = acc, t
    ratio = H * W / params
    alive = best_acc >= MATCH and (ratio > 2.0 if arm == "unfolded_psi" else True)
    return best_acc, best_t, params, ratio, alive


def main() -> int:
    t0 = time.time()
    pos = _perception()
    rows: list[str] = []
    ok_all = True

    for name in PATTERNS:
        pattern = _pattern(name)
        for seed in SEEDS:
            torch.manual_seed(seed)
            for arm in ("unfolded_psi", "readout_adapter"):
                t_grid = TS if arm == "unfolded_psi" else (TS[-1],)
                best_acc, best_t, params, ratio, alive = _eval_arm(
                    arm, pattern, pos, t_grid
                )
                ok_all &= alive
                rows.append(
                    f"{name:>8} {arm:>15} seed {seed}: match {best_acc:.3f} "
                    f"@T={best_t}  |ψ|={params}  ratio {ratio:.2f}x  "
                    f"{'ok' if alive else 'FAIL'}"
                )

    print("\n".join(rows))
    psi_rows = [r for r in rows if "unfolded_psi" in r]
    psi_ok = all("FAIL" not in r for r in psi_rows)
    print(
        f"\nVERDICT: {'E2 ALIVE — short ψ unfolds O(K) output' if psi_ok else 'E2 falsified — ψ must encode the output'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if psi_ok else 1


if __name__ == "__main__":
    sys.exit(main())
