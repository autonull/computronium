# ruff: noqa: PLC0415
# ruff: noqa: INP001
"""Tile Mesh Geometry primitive.

This primitive implements the TileNet mesh topology with modular independent
tiles and local routing.

Reference implementation:
    computronium.primitives.geometry.tile_mesh.reference

Accelerated kernel:
    computronium.primitives.geometry.tile_mesh.kernel
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
