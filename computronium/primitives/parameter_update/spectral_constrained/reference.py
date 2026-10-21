"""Reference implementation for Spectral Constrained.

Delegates to computronium.ontology.update.SpectralConstrainedUpdate (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from computronium.harness import update_geometry, update_pseudo_grads
from computronium.ontology.update import (
    ParameterUpdateConfig,
    SpectralConstrainedUpdate,
)

if TYPE_CHECKING:
    import torch


def step(case: Any) -> dict[str, torch.Tensor]:
    """
    Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Updated parameters (name -> tensor).
    """
    config = ParameterUpdateConfig.spectral_constrained(
        step_size=case.config.get("step_size", 0.01),
        spectral_norm=case.config.get("spectral_norm", 1.0),
        momentum=case.config.get("momentum", 0.9),
        ortho_steps=case.config.get("ortho_steps", 5),
    )
    update = SpectralConstrainedUpdate(config)

    geometry = update_geometry(case)
    pseudo_grad_list = update_pseudo_grads(case, geometry)
    params = dict(geometry.params)
    updated = update.step(params, pseudo_grad_list, geometry)

    return updated
