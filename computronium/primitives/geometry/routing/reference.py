"""Reference implementation for the hard top-k routing geometry.

Delegates to :class:`RoutingGeometry` (the source of truth). This wrapper
provides the uniform ``forward(case)`` interface for parity/microbench.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from computronium.harness import geometry_forward

if TYPE_CHECKING:
    import torch


def forward(case: Any) -> torch.Tensor:
    """Forward the case's state through its hard top-k gate."""
    return geometry_forward(case)


# Alias for the central registry test which expects `step`
step = forward
