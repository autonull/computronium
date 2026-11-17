"""The D2 gate must promote only on a paired interval at matched walltime.

The screen's verdict is a predicate the repository evaluates: a memory arm
within 1 pp of the same rule on digital, at no more than 1.2x its walltime
and with less device state, promotes to the retention rung; a measured
disadvantage refuses with the constraint that binds; an interval that
crosses the margin at ``n_max`` is a coordinate result; a control below the
floor invalidates the run. The int8 QDQ control prices the representation
with no device model, and the walltime prices the programming budget.
"""

from __future__ import annotations

import json
from dataclasses import asdict

import pytest
import torch

from computronium import QuantizedSubstrate, SubstrateConfig
from computronium.validation.matched_substrate import (
    D2_HIDDEN_DIMS,
    EXTENSION_MARGIN,
    EXTENSION_SEEDS,
    PAIRED_SEEDS,
    QDQ_ARM,
    SETTLE_LADDER,
    MatchedPair,
    _gate,
    _pair,
    _screen_adopts,
    replay_matched_comparison,
)
from computronium.validation.substrate_ladder import (
    DEVICE_BITS,
    HIDDEN_DIMS,
    LEARNING_CONTROL,
    PARITY_DELTA,
    SubstrateCell,
    _build_system,
    device_state,
)


def _cell(
    arm: str,
    acc: float | None = 0.910,
    *,
    seed: int = 71,
    settle: int = 20,
    stage: str = "matched",
    time_s: float = 10.0,
    refused: bool = False,
) -> SubstrateCell:
    return SubstrateCell(
        arm=arm,
        stage="control" if arm == LEARNING_CONTROL else stage,
        seed=seed,
        lr=1e-2,
        max_steps=settle,
        device="cpu",
        val_acc=None if refused else acc,
        train_acc=None if refused else acc,
        device_state_bytes=1000,
        device_state_per_weight=4.0,
        train_state_bytes=2048,
        params_mb=1.0,
        optimizer_mb=1.0,
        activations_mb=1.0,
        steps=0 if refused else 600,
        time_s=time_s,
        forward_equivalents=2.0 * settle if not refused else None,
        note="refused" if refused else "",
        refused=refused,
    )


def _pair_at(
    seed: int,
    *,
    rule: float = 0.912,
    mem: float = 0.910,
    qdq: float = 0.902,
    control: float = 0.923,
    rule_time: float = 10.0,
    mem_time: float = 10.5,
    refused: bool = False,
) -> MatchedPair:
    return _pair(
        seed,
        20,
        rule=_cell("digital", rule, seed=seed, time_s=rule_time),
        memristive=_cell(
            "memristive", mem, seed=seed, time_s=mem_time, refused=refused
        ),
        qdq=_cell(QDQ_ARM, qdq, seed=seed, time_s=rule_time),
        control=_cell(LEARNING_CONTROL, control, seed=seed),
    )


def _pairs(
    *, mem_gaps: tuple[float, ...], rule: float = 0.912, **kwargs
) -> tuple[MatchedPair, ...]:
    return tuple(
        _pair_at(seed, rule=rule, mem=rule + gap, **kwargs)
        for seed, gap in zip(PAIRED_SEEDS, mem_gaps, strict=True)
    )


def test_parity_within_one_pp_at_matched_walltime_promotes_to_the_retention_rung() -> (
    None
):
    gate = _gate(
        pairs=_pairs(mem_gaps=(-0.003, -0.001, 0.0, -0.002, 0.001)),
        settle=SETTLE_LADDER[-1],
    )
    assert gate.verdict == "promote"
    assert "D3" in gate.reason
    assert gate.mean_gap is not None and gate.mean_gap > -PARITY_DELTA


def test_a_disadvantage_beyond_one_pp_refuses_with_its_measured_mechanism() -> None:
    gate = _gate(
        pairs=_pairs(mem_gaps=(-0.03, -0.025, -0.02, -0.028, -0.022)),
        settle=SETTLE_LADDER[0],
    )
    assert gate.verdict == "refuse"
    assert "trails" in gate.reason
    assert gate.mean_gap is not None and gate.mean_gap < -PARITY_DELTA


def test_a_cost_above_the_walltime_limit_refuses() -> None:
    gate = _gate(
        pairs=_pairs(mem_gaps=(0.0,) * len(PAIRED_SEEDS), mem_time=13.5),
        settle=SETTLE_LADDER[0],
    )
    assert gate.verdict == "refuse"
    assert "walltime" in gate.reason
    assert gate.mean_walltime_ratio is not None
    assert gate.mean_walltime_ratio > 1.2


def test_an_interval_that_crosses_the_margin_is_a_coordinate_result() -> None:
    gate = _gate(
        pairs=_pairs(mem_gaps=(0.02, -0.03, 0.02, -0.03, 0.02)),
        settle=SETTLE_LADDER[0],
    )
    assert gate.verdict == "coordinate"
    assert "n_max" in gate.reason
    assert gate.gap_ci95 is not None and gate.gap_ci95[0] < -PARITY_DELTA


def test_a_control_below_the_floor_invalidates_the_run() -> None:
    gate = _gate(
        pairs=_pairs(mem_gaps=(0.0,) * len(PAIRED_SEEDS), control=0.40),
        settle=SETTLE_LADDER[0],
    )
    assert gate.verdict == "invalid-learning-control"
    assert "not the substrate" in gate.reason


def test_a_refused_constrained_cell_is_a_refusal_with_a_trigger() -> None:
    gate = _gate(
        pairs=_pairs(mem_gaps=(0.0,) * len(PAIRED_SEEDS), refused=True),
        settle=SETTLE_LADDER[0],
    )
    assert gate.verdict == "refuse"
    assert "trigger" in gate.reason


def test_the_programming_budget_is_named_when_it_binds() -> None:
    gate = _gate(
        pairs=_pairs(mem_gaps=(0.0,) * len(PAIRED_SEEDS), qdq=0.911, mem_time=30.0),
        settle=SETTLE_LADDER[0],
    )
    assert gate.verdict == "refuse"
    assert "programming budget" in gate.reason
    assert "3.00x" in gate.reason


def test_the_int8_width_is_named_when_it_binds() -> None:
    gate = _gate(
        pairs=_pairs(mem_gaps=(0.0,) * len(PAIRED_SEEDS), qdq=0.892),
        settle=SETTLE_LADDER[0],
    )
    assert gate.verdict == "promote"
    assert "the int8 width binds" in gate.reason


def test_the_extension_is_adopted_only_when_both_screen_seeds_gain() -> None:
    def screen(high: tuple[float, float]) -> tuple[SubstrateCell, ...]:
        cells = []
        for seed, gain in zip(EXTENSION_SEEDS, high, strict=True):
            for steps in SETTLE_LADDER:
                acc = 0.90 + (gain if steps == SETTLE_LADDER[-1] else 0.0)
                cells.append(
                    _cell("memristive", acc, seed=seed, settle=steps, stage="screen")
                )
        return tuple(cells)

    gain = EXTENSION_MARGIN + 0.002
    assert _screen_adopts(screen((gain, gain)))
    assert not _screen_adopts(screen((gain, 0.0)))
    assert not _screen_adopts(screen((gain, -0.01)))


def test_the_qdq_control_is_an_int8_width_with_a_float_forward() -> None:
    substrate = QuantizedSubstrate()
    assert substrate.config.precision == "float32"
    weights = torch.tensor(
        [[0.10, -0.20, 0.30], [0.50, -0.40, 0.25]], requires_grad=True
    )
    quantised = substrate._qdq(weights)
    assert torch.unique(quantised).numel() <= QuantizedSubstrate.LEVELS + 1
    assert quantised.dtype == torch.float32
    quantised.sum().backward()
    assert weights.grad is not None
    assert torch.allclose(weights.grad, torch.ones_like(weights))


def test_an_int8_cast_is_refused_as_the_qdq_control() -> None:
    with pytest.raises(ValueError, match="does not quantise"):
        QuantizedSubstrate(SubstrateConfig.digital(precision="int8"))


def test_the_qdq_device_state_is_eight_bits_and_below_the_digital_rule() -> None:
    assert DEVICE_BITS[QDQ_ARM] == 8
    assert DEVICE_BITS[QDQ_ARM] < DEVICE_BITS["digital"]
    qdq_system = _build_system(QDQ_ARM, seed=71, lr=1e-2, max_steps=20)
    digital_system = _build_system("digital", seed=71, lr=1e-2, max_steps=20)
    qdq_bytes, qdq_per_weight = device_state(qdq_system, QDQ_ARM)
    digital_bytes, digital_per_weight = device_state(digital_system, "digital")
    assert 0 < qdq_bytes < digital_bytes
    assert 1.0 <= qdq_per_weight < 1.001
    assert digital_per_weight == 4.0


def test_the_box_is_two_times_d1s_width() -> None:
    assert (2 * HIDDEN_DIMS[0],) == D2_HIDDEN_DIMS


def test_the_cell_log_replays_the_paired_gate(tmp_path) -> None:
    cells = []
    for seed in EXTENSION_SEEDS:
        for steps in SETTLE_LADDER:
            cells.append(
                _cell("memristive", 0.90, seed=seed, settle=steps, stage="screen")
            )
    pairs = _pairs(mem_gaps=(-0.002, 0.0, 0.001, -0.001, 0.0))
    for pair in pairs:
        cells.extend((pair.rule, pair.memristive, pair.qdq, pair.control))
    progress = tmp_path / "matched.cells.jsonl"
    progress.write_text(
        "\n".join(json.dumps(asdict(cell)) for cell in cells) + "\n",
        encoding="utf-8",
    )
    report = replay_matched_comparison(progress=progress)
    assert report.verdict == "promote"
    assert [p.seed for p in report.pairs] == list(PAIRED_SEEDS)
    assert report.mean_gap is not None and report.mean_gap > -PARITY_DELTA
    assert report.settle == SETTLE_LADDER[0]
