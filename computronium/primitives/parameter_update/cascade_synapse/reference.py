"""Reference implementation for the Benna-Fusi cascade rule.

Delegates to :class:`CascadeSynapsePlasticity` (the source of truth), so the uniform
``step(case)`` interface stays available on every backend.
"""

from typing import Any

import torch

from computronium.ontology._utils import _learnable_weight_names
from computronium.ontology.update import CascadeSynapsePlasticity, ParameterUpdateConfig


def _config(config: dict[str, Any]) -> ParameterUpdateConfig:
    return ParameterUpdateConfig.cascade_synapse()


def step(case: Any) -> dict[str, torch.Tensor]:
    update = CascadeSynapsePlasticity(_config(case.config))
    params = dict(case.geometry.params)
    generator = torch.Generator(device=case.geometry.params[
        _learnable_weight_names(params)[0]
    ].device).manual_seed(case.config.get("seed", 0))
    grads = [
        torch.randn_like(param, generator=generator)
        for param in params.values()
        if param.ndim == 2
    ]
    return update.step(params, grads, case.geometry)
