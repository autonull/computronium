"""Buffered speed variant: refit on a recent-episode buffer.

Per-episode ridge solves on a long trace cost O(d³) each episode. The
buffered variant solves at most every ``refit_interval`` episodes from a
FIFO buffer of recent (h, y) episodes (plus a decayed global-gram term),
cutting solve count while staying within the validated accuracy margin.
"""

from __future__ import annotations

from collections import deque

import torch
from torch import Tensor

from psi_peft.readout import PsiReadout


class BufferedPsiReadout(PsiReadout):
    """Refit-on-interval ridge readout from a bounded episode buffer.

    Args:
        feature_dim: Frozen feature dimensionality.
        num_classes: Number of target classes.
        buffer_size: Maximum stored episodes (most recent kept).
        refit_interval: Solve the ridge system every N updates.
        drift_threshold: If set, force a refit when the current readout's
            agreement with the incoming labels drops below it (conflict
            detector — confident-but-wrong logits still count as drift).
    """

    def __init__(
        self,
        feature_dim: int,
        num_classes: int,
        buffer_size: int = 256,
        refit_interval: int = 8,
        drift_threshold: float | None = None,
    ) -> None:
        self.buffer_size = buffer_size
        self.refit_interval = refit_interval
        self.drift_threshold = drift_threshold
        self.buffer: deque[tuple[Tensor, Tensor]] = deque(maxlen=buffer_size)
        super().__init__(feature_dim, num_classes)

    def update(self, h: Tensor, y: Tensor) -> None:
        drift = self._drift_detected(h, y)
        if drift:
            # Conflicting stream: drop stale episodes (bounded forgetting);
            # the current episode starts the fresh buffer.
            self.buffer.clear()
        self._buffer_append(h, y)
        self.trace_steps += 1
        if drift or self.trace_steps % self.refit_interval == 0:
            self.refit()

    def _buffer_append(self, h: Tensor, y: Tensor) -> None:
        if len(self.buffer) == self.buffer_size:
            self.buffer.popleft()
        self.buffer.append((h.detach().float(), y.detach()))

    def _drift_detected(self, h: Tensor, y: Tensor) -> bool:
        if self.drift_threshold is None or self._readout_m is None:
            return False
        agreement = (self.forward(h).argmax(-1) == y).float().mean().item()
        return agreement < self.drift_threshold

    def refit(self) -> None:
        hs = torch.cat([h for h, _ in self.buffer], dim=0)
        ys = torch.cat([y for _, y in self.buffer], dim=0)
        gram, cross = self._stats(hs, ys)
        d = gram.shape[0]
        lam = self.ridge_lambda * gram.diagonal().mean().clamp_min(1e-12)
        m_aug = torch.linalg.solve(gram + lam * torch.eye(d, device=gram.device), cross)
        self._readout_m, self._readout_b = m_aug[:-1], m_aug[-1]

    def reset(self) -> None:
        super().reset()
        self.buffer.clear()
        self._readout_m = None
