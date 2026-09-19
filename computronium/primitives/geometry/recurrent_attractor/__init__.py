# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Recurrent Attractor primitive.

This primitive implements the recurrent attractor geometry for energy-based models like equilibrium propagation

Reference implementation:
    computronium.primitives.geometry.recurrent_attractor.reference

Accelerated kernel:
    computronium.primitives.geometry.recurrent_attractor.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import forward as kernel_forward
from .reference import forward as reference_forward
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "kernel_forward",
    "make_case",
    "reference_forward",
]
