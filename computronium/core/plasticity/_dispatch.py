"""The one dispatcher from a ``PlasticityConfig`` to its law."""

from __future__ import annotations

from computronium.core.joint.transition import (
    NullPlasticity,
    PlasticityConfig,
    PlasticityPrimitive,
)
from computronium.core.plasticity.adaptive_psi import conflict_adaptive_from_config
from computronium.core.plasticity.closed_form import closed_form_ridge_from_config
from computronium.core.plasticity.fast_weights import create_fast_weight_plasticity
from computronium.core.plasticity.routing import create_routing_plasticity
from computronium.core.plasticity.rule_state import create_rule_state_plasticity
from computronium.core.plasticity.substrate_coupled import (
    create_substrate_coupled_plasticity,
)
from computronium.core.plasticity.temporal_psi import create_temporal_psi_plasticity

__all__ = ["plasticity_from_config"]


def plasticity_from_config(  # ruff: ignore[too-many-return-statements]
    config: PlasticityConfig,
) -> PlasticityPrimitive:
    """Instantiate the plasticity law named by ``config.plasticity_type``.

    One dispatcher for every caller that builds a joint system: an unknown type
    raises instead of falling back to ``null``, because null plasticity must be
    declared, not defaulted.

    Args:
        config: The plasticity axis's typed config.

    Returns:
        The law the config names.

    Raises:
        ValueError: The config names no known plasticity type.
    """
    match config.plasticity_type.lower():
        case "routing":
            return create_routing_plasticity(config)
        case "fast_weights":
            return create_fast_weight_plasticity(config)
        case "substrate_coupled":
            return create_substrate_coupled_plasticity(config)
        case "rule_state":
            return create_rule_state_plasticity(config)
        case "temporal_psi":
            return create_temporal_psi_plasticity(config)
        case "conflict_adaptive":
            return conflict_adaptive_from_config(config)
        case "closed_form_ridge":
            return closed_form_ridge_from_config(config)
        case "null":
            return NullPlasticity()
        case other:
            msg = f"Unknown plasticity_type: {other!r}"
            raise ValueError(msg)
