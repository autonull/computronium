"""
Natural Gradient Primitive.

This primitive implements the natural gradient parameter update with Fisher geometry preconditioning.

Reference implementation:
    computronium.primitives.parameter_update.natural_gradient.reference

Accelerated kernel:
    computronium.primitives.parameter_update.natural_gradient.kernel
"""

from computronium.acceleration.registry import register

from .cases import make_case
from .kernel import is_available
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "is_available",
    "kernel_step",
    "make_case",
    "reference_step",
]
