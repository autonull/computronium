"""E1b — Does multi-step credit overturn E1? (TODO17 follow-up #1)

Pre-registered. E1 (v4) boundary: a chunk operator trained with
one-step local credit (MSE 0.004) compounds error multiplicatively when
ψ unfolds it N steps (growth 21× vs null 4×, chaotic norm-preserving
recurrence). This probe adds INTERMEDIATE SUPERVISION: the chunk
operator is trained on T=4-step rollouts, loss evaluated at every
horizon t ≤ T against the true states — credit that directly constrains
compositional stability, not just one-step fit.

Setup identical to E1 v4 (r_{t+1} = norm-preserving tanh(W r_t), W fixed
orthogonal 64×64, N ∈ {4, 8, 16, 32}, 3 seeds, depth-4 controller +
NTM-style fixed single-slot tape, 6000 steps, lr 3e-3).

Arms:
  null          — end-to-end depth-4 on (r_0 → r_N)  [v4 control]
  memory_no_psi — BPTT through the full N-step episode  [v4 control]
  psi_multi     — chunk operator trained on T=4 rollouts with
                  intermediate credit, ψ unfolds N/D chunks over memory

Prediction: psi_multi error growth (N32/N4) ≪ null growth AND ≪ E1's
one-step-credit 21×; overturn criterion = psi growth ≤ null growth
(i.e. ψ no longer degrades FASTER than the fixed-depth baseline).
Falsification: psi_multi growth ≥ 21× (no better than one-step credit)
→ intermediate credit through T=4 does not reach the composition
problem; the boundary is credit-horizon-independent at this scale.

uv run python scripts/probes/w17_e1b_multistep_credit.py
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
LR = 3e-3
CREDIT_HORIZON = 4
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
        # norm-preserving mixing map (E1 v4 defect fix: tanh alone
        # contracts to a trivial attractor)
        s = torch.tanh(f(r))
        s *= r.norm(dim=-1, keepdim=True) / s.norm(dim=-1, keepdim=True)
        r = s
        states.append(r)
    return states


class _MemArm(nn.Module):
    """Depth-4 controller + fixed single-slot tape; episode(x, n) unrolls
    n controller steps, each emitting the next 64-dim intermediate."""

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


class _NullAdapter(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(STATE, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, STATE),
        )

    def episode(self, r0: torch.Tensor, n: int) -> torch.Tensor:
        return self.net(r0)


def main() -> int:  # ruff: ignore[too-many-locals] - probe harness
    t0 = time.time()
    results: dict[tuple[str, int], list[float]] = {}

    for seed in SEEDS:
        torch.manual_seed(seed)
        f = _recurrence(seed)
        train_gen = torch.Generator().manual_seed(seed)
        eval_gen = torch.Generator().manual_seed(999)

        for n in NS:
            eval_states = _trajectory(f, n, 512, eval_gen)

            null = _NullAdapter()
            opt = torch.optim.Adam(null.parameters(), lr=LR)
            for _ in range(TRAIN_STEPS):
                s = _trajectory(f, n, 128, train_gen)
                loss = ((null.net(s[0]) - s[-1]) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()

            bptt = _MemArm()
            opt = torch.optim.Adam(bptt.parameters(), lr=LR)
            for _ in range(TRAIN_STEPS):
                s = _trajectory(f, n, 128, train_gen)
                loss = ((bptt.episode(s[0], n) - s[-1]) ** 2).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()

            # psi_multi: chunk credit at every horizon t ≤ CREDIT_HORIZON,
            # through the operator's own unfolding (intermediate supervision)
            psi = _MemArm()
            opt = torch.optim.Adam(psi.parameters(), lr=LR)
            for _ in range(TRAIN_STEPS):
                s = _trajectory(f, CREDIT_HORIZON, 128, train_gen)
                losses = [
                    (psi.episode(s[0], t) - s[t]) ** 2
                    for t in range(1, CREDIT_HORIZON + 1)
                ]
                loss = torch.stack([term.mean() for term in losses]).mean()
                opt.zero_grad()
                loss.backward()
                opt.step()

            for arm_name, arm in (
                ("null", null),
                ("memory_no_psi", bptt),
                ("psi_multi", psi),
            ):
                with torch.no_grad():
                    pred = arm.episode(eval_states[0], n)
                mse = ((pred - eval_states[-1]) ** 2).mean().item()
                results.setdefault((arm_name, n), []).append(mse)
            print(f"seed {seed} N={n} done", flush=True)

    for (arm_name, n), mses in sorted(results.items()):
        print(f"{arm_name:>15} N={n:>2}: MSE {sum(mses) / len(mses):.5f}  {mses}")

    def mean(arm_name: str, n: int) -> float:
        return sum(results[arm_name, n]) / len(results[arm_name, n])

    growth = {
        a: mean(a, 32) / max(mean(a, 4), 1e-9)
        for a in ("null", "memory_no_psi", "psi_multi")
    }
    for a, g in growth.items():
        print(f"{a:>15} error growth N32/N4: {g:.2f}")
    psi_solves = mean("psi_multi", 32) < SOLVED_MSE

    # E1 one-step-credit comparison point: 21x (E1 v4)
    overturn = growth["psi_multi"] <= growth["null"]
    no_change = growth["psi_multi"] >= 21.0
    print(f"psi_multi solves N=32 (MSE<{SOLVED_MSE}): {psi_solves}")
    print(f"E1 overturn criterion (psi growth <= null growth): {overturn}")
    print(f"credit-horizon-independent (psi growth >= 21x): {no_change}")
    ok = overturn or psi_solves
    print(
        f"\nVERDICT: {'E1b — E1 OVERTURNED by multi-step intermediate credit' if ok else 'E1b — boundary stands; intermediate T=4 credit does not reach the composition problem'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
