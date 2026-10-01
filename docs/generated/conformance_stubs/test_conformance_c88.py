"""Conformance test for C88: Probe conventions"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c88() -> None:
    """Verify C88 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_wp11_surface_lock.py::TestAlertsAndControl::test_operator_intent_factory",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
