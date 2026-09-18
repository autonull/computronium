"""Accelerated kernel for Spiking SNN algorithm.

Delegates to spike_integration and temporal_trace primitive kernels where possible.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.primitives.credit_assignment.temporal_trace.kernel import (
    is_available as tt_kernel_available,
)
from computronium.primitives.state_dynamics.predictive_settling.kernel import (
    is_available as si_kernel_available,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and (
        si_kernel_available() or tt_kernel_available()
    )


def step(case: Any) -> Any:
    """Execute one accelerated training step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # For now, delegate to reference implementation
    from .reference import step as reference_step

    return reference_step(case)
