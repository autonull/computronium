"""One kernel-parity contract for every primitive spec.

The TODO97 migration deleted the per-primitive kernel modules. A spec that
declares ``kernel_status == "implemented"`` has a kernel rung to compare; an
absent kernel is reference-only and the parity test skips. Reference
determinism and the seed contract live in ``test_primitive_contract.py``, so
this file adds only the rung comparison.
"""

from __future__ import annotations

import pytest

from computronium.acceleration.parity import assert_parity
from computronium.acceleration.spec import ParityTolerance
from computronium.primitives.protocol import ReferenceAdapter
from computronium.primitives.registry import REGISTRY

SPECS = tuple(sorted(REGISTRY.values(), key=lambda spec: spec.id))
IDS = [spec.id for spec in SPECS]

#: Axes whose entrypoint builds an object with a factory, not a ``StepResult``.
_FACTORY_AXES = frozenset({"geometry", "substrate"})

#: Seeds the kernel must track the reference on. One seed cannot see a rung
#: that caches the first case; the legacy per-package tests looped 0/1/42.
SEEDS = (0, 3)


def _case(spec, seed: int):
    return ReferenceAdapter(spec).make_task_case("mnist", {"seed": seed}, seed)


def test_every_implemented_kernel_declares_its_entrypoint() -> None:
    """A ``kernel_status="implemented"`` row names the entrypoint it dispatches to."""
    missing = [
        spec.id
        for spec in SPECS
        if spec.kernel_status == "implemented" and not spec.kernel_entrypoint
    ]
    assert not missing, missing


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_kernel_matches_reference(spec, seed: int) -> None:
    """The kernel rung agrees with the reference within the parity tolerance."""
    if spec.axis in _FACTORY_AXES:
        pytest.skip("geometry/substrate build an object, not a StepResult")
    if spec.kernel_status != "implemented":
        pytest.skip("kernel absent: the reference path is the only rung")

    adapter = ReferenceAdapter(spec)
    reference = adapter.reference_step(_case(spec, seed))
    kernel = adapter.kernel_step(_case(spec, seed))
    assert_parity(reference.weights, kernel.weights, ParityTolerance())
