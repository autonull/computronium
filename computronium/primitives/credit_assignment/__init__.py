"""Credit Assignment primitives.

Reusable credit assignment mechanisms.
"""

# Import submodules to trigger SPEC registration
from . import (
    local_goodness,  # ruff: ignore[unused-import]
    pc_alm,  # ruff: ignore[unused-import]
    random_projections,  # ruff: ignore[unused-import]
    temporal_trace,  # ruff: ignore[unused-import]
)

__all__ = [
    "local_goodness",
    "pc_alm",
    "random_projections",
    "temporal_trace",
]
