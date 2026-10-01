"""Conformance test for C52: No global singletons"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c52() -> None:
    """Verify C52 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_kernel_isolation_lock.py::TestRunScopedState::test_engine_singleton_removed",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
