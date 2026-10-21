"""Reference implementation for Spiking SNN algorithm.

Composes Spiking SNN training step with SpikeIntegrationDynamics and TemporalTraceCredit.
"""

from typing import Any

from computronium.harness import (
    make_reference_system,
    reference_config,
    run_reference_step,
)
from computronium.ontology.credit import CreditAssignmentConfig, TemporalTraceCredit
from computronium.ontology.dynamics import SpikeIntegrationDynamics, StateDynamicsConfig


def build_system(case: Any) -> Any:
    """Create the system the reference step runs on."""
    dynamics = SpikeIntegrationDynamics(
        StateDynamicsConfig.spike_integration(
            max_steps=case.config.get("max_steps", 30),
            beta=case.config.get("beta", 0.1),
            threshold=case.config.get("threshold", 0.5),
        )
    )
    credit = TemporalTraceCredit(
        CreditAssignmentConfig.temporal_trace(
            tau_pre=0.9,
            tau_post=0.9,
        )
    )
    return make_reference_system(
        reference_config(case),
        credit,
        dynamics=dynamics,
    )


def step(case: Any) -> Any:
    """Execute one reference training step using the opaque case object."""
    return run_reference_step(case, build=build_system)
