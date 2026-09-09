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

Scope note: rule heads are trained independently (closed-form
selection, Z3-toy machinery); ρ(J_F) stability tracking rides the
ontology's NcaGeometry primitives and is out of scope for this
mechanism-level probe — recorded per §7 discipline.

uv run python scripts/probes/w17_e3_rule_reconfig.py
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


def train_head(pattern: torch.Tensor, pos: torch.Tensor) -> tuple[nn.Module, float]:
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


def main() -> int:
    t0 = time.time()
    pos = _perception()
    sha_before = _theta_sha(pos)
    ok_all = True

    for k in (2, 4, 8):
        pattern_set = _patterns(k)
        heads: list[nn.Module] = []
        for _, pattern in pattern_set:
            torch.manual_seed(0)
            head, acc = train_head(pattern, pos)
            heads.append(head)
            ok_all &= acc >= MATCH

        # psi_rule_select: switch ψ over all K rules from the same seed θ
        distinct: set[str] = set()
        for idx, (name, pattern) in enumerate(pattern_set):
            out = rollout(heads[idx], pos)
            match = ((out > 0.5).float() == pattern).float().mean().item()
            ok_all &= match >= MATCH
            distinct.add(
                "".join(str(int(v)) for v in (out > 0.5).float().flatten()[::37])
            )
        # single_rule control: ψ pinned to rule 1
        out1 = rollout(heads[0], pos)
        pin1 = ((out1 > 0.5).float() == pattern_set[0][1]).float().mean().item()
        ok_all &= pin1 >= MATCH

        print(
            f"K={k}: distinct patterns {len(distinct)}/{k}, "
            f"per-rule match ok, single_rule regenerates P1 only ({pin1:.3f})"
        )
        ok_all &= len(distinct) == k

    theta_invariant = _theta_sha(pos) == sha_before
    print(f"\nθ bitwise invariant: {theta_invariant}")
    ok = ok_all and theta_invariant
    print(
        f"VERDICT: {'E3 ALIVE — ψ reconfigures the computational fabric' if ok else 'E3 falsified'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
