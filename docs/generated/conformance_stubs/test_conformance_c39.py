"""Conformance test for C39: I(C,U) leakage audit"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c39() -> None:
    """Verify C39 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::test_icu_calibration_audit",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
