"""Conformance test for C58: Multi-objective Pareto"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c58() -> None:
    """Verify C58 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::test_multi_objective_pareto",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
