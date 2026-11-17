"""Reference implementation for the local-supervision estimator.

Delegates to :class:`LocalSupervisionCredit` (the source of truth), so the uniform
``step(case)`` interface stays available on every backend.
"""

from typing import Any

from computronium.core.losses import cross_entropy
from computronium.ontology.credit import (
    CreditAssignmentConfig,
    LocalSupervisionCredit,
    Phase,
)
from computronium.primitives._common import make_reference_step_with_loss
from computronium.state import CompositeState


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.local_supervision()


def _states(case: Any) -> dict[Any, Any]:
    free = CompositeState(
        activity={
            "x": case.state,
            "y": case.config["target"],
            "activations": case.activations,
        },
        plastic={},
        substrate={},
    )
    return {Phase.FREE: free}


step = make_reference_step_with_loss(
    LocalSupervisionCredit,
    _config_factory,
    case_to_states_fn=_states,
    loss_fn=lambda case: cross_entropy(case.activations[-1], case.config["target"]),
)
