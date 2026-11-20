"""One registry gate for every primitive spec.

The TODO97 migration replaced the per-primitive modules with a 75-row
``PrimitiveSpec`` registry. This file guards that registry: every row is a
declared spec, every kernel claim carries its evidence, and a kernel parity
test can pass only when the selected path is ``implemented`` (a stub cannot).
Reference execution is the wiring suite's job (``test_primitive_wiring.py``),
so it is not duplicated here.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import all_specs
from computronium.primitives.registry import REGISTRY

KERNEL_STATES = frozenset({"implemented", "wrapper", "stub", "absent"})

PRIMITIVE_SPECS = tuple(
    sorted(
        (spec for spec in all_specs() if spec.kind == "primitive"),
        key=lambda spec: spec.id,
    )
)
IDS = [spec.id for spec in PRIMITIVE_SPECS]


def _primitive(spec):
    return REGISTRY[spec.id]


def _has_microbench_evidence(spec) -> bool:
    """Check if microbench JSONL evidence exists for this spec."""
    bench_dir = Path("artifacts/benchmarks")
    if not bench_dir.exists():
        return False
    for jsonl_file in bench_dir.glob("*.jsonl"):
        with jsonl_file.open() as handle:
            for line in handle:
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("id") == spec.id:
                    return True
    return False


def _dispatch_routes_to_kernel(spec) -> bool:
    """Check if ``dispatch.auto`` routes to kernel (not reference)."""
    try:
        backend = select_backend(spec, "auto")
    except Exception:
        return False
    return backend != "reference"


@pytest.mark.parametrize("spec", PRIMITIVE_SPECS, ids=IDS)
def test_primitive_is_a_declared_spec(spec) -> None:
    """Every acceleration primitive row names a declared ``PrimitiveSpec``."""
    primitive = _primitive(spec)
    assert primitive.id == spec.id
    assert primitive.kernel_status in KERNEL_STATES, primitive.kernel_status
    assert primitive.axis in {
        "credit",
        "dynamics",
        "geometry",
        "plasticity",
        "substrate",
        "update",
    }


@pytest.mark.parametrize("spec", PRIMITIVE_SPECS, ids=IDS)
def test_absent_kernel_refuses_parity(spec) -> None:
    """The parity test passes only when the kernel path is implemented."""
    primitive = _primitive(spec)
    if primitive.kernel_status == "implemented":
        pytest.skip("declared: implemented kernels are covered by the parity contract")

    from computronium.primitives.protocol import ReferenceAdapter

    adapter = ReferenceAdapter(primitive)
    with pytest.raises(RuntimeError, match="Kernel not implemented"):
        adapter.kernel_step(object())


@pytest.mark.parametrize("spec", PRIMITIVE_SPECS, ids=IDS)
def test_implemented_kernel_carries_its_evidence(spec) -> None:
    """An implemented kernel names its entrypoint, a route, and microbench evidence."""
    primitive = _primitive(spec)
    if primitive.kernel_status != "implemented":
        pytest.skip("declared: only applies to implemented kernels")

    assert primitive.kernel_entrypoint, f"{spec.id}: no kernel entrypoint"
    assert _has_microbench_evidence(spec), (
        f"{spec.id}: no microbench evidence in artifacts/benchmarks/"
    )
    assert _dispatch_routes_to_kernel(spec), (
        f"{spec.id}: dispatch.auto routes to reference"
    )
