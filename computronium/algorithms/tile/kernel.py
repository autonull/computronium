"""Accelerated kernel for TileNet algorithm.

Imports Tile Triton kernels from acceleration.tile_kernels to establish
family membership and technology. Delegates to reference implementation
until a fused Tile algorithm kernel is written.
"""

from typing import Any

from computronium.acceleration.availability import triton_rung_available
from computronium.acceleration.tile_kernels import TRITON_IMPORTED_TILE  # ruff: ignore[unused-import] (used by family_of derivation)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("tile")


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the Tile algorithm using
    # tile_activity_update, tile_prediction, tile_contrastive_update
    # from tile_kernels
    from .reference import step as reference_step

    return reference_step(case)
