"""Conformance test for C36: Transfer provenance tracking"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c36() -> None:
    """Verify C36 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_statistical_protocol_lock.py::test_transfer_provenance",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
