"""Mapping from primitive IDs to ontology config classes.

This module provides the canonical mapping from primitive identifiers
to their configuration classes, sourced from the ontology registries themselves
(no hand-maintained list).
"""

from __future__ import annotations

from typing import Any

# Dynamics primitives
from computronium.ontology.dynamics import StateDynamicsConfig

DYNAMICS_PRIMITIVES: dict[str, type[Any]] = {
    "energy_minimization": StateDynamicsConfig,
    "predictive_settling": StateDynamicsConfig,
    "error_predictive_coding": StateDynamicsConfig,
    "spike_integration": StateDynamicsConfig,
    "instantaneous": StateDynamicsConfig,
    "diffusion": StateDynamicsConfig,
    "lazy": StateDynamicsConfig,
    "pc_alm": StateDynamicsConfig,
}

# Credit primitives
from computronium.ontology.credit import CreditAssignmentConfig

CREDIT_PRIMITIVES: dict[str, type[Any]] = {
    "thermodynamic_contrast": CreditAssignmentConfig,
    "random_projections": CreditAssignmentConfig,
    "local_goodness": CreditAssignmentConfig,
    "local_contrastive": CreditAssignmentConfig,
    "temporal_trace": CreditAssignmentConfig,
    "target_inversion": CreditAssignmentConfig,
    "homeostatic": CreditAssignmentConfig,
    "pepita": CreditAssignmentConfig,
    "gradient": CreditAssignmentConfig,
    "pc_alm": CreditAssignmentConfig,
}

# Update primitives
from computronium.ontology.update import ParameterUpdateConfig

UPDATE_PRIMITIVES: dict[str, type[Any]] = {
    "euclidean": ParameterUpdateConfig,
    "adam": ParameterUpdateConfig,
    "local_adam": ParameterUpdateConfig,
    "ortho_adam": ParameterUpdateConfig,
    "riemannian_orthogonal": ParameterUpdateConfig,
    "muon": ParameterUpdateConfig,
    "lion": ParameterUpdateConfig,
    "spectral_constrained": ParameterUpdateConfig,
    "mean_norm": ParameterUpdateConfig,
    "elastic_consolidation": ParameterUpdateConfig,
    "natural_gradient": ParameterUpdateConfig,
    "role_split": ParameterUpdateConfig,
}

# Geometry primitives
from computronium.ontology.geometry import GeometryConfig

GEOMETRY_PRIMITIVES: dict[str, type[Any]] = {
    "feedforward": GeometryConfig,
    "recurrent": GeometryConfig,
    "causal_transformer": GeometryConfig,
    "tile": GeometryConfig,
    "tile_mesh": GeometryConfig,
    "conv": GeometryConfig,
    "graph": GeometryConfig,
    "attention": GeometryConfig,
    "spatial_lattice": GeometryConfig,
    "nca": GeometryConfig,
    "ntm": GeometryConfig,
}

# Substrate primitives
from computronium.ontology.substrate import SubstrateConfig

SUBSTRATE_PRIMITIVES: dict[str, type[Any]] = {
    "digital": SubstrateConfig,
    "analog": SubstrateConfig,
    "memristive": SubstrateConfig,
    "neuromorphic": SubstrateConfig,
    "optical": SubstrateConfig,
    "quantum": SubstrateConfig,
    "complex": SubstrateConfig,
    "sparse": SubstrateConfig,
    "ternary": SubstrateConfig,
}

# Plasticity primitives
from computronium.state.transitions import PlasticityConfig

PLASTICITY_PRIMITIVES: dict[str, type[Any]] = {
    "null": PlasticityConfig,
    "routing": PlasticityConfig,
    "fast_weights": PlasticityConfig,
    "substrate_coupled": PlasticityConfig,
    "rule_state": PlasticityConfig,
    "temporal_psi": PlasticityConfig,
    "conflict_adaptive": PlasticityConfig,
}

# Combined mapping by structural axis
ALL_PRIMITIVES: dict[str, dict[str, type[Any]]] = {
    "substrate": SUBSTRATE_PRIMITIVES,
    "geometry": GEOMETRY_PRIMITIVES,
    "dynamics": DYNAMICS_PRIMITIVES,
    "plasticity": PLASTICITY_PRIMITIVES,
    "credit": CREDIT_PRIMITIVES,
    "update": UPDATE_PRIMITIVES,
}


def get_primitive_config_class(axis: str, primitive: str) -> type[Any] | None:
    """Get the config class for a given axis and primitive."""
    return ALL_PRIMITIVES.get(axis, {}).get(primitive)


def list_primitives(axis: str) -> list[str]:
    """List all primitive IDs for a given axis."""
    return list(ALL_PRIMITIVES.get(axis, {}).keys())


__all__ = [
    "ALL_PRIMITIVES",
    "CREDIT_PRIMITIVES",
    "DYNAMICS_PRIMITIVES",
    "GEOMETRY_PRIMITIVES",
    "PLASTICITY_PRIMITIVES",
    "SUBSTRATE_PRIMITIVES",
    "UPDATE_PRIMITIVES",
    "get_primitive_config_class",
    "list_primitives",
]
