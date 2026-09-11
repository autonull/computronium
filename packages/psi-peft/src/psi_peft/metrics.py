"""Shared probe metrics for psi-peft demos and benchmarks."""

from __future__ import annotations

import hashlib
from typing import Protocol

import torch
from torch import Tensor


class Readout(Protocol):
    """Anything psi-peft demos can fit and query."""

    def update(self, h: Tensor, y: Tensor) -> None: ...

    def forward(self, h: Tensor) -> Tensor: ...


def accuracy(readout: Readout, h: Tensor, y: Tensor) -> float:
    """Mean argmax agreement of a fitted readout over a probe batch."""
    logits = readout.forward(h)
    return float((logits.argmax(-1) == y).float().mean().item())


def theta_sha(model: object) -> str:
    """SHA-256 of the concatenated frozen-parameter bytes (θ invariance)."""
    h = hashlib.sha256()
    for p in model.parameters():  # type: ignore[attr-defined]
        h.update(p.detach().numpy().tobytes())
    return h.hexdigest()


class SyntheticTask:
    """Frozen-feature task: fixed informative basis + label map.

    ``flip()`` produces the CONFLICTING task: same feature basis, inverted
    label geometry — the coordinate where temporal credit wins (X-TPC-002).
    """

    def __init__(
        self,
        gen: torch.Generator,
        feature_dim: int,
        num_classes: int,
        noise_scale: float = 0.1,
    ) -> None:
        self.gen = gen
        self.basis = torch.randn(feature_dim, num_classes, generator=gen) * 3.0
        self.feature_dim = feature_dim
        self.num_classes = num_classes
        self.noise_scale = noise_scale
        self._sign = 1.0

    def flip(self) -> None:
        """Invert the label geometry on the same feature basis."""
        self._sign = -self._sign

    def batch(self, n: int) -> tuple[Tensor, Tensor]:
        h = torch.randn(n, self.feature_dim, generator=self.gen)
        noise = torch.randn(n, self.num_classes, generator=self.gen) * self.noise_scale
        logits = h @ self.basis * self._sign + noise
        return h, logits.argmax(-1)
