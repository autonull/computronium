"""Conformance test for C47: Currency lock flags"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c47() -> None:
    """Verify C47 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_conformance_harness.py::TestFlagProjectionLock::test_flag_projection_totality",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
