# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Substrate Coupled primitive.

This primitive implements the substrate-coupled plasticity.

Reference implementation:
    computronium.primitives.plasticity.substrate_coupled.reference

Accelerated kernel:
    computronium.primitives.plasticity.substrate_coupled.kernel
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
