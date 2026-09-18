"""Reference implementation for Local Goodness Credit Assignment.

Delegates to computronium.ontology.credit.LocalGoodnessCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch
from torch import nn

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    LocalGoodnessCredit,
    Phase,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.system import SystemState


def step(case: Any) -> list[torch.Tensor]:
    """Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        List of pseudo-gradient tensors (one per weight matrix).
    """
    config = CreditAssignmentConfig.local_goodness(
        local_objective=case.config.get("local_objective", "ff"),
        feedback_scale=case.config.get("feedback_scale", 1.0),
        orthogonal_init=case.config.get("orthogonal_init", True),
        readout_error=case.config.get("readout_error", False),
        credit_norm=case.config.get("credit_norm", "rms"),
        learned_feedback=case.config.get("learned_feedback", False),
        feedback_lr=case.config.get("feedback_lr", 0.01),
        feedback_update_every=case.config.get("feedback_update_every", 10),
    )
    credit = LocalGoodnessCredit(config)

    # Convert case to SystemState objects for free and nudged phases
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

    # Build a geometry with the case's weights
    weight_shapes = [w.shape for w in case.weights]
    dims = (weight_shapes[0][1], *[s[0] for s in weight_shapes])
    layers = nn.ModuleList()
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

    states = {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }

    # Compute pseudo-gradient
    grads = credit.compute_pseudo_gradient(states, None, geometry)
    return grads
