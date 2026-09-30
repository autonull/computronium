"""Conformance test for C83: Surface CLI dispatcher"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c83() -> None:
    """Verify C83 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_public_surface_lock.py::test_surface_cli_profiles",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
