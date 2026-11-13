"""Reference implementation for Conflict-Adaptive Plasticity.

Delegates to computronium.core.plasticity.adaptive_psi
.ConflictAdaptivePsiPlasticity (the source of truth).
"""

from typing import TYPE_CHECKING, Any

from computronium.core.plasticity.adaptive_psi import (
    ConflictAdaptivePsiConfig,
    ConflictAdaptivePsiPlasticity,
)
from computronium.harness import seeded_rng
from computronium.state import CompositeState

if TYPE_CHECKING:
    import torch


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to the CompositeState the law reads."""
    return CompositeState(
        activity={
            "h": case.pre_activity,
            "target": case.target,
            "y": case.post_activity,
        },
        plastic={},
        substrate={},
    )


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute one reference plasticity step using the opaque case object."""
    config = ConflictAdaptivePsiConfig(
        conflict_threshold=case.config.get("conflict_threshold", 0.65),
        forget_decay=case.config.get("forget_decay", 0.5),
        ridge_lambda=case.config.get("ridge_lambda", 1e-3),
        replace_readout=case.config.get("replace_readout", True),
    )
    plasticity = ConflictAdaptivePsiPlasticity(config)
    activity = _case_to_composite_state(case)

    with seeded_rng(case.config.get("seed", 0)):
        new_psi = plasticity.step(case.psi, activity, None)  # type: ignore[arg-type]

    return new_psi
