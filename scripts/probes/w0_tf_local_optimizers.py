"""W0.1 probe: transformer local_contrastive × optimizer matrix — the
TODO14 §3 flagship overturn attempt (Session 1 + §8 infrastructure).

The W2 P4 falsification (scripts/probes/w2_p4_transformer_local.py:
per-layer contrastive targets DRIFT DOWN on the transformer, top-1
0.109 / CE 3.686 at 3000 steps while bp climbs to 0.219 / 2.936) was
obtained under Euclidean SGD only. TODO14's central hypothesis —
credit × update interaction I(C,U) — says that falsification is not
yet a boundary: local credit needed the RIGHT OPTIMIZER everywhere
else (SP2: ff × OrthoAdam ≈ BP × OrthoAdam; D17: Muon rescues
ff_hybrid).

Mechanism landed for this probe (TODO14 §8, required): the
``sequential_lr`` recomputation views now use the update rule's ACTUAL
per-parameter displacement (``actual_parameter_displacement``,
snapshot-replay in computronium/ontology/update.py; wired by
``compose_system`` via ``LocalContrastiveCredit.set_update_rule``) —
previously they assumed displacement ≈ step_size, a plain-SGD identity
false for the matrix rules, which would have made a failed
Muon/OrthoAdam cell ambiguous.

Pre-registered predictions (written BEFORE any measurement):

- W0.1-P (overturn, §3 criterion): some optimizer arm reaches
  validation CE materially below the unigram regime (CE < 3.30, the
  600-step bp reference) with top-1 > 0.153 (this vocab's unigram
  anchor) at 3000 steps — the P4 falsification is REOPENED; promote to
  3 seeds. Strong overturn: local arm ≥ bp's 0.219 top-1 at matched
  tokens. Dream: exceeds it.
- W0.1-Q (optimizer sensitivity): the matrix rules (muon, ortho_adam)
  change the SIGN of the training trajectory (CE falling, not the
  euclid arm's monotone rise). Falsified -> the failure is
  optimizer-invariant at probe scale; the injection-gain channel
  (§4 W0.2) becomes the primary suspect and this graduates toward a
  boundary with the optimizer axis now honestly covered.
- W0.1-R (displacement sanity): with a registered matrix rule the
  sequential recompute views differ from the naive step_size·grad view
  (the §8 fix is load-bearing, not cosmetic).

Budget: screen = 300 steps × seed 0 per arm (LR sanity for the matrix
rules, whose per_element_displacement step semantics differ from
euclid's gradient_relative axis). full = 3000 steps, seeds 0-2 for the
screen winners. grad_clip=0 everywhere (per-layer displacement replays
must match the pipeline's update semantics exactly; a global-norm clip
would make the view inconsistent with the applied step).

Walltime printed, never recorded.
"""

import dataclasses
import sys
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
RO_SCALE = 1.0
SEQ_LR = 0.005
VAL_WINDOWS = 512
VAL_BATCH = 64
SCREEN_STEPS = 300
FULL_STEPS = 3000
SEEDS = (0, 1, 2)

EUCLID = ParameterUpdateConfig.euclidean(step_size=0.005, grad_clip=1.0)

# (name, steps, seed) -> update config. Two LRs per matrix rule: the
# per_element_displacement axis is a different lr regime from euclid's.
_ARMS: dict[str, ParameterUpdateConfig] = {
    "euclid": EUCLID,
    "adam_lo": ParameterUpdateConfig.adam(step_size=0.005, grad_clip=0.0),
    "adam_hi": ParameterUpdateConfig.adam(step_size=0.01, grad_clip=0.0),
    "muon_mid": ParameterUpdateConfig.riemannian_orthogonal(
        step_size=0.005, momentum=0.9
    ),
    "muon_lo": ParameterUpdateConfig.riemannian_orthogonal(
        step_size=0.01, momentum=0.9
    ),
    "muon_hi": ParameterUpdateConfig.riemannian_orthogonal(
        step_size=0.02, momentum=0.9
    ),
    "orthoadam_lo": ParameterUpdateConfig.ortho_adam(
        step_size=0.005, ortho_lr=0.003, grad_clip=0.0
    ),
    "orthoadam_hi": ParameterUpdateConfig.ortho_adam(
        step_size=0.01, ortho_lr=0.01, grad_clip=0.0
    ),
}

# Readout-scale share per arm (head CE's slice of the unit-RMS step axis;
# default 1.0 = the w2_p4 contract).
_RO_SCALE: dict[str, float] = {"muon_ro03": 0.3, "muon_ro30": 3.0}
for _name, _ro in _RO_SCALE.items():
    _ARMS[_name] = _ARMS["muon_mid"]


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


def _build(seed: int, update_cfg: ParameterUpdateConfig, ro_scale: float = RO_SCALE):
    torch.manual_seed(seed)
    return compose_system_from_configs(
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
            readout_scale=ro_scale,
            sequential_lr=SEQ_LR,
            contrast_threshold=2.0,
        ),
        update_cfg,
    )


def _train(
    system, train_t: torch.Tensor, seed: int, steps: int, decay: bool = False
) -> None:
    """``decay``: cosine the update rule's step_size from its configured
    value to ~0 over ``steps`` — the decay-past-peak lever (W0 next-step
    #1; the muon trajectory degrades gently at 0.005, collapses at 0.01,
    so a schedule is the obvious cure)."""
    base_lr = system.update.config.step_size
    gen = torch.Generator().manual_seed(seed)
    for i in range(steps):
        if decay:
            import math

            lr_t = base_lr * 0.5 * (1 + math.cos(math.pi * i / steps))
            system.update.config = dataclasses.replace(
                system.update.config, step_size=lr_t
            )
        idx = torch.randint(0, len(train_t) - CTX - 1, (BATCH,), generator=gen)
        wins = torch.stack([train_t[i : i + CTX + 1] for i in idx])
        x, y = wins[:, :-1], wins[:, 1:].reshape(-1)
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
        if (i + 1) % 100 == 0:
            print(f"    step {i + 1}", flush=True)


def _unigram(train_t: torch.Tensor) -> float:
    counts = Counter(train_t.tolist())
    return max(counts.values()) / sum(counts.values())


def _args() -> tuple[bool, bool, int, int]:
    """(full, skip_screen, steps, seed) from argv (short-run friendly)."""
    full = "full" in sys.argv
    skip = "--skip-screen" in sys.argv
    steps = SCREEN_STEPS
    seed = 0
    for a in sys.argv:
        if a.startswith("--steps="):
            steps = int(a.removeprefix("--steps="))
        if a.startswith("--seed="):
            seed = int(a.removeprefix("--seed="))
    return full, skip, steps, seed


def main() -> int:
    t0 = time.time()
    full, skip_screen, full_steps, full_seed = _args()
    train_t, val_t = _tokens()
    unigram = _unigram(train_t)
    val = _val_windows(val_t, 0)
    print(
        f"unigram top-1 {unigram:.3f}  chance {1 / VOCAB:.3f}  "
        f"ctx {CTX} d {D_MODEL} L {N_LAYERS}  mode {'full' if full else 'screen'}",
        flush=True,
    )

    results: dict[str, tuple[float, float]] = {}
    if not skip_screen:
        for name, cfg in _ARMS.items():
            print(f"=== arm {name} ===", flush=True)
            system = _build(0, cfg)
            _train(system, train_t, 0, SCREEN_STEPS)
            acc, ce = _evaluate(system, val)
            results[name] = (acc, ce)
            print(
                f"  seed 0 @ {SCREEN_STEPS}: top-1 {acc:.3f}  val CE {ce:.3f} "
                f"(ppl {min(2.718281828**ce, 1e6):.1f})",
                flush=True,
            )

        print("\n=== screen summary (300 steps, seed 0) ===")
        for name, (acc, ce) in sorted(results.items(), key=lambda kv: kv[1][1]):
            print(f"  {name:>13}: top-1 {acc:.3f}  CE {ce:.3f}", flush=True)

    if full:
        if skip_screen:
            # Pre-registered winner from the recorded screen run
            # (logs/w0_screen.log): muon_lo CE 3.337, the only arm under
            # the 3.35 gate and the only one above the unigram anchor.
            winners = ["muon_lo"]
            for a in sys.argv:
                if a.startswith("--arm="):
                    winners = [a.removeprefix("--arm=")]
        else:
            winners = [
                n for n, (_, ce) in results.items() if ce < 3.35 and n != "euclid"
            ]
        print(
            f"\n=== full phase: winners {winners}"
            f" -> {full_steps} steps, seed {full_seed} ==="
        )
        for name in winners or ["muon_hi"]:
            system = _build(full_seed, _ARMS[name], _RO_SCALE.get(name, RO_SCALE))
            _train(system, train_t, full_seed, full_steps, decay="--decay" in sys.argv)
            acc, ce = _evaluate(system, val)
            print(
                f"  {name} seed {full_seed}: top-1 {acc:.3f}  val CE {ce:.3f} "
                f"(ppl {min(2.718281828**ce, 1e6):.1f})",
                flush=True,
            )

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
