"""Credit dispatch totality lock (TODO88 G6).

The credit axis registry advertises ten primitives, but two of the three
credit dispatchers (``spec``, ``factory``, ``joint``) had drifted: the ``spec``
copy — the one ``compose_system_from_configs`` uses when called through
``computronium.core.system_trainer.spec`` — did not know ``local_contrastive``
or ``pc_alm``, so those legal cells died with ``Unknown credit_type`` at system
build. The lock contains that case: every advertised credit primitive must
build through every dispatcher entry point.
"""

from __future__ import annotations

import pytest

from computronium.core.system_trainer.factory import (
    _credit_from_config as factory_credit_from_config,
)
from computronium.core.system_trainer.joint import (
    _credit_from_config as joint_credit_from_config,
)
from computronium.core.system_trainer.spec import (
    _credit_from_config as spec_credit_from_config,
)
from computronium.experiment.schema.axis import AXES_REGISTRIES
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.ontology.credit import CreditAssignmentConfig

DISPATCHERS = (
    pytest.param(spec_credit_from_config, id="spec"),
    pytest.param(factory_credit_from_config, id="factory"),
    pytest.param(joint_credit_from_config, id="joint"),
)


@pytest.fixture(scope="module")
def credit_names() -> list[str]:
    seed_all_registries()
    return sorted(AXES_REGISTRIES["credit"].keys())


def test_registry_advertises_the_known_credits(credit_names: list[str]) -> None:
    assert "local_contrastive" in credit_names
    assert "pc_alm" in credit_names


@pytest.mark.parametrize("dispatch", DISPATCHERS)
def test_every_advertised_credit_builds(dispatch, credit_names: list[str]) -> None:
    for name in credit_names:
        config = getattr(CreditAssignmentConfig, name)()
        credit = dispatch(config)
        assert type(credit).__name__
