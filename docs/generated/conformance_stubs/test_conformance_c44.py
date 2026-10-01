"""Conformance test for C44: Surface CLI profiles"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c44() -> None:
    """Verify C44 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_wp11_surface_lock.py::TestDocumentedCommands::test_run_profiles_canonical_stages",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
