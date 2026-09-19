# ruff: file-ignore[import-outside-top-level]
# ruff: file-ignore[implicit-namespace-package]
"""TileNet algorithm.

Modular tiled architecture with TileGeometry. Wraps
computronium.core.presets.create_tile_mlp.

Reference implementation:
    computronium.algorithms.tile.reference

Accelerated kernel:
    computronium.algorithms.tile.kernel
"""

# Register the spec when this module is imported
from computronium.acceleration.registry import register as _register

from .cases import make_case
from .factory import create_tile_mlp
from .kernel import step as kernel_step
from .reference import step as reference_step
from .spec import SPEC

_register(SPEC)  # ruff: ignore[non-empty-init-module]

__all__ = [
    "SPEC",
    "create_tile_mlp",
    "kernel_step",
    "make_case",
    "reference_step",
]
