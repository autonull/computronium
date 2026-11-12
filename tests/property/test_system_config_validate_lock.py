"""Lock: SystemConfig.validate() rejects known-incompatible primitive pairs.

The flat ``_INCOMPATIBILITY_RULES`` table is deleted (TODO89 T4): legality has
one source, the declared constraints consumed by ``iter_candidates``, and the
last-mile gate is ``SystemConfig.validate``. These two tests keep the last-mile
contract: a known-bad pair raises, a known-good pair does not.
"""

from __future__ import annotations

import pytest

from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.system import SystemConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium.state import PlasticityConfig


def _base_config(
    substrate: str = "digital",
    geometry: str = "feedforward",
    dynamics: str = "energy_minimization",
    plasticity: str = "null",
    credit: str = "thermodynamic_contrast",
    update: str = "euclidean",
) -> SystemConfig:
    """Create a valid base SystemConfig for testing."""
    return SystemConfig(
        substrate=SubstrateConfig.digital()
        if substrate == "digital"
        else SubstrateConfig.analog(),
        geometry=GeometryConfig.feedforward(
            input_dim=64, output_dim=10, hidden_dims=[128, 64]
        )
        if geometry == "feedforward"
        else GeometryConfig.recurrent(input_dim=64, output_dim=10, hidden_dim=128),
        dynamics=StateDynamicsConfig.energy_minimization()
        if dynamics == "energy_minimization"
        else StateDynamicsConfig.instantaneous(),
        plasticity=PlasticityConfig.null()
        if plasticity == "null"
        else PlasticityConfig.fast_weights(
            fast_weight_dim=64, decay=0.9, learning_rate=0.1
        ),
        credit=CreditAssignmentConfig.thermodynamic_contrast()
        if credit == "thermodynamic_contrast"
        else CreditAssignmentConfig.gradient(),
        update=ParameterUpdateConfig.euclidean()
        if update == "euclidean"
        else ParameterUpdateConfig.adam(),
    )


def test_system_config_validate_catches_incompatibilities() -> None:
    """SystemConfig.validate() rejects known incompatible combinations."""
    config = SystemConfig(
        substrate=SubstrateConfig.quantum(),
        geometry=GeometryConfig.feedforward(
            input_dim=64, output_dim=10, hidden_dims=[128, 64]
        ),
        dynamics=StateDynamicsConfig.spike_integration(),
        plasticity=PlasticityConfig.null(),
        credit=CreditAssignmentConfig.temporal_trace(),
        update=ParameterUpdateConfig.euclidean(),
    )

    with pytest.raises(ValueError, match="requires"):
        config.validate()


def test_system_config_validate_allows_compatible() -> None:
    """SystemConfig.validate() allows compatible combinations."""
    config = _base_config()
    config.validate()  # Should not raise
