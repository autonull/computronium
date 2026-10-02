"""Conformance test for C48: Synthesis policy question-first"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c48() -> None:
    """Verify C48 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_wp11_surface_lock.py::TestQuestionFirst::test_spec_shape",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
