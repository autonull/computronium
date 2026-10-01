"""Conformance test for C40: Alert predicates"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c40() -> None:
    """Verify C40 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestAlertPredicates::test_alert_on_resource_exhaustion",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
