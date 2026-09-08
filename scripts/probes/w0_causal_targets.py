"""W0.4 causal local targets (TODO14 §6): does local credit need
supervision aligned with the causal structure of the task?

The current construction is ALREADY the token-local next-token arm of
§6: `_tf_recompute` injects ``label_emb[y_lab]`` per position (y_lab =
flattened next-token targets) and the i==0 goodness adds the same — the
untried variants are the MISALIGNED ones. All arms share the i==0
goodness and stream injection (both receive the transformed y_lab from
`_tf_layer_grad`); the readout path keeps TRUE targets (local CE on the
real next token is the task definition, not a treatment arm).

Arms (all: local_contrastive gate θ=2, muon 0.005, 600 steps, seed 0):
- baseline         token-local next-token labels (replicates 0.190/3.225)
- shuffled_pos     per-window position permutation of the labels — same
                   token statistics, WRONG positions (the sharpest
                   alignment test)
- seq_label        one label per window (its first target token) —
                   sequence-level supervision
- random_target    labels from an independent fixed generator — nonzero
                   pos/neg contrast (neg = rolled random), zero task
                   information

Pre-registered predictions (written BEFORE measurement):
- P-A (alignment): baseline > shuffled_pos > {seq_label, random_target}.
  Falsified if shuffled_pos ≈ baseline -> the contrast learns token
  STATISTICS, not causal alignment — the supervision geometry question
  dissolves and the boundary is elsewhere.
- P-B (noise floor): random_target materially below shuffled_pos (pure
  noise vs misaligned-but-real signal). Falsified -> even a random
  channel suffices, i.e. the injection acts as a fixed random anchor
  and the stream organization is doing all the work (the §6 "random
  low-dimensional target" outcome).
- P-C (W0 verdict input): if NO arm and NO misalignment variant changes
  the qualitative picture, W0.4 closes the last rescue hypothesis and
  W0 graduates to Boundary at probe scale.

Run: ``uv run python scripts/probes/w0_causal_targets.py`` (~11 min).
Walltime printed, never recorded.
"""

import torch
from torch import nn
from w0_tf_local_optimizers import (
    CTX,
    D_MODEL,
    N_HEADS,
    N_LAYERS,
    SEQ_LR,
    VOCAB,
    _evaluate,
    _tokens,
    _train,
    _unigram,
    _val_windows,
)

from computronium import (
    GeometryConfig,
    ParameterUpdateConfig,
    RiemannianOrthogonalUpdate,
    StateDynamicsConfig,
    SubstrateConfig,
    compose_system,
)
from computronium.ontology.credit import CreditAssignmentConfig, LocalContrastiveCredit
from computronium.ontology.dynamics import InstantaneousDynamics
from computronium.ontology.geometry import Geometry, TransformerGeometry
from computronium.ontology.substrate import DigitalSubstrate

STEPS = 600
SEED = 0
UPDATE = ParameterUpdateConfig.riemannian_orthogonal(step_size=0.005, momentum=0.9)

Mode = str  # "baseline" | "shuffled_pos" | "seq_label" | "random_target"


class TargetVariantCredit(LocalContrastiveCredit):
    """LocalContrastiveCredit with a transformed hidden-layer target
    signal (probe-only). The readout keeps true targets."""

    def __init__(self, config: CreditAssignmentConfig, mode: Mode):
        super().__init__(config)
        self.mode = mode
        self._rand_gen = torch.Generator().manual_seed(1234)

    def _relabel(self, y_lab: torch.Tensor, b: int, t: int) -> torch.Tensor:
        if self.mode == "shuffled_pos":
            perm = torch.randperm(t, generator=self._rand_gen)
            return y_lab.view(b, t)[:, perm].reshape(-1)
        if self.mode == "seq_label":
            return y_lab.view(b, t)[:, :1].expand(b, t).reshape(-1)
        if self.mode == "random_target":
            return torch.randint(0, VOCAB, (b * t,), generator=self._rand_gen).to(
                y_lab.device
            )
        return y_lab

    def _tf_layer_grad(
        self,
        geometry: Geometry,
        x: torch.Tensor,
        y_lab: torch.Tensor,
        i: int,
        b: int,
        t: int,
        linears: list[tuple[str, nn.Linear]],
    ) -> torch.Tensor:
        return super()._tf_layer_grad(
            geometry, x, self._relabel(y_lab, b, t), i, b, t, linears
        )


def _build(mode: Mode):
    torch.manual_seed(SEED)
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=TransformerGeometry(
            GeometryConfig.causal_transformer(
                vocab_size=VOCAB,
                d_model=D_MODEL,
                n_layers=N_LAYERS,
                n_heads=N_HEADS,
                seq_len=CTX,
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=TargetVariantCredit(
            CreditAssignmentConfig.local_contrastive(
                ema_beta=0.99, sequential_lr=SEQ_LR, contrast_threshold=2.0
            ),
            mode,
        ),
        update=RiemannianOrthogonalUpdate(UPDATE),
    )


def main() -> int:
    import time

    t0 = time.time()
    train_t, val_t = _tokens()
    val = _val_windows(val_t, 0)
    print(f"unigram top-1 {_unigram(train_t):.3f}  chance {1 / VOCAB:.3f}", flush=True)

    for mode in ("baseline", "shuffled_pos", "seq_label", "random_target"):
        torch.manual_seed(SEED)
        system = _build(mode)
        _train(system, train_t, SEED, STEPS)
        acc, ce = _evaluate(system, val)
        print(f"{mode:>14} @ {STEPS}: top-1 {acc:.3f}  val CE {ce:.3f}", flush=True)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
