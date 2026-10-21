"""Accelerated kernel for Recurrent Attractor.

Delegates to computronium.ontology.geometry.RecurrentGeometry with triton acceleration.
Provides uniform `forward(case)` interface.
"""

from typing import TYPE_CHECKING, Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import geometry_forward

if TYPE_CHECKING:
    import torch

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def forward(case: Any) -> torch.Tensor:
    """Execute one accelerated forward pass using the opaque case object."""
    if not is_available():
        from .reference import forward as reference_forward

        return reference_forward(case)

    return geometry_forward(case)


# Alias for the central registry test which expects `step`
step = forward
