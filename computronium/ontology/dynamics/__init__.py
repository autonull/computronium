"""Layer 3: StateDynamics — Forward Evolution & Settling."""

from typing import TYPE_CHECKING, cast

from computronium.ontology.dynamics._dynamics import (
    DiffusionDynamics,
    EnergyMinimizationDynamics,
    ErrorPredictiveCodingDynamics,
    InstantaneousDynamics,
    LazyStateDynamics,
    PCALMDynamics,
    PredictiveSettlingDynamics,
    SpikeIntegrationDynamics,
    StateDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.dynamics._registry import (
    DYNAMICS_REGISTRY,
    _DYNAMICS_REGISTRY,
)
from computronium.ontology.dynamics._state import (
    SettableState,
    is_composite_state,
    is_system_state,
    set_state_field,
    state_dual_vars,
    state_energy,
)

if TYPE_CHECKING:
    from collections.abc import Callable


def dynamics_from_config(config: StateDynamicsConfig) -> StateDynamics:  # ruff: ignore[non-empty-init-module]
    """Instantiate the registered StateDynamics for a config's ``dynamics_type``."""
    return _DYNAMICS_REGISTRY.build(config.dynamics_type.lower(), config)


__all__ = [
    "DYNAMICS_REGISTRY",
    "DiffusionDynamics",
    "EnergyMinimizationDynamics",
    "ErrorPredictiveCodingDynamics",
    "InstantaneousDynamics",
    "LazyStateDynamics",
    "PCALMDynamics",
    "PredictiveSettlingDynamics",
    "SettableState",
    "SpikeIntegrationDynamics",
    "StateDynamics",
    "StateDynamicsConfig",
    "dynamics_from_config",
    "is_composite_state",
    "is_system_state",
    "set_state_field",
    "state_dual_vars",
    "state_energy",
]
