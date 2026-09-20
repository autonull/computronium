# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Spectral Constrained primitive.

This primitive implements the spectral-constrained parameter update.

Reference implementation:
    computronium.primitives.parameter_update.spectral_constrained.reference

Accelerated kernel:
    computronium.primitives.parameter_update.spectral_constrained.kernel
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
