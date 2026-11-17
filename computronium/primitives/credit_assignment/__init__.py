"""Credit Assignment primitives.

Reusable credit assignment mechanisms.
"""

# Import submodules to trigger SPEC registration
from . import (
    forward_tangent,  # ruff: ignore[unused-import]
    hybrid,  # ruff: ignore[unused-import]
    local_goodness,  # ruff: ignore[unused-import]
    pc_alm,  # ruff: ignore[unused-import]
    random_projections,  # ruff: ignore[unused-import]
    score_function,  # ruff: ignore[unused-import]
    temporal_trace,  # ruff: ignore[unused-import]
    zeroth_order,  # ruff: ignore[unused-import]
)

__all__ = [
    "forward_tangent",
    "hybrid",
    "local_goodness",
    "pc_alm",
    "random_projections",
    "score_function",
    "temporal_trace",
    "zeroth_order",
]
