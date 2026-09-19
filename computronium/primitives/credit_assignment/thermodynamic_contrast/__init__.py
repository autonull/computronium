"""
Thermodynamic Contrast Credit Primitive.

This primitive implements Equilibrium Propagation contrastive credit assignment
using the free/nudged phase difference.

Reference implementation:
    computronium.primitives.credit_assignment.thermodynamic_contrast.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.thermodynamic_contrast.kernel
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
