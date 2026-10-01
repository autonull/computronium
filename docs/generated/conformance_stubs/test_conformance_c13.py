"""Conformance test for C13: Claim eligibility predicates"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c13() -> None:
    """Verify C13 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_pass_verdict",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
