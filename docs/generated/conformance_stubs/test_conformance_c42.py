"""Conformance test for C42: Effect size protocol"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c42() -> None:
    """Verify C42 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::TestEffectSizeProtocol::test_effect_size_reports_cohens_d_with_ci",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
