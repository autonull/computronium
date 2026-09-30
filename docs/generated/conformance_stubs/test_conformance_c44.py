"""Conformance test for C44: Run controller"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c44() -> None:
    """Verify C44 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_public_surface_lock.py::test_run_controller_pause_resume",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
