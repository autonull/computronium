"""Closed-form ridge plasticity: ψ computed, not trained.

B1's closed-form pattern generalized to the P-axis (TODO13b W3): a
readout-residual ψ solved in closed form from NUDGED-phase settled
activity — no gradients anywhere, θ bitwise frozen. The law accumulates
ridge sufficient statistics G = Σ HᵀH, C = Σ Hᵀ(onehot(y) − logits)
over episodes and solves M = (G + λI)⁻¹C exactly; modulation adds the
residual correction H@M to the output logits. This is "LoRA without
gradients": instant, forget-free adaptation that backprop structurally
cannot express (backprop must edit θ, which forgets).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium.core.joint.transition import PlasticityPrimitive

if TYPE_CHECKING:
    from computronium.state import CompositeState, SystemContext


@dataclass(frozen=True, slots=True)
class ClosedFormRidgeConfig:
    """Ridge regularization relative to G's mean diagonal (scale-free)."""

    ridge_lambda: float = 1e-3


class ClosedFormRidgePlasticity(PlasticityPrimitive):
    """ψ = closed-form ridge readout residual on NUDGED settled activity.

    Declares ``psi_phase = "nudged"`` — the pipeline hands the law the
    target-conditioned settle (the D22 root-cause repair: no ψ law can
    consume a supervision term it is never shown). ``z.activity`` carries
    ``h`` (pre-readout settled stream) and ``target``.
    """

    psi_phase = "nudged"

    config: ClosedFormRidgeConfig

    def __init__(self, config: ClosedFormRidgeConfig | None = None):
        self.config = config or ClosedFormRidgeConfig()

    def initial_psi(
        self, context: SystemContext | None, batch_size: int = 1
    ) -> dict[str, Tensor]:
        return {}

    def step(
        self,
        psi: dict[str, Tensor],
        z: CompositeState,
        context: SystemContext,
    ) -> dict[str, Tensor]:
        h = z.activity.get("h")
        target = z.activity.get("target")
        post = z.activity.get("y")
        if not (isinstance(h, Tensor) and isinstance(target, Tensor)):
            return psi
        if not isinstance(post, Tensor):
            return psi
        h = h.detach().float()
        # Bias-augmented ridge: a constant column absorbs systematic logit
        # offsets (a pure weight-space correction has no intercept).
        ones = torch.ones(h.shape[0], 1, device=h.device, dtype=h.dtype)
        h_aug = torch.cat((h, ones), dim=-1)
        num_classes = post.shape[-1]
        onehot = (
            torch.nn.functional.one_hot(target, num_classes).float().to(post.device)
        )
        residual = onehot - torch.softmax(post.detach().float(), dim=-1)
        g = h_aug.T @ h_aug
        c = h_aug.T @ residual.to(h.device)
        gram = psi.get("gram")
        cross = psi.get("cross")
        gram = g if gram is None else gram + g
        cross = c if cross is None else cross + c
        d = gram.shape[0]
        lam = self.config.ridge_lambda * gram.diagonal().mean().clamp_min(1e-12)
        m_aug = torch.linalg.solve(gram + lam * torch.eye(d, device=gram.device), cross)
        return {
            "gram": gram,
            "cross": cross,
            "readout_m": m_aug[:-1],
            "readout_b": m_aug[-1],
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
        out[-1] += corr
        return out


def create_closed_form_ridge_plasticity(
    **kwargs: float,
) -> ClosedFormRidgePlasticity:
    return ClosedFormRidgePlasticity(ClosedFormRidgeConfig(**kwargs))
