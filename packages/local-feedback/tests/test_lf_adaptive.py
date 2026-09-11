"""Unit tests — AdaptiveFeedback re-projection math and semantics."""

from __future__ import annotations

import math

import pytest
import torch
from local_feedback import AdaptiveFeedback, FixedFeedback, matched_norm


def test_reprojection_matches_x_ali_001_formula() -> None:
    torch.manual_seed(0)
    fb = AdaptiveFeedback(8, 4, feedback_lr=1.0, feedback_scale=0.1)
    w = torch.randn(4, 8)
    expected = (w / w.norm()) * 0.1 * math.sqrt(32)
    fb.update(w)
    assert torch.allclose(fb.weight, expected)


def test_expected_norm_preserved() -> None:
    torch.manual_seed(0)
    fb = AdaptiveFeedback(16, 4, feedback_lr=1.0, feedback_scale=0.1)
    target = fb.expected_norm
    for _ in range(5):
        fb.update(torch.randn(4, 16))
    assert fb.weight.norm().item() == pytest.approx(target, rel=1e-4)


def test_ema_blend() -> None:
    torch.manual_seed(0)
    fb = AdaptiveFeedback(8, 4, feedback_lr=0.5, feedback_scale=0.1)
    w = torch.randn(4, 8)
    start = fb.weight.clone()
    target = (w / w.norm()) * 0.1 * math.sqrt(32)
    fb.update(w)
    assert torch.allclose(fb.weight, start + 0.5 * (target - start))


def test_update_frequency_skips_steps() -> None:
    fb = AdaptiveFeedback(8, 4, feedback_lr=1.0, update_frequency=3)
    w = torch.randn(4, 8)
    start = fb.weight.clone()
    fb.update(w)  # step 1 — skipped (1 % 3 != 0)
    assert torch.equal(fb.weight, start)
    fb.update(w)  # step 2 — skipped
    assert torch.equal(fb.weight, start)
    fb.update(w)  # step 3 — applied
    expected = (w / w.norm()) * fb.feedback_scale * math.sqrt(32)
    assert torch.allclose(fb.weight, expected)


def test_zero_weight_is_noop() -> None:
    fb = AdaptiveFeedback(8, 4, feedback_lr=1.0)
    start = fb.weight.clone()
    fb.update(torch.zeros(4, 8))
    assert torch.equal(fb.weight, start)


def test_project_shape() -> None:
    fb = AdaptiveFeedback(8, 4)
    error = torch.randn(7, 4)
    assert fb.project(error).shape == (7, 8)


def test_fixed_feedback_never_moves() -> None:
    gen = torch.Generator().manual_seed(3)
    fb = FixedFeedback(8, 4, generator=gen)
    twin = FixedFeedback(8, 4, generator=torch.Generator().manual_seed(3))
    start = fb.weight.clone()
    fb.update(torch.randn(4, 8))
    assert torch.equal(fb.weight, start)
    assert matched_norm(fb, twin) == pytest.approx(1.0)


def test_invalid_init_rejected() -> None:
    with pytest.raises(ValueError, match="init"):
        AdaptiveFeedback(8, 4, init="zeros")  # type: ignore[arg-type]


def test_deterministic_under_generator() -> None:
    a = AdaptiveFeedback(8, 4, generator=torch.Generator().manual_seed(7))
    b = AdaptiveFeedback(8, 4, generator=torch.Generator().manual_seed(7))
    assert torch.equal(a.weight, b.weight)
