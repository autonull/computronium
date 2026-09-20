"""Parameter Update primitives package."""

# Import submodules to register their SPECs
from . import (
    elastic_consolidation,  # noqa: F401
    euclidean,  # noqa: F401
    muon,  # noqa: F401
    natural_gradient,  # noqa: F401
    spectral_constrained,  # noqa: F401
)

__all__ = [
    "elastic_consolidation",
    "euclidean",
    "muon",
    "natural_gradient",
    "spectral_constrained",
]
