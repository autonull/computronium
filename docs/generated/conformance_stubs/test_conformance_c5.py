"""Conformance test for C5: Cell key grouping"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c5() -> None:
    """Verify C5 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_concurrent_append_dedup_by_measurement_key",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
