"""Tests for stable-matrix helpers (Phase 6A)."""

from __future__ import annotations

import pytest
import torch
from stability.matrices import jordan_block, rotation, verify_spectrum


def test_jordan_block_is_nonnormal_transient() -> None:
    checks = verify_spectrum(jordan_block(1.05))
    assert float(checks["sigma_max"]) > 1.0
    assert float(checks["rho"]) == pytest.approx(1.05)


def test_rotation_is_normal_marginal() -> None:
    checks = verify_spectrum(rotation(0.3))
    assert checks["rho_ok"] is True
    assert abs(float(checks["sigma_max"]) - 1.0) < 1e-4


def test_jordan_block_structure() -> None:
    J = jordan_block(1.05)
    assert J.shape == (4, 4)
    assert torch.equal(J, 1.05 * torch.eye(4) + torch.diag(torch.ones(3), 1))
