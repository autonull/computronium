"""Reference implementation for Natural Gradient.

Delegates to computronium.ontology.update.NaturalGradientUpdate (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from computronium.harness import update_geometry, update_pseudo_grads
from computronium.ontology.update import (
    NaturalGradientUpdate,
    ParameterUpdateConfig,
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
