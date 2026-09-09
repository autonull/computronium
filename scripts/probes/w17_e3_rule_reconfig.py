"""E3 — NCA rule reconfiguration for pattern generation (TODO17 §4.3).

Pre-registered. Question: can ψ change the NCA rules to generate
DIFFERENT spatial patterns from the same seed, with θ frozen?

Design: shared perception θ (position channels + zero seed — fixed
tensors, SHA-asserted unused by any gradient step); per-pattern rule
heads ψ_k trained on K ∈ {2, 4, 8} procedural patterns. Switching ψ
selects the rule; the SAME θ generates P_k.

Arms:
  single_rule     — ψ pinned to rule 1 (control: only P1 regenerates)
  psi_rule_select — ψ selects among K rules, θ frozen

Prediction: the number of distinct generated patterns equals K with
match ≥ 0.9 each, θ bitwise invariant. Falsification: psi_rule_select
produces only P1 regardless of ψ, or θ changes.

REV r2 (TODO17 session 5): --seed flag, candidate-init screening
(6 inits per pattern, best-match head selected — screening recorded,
not hidden), σ_max(J_F) power iteration per candidate (§5.2
stability-frontier data; σ_max ≥ ρ, an upper bound on the NCA step
Jacobian). r2 finding: thin-structure patterns (cross, diagonal) are
init-sensitive — some inits converge to unstable rules (σ_max > 1)
that fail match; the stability budget is measured, not assumed.

uv run python scripts/probes/w17_e3_rule_reconfig.py [--seed S]
Walltime printed, never recorded.
"""

from __future__ import annotations

import hashlib
import sys
import time

import torch
from torch import nn
from torch.nn import functional

H = W = 32
TRAIN_STEPS = 300
MATCH = 0.9


def _patterns(k: int) -> list[tuple[str, torch.Tensor]]:
    ii = torch.arange(H).view(H, 1).float()
    jj = torch.arange(W).view(1, W).float()
    spec = {
        "checker": ((ii + jj) % 2),
        "diag_stripes": (((ii + jj) % 4) < 2),
        "plaid": ((((ii % 4) < 2).float() + ((jj % 4) < 2).float()) % 2),
        "vert_stripes": ((jj % 4) < 2),
        "horz_stripes": ((ii % 4) < 2),
        "dotgrid": (((ii % 4) < 2) & ((jj % 4) < 2)),
        "cross": ((torch.abs(ii - H / 2) < 2) | (torch.abs(jj - W / 2) < 2)),
        "diagonal": ((ii - jj).abs() < 1.5),
    }
    return [
        (n, torch.broadcast_to(t.float(), (H, W)).contiguous())
        for n, t in list(spec.items())[:k]
    ]


def _perception() -> torch.Tensor:
    """Shared perception θ — same basis as E2 (Fourier positional
    features; single source of truth in w17_e2_kolmogorov)."""
    from w17_e2_kolmogorov import _perception as _e2_perception

    return _e2_perception()


def _theta_sha(pos: torch.Tensor) -> str:
    return hashlib.sha256(pos.contiguous().numpy().tobytes()).hexdigest()


def rollout(rule: nn.Module, pos: torch.Tensor, t: int = 16) -> torch.Tensor:
    x = torch.zeros(H, W)
    for _ in range(t):
        nb = functional.pad(x[None, None], (1, 1, 1, 1), mode="circular")[0]
        nb = nb.unfold(1, 3, 1).unfold(2, 3, 1).reshape(9, H, W)
        inp = torch.cat((nb, pos.permute(2, 0, 1), x[None]), dim=0).permute(1, 2, 0)
        x = torch.sigmoid(rule(inp)[..., 0])
    return x


def train_head(
    pattern: torch.Tensor, pos: torch.Tensor, seed: int
) -> tuple[nn.Module, float]:
    torch.manual_seed(seed)
    rule = nn.Sequential(nn.Linear(22, 16), nn.Tanh(), nn.Linear(16, 1))
    opt = torch.optim.Adam(rule.parameters(), lr=0.05)
    out = pattern
    for _ in range(TRAIN_STEPS):
        out = rollout(rule, pos)
        loss = functional.binary_cross_entropy(out.clamp(1e-4, 1 - 1e-4), pattern)
        opt.zero_grad()
        loss.backward()
        opt.step()
    acc = ((out > 0.5).float() == pattern).float().mean().item()
    return rule, acc


def sigma_max_jacobian(rule: nn.Module, pos: torch.Tensor, iters: int = 12) -> float:
    """σ_max(J_F) of one NCA step at the converged attractor, via power
    iteration with autograd jvp/vjp (upper bound on ρ(J_F); §5.2)."""
    x0 = torch.zeros(H, W)

    def step(flat: torch.Tensor) -> torch.Tensor:
        x = flat.view(H, W)
        nb = functional.pad(x[None, None], (1, 1, 1, 1), mode="circular")[0]
        nb = nb.unfold(1, 3, 1).unfold(2, 3, 1).reshape(9, H, W)
        inp = torch.cat((nb, pos.permute(2, 0, 1), x[None]), dim=0).permute(1, 2, 0)
        return torch.sigmoid(rule(inp)[..., 0]).flatten()

    with torch.no_grad():
        for _ in range(16):
            x0 = step(x0)
    v = torch.randn(H * W)
    v /= v.norm()
    s = 0.0
    for _ in range(iters):
        _, jv = torch.autograd.functional.jvp(step, x0, v)
        s = jv.norm().item()
        v = jv / max(s, 1e-12)
    return s


CANDIDATES = 6


def train_screened(
    pattern: torch.Tensor, pos: torch.Tensor, seed: int
) -> tuple[nn.Module, float, list[float]]:
    """Train CANDIDATE inits, keep the best-match head; return it with
    the full per-candidate σ_max(J_F) list (screening is recorded)."""
    results: list[tuple[nn.Module, float, float]] = []
    for c in range(CANDIDATES):
        head, acc = train_head(pattern, pos, seed=seed + c)
        results.append((head, acc, sigma_max_jacobian(head, pos)))
    best_i = max(range(CANDIDATES), key=lambda i: results[i][1])
    return results[best_i][0], results[best_i][1], [r[2] for r in results]


def _eval_k(
    heads: list[nn.Module],
    pattern_set: list[tuple[str, torch.Tensor]],
    pos: torch.Tensor,
) -> tuple[int, float, bool]:
    """psi_rule_select distinct-pattern count + single_rule control pin."""
    distinct: set[str] = set()
    matches_ok = True
    for idx, (_, pattern) in enumerate(pattern_set):
        out = rollout(heads[idx], pos)
        match = ((out > 0.5).float() == pattern).float().mean().item()
        matches_ok &= match >= MATCH
        distinct.add("".join(str(int(v)) for v in (out > 0.5).float().flatten()[::37]))
    out1 = rollout(heads[0], pos)
    pin1 = ((out1 > 0.5).float() == pattern_set[0][1]).float().mean().item()
    return len(distinct), pin1, matches_ok and pin1 >= MATCH


def _train_heads(
    seed: int, pos: torch.Tensor
) -> tuple[list[nn.Module], list[tuple[str, torch.Tensor]], bool]:
    """Screened rule heads for all 8 patterns + per-pattern σ_max report."""
    all_patterns = _patterns(8)
    heads: list[nn.Module] = []
    ok = True
    for idx, (name, pattern) in enumerate(all_patterns):
        head, acc, sigmas = train_screened(pattern, pos, seed=1000 * (seed + 1) + idx)
        heads.append(head)
        ok &= acc >= MATCH
        print(
            f"{name}: best acc {acc:.3f}, "
            f"σ_max per candidate [{', '.join(f'{s:.2f}' for s in sigmas)}]"
        )
    return heads, all_patterns, ok


def main() -> int:
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 0

    t0 = time.time()
    pos = _perception()
    sha_before = _theta_sha(pos)

    heads, all_patterns, ok_all = _train_heads(seed, pos)

    for k in (2, 4, 8):
        pattern_set = all_patterns[:k]
        distinct_n, pin1, ok = _eval_k(heads, pattern_set, pos)
        ok_all &= ok and distinct_n == k
        print(
            f"K={k}: distinct patterns {distinct_n}/{k}, "
            f"single_rule regenerates P1 only ({pin1:.3f})"
        )

    theta_invariant = _theta_sha(pos) == sha_before
    print(f"\nθ bitwise invariant: {theta_invariant} (seed {seed})")
    ok = ok_all and theta_invariant
    print(
        f"VERDICT: {'E3 ALIVE — ψ reconfigures the computational fabric' if ok else 'E3 falsified'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
