"""Primitives package.

Reusable axis-level mechanisms for learning systems.
"""

# Import subpackages to trigger SPEC registration
from . import credit_assignment, parameter_update, state_dynamics  # ruff: ignore[unused-import]

__all__ = [
    "credit_assignment",
    "parameter_update",
    "state_dynamics",
]
