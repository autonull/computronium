"""Conformance test for C33: Reproducibility class tracking"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c33() -> None:
    """Verify C33 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_status_requires_reproducibility_class",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
