"""Accelerated kernel for Elastic Consolidation Update.

Delegates to computronium.ontology.update.ElasticConsolidationUpdate with triton acceleration.
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

    # Use accelerated implementation

    from computronium.ontology.update import (
        ElasticConsolidationUpdate,
        ParameterUpdateConfig,
    )

    config = ParameterUpdateConfig.elastic_consolidation(
        step_size=case.config.get("step_size", 0.01),
        momentum=case.config.get("momentum", 0.9),
    )

    geometry = update_geometry(case)
    pseudo_grads = update_pseudo_grads(case, geometry)

    params = dict(geometry.params)
    update = ElasticConsolidationUpdate(config)
    updated = update.step(params, pseudo_grads, geometry)

    return updated
