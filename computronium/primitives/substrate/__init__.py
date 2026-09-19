"""Substrate primitives package.

Lazy loading for substrate primitives.
"""

import importlib
from typing import Any

# Primitive modules that can be directly accessed
_PRIMITIVES: frozenset[str] = frozenset({  # noqa: RUF067
    "digital",
})


def __getattr__(name: str) -> Any:
    """Lazy load substrate primitives."""
    if name in _PRIMITIVES:
        return importlib.import_module(f".{name}", __name__)

    raise AttributeError(f"module 'computronium.primitives.substrate' has no attribute '{name}'")


def __dir__() -> list[str]:
    """List available attributes for tab completion."""
    return sorted([*_PRIMITIVES, "__all__", "__doc__", "__name__", "__package__"])


__all__: list[str] = sorted([*_PRIMITIVES])  # noqa: PLE0605