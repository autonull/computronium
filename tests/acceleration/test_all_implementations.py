"""Central registry test - iterates over all registered implementations."""

import importlib

import pytest

from computronium.acceleration.registry import all_specs


def _is_state_dynamics_like(spec) -> bool:
    """Check if spec uses the standard step/case interface."""
    return spec.axis in (
        "state_dynamics",
        "credit_assignment",
        "parameter_update",
        "plasticity",
    )


@pytest.mark.parametrize("spec", all_specs())
def test_reference_smoke(spec):
    """Test that reference implementation runs without error."""
    # Skip geometry and substrate primitives - they have different interfaces
    if spec.axis in ("geometry", "substrate"):
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
    if spec.axis in ("geometry", "substrate"):
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
