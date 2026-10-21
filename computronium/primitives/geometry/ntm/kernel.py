"""Accelerated kernel for NTM Geometry.

Delegates to computronium.ontology.geometry.NtmGeometry with triton
acceleration. Provides uniform `forward(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import geometry_forward

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case: Any) -> Any:
    """Execute one accelerated forward pass using the opaque case object."""
    if not is_available():
        from .reference import forward as reference_forward

        return reference_forward(case)

    return geometry_forward(case)


# Alias for the central registry test which expects `step`
step = forward
