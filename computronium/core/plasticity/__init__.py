"""Plasticity Primitives: Non-null plasticity laws for the joint architecture."""

from __future__ import annotations

from computronium.core.joint.transition import (
    NullPlasticity,
    PlasticityConfig,
    PlasticityPrimitive,
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

__all__ = [  # ruff: ignore[unsorted-dunder-all]
    # Base
    "PlasticityConfig",
    "PlasticityPrimitive",
    "NullPlasticity",
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
    # Rule State (Z3)
    "RuleStatePlasticity",
    "RuleStatePlasticityConfig",
    "create_rule_state_plasticity",
]
