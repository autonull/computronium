"""Conformance test for C10: Evidence-driven allocation"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c10() -> None:
    """Verify C10 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_allocator_promotion.py::TestEvidenceDrivenAllocation::test_first_observation_nominates_next_fidelity",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
