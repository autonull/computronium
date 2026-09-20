"""Reference implementation for Lazy State Dynamics.

Delegates to computronium.ontology.dynamics.LazyStateDynamics (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.ontology.dynamics import LazyStateDynamics, StateDynamicsConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.state import CompositeState


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to a CompositeState for LazyStateDynamics."""
    # LazyStateDynamics expects a CompositeState with x (input) and layer activations
    state = CompositeState(activity={"x": case.state}, plastic={}, substrate={})
    # Store additional data in metrics for the dynamics to use
    state.metrics = {
        "prediction": case.prediction,
        "multiplier": case.multiplier,
    }
    return state


def step(case: Any) -> Any:
    """Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.
    """
    config = StateDynamicsConfig.lazy(
        max_steps=case.config["steps"],
        step_size=case.config.get("step_size", 0.1),
    )
    dynamics = LazyStateDynamics(config)

    # Convert case to CompositeState
    state = _case_to_composite_state(case)

    # Use geometry from case (pre-initialized for determinism)
    geometry = case.geometry
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=case.state.device))

    # Get target for nudged phase
    target = case.config.get("target")
    if target is not None:
        target = torch.as_tensor(target, device=case.state.device)

    # Run settle with deterministic RNG state
    # Save RNG state AFTER geometry/substrate creation (which may use RNG for init)
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        result = dynamics.settle(state, geometry, substrate, target)
    finally:
        torch.set_rng_state(rng_state)
    return result
