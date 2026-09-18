"""Accelerated kernel for Forward-Forward algorithm.

Delegates to local_goodness primitive kernel where possible.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.primitives.credit_assignment.local_goodness.kernel import (
    is_available as lg_kernel_available,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and lg_kernel_available()


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the FF algorithm
    from .reference import step as reference_step

    return reference_step(case)
