"""Geometry primitives package.

Geometry primitives define the topology and routing of computational units.

This module uses lazy loading to avoid importing all primitives at startup.
Access specific primitives (e.g., `primitives.geometry.tile_mesh`) to trigger
registration.
"""

import importlib
from typing import Any

# Primitive modules that can be directly accessed
_PRIMITIVES: dict[str, str] = {  # noqa: RUF067
    "tile_mesh": "tile_mesh",
    "feedforward_dag": "feedforward_dag",
    "recurrent_attractor": "recurrent_attractor",
}


def __getattr__(name: str) -> Any:
    """Lazy load primitives."""
    primitive_path = _PRIMITIVES.get(name)
    if primitive_path:
        module = importlib.import_module(f".{primitive_path}", __name__)
        return module

    raise AttributeError(f"module 'computronium.primitives.geometry' has no attribute '{name}'")


def __dir__() -> list[str]:
    """List available attributes for tab completion."""
    return sorted([
        *_PRIMITIVES.keys(),
        "__all__",
        "__doc__",
        "__name__",
        "__package__",
    ])


__all__: list[str] = sorted([*_PRIMITIVES.keys()])  # noqa: PLE0605