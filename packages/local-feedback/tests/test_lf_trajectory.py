"""Trajectory tests — local trainer descent quality and X-ALI-001 verdict."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import torch
from local_feedback import (
    AdaptiveFeedback,
    FixedFeedback,
    LocalFeedbackTrainer,
    late_half_mean,
)


def _load_demo():
    demo_path = (
        Path(__file__).resolve().parents[1] / "examples" / "local_feedback_demo.py"
    )
    spec = importlib.util.spec_from_file_location("local_feedback_demo", demo_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_arm = _load_demo().run_arm


def _trainer(adaptive: bool, seed: int = 0) -> LocalFeedbackTrainer:
    gen = torch.Generator().manual_seed(seed)
    from torch import nn

    model = nn.Sequential()
    hidden = nn.Linear(16, 32)
    readout = nn.Linear(32, 4)
    with torch.no_grad():
        hidden.weight.normal_(0.0, 0.3, generator=gen)
        hidden.bias.zero_()
        readout.weight.normal_(0.0, 0.3, generator=gen)
        readout.bias.zero_()
    model.add_module("hidden", hidden)
    model.add_module("readout", readout)
    fb: AdaptiveFeedback = (
        AdaptiveFeedback(32, 4, feedback_lr=1.0, generator=gen)
        if adaptive
        else FixedFeedback(32, 4, generator=gen)
    )
    return LocalFeedbackTrainer(model, fb, lr=0.02)


def test_trainer_descends() -> None:
    trainer = _trainer(adaptive=False)
    x, y = _task(0)
    first = trainer.train_step(x, y)
    for _ in range(10):
        trainer.train_step(x, y)
    last = trainer.train_step(x, y)
    assert last.loss_after < first.loss_before


def _task(seed: int, n: int = 64) -> tuple[torch.Tensor, torch.Tensor]:
    gen = torch.Generator().manual_seed(seed + 500)
    basis = torch.randn(16, 4, generator=gen) * 2.0
    x = torch.randn(n, 16, generator=gen)
    y = (x @ basis + torch.randn(n, 4, generator=gen) * 0.5).argmax(-1)
    return x, y


def test_feedback_alignment_converges_to_one() -> None:
    trainer = _trainer(adaptive=True)
    x = torch.randn(64, 16)
    y = torch.randint(0, 4, (64,))
    for _ in range(30):
        trainer.train_step(x, y)
    assert trainer.feedback.feedback_alignment(
        trainer.readout.weight.detach()
    ) == pytest.approx(1.0, abs=1e-3)


def test_fixed_alignment_stays_low() -> None:
    trainer = _trainer(adaptive=False)
    x = torch.randn(64, 16)
    y = torch.randint(0, 4, (64,))
    for _ in range(30):
        trainer.train_step(x, y)
    assert trainer.feedback.feedback_alignment(trainer.readout.weight.detach()) < 0.9


def test_adaptive_late_ipn_greater_than_fixed_all_seeds() -> None:
    """The X-ALI-001 verdict statistic on the standalone form."""
    for seed in range(3):
        fixed = run_arm(seed, adaptive=False)
        adaptive = run_arm(seed, adaptive=True)
        assert adaptive["late_ipn"] > fixed["late_ipn"]  # type: ignore[operator]


def test_run_arm_deterministic() -> None:
    a = run_arm(1, adaptive=True)
    b = run_arm(1, adaptive=True)
    assert a["losses"] == b["losses"]  # type: ignore[comparison-overlap]


def test_late_half_mean_statistic() -> None:
    assert late_half_mean([1, 2, 3, 4]) == pytest.approx(3.5)
    assert late_half_mean([5]) == pytest.approx(5.0)


def test_trainer_requires_two_linears() -> None:
    from torch import nn

    with pytest.raises(ValueError, match="two Linear"):
        LocalFeedbackTrainer(nn.Linear(4, 4), AdaptiveFeedback(4, 4), lr=0.01)
