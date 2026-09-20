"""
Local Goodness Credit Assignment primitive.

This primitive implements layer-local contrastive credit assignment with
two variants:
- Forward-Forward (local_objective="ff"): autograd of goodness contrast
- LEMMA (local_objective="lemma"): closed-form fixed/learned feedback

Reference implementation:
    computronium.primitives.credit_assignment.local_goodness.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.local_goodness.kernel
"""

from computronium.acceleration.registry import register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
