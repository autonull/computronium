"""Accelerated kernel for Natural Gradient.

Delegates to computronium.ontology.update.NaturalGradientUpdate with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import TYPE_CHECKING, Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import update_geometry, update_pseudo_grads
from computronium.ontology.update import (
    NaturalGradientUpdate,
    ParameterUpdateConfig,
)

if TYPE_CHECKING:
    import torch

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> dict[str, torch.Tensor]:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation (fallback to reference for now)
    config = ParameterUpdateConfig.natural_gradient(
        step_size=case.config.get("step_size", 1e-3),
        momentum=case.config.get("momentum", 0.9),
        fisher_damping=case.config.get("fisher_damping", 1e-3),
        beta2=case.config.get("beta2", 0.999),
        eps=case.config.get("eps", 1e-8),
        grad_clip=case.config.get("grad_clip", 1.0),
    )
    update = NaturalGradientUpdate(config)

    geometry = update_geometry(case)
    pseudo_grad_list = update_pseudo_grads(case, geometry)
    params = dict(geometry.params)
    updated = update.step(params, pseudo_grad_list, geometry)

    return updated
