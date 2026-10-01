"""Conformance test for C36: Assessment procedure versioning"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c36() -> None:
    """Verify C36 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_status_requires_assessment_procedure_version",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
