"""Reference implementation for NCA Geometry.

Delegates to computronium.ontology.geometry.NcaGeometry. This wrapper provides
the uniform `forward(case)` interface for parity/microbench.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from computronium.harness import geometry_forward

if TYPE_CHECKING:
    import torch


def forward(case: Any) -> torch.Tensor:
    """Execute reference forward pass using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Updated state grid tensor of shape (batch, channels, H, W).
    """
    return geometry_forward(case)


# Alias for the central registry test which expects `step`
step = forward
