"""Temporal-ψ ridge readout: ψ computed, not trained.

    G_t = ρ·G_{t−1} + H_augᵀH_aug,  C_t = ρ·C_{t−1} + H_augᵀ(onehot(y) − ½),
    M_t = (G_t + λ·mean(diag G_t)·I)⁻¹ C_aug,  o' = h@M + b

ρ < 1 lets ψ forget: the correction tracks the current task distribution,
enabling migration A₀ → A₁ under a bitwise-frozen θ where the forget-free
(ρ = 1) law irreversibly blends both tasks. The regression target is the
centered one-hot label — on a frozen net with saturated logit margins the
softmax-residual form collapses (X-TPC-001 pre-flight defect).
"""

from __future__ import annotations

import torch
from torch import Tensor


class PsiReadout:
    """Trace-decayed ridge readout over frozen features.

    Args:
        feature_dim: Dimensionality of the frozen feature stream ``h``.
        num_classes: Number of target classes.
        trace_decay: Trace decay ρ; 1.0 is the forget-free limit.
        ridge_lambda: Scale-free ridge regularization.
        replace_readout: Forward returns the ridge prediction instead of
            adding a residual correction.
    """

    def __init__(
        self,
        feature_dim: int,
        num_classes: int,
        trace_decay: float = 0.9,
        ridge_lambda: float = 1e-3,
        replace_readout: bool = True,
    ) -> None:
        self.feature_dim = feature_dim
        self.num_classes = num_classes
        self.trace_decay = trace_decay
        self.ridge_lambda = ridge_lambda
        self.replace_readout = replace_readout
        self.reset()

    def reset(self) -> None:
        """Clear the accumulated trace statistics."""
        self._gram: Tensor | None = None
        self._cross: Tensor | None = None
        self._readout_m: Tensor | None = None
        self._readout_b: Tensor | None = None
        self.trace_steps = 0

    def _stats(self, h: Tensor, y: Tensor) -> tuple[Tensor, Tensor]:
        h = h.detach().float()
        ones = torch.ones(h.shape[0], 1, device=h.device, dtype=h.dtype)
        h_aug = torch.cat((h, ones), dim=-1)
        onehot = (
            torch.nn.functional
            .one_hot(y.detach(), self.num_classes)
            .float()
            .to(h.device)
        )
        return h_aug.T @ h_aug, h_aug.T @ (onehot - 0.5).to(h.device)

    def update(self, h: Tensor, y: Tensor) -> None:
        """Accumulate one episode's statistics and re-solve the ridge readout."""
        gram, cross = self._stats(h, y)
        rho = self.trace_decay
        if self._gram is not None:
            gram = gram + self._gram if rho == 1.0 else gram + rho * self._gram
        if self._cross is not None:
            cross = cross + self._cross if rho == 1.0 else cross + rho * self._cross
        self._gram, self._cross = gram, cross
        d = gram.shape[0]
        lam = self.ridge_lambda * gram.diagonal().mean().clamp_min(1e-12)
        m_aug = torch.linalg.solve(gram + lam * torch.eye(d, device=gram.device), cross)
        self._readout_m, self._readout_b = m_aug[:-1], m_aug[-1]
        self.trace_steps += 1

    def forward(self, h: Tensor) -> Tensor:
        """Readout over frozen features (requires at least one update)."""
        if self._readout_m is None or self._readout_b is None:
            raise RuntimeError("PsiReadout.forward before any update()")
        out = h.detach().float() @ self._readout_m + self._readout_b
        return out

    @property
    def has_readout(self) -> bool:
        return self._readout_m is not None

    @property
    def readout(self) -> tuple[Tensor, Tensor] | None:
        """(M, b) ridge solution, or None before the first update."""
        if self._readout_m is None or self._readout_b is None:
            return None
        return self._readout_m, self._readout_b

    @property
    def gram(self) -> Tensor | None:
        return self._gram
