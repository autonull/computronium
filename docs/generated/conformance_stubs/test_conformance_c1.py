"""Conformance test for C1: Six-axis coordinate space"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c1() -> None:
    """Verify C1 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_experiment_registries_wiring_lock.py::test_all_registries_dict_completeness",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
