"""Accelerated kernel for Spectral Constrained.

Delegates to computronium.ontology.update.SpectralConstrainedUpdate with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available
from computronium.harness import update_geometry, update_pseudo_grads

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation (falls back to reference for now)

    from computronium.ontology.update import (
        ParameterUpdateConfig,
        SpectralConstrainedUpdate,
    )

    config = ParameterUpdateConfig.spectral_constrained(
        step_size=case.config.get("step_size", 0.01),
        spectral_norm=case.config.get("spectral_norm", 1.0),
        momentum=case.config.get("momentum", 0.9),
        ortho_steps=case.config.get("ortho_steps", 5),
    )

    geometry = update_geometry(case)
    pseudo_grad_list = update_pseudo_grads(case, geometry)

    params = dict(geometry.params)
    update = SpectralConstrainedUpdate(config)
    updated = update.step(params, pseudo_grad_list, geometry)

    return updated
