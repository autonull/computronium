"""
Null Plasticity Primitive.

This primitive implements the zero-extension identity for plasticity:
ψ_{t+1} = ψ_t — makes 5-D systems valid 6-D coordinates.

Reference implementation:
    computronium.primitives.plasticity.null.reference

Accelerated kernel:
    computronium.primitives.plasticity.null.kernel
"""

from computronium.acceleration.registry import register

from .cases import make_case
from .kernel import is_available
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "is_available",
    "kernel_step",
    "make_case",
    "reference_step",
]
