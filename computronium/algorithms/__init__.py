"""Algorithms package.

Named compositions of primitives into usable learning systems.

This module uses lazy loading to avoid importing all algorithms at startup.
Access specific algorithms (e.g., `algorithms.pcalm`) to trigger registration.
"""

import importlib
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

# Algorithm modules that can be directly accessed.
PUBLIC_ALGORITHMS: Final[frozenset[str]] = frozenset({  # ruff: ignore[non-empty-init-module]
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

# TODO91 S1: shipped algorithm packages that are not part of the selector
# surface. Each is reached through a named preset; the value is the factory
# that builds it. A package in neither table is undeclared, and the inventory
# reports it as `unknown`.
INTERNAL_ALGORITHMS: Final[Mapping[str, str]] = MappingProxyType({  # ruff: ignore[non-empty-init-module]
    "diffusion_eqprop": "computronium.core.presets.create_diffusion_eqprop_mlp",
    "directed_ep": "computronium.core.presets.create_directed_ep_mlp",
    "finite_nudge_ep": "computronium.core.presets.create_finite_nudge_ep_mlp",
    "holomorphic_ep": "computronium.core.presets.create_holomorphic_ep_mlp",
    "momentum_eqprop": "computronium.core.presets.create_momentum_eqprop_mlp",
    "sparse_eqprop": "computronium.core.presets.create_sparse_eqprop_mlp",
    "ternary_eqprop": "computronium.core.presets.create_ternary_eqprop_mlp",
})

ALL_ALGORITHMS: Final[frozenset[str]] = PUBLIC_ALGORITHMS | frozenset(  # ruff: ignore[non-empty-init-module]
    INTERNAL_ALGORITHMS
)

# Backwards-compatible private alias: the lazy namespace uses this name.
_ALGORITHMS = PUBLIC_ALGORITHMS  # ruff: ignore[non-empty-init-module]


def __getattr__(name: str) -> Any:
    """Lazy load algorithm modules."""
    if name in _ALGORITHMS:
        module = importlib.import_module(f".{name}", __name__)
        return module

    raise AttributeError(f"module 'computronium.algorithms' has no attribute '{name}'")


def __dir__() -> list[str]:
    """List available attributes for tab completion."""
    return sorted([*_ALGORITHMS, "__all__", "__doc__", "__name__", "__package__"])


__all__: list[str] = sorted(_ALGORITHMS)  # ruff: ignore[invalid-all-format]
