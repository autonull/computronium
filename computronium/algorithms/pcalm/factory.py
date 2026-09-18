"""Public factory for PC-ALM systems.

Wraps computronium.core.system_trainer.compose_joint_system, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.system_trainer import compose_joint_system
from computronium.ontology.credit import CreditAssignmentConfig, PCALMCredit
from computronium.ontology.dynamics import PCALMDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.plasticity import NullPlasticity
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


def create_pc_alm_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
) -> Any:
    """
    Create a PC-ALM MLP system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.pcalm")
    backend = select_backend(spec, backend)

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=input_dim, output_dim=output_dim, hidden_dims=hidden_dims
        )
    )
    dynamics = PCALMDynamics(
        StateDynamicsConfig.pc_alm(
            max_steps=30,
            step_size=0.1,
            rho=1.0,
            beta=0.5,
            prospective_leak=0.0,
        )
    )
    plasticity = NullPlasticity()
    credit = PCALMCredit(CreditAssignmentConfig.pc_alm())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=lr))

    return compose_joint_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        plasticity=plasticity,
        credit=credit,
        update=update,
    )
