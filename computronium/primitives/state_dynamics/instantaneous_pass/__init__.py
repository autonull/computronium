# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Instantaneous Pass primitive.

This primitive implements the single-pass feedforward dynamics for backprop and forward-forward algorithms

Reference implementation:
    computronium.primitives.state_dynamics.instantaneous_pass.reference

Accelerated kernel:
    computronium.primitives.state_dynamics.instantaneous_pass.kernel
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
