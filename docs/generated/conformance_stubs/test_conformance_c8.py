"""Conformance test for C8: S1-S11 pipeline"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c8() -> None:
    """Verify C8 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/acceptance/test_unified_kernel.py::TestU1_SynthesisPolicyPipeline::test_u1_synthesis_policy_end_to_end",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
