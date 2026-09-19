"""Reference implementation for Temporal ψ Plasticity.

Delegates to computronium.core.plasticity.temporal_psi.TemporalPsiPlasticity
(the source of truth). This wrapper provides the uniform `step(case)` interface
for parity/microbench.
"""

from typing import Any

import torch

from computronium.core.plasticity.temporal_psi import (
    TemporalPsiConfig,
    TemporalPsiPlasticity,
)
from computronium.state import CompositeState


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to a CompositeState for TemporalPsiPlasticity."""
    state = CompositeState(
        activity={
            "h": case.pre_activity,
            "target": case.target,
            "y": case.post_activity,
        },
        plastic={},
        substrate={},
    )
    return state


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute reference plasticity step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Updated plastic state dict with gram, cross, readout_m, readout_b.
    """
    config = TemporalPsiConfig(
        trace_decay=case.config.get("trace_decay", 0.9),
        ridge_lambda=case.config.get("ridge_lambda", 1e-3),
        replace_readout=case.config.get("replace_readout", False),
    )
    plasticity = TemporalPsiPlasticity(config)

    psi = case.psi
    z = _case_to_composite_state(case)

    # Run step with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        new_psi = plasticity.step(psi, z, None)  # type: ignore[arg-type]
    finally:
        torch.set_rng_state(rng_state)

    return new_psi
