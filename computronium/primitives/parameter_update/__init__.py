"""Parameter Update primitives package."""

# Import submodules to register their SPECs
from . import (
    euclidean,  # ruff: ignore[unused-import]
    muon,  # ruff: ignore[unused-import]
)

__all__ = ["euclidean", "muon"]
