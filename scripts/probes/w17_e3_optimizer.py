"""E3 follow-up: rule reconfiguration under Muon vs Adam (TODO17 §5.2
+ campaign 7.2 transfer).

Pre-registered. Question: does Muon's displacement geometry absorb the
stability cost of rule reconfiguration (campaign 7.2's hypothesis), or
is the σ_max(J_F) stability-expressiveness frontier optimizer-
independent? The E3 r2 round trained all heads under Adam (lr 0.05)
with candidate-init screening; the frontier finding (6/8 patterns are
stable attractors at σ_max ≈ 0; cross REQUIRES σ_max ∈ [1.4, 2.8]) is
an Adam-conditional measurement until this cell runs.

Design: same 8 patterns, same screening (6 candidate inits, best-match
head kept), TRAIN_STEPS matched; the only change is the update rule —
Muon (newton-schulz orthogonalized momentum on the 2-D weights, plain
SGD on the 1-D bias, lr 0.02 per the campaign-7.2 calibration) vs the
recorded Adam 0.05 control. Report per pattern: best match, σ_max(J_F)
of the kept head, and the frontier row (stable-attractor vs
non-contractive).

Prediction (pre-registered): the frontier is pattern-structured, not
optimizer-conditional — cross still requires σ_max > 1 under Muon, and
the stable set is unchanged. Falsification: Muon moves cross (or any
frontier row) across the σ_max = 1 boundary at matched match — the
budget is an optimizer artifact.

uv run python scripts/probes/w17_e3_optimizer.py
Walltime printed, never recorded.

RESULT (2026-09-10, 449.7 s): the frontier is pattern-structured,
optimizer-INDEPENDENT. dotgrid σ 0.01 (muon) vs 0.00 (adam) — stable
under both; cross stays non-contractive under both (adam σ 2.39 /
match 0.909; muon σ 1.50 / match 0.890) and diagonal mildly > 1 under
both (1.14 / 1.06); no frontier row crosses the σ_max = 1 boundary
under either optimizer. Muon softens cross's σ (2.39 → 1.50) but does
not move it across the boundary — campaign 7.2's "Muon absorbs the
reconfiguration stability cost" does NOT transfer to the structural
budget: the cross-pattern expressiveness cost is pattern-conditional,
not optimizer-conditional.
"""

from __future__ import annotations

import sys
import time

import torch
from torch.nn import functional
from w17_e3_rule_reconfig import (
    TRAIN_STEPS,
    _patterns,
    _perception,
    rollout,
    sigma_max_jacobian,
)

from computronium.core.optimization.strategies.update import newton_schulz5

CANDIDATES = 6


def _muon_step(p: torch.Tensor, g: torch.Tensor, buf: torch.Tensor, lr: float):
    buf.mul_(0.9).add_(g)
    u = newton_schulz5(buf.clone())
    with torch.no_grad():
        p.add_(u, alpha=-lr)


def train_head(
    pattern: torch.Tensor,
    pos: torch.Tensor,
    seed: int,
    update: str,
) -> tuple[torch.nn.Module, float]:
    from torch import nn

    torch.manual_seed(seed)
    rule = nn.Sequential(nn.Linear(22, 16), torch.nn.Tanh(), nn.Linear(16, 1))
    if update == "adam":
        opt = torch.optim.Adam(rule.parameters(), lr=0.05)
    bufs = {n: torch.zeros_like(p) for n, p in rule.named_parameters()}
    out = pattern
    for _ in range(TRAIN_STEPS):
        out = rollout(rule, pos)
        loss = functional.binary_cross_entropy(out.clamp(1e-4, 1 - 1e-4), pattern)
        if update == "adam":
            opt.zero_grad()
            loss.backward()
            opt.step()
        else:  # muon
            named = list(rule.named_parameters())
            grads = torch.autograd.grad(loss, [p for _, p in named])
            for (n, p), g in zip(named, grads, strict=True):
                if p.ndim == 2:
                    _muon_step(p, g, bufs[n], 0.02)
                else:
                    with torch.no_grad():
                        p.add_(g, alpha=-0.003)
    acc = ((out > 0.5).float() == pattern).float().mean().item()
    return rule, acc


def train_screened(
    pattern: torch.Tensor, pos: torch.Tensor, seed: int, update: str
) -> tuple[torch.nn.Module, float, float]:
    best_head, best_acc = None, -1.0
    for c in range(CANDIDATES):
        head, acc = train_head(pattern, pos, seed=seed + c, update=update)
        if acc > best_acc:
            best_head, best_acc = head, acc
    if best_head is None:  # CANDIDATES >= 1 guarantees a head
        raise RuntimeError("no candidate trained")  # ruff: ignore[raise-vanilla-args]
    return best_head, best_acc, sigma_max_jacobian(best_head, pos)


def main() -> int:
    t0 = time.time()
    pos = _perception()
    rows = []
    frontier_shift = False
    for name, pattern in _patterns(8):
        line = f"{name:>13}:"
        for update in ("adam", "muon"):
            _, acc, sigma = train_screened(
                pattern, pos, seed=7000 + hash(name) % 1000, update=update
            )
            tag = f"  {update:>4} match {acc:.3f} σ_max {sigma:.2f}"
            line += tag
            rows.append((name, update, acc, sigma))
        print(line, flush=True)
    # frontier comparison: stable set = σ_max < 1 at match
    for name in {r[0] for r in rows}:
        a = next(r for r in rows if r[0] == name and r[1] == "adam")
        m = next(r for r in rows if r[0] == name and r[1] == "muon")
        if (a[3] < 1.0) != (m[3] < 1.0):
            frontier_shift = True
            print(f"FRONTIER SHIFT at {name}: adam σ {a[3]:.2f} vs muon σ {m[3]:.2f}")
    print(
        f"\nVERDICT: stability-expressiveness frontier is "
        f"{'OPTIMIZER-CONDITIONAL (shift detected)' if frontier_shift else 'pattern-structured, optimizer-INDEPENDENT'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
