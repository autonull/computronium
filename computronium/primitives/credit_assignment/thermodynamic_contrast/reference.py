"""Reference implementation for Thermodynamic Contrast Credit.

Delegates to computronium.ontology.credit.ThermodynamicContrast (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    Phase,
    ThermodynamicContrast,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.system import SystemState


def _case_to_states(case: Any) -> dict[Phase, SystemState]:
    """Convert opaque case object to phase-keyed states for the credit protocol."""
    free_state = SystemState(
        activations=case.free_activations,
        x=case.free_activations[0],
        y=case.config.get("target"),
    )
    nudged_state = SystemState(
        activations=case.nudged_activations,
        x=case.nudged_activations[0],
        y=case.config.get("target"),
    )
    return {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }


def _case_to_geometry(case: Any) -> FeedforwardGeometry:
    """Create a minimal geometry from the case."""
    # Extract dimensions from case tensors
    weight_shapes = [w.shape for w in case.weights]
    dims = (weight_shapes[0][1], *[s[0] for s in weight_shapes])
    layers = []
    from torch import nn

    for i in range(len(weight_shapes)):
        layer = nn.Linear(dims[i], dims[i + 1], bias=False)
        layer.weight.data = case.weights[i].clone()
        layers.append(layer)

    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=dims[0],
            output_dim=dims[-1],
            hidden_dims=dims[1:-1],
        ),
        layers=layers,
    )
    return geometry


def step(case: Any) -> list[torch.Tensor]:
    """Execute reference credit assignment step.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        List of pseudo-gradient tensors (one per weight matrix).
    """
    config = CreditAssignmentConfig.thermodynamic_contrast(
        beta=case.config.get("beta", 0.5),
        credit_norm=case.config.get("credit_norm", "none"),
    )
    credit = ThermodynamicContrast(config)

    states = _case_to_states(case)
    geometry = _case_to_geometry(case)

    # Compute pseudo-gradients with deterministic RNG
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        grads = credit.compute_pseudo_gradient(states, None, geometry)
    finally:
        torch.set_rng_state(rng_state)

    return grads
