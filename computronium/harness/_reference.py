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

from computronium.core.system_trainer import compose_system
from computronium.ontology.dynamics import InstantaneousDynamics, StateDynamicsConfig
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.update import EuclideanUpdate, ParameterUpdateConfig

from ._case import seeded_rng

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology.credit import CreditAssignment
    from computronium.ontology.dynamics import StateDynamics
    from computronium.ontology.geometry import Geometry
    from computronium.ontology.plasticity import PlasticityPrimitive

__all__ = [
    "ReferenceSystemConfig",
    "make_joint_reference_system",
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


def _standard_parts(
    config: ReferenceSystemConfig,
    credit: CreditAssignment,
    geometry: Geometry | None,
    dynamics: StateDynamics | None,
) -> tuple[Any, Geometry, StateDynamics, CreditAssignment, Any]:
    """The five axes every reference system shares, with the two defaults filled in.

    The substrate and the Euclidean update are the same everywhere; the geometry
    and the dynamics are the same unless the algorithm brings its own.
    """
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=config.device))
    if geometry is None:
        geometry = FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=config.input_dim,
                output_dim=config.output_dim,
                hidden_dims=config.hidden_dims,
            )
        )
    if dynamics is None:
        dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=config.lr))
    return substrate, geometry, dynamics, credit, update


def make_reference_system(
    config: ReferenceSystemConfig,
    credit: CreditAssignment,
    *,
    geometry: Geometry | None = None,
    dynamics: StateDynamics | None = None,
) -> Any:
    """Compose the system a reference step runs on.

    Args:
        config: The shape of the system.
        credit: The credit rule the algorithm is built on.
        geometry: The geometry, or ``None`` for the standard feedforward one.
        dynamics: The dynamics, or ``None`` for the standard instantaneous ones.

    Returns:
        The composed system.
    """
    return compose_system(*_standard_parts(config, credit, geometry, dynamics))


def make_joint_reference_system(
    config: ReferenceSystemConfig,
    credit: CreditAssignment,
    plasticity: PlasticityPrimitive,
    *,
    geometry: Geometry | None = None,
    dynamics: StateDynamics | None = None,
) -> Any:
    """Compose the joint system a reference step runs on.

    The joint composition is the five-axis one with the plasticity primitive
    added, which is what the fast-weight, PC-ALM, and routing algorithms need.

    Args:
        config: The shape of the system.
        credit: The credit rule the algorithm is built on.
        plasticity: The plasticity primitive the algorithm is built on.
        geometry: The geometry, or ``None`` for the standard feedforward one.
        dynamics: The dynamics, or ``None`` for the standard instantaneous ones.

    Returns:
        The composed joint system.
    """
    from computronium.core.system_trainer import compose_joint_system

    substrate, geometry, dynamics, credit, update = _standard_parts(
        config, credit, geometry, dynamics
    )
    return compose_joint_system(
        substrate=substrate,
        geometry=geometry,
        dynamics=dynamics,
        plasticity=plasticity,
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
    with seeded_rng(case.config.get("seed", 0)):
        system = build(case)
        result = system.train_step(case.state, case.target)
    return result
