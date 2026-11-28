"""Lock: every declared primitive across all six registries has a composer implementation.

Regression this guards: ``compose_joint_system_from_configs`` hand-maintained its
dynamics and credit dispatch, so primitives the registries declared but the
dispatch omitted — ``pc_alm``/``lazy``/``error_predictive_coding`` dynamics and
``pc_alm`` credit — passed ``SystemConfig.validate`` and screening, then aborted
every training cell with ``Unknown dynamics_type``/``credit_type``. The composer
now reads the registries; these tests pin that the two never drift again.

Extended to all six axes (Substrate, Geometry, Dynamics, Plasticity, Credit, Update).
"""

from __future__ import annotations

import pytest

from computronium.core.plasticity import plasticity_from_config
from computronium.core.system_trainer.joint import _credit_from_config
from computronium.experiment.kernel.compose import build_geometry_config
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology import (
    DYNAMICS_REGISTRY,
    CreditAssignmentConfig,
    ParameterUpdateConfig,
    PlasticityConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    dynamics_from_config,
    geometry_from_config,
    substrate_from_config,
    update_from_config,
)

seed_all_registries()


def _get_primitives_for_axis(axis: StructuralAxis) -> list[str]:
    """Get all primitive names for a structural axis."""
    return sorted(AXES_REGISTRIES[axis].keys())


# The task-derived arguments a topology's own task family supplies; the
# canonical image shape covers every other builder.
_GEOMETRY_TASK_ARGS: dict[str, dict[str, object]] = {
    "graph": {"edge_index": [[0, 1], [1, 0]]},
    "spatial_lattice": {"lattice_dims": [2, 4, 4]},
}


# Test each axis - verify config classmethod exists and returns a config
@pytest.mark.parametrize("name", sorted(DYNAMICS_REGISTRY))
def test_every_dynamics_registry_key_composes(name: str):
    """Each registered dynamics_type has a valid config classmethod."""
    config = getattr(StateDynamicsConfig, name)()
    assert config is not None
    assert config.dynamics_type == name
    # Verify it can be instantiated through the composer
    instance = dynamics_from_config(config)
    assert instance is not None


@pytest.mark.parametrize("name", _get_primitives_for_axis(StructuralAxis.CREDIT))
def test_every_credit_registry_key_composes(name: str):
    """Each credit primitive the registry declares has a valid config classmethod."""
    config = getattr(CreditAssignmentConfig, name)()
    assert config is not None
    assert config.credit_type == name
    instance = _credit_from_config(config)
    assert instance is not None


@pytest.mark.parametrize("name", _get_primitives_for_axis(StructuralAxis.SUBSTRATE))
def test_every_substrate_registry_key_composes(name: str):
    """Each substrate primitive the registry declares has a valid config classmethod."""
    config = getattr(SubstrateConfig, name)()
    assert config is not None
    # SubstrateConfig returns substrate_type as 'digital' for all digital variants
    # The name is the preset name, not the substrate_type
    instance = substrate_from_config(config)
    assert instance is not None


@pytest.mark.parametrize("name", _get_primitives_for_axis(StructuralAxis.GEOMETRY))
def test_every_geometry_registry_key_composes(name: str):
    """Each geometry primitive the registry declares composes from the task shape."""
    config = build_geometry_config(
        dict(_GEOMETRY_TASK_ARGS.get(name, {})),
        topology=name,
        input_shape=(1, 28, 28),
        output_dim=10,
    )
    assert config.topology_type == name
    assert geometry_from_config(config) is not None


@pytest.mark.parametrize("name", _get_primitives_for_axis(StructuralAxis.PLASTICITY))
def test_every_plasticity_registry_key_composes(name: str):
    """Each plasticity primitive the registry declares has a valid config classmethod."""
    config = getattr(PlasticityConfig, name)()
    assert config is not None
    assert config.plasticity_type == name
    assert plasticity_from_config(config) is not None


@pytest.mark.parametrize("name", _get_primitives_for_axis(StructuralAxis.UPDATE))
def test_every_update_registry_key_composes(name: str):
    """Each update primitive the registry declares has a valid config classmethod."""
    config = getattr(ParameterUpdateConfig, name)()
    assert config is not None
    assert config.update_type == name
    assert update_from_config(config) is not None
