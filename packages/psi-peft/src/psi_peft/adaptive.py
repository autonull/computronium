"""Conflict-adaptive variant: trace decay driven by readout agreement.

    a_t = mean(argmax(h@M_{t−1} + b_{t−1}) == y)
    ρ_t = forget_decay if a_t < conflict_threshold else 1.0

Conflict is detected from the law's own readout — no task-boundary oracle.
Warm-up episodes (no readout yet) count as conflicting, so acquisition
always runs at ``forget_decay``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from psi_peft.readout import PsiReadout

if TYPE_CHECKING:
    from torch import Tensor


class AdaptivePsiReadout(PsiReadout):
    """Self-switching trace decay: forgets only when it should.

    Args:
        feature_dim: Frozen feature dimensionality.
        num_classes: Number of target classes.
        conflict_threshold: Mean readout agreement below this marks the
            incoming stream as conflicting.
        forget_decay: ρ used while conflicting (and during warm-up).
    """

    def __init__(
        self,
        feature_dim: int,
        num_classes: int,
        conflict_threshold: float = 0.6,
        forget_decay: float = 0.5,
    ) -> None:
        super().__init__(feature_dim, num_classes, replace_readout=True)
        self.conflict_threshold = conflict_threshold
        self.forget_decay = forget_decay
        self.last_agreement: float | None = None
        self.last_rho: float | None = None

    def update(self, h: Tensor, y: Tensor) -> None:
        agreement: float | None = None
        if self._readout_m is not None and self._readout_b is not None:
            logits = h.detach().float() @ self._readout_m + self._readout_b
            agreement = (logits.argmax(-1) == y.detach()).float().mean().item()
        conflict = agreement is None or agreement < self.conflict_threshold
        self.last_agreement = agreement
        self.last_rho = self.forget_decay if conflict else 1.0
        rho_saved, self.trace_decay = self.trace_decay, self.last_rho
        super().update(h, y)
        self.trace_decay = rho_saved
