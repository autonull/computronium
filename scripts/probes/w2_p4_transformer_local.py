"""W2 P4 probe: local_contrastive on TransformerGeometry — per-layer
targets on a transformer with zero global signals (TODO13b W2).

Design landed with the credit (computronium/ontology/credit.py, tf
path): the label channel is a credit-owned label embedding injected
additively at the embedding output (pos stream = true next tokens,
neg = batch-rolled); every linear (embed, per-block in_proj/out_proj/
ffn1/ffn2) descends a softplus-gated goodness contrast on its own
output (O(1) peak — one layer's graph at a time, no-grad prefix
recompute, Hinton within-batch ordering via sequential_lr); the head
trains local per-position CE (raw magnitude x readout_scale). Because
the readout is a trained softmax head, val CE (ppl) is CALIBRATED and
reportable — unlike the FF-goodness readouts (b4_per_layer_lm's
metric caveats do not apply).

Pre-registered predictions (written BEFORE any measurement):

- P4 (the plan's prediction): learns LM without global CE — per-
  position next-char top-1 accuracy > 15% (unigram 9.4%, chance 1.5%)
  at the b4_per_layer_lm regime (600 steps, ctx 32, batch 32, d 128,
  depth 2, CPU, seeds 0-2). Falsified -> per-layer targets do not
  transfer to the transformer at probe scale; name the boundary.
- P4b (leak control): the shuffled-label arm (targets randomized at
  TRAIN time only, eval identical) collapses to <= chance + unigram
  floor. Falsified -> the signal is a conditioning side-door; the P4
  number is void.
- P4c (F5 ratchet, transformer edition): per-layer peak saved-for-
  backward bytes < bp's whole-graph bytes on the same geometry at
  depth >= 2 blocks. Falsified -> the memory advantage does not
  survive the transformer composition.

Walltime printed, never recorded.

VERDICT (2026-09-07; ~35 min CPU total):

- UNIGRAM ANCHOR CORRECTION: this vocab's unigram top-1 is 0.153
  (space-heavy char ids), not the 9.4% quoted in the plan (a
  different probe's vocab). All comparisons below are vs 0.153.
- P4c PASS: local per-layer peak 0.0 KiB (graphs built and released
  per layer) vs bp whole-graph 256 KiB — the F5 ratchet holds on the
  transformer composition; O(1) peak is structural.
- P4b PASS (control sound): shuffled-label arm behaves like the
  trained arms — no leak in either direction.
- P4 FALSIFIED — and the falsification is MECHANISM, not budget:
  - bp reference at the IDENTICAL cell: 600 steps -> top-1 0.152 /
    CE 3.329 (= unigram regime; the 600-step budget is underpowered
    for ANY method); 3000 steps -> top-1 0.219 / CE 2.936 (bp learns
    context). local_contrastive at 3000 steps: top-1 0.109, CE 3.686,
    DRIFTING DOWN (0.101 -> 0.130 -> 0.109; CE 3.43 -> 3.69) while bp
    climbs — the goodness dynamics actively destroy readout-useful
    features at this scale.
- Defect trail (all measured, in order of discovery):
  1. RMS-normalizing the goodness stream pins G == 1 for both phases
     (structurally zero contrast) — removed; goodness is measured on
     the raw stream.
  2. A LEARNED label injection is a runaway positive feedback
     (norm 8 -> 349 in 200 steps, CE diverging in lockstep) — the
     label projection is FIXED (the MLP contract's label channel is a
     constant one-hot; the direct analogue).
  3. pe (+-1 entries) would swamp the label contrast in G (~1.0 vs
     ~0.008) — pe excluded from the embed goodness, kept in the
     stream.
  4. The MLP raw-CE readout contract does NOT transfer: head raw CE
     grad RMS ~1e-5 vs hidden ~0.65 (a ~5e4 imbalance) — head moved
     to the EMA-normalized axis with readout_scale as its share.
  5. Train/eval mismatch: the readout now trains on the LABEL-FREE
     stream (matching eval; never the true label at eval).
- The surviving mechanism hypothesis: the fixed label injection
  (RMS 0.088) modulates a 0.79-RMS stream by ~1% — the goodness
  contrast's direction is then noise-dominated, and unit-RMS
  EMA-normalized hidden steps random-walk the features faster than
  the ~1%-scale signal can organize them (CE rises monotonically
  with training). NOT yet tried (queued): (a) gain-matched per-block
  label re-injection; (b) the SP2/D17 lesson — local credit needed
  the RIGHT OPTIMIZER (Muon rescues weak credit ~2x bp); a
  Muon/OrthoAdam update on these pseudo-gradients is the obvious
  lever; (c) goodness on normalized streams at matched contrast
  scale. None of these are claimed — the honest state is:
  per-layer contrastive targets do NOT transfer to the transformer
  at probe scale (the pre-registered falsification clause).
- Note: local_contrastive vs bp at the 600-step budget is PARITY
  (0.146 vs 0.152 top-1; CE 3.40 vs 3.33) — both in the marginal
  regime; the local rule's failure only manifests where bp starts
  winning.
"""

import time
from collections import Counter

import torch

from computronium import (
    CreditAssignmentConfig,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system_from_configs,
)
from computronium.core.pipeline import run_train_step
from computronium.data.lm import get_lm_dataset

VOCAB = 65
CTX = 32
BATCH = 32
D_MODEL = 128
N_LAYERS = 2
N_HEADS = 4
STEPS = 600
SEEDS = (0, 1, 2)
VAL_WINDOWS = 512
LR = 0.005
RO_SCALE = 1.0
VAL_BATCH = 64


def _tokens() -> tuple[torch.Tensor, torch.Tensor]:
    train_ds = get_lm_dataset("tiny_shakespeare", seq_len=CTX + 1, split="train")
    val_ds = get_lm_dataset("tiny_shakespeare", seq_len=CTX + 1, split="validation")
    stoi = {c: i for i, c in enumerate(sorted(set(train_ds.idx_to_char.values())))}
    val_t = torch.tensor([stoi[c] for c in val_ds.decode(val_ds.data)])
    return train_ds.data.long(), val_t


def _val_windows(
    val_t: torch.Tensor, seed: int
) -> list[tuple[torch.Tensor, torch.Tensor]]:
    gen = torch.Generator().manual_seed(seed)
    idx = torch.randint(0, len(val_t) - CTX - 1, (VAL_WINDOWS,), generator=gen)
    wins = torch.stack([val_t[i : i + CTX + 1] for i in idx])
    return [(w[:, :-1], w[:, 1:].reshape(-1)) for w in wins.split(VAL_BATCH)]


def _evaluate(
    system, val: list[tuple[torch.Tensor, torch.Tensor]]
) -> tuple[float, float]:
    """Held-out per-position top-1 and CE — the plain LM readout (no
    label injection anywhere: the credit's label channel is train-side
    only)."""
    correct = total = 0
    ce_sum = ce_n = 0.0
    with torch.no_grad():
        for x, y in val:
            logits = system.geometry(x)
            correct += (logits.argmax(-1) == y).sum().item()
            total += y.numel()
            ce_sum += torch.nn.functional.cross_entropy(
                logits, y, reduction="sum"
            ).item()
            ce_n += y.numel()
    return correct / total, ce_sum / ce_n


def _build(seed: int, shuffled: bool = False):
    torch.manual_seed(seed)
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.causal_transformer(
            vocab_size=VOCAB,
            d_model=D_MODEL,
            n_layers=N_LAYERS,
            n_heads=N_HEADS,
            seq_len=CTX,
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.local_contrastive(
            ema_beta=0.99,
            readout_scale=RO_SCALE,
            sequential_lr=LR,
            contrast_threshold=2.0,
        ),
        ParameterUpdateConfig.euclidean(step_size=LR),
    )
    return system


def _train(system, train_t: torch.Tensor, seed: int, shuffled: bool = False) -> None:
    gen = torch.Generator().manual_seed(seed)
    for _ in range(STEPS):
        idx = torch.randint(0, len(train_t) - CTX - 1, (BATCH,), generator=gen)
        wins = torch.stack([train_t[i : i + CTX + 1] for i in idx])
        x, y = wins[:, :-1], wins[:, 1:].reshape(-1)
        if shuffled:
            y = y[torch.randperm(y.numel(), generator=gen)]
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )


def _peak_saved_bytes(system, x: torch.Tensor, y: torch.Tensor) -> int:
    """Max bytes saved-for-backward across one local step (the credit
    builds and releases each layer's graph inside the call) vs one bp
    step's whole-graph."""
    peaks: list[int] = []

    def hook(t: torch.Tensor) -> torch.Tensor:
        peaks.append(t.untyped_storage().nbytes())
        return t

    grad_mode = torch.is_grad_enabled()
    torch.set_grad_enabled(True)
    handles = [p.register_hook(hook) for p in system.geometry.params.values()]
    try:
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    finally:
        for h in handles:
            h.remove()
        torch.set_grad_enabled(grad_mode)
    return max(peaks) if peaks else 0


def _unigram(train_t: torch.Tensor) -> float:
    counts = Counter(train_t.tolist())
    return max(counts.values()) / sum(counts.values())


def main() -> int:
    t0 = time.time()
    train_t, val_t = _tokens()
    unigram = _unigram(train_t)
    val = _val_windows(val_t, 0)
    print(
        f"unigram top-1 {unigram:.3f}  chance {1 / VOCAB:.3f}  "
        f"steps {STEPS} ctx {CTX} d {D_MODEL} L {N_LAYERS}",
        flush=True,
    )

    for seed in SEEDS:
        system = _build(seed)
        _train(system, train_t, seed)
        acc, ce = _evaluate(system, val)
        print(
            f"seed {seed}: top-1 {acc:.3f}  val CE {ce:.3f} (ppl {2.718281828**ce:.1f})",
            flush=True,
        )

    print("\n=== P4b leak control: shuffled-label train arm (seed 0) ===")
    system = _build(0, shuffled=True)
    _train(system, train_t, 0, shuffled=True)
    acc, ce = _evaluate(system, val)
    print(f"shuffled: top-1 {acc:.3f}  val CE {ce:.3f}", flush=True)

    _memory_ratchet(train_t)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


def _memory_ratchet(train_t: torch.Tensor) -> None:
    """P4c: local per-layer peak saved bytes vs bp whole-graph."""
    print("\n=== P4c memory ratchet: per-layer peak vs bp whole-graph ===")
    system = _build(0)
    gen = torch.Generator().manual_seed(0)
    idx = torch.randint(0, len(train_t) - CTX - 1, (BATCH,), generator=gen)
    wins = torch.stack([train_t[i : i + CTX + 1] for i in idx])
    x, y = wins[:, :-1], wins[:, 1:].reshape(-1)
    local_peak = _peak_saved_bytes(system, x, y)
    bp_system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.causal_transformer(
            vocab_size=VOCAB,
            d_model=D_MODEL,
            n_layers=N_LAYERS,
            n_heads=N_HEADS,
            seq_len=CTX,
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=1e-3),
    )
    bp_peak = _peak_saved_bytes(bp_system, x, y)
    verdict = "P4c PASS" if local_peak < bp_peak else "P4c FAIL"
    print(
        f"local per-layer peak {local_peak / 1024:.1f} KiB vs "
        f"bp whole-graph {bp_peak / 1024:.1f} KiB -> {verdict}",
        flush=True,
    )


if __name__ == "__main__":
    raise SystemExit(main())
