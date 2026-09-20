# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Lazy State Dynamics primitive.

This primitive implements the sequential (gauss-seidel) eqprop settle with lazy per-layer activation

Reference implementation:
    computronium.primitives.state_dynamics.lazy_state_dynamics.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.lazy_state_dynamics.kernel
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
