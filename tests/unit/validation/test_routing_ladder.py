"""The B1 routing gate must promote only on a measured, repeated growth.

The screen's verdict is a predicate the repository evaluates: a gap that
clears the pre-registered margin on both seeds promotes the track to its
matched pair; a flat or falling gap refuses it with a trigger; a reference
that misses its own finite difference, or an arm that does not train,
invalidates the run instead. The gradient fixture is the stub detector: an
STE implemented as the plain soft relaxation would read a zero gap and fail
here.
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest
import torch

from computronium.validation.routing_ladder import (
    FLOOR,
    GROWTH_DELTA,
    REFERENCE_TOL,
    TEMP_LADDER_DEPTH,
    TEMPERATURES,
    RoutingCell,
    RoutingNet,
    _gradient_gap,
    _objective,
    _verdict,
    read_cells,
    replay_routing,
    run_routing_ladder,
)


def _cell(
    *,
    stage: str = "depth",
    depth: int = 1,
    temperature: float = 1.0,
    seed: int = 51,
    acc: float = 0.95,
    gap: float = 0.50,
    reference: float = 0.01,
    normal: float = 0.10,
) -> RoutingCell:
    return RoutingCell(
        stage=stage,
        depth=depth,
        temperature=temperature,
        seed=seed,
        end_task_acc=acc,
        router_acc=0.40,
        ste_gap=gap,
        reference_gap=reference,
        ste_norm=normal,
        reference_norm=normal,
        time_s=1.0,
    )


def _ladder(
    gaps: tuple[float, float, float, float], *, temperature: float = 0.25
) -> tuple[RoutingCell, ...]:
    return tuple(
        _cell(depth=depth, gap=gap, temperature=temperature)
        for depth, gap in zip((1, 2, 4, 8), gaps, strict=True)
    )


def _setup(
    *,
    seed_gaps: tuple[float, ...] = (0.50, 0.50, 0.50, 0.50),
    confirmation_gaps: tuple[float, float] = (0.50, 0.50),
    deep_acc: float = 0.95,
) -> tuple[tuple[RoutingCell, ...], tuple[RoutingCell, ...], tuple[RoutingCell, ...]]:
    temperatures = tuple(
        _cell(
            stage="temperature",
            depth=TEMP_LADDER_DEPTH,
            temperature=temperature,
            gap=gap,
            normal=normal,
        )
        for temperature, gap, normal in zip(
            TEMPERATURES, (0.40, 0.45, 0.50), (0.30, 0.20, 0.10), strict=True
        )
    )
    ladder = _ladder(seed_gaps)
    if deep_acc != 0.95:
        ladder = (*ladder[:-1], _cell(depth=8, acc=deep_acc))
    confirmation = tuple(
        _cell(stage="confirmation", depth=depth, temperature=0.25, seed=52, gap=gap)
        for depth, gap in zip((1, 8), confirmation_gaps, strict=True)
    )
    return temperatures, ladder, confirmation


def _gate(
    temperatures: tuple[RoutingCell, ...],
    ladder: tuple[RoutingCell, ...],
    confirmation: tuple[RoutingCell, ...],
) -> tuple[str, str]:
    return _verdict(
        temperature_cells=temperatures,
        depth_ladder=ladder,
        confirmation=confirmation,
    )


def test_flat_depth_ladder_refuses_with_a_trigger() -> None:
    verdict, reason = _gate(*_setup())
    assert verdict == "refuse"
    assert "growth margin" in reason


def test_growth_on_two_seeds_promotes_to_b2() -> None:
    temperatures, ladder, confirmation = _setup(
        seed_gaps=(0.40, 0.55, 0.70, 0.80), confirmation_gaps=(0.42, 0.62)
    )
    verdict, reason = _gate(temperatures, ladder, confirmation)
    assert verdict == "promote"
    assert "compounds" in reason


def test_growth_on_one_seed_is_provisional() -> None:
    temperatures, ladder, confirmation = _setup(
        seed_gaps=(0.40, 0.55, 0.70, 0.80), confirmation_gaps=(0.42, 0.44)
    )
    verdict, reason = _gate(temperatures, ladder, confirmation)
    assert verdict == "refuse"
    assert "-0.02" in reason or "+0.02" in reason


def test_a_rising_growth_below_the_margin_refuses() -> None:
    temperatures, ladder, confirmation = _setup(
        seed_gaps=(0.50, 0.51, 0.52, 0.52),
        confirmation_gaps=(0.50, 0.50 + GROWTH_DELTA / 2),
    )
    verdict, _ = _gate(temperatures, ladder, confirmation)
    assert verdict == "refuse"


def test_reference_mismatch_invalidates_the_run() -> None:
    temperatures, ladder, _ = _setup()
    broken = (*ladder[:-1], _cell(depth=8, reference=REFERENCE_TOL + 0.01))
    verdict, reason = _gate(temperatures, broken, ())
    assert verdict == "invalid-instrument"
    assert "finite difference" in reason


def test_chance_level_temperature_cell_invalidates_the_run() -> None:
    _, ladder, confirmation = _setup()
    collapsed = tuple(
        _cell(stage="temperature", depth=2, temperature=t, acc=FLOOR - 0.1)
        for t in TEMPERATURES
    )
    verdict, reason = _gate(collapsed, ladder, confirmation)
    assert verdict == "invalid-learning"
    assert "does not train" in reason


def test_chance_level_deep_cell_invalidates_the_growth_measurement() -> None:
    temperatures, ladder, confirmation = _setup(deep_acc=FLOOR - 0.1)
    verdict, reason = _gate(temperatures, ladder, confirmation)
    assert verdict == "invalid-learning"
    assert "not a trained arm" in reason


def test_ste_gradient_differs_from_its_soft_reference() -> None:
    """The stub detector: a soft relaxation in place of STE reads a zero gap."""
    torch.manual_seed(7)
    net = RoutingNet(depth=2, temperature=1.0)
    generator = torch.Generator().manual_seed(3)
    x = torch.randn(64, 8, generator=generator)
    y = torch.randint(0, 4, (64,), generator=generator)

    def grads(mode: str) -> list[torch.Tensor]:
        net.set_mode(mode)
        return list(torch.autograd.grad(_objective(net, x, y), net.router_parameters()))

    ste, reference = grads("ste"), grads("soft")
    for ste_block, reference_block in zip(ste, reference, strict=True):
        difference = (ste_block - reference_block).norm()
        assert (difference / reference_block.norm()).item() > 0.1


def test_reference_matches_its_own_finite_difference() -> None:
    """The instrument control: the smoothed gradient tracks its objective."""
    torch.manual_seed(11)
    net = RoutingNet(depth=2, temperature=1.0)
    generator = torch.Generator().manual_seed(5)
    x = torch.randn(64, 8, generator=generator)
    y = torch.randint(0, 4, (64,), generator=generator)
    _, reference_gap, _, _ = _gradient_gap(net, x, y)
    assert reference_gap <= REFERENCE_TOL


def test_replay_recomputes_the_gate_from_the_cell_log(tmp_path) -> None:
    temperatures, ladder, confirmation = _setup(
        seed_gaps=(0.40, 0.55, 0.70, 0.80), confirmation_gaps=(0.42, 0.62)
    )
    log = tmp_path / "routing.cells.jsonl"
    rows = [json.dumps(asdict(c)) for c in (*temperatures, *ladder, *confirmation)]
    log.write_text("\n".join((*rows, rows[0])) + "\n", encoding="utf-8")
    report = replay_routing(progress=log)
    assert report.verdict == "promote"
    assert len(report.cells) == len(temperatures) + len(ladder)
    assert len(read_cells(log)) == len(temperatures) + len(ladder) + len(confirmation)


def test_resume_does_not_re_run_measured_cells(tmp_path, monkeypatch) -> None:
    temperatures, ladder, confirmation = _setup(
        seed_gaps=(0.40, 0.55, 0.70, 0.80), confirmation_gaps=(0.42, 0.62)
    )
    log = tmp_path / "routing.cells.jsonl"
    log.write_text(
        "\n".join(
            json.dumps(asdict(c)) for c in (*temperatures, *ladder, *confirmation)
        )
        + "\n",
        encoding="utf-8",
    )

    def _fail(**_: object) -> RoutingCell:
        raise AssertionError("a measured cell was re-run")

    monkeypatch.setattr("computronium.validation.routing_ladder._run_cell", _fail)
    report = run_routing_ladder(device="cpu", progress=log)
    assert report.verdict == "promote"
    assert len(report.depth_ladder) == 4


@pytest.mark.parametrize("gap", [0.0, 0.5, 1.5])
def test_gap_is_a_relative_norm(gap: float) -> None:
    """A cell's gap is its own number, not rescaled by the ladder."""
    cell = _cell(gap=gap)
    assert cell.ste_gap == pytest.approx(gap)
