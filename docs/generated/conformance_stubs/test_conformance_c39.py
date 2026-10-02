"""Conformance test for C39: ICU calibration audit"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c39() -> None:
    """Verify C39 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_effect_size_guards",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
