"""Conformance test for C84: Report generator"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c84() -> None:
    """Verify C84 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_wp11_surface_lock.py::TestPublicExports::test_handoff_mentions_intents",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
