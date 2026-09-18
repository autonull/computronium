"""Accelerated kernel for Feedback Alignment algorithm.

Delegates to random_projections primitive kernel where possible.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.primitives.credit_assignment.random_projections.kernel import (
    is_available as rp_kernel_available,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and rp_kernel_available()


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the FA algorithm
    from .reference import step as reference_step

    return reference_step(case)
