"""Temporal ψ plasticity: trace-decayed supervised readout residual.

The temporal-credit lever (TODO19 X-TPC-001): like ClosedFormRidgePlasticity
the law consumes the NUDGED-phase target (the D22 root-cause repair — no ψ
law can adapt on target-free first-phase activity), but accumulates its
ridge sufficient statistics through an exponentially-decayed trace:

    G_t = ρ·G_{t−1} + HᵀH,   C_t = ρ·C_{t−1} + Hᵀ(onehot(y) − ½),
    M_t = (G_t + λI)⁻¹ C_t

ρ < 1 makes ψ forget: the correction tracks the *current* task
distribution, enabling migration A₀ → A₁ under bitwise-frozen θ, where
the forget-free (ρ = 1) law irreversibly blends both tasks. The
regression target is the centered one-hot label, NOT the
onehot−softmax residual inherited from ClosedFormRidgePlasticity: on a
frozen net with saturated logit margins the residual is dominated by
the softmax term and the fit collapses (pre-flight defect, X-TPC-001).
θ is never touched — ψ is computed, not trained.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.core.identity_card import AlgorithmIdentityCard

if TYPE_CHECKING:
    from computronium.state import CompositeState, SystemContext


@dataclass(frozen=True, slots=True)
class TemporalPsiConfig:
    """Trace decay ρ and scale-free ridge regularization λ.

    ``replace_readout``: modulate replaces the output logits with the
    ridge prediction instead of adding the correction. The additive
    residual channel is swamped by confident frozen-net margins (measured
    ~9.5 vs correction ~0.4/sample on the D22 switch coordinate — zero
    argmax flips); replacement is the margin-robust channel.
    """

    trace_decay: float = 0.9
    ridge_lambda: float = 1e-3
    replace_readout: bool = False


class TemporalPsiPlasticity:
    """ψ = trace-decayed ridge readout residual on NUDGED settled activity.

    Satisfies the ``PlasticityPrimitive`` protocol structurally (duck-typed
    like the other concrete primitives — inheriting the Protocol itself
    marks the class ``_is_protocol`` and drops it from the identity-card
    scan). Declares ``psi_phase = "nudged"`` — the pipeline hands the law
    the target-conditioned settle. ``z.activity`` carries ``h`` (pre-readout
    settled stream), ``target``, and ``y`` (post-settled logits). ψ keys:
    ``gram``/``cross`` (decayed sufficient statistics), ``readout_m``/
    ``readout_b`` (correction), ``trace_steps`` (episode count, float).
    """

    psi_phase = "nudged"

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="TemporalPsiPlasticity",
        reference_equations=(
            "G_t = ρG_{t−1} + H_augᵀH_aug; C_t = ρC_{t−1} + H_augᵀ(onehot(y) − ½); "
            "M_t = (G_t + λ·mean(diag G_t)·I)⁻¹C_t; o' = o + H@M + b"
        ),
        deviations_from_literature=(
            "ψ computed in closed form per episode, not trained",
            "single-pass exponentially-decayed ridge — no optimality claim vs gradient descent",
            "ρ=1 is the forget-free limit (accumulation without decay)",
        ),
        objective_function="trace-weighted ridge fit of centered one-hot targets from settled h",
        pseudo_gradient_def="none — no gradient path; ψ is a deterministic function of (ψ_{t−1}, activity, target)",
        symmetry_requirements=(
            "G symmetric PSD by construction; solve is exact (torch.linalg.solve)",
        ),
        approximation_parameters=(
            "trace_decay=0.9",
            "ridge_lambda=1e-3",
            "replace_readout=False",
        ),
        validated_limits=(
            "quick-budget CPU probes (3 seeds, ≤600 episodes/task); ρ ∈ {0.5, 0.9, 1.0}",
        ),
    )

    config: TemporalPsiConfig

    def __init__(self, config: TemporalPsiConfig | None = None):
        self.config = config or TemporalPsiConfig()

    def initial_psi(
        self, context: SystemContext | None, batch_size: int = 1
    ) -> dict[str, Tensor]:
        return {}

    def _stats(self, z: CompositeState) -> tuple[Tensor, Tensor] | None:
        h = z.activity.get("h")
        target = z.activity.get("target")
        post = z.activity.get("y")
        if not (isinstance(h, Tensor) and isinstance(target, Tensor)):
            return None
        if not isinstance(post, Tensor):
            return None
        h = h.detach().float()
        ones = torch.ones(h.shape[0], 1, device=h.device, dtype=h.dtype)
        h_aug = torch.cat((h, ones), dim=-1)
        num_classes = post.shape[-1]
        onehot = (
            torch.nn.functional.one_hot(target, num_classes).float().to(post.device)
        )
        residual = onehot - 0.5
        return h_aug.T @ h_aug, h_aug.T @ residual.to(h.device)

    def step(
        self,
        psi: dict[str, Tensor],
        z: CompositeState,
        context: SystemContext,
    ) -> dict[str, Tensor]:
        stats = self._stats(z)
        if stats is None:
            return psi
        g, c = stats
        rho = self.config.trace_decay
        gram, cross = g, c
        if (prev_gram := psi.get("gram")) is not None:
            gram += prev_gram if rho == 1.0 else rho * prev_gram
        if (prev_cross := psi.get("cross")) is not None:
            cross += prev_cross if rho == 1.0 else rho * prev_cross
        d = gram.shape[0]
        lam = self.config.ridge_lambda * gram.diagonal().mean().clamp_min(1e-12)
        m_aug = torch.linalg.solve(gram + lam * torch.eye(d, device=gram.device), cross)
        return {
            "gram": gram,
            "cross": cross,
            "readout_m": m_aug[:-1],
            "readout_b": m_aug[-1],
            "trace_steps": torch.tensor(
                psi.get("trace_steps", torch.zeros(())).item() + 1.0
            ),
        }

    def modulate(
        self, activations: list[Tensor] | Tensor, psi: dict[str, Tensor]
    ) -> list[Tensor] | Tensor:
        m = psi.get("readout_m")
        if m is None or not isinstance(activations, list) or len(activations) < 2:
            return activations
        out = list(activations)
        corr = out[-2] @ m.to(out[-1].dtype)
        bias = psi.get("readout_b")
        if isinstance(bias, Tensor):
            corr += bias.to(out[-1].dtype)
        if self.config.replace_readout:
            out[-1] = corr
        else:
            out[-1] += corr
        return out


def create_temporal_psi_plasticity(
    **kwargs: float,
) -> TemporalPsiPlasticity:
    return TemporalPsiPlasticity(TemporalPsiConfig(**kwargs))
