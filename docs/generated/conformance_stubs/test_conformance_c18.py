"""Conformance test for C18: Surrogate policy wrapper"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c18() -> None:
    """Verify C18 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_training_split_excludes_calibration_test",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
