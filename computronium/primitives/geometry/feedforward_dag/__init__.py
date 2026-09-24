# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
"""Feedforward DAG Geometry primitive.

This primitive implements the standard feedforward DAG topology (MLP/CNN)
with configurable depth and width.

Reference implementation:
    computronium.primitives.geometry.feedforward_dag.reference

Accelerated kernel:
    computronium.primitives.geometry.feedforward_dag.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import forward as kernel_forward
from .reference import forward as reference_forward
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "kernel_forward",
    "make_case",
    "reference_forward",
]
