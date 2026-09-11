"""Adaptive feedback projection — the X-ALI-001 mechanism.

The validated lever: instead of keeping a fixed random feedback matrix, the
feedback pathway is slowly re-projected onto the (normalized) forward weight
it feeds, holding the fixed arm's expected Frobenius norm so comparisons stay
matched-norm. Extracted from the Computronium X-ALI-001 probe.
"""

from __future__ import annotations

import math

import torch
from torch import Tensor


class AdaptiveFeedback:
    """Feedback projection ``B`` that drifts with the forward weight.

    ``project`` maps an output-space error back to input space
    (``error @ B``). ``update`` moves ``B`` toward the normalized forward
    weight at ``feedback_lr`` — with ``feedback_lr=1.0`` this is exactly the
    X-ALI-001 re-projection (``B := scale * W / ||W|| * sqrt(numel)``);
    smaller values adapt more slowly.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        init: str = "random",
        feedback_lr: float = 1e-2,
        update_frequency: int = 1,
        feedback_scale: float = 0.1,
        generator: torch.Generator | None = None,
    ) -> None:
        if init != "random":
            raise ValueError(f"unsupported init: {init!r}")
        if update_frequency < 1:
            raise ValueError("update_frequency must be >= 1")
        self.in_features = in_features
        self.out_features = out_features
        self.feedback_lr = feedback_lr
        self.update_frequency = update_frequency
        self.feedback_scale = feedback_scale
        self.weight: Tensor = (
            torch.randn(out_features, in_features, generator=generator) * feedback_scale
        )
        self._steps = 0

    @property
    def expected_norm(self) -> float:
        """Expected Frobenius norm of the random init (the matched norm)."""
        return self.feedback_scale * math.sqrt(self.weight.numel())

    def project(self, error: Tensor) -> Tensor:
        """Project an output-space error ``(..., out_features)`` to input space."""
        return error @ self.weight

    def update(self, forward_weight: Tensor, activity: Tensor | None = None) -> None:
        """Re-project toward the normalized forward weight (norm-matched).

        ``activity`` is accepted for API symmetry; the validated mechanism
        does not use it.
        """
        self._steps += 1
        if self._steps % self.update_frequency != 0:
            return
        w = forward_weight.detach()
        w_norm = float(w.norm().item())
        if w_norm == 0:
            return
        flat_target: Tensor = (w / w_norm) * self.feedback_scale * math.sqrt(w.numel())
        target = flat_target.view_as(self.weight).to(self.weight.dtype)
        self.weight += self.feedback_lr * (target - self.weight)

    def feedback_alignment(self, forward_weight: Tensor) -> float:
        """Cosine between the feedback matrix and the forward weight."""
        return float(
            torch.nn.functional.cosine_similarity(
                self.weight.flatten(), forward_weight.detach().flatten(), dim=0
            )
        )
