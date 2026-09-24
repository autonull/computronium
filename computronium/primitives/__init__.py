"""Primitives package.

Reusable axis-level mechanisms for learning systems.

This module uses lazy loading to avoid importing all primitives at startup.
Access submodules (e.g., `primitives.state_dynamics`) or specific primitives
(e.g., `primitives.state_dynamics.pc_alm_settling`) to trigger registration.
"""

import importlib
from typing import Any

# Submodule names that should be lazily loaded
_SUBMODULES: frozenset[str] = frozenset({  # ruff: ignore[non-empty-init-module]
    "credit_assignment",
    "parameter_update",
    "state_dynamics",
    "geometry",
    "plasticity",
    "substrate",
})

# Primitive modules that can be directly accessed
_PRIMITIVES: dict[str, str] = {  # ruff: ignore[non-empty-init-module]
    # state_dynamics
    "pc_alm_settling": "state_dynamics.pc_alm_settling",
    "predictive_settling": "state_dynamics.predictive_settling",
    "energy_minimization": "state_dynamics.energy_minimization",
    # credit_assignment
    "random_projections": "credit_assignment.random_projections",
    "local_goodness": "credit_assignment.local_goodness",
    "temporal_trace": "credit_assignment.temporal_trace",
    "pc_alm": "credit_assignment.pc_alm",
    "thermodynamic_contrast": "credit_assignment.thermodynamic_contrast",
    # parameter_update
    "muon": "parameter_update.muon",
    "euclidean": "parameter_update.euclidean",
    "natural_gradient": "parameter_update.natural_gradient",
    "spectral_constrained": "parameter_update.spectral_constrained",
    "elastic_consolidation": "parameter_update.elastic_consolidation",
    # plasticity
    "fast_weight": "plasticity.fast_weight",
    "routing": "plasticity.routing",
    "null": "plasticity.null",
    # geometry
    "tile_mesh": "geometry.tile_mesh",
    "feedforward_dag": "geometry.feedforward_dag",
    "recurrent_attractor": "geometry.recurrent_attractor",
    "fabric_pc": "geometry.fabric_pc",
    "ntm": "geometry.ntm",
    "nca": "geometry.nca",
    "spatial_lattice_3d": "geometry.spatial_lattice_3d",
    # substrate
    "digital": "substrate.digital",
    "memristive": "substrate.memristive",
    "neuromorphic": "substrate.neuromorphic",
    "photonic": "substrate.photonic",
    "quantum": "substrate.quantum",
    "noisy": "substrate.noisy",
    "sparse": "substrate.sparse",
    "complex": "substrate.complex",
    "ternary": "substrate.ternary",
}


def __getattr__(name: str) -> Any:
    """Lazy load submodules and primitives."""
    if name in _SUBMODULES:
        module = importlib.import_module(f".{name}", __name__)
        return module

    primitive_path = _PRIMITIVES.get(name)
    if primitive_path:
        module = importlib.import_module(f".{primitive_path}", __name__)
        return module

    raise AttributeError(f"module 'computronium.primitives' has no attribute '{name}'")


def __dir__() -> list[str]:
    """List available attributes for tab completion."""
    return sorted([
        *_SUBMODULES,
        *_PRIMITIVES.keys(),
        "__all__",
        "__doc__",
        "__name__",
        "__package__",
    ])


__all__: list[str] = sorted([*_SUBMODULES, *_PRIMITIVES.keys()])  # ruff: ignore[invalid-all-format]
