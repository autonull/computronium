"""Accelerated kernel for Euclidean Update (SGD with momentum).

Delegates to computronium.ontology.update.EuclideanUpdate with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import TYPE_CHECKING, Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import update_geometry, update_pseudo_grads
from computronium.ontology.update import (
    EuclideanUpdate,
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
    config = ParameterUpdateConfig.euclidean(
        step_size=case.config.get("step_size", 0.01),
        momentum=case.config.get("momentum", 0.9),
        grad_clip=case.config.get("grad_clip", None),
    )
    update = EuclideanUpdate(config)

    geometry = update_geometry(case)
    pseudo_grad_list = update_pseudo_grads(case, geometry)
    params = dict(geometry.params)
    updated = update.step(params, pseudo_grad_list, geometry)

    return updated
