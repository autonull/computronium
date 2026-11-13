"""One kernel-parity contract for every primitive spec.

Each primitive ships a ``cases`` module, a reference entrypoint, and a kernel
entrypoint, and every spec declares the tolerance the two must agree within. The
contract is therefore the same for all of them: it is written once here and
parameterized by spec, so a new primitive is covered by registering it.

The per-axis reference and case assertions stay in each package's own tests;
what this module replaces is the private copy of "the kernel matches the
reference" that every package used to carry.
"""

from __future__ import annotations

from importlib import import_module

import pytest
import torch

from computronium.acceleration.parity import assert_parity, digest
from computronium.acceleration.registry import all_specs

#: Reference entrypoints whose callable takes the case's own spec.
_TAKES_SPEC = frozenset({"make_substrate"})

SPECS = tuple(
    sorted(
        (spec for spec in all_specs() if spec.kind == "primitive"),
        key=lambda spec: spec.id,
    )
)
IDS = [spec.id for spec in SPECS]


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


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_kernel_matches_reference(spec) -> None:
    """The kernel rung agrees with the reference within the spec's tolerance.

    A substrate factory returns an object rather than tensors, so its parity is
    structural: the same configuration, digested.
    """
    assert spec.kernel_entrypoint is not None, spec.id
    reference = _run(spec, spec.reference_entrypoint, seed=0)
    kernel = _run(spec, spec.kernel_entrypoint, seed=0)
    if isinstance(reference, torch.Tensor | dict | list | tuple):
        assert_parity(reference, kernel, spec.parity)
    else:
        assert digest(reference) == digest(kernel), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_reference_is_deterministic(spec) -> None:
    """Two reference calls on one seed produce the same output."""
    first = _run(spec, spec.reference_entrypoint, seed=3)
    second = _run(spec, spec.reference_entrypoint, seed=3)
    assert digest(first) == digest(second), spec.id
