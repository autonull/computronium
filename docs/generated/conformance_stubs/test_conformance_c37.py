"""Conformance test for C37: Comparison guard"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c37() -> None:
    """Verify C37 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestComparisonGuards::test_matched_cost_comparison",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
