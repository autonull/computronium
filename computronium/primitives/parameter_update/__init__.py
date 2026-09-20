"""Parameter Update primitives package."""

# Import submodules to register their SPECs
from . import (
    elastic_consolidation,  # ruff: ignore[unused-import]
    euclidean,  # ruff: ignore[unused-import]
    muon,  # ruff: ignore[unused-import]
    natural_gradient,  # ruff: ignore[unused-import]
    spectral_constrained,  # ruff: ignore[unused-import]
)

__all__ = [
    "elastic_consolidation",
    "euclidean",
    "muon",
    "natural_gradient",
    "spectral_constrained",
]
