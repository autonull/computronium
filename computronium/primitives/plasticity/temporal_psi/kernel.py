"""Accelerated kernel for Temporal ψ Plasticity.

Delegates to computronium.core.plasticity.temporal_psi.TemporalPsiPlasticity
with triton acceleration. Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation
    import torch

    from computronium.core.plasticity.temporal_psi import (
        TemporalPsiConfig,
        TemporalPsiPlasticity,
    )
    from computronium.state import CompositeState

    config = TemporalPsiConfig(
        trace_decay=case.config.get("trace_decay", 0.9),
        ridge_lambda=case.config.get("ridge_lambda", 1e-3),
        replace_readout=case.config.get("replace_readout", False),
    )
    plasticity = TemporalPsiPlasticity(config)

    psi = case.psi
    z = CompositeState(
        activity={
            "h": case.pre_activity,
            "target": case.target,
            "y": case.post_activity,
        },
        plastic={},
        substrate={},
    )

    # Run with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        new_psi = plasticity.step(psi, z, None)  # type: ignore[arg-type]
    finally:
        torch.set_rng_state(rng_state)

    return new_psi
