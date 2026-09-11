"""Shared probe metrics for local-feedback demos and benchmarks."""

from __future__ import annotations

import torch
from torch import Tensor


def improvement_per_norm(
    loss_before: float, loss_after: float, displacement_norm: float
) -> float:
    """Descent quality per unit parameter displacement (0 when inert)."""
    return (
        (-loss_after + loss_before) / displacement_norm
        if displacement_norm > 0
        else 0.0
    )


def feedback_alignment(feedback_weight: Tensor, forward_weight: Tensor) -> float:
    """Cosine between a feedback matrix and its forward weight."""
    return float(
        torch.nn.functional.cosine_similarity(
            feedback_weight.flatten(), forward_weight.flatten(), dim=0
        )
    )


def pseudo_gradient_alignment(pseudo_grad: Tensor, true_grad: Tensor) -> float:
    """Cosine between a feedback-derived pseudo-gradient and the true gradient."""
    return float(
        torch.nn.functional.cosine_similarity(
            pseudo_grad.flatten(), true_grad.flatten(), dim=0
        )
    )


def late_half_mean(values: list[float]) -> float:
    """Mean over the second half of a trajectory (the X-ALI-001 statistic)."""
    half = len(values) // 2
    tail = values[half:]
    return sum(tail) / len(tail) if tail else 0.0
