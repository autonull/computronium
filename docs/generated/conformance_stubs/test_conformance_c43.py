"""Conformance test for C43: Budget tier system"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c43() -> None:
    """Verify C43 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestEffectSizeProtocol::test_budget_tier_matching_required",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
