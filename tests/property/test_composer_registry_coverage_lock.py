"""Lock: every declared dynamics/credit primitive has a composer implementation.

Regression this guards: ``compose_joint_system_from_configs`` hand-maintained its
dynamics and credit dispatch, so primitives the registries declared but the
dispatch omitted — ``pc_alm``/``lazy``/``error_predictive_coding`` dynamics and
``pc_alm`` credit — passed ``SystemConfig.validate`` and screening, then aborted
every training cell with ``Unknown dynamics_type``/``credit_type``. The composer
now reads the registries; these tests pin that the two never drift again.
"""

from __future__ import annotations

import pytest

from computronium.core.system_trainer.joint import _credit_from_config
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology import (
    DYNAMICS_REGISTRY,
    CreditAssignmentConfig,
    StateDynamicsConfig,
    dynamics_from_config,
)

seed_all_registries()


def _credit_primitives() -> list[str]:
    return sorted(AXES_REGISTRIES[StructuralAxis.CREDIT].keys())


@pytest.mark.parametrize("name", sorted(DYNAMICS_REGISTRY))
def test_every_dynamics_registry_key_composes(name: str):
    """Each registered dynamics_type instantiates through the composer."""
    instance = dynamics_from_config(getattr(StateDynamicsConfig, name)())
    assert instance is not None


@pytest.mark.parametrize("name", _credit_primitives())
def test_every_declared_credit_composes(name: str):
    """Each credit primitive the registry declares instantiates through the composer."""
    instance = _credit_from_config(getattr(CreditAssignmentConfig, name)())
    assert instance is not None
