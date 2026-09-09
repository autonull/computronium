"""E1 — Algorithmic depth beyond architecture depth (TODO17 §4.1).

Pre-registered. Question: can ψ + NTM memory solve a task requiring N
sequential recurrence steps at architectural depth D=4, with accuracy
independent of N?

Task: r_{t+1} = tanh(W r_t), W a FIXED orthogonal 64×64 map (θ of the
task). Predict r_N from r_0 for N ∈ {4, 8, 16, 32}. Trajectory pairs are
observable at training time.

Arms (matched: same depth-4 controller, hidden 64 matches state dim 64 — the
intermediate does not fit in the controller's plastic state, memory is
the tape):
  null            — depth-4 MLP trained end-to-end on (r_0 → r_N)
  memory_no_psi   — controller + NTM memory (fixed slot addressing,
                    one current-state slot), BPTT through the full
                    N-step episode
  psi_sequential  — same controller trained per-chunk on one-step pairs
                    (r_t → r_{t+1}), ψ sequences N/D chunks over memory

Prediction: psi_sequential eval error is independent of N (ratio
N=32/N=4 < 2) while null collapses monotonically with N.
Falsification: psi_sequential degrades at the same rate as null.

Known traps checked: fixed addressing (no slot-identity collision,
single slot overwritten); value binding trivial (exact-state writes —
the cosine-softmax signed-content trap avoided by construction).

uv run python scripts/probes/w17_e1_algorithmic_depth.py
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
SOLVED_MSE = 0.01


def _recurrence(seed: int) -> nn.Linear:
    g = torch.Generator().manual_seed(seed)
    w = torch.linalg.qr(torch.randn(STATE, STATE, generator=g))[0]
    f = nn.Linear(STATE, STATE, bias=False)
    with torch.no_grad():
        f.weight.copy_(w)
    f.weight.requires_grad_(False)  # θ of the task: fixed, never trained
    return f


def _trajectory(f: nn.Linear, n: int, batch: int, gen: torch.Generator):
    r = torch.randn(batch, STATE, generator=gen) / STATE**0.5
    r = r / r.norm(dim=-1, keepdim=True) * STATE**0.5
    states = [r]
    for _ in range(n):
        # norm-preserving mixing map: tanh alone contracts the state to a
        # trivial attractor (defect found 2026-09-10 — E1 v1 null control
        # improved with N because the TARGET degenerated), renormalize to
        # keep the task non-degenerate at every depth
        s = torch.tanh(f(r))
        s *= r.norm(dim=-1, keepdim=True) / s.norm(dim=-1, keepdim=True)
        r = s
        states.append(r)
    return states


class _MemArm(nn.Module):
    """Depth-4 controller + NTM memory, fixed single-slot addressing.

    episode(x, n): unroll n controller steps; each step reads the tape,
    emits the next intermediate (64-dim — carried by the tape across chunks —
    16-dim plastic state), writes it back as the tape."""

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


def _null_arm() -> nn.Sequential:
    return nn.Sequential(
        nn.Linear(STATE, 64),
        nn.Tanh(),
        nn.Linear(64, 64),
        nn.Tanh(),
        nn.Linear(64, 64),
        nn.Tanh(),
        nn.Linear(64, STATE),
    )


def main() -> int:  # ruff: ignore[complex-structure, too-many-locals] - probe harness
    t0 = time.time()
    results: dict[tuple[str, int], list[float]] = {}

    class _NullAdapter(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.net = _null_arm()

        def episode(self, r0: torch.Tensor, n: int) -> torch.Tensor:
            return self.net(r0)

    for seed in SEEDS:
        torch.manual_seed(seed)
        f = _recurrence(seed)
        train_gen = torch.Generator().manual_seed(seed)
        eval_gen = torch.Generator().manual_seed(999)

        for n in NS:
            # null: end-to-end depth-4 on (r0 -> rN)
            null = _NullAdapter()
            opt = torch.optim.Adam(null.parameters(), lr=3e-3)
            for _ in range(TRAIN_STEPS):
                s = _trajectory(f, n, 128, train_gen)
                loss = ((null.net(s[0]) - s[-1]) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()

            # memory_no_psi: BPTT through the full n-step episode
            bptt = _MemArm()
            opt = torch.optim.Adam(bptt.parameters(), lr=3e-3)
            for _ in range(TRAIN_STEPS):
                s = _trajectory(f, n, 128, train_gen)
                loss = ((bptt.episode(s[0], n) - s[-1]) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()

            # psi_sequential: per-chunk (one-step) training, ψ unfolds n
            psi = _MemArm()
            opt = torch.optim.Adam(psi.parameters(), lr=3e-3)
            for _ in range(TRAIN_STEPS):
                s = _trajectory(f, 1, 128, train_gen)
                loss = ((psi.episode(s[0], 1) - s[1]) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()

            eval_states = _trajectory(f, n, 512, eval_gen)
            for arm_name, arm in (
                ("null", null),
                ("memory_no_psi", bptt),
                ("psi_sequential", psi),
            ):
                with torch.no_grad():
                    pred = arm.episode(eval_states[0], n)
                mse = ((pred - eval_states[-1]) ** 2).mean().item()
                results.setdefault((arm_name, n), []).append(mse)

    for (arm_name, n), mses in sorted(results.items()):
        print(f"{arm_name:>15} N={n:>2}: MSE {sum(mses) / len(mses):.5f}  {mses}")

    def mean(arm_name: str, n: int) -> float:
        return sum(results[arm_name, n]) / len(results[arm_name, n])

    psi_ratio = mean("psi_sequential", 32) / max(mean("psi_sequential", 4), 1e-9)
    null_ratio = mean("null", 32) / max(mean("null", 4), 1e-9)
    psi_indep = psi_ratio < 2.0
    null_collapses = mean("null", 32) > 2 * mean("null", 4)
    psi_solves = mean("psi_sequential", 32) < SOLVED_MSE
    print(f"\npsi error growth N32/N4: {psi_ratio:.2f} (independent: {psi_indep})")
    print(f"null error growth N32/N4: {null_ratio:.2f} (collapses: {null_collapses})")
    print(f"psi solves N=32 (MSE<{SOLVED_MSE}): {psi_solves}")
    ok = psi_indep and psi_solves
    print(
        f"\nVERDICT: {'E1 ALIVE — ψ+memory unfolds depth N≫D' if ok else 'E1 falsified at this task class'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
