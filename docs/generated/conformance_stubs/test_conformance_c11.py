"""Conformance test for C11: Replay and resume"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c11() -> None:
    """Verify C11 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_atomic_append_kill_proof.py::test_monotonic_seq_across_concurrent",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
