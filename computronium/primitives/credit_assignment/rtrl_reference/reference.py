"""Reference implementation for the exact RTRL reference.

Delegates to :class:`RTRLReference` (the source of truth), so the uniform
``step(case)`` interface stays available on every backend.
"""

from typing import Any

import torch

from computronium.ontology.credit import CreditAssignmentConfig, Phase, RTRLReference
from computronium.primitives._common import make_reference_step_with_loss
from computronium.state import CompositeState


def _config_factory(config: dict[str, Any]) -> CreditAssignmentConfig:
    return CreditAssignmentConfig.rtrl_reference()


def _states(case: Any) -> dict[Any, Any]:
    free = CompositeState(
        activity={"x": case.x, "y": case.y},
        plastic={},
        substrate={},
    )
    return {Phase.FREE: free}


step = make_reference_step_with_loss(
    RTRLReference,
    _config_factory,
    case_to_states_fn=_states,
    loss_fn=lambda case: torch.zeros((), device=case.x.device),
)
