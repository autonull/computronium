"""Conformance test for C4: Measurement key deduplication"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c4() -> None:
    """Verify C4 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_append_with_artifacts_atomic_on_duplicate_measurement",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
