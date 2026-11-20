"""A primitive kernel must run without the adapter's reference rung (TODO97 S7).

The kill test: patch ``ReferenceAdapter.reference_step`` to raise. A kernel
that quietly delegates to it stops, which is the point — a wrapper that runs
the reference rung and reports the kernel rung's speed is the defect S7 fixes.
An ``absent`` row must still refuse ``kernel_step`` by name.
"""

from __future__ import annotations

import pytest

from computronium.primitives.cases import IMPOSSIBLE, PrimitiveImpossibleError
from computronium.primitives.protocol import ReferenceAdapter
from computronium.primitives.registry import REGISTRY

SPECS = tuple(sorted(REGISTRY.values(), key=lambda spec: spec.id))
IDS = [spec.id for spec in SPECS]


def _kill_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*args: object, **kwargs: object) -> object:
        msg = "the adapter's reference rung was called by a kernel"
        raise AssertionError(msg)

    monkeypatch.setattr(ReferenceAdapter, "reference_step", _raise)


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_a_kernel_never_calls_the_adapter_reference(
    spec, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An implemented kernel runs with its reference rung killed."""
    adapter = ReferenceAdapter(spec)
    if spec.id in IMPOSSIBLE:
        with pytest.raises(PrimitiveImpossibleError):
            adapter.make_task_case("mnist", {"seed": 0}, 0)
        return
    case = adapter.make_task_case("mnist", {"seed": 0}, 0)
    _kill_reference(monkeypatch)

    if spec.kernel_status != "implemented":
        with pytest.raises(RuntimeError, match="Kernel not implemented"):
            adapter.kernel_step(case)
        return

    result = adapter.kernel_step(case)
    assert result.weights or result.activations or result.state, (
        f"{spec.id}: the kernel returned no evidence"
    )
