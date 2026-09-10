"""E2 sub-prediction: compression ratio vs rollout horizon T (TODO17 §4.2).

The E2 headline measured ratio 2.66x at one operating point. The
pre-registered prediction "the ratio grows with T" has two measurable
forms at fixed output size (32x32 = 1024 bits):

  (a) rollout-horizon INVARIANCE: the same |ψ| reaches match >= 0.95 at
      every T in the sweep (unfolding is horizon-flexible);
  (b) program-size SHRINKAGE: a narrower ψ (fewer params) suffices as T
      grows — longer unfolding trades architecture for time, the
      Kolmogorov-unfolding signature proper.

Arms: ψ rule with hidden 16 (385 params) and hidden 4 (93 params),
patterns checker/stripes/plaid, seed 0, T in {2, 4, 8, 16, 32, 64},
600 training steps each (matched to E2's budget).

Prediction: (a) holds for the wide rule; (b) shows a critical T below
which the narrow rule cannot express the transient (checker needs
parity alternation — plausibly unreachable at small T) and succeeds at
large T. Falsification: match is T-independent for both sizes (no
time-architecture trade) or degrades with T everywhere.

uv run python scripts/probes/w17_e2_t_sweep.py
Walltime printed, never recorded.

RESULT (2026-09-10, 452.6 s): wide rule match 1.000 at EVERY T ∈
{2..64} on all 3 patterns; the 97-param narrow rule ALSO reaches
match 1.000 at every T (ratio 11.0x vs the 385-param rule's 2.66x).
Verdict: (a) horizon flexibility YES; (b) program-size shrinkage YES
but NOT T-driven — the narrow rule solves at T=2 too, so the ratio
lift is expressiveness of the ψ-supplied positional basis, not a
time-architecture trade. The pre-registered "ratio grows with T" is
NOT confirmed in its specific form on this pattern set (checker/
stripes/plaid are all cheap in rule space); a genuine T-dependence
would need patterns whose rule-space description exceeds the 93-param
budget (fractals — the original §4.2 procedural-sprite target class).
"""

from __future__ import annotations

import sys
import time

import torch
from torch import nn
from torch.nn import functional
from w17_e2_kolmogorov import MATCH, H, W, _pattern, _perception

TS = (2, 4, 8, 16, 32, 64)
TRAIN_STEPS = 600
DEVICE = "cpu"


class _RuleN(nn.Module):
    """_Rule with parameterized hidden width."""

    def __init__(self, hidden: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(22, hidden), nn.Tanh(), nn.Linear(hidden, 1))

    def rollout(self, grid: torch.Tensor, t: int, pos: torch.Tensor) -> torch.Tensor:
        x = grid
        for _ in range(t):
            nb = functional.pad(x[None, None], (1, 1, 1, 1), mode="circular")
            nb = nb[0].unfold(1, 3, 1).unfold(2, 3, 1).reshape(9, H, W)
            inp = torch.cat((nb, pos.permute(2, 0, 1), x[None]), dim=0).permute(1, 2, 0)
            nxt = torch.sigmoid(self.net(inp)[..., 0])
            x = nxt
        return x


def _train(pattern: torch.Tensor, pos: torch.Tensor, t: int, hidden: int) -> float:
    torch.manual_seed(0)
    rule = _RuleN(hidden)
    opt = torch.optim.Adam(rule.parameters(), lr=0.03)
    grid = torch.zeros(H, W)
    for _ in range(TRAIN_STEPS):
        out = rule.rollout(grid, t, pos)
        loss = functional.mse_loss(out, pattern)
        opt.zero_grad()
        loss.backward()
        opt.step()
    match = (out > 0.5).to(torch.float)
    return (match * pattern + (1 - match) * (1 - pattern)).mean().item()


def main() -> int:
    t0 = time.time()
    pos = _perception()
    ok_wide = True
    narrow_pass_ts: list[int] = []
    print("ψ acquisition: WRITTEN... no — trained per E2's protocol (600 steps)")
    for name in ("checker", "stripes", "plaid"):
        pattern = _pattern(name)
        for hidden in (16, 4):
            params = sum(p.numel() for p in _RuleN(hidden).parameters())
            accs = []
            for t in TS:
                acc = _train(pattern, pos, t, hidden)
                accs.append(acc)
                if hidden == 16:
                    ok_wide &= acc >= MATCH
                elif acc >= MATCH:
                    narrow_pass_ts.append(t)
            verdict = " ".join(
                f"T{t}:{a:.3f}{'✓' if a >= MATCH else '×'}" for t, a in zip(TS, accs)
            )
            print(
                f"{name:>8} h={hidden:>2} ({params:>3} params): {verdict}", flush=True
            )
    print(
        f"\nnarrow-rule (93 params, ratio {H * W / 93:.1f}x) passes at T = "
        f"{sorted(set(narrow_pass_ts))}"
    )
    print(
        f"\nVERDICT: wide rule horizon-flexible: {'YES' if ok_wide else 'NO'}; "
        f"program-size shrinkage with T: "
        f"{'YES' if narrow_pass_ts and max(narrow_pass_ts) > min(TS) else 'NO'}"
    )
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
