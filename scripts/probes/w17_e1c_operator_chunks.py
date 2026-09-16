"""E1c — operator-space closed-form chunks (TODO17 E1 follow-up 3).

Pre-registered. Question: does the E1 composition-error boundary
localize to the CREDIT signal (state-map learning) or to OPERATOR
composition itself?

Design: same task as E1 (fixed orthogonal W, norm-preserving tanh
mixing map, predict r_N from r_0). Instead of a learned state map, fit
the chunk operator in OPERATOR SPACE — a linear Ŵ closed-form ridge
fit on trajectory pairs — and let ψ sequence exact matrix powers:

  operator_fit       Ŵ fit on one-step pairs; rollout N steps
  operator_fit_chunk Ŵ_D fit on D=4-step pairs; rollout N/D chunks

θ training steps: 0 (closed-form solve, E4 precedent). No credit
signal anywhere in the loop — if error still compounds with N, the
boundary is the composition of the operator field, not local credit.

E1 recorded numbers are cited for comparison, never re-run:
psi_sequential one-step MSE 0.004 → N=32 1.21 (21× growth);
E1b multi-step credit T=4 → 0.907 @N=32 (56× growth).

Prediction (pre-registered): composition error of a fitted
norm-preserving operator accumulates linearly (~ N·ε², a √N law),
NOT multiplicatively — so if operator_fit reaches N=32 MSE < 0.01,
the E1 boundary localizes to credit; if error is linear-accumulating
but > 0.01, the boundary is quantitatively an operator-precision
budget (record the law); multiplicative blowup (σ_max(Ŵ) > 1
driving it) is a separate mechanism — record which.

uv run python scripts/probes/w17_e1c_operator_chunks.py
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
D_CHUNK = 4
FIT_BATCH = 8192
EVAL_BATCH = 512
SOLVED_MSE = 0.01
RIDGE = 1e-6


def _recurrence(seed: int) -> nn.Linear:
    g = torch.Generator().manual_seed(seed)
    w = torch.linalg.qr(torch.randn(STATE, STATE, generator=g))[0]
    f = nn.Linear(STATE, STATE, bias=False)
    with torch.no_grad():
        f.weight.copy_(w)
    f.weight.requires_grad_(False)
    return f


def _step(f: nn.Linear, r: torch.Tensor) -> torch.Tensor:
    s = torch.tanh(f(r))
    return s * r.norm(dim=-1, keepdim=True) / s.norm(dim=-1, keepdim=True)


def _trajectory(f: nn.Linear, n: int, batch: int, gen: torch.Generator):
    r = torch.randn(batch, STATE, generator=gen) / STATE**0.5
    r = r / r.norm(dim=-1, keepdim=True) * STATE**0.5
    states = [r]
    for _ in range(n):
        r = _step(f, r)
        states.append(r)
    return states


def _fit_operator(f: nn.Linear, horizon: int, seed: int) -> tuple[torch.Tensor, float]:
    """Closed-form ridge fit of a linear operator on (r_t → r_{t+h})
    pairs; returns Ŵ and its fit MSE."""
    gen = torch.Generator().manual_seed(seed)
    src = torch.randn(FIT_BATCH, STATE, generator=gen) / STATE**0.5
    src = src / src.norm(dim=-1, keepdim=True) * STATE**0.5
    tgt = src
    for _ in range(horizon):
        tgt = _step(f, tgt)
    a = torch.cat((src, torch.ones(FIT_BATCH, 1)), dim=-1)
    ridge = torch.eye(STATE + 1) * RIDGE * FIT_BATCH
    what = torch.linalg.solve(a.T @ a + ridge, a.T @ tgt)
    fit_mse = ((a @ what - tgt) ** 2).mean().item()
    return what, fit_mse


def _rollout(
    what: torch.Tensor, r0: torch.Tensor, n: int, horizon: int
) -> torch.Tensor:
    """ψ sequences n/horizon applications of the fitted chunk operator;
    each chunk is one matrix application (the fit at horizon h)."""
    chunks = n // horizon
    a = torch.cat((r0, torch.ones(r0.shape[0], 1)), dim=-1)
    for _ in range(chunks):
        r0 = a @ what
        a = torch.cat((r0, torch.ones(r0.shape[0], 1)), dim=-1)
    return r0


def _run_seed(
    seed: int,
) -> tuple[
    dict[tuple[str, int], list[float]],
    dict[str, list[float]],
    dict[str, list[float]],
]:
    f = _recurrence(seed)
    eval_gen = torch.Generator().manual_seed(999)

    fits: dict[str, tuple[torch.Tensor, int]] = {}
    fit_mses: dict[str, list[float]] = {}
    sigmas: dict[str, list[float]] = {}
    results: dict[tuple[str, int], list[float]] = {}
    for name, horizon in (("operator_fit", 1), ("operator_fit_chunk", D_CHUNK)):
        what, fit_mse = _fit_operator(f, horizon, seed)
        fits[name] = (what, horizon)
        fit_mses.setdefault(name, []).append(fit_mse)
        sigmas.setdefault(name, []).append(
            torch.linalg.matrix_norm(what[:STATE], ord=2).item()
        )

    for n in NS:
        states = _trajectory(f, n, EVAL_BATCH, eval_gen)
        for name, (what, horizon) in fits.items():
            pred = _rollout(what, states[0], n, horizon)
            mse = ((pred - states[-1]) ** 2).mean().item()
            results.setdefault((name, n), []).append(mse)
    return results, fit_mses, sigmas


def main() -> int:  # ruff: ignore[complex-structure] - probe harness
    t0 = time.time()
    results: dict[tuple[str, int], list[float]] = {}
    fit_mses: dict[str, list[float]] = {}
    sigmas: dict[str, list[float]] = {}

    for seed in SEEDS:
        seed_results, seed_fits, seed_sigmas = _run_seed(seed)
        for key, v in seed_results.items():
            results.setdefault(key, []).extend(v)
        for name, v in seed_fits.items():
            fit_mses.setdefault(name, []).extend(v)
        for name, v in seed_sigmas.items():
            sigmas.setdefault(name, []).extend(v)

    for (name, n), mses in sorted(results.items()):
        print(f"{name:>18} N={n:>2}: MSE {sum(mses) / len(mses):.5f}  {mses}")

    def mean(d, k):
        return sum(d[k]) / len(d[k])

    for name in ("operator_fit", "operator_fit_chunk"):
        print(
            f"{name}: fit MSE {mean(fit_mses, name):.6f}, σ_max {mean(sigmas, name):.4f}"
        )

    print("\nE1 recorded comparison: psi_sequential 0.057 (N=4) → 1.21 (N=32)")

    growth = {}
    for name in ("operator_fit", "operator_fit_chunk"):
        g = mean(results, (name, 32)) / max(mean(results, (name, 4)), 1e-12)
        growth[name] = g
        print(f"{name} error growth N32/N4: {g:.2f}")

    best_n32 = min(mean(results, (name, 32)) for name in growth)
    linear_ok = max(growth.values()) < 2.0 and best_n32 < SOLVED_MSE
    linear_law = (
        abs(mean(results, ("operator_fit", 32)) - 32 * mean(fit_mses, "operator_fit"))
        / max(mean(results, ("operator_fit", 32)), 1e-9)
        < 10.0
    )
    print(
        f"\nN=32 best MSE {best_n32:.5f} (solved <{SOLVED_MSE}: {best_n32 < SOLVED_MSE})"
    )
    print(f"linear-accumulation law ~N·ε² within 10×: {linear_law}")
    if linear_ok:
        verdict = "E1c ALIVE — boundary localizes to CREDIT (state-map learning), not composition"
    elif linear_law:
        verdict = (
            "E1c BOUNDARY SHARPENED — error is linear accumulation ~N·ε² of operator "
            "fit precision: depth is unbounded given operator precision; credit-local "
            "signals must fit operators, not state maps"
        )
    else:
        verdict = (
            "E1c multiplicative — composition of the operator field itself compounds"
        )
    print(f"\nVERDICT: {verdict}")
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if linear_ok else 1


if __name__ == "__main__":
    sys.exit(main())
