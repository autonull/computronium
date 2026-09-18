"""Accelerated kernel for Predictive Coding algorithm.

Delegates to predictive_settling primitive kernel where possible.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.primitives.state_dynamics.predictive_settling.kernel import (
    is_available as ps_kernel_available,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and ps_kernel_available()


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    from .reference import step as reference_step

    return reference_step(case)
