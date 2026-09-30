"""Conformance test for C8: S1-S11 pipeline"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c8() -> None:
    """Verify C8 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_experiment_registries_wiring_lock.py::test_stage_registry_completeness",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
