# ruff: file-ignore: [PLC0415, INP001]
"""PC-ALM Credit Assignment primitive.

This primitive implements local Hebbian credit assignment using dual variables
from PCALMDynamics (Augmented Lagrangian Predictive Coding).

Reference implementation:
    computronium.primitives.credit_assignment.pc_alm.reference

Accelerated kernel:
    computronium.primitives.credit_assignment.pc_alm.kernel
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
