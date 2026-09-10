"""Serialization/deserialization utilities for System and JointSystem."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.ontology import (
    BackpropCredit,
    CreditAssignmentConfig,
    DiffusionDynamics,
    EnergyMinimizationDynamics,
    GeometryConfig,
    HomeostaticCredit,
    InstantaneousDynamics,
    LocalGoodnessCredit,
    ParameterUpdateConfig,
    PepitaCredit,
    PredictiveSettlingDynamics,
    RandomProjectionsCredit,
    SpikeIntegrationDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    TargetInversionCredit,
    TemporalTraceCredit,
    ThermodynamicContrast,
    geometry_from_config,
    substrate_from_config,
    update_from_config,
)

if TYPE_CHECKING:
    from computronium.core.joint.transition import PlasticityConfig, PlasticityPrimitive
    from computronium.core.system_trainer.protocol import JointSystem
    from computronium.ontology import (
        CreditAssignment,
        Geometry,
        ParameterUpdate,
        StateDynamics,
        Substrate,
        System,
    )


def extract_config(system: System) -> dict[str, object]:
    """Extract configuration from a composed System.

    Returns a dictionary mapping layer names to their configuration objects.
    This enables round-trip: System -> configs -> System.

    Args:
        system: A composed System instance.

    Returns:
        Dictionary with keys: substrate, geometry, dynamics, credit, update.
    """
    return {
        "substrate": system.substrate.config,
        "geometry": system.geometry.config,
        "dynamics": system.dynamics.config,
        "credit": system.credit.config,
        "update": system.update.config,
    }


def _geometry_from_config(geometry: GeometryConfig) -> Geometry:
    """Instantiate geometry from config (single dispatcher in ontology)."""
    return geometry_from_config(geometry)


def _dynamics_from_config(dynamics: StateDynamicsConfig) -> StateDynamics:
    """Instantiate dynamics from config."""
    dynamics_type = dynamics.dynamics_type.lower()
    if dynamics_type == "energy_minimization":
        return EnergyMinimizationDynamics(dynamics)
    elif dynamics_type == "predictive_settling":
        return PredictiveSettlingDynamics(dynamics)
    elif dynamics_type == "spike_integration":
        return SpikeIntegrationDynamics(dynamics)
    elif dynamics_type == "diffusion":
        return DiffusionDynamics(dynamics)
    elif dynamics_type == "instantaneous":
        return InstantaneousDynamics(dynamics)
    else:
        raise ValueError(f"Unknown dynamics_type: {dynamics_type!r}")


def _credit_from_config(config: CreditAssignmentConfig):  # ruff: ignore[too-many-return-statements]
    """Instantiate the credit implementation named by ``config.credit_type``."""
    match config.credit_type.lower():
        case "thermodynamic_contrast" | "equilibrium":
            return ThermodynamicContrast(config)
        case (
            "random_projections" | "feedback_alignment" | ("direct_feedback_alignment")
        ):
            return RandomProjectionsCredit(config)
        case "local_goodness" | "forward_only":
            return LocalGoodnessCredit(config)
        case "pepita":
            return PepitaCredit(config)
        case "temporal_trace" | "spiking":
            return TemporalTraceCredit(config)
        case "target_inversion" | "target_prop":
            return TargetInversionCredit(config)
        case "homeostatic":
            return HomeostaticCredit(config)
        case "gradient" | "backprop":
            return BackpropCredit(config)
        case other:
            raise ValueError(f"Unknown credit_type: {other!r}")


def _update_from_config(update: ParameterUpdateConfig):
    """Instantiate update from config (canonical dispatch in ontology.update)."""
    return update_from_config(update)


def _plasticity_from_config(plasticity: PlasticityConfig):
    """Instantiate plasticity from config."""
    from computronium.core.plasticity import (
        NullPlasticity,
        conflict_adaptive_from_config,
        create_fast_weight_plasticity,
        create_routing_plasticity,
        create_rule_state_plasticity,
        create_substrate_coupled_plasticity,
        temporal_psi_from_config,
    )

    factories = {
        "routing": create_routing_plasticity,
        "fast_weights": create_fast_weight_plasticity,
        "substrate_coupled": create_substrate_coupled_plasticity,
        "rule_state": create_rule_state_plasticity,
        "temporal_psi": temporal_psi_from_config,
        "conflict_adaptive": conflict_adaptive_from_config,
    }
    plasticity_type = plasticity.plasticity_type.lower()
    factory = factories.get(plasticity_type)
    if factory is not None:
        return factory(plasticity)
    if plasticity_type == "null":
        return NullPlasticity()
    raise ValueError(f"Unknown plasticity_type: {plasticity_type!r}")


def compose_system_from_configs(
    substrate: SubstrateConfig,
    geometry: GeometryConfig,
    dynamics: StateDynamicsConfig,
    credit: CreditAssignmentConfig,
    update: ParameterUpdateConfig,
) -> System:
    """Compose a System from five configuration objects.

    This is the inverse of extract_config(), enabling the round-trip:
    System --extract_config--> configs --compose_system_from_configs--> System

    Args:
        substrate: Substrate configuration
        geometry: Geometry configuration
        dynamics: StateDynamics configuration
        credit: CreditAssignment configuration
        update: ParameterUpdate configuration

    Returns:
        A composed System with default implementations for each layer.
    """
    # Instantiate substrate from config (class named by the explicit type tag)
    substrate_instance = substrate_from_config(substrate)

    # Instantiate geometry from config
    geometry_instance = _geometry_from_config(geometry)

    # Instantiate dynamics from config
    dynamics_instance = _dynamics_from_config(dynamics)

    # Instantiate credit from config
    credit_instance = _credit_from_config(credit)

    # Instantiate update from config
    update_instance = _update_from_config(update)

    from computronium.core.system_trainer.factory import compose_system

    return compose_system(
        substrate_instance,
        geometry_instance,
        dynamics_instance,
        credit_instance,
        update_instance,
    )


def compose_joint_system_from_configs(
    substrate: SubstrateConfig,
    geometry: GeometryConfig,
    dynamics: StateDynamicsConfig,
    plasticity: PlasticityConfig,
    credit: CreditAssignmentConfig,
    update: ParameterUpdateConfig,
) -> JointSystem[
    Substrate,
    Geometry,
    StateDynamics,
    PlasticityPrimitive,
    CreditAssignment,
    ParameterUpdate,
]:
    """Compose a JointSystem from six configuration objects.

    This is the inverse of extract_config(), enabling the round-trip:
    JointSystem --extract_config--> configs --compose_joint_system_from_configs--> JointSystem

    Args:
        substrate: Substrate configuration
        geometry: Geometry configuration
        dynamics: StateDynamics configuration
        plasticity: Plasticity configuration
        credit: CreditAssignment configuration
        update: ParameterUpdate configuration

    Returns:
        A composed JointSystem with default implementations for each layer.
    """
    # Instantiate substrate from config (class named by the explicit type tag)
    substrate_instance = substrate_from_config(substrate)

    # Instantiate geometry from config
    geometry_instance = _geometry_from_config(geometry)

    # Instantiate dynamics from config
    dynamics_instance = _dynamics_from_config(dynamics)

    # Instantiate credit from config
    credit_instance = _credit_from_config(credit)

    # Instantiate update from config
    update_instance = _update_from_config(update)

    # Instantiate plasticity from config
    plasticity_instance = _plasticity_from_config(plasticity)

    from computronium.core.system_trainer.joint import compose_joint_system

    return compose_joint_system(
        substrate_instance,
        geometry_instance,
        dynamics_instance,
        plasticity_instance,
        credit_instance,
        update_instance,
    )


__all__ = [
    "compose_joint_system_from_configs",
    "compose_system_from_configs",
    "extract_config",
]
