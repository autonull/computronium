"""Conformance test for C53: Reasoning persistence"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c53() -> None:
    """Verify C53 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_provenance_with_data_origin",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
