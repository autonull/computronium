"""Shared scaffolding for the reference implementations that anchor the ladder.

A reference implementation composes a small system and takes one deterministic
step with it. The composition — a digital substrate, a feedforward geometry, an
instantaneous dynamics, a Euclidean update — and the step's RNG discipline are
the same for every algorithm, so they are written once here. Each algorithm
contributes only the credit rule it is built on, or the geometry, dynamics, and
plasticity its own case implies.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

import torch

from computronium.core.system_trainer import compose_system
from computronium.ontology.dynamics import InstantaneousDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology.credit import CreditAssignment

__all__ = [
    "ReferenceSystemConfig",
    "make_reference_system",
    "reference_config",
    "run_reference_step",
]


@dataclass(frozen=True, slots=True)
class ReferenceSystemConfig:
    """The shape of the small system a reference step composes.

    Attributes:
        input_dim: Width of the input.
        output_dim: Width of the readout.
        hidden_dims: Widths of the hidden layers.
        lr: Step size of the Euclidean update.
        device: The device the substrate is configured for.
    """

    input_dim: int = 4
    output_dim: int = 4
    hidden_dims: tuple[int, ...] = ()
    lr: float = 1e-3
    device: str = "cpu"


def make_reference_system(
    config: ReferenceSystemConfig,
    credit: CreditAssignment,
) -> Any:
    """Compose the system a reference step runs on.

    Args:
        config: The shape of the system.
        credit: The credit rule the algorithm is built on.

    Returns:
        The composed system.
    """
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=config.input_dim,
            output_dim=config.output_dim,
            hidden_dims=config.hidden_dims,
        )
    )
    dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=config.lr))
    return compose_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        credit=credit,
        update=update,
    )


def reference_config(case: Any, **overrides: Any) -> ReferenceSystemConfig:
    """The standard reference system shape implied by ``case``.

    Args:
        case: The case the step is about to run on.
        **overrides: Fields to override on the standard shape.

    Returns:
        The config the reference system is composed from.
    """
    config = ReferenceSystemConfig(
        input_dim=case.state.shape[1],
        output_dim=case.config.get("output_dim", case.state.shape[1]),
        lr=case.config.get("lr", 1e-3),
        device=str(case.state.device),
    )
    if not overrides:
        return config
    return replace(config, **overrides)


def run_reference_step(
    case: Any,
    *,
    build: Callable[[Any], Any],
) -> Any:
    """Take one deterministic training step with a system built from ``case``.

    The system is composed inside the seeded RNG block, so a given seed always
    produces the same system and the same step.

    Args:
        case: The case the step runs on.
        build: Builds the system from the case.

    Returns:
        Whatever the system's ``train_step`` returns.
    """
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        system = build(case)
        result = system.train_step(case.state, case.target)
    finally:
        torch.set_rng_state(rng_state)
    return result
