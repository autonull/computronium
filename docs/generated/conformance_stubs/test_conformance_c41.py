"""Conformance test for C41: Promotion predicates"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c41() -> None:
    """Verify C41 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_promoted_requires_l2_maturity",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
