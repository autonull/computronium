# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Sparse Substrate primitive.

This primitive implements the digital substrate with configurable sparsity constraints

Reference implementation:
    computronium.primitives.substrate.sparse.reference

Accelerated kernel:
    computronium.primitives.substrate.sparse.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case, make_case_high_sparsity
from .kernel import is_available
from .kernel import make_substrate as kernel_make_substrate
from .reference import make_substrate as reference_make_substrate
from .spec import SPEC

_register(SPEC)  # noqa: RUF067

__all__ = [
    "SPEC",
    "is_available",
    "kernel_make_substrate",
    "make_case",
    "make_case_high_sparsity",
    "reference_make_substrate",
]
