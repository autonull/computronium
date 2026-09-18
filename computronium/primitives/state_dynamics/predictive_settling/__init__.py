# ruff: noqa: PLC0415
# ruff: noqa: INP001
"""Predictive settling primitive.

This primitive implements the predictive coding settling dynamics (PCN).

Reference implementation:
    computronium.primitives.state_dynamics.predictive_settling.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.predictive_settling.kernel
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
