"""Conformance test for C15: Unified artifact storage"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c15() -> None:
    """Verify C15 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_kill_during_atomic_append_no_partial_state",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
