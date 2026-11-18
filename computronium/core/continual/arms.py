"""Continual learning arm factories (6-D Joint Systems)."""

from __future__ import annotations

import torch

from computronium.core.continual.buffers import ReplayBuffer
from computronium.core.continual.constants import CL_TOTAL_CLASSES
from computronium.core.continual.losses import LwFLoss, SynapticIntelligence
from computronium.core.continual.system import ContinualJointSystem
from computronium.core.joint.transition import NullPlasticity, PlasticityConfig
from computronium.core.plasticity import create_fast_weight_plasticity
from computronium.ontology import (
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    ElasticConsolidationUpdate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    PepitaCredit,
    StateDynamicsConfig,
    SubstrateConfig,
    ThermodynamicContrast,
)


def _get_compose_joint_system():
    """Lazy import to avoid circular dependency."""
    from computronium.core.system_trainer import compose_joint_system

    return compose_joint_system


def _mlp_stack(
    input_dim: int,
    hidden_dim: int,
    output_dim: int,
    device: str,
) -> tuple[DigitalSubstrate, FeedforwardGeometry]:
    """The shared substrate and geometry: every arm differs only in credit/update."""
    substrate = DigitalSubstrate(
        SubstrateConfig.digital(precision="float32", noise_level=0.0, device=device)
    )
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=(hidden_dim, hidden_dim),
            init_scale=0.1,
        )
    )
    return substrate, geometry


def _compose_credit_arm(
    credit,
    update,
    input_dim: int,
    hidden_dim: int,
    output_dim: int,
    device: str,
    classes_per_task: int = 2,
) -> ContinualJointSystem:
    """Compose one arm from the shared stack plus its credit and update."""
    substrate, geometry = _mlp_stack(input_dim, hidden_dim, output_dim, device)
    joint = _get_compose_joint_system()(
        substrate,
        geometry,
        InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        NullPlasticity(),
        credit,
        update,
    )
    return ContinualJointSystem.from_joint_system(joint, classes_per_task=classes_per_task).to(device)


def create_local_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    lr: float = 0.001,
    classes_per_task: int = 2,
) -> ContinualJointSystem:
    """PEPITA (local, two-pass) credit with a plain update."""
    return _compose_credit_arm(
        PepitaCredit(CreditAssignmentConfig.pepita()),
        EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=lr)),
        input_dim,
        hidden_dim,
        output_dim,
        device,
        classes_per_task=classes_per_task,
    )


def create_local_ewc_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    lr: float = 0.001,
    ewc_lambda: float = 1000.0,
    classes_per_task: int = 2,
) -> tuple[ContinualJointSystem, ElasticConsolidationUpdate]:
    """PEPITA credit composed with EWC consolidation (local × EWC)."""
    update = ElasticConsolidationUpdate(
        ParameterUpdateConfig.elastic_consolidation(
            step_size=lr, momentum=0.0, ewc_lambda=ewc_lambda
        )
    )
    model = _compose_credit_arm(
        PepitaCredit(CreditAssignmentConfig.pepita()),
        update,
        input_dim,
        hidden_dim,
        output_dim,
        device,
        classes_per_task=classes_per_task,
    )
    return model, update


def create_backprop_ewc_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    lr: float = 0.001,
    ewc_lambda: float = 1000.0,
    classes_per_task: int = 2,
) -> tuple[ContinualJointSystem, ElasticConsolidationUpdate]:
    """Exact-gradient credit composed with EWC: the strong retention baseline."""
    update = ElasticConsolidationUpdate(
        ParameterUpdateConfig.elastic_consolidation(
            step_size=lr, momentum=0.0, ewc_lambda=ewc_lambda
        )
    )
    model = _compose_credit_arm(
        BackpropCredit(CreditAssignmentConfig.gradient()),
        update,
        input_dim,
        hidden_dim,
        output_dim,
        device,
        classes_per_task=classes_per_task,
    )
    return model, update


def create_fast_weight_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,  # 10 classes
    device: str = "cpu",
    lr: float = 0.001,
    classes_per_task: int = 2,
) -> ContinualJointSystem:
    """Create FastWeightPlasticity arm (ψ/θ decoupling).

    Uses EnergyMinimizationDynamics with ThermodynamicContrast for proper
    free/nudged settling dynamics required by the contrastive credit assignment.
    """
    substrate, geometry = _mlp_stack(input_dim, hidden_dim, output_dim, device)

    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(max_steps=30, beta=0.5)
    )

    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
    )

    update = EuclideanUpdate(
        ParameterUpdateConfig.euclidean(step_size=lr, momentum=0.0)
    )

    plasticity = create_fast_weight_plasticity(
        PlasticityConfig.fast_weights(fast_weight_dim=512, decay=0.9, learning_rate=0.1)
    )

    joint = _get_compose_joint_system()(
        substrate, geometry, dynamics, plasticity, credit, update
    )
    return ContinualJointSystem.from_joint_system(joint, classes_per_task=classes_per_task).to(device)


def create_ewc_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    ewc_lambda: float = 1000.0,
    lr: float = 0.001,
    classes_per_task: int = 2,
) -> tuple[ContinualJointSystem, ElasticConsolidationUpdate]:
    """Create ElasticConsolidationUpdate (EWC) arm.

    Uses EnergyMinimizationDynamics with ThermodynamicContrast for proper
    free/nudged settling dynamics required by the contrastive credit assignment.
    """
    substrate, geometry = _mlp_stack(input_dim, hidden_dim, output_dim, device)

    dynamics = EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(max_steps=30, beta=0.5)
    )

    credit = ThermodynamicContrast(
        CreditAssignmentConfig.thermodynamic_contrast(beta=0.5)
    )

    update = ElasticConsolidationUpdate(
        ParameterUpdateConfig.elastic_consolidation(
            step_size=lr, momentum=0.0, ewc_lambda=ewc_lambda
        )
    )

    joint = _get_compose_joint_system()(
        substrate, geometry, dynamics, NullPlasticity(), credit, update
    )
    system = ContinualJointSystem.from_joint_system(joint, classes_per_task=classes_per_task).to(device)

    # Return the update object for consolidation at task boundaries
    return system, update


def _backprop_components(
    input_dim: int,
    hidden_dim: int,
    output_dim: int,
    device: str,
    lr: float = 0.001,
):
    """The matched reference stack; every continuous axis is held fixed."""
    substrate, geometry = _mlp_stack(input_dim, hidden_dim, output_dim, device)
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    credit = BackpropCredit(CreditAssignmentConfig.gradient())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=lr))
    return substrate, geometry, dynamics, credit, update


def create_backprop_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    lr: float = 0.001,
    classes_per_task: int = 2,
) -> ContinualJointSystem:
    """Create Backprop+SGD control arm."""
    substrate, geometry, dynamics, credit, update = _backprop_components(
        input_dim, hidden_dim, output_dim, device, lr
    )
    joint = _get_compose_joint_system()(
        substrate, geometry, dynamics, NullPlasticity(), credit, update
    )
    return ContinualJointSystem.from_joint_system(joint, classes_per_task=classes_per_task).to(device)


def create_plasticity_arm(
    plasticity: str,
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    classes_per_task: int = 2,
) -> ContinualJointSystem:
    """Create a Backprop arm whose only difference from the control is plasticity.

    ``plasticity`` is ``null`` or ``fast_weights``. The existing
    ``create_fast_weight_arm`` changes dynamics, credit and update as well, so
    it is a four-axis contrast; this factory isolates the plasticity axis.
    """
    substrate, geometry, dynamics, credit, update = _backprop_components(
        input_dim, hidden_dim, output_dim, device
    )
    match plasticity:
        case "null":
            psi = NullPlasticity()
        case "fast_weights":
            psi = create_fast_weight_plasticity(
                PlasticityConfig.fast_weights(
                    fast_weight_dim=512, decay=0.9, learning_rate=0.1
                )
            )
        case _:
            msg = f"unknown matched plasticity {plasticity!r}"
            raise ValueError(msg)
    joint = _get_compose_joint_system()(
        substrate, geometry, dynamics, psi, credit, update
    )
    return ContinualJointSystem.from_joint_system(joint, classes_per_task=classes_per_task).to(device)


def create_replay_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    buffer_capacity: int = 5000,
    lr: float = 0.001,
    classes_per_task: int = 2,
) -> tuple[ContinualJointSystem, ReplayBuffer]:
    """Create replay buffer arm (matched total memory)."""
    system = create_backprop_arm(input_dim, hidden_dim, output_dim, device, lr, classes_per_task=classes_per_task)
    # Fast weight plasticity has ~512 * 4 bytes * batch_size = ~2KB per sample
    # Match replay buffer capacity to equivalent memory
    buffer = ReplayBuffer(buffer_capacity, (input_dim,), torch.device(device))
    return system, buffer


def create_lwf_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    lr: float = 0.001,
    classes_per_task: int = 2,
) -> tuple[ContinualJointSystem, LwFLoss]:
    """Create LwF arm."""
    system = create_backprop_arm(input_dim, hidden_dim, output_dim, device, lr, classes_per_task=classes_per_task)
    lwf_loss = LwFLoss(temperature=2.0, lambda_lwf=1.0)
    return system, lwf_loss


def create_si_arm(
    input_dim: int = 784,
    hidden_dim: int = 256,
    output_dim: int = CL_TOTAL_CLASSES,
    device: str = "cpu",
    lr: float = 0.001,
    xi: float = 0.1,
    classes_per_task: int = 2,
) -> tuple[ContinualJointSystem, SynapticIntelligence]:
    """Create Synaptic Intelligence arm."""
    system = create_backprop_arm(input_dim, hidden_dim, output_dim, device, lr, classes_per_task=classes_per_task)
    si = SynapticIntelligence(system, xi=xi)
    return system, si


__all__ = [
    "create_backprop_arm",
    "create_backprop_ewc_arm",
    "create_ewc_arm",
    "create_fast_weight_arm",
    "create_local_arm",
    "create_local_ewc_arm",
    "create_lwf_arm",
    "create_replay_arm",
    "create_si_arm",
]
