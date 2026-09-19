"""Algorithms package.

Named compositions of primitives into usable learning systems.

This module uses lazy loading to avoid importing all algorithms at startup.
Access specific algorithms (e.g., `algorithms.pcalm`) to trigger registration.
"""

import importlib
from typing import Any

# Algorithm modules that can be directly accessed
_ALGORITHMS: frozenset[str] = frozenset({  # noqa: RUF067
    "backprop",
    "fa",
    "dfa",
    "ff",
    "pepita",
    "pc",
    "pcalm",
    "eqprop",
    "hebbian",
    "tile",
    "fast_weight",
    "routing",
    "spiking_snn",
    "tp",
})


def __getattr__(name: str) -> Any:
    """Lazy load algorithm modules."""
    if name in _ALGORITHMS:
        module = importlib.import_module(f".{name}", __name__)
        return module

    raise AttributeError(f"module 'computronium.algorithms' has no attribute '{name}'")


def __dir__() -> list[str]:
    """List available attributes for tab completion."""
    return sorted([*_ALGORITHMS, "__all__", "__doc__", "__name__", "__package__"])


__all__: list[str] = sorted(_ALGORITHMS)  # noqa: PLE0605
