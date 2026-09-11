# Psi-PEFT

Standalone frozen-backbone task switching via temporal-ψ ridge readouts.
A frozen backbone acquires, switches, and re-acquires tasks through a
lightweight closed-form ψ readout — θ is never edited, so there is no
catastrophic forgetting **in the validated scope** (conflicting-label
switching on a frozen feature basis).

## What it does

Three readouts over frozen features `h`:

- **`PsiReadout`** — trace-decayed closed-form ridge: accumulate
  `G_t = ρ·G_{t−1} + HᵀH`, `C_t = ρ·C_{t−1} + Hᵀ(onehot(y) − ½)`, solve
  `M = (G + λ·mean(diag G)·I)⁻¹C` exactly. ρ < 1 tracks the *current*
  task; ρ = 1 accumulates forget-free (which *blends* conflicting tasks).
- **`AdaptivePsiReadout`** — conflict-adaptive: the law detects label-
  geometry conflict from its own readout agreement and switches forgetting
  on/off. No task-boundary oracle is handed in.
- **`BufferedPsiReadout`** — speed variant: refit from a bounded recent-
  episode buffer every N updates, with agreement-based drift detection
  (drift clears stale episodes). Fewer ridge solves than per-episode
  refitting; trades some accuracy under conflict (documented below).

## Install / usage

```bash
pip install -e packages/psi-peft
python examples/task_switching_demo.py          # A → B(conflict) → A′
python benchmarks/psi_vs_sgd_readout.py --quick # 6 arms, 3 seeds, mean±var
```

```python
from psi_peft import AdaptivePsiReadout

readout = AdaptivePsiReadout(feature_dim=32, num_classes=4)
for h, y in episodes:            # h = frozen backbone features
    readout.update(h, y)
probs = readout.forward(h_test)  # task-specific logits, θ untouched
```

## Validated scope

Validated on quick-budget CPU probes of conflicting-label task switching
(A → inverted-label B → A) on frozen features — X-TPC-001 (P1 positive,
P2 falsified at non-conflicting coordinate), X-TPC-002 (P1+P2 supported),
X-TPC-003 (real-task MNIST pair, matches SGD readout re-training at
matched budget), X-TAC-001 (self-switching trace decay matches hand-tuned
ρ). The standalone package reproduces the qualitative pattern on a
synthetic conflicting-label benchmark (`--quick`, 3 seeds): temporal arms
switch under conflict where the forget-free (ρ=1) law blends to chance,
all ψ arms leave θ bitwise invariant, and the SGD-readout baseline is
slower at matched quick budget.

## Known limitations / boundaries

- **Conflict requirement**: forgetting-on-demand needs a *conflicting*
  label geometry on the same frozen basis. On non-conflicting streams the
  forget-free law does not lose to temporal credit (X-TPC-001 P2).
- **No optimality claim** vs gradient readout retraining; at larger
  budgets a re-trained readout may dominate (X-TPC-003 P3 boundary).
- **Buffered tradeoff**: at quick budget the buffered variant is ~2×
  faster than per-episode ridge but drops ~0.1 phase accuracy under
  conflict versus `temporal_090` — the planned ≤0.02 margin did NOT hold
  at this budget; use per-episode arms when accuracy dominates.
- CPU quick probes only; no GPU, no large-scale benchmarking.

## Evidence references

Internal evidence: X-TPC-001/002/003, X-TAC-001 (Computronium CEEC ledger
E-000022..E-000026); mechanism source
`computronium/core/plasticity/temporal_psi.py` + `adaptive_psi.py`
(parity enforced by `tests/platform/test_psi_peft_parity.py`).

## Verification level

Unit-tested (trace math vs manual ridge, conflict switching, θ-freeze
invariance, buffer/drift semantics), demo determinism test, quick
benchmark; math parity with the validated internal implementation.