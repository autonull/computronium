"""The substrate axis contract, parameterized by spec.

The case/reference seed contract is axis-independent and lives in
``tests/primitives/test_primitive_contract.py``; a substrate is seed-blind by
declaration there, and kernel parity is structural in
``test_primitive_kernel_parity.py``. What is specific to a substrate is the
object its factory builds: a deterministic instance of the spec's device model,
and a spec that survives a config round trip. The legacy per-package structural
tests repeated both per substrate, and its ``make_case_noisy``/``_sparse``/
``_high_*`` variants are covered here by walking every factory the cases module
declares rather than naming them.
"""

from __future__ import annotations

from importlib import import_module

import pytest

from computronium.ontology.substrate.spec import SubstrateSpec
from tests.primitives._contract import (
    axis_specs,
    case_factories,
    make_case,
    package,
    reference,
)

SPECS = axis_specs("substrate")
IDS = [spec.id for spec in SPECS]


FACTORIES = tuple((spec, factory) for spec in SPECS for factory in case_factories(spec))
FACTORY_IDS = [f"{spec.id}-{factory}" for spec, factory in FACTORIES]


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_factory_is_deterministic(spec) -> None:
    """Two factories over one spec build the same type and config."""
    case = make_case(spec, seed=0)
    first = reference(spec, case)
    second = reference(spec, case)
    assert type(first) is type(second), spec.id
    assert first.config == second.config, spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_spec_round_trips_through_its_config(spec) -> None:
    """The spec's config is a lossless view of the spec."""
    config = make_case(spec, seed=0).spec.to_config()
    assert SubstrateSpec.from_config(config).to_config() == config, spec.id


@pytest.mark.parametrize(("spec", "factory"), FACTORIES, ids=FACTORY_IDS)
def test_every_case_factory_builds_the_same_deterministic_substrate(
    spec, factory: str
) -> None:
    """A noisy/sparse variant case builds the same substrate twice, losslessly."""
    cases = import_module(f"{package(spec)}.cases")
    first = getattr(cases, factory)(device="cpu", seed=0)
    second = getattr(cases, factory)(device="cpu", seed=0)

    assert first.spec == second.spec, (spec.id, factory)
    if factory != "make_case":
        assert first.spec != make_case(spec, seed=0).spec, (spec.id, factory)
    assert reference(spec, first).config == reference(spec, second).config, (
        spec.id,
        factory,
    )
    config = first.spec.to_config()
    assert SubstrateSpec.from_config(config).to_config() == config, (spec.id, factory)
