"""Plasticity Primitives: Non-null plasticity laws for the joint architecture."""

from __future__ import annotations

from computronium.core.joint.transition import (
    NullPlasticity,
    PlasticityConfig,
    PlasticityPrimitive,
)
from computronium.core.plasticity.adaptive_psi import (
    ConflictAdaptivePsiConfig,
    ConflictAdaptivePsiPlasticity,
    conflict_adaptive_from_config,
    create_conflict_adaptive_psi_plasticity,
)
from computronium.core.plasticity.closed_form import (
    ClosedFormRidgeConfig,
    ClosedFormRidgePlasticity,
    create_closed_form_ridge_plasticity,
)
from computronium.core.plasticity.fast_weights import (
    FastWeightPlasticity,
    FastWeightPlasticityConfig,
    create_fast_weight_plasticity,
)
from computronium.core.plasticity.routing import (
    RoutingPlasticity,
    RoutingPlasticityConfig,
    create_routing_plasticity,
)
from computronium.core.plasticity.rule_state import (
    RuleStatePlasticity,
    RuleStatePlasticityConfig,
    create_rule_state_plasticity,
)
from computronium.core.plasticity.substrate_coupled import (
    SubstrateCoupledPlasticity,
    create_substrate_coupled_plasticity,
)
from computronium.core.plasticity.temporal_psi import (
    TemporalPsiConfig,
    TemporalPsiPlasticity,
    create_temporal_psi_plasticity,
    temporal_psi_from_config,
)

__all__ = [  # ruff: ignore[unsorted-dunder-all]
    # Base
    "PlasticityConfig",
    "PlasticityPrimitive",
    "NullPlasticity",
    # Conflict-adaptive psi (TODO19 R7 — self-switching trace decay)
    "ConflictAdaptivePsiPlasticity",
    "ConflictAdaptivePsiConfig",
    "create_conflict_adaptive_psi_plasticity",
    "conflict_adaptive_from_config",
    # Closed Form (W3 — ψ computed, not trained)
    "ClosedFormRidgePlasticity",
    "ClosedFormRidgeConfig",
    "create_closed_form_ridge_plasticity",
    # Routing
    "RoutingPlasticity",
    "RoutingPlasticityConfig",
    "create_routing_plasticity",
    # Fast Weights
    "FastWeightPlasticity",
    "FastWeightPlasticityConfig",
    "create_fast_weight_plasticity",
    # Substrate Coupled
    "SubstrateCoupledPlasticity",
    "create_substrate_coupled_plasticity",
    # Temporal Psi (TODO19 X-TPC-001)
    "TemporalPsiPlasticity",
    "TemporalPsiConfig",
    "create_temporal_psi_plasticity",
    "temporal_psi_from_config",
    # Rule State (Z3)
    "RuleStatePlasticity",
    "RuleStatePlasticityConfig",
    "create_rule_state_plasticity",
]
