"""Conformance test for C35: Transfer provenance"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c35() -> None:
    """Verify C35 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_transfer_mode_enum",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
