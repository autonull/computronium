"""The deterministic geometry and pseudo-gradients a parameter-update step runs on.

A parameter update does not act on a model; it acts on a parameter set and a
gradient. The parameter set comes from a small geometry drawn from the case's
seed, and the gradient comes from a pseudo-gradient drawn the same way, so the
update is reproducible without training anything.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
    from computronium.harness._case import UpdateCase
    from computronium.ontology.geometry import FeedforwardGeometry

__all__ = ["update_geometry", "update_pseudo_grads"]


def update_geometry(case: UpdateCase) -> FeedforwardGeometry:
    """A deterministic minimal geometry built from the case.

    Args:
        case: The case the update acts on.

    Returns:
        A feedforward geometry whose weights are drawn from the case's seed.
    """
    from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig

    _, input_dim = case.state.shape
    _, output_dim = case.prediction.shape
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=(output_dim,),
        )
    )
    seed = case.config.get("seed", 0)
    generator = torch.Generator(device=case.state.device).manual_seed(seed + 3000)
    for param in geometry.params.values():
        param.data.normal_(generator=generator)
    return geometry


def update_pseudo_grads(
    case: UpdateCase,
    geometry: FeedforwardGeometry,
) -> list[torch.Tensor]:
    """Deterministic pseudo-gradients matching the geometry's parameter shapes.

    Args:
        case: The case the update acts on.
        geometry: The geometry whose parameters the update changes.

    Returns:
        One pseudo-gradient per geometry parameter, in parameter order.
    """
    seed = case.config.get("seed", 0)
    generator = torch.Generator(device=case.multiplier.device).manual_seed(seed + 2000)
    return [
        torch.randn_like(param, generator=generator)
        for param in geometry.params.values()
    ]
