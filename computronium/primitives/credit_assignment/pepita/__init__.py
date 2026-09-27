"""
PEPITA Credit Assignment primitive.

This primitive implements the published PEPITA rule (Dellaferrera & Kreiman 2022,
arXiv 2201.11665): input-modulated second forward pass with exact autograd gradient.

Reference implementation:
    computronium.primitives.credit_assignment.pepita.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.pepita.kernel
"""

from computronium.acceleration.registry import register

from .cases import Case, make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

register(SPEC)  # ruff: ignore[non-empty-init-module] (registration side effect required)

__all__ = [
    "SPEC",
    "Case",
    "kernel_step",
    "make_case",
    "reference_step",
]
