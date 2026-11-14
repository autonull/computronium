"""One kernel-parity contract for every primitive spec.

Each primitive ships a ``cases`` module, a reference entrypoint, and a kernel
entrypoint, and every spec declares the tolerance the two must agree within. The
contract is therefore the same for all of them: it is written once here and
parameterized by spec, so a new primitive is covered by registering it — and by
declaring any non-default case knob it supports in ``CASE_VARIANTS``.
"""

from __future__ import annotations

from importlib import import_module

import pytest
import torch

from computronium.acceleration.parity import assert_parity, digest
from computronium.acceleration.registry import all_specs
from tests.primitives._contract import case_factories

#: Reference entrypoints whose callable takes the case's own spec.
_TAKES_SPEC = frozenset({"make_substrate"})

SPECS = tuple(
    sorted(
        (spec for spec in all_specs() if spec.kind == "primitive"),
        key=lambda spec: spec.id,
    )
)
IDS = [spec.id for spec in SPECS]


#: Seeds the kernel must track the reference on. One seed cannot see a rung
#: that reads a fixed seed or caches the first case; the legacy per-package
#: parity tests looped 0/1/42 by hand, so the contract loops here instead.
SEEDS = (0, 3)

#: Non-default case knobs a spec's kernel must also track, by spec ID. A law
#: with a second mode is one mechanism with two declared paths; the legacy
#: per-package parity test asserted the mode per package.
CASE_VARIANTS: dict[str, tuple[dict, ...]] = {
    "primitive.credit_assignment.local_goodness": ({"local_objective": "lemma"},),
}
VARIANT_CASES = tuple(
    (spec, variant) for spec in SPECS for variant in CASE_VARIANTS.get(spec.id, ())
)


def _call(entrypoint: str, case):
    module_path, _, function_name = entrypoint.rpartition(".")
    function = getattr(import_module(module_path), function_name)
    return function(case.spec) if function_name in _TAKES_SPEC else function(case)


def _run(spec, entrypoint: str, seed: int):
    reference_module = spec.reference_entrypoint.rpartition(".")[0]
    cases = import_module(f"{reference_module.rpartition('.')[0]}.cases")
    return _call(entrypoint, cases.make_case(seed=seed))


def test_every_primitive_declares_a_kernel_entrypoint() -> None:
    """A spec with a kernel backend must name the kernel rung's entrypoint."""
    missing = [
        spec.id
        for spec in SPECS
        if "kernel" in spec.supported_backends and not spec.kernel_entrypoint
    ]
    assert not missing, missing


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_kernel_matches_reference(spec, seed: int) -> None:
    """The kernel rung agrees with the reference within the spec's tolerance.

    A substrate factory returns an object rather than tensors, so its parity is
    structural: the same configuration, digested.
    """
    assert spec.kernel_entrypoint is not None, spec.id
    reference = _run(spec, spec.reference_entrypoint, seed=seed)
    kernel = _run(spec, spec.kernel_entrypoint, seed=seed)
    if isinstance(reference, torch.Tensor | dict | list | tuple):
        assert_parity(reference, kernel, spec.parity)
    else:
        assert digest(reference) == digest(kernel), (spec.id, seed)


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_reference_is_deterministic(spec) -> None:
    """Two reference calls on one seed produce the same output."""
    first = _run(spec, spec.reference_entrypoint, seed=3)
    second = _run(spec, spec.reference_entrypoint, seed=3)
    assert digest(first) == digest(second), spec.id


@pytest.mark.parametrize(
    ("spec", "variant"),
    VARIANT_CASES,
    ids=[f"{spec.id}-{','.join(variant)}" for spec, variant in VARIANT_CASES],
)
def test_kernel_matches_reference_in_every_declared_mode(spec, variant) -> None:
    """A second mode of a law is a second path the kernel must match."""
    assert spec.kernel_entrypoint is not None, spec.id
    cases = import_module(
        f"{spec.reference_entrypoint.rsplit('.', 1)[0].rsplit('.', 1)[0]}.cases"
    )
    case = cases.make_case(seed=0, **variant)
    reference = _call(spec.reference_entrypoint, case)
    kernel = _call(spec.kernel_entrypoint, case)
    if isinstance(reference, torch.Tensor | dict | list | tuple):
        assert_parity(reference, kernel, spec.parity)
    else:
        assert digest(reference) == digest(kernel), spec.id


def _variant_factories(spec):
    """Every case factory the spec's cases module declares, beyond ``make_case``."""
    return tuple(factory for factory in case_factories(spec) if factory != "make_case")


FACTORY_CASES = tuple(
    (spec, factory) for spec in SPECS for factory in _variant_factories(spec)
)
FACTORY_IDS = [f"{spec.id}-{factory}" for spec, factory in FACTORY_CASES]


@pytest.mark.parametrize(("spec", "factory"), FACTORY_CASES, ids=FACTORY_IDS)
def test_kernel_matches_reference_on_every_case_factory(spec, factory: str) -> None:
    """A noisy/sparse case factory is a second case the kernel must match."""
    assert spec.kernel_entrypoint is not None, spec.id
    cases = import_module(
        f"{spec.reference_entrypoint.rsplit('.', 1)[0].rsplit('.', 1)[0]}.cases"
    )
    case = getattr(cases, factory)(device="cpu", seed=0)
    reference = _call(spec.reference_entrypoint, case)
    kernel = _call(spec.kernel_entrypoint, case)
    if isinstance(reference, torch.Tensor | dict | list | tuple):
        assert_parity(reference, kernel, spec.parity)
    else:
        assert digest(reference) == digest(kernel), (spec.id, factory)
