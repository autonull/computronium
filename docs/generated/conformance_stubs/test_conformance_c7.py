"""Conformance test for C7: Legality engine"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c7() -> None:
    """Verify C7 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_legality_boundary_lock.py",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
