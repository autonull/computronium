"""Conformance test for C9: Eight-policy catalog"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c9() -> None:
    """Verify C9 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_sampler_lock.py::TestTheRunReachesThePolicy::test_the_spec_reaches_a_learning_policy",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
