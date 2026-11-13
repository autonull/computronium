"""Reference implementation for Attention Geometry.

Delegates to computronium.ontology.geometry.AttentionGeometry. This wrapper provides the
uniform `forward(case)` interface for parity/microbench.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from computronium.harness import geometry_forward

if TYPE_CHECKING:
    import torch


def forward(case: Any) -> torch.Tensor:
    """Execute the reference forward pass using the opaque case object."""
    return geometry_forward(case)


# Alias for the central registry test which expects `step`
step = forward
