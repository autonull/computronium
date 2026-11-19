"""Accelerated kernel for Feedback Alignment algorithm.

Delegates to random_projections primitive kernel where possible.
"""

from typing import Any

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    """No fused feedback-alignment kernel exists; the reference path is the only rung."""
    return False


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    # In the future, this could fuse the FA algorithm
    from .reference import step as reference_step

    return reference_step(case)
