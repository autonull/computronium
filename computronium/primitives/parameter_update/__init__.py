"""Parameter Update primitives package."""

# Import submodules to register their SPECs
from . import (
    euclidean,  # noqa: F401
    muon,  # noqa: F401
)

__all__ = ["euclidean", "muon"]
