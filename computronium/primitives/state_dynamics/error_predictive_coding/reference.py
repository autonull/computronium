"""Reference implementation for Error Predictive Coding.

Delegates to computronium.ontology.dynamics.ErrorPredictiveCodingDynamics
(the source of truth). This wrapper provides the uniform `step(case)`
interface for parity/microbench.
"""

from typing import Any

from computronium.harness import seeded_rng
from computronium.ontology.dynamics import (
    ErrorPredictiveCodingDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.state import CompositeState


def _case_to_composite_state(case: Any) -> CompositeState:
    """Convert a test case to the CompositeState the dynamics settle."""
    state = CompositeState(activity={"x": case.state}, plastic={}, substrate={})
    state.metrics = {
        "prediction": case.prediction,
        "multiplier": case.multiplier,
    }
    return state


def step(case: Any) -> Any:
    """Execute one reference step using the opaque case object."""
    steps = case.config["steps"]
    config = StateDynamicsConfig.error_predictive_coding(
        max_steps=steps,
        step_size=case.config.get("step_size", 0.1),
        beta=case.config.get("beta", 0.5),
        convergence_threshold=0.0,
        convergence_start=steps + 1,
    )
    dynamics = ErrorPredictiveCodingDynamics(config)
    state = _case_to_composite_state(case)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=case.state.device))

    with seeded_rng(case.config.get("seed", 0)):
        return dynamics.settle(state, case.geometry, substrate, None)
