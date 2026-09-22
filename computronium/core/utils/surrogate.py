"""Surrogate gradient functions for spiking neural networks."""

from typing import Literal

import torch
from torch import Tensor

SurrogateType = Literal["fast_sigmoid", "piecewise", "gaussian", "straight_through"]


def surrogate_gradient(
    v: Tensor,
    surrogate_type: SurrogateType = "fast_sigmoid",
    beta: float = 10.0,
) -> Tensor:
    """Compute surrogate gradient for spiking non-linearity.

    Args:
        v: Membrane potential or pre-activation value
        surrogate_type: Type of surrogate gradient function
        beta: Sharpness parameter (higher = closer to true step function)

    Returns:
        Surrogate gradient tensor of same shape as v
    """
    if surrogate_type == "fast_sigmoid":
        return beta / (1 + beta * v.abs()) ** 2
    if surrogate_type == "piecewise":
        return (v.abs() < 1.0 / beta).float() * beta
    if surrogate_type == "gaussian":
        return torch.exp(-0.5 * (beta * v) ** 2) * beta
    # straight_through
    return torch.ones_like(v)


__all__ = ["surrogate_gradient", "SurrogateType"]
