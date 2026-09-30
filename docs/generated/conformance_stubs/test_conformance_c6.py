"""Conformance test for C6: Schema versioning"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c6() -> None:
    """Verify C6 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_experiment_registries_wiring_lock.py::test_schema_versioning_fail_closed",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
