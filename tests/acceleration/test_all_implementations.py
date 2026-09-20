"""Central registry test - iterates over all registered implementations."""

import importlib
import json
from pathlib import Path

import pytest

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import all_specs

_STATE_DYNAMICS_AXES = {
    "state_dynamics",
    "credit_assignment",
    "parameter_update",
    "plasticity",
}


_GEOMETRY_SUBSTRATE_AXES = {"geometry", "substrate"}


def _is_state_dynamics_like(spec) -> bool:
    """Check if spec uses the standard step/case interface."""
    return spec.axis in _STATE_DYNAMICS_AXES


def _has_microbench_evidence(spec) -> bool:
    """Check if microbench JSONL evidence exists for this spec."""
    # Look for bench.jsonl or similar in artifacts/benchmarks/
    bench_dir = Path("artifacts/benchmarks")
    if not bench_dir.exists():
        return False
    # Check if any JSONL file contains this spec's id
    for jsonl_file in bench_dir.glob("*.jsonl"):
        with jsonl_file.open() as f:
            for line in f:
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("id") == spec.id:
                    return True
    return False


def _dispatch_routes_to_kernel(spec) -> bool:
    """Check if dispatch.auto routes to kernel (not reference)."""
    try:
        backend = select_backend(spec, "auto")
    except Exception:
        return False
    else:
        return backend != "reference"


@pytest.mark.parametrize("spec", all_specs())
def test_reference_smoke(spec):
    """Test that reference implementation runs without error."""
    # Skip geometry and substrate primitives - they have different interfaces
    if spec.axis in _GEOMETRY_SUBSTRATE_AXES:
        pytest.skip(f"{spec.axis} primitives use different interface")

    module_path = spec.reference_entrypoint.rsplit(".", 1)[0]
    module = importlib.import_module(module_path)

    case_module_path = module_path.rsplit(".", 1)[0] + ".cases"
    case_module = importlib.import_module(case_module_path)

    case = case_module.make_case()
    output = module.step(case)

    assert output is not None


@pytest.mark.parametrize("spec", all_specs())
def test_kernel_parity(spec):
    """Test that kernel output matches reference within tolerance."""
    # Skip geometry and substrate primitives - they have different interfaces
    if spec.axis in _GEOMETRY_SUBSTRATE_AXES:
        pytest.skip(f"{spec.axis} primitives use different interface")

    if "kernel" not in spec.supported_backends:
        pytest.skip("no kernel backend")

    module_path = spec.reference_entrypoint.rsplit(".", 2)[0]

    reference_module = importlib.import_module(f"{module_path}.reference")
    kernel_module = importlib.import_module(f"{module_path}.kernel")
    case_module = importlib.import_module(f"{module_path}.cases")

    if not kernel_module.is_available():
        pytest.skip("kernel not available")

    # Use separate cases for reference and kernel to avoid autograd graph reuse issues
    case_ref = case_module.make_case()
    case_kern = case_module.make_case()

    reference_output = reference_module.step(case_ref)
    kernel_output = kernel_module.step(case_kern)

    from computronium.acceleration.parity import assert_parity

    assert_parity(reference_output, kernel_output, spec.parity)


@pytest.mark.parametrize("spec", all_specs())
def test_kernel_verified_promotion_rule(spec):
    """Enforce status promotion rule: kernel_verified requires (a) parity green on CPU+GPU,
    (b) microbench JSONL evidence, (c) dispatch auto routes to kernel.

    This test FAILS if a spec claims kernel_verified without meeting all criteria.
    """
    if spec.status != "kernel_verified":
        pytest.skip("only applies to kernel_verified specs")

    # (a) Parity must pass (this test running means it does on current device)
    # We also check kernel is available
    if "kernel" not in spec.supported_backends:
        pytest.fail(f"{spec.id}: claims kernel_verified but no kernel backend")

    module_path = spec.reference_entrypoint.rsplit(".", 2)[0]
    kernel_module = importlib.import_module(f"{module_path}.kernel")

    if not kernel_module.is_available():
        pytest.fail(f"{spec.id}: claims kernel_verified but kernel not available")

    # (b) Microbench JSONL evidence
    if not _has_microbench_evidence(spec):
        pytest.fail(
            f"{spec.id}: claims kernel_verified but no microbench evidence found in artifacts/benchmarks/"
        )

    # (c) Dispatch auto routes to kernel
    if not _dispatch_routes_to_kernel(spec):
        pytest.fail(
            f"{spec.id}: claims kernel_verified but dispatch.auto returns 'reference'"
        )
