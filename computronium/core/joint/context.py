"""The SystemContext a joint system's components describe.

A joint system is six components; the transition reads them through a
``SystemContext``. The context is not a bag of parts: it also names the
persistent parameters (θ) and the plastic variables (ψ) in a registry, and
that naming is the lifecycle contract the consolidation pass relies on. So
the context is built in one place, from the components, rather than twice.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.core.joint.transition import PlasticityConfig
from computronium.state import StateRegistry, StateVariable, SystemContext

if TYPE_CHECKING:
    from computronium.ontology.credit import CreditAssignment
    from computronium.ontology.dynamics import StateDynamics
    from computronium.ontology.geometry import Geometry
    from computronium.ontology.substrate import Substrate
    from computronium.ontology.update import ParameterUpdate
    from computronium.state.transitions import PlasticityPrimitive

__all__ = ["build_system_context"]


def build_system_context(
    *,
    geometry: Geometry,
    substrate: Substrate,
    dynamics: StateDynamics,
    credit: CreditAssignment,
    update: ParameterUpdate,
    plasticity: PlasticityPrimitive | None = None,
) -> SystemContext:
    """Build the context bound to a joint system's θ and component configs.

    Args:
        geometry: The system's geometry; its parameters are θ.
        substrate: The system's substrate.
        dynamics: The system's state dynamics.
        credit: The system's credit assignment.
        update: The system's parameter update.
        plasticity: The system's plasticity, if it has one.

    Returns:
        The context, with a registry naming θ and the plastic variables.
    """
    registry = StateRegistry()
    for name in geometry.params:
        registry.register(
            StateVariable(
                name=name,
                persistent=True,
                fast_plastic=False,
                consolidatable=False,
            )
        )

    plastic_config = getattr(plasticity, "config", None)
    if plastic_config is not None:
        for name in getattr(plastic_config, "plastic_state_dims", None) or ():
            registry.register(
                StateVariable(
                    name=name,
                    persistent=False,
                    fast_plastic=True,
                    consolidatable=True,
                )
            )

    return SystemContext(
        theta=geometry.params,
        geometry=geometry,
        substrate=substrate,
        substrate_config=substrate.config,
        geometry_config=geometry.config,
        dynamics_config=dynamics.config,
        credit_config=credit.config,
        update_config=update.config,
        plasticity_config=getattr(plasticity, "config", PlasticityConfig.null()),
        registry=registry,
    )
