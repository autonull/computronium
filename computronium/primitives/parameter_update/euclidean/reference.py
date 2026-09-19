"""Reference implementation for Euclidean Update (SGD with momentum).

Delegates to computronium.ontology.update.EuclideanUpdate (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.update import (
    EuclideanUpdate,
    ParameterUpdateConfig,
)


def _case_to_geometry(case: Any) -> FeedforwardGeometry:
    """Create a deterministic minimal geometry from the case."""
    _, input_dim = case.state.shape
    _, output_dim = case.prediction.shape

    config = GeometryConfig.feedforward(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dims=(output_dim,),
    )
    geometry = FeedforwardGeometry(config)

    # Make weights deterministic based on case seed
    seed = case.config.get("seed", 0)
    generator = torch.Generator(device=case.state.device).manual_seed(seed + 3000)
    for param in geometry.params.values():
        param.data.normal_(generator=generator)

    return geometry


def _make_pseudo_grads(case: Any, geometry: FeedforwardGeometry) -> list[torch.Tensor]:
    """Create deterministic pseudo-gradients matching parameter shapes from case multiplier."""
    pseudo_grads = []
    seed = case.config.get("seed", 0)
    generator = torch.Generator(device=case.multiplier.device).manual_seed(seed + 2000)
    for name, param in geometry.params.items():
        pg = torch.randn_like(param, generator=generator)
        pseudo_grads.append(pg)
    return pseudo_grads


def step(case: Any) -> dict[str, torch.Tensor]:
    """
    Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Updated parameters (name -> tensor).
    """
    config = ParameterUpdateConfig.euclidean(
        step_size=case.config.get("step_size", 0.01),
        momentum=case.config.get("momentum", 0.9),
        grad_clip=case.config.get("grad_clip", None),
    )
    update = EuclideanUpdate(config)

    geometry = _case_to_geometry(case)
    pseudo_grad_list = _make_pseudo_grads(case, geometry)
    params = dict(geometry.params)
    updated = update.step(params, pseudo_grad_list, geometry)

    return updated
