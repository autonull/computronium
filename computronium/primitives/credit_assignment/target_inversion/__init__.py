# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Target Inversion primitive.

This primitive implements the target propagation with transpose feedback for local target propagation

Reference implementation:
    computronium.primitives.credit_assignment.target_inversion.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.target_inversion.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "kernel_step",
    "make_case",
    "reference_step",
]
