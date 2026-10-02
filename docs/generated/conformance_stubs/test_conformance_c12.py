"""Conformance test for C12: Three-tier status model"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c12() -> None:
    """Verify C12 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_l2_fidelity",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
