"""Conformance test for C48: Question-first entry"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c48() -> None:
    """Verify C48 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_public_surface_lock.py::test_synthesis_policy_question_first",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
