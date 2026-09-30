"""Conformance test for C52: Run-scoped ICU/Reasoning"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c52() -> None:
    """Verify C52 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_experiment_registries_wiring_lock.py::test_no_global_singletons",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
