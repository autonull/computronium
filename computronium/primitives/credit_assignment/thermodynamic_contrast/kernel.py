"""Accelerated kernel for Thermodynamic Contrast Credit.

Delegates to computronium.ontology.credit.ThermodynamicContrast with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> list[torch.Tensor]:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation (fallback to reference for now)
    import torch

    from computronium.ontology.credit import (
        CreditAssignmentConfig,
        Phase,
        ThermodynamicContrast,
    )
    from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
    from computronium.ontology.system import SystemState

    config = CreditAssignmentConfig.thermodynamic_contrast(
        beta=case.config.get("beta", 0.5),
        credit_norm=case.config.get("credit_norm", "none"),
    )
    credit = ThermodynamicContrast(config)

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
    states = {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }

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

    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        grads = credit.compute_pseudo_gradient(states, None, geometry)
    finally:
        torch.set_rng_state(rng_state)

    return grads
