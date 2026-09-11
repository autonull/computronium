"""Fixed-feedback baseline and matched-norm comparison utilities."""

from __future__ import annotations

import torch
from torch import Tensor

from local_feedback.adaptive import AdaptiveFeedback


class FixedFeedback(AdaptiveFeedback):
    """Fixed random feedback — the X-ALI-001 control arm.

    Same projection surface and expected norm as :class:`AdaptiveFeedback`;
    ``update`` never changes the matrix.
    """

    def update(self, forward_weight: Tensor, activity: Tensor | None = None) -> None:
        pass


def matched_norm(left: AdaptiveFeedback, right: AdaptiveFeedback) -> float:
    """Ratio of Frobenius norms between two feedback matrices (1.0 = matched)."""
    left_norm = float(left.weight.norm().item())
    right_norm = float(right.weight.norm().item())
    return left_norm / max(right_norm, torch.finfo(torch.float32).eps)
