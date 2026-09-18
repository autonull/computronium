"""Accelerated kernel for PC-ALM settling.

Delegates to computronium.acceleration.pcalm_kernels.fused_dual_primal_update
and _compiled_pcalm_settle. Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.acceleration.pcalm_kernels import (
    HAS_TRITON_PCALM,
)

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY) and HAS_TRITON_PCALM


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use compiled settle loop
    import torch

    from computronium.ontology.dynamics import StateDynamicsConfig
    from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
    from computronium.state import CompositeState

    config = StateDynamicsConfig.pc_alm(
        max_steps=case.config["steps"],
        step_size=case.config.get("step_size", 0.1),
        rho=case.config.get("rho", 1.0),
        beta=case.config.get("beta", 0.5),
        prospective_leak=case.config.get("prospective_leak", 0.0),
        convergence_threshold=case.config.get("tol", 1e-4),
        compiled=True,
    )

    # Convert case to CompositeState
    state = CompositeState(activity={"x": case.state}, plastic={}, substrate={})
    state.metrics = {
        "prediction": case.prediction,
        "multiplier": case.multiplier,
    }

    # Use geometry from case (pre-initialized for determinism)
    geometry = case.geometry
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=case.state.device))

    target = case.config.get("target")
    if target is not None:
        target = torch.as_tensor(target, device=case.state.device)

    # PCALMDynamics with compiled=True will use _compiled_pcalm_settle
    from computronium.ontology.dynamics import PCALMDynamics

    dynamics = PCALMDynamics(config)

    # Run settle with deterministic RNG state
    # Save RNG state AFTER geometry/substrate creation (which may use RNG for init)
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        result = dynamics.settle(state, geometry, substrate, target)
    finally:
        torch.set_rng_state(rng_state)
    return result
