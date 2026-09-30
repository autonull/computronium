"""Conformance test for C34: Assessment procedure versioning"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c34() -> None:
    """Verify C34 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::test_assessment_procedure_versioning",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
