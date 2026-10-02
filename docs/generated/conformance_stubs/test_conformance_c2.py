"""Conformance test for C2: Unified record schema"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c2() -> None:
    """Verify C2 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_dynamics_wiring_lock.py::test_registry_classes_round_trip_to_spec_from_spec",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
