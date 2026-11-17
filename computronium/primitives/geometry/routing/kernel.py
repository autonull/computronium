"""Accelerated kernel for the hard top-k routing geometry.

The Triton path is not implemented yet; this delegates to the reference so
the uniform ``forward(case)`` interface stays available on every backend.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case: Any) -> Any:
    """Execute one accelerated forward using the opaque case object."""
    from .reference import forward as reference_forward

    return reference_forward(case)


# Alias for the central registry test which expects `step`
step = forward
