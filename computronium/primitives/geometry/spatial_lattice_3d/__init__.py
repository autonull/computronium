# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""Spatial Lattice 3D Geometry primitive.

This primitive implements the 3D spatial lattice topology with local connectivity

Reference implementation:
    computronium.primitives.geometry.spatial_lattice_3d.reference

Accelerated kernel:
    computronium.primitives.geometry.spatial_lattice_3d.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .kernel import forward as kernel_forward
from .kernel import is_available
from .reference import forward as reference_forward
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "is_available",
    "kernel_forward",
    "make_case",
    "reference_forward",
]
