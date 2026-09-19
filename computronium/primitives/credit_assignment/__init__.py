"""Credit Assignment primitives.

Reusable credit assignment mechanisms.
"""

# Import submodules to trigger SPEC registration
from . import (
    local_goodness,  # noqa: F401
    pc_alm,  # noqa: F401
    random_projections,  # noqa: F401
    temporal_trace,  # noqa: F401
)

__all__ = [
    "local_goodness",
    "pc_alm",
    "random_projections",
    "temporal_trace",
]
