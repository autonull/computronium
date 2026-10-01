"""Conformance test for C87: Gallery lock"""

# This test is generated from the capability registry.
# Do not edit manually - regenerate via codegen.

import pytest
from computronium.experiment.surface.conformance import run_verifying_test


def test_conformance_c87() -> None:
    """Verify C87 capability via its verifying test."""
    passed, output, duration = run_verifying_test(
        "tests/integration/test_gallery_lock.py::test_figure_lock",
        timeout_seconds=120,
    )
    assert passed, f"Verifying test failed: {output}"
