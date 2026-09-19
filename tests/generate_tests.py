#!/usr/bin/env python
"""Generate test files from ImplementationSpec and Case dataclass.

This script reads a primitive or algorithm spec and generates the standard
test files (test_reference.py, test_kernel_parity.py, test_cases.py).

Usage:
    uv run python tests/generate_tests.py --spec primitive.state_dynamics.energy_minimization
    uv run python tests/generate_tests.py --spec algorithm.pcalm
    uv run python tests/generate_tests.py --all
"""

import argparse
import sys
from pathlib import Path

from computronium.acceleration.registry import all_specs


def get_spec(spec_id: str):
    """Get a spec by ID from the registry."""
    from computronium.acceleration.registry import get

    return get(spec_id)


def get_module_parts(entrypoint: str) -> tuple[str, str]:
    """Split entrypoint into module path and function name."""
    parts = entrypoint.split(".")
    return ".".join(parts[:-1]), parts[-1]


def get_module_name(spec) -> str:
    """Get the module name from spec.id (e.g., primitive.state_dynamics.energy_minimization -> computronium.primitives.state_dynamics.energy_minimization)"""
    # spec.id format: primitive.axis.name or algorithm.name
    return f"computronium.{spec.id.replace('primitive.', 'primitives.').replace('algorithm.', 'algorithms.')}"


def generate_primitive_tests(spec) -> dict[str, str]:
    """Generate test files for a primitive."""
    base_module = get_module_name(spec)
    case_module = f"{base_module}.cases"

    test_reference = f'''"""Reference implementation tests for {spec.name} primitive."""

import torch

from {base_module} import (
    make_case,
    reference_step,
)


def test_reference_step_returns_state():
    """Test that reference_step returns a CompositeState."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result is not None
    assert hasattr(result, "activity")
    assert hasattr(result, "plastic")
    assert hasattr(result, "substrate")
    assert "x" in result.activity


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    # Compare activations
    act1 = result1.activations
    act2 = result2.activations

    assert act1 is not None and act2 is not None
    for a1, a2 in zip(act1, act2):
        torch.testing.assert_close(a1, a2)


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    act1 = result1.activations
    act2 = result2.activations

    # At least one activation should differ
    differ = False
    for a1, a2 in zip(act1, act2):
        if not torch.allclose(a1, a2):
            differ = True
            break
    assert differ
'''

    test_kernel_parity = f'''"""Kernel parity tests for {spec.name} primitive."""

import pytest

from computronium.acceleration.parity import assert_parity
from {base_module} import (
    SPEC,
    make_case,
    reference_step,
)
from {base_module}.kernel import (
    is_available,
    step as kernel_step,
)


def test_kernel_parity():
    """Test that kernel output matches reference within tolerance."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case(device="cpu", seed=0)

    reference_output = reference_step(case)
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_different_seeds():
    """Test kernel parity with different seeds."""
    if not is_available():
        pytest.skip("kernel not available")

    for seed in [1, 2, 42]:
        case = make_case(device="cpu", seed=seed)

        reference_output = reference_step(case)
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, SPEC.parity)
'''

    test_cases = f'''"""Case factory tests for {spec.name} primitive."""

import torch

from {case_module} import (
    Case,
    make_case,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert isinstance(case.state, torch.Tensor)
    assert isinstance(case.prediction, torch.Tensor)
    assert isinstance(case.multiplier, torch.Tensor)
    assert isinstance(case.config, dict)
    assert hasattr(case, "geometry")


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.state, case2.state)
    torch.testing.assert_close(case1.prediction, case2.prediction)
    torch.testing.assert_close(case1.multiplier, case2.multiplier)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    # At least one tensor should differ
    assert not torch.allclose(case1.state, case2.state) or \\
           not torch.allclose(case1.prediction, case2.prediction) or \\
           not torch.allclose(case1.multiplier, case2.multiplier)


def test_make_case_config_structure():
    """Test that case config has expected structure."""
    case = make_case(device="cpu", seed=0)

    assert "steps" in case.config
    assert "step_size" in case.config
    assert "target" in case.config
    assert "seed" in case.config
    assert case.config["steps"] > 0
    assert case.config["step_size"] > 0
    assert case.config["seed"] == 0
'''

    return {
        "test_reference.py": test_reference,
        "test_kernel_parity.py": test_kernel_parity,
        "test_cases.py": test_cases,
    }


def generate_algorithm_tests(spec) -> dict[str, str]:
    """Generate test files for an algorithm."""
    base_module = get_module_name(spec)
    case_module = f"{base_module}.cases"

    test_reference = f'''"""Reference implementation tests for {spec.name} algorithm."""

import torch

from {base_module} import (
    make_case,
    reference_step,
)


def test_reference_step_returns_state():
    """Test that reference_step returns a CompositeState."""
    case = make_case(device="cpu", seed=0)
    result = reference_step(case)

    assert result is not None
    assert hasattr(result, "activity")
    assert hasattr(result, "plastic")
    assert hasattr(result, "substrate")
    assert "x" in result.activity


def test_reference_step_deterministic():
    """Test that reference_step is deterministic with fixed seed."""
    case = make_case(device="cpu", seed=42)
    result1 = reference_step(case)

    case2 = make_case(device="cpu", seed=42)
    result2 = reference_step(case2)

    act1 = result1.activations
    act2 = result2.activations

    assert act1 is not None and act2 is not None
    for a1, a2 in zip(act1, act2):
        torch.testing.assert_close(a1, a2)


def test_reference_step_different_seeds():
    """Test that different seeds produce different results."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    result1 = reference_step(case1)
    result2 = reference_step(case2)

    act1 = result1.activations
    act2 = result2.activations

    differ = False
    for a1, a2 in zip(act1, act2):
        if not torch.allclose(a1, a2):
            differ = True
            break
    assert differ
'''

    test_kernel_parity = f'''"""Kernel parity tests for {spec.name} algorithm."""

import pytest

from computronium.acceleration.parity import assert_parity
from {base_module} import (
    SPEC,
    make_case,
    reference_step,
)
from {base_module}.kernel import (
    is_available,
    step as kernel_step,
)


def test_kernel_parity():
    """Test that kernel output matches reference within tolerance."""
    if not is_available():
        pytest.skip("kernel not available")

    case = make_case(device="cpu", seed=0)

    reference_output = reference_step(case)
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_different_seeds():
    """Test kernel parity with different seeds."""
    if not is_available():
        pytest.skip("kernel not available")

    for seed in [1, 2, 42]:
        case = make_case(device="cpu", seed=seed)

        reference_output = reference_step(case)
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, SPEC.parity)
'''

    test_factory = f'''"""Factory tests for {spec.name} algorithm."""

from {base_module}.factory import create_{spec.name.lower().replace("-", "_").replace(" ", "_")}_mlp as create_factory
from {case_module} import make_case


def test_factory_creates_system():
    """Test that factory creates a valid system."""
    # Use a minimal config
    system = create_factory(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=2,
        lr=1e-3,
        device="cpu",
        backend="reference",
    )

    assert system is not None
    assert hasattr(system, "step")


def test_factory_with_case():
    """Test that factory system works with a test case."""
    case = make_case(device="cpu", seed=0)
    system = create_factory(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=2,
        lr=1e-3,
        device="cpu",
        backend="reference",
    )

    # Run a step
    result = system.step(case)
    assert result is not None
'''

    test_cases = f'''"""Case factory tests for {spec.name} algorithm."""

import torch

from {case_module} import (
    Case,
    make_case,
)


def test_make_case_returns_case():
    """Test that make_case returns a Case instance."""
    case = make_case(device="cpu", seed=0)

    assert isinstance(case, Case)
    assert isinstance(case.state, torch.Tensor)
    assert hasattr(case, "geometry")


def test_make_case_deterministic():
    """Test that make_case is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    torch.testing.assert_close(case1.state, case2.state)
    assert case1.config == case2.config


def test_make_case_different_seeds():
    """Test that different seeds produce different cases."""
    case1 = make_case(device="cpu", seed=0)
    case2 = make_case(device="cpu", seed=1)

    assert not torch.allclose(case1.state, case2.state)
'''

    return {
        "test_reference.py": test_reference,
        "test_kernel_parity.py": test_kernel_parity,
        "test_factory.py": test_factory,
        "test_cases.py": test_cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate test files from spec")
    parser.add_argument(
        "--spec", help="Spec ID (e.g., primitive.state_dynamics.energy_minimization)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Generate tests for all registered specs"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print files without writing"
    )
    parser.add_argument("--output-dir", help="Output directory (default: tests/)")
    args = parser.parse_args()

    if not args.spec and not args.all:
        parser.error("Either --spec or --all is required")

    specs_to_process = list(all_specs()) if args.all else [get_spec(args.spec)]

    output_base = Path(args.output_dir) if args.output_dir else Path("tests")

    for spec in specs_to_process:
        if spec.kind == "primitive":
            test_files = generate_primitive_tests(spec)
            axis = spec.axis or "unknown"
            # Get the primitive name from spec.id (primitive.axis.name)
            prim_name = spec.id.replace(f"primitive.{axis}.", "")
            test_dir = output_base / "primitives" / axis / prim_name
        else:
            test_files = generate_algorithm_tests(spec)
            # Extract algorithm name from spec.id (algorithm.xxx)
            algo_name = spec.id.replace("algorithm.", "")
            test_dir = output_base / "algorithms" / algo_name

        for filename, content in test_files.items():
            path = test_dir / filename
            if args.dry_run:
                print(f"=== {path} ===")
                print(content)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                print(f"Created: {path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
