"""Credit Assignment primitives.

Reusable credit assignment mechanisms.
"""

# Import submodules to trigger SPEC registration
from . import (
    hybrid,  # ruff: ignore[unused-import]
    local_goodness,  # ruff: ignore[unused-import]
    pc_alm,  # ruff: ignore[unused-import]
    random_projections,  # ruff: ignore[unused-import]
    temporal_trace,  # ruff: ignore[unused-import]
)

__all__ = [
    "hybrid",
    "local_goodness",
    "pc_alm",
    "random_projections",
    "temporal_trace",
]
