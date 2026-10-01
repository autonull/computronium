"""Conformance test for C51: Prior single source"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c51() -> None:
    """Verify C51 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_wp10_learning_integration_lock.py::TestPriorSingleSource::test_ruler_tasks_resolve_via_registry",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
