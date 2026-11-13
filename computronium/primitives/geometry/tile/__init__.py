# ruff: file-ignore[unsorted-imports]
# ruff: file-ignore[implicit-namespace-package]
# ruff: file-ignore[non-empty-init-module]
"""
Tile Geometry Primitive.

This primitive implements tilenet with a tile graph the tile count is derived into.

Reference implementation:
    computronium.primitives.geometry.tile.reference

Accelerated kernel:
    computronium.primitives.geometry.tile.kernel
"""

from computronium.acceleration.registry import register_module

globals().update(
    register_module(
        __name__,
        __doc__,
        has_factory=False,
        kernel_fn="step",
        reference_fn="step",
    )
)
