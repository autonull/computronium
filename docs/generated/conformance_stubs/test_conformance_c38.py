"""Conformance test for C38: Stratification guard"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c38() -> None:
    """Verify C38 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestComparisonGuards::test_same_hardware_class_for_walltime",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
