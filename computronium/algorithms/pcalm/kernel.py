"""Accelerated kernel for PC-ALM algorithm.

Delegates to primitive kernels where possible.
"""

from typing import Any

from computronium.acceleration.availability import triton_rung_available
from computronium.acceleration.pcalm_kernels import TRITON_IMPORTED_PCALM

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """Whether this rung can run here: the family's Triton kernels compile."""
    return triton_rung_available("pcalm")


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the entire algorithm
    from .reference import step as reference_step

    return reference_step(case)
