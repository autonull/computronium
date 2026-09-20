"""Accelerated kernel for Elastic Consolidation Update.

Delegates to computronium.ontology.update.ElasticConsolidationUpdate with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation
    import torch

    from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
    from computronium.ontology.update import (
        ElasticConsolidationUpdate,
        ParameterUpdateConfig,
    )

    config = ParameterUpdateConfig.elastic_consolidation(
        step_size=case.config.get("step_size", 0.01),
        momentum=case.config.get("momentum", 0.9),
    )

    # Create deterministic geometry
    _, input_dim = case.state.shape
    _, output_dim = case.prediction.shape

    geometry_config = GeometryConfig.feedforward(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dims=(output_dim,),
    )
    geometry = FeedforwardGeometry(geometry_config)

    seed = case.config.get("seed", 0)
    generator = torch.Generator(device=case.state.device).manual_seed(seed + 3000)
    for param in geometry.params.values():
        param.data.normal_(generator=generator)

    # Create deterministic pseudo-gradients
    pseudo_grads = []
    generator = torch.Generator(device=case.multiplier.device).manual_seed(seed + 2000)
    for name, param in geometry.params.items():
        pg = torch.randn_like(param, generator=generator)
        pseudo_grads.append(pg)

    params = dict(geometry.params)
    update = ElasticConsolidationUpdate(config)
    updated = update.step(params, pseudo_grads, geometry)

    return updated
