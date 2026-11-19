"""The substrate axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``; kernel parity is structural
in ``test_primitive_kernel_parity.py``. What is specific to a substrate is the
factory's determinism and the structured spec's round trip through the typed
``SubstrateConfig``. The legacy per-package ``make_case_noisy``/``_sparse``/
``_high_*`` variants are the substrate's own factory rows now, so there is one
body to keep.
"""

from __future__ import annotations

from importlib import import_module

import pytest

from computronium.ontology.substrate.spec import SubstrateSpec
from computronium.primitives.cases import IMPOSSIBLE
from computronium.primitives.registry import REGISTRY
from tests.primitives._contract import make_case

SPECS = tuple(
    sorted(
        (
            spec
            for spec in REGISTRY.values()
            if spec.axis == "substrate" and spec.id not in IMPOSSIBLE
        ),
        key=lambda spec: spec.id,
    )
)
IDS = [spec.id for spec in SPECS]


def _config(spec):
    owner, method = spec.config_factory.rsplit(".", 1)
    module_path, class_name = owner.rsplit(".", 1)
    config_class = getattr(import_module(module_path), class_name)
    return getattr(config_class, method)()


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_factory_is_deterministic(spec) -> None:
    """Two case factories over one spec build the same config."""
    first = make_case(spec, seed=0)
    second = make_case(spec, seed=0)
    assert type(first) is type(second), spec.id
    assert first.config == second.config, spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_spec_survives_its_config_round_trip(spec) -> None:
    """The structured spec is idempotent under projection to its typed config."""
    lifted = SubstrateSpec.from_config(_config(spec))
    assert SubstrateSpec.from_config(lifted.to_config()) == lifted, spec.id
