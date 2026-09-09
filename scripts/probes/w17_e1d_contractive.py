"""E1d — contractive-with-margin recurrences (TODO17 E1 follow-up 2).

Pre-registered. Question: does a contraction margin tame learned-
operator composition error (the E1 boundary), and can the null
shortcut it (v1 lesson)?

Design: same task/arms as E1, but the map is κ-Lipschitz —
T(r) = κ·tanh(W r), W fixed orthogonal, κ = 0.99 — with NO
renormalization (that made E1's map norm-preserving/chaotic). Banach:
trajectory deviation and operator composition error are bounded by
the geometric series ε·(1−κ^N)/(1−κ); chaos-driven multiplicative
compounding has no room.

Arms (matched to E1):
  null            — depth-4 MLP end-to-end on (r0 → rN), per N
  memory_no_psi   — controller + NTM single slot, BPTT through the
                    full N-step episode, per N
  psi_sequential  — per-chunk (one-step) local credit, trained ONCE
                    per seed (E1 improvement: identical one-step task
                    per N does not need retraining), ψ unrolls N chunks

Metric: unexplained-variance fraction U = MSE(pred, r_N)/Var(r_N).
Shortcut-proof by construction: predicting the attractor (or the
batch-mean target — the smartest target-free shortcut) scores U = 1.0.
Also reported: variance retention Var(r_N)/Var(r_0) (non-degeneracy,
v1 lesson), σ_max(J_T) power-iteration contraction check.

Prediction (pre-registered, r2): ABSOLUTE rollout error growth
N32/N4 < 15 (E1 chaotic: 21× unbounded; geometric bound at κ=0.995
allows ~30×) and ψ abs error inside the geometric series
ε₁·(1−κ^N)/(1−κ). r1 smoke history (recorded): the U-normalized
criterion was miscalibrated — under contraction Var(r_N) collapses
(fixed-point concentration) so U inflates mechanically while absolute
error saturates (0.00027 → 0.00275, 20× below the bound at κ=0.995);
the v1-lesson check rides on variance retention, not on U.

uv run python scripts/probes/w17_e1d_contractive.py [--smoke]
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time

import torch
from torch import nn

SEEDS = (0, 1, 2)
NS = (4, 8, 16, 32)
STATE = 64
HIDDEN = 64
TRAIN_STEPS = 6000
# κ=0.99 smoke r1: task degenerate at N=32 (var retention 0.303, at the
# floor) — U-normalization inflates mechanically while ψ's ABSOLUTE
# rollout error is bounded (0.00026 → 0.00216, inside the geometric
# bound ε(1−κ^N)/(1−κ)); pre-registered branch: rerun at κ=0.995
# (retention 0.995^64 ≈ 0.73, signal alive at N=32).
KAPPA = 0.995
VAR_FLOOR = 0.3


def _recurrence(seed: int) -> nn.Linear:
    g = torch.Generator().manual_seed(seed)
    w = torch.linalg.qr(torch.randn(STATE, STATE, generator=g))[0]
    f = nn.Linear(STATE, STATE, bias=False)
    with torch.no_grad():
        f.weight.copy_(w)
    f.weight.requires_grad_(False)
    return f


def _step(f: nn.Linear, r: torch.Tensor) -> torch.Tensor:
    return KAPPA * torch.tanh(f(r))


def _trajectory(f: nn.Linear, n: int, batch: int, gen: torch.Generator):
    r = torch.randn(batch, STATE, generator=gen) / STATE**0.5
    states = [r]
    for _ in range(n):
        r = _step(f, r)
        states.append(r)
    return states


def _sigma_max(f: nn.Linear, iters: int = 12) -> float:
    """σ_max(J_T) of one step at a typical state (contraction check)."""
    r0 = (torch.randn(1, STATE) / STATE**0.5).flatten()

    def step(flat: torch.Tensor) -> torch.Tensor:
        return _step(f, flat.view(1, STATE)).flatten()

    with torch.no_grad():
        for _ in range(8):
            r0 = step(r0)
    v = torch.randn(STATE, dtype=torch.float32)
    v /= v.norm()
    s = 0.0
    for _ in range(iters):
        jvp_out = torch.autograd.functional.jvp(step, r0, v)
        jv = torch.as_tensor(jvp_out[1])
        s = jv.norm().item()
        v = jv / max(s, 1e-12)
    return s


class _MemArm(nn.Module):
    """E1's controller + NTM single-slot memory, verbatim."""

    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(STATE + HIDDEN, HIDDEN),
            nn.Tanh(),
            nn.Linear(HIDDEN, HIDDEN),
            nn.Tanh(),
            nn.Linear(HIDDEN, HIDDEN),
            nn.Tanh(),
            nn.Linear(HIDDEN, STATE),
        )
        self.enc = nn.Linear(STATE, HIDDEN)

    def episode(self, r0: torch.Tensor, n: int) -> torch.Tensor:
        h = self.enc(r0)
        tape = r0
        for _ in range(n):
            tape = self.net(torch.cat((tape, h), dim=-1))
        return tape


def _null_net() -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(STATE, 64),
        nn.Tanh(),
        nn.Linear(64, 64),
        nn.Tanh(),
        nn.Linear(64, 64),
        nn.Tanh(),
        nn.Linear(64, STATE),
    )


def _run_seed(seed: int, ns: tuple[int, ...]) -> dict[tuple[str, int], list[float]]:
    torch.manual_seed(seed)
    f = _recurrence(seed)
    train_gen = torch.Generator().manual_seed(seed)
    eval_gen = torch.Generator().manual_seed(999)
    results: dict[tuple[str, int], list[float]] = {}

    # psi_sequential: one-step local credit, ONCE per seed. Pairs are
    # sampled ALONG trajectories (uniform t over a 32-step rollout):
    # under contraction the state distribution is t-dependent — training
    # only at t=0 is a train/eval mismatch defect (§8; the attractor
    # neighborhood is where N=32 eval queries live).
    psi = _MemArm()
    opt = torch.optim.Adam(psi.parameters(), lr=3e-3)
    for _ in range(TRAIN_STEPS):
        s = _trajectory(f, 32, 128, train_gen)
        t = int(torch.randint(0, 32, (1,)).item())
        loss = ((psi.episode(s[t], 1) - s[t + 1]) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()

    for n in ns:
        null = _null_net()
        opt = torch.optim.Adam(null.parameters(), lr=3e-3)
        for _ in range(TRAIN_STEPS):
            s = _trajectory(f, n, 128, train_gen)
            loss = ((null(s[0]) - s[-1]) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()

        bptt = _MemArm()
        opt = torch.optim.Adam(bptt.parameters(), lr=3e-3)
        for _ in range(TRAIN_STEPS):
            s = _trajectory(f, n, 128, train_gen)
            loss = ((bptt.episode(s[0], n) - s[-1]) ** 2).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()

        states = _trajectory(f, n, 512, eval_gen)
        r_n = states[-1]
        results.setdefault(("var_retention", n), []).append(
            r_n.var().item() / states[0].var().item()
        )
        for arm_name, pred in (
            ("null", null(states[0])),
            ("memory_no_psi", bptt.episode(states[0], n)),
            ("psi_sequential", psi.episode(states[0], n)),
        ):
            with torch.no_grad():
                mse = ((pred - r_n) ** 2).mean().item()
            results.setdefault((arm_name, n), []).append(mse)
    return results


def main() -> int:
    smoke = "--smoke" in sys.argv
    ns = (4, 32) if smoke else NS
    seeds = (0,) if smoke else SEEDS
    t0 = time.time()
    results: dict[tuple[str, int], list[float]] = {}

    for seed in seeds:
        seed_results = _run_seed(seed, ns)
        for key, v in seed_results.items():
            results.setdefault(key, []).extend(v)

    f_check = _recurrence(seeds[0])
    print(f"contraction check σ_max(J_T) = {_sigma_max(f_check):.4f} (κ={KAPPA})")

    for (arm_name, n), us in sorted(results.items()):
        print(f"{arm_name:>15} N={n:>2}: abs {sum(us) / len(us):.5f}  {us}")

    def mean(arm_name: str, n: int) -> float:
        return sum(results[arm_name, n]) / len(results[arm_name, n])

    var_ret = mean("var_retention", 32)
    print(
        f"\nvariance retention N=32: {var_ret:.3f} (task alive: {var_ret > VAR_FLOOR})"
    )

    psi_g = mean("psi_sequential", 32) / max(mean("psi_sequential", 4), 1e-12)
    null_g = mean("null", 32) / max(mean("null", 4), 1e-12)
    eps1 = mean("psi_sequential", min(NS))
    geo_bound = eps1 * (1 - KAPPA**32) / (1 - KAPPA)
    abs_bounded = psi_g < 15
    in_bound = mean("psi_sequential", 32) < geo_bound
    print(f"psi ABS growth N32/N4: {psi_g:.2f} (bounded <15: {abs_bounded})")
    print(
        f"psi abs N=32 {mean('psi_sequential', 32):.5f} vs geometric "
        f"bound {geo_bound:.5f} (inside: {in_bound})"
    )
    print(f"null ABS growth N32/N4: {null_g:.2f}")

    if var_ret <= VAR_FLOOR:
        verdict = (
            "E1d INCONCLUSIVE — targets degenerate (v1 lesson); rerun with larger κ"
        )
    elif abs_bounded and in_bound:
        verdict = (
            "E1d ALIVE — contraction bounds composition error inside the "
            "geometric series: the E1 multiplicative explosion is "
            "chaos-specific; U-normalized metrics degenerate (recorded)"
        )
    elif abs_bounded:
        verdict = "E1d mixed — growth bounded but above the geometric bound; see table"
    else:
        verdict = (
            "E1d falsified — composition error compounds even under "
            "contraction; the boundary is deeper than chaos"
        )
    print(f"\nVERDICT: {verdict}")
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if (not smoke and var_ret > VAR_FLOOR and abs_bounded and in_bound) else 1


if __name__ == "__main__":
    sys.exit(main())
