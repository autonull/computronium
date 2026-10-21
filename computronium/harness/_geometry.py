"""The reference forward pass a geometry's case runs through.

A geometry's reference implementation forwards the case's state through the
case's geometry on a digital substrate, under a deterministic RNG state. The
shape of that is the same for every geometry, so it is written once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._case import seeded_rng

if TYPE_CHECKING:
    from torch import Tensor

__all__ = ["geometry_forward"]


def geometry_forward(case: Any) -> Tensor:
    """Forward the case's state through the case's geometry.

    Args:
        case: The case the geometry's reference step consumes.

    Returns:
        The geometry's output.
    """
    from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig

    substrate = DigitalSubstrate(SubstrateConfig.digital(device=str(case.state.device)))
    with seeded_rng(case.config.get("seed", 0)):
        output = case.geometry(case.state, substrate)
    return output
