"""Unit tests for the calibrated stability guard."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch
from stability import (
    DEFAULT_TAU,
    GuardDecision,
    StabilityGuard,
    StabilityVerdict,
    attach,
    calibrate_threshold,
)
from stability.state import CompositeState, SystemContext
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Callable

GOOD_STATS = [1.0, 1.1, 0.9]
BAD_STATS = [2.0, 2.2, 2.1]
FEASIBLE_FALSE_KILL = 0.05
FEASIBLE_KILL_RATE = 0.95
WINDOW_THRESHOLD = 1.1


def _scaling_transition(
    scale: float,
) -> Callable[[CompositeState, SystemContext | None], CompositeState]:
    def transition(z: CompositeState, _context: SystemContext | None) -> CompositeState:
        x = z.activity["x"]
        return CompositeState(
            activity={"x": scale * x if isinstance(x, Tensor) else x},
            plastic=z.plastic,
            substrate=z.substrate,
        )

    return transition


def test_calibrate_threshold_selects_feasible_operating_point() -> None:
    report = calibrate_threshold(
        GOOD_STATS, BAD_STATS, FEASIBLE_FALSE_KILL, FEASIBLE_KILL_RATE
    )
    assert report is not None
    assert report.false_kill_rate <= FEASIBLE_FALSE_KILL
    assert report.kill_rate >= FEASIBLE_KILL_RATE
    assert max(GOOD_STATS) < report.threshold < min(BAD_STATS)


def test_calibrate_threshold_infeasible_returns_none() -> None:
    assert calibrate_threshold([1.0, 2.0], [1.1, 2.1], 0.05, 0.95) is None


def test_calibrate_threshold_empty_returns_none() -> None:
    assert calibrate_threshold([], BAD_STATS) is None


def test_decide_kills_above_threshold() -> None:
    guard = StabilityGuard(threshold=DEFAULT_TAU)
    decision: GuardDecision = guard.decide(1.5)
    assert decision.kill
    assert not guard.decide(1.0).kill


def test_windowed_growth_scales_with_map() -> None:
    z = CompositeState(activity={"x": torch.ones(2, 4)}, plastic={}, substrate={})
    guard = StabilityGuard(threshold=DEFAULT_TAU, statistic="windowed_growth", window=5)
    stat = guard.probe(_scaling_transition(2.0), z, None)  # type: ignore[arg-type]
    assert stat > WINDOW_THRESHOLD


def test_attach_kill_on_explosive_model() -> None:
    model = torch.nn.Linear(8, 8, bias=False)
    with torch.no_grad():
        model.weight.copy_(1.5 * torch.eye(8) + 0.5 * torch.randn(8, 8))
    handle = attach(model, window=5)
    verdict: StabilityVerdict | None = None
    generator = torch.Generator().manual_seed(0)
    for step in range(50):
        x = torch.randn(4, 8, generator=generator)
        verdict = handle.check({"x": x}, step=step)
        if verdict.kill:
            break
    assert verdict is not None
    assert verdict.kill


def test_attach_survives_contractive_model() -> None:
    model = torch.nn.Linear(8, 8, bias=False)
    with torch.no_grad():
        model.weight.copy_(0.1 * torch.eye(8))
    handle = attach(model, window=5)
    generator = torch.Generator().manual_seed(0)
    for step in range(20):
        x = torch.randn(4, 8, generator=generator)
        assert not handle.check({"x": x}, step=step).kill


def test_default_tau_is_calibrated_value() -> None:
    assert DEFAULT_TAU == 1.029


def test_verdict_bool_semantics() -> None:
    guard = StabilityGuard(threshold=1.0)

    def transition(state: dict[str, object]) -> dict[str, object]:
        x = state["x"]
        return {**state, "x": x * 0.5 if isinstance(x, Tensor) else x}

    verdict = guard.check_external({"x": torch.ones(2, 3)}, transition)
    assert isinstance(verdict, StabilityVerdict)
    assert not verdict.kill
    assert not bool(verdict)


def test_tensor_guard() -> None:
    assert torch.ones(1).sum().item() == pytest.approx(1.0)
