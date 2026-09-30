"""Conformance test for C12: Three-tier status model"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c12() -> None:
    """Verify C12 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::test_three_tier_status_model",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
