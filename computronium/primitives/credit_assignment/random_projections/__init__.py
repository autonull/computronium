# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""Random Projections Credit primitive.

This primitive implements fixed random feedback matrix credit assignment
(Feedback Alignment / Direct Feedback Alignment).

Reference implementation:
    computronium.primitives.credit_assignment.random_projections.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.random_projections.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
