"""Accelerated kernel for Lazy State Dynamics.

Delegates to computronium.ontology.dynamics.LazyStateDynamics with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import seeded_rng

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

    from computronium.ontology.dynamics import LazyStateDynamics, StateDynamicsConfig
    from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
    from computronium.state import CompositeState

    config = StateDynamicsConfig.lazy(
        max_steps=case.config["steps"],
        step_size=case.config.get("step_size", 0.1),
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

    # Run with deterministic RNG state
    with seeded_rng(case.config.get("seed", 0)):
        dynamics = LazyStateDynamics(config)
        result = dynamics.settle(state, geometry, substrate, target)
    return result
