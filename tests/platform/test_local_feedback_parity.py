"""Parity lock — standalone AdaptiveFeedback ≡ X-ALI-001 probe re-projection."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import torch
from local_feedback import AdaptiveFeedback

PROBE = Path(__file__).resolve().parents[2] / "scripts" / "probes" / "x_ali_001.py"
FEEDBACK_SCALE = 0.1


def _load_probe():
    spec = importlib.util.spec_from_file_location("x_ali_001", PROBE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["x_ali_001"] = module
    spec.loader.exec_module(module)
    return module


def test_adaptive_feedback_reprojection_matches_probe() -> None:
    """Package update(lr=1) ≡ probe _adapt_feedback on identical weights."""
    probe = _load_probe()

    class _Credit:
        _feedback_weights: dict[str, torch.Tensor]

    for seed in range(3):
        torch.manual_seed(seed)
        credit = _Credit()
        credit._feedback_weights = {"layer": torch.randn(6, 5) * FEEDBACK_SCALE}
        w = torch.randn(6, 5)
        geometry = type("G", (), {"params": {"layer": w}})()

        package_fb = AdaptiveFeedback(5, 6, feedback_lr=1.0)
        package_fb.weight = credit._feedback_weights["layer"].clone()
        package_fb.update(w)

        probe._adapt_feedback(credit, geometry)

        expected = credit._feedback_weights["layer"]
        assert package_fb.weight.shape == expected.shape
        assert torch.allclose(package_fb.weight, expected, atol=1e-6)
        assert package_fb.weight.norm().item() == pytest_approx(
            FEEDBACK_SCALE * math.sqrt(30)
        )


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value, rel=1e-4)
