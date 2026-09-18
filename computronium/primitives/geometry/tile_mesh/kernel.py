"""Accelerated kernel for Tile Mesh Geometry.

Delegates to computronium.acceleration.tile_kernels or falls back to reference.
Provides uniform `forward(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import forward as reference_forward

        return reference_forward(case)

    # TODO: Implement tile mesh kernel path for geometry forward
    # For now, delegate to reference
    from .reference import forward as reference_forward

    return reference_forward(case)


# Alias for the central registry test which expects `step`
step = forward
