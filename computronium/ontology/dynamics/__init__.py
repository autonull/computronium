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
from computronium.ontology.dynamics._registry import DYNAMICS_REGISTRY
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


def dynamics_from_config(config: StateDynamicsConfig) -> StateDynamics:
    """Instantiate the registered StateDynamics for a config's ``dynamics_type``."""
    cls = DYNAMICS_REGISTRY.get(config.dynamics_type.lower())
    if cls is None:
        raise ValueError(f"Unknown dynamics_type: {config.dynamics_type!r}")
    # The registry stores concrete implementations behind the runtime-checkable
    # Protocol; their common constructor shape is (config).
    factory = cast("Callable[[StateDynamicsConfig], StateDynamics]", cls)
    return factory(config)


__all__ = [
    "DYNAMICS_REGISTRY",
    "DiffusionDynamics",
    "EnergyMinimizationDynamics",
    "ErrorPredictiveCodingDynamics",
    "InstantaneousDynamics",
    "LazyStateDynamics",
    "PCALMDynamics",
    "PredictiveSettlingDynamics",
    "SpikeIntegrationDynamics",
    "StateDynamics",
    "SettableState",
    "StateDynamicsConfig",
    "dynamics_from_config",
    "is_composite_state",
    "is_system_state",
    "set_state_field",
    "state_dual_vars",
    "state_energy",
]
