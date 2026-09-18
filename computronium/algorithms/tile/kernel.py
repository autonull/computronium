"""Accelerated kernel for TileNet algorithm.

Delegates to tile_mesh primitive kernel where possible.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.primitives.geometry.tile_mesh.kernel import (
    is_available as tile_kernel_available,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and tile_kernel_available()


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    from .reference import step as reference_step

    return reference_step(case)
