# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Noisy Substrate primitive.

This primitive implements the digital substrate with configurable additive Gaussian noise

Reference implementation:
    computronium.primitives.substrate.noisy.reference

Accelerated kernel:
    computronium.primitives.substrate.noisy.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case, make_case_high_noise
from .kernel import is_available
from .kernel import make_substrate as kernel_make_substrate
from .reference import make_substrate as reference_make_substrate
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "is_available",
    "kernel_make_substrate",
    "make_case",
    "make_case_high_noise",
    "reference_make_substrate",
]
