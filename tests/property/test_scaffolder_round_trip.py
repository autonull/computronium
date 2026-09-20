"""Scaffolder Self-Test (F2 from TODO32b) - Template Rendering Verification.

Verifies that scaffold_primitive.py and scaffold_algorithm.py templates
render correctly without errors. Full round-trip test (running generated tests)
requires a temporary repo copy and is implemented separately.
"""

# ruff: file-ignore[suspicious-subprocess-import]
import subprocess
import sys
from pathlib import Path


def test_primitive_scaffolder_dry_run() -> None:
    """Test that primitive scaffolder templates render without errors."""
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [
            sys.executable,
            "scripts/scaffold_primitive.py",
            "--axis",
            "state_dynamics",
            "--name",
            "test_dynamics",
            "--ontology-class",
            "TestDynamics",
            "--ontology-module",
            "computronium.ontology.dynamics",
            "--config-class",
            "StateDynamicsConfig.instantaneous",
            "--summary",
            "Test dynamics primitive",
            "--dry-run",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Primitive scaffolder dry-run failed: {result.stderr}"
    )

    # Verify all expected files are in output
    output = result.stdout
    expected_files = [
        "computronium/primitives/state_dynamics/test_dynamics/__init__.py",
        "computronium/primitives/state_dynamics/test_dynamics/spec.py",
        "computronium/primitives/state_dynamics/test_dynamics/reference.py",
        "computronium/primitives/state_dynamics/test_dynamics/kernel.py",
        "computronium/primitives/state_dynamics/test_dynamics/cases.py",
        "tests/primitives/state_dynamics/test_dynamics/test_reference.py",
        "tests/primitives/state_dynamics/test_dynamics/test_kernel_parity.py",
        "tests/primitives/state_dynamics/test_dynamics/test_cases.py",
    ]
    for f in expected_files:
        assert f in output, f"Expected file {f} not in dry-run output"

    print("Primitive scaffolder dry-run: all templates render correctly")


def test_algorithm_scaffolder_dry_run() -> None:
    """Test that algorithm scaffolder templates render without errors."""
    result = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
        [
            sys.executable,
            "scripts/scaffold_algorithm.py",
            "--name",
            "test_algorithm",
            "--family",
            "test_family",
            "--primitives",
            "energy_minimization,euclidean,thermodynamic_contrast",
            "--factory",
            "create_test_algorithm_mlp",
            "--summary",
            "Test algorithm",
            "--dry-run",
        ],
        cwd=Path.cwd(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"Algorithm scaffolder dry-run failed: {result.stderr}"
    )

    # Verify all expected files are in output
    output = result.stdout
    expected_files = [
        "computronium/algorithms/test_algorithm/__init__.py",
        "computronium/algorithms/test_algorithm/spec.py",
        "computronium/algorithms/test_algorithm/reference.py",
        "computronium/algorithms/test_algorithm/kernel.py",
        "computronium/algorithms/test_algorithm/cases.py",
        "computronium/algorithms/test_algorithm/factory.py",
        "tests/algorithms/test_algorithm/test_reference.py",
        "tests/algorithms/test_algorithm/test_kernel_parity.py",
        "tests/algorithms/test_algorithm/test_factory.py",
        "tests/algorithms/test_algorithm/test_cases.py",
    ]
    for f in expected_files:
        assert f in output, f"Expected file {f} not in dry-run output"

    print("Algorithm scaffolder dry-run: all templates render correctly")


def test_scaffolder_templates_exist() -> None:
    """Verify all template files exist."""
    template_dir = Path("scripts/templates")
    primitive_templates = [
        "primitive/init.py.j2",
        "primitive/spec.py.j2",
        "primitive/reference.py.j2",
        "primitive/kernel.py.j2",
        "primitive/cases.py.j2",
        "primitive/test_reference.py.j2",
        "primitive/test_kernel_parity.py.j2",
        "primitive/test_cases.py.j2",
    ]
    algorithm_templates = [
        "algorithm/init.py.j2",
        "algorithm/spec.py.j2",
        "algorithm/reference.py.j2",
        "algorithm/kernel.py.j2",
        "algorithm/cases.py.j2",
        "algorithm/factory.py.j2",
        "algorithm/test_reference.py.j2",
        "algorithm/test_kernel_parity.py.j2",
        "algorithm/test_factory.py.j2",
        "algorithm/test_cases.py.j2",
    ]

    for t in primitive_templates:
        assert (template_dir / t).exists(), f"Missing primitive template: {t}"

    for t in algorithm_templates:
        assert (template_dir / t).exists(), f"Missing algorithm template: {t}"

    print("All scaffolder templates exist")


if __name__ == "__main__":
    test_scaffolder_templates_exist()
    test_primitive_scaffolder_dry_run()
    test_algorithm_scaffolder_dry_run()
    print("All scaffolder self-tests passed!")
