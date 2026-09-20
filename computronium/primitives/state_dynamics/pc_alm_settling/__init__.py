# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""PC-ALM settling primitive.

This primitive implements the primal-dual settling dynamics used by
Augmented Lagrangian Predictive Coding.

Reference implementation:
    computronium.primitives.state_dynamics.pc_alm_settling.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.pc_alm_settling.kernel
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
