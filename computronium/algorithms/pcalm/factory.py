"""Public factory for PC-ALM systems."""

from __future__ import annotations

from typing import Any

from computronium.acceleration.dispatch import make_factory
from computronium.core.system_trainer import compose_joint_system
from computronium.ontology.credit import CreditAssignmentConfig, PCALMCredit
from computronium.ontology.dynamics import PCALMDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.plasticity import NullPlasticity
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig


def _build_pc_alm(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
) -> Any:
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


create_pc_alm_mlp = make_factory(
    _build_pc_alm,
    "algorithm.pcalm",
    extra_params=(),
)
