"""W0.3 component ablation (TODO14 §5): which transformer components are
compatible with local goodness contrast, and which are sabotaged by it?

The Session-2/4 mechanism chain: per-layer goodness-contrast sign
inversions arise (w0_contrast_track), acting on them is harmful (hinge
falsified), freezing them only partially mitigates (gate). The two
out_proj layers inverted FIRST — attention-output goodness is the prime
suspect. The seams already exist in `LocalContrastiveCredit._tf_layer_grad`
(pe excluded at the embed layer, attention applied to in_proj goodness);
this probe extends them into ablation arms.

Arms (all: local_contrastive gate θ=2, muon 0.005, 600 steps, seed 0 —
the w0 3-seed-confirmed rescue cell):
- baseline        parent behavior (replicates 0.190/3.225)
- embed_excluded  embed weight frozen at init (grad exactly 0)
- preattn_good    in_proj goodness on the RAW projection — the attention
                  output never enters the contrast (removes the suspect)
- attention_only  only in_proj/out_proj receive pseudo-gradients
- ffn_only        only ffn1/ffn2 receive pseudo-gradients

Pre-registered predictions (written BEFORE measurement):
- P-A: if attention-output goodness is the inversion source, preattn_good
  materially beats baseline at 600 steps (CE below 3.225) — a structural
  compatibility fix, P4 downgraded to "attention-output sabotage".
- P-B: if the stream organization is the problem, no arm beats baseline
  materially -> the boundary is the objective's fit to the transformer
  stream itself, not one component. W0 graduates toward a Boundary for
  local_contrastive on causal transformers at probe scale.
- P-C (localization): ffn_only collapses relative to attention_only (the
  FFN carries the label-independent representation; the attention
  projection carries the token mixing) -> component map for the tiered
  rewrite question (§5's "highly valuable result").

Run: ``uv run python scripts/probes/w0_component_ablation.py`` (~13 min).
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
    StateDynamicsConfig,
    SubstrateConfig,
)
from computronium.ontology.credit import CreditAssignmentConfig, LocalContrastiveCredit
from computronium.ontology.dynamics import InstantaneousDynamics
from computronium.ontology.geometry import Geometry, TransformerGeometry
from computronium.ontology.substrate import DigitalSubstrate

STEPS = 600
SEED = 0
UPDATE = ParameterUpdateConfig.riemannian_orthogonal(step_size=0.005, momentum=0.9)

Mode = str  # "baseline" | "embed_excluded" | "preattn_good" | "attention_only" | "ffn_only"


class AblatedCredit(LocalContrastiveCredit):
    """LocalContrastiveCredit with one component ablated (probe-only)."""

    def __init__(self, config: CreditAssignmentConfig, mode: Mode):
        super().__init__(config)
        self.mode = mode

    def _excluded(self, name: str, i: int, n_linears: int) -> bool:
        if self.mode == "embed_excluded":
            return i == 0
        if self.mode == "attention_only":
            return ".ffn" in name
        if self.mode == "ffn_only":
            return ".in_proj" in name or ".out_proj" in name
        return False

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
        name = linears[i][0]
        if self._excluded(name, i, len(linears)):
            return torch.zeros_like(linears[i][1].weight)
        tf = geometry if isinstance(geometry, TransformerGeometry) else None
        if self.mode != "preattn_good" or ".in_proj" not in name or i == 0:
            return super()._tf_layer_grad(geometry, x, y_lab, i, b, t, linears)
        # preattn_good: in_proj goodness on the RAW projection output —
        # the attention context never enters this layer's contrast.
        if tf is None:
            return super()._tf_layer_grad(geometry, x, y_lab, i, b, t, linears)
        lin = linears[i][1]
        a_pos = self._tf_recompute(geometry, x, y_lab, i, b, t, linears)
        y_neg = y_lab.view(b, t).roll(1, 0).reshape(b * t)
        a_neg = self._tf_recompute(geometry, x, y_neg, i, b, t, linears)
        with torch.enable_grad():
            w = lin.weight.detach().requires_grad_(True)
            g_pos = torch.nn.functional.linear(a_pos, w)
            g_neg = torch.nn.functional.linear(a_neg, w)
            delta = g_pos.pow(2).mean() - g_neg.pow(2).mean()
            if self.config.contrast_objective == "hinge":
                delta = delta.abs()
            loss = torch.nn.functional.softplus(self.config.contrast_threshold - delta)
            (gw,) = torch.autograd.grad(loss, w)
        return gw


def _build(mode: Mode):
    from computronium import RiemannianOrthogonalUpdate, compose_system

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
        credit=AblatedCredit(
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

    for mode in (
        "baseline",
        "embed_excluded",
        "preattn_good",
        "attention_only",
        "ffn_only",
    ):
        torch.manual_seed(SEED)
        system = _build(mode)
        _train(system, train_t, SEED, STEPS)
        acc, ce = _evaluate(system, val)
        print(
            f"{mode:>16} @ {STEPS}: top-1 {acc:.3f}  val CE {ce:.3f}",
            flush=True,
        )

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
