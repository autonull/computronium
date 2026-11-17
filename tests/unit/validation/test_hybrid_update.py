"""T6d's locks (TODO93 §8.1 ticket 12c).

The gate must read the floor from the reference minus delta, rank the two
update knobs on two seeds each, and name the mechanism that binds:
promote a knob that reaches the floor, record a real gain as a coordinate,
and refuse with the head-only control's reading. The report must be
rebuildable from the cell log without training a cell, and the cell plan
must price eleven cells at most with the baseline as the ladder's first
point.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING

import pytest
import torch

from computronium.validation import hybrid_update as diagnostic
from computronium.validation import memory_frontier as frontier

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

FLOOR = 0.354
BASELINE = 0.184


def _cell(  # ruff: ignore[too-many-arguments]
    arm: str,
    gamma: float,
    *,
    train_biases: bool = False,
    seed: int = 21,
    acc: float = BASELINE,
    activations_mb: float | None = 210.0,
    split_layer: int = diagnostic.REGISTERED_SPLIT,
    trunk_lr: float = 1.0,
    orthogonal_init: bool = False,
    learned_feedback: bool = False,
) -> diagnostic.DiagnosticCell:
    return diagnostic.DiagnosticCell(
        arm=arm,
        gamma=gamma,
        train_biases=train_biases,
        seed=seed,
        val_acc=acc,
        walltime_s=10.0,
        activations_mb=activations_mb,
        peak_mb=282.3,
        split_layer=split_layer,
        trunk_lr=trunk_lr,
        orthogonal_init=orthogonal_init,
        learned_feedback=learned_feedback,
    )


def _row(
    mechanism: str,
    *,
    gamma: float | None,
    acc: float,
    train_biases: bool = False,
    n: int = 2,
) -> diagnostic.MechanismRow:
    return diagnostic.MechanismRow(
        mechanism=mechanism,
        gamma=gamma,
        train_biases=train_biases,
        n=n,
        val_acc=acc,
        val_acc_sd=0.0,
        gain=acc - BASELINE,
        activations_mb=210.0,
        activation_ratio=0.46,
        floor=FLOOR,
    )


def _ladder(
    accs: dict[float, float] | None = None,
) -> tuple[diagnostic.DiagnosticCell, ...]:
    readings = accs if accs is not None else {0.05: 0.166, 0.3: 0.100, 1.0: 0.100}
    return tuple(_cell("hybrid", gamma, acc=acc) for gamma, acc in readings.items())


def _sibling(
    accs: dict[float, float] | None = None,
) -> tuple[diagnostic.DiagnosticCell, ...]:
    readings = accs if accs is not None else {0.05: 0.166, 0.3: 0.170, 1.0: 0.170}
    return tuple(
        _cell(diagnostic.SIBLING_ARM, gamma, acc=acc) for gamma, acc in readings.items()
    )


def _gate(
    *,
    reference_acc: float = 0.364,
    baseline_acc: float = BASELINE,
    rows: tuple[diagnostic.MechanismRow, ...] | None = None,
    ladder: tuple[diagnostic.DiagnosticCell, ...] | None = None,
    sibling: tuple[diagnostic.DiagnosticCell, ...] | None = None,
    head_only_acc: float = 0.201,
) -> diagnostic.UpdateVerdict:
    return diagnostic.update_gate(
        reference_acc=reference_acc,
        baseline_acc=baseline_acc,
        rows=rows
        if rows is not None
        else (
            _row("train_biases", gamma=None, acc=0.200, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.200),
        ),
        ladder=ladder if ladder is not None else _ladder(),
        sibling=sibling if sibling is not None else _sibling(),
        head_only_acc=head_only_acc,
        floor=FLOOR,
    )


def _key(arm: str, gamma: float, train_biases: bool, seed: int) -> diagnostic.CellKey:
    return (
        arm,
        gamma,
        train_biases,
        seed,
        diagnostic.REGISTERED_SPLIT,
        1.0,
        False,
        False,
    )


def _plan(
    *,
    reference_acc: float = 0.364,
    hybrid_acc: dict[float, float] | None = None,
    bias_gain: float = 0.0,
    head_only_acc: float = 0.201,
    sibling_accs: dict[float, float] | None = None,
) -> dict[diagnostic.CellKey, diagnostic.DiagnosticCell]:
    """The cells a fake measurement returns, keyed like the cell log."""
    accs = (
        hybrid_acc if hybrid_acc is not None else {0.05: 0.184, 0.3: 0.190, 1.0: 0.200}
    )
    sibling_accs = (
        sibling_accs
        if sibling_accs is not None
        else {0.05: 0.3995, 0.3: 0.4051, 1.0: 0.3837}
    )
    cells: dict[diagnostic.CellKey, diagnostic.DiagnosticCell] = {}
    for seed in diagnostic.DIAGNOSTIC_SEEDS:
        cells[_key("backprop+ckpt", 0.05, False, seed)] = _cell(
            "backprop+ckpt", 0.05, seed=seed, acc=reference_acc, activations_mb=453.0
        )
        base = accs[diagnostic.GAMMA_LADDER[0]]
        cells[_key("hybrid", 0.05, False, seed)] = _cell(
            "hybrid", 0.05, seed=seed, acc=base
        )
        cells[_key("hybrid", 0.05, True, seed)] = _cell(
            "hybrid", 0.05, train_biases=True, seed=seed, acc=base + bias_gain
        )
    first = diagnostic.DIAGNOSTIC_SEEDS[0]
    last = diagnostic.DIAGNOSTIC_SEEDS[-1]
    best = max(accs, key=lambda gamma: accs[gamma])
    for gamma, acc in accs.items():
        cells[_key("hybrid", gamma, False, first)] = _cell(
            "hybrid", gamma, seed=first, acc=acc
        )
    cells[_key("hybrid", best, False, last)] = _cell(
        "hybrid", best, seed=last, acc=accs[best]
    )
    cells[_key("hybrid", diagnostic.HEAD_ONLY_GAMMA, False, first)] = _cell(
        "hybrid", diagnostic.HEAD_ONLY_GAMMA, seed=first, acc=head_only_acc
    )
    for gamma, acc in sibling_accs.items():
        cells[_key(diagnostic.SIBLING_ARM, gamma, False, first)] = _cell(
            diagnostic.SIBLING_ARM, gamma, seed=first, acc=acc
        )
    return cells


def _read(
    cells: dict[diagnostic.CellKey, diagnostic.DiagnosticCell],
) -> Callable[..., diagnostic.DiagnosticCell]:
    def cell(
        arm: str, *, gamma: float, train_biases: bool = False, seed: int
    ) -> diagnostic.DiagnosticCell:
        return cells[_key(arm, gamma, train_biases, seed)]

    return cell


def test_the_gate_promotes_the_flag_before_the_scale() -> None:
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.360, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.358),
        )
    )
    assert gate.verdict == "promote"
    assert "train_biases" in gate.mechanism
    assert "0.354" in gate.reason
    assert "claim run" in gate.trigger


def test_the_gate_promotes_a_scale_that_reaches_the_floor() -> None:
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.200, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.355),
        )
    )
    assert gate.verdict == "promote"
    assert "feedback_scale=1" in gate.mechanism


def test_a_gain_without_the_floor_is_a_coordinate() -> None:
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.190, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.196),
        )
    )
    assert gate.verdict == "coordinate"
    assert "feedback_scale=1" in gate.mechanism
    assert "decoupled trunk learning rate" in gate.trigger


def test_a_gain_within_delta_of_the_baseline_moves_nothing() -> None:
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.189, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.189),
        )
    )
    assert gate.verdict == "refuse"


def test_the_sibling_control_names_the_composition_as_the_mechanism() -> None:
    """The same trunk rule, whole stack, beats the hybrid by 24 pp: the split."""
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.171, train_biases=True),
            _row("feedback_scale", gamma=0.05, acc=0.166),
        ),
        sibling=_sibling({0.05: 0.3995, 0.3: 0.4051, 1.0: 0.3837}),
        head_only_acc=0.149,
    )
    assert gate.verdict == "refuse"
    assert "composition" in gate.mechanism
    assert "0.405" in gate.reason
    assert "split_layer" in gate.trigger


def test_a_sibling_that_does_not_train_refuses_the_box() -> None:
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.189, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.189),
        ),
        head_only_acc=0.180,
    )
    assert gate.verdict == "refuse"
    assert "this box" in gate.mechanism
    assert "the box is the next variable" in gate.trigger


def test_the_ladder_shape_is_named_beside_the_sibling() -> None:
    """The refusal states where the hybrid's ladder collapses, not just that it does."""
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.191, train_biases=True),
            _row("feedback_scale", gamma=0.05, acc=0.166),
        ),
        sibling=_sibling({0.05: 0.3995, 0.3: 0.4051, 1.0: 0.3837}),
        head_only_acc=0.149,
    )
    assert gate.verdict == "refuse"
    assert (
        "does not collapse where the hybrid does (hybrid to 0.100 at gamma=0.3/1)"
        in (gate.reason)
    )
    assert "+0.7 pp" in gate.reason
    assert "decoupled trunk learning rate" in gate.trigger


def test_a_head_only_control_that_reaches_the_floor_refuses_the_trunk() -> None:
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.189, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.189),
        ),
        head_only_acc=0.356,
    )
    assert gate.verdict == "refuse"
    assert "destructive" in gate.mechanism
    assert "head alone reads 0.356" in gate.reason
    assert "direction check" in gate.trigger


def test_a_head_only_control_below_the_floor_refuses_the_head() -> None:
    gate = _gate(
        rows=(
            _row("train_biases", gamma=None, acc=0.189, train_biases=True),
            _row("feedback_scale", gamma=1.0, acc=0.189),
        ),
        sibling=_sibling({0.05: 0.3995, 0.3: 0.4051, 1.0: 0.3837}),
        head_only_acc=0.180,
    )
    assert gate.verdict == "refuse"
    assert "composition" in gate.mechanism
    assert "0.100 at gamma=0.3/1" in gate.reason
    assert "split's position" in gate.trigger


def test_a_reference_below_the_floor_invalidates_the_diagnostic() -> None:
    gate = _gate(reference_acc=0.200)
    assert gate.verdict == "invalid"
    assert "reference" in gate.mechanism
    assert "re-measure" in gate.trigger


def test_the_floor_is_the_reference_mean_minus_delta() -> None:
    plan = _plan(reference_acc=0.364)
    report = diagnostic._assemble(_read(plan), point=diagnostic.BOX)
    assert report.floor == pytest.approx(0.364 - diagnostic.DELTA)
    assert report.baseline_acc == pytest.approx(BASELINE)
    assert [row.n for row in report.rows] == [2, 2]
    assert report.rows[0].floor == pytest.approx(report.floor)
    assert report.rows[0].train_biases is True
    assert report.rows[1].gamma == pytest.approx(1.0)


def test_the_ladder_is_confirmed_on_the_second_seed() -> None:
    plan = _plan(hybrid_acc={0.05: 0.184, 0.3: 0.196, 1.0: 0.362})
    report = diagnostic._assemble(_read(plan), point=diagnostic.BOX)
    assert report.best_gamma == pytest.approx(1.0)
    assert report.confirmation.gamma == pytest.approx(1.0)
    assert report.confirmation.seed == diagnostic.DIAGNOSTIC_SEEDS[-1]
    assert report.verdict == "promote"
    assert "feedback_scale=1" in report.mechanism


def test_the_head_only_control_is_zero_modulation() -> None:
    frozen = frontier.FROZEN_LR["hybrid"]
    assert diagnostic.HEAD_ONLY_GAMMA == 0.0
    assert diagnostic.GAMMA_LADDER[0] == frontier.HYBRID_GAMMA
    assert float(diagnostic.LR) == pytest.approx(frozen)
    assert set(diagnostic.DIAGNOSTIC_SEEDS).isdisjoint(frontier.CLAIM_SEEDS)


def test_the_assembly_reads_each_knob_at_the_pilot_box() -> None:
    plan = _plan()
    seen: list[tuple[str, float, bool, int]] = []

    def cell(
        arm: str, *, gamma: float, train_biases: bool = False, seed: int
    ) -> diagnostic.DiagnosticCell:
        seen.append((arm, gamma, train_biases, seed))
        return plan[_key(arm, gamma, train_biases, seed)]

    report = diagnostic._assemble(cell, point=diagnostic.BOX)
    assert len(seen) == 14
    assert len(set(seen)) == 13
    assert {gamma for arm, gamma, flag, _ in seen if arm == "hybrid"} == {
        *diagnostic.GAMMA_LADDER,
        diagnostic.HEAD_ONLY_GAMMA,
    }
    assert report.point.depth == 8
    assert report.point.batch == 8192
    assert len(report.cells) == 13
    assert report.rows[1].activation_ratio == pytest.approx(210.0 / 453.0)


def test_the_json_carries_the_verdict_and_its_rulers(tmp_path: Path) -> None:
    report = diagnostic._assemble(_read(_plan()), point=diagnostic.BOX)
    path = diagnostic.write_report(report, tmp_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["verdict"] == report.verdict
    assert raw["floor"] == pytest.approx(report.floor, abs=1e-4)
    assert raw["point"]["lr"] == diagnostic.LR
    assert len(raw["rows"]) == 2
    assert {"mechanism", "reason", "trigger"} <= set(raw)
    markdown = (tmp_path / "hybrid_update.md").read_text(encoding="utf-8")
    assert report.verdict in markdown
    assert "0.354" in markdown


def test_the_cell_log_reuses_a_measured_cell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple[float, bool, int]] = []

    def fake_measure(  # ruff: ignore[too-many-arguments]
        arm: str,
        point: object,
        *,
        lr: float,
        seed: int,
        device: str,
        x_train: torch.Tensor,
        y_train: torch.Tensor,
        x_test: torch.Tensor,
        y_test: torch.Tensor,
        gamma: float,
        train_biases: bool,
        split_layer: int,
        trunk_lr: float,
        orthogonal_init: bool = False,
        learned_feedback: bool = False,
    ) -> frontier.ArmCell:
        calls.append((gamma, train_biases, seed))
        return frontier.ArmCell(
            arm=arm,
            seed=seed,
            depth=8,
            batch=8192,
            steps=200,
            lr=lr,
            val_acc=0.2,
            walltime_s=1.0,
            forward_equivalents=1.0,
            peak_mb=1.0,
            params_mb=1.0,
            optimizer_mb=None,
            activations_mb=1.0,
            auxiliary_mb=None,
            activation_share=0.8,
            binding=True,
        )

    monkeypatch.setattr(diagnostic, "measure_cell", fake_measure)
    path = tmp_path / "hybrid_update.cells.jsonl"
    log = diagnostic._CellLog(path)
    first = log.measure(
        "hybrid",
        gamma=0.3,
        seed=21,
        point=diagnostic.BOX,
        device="cuda",
        data=(torch.empty(0), torch.empty(0), torch.empty(0), torch.empty(0)),
    )
    again = log.measure(
        "hybrid",
        gamma=0.3,
        seed=21,
        point=diagnostic.BOX,
        device="cuda",
        data=(torch.empty(0), torch.empty(0), torch.empty(0), torch.empty(0)),
    )
    assert first == again
    assert calls == [(0.3, False, 21)]
    cells = diagnostic.read_cells(path)
    assert len(cells) == 1
    assert cells[_key("hybrid", 0.3, False, 21)] == first
    path.write_text(path.read_text(encoding="utf-8") * 2, encoding="utf-8")
    assert diagnostic.read_cells(path) == cells
    assert asdict(first)["arm"] == "hybrid"


def _split_key(
    arm: str, gamma: float, seed: int, *, split_layer: int, trunk_lr: float = 1.0
) -> diagnostic.CellKey:
    return (arm, gamma, False, seed, split_layer, trunk_lr, False, False)


def _split_row(
    mechanism: str,
    *,
    split_layer: int = diagnostic.READOUT_SPLIT,
    trunk_lr: float = 1.0,
    acc: float = BASELINE,
    n: int = 2,
) -> diagnostic.SplitRow:
    return diagnostic.SplitRow(
        mechanism=mechanism,
        split_layer=split_layer,
        trunk_lr=trunk_lr,
        n=n,
        val_acc=acc,
        val_acc_sd=0.0,
        gain=acc - BASELINE,
        activations_mb=210.0,
        activation_ratio=0.46,
        floor=FLOOR,
    )


def _split_gate(
    *,
    reference_acc: float = 0.364,
    rows: tuple[diagnostic.SplitRow, ...] | None = None,
    ladder: tuple[diagnostic.DiagnosticCell, ...] | None = None,
) -> diagnostic.UpdateVerdict:
    return diagnostic.split_gate(
        reference_acc=reference_acc,
        baseline_acc=BASELINE,
        rows=rows
        if rows is not None
        else (
            _split_row("split_layer", acc=0.190),
            _split_row("trunk_lr", trunk_lr=0.3, acc=0.190, n=1),
            _split_row("trunk_lr", acc=0.190),
            _split_row("trunk_lr", trunk_lr=3.0, acc=0.190, n=1),
        ),
        ladder=ladder
        if ladder is not None
        else tuple(
            _cell("hybrid", diagnostic.HYBRID_GAMMA, split_layer=7, trunk_lr=trunk_lr)
            for trunk_lr in diagnostic.TRUNK_LR_LADDER
        ),
        floor=FLOOR,
    )


def _split_plan(
    *,
    reference_acc: float = 0.364,
    readout_acc: float = 0.190,
    trunk_accs: dict[float, float] | None = None,
) -> dict[diagnostic.CellKey, diagnostic.DiagnosticCell]:
    accs = trunk_accs if trunk_accs is not None else {0.3: 0.190, 3.0: 0.190}
    cells: dict[diagnostic.CellKey, diagnostic.DiagnosticCell] = {}
    readout = diagnostic.READOUT_SPLIT
    for seed in diagnostic.DIAGNOSTIC_SEEDS:
        cells[_key("backprop+ckpt", 0.05, False, seed)] = _cell(
            "backprop+ckpt", 0.05, seed=seed, acc=reference_acc, activations_mb=453.0
        )
        cells[_key("hybrid", 0.05, False, seed)] = _cell(
            "hybrid", 0.05, seed=seed, acc=BASELINE
        )
        cells[_split_key("hybrid", 0.05, seed, split_layer=readout)] = _cell(
            "hybrid", 0.05, seed=seed, acc=readout_acc, split_layer=readout
        )
    first, last = diagnostic.DIAGNOSTIC_SEEDS[0], diagnostic.DIAGNOSTIC_SEEDS[-1]
    points = {**dict.fromkeys(diagnostic.TRUNK_LR_LADDER, readout_acc), **accs}
    for trunk_lr, acc in accs.items():
        cells[
            _split_key("hybrid", 0.05, first, split_layer=readout, trunk_lr=trunk_lr)
        ] = _cell(
            "hybrid",
            0.05,
            seed=first,
            acc=acc,
            split_layer=readout,
            trunk_lr=trunk_lr,
        )
    best = max(diagnostic.TRUNK_LR_LADDER, key=lambda trunk_lr: points[trunk_lr])
    if best != 1.0:
        cells[_split_key("hybrid", 0.05, last, split_layer=readout, trunk_lr=best)] = (
            _cell(
                "hybrid",
                0.05,
                seed=last,
                acc=points[best],
                split_layer=readout,
                trunk_lr=best,
            )
        )
    return cells


def _read_split(
    cells: dict[diagnostic.CellKey, diagnostic.DiagnosticCell],
) -> Callable[..., diagnostic.DiagnosticCell]:
    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        split_layer: int = diagnostic.REGISTERED_SPLIT,
        trunk_lr: float = 1.0,
        seed: int,
    ) -> diagnostic.DiagnosticCell:
        if split_layer == diagnostic.REGISTERED_SPLIT:
            return cells[_key(arm, gamma, train_biases, seed)]
        return cells[
            arm, gamma, train_biases, seed, split_layer, trunk_lr, False, False
        ]

    return cell


def test_the_split_ladder_is_the_last_linear_and_the_registered_head() -> None:
    assert diagnostic.REGISTERED_SPLIT == -1
    assert 2 * (diagnostic.BOX.depth - 1) == diagnostic.READOUT_SPLIT
    assert diagnostic.SPLIT_LADDER == (-1, 14)
    assert diagnostic.TRUNK_LR_LADDER[1] == 1.0
    assert set(diagnostic.TRUNK_LR_LADDER) == {0.3, 1.0, 3.0}


def test_the_split_gate_promotes_a_readout_head_that_reaches_the_floor() -> None:
    gate = _split_gate(
        rows=(
            _split_row("split_layer", acc=0.360),
            _split_row("trunk_lr", acc=0.200),
        )
    )
    assert gate.verdict == "promote"
    assert "head's depth" in gate.mechanism
    assert "0.354" in gate.reason
    assert "claim run" in gate.trigger


def test_the_split_gate_promotes_a_trunk_step_that_reaches_the_floor() -> None:
    gate = _split_gate(
        rows=(
            _split_row("split_layer", acc=0.186),
            _split_row("trunk_lr", trunk_lr=0.3, acc=0.200, n=1),
            _split_row("trunk_lr", acc=0.358),
            _split_row("trunk_lr", trunk_lr=3.0, acc=0.210, n=1),
        )
    )
    assert gate.verdict == "promote"
    assert "decoupled trunk step" in gate.mechanism
    assert "trunk_lr=1" in gate.mechanism


def test_a_trunk_step_gain_without_the_floor_is_a_coordinate() -> None:
    gate = _split_gate(
        rows=(
            _split_row("split_layer", acc=0.186),
            _split_row("trunk_lr", acc=0.196),
        )
    )
    assert gate.verdict == "coordinate"
    assert "trunk_lr=1" in gate.mechanism
    assert "next trunk-step edge" in gate.trigger


def test_a_split_that_moves_nothing_refuses_the_direction() -> None:
    gate = _split_gate(
        rows=(
            _split_row("split_layer", acc=0.189),
            _split_row("trunk_lr", trunk_lr=0.3, acc=0.189, n=1),
            _split_row("trunk_lr", acc=0.189),
        )
    )
    assert gate.verdict == "refuse"
    assert "direction" in gate.mechanism
    assert "0.3/1/3" in gate.reason
    assert "learned_feedback" in gate.trigger


def test_the_split_gate_invalidates_a_reference_below_the_floor() -> None:
    gate = _split_gate(reference_acc=0.200)
    assert gate.verdict == "invalid"
    assert "reference" in gate.mechanism


def test_the_split_assembly_prices_the_cells_at_the_pilot_box() -> None:
    plan = _split_plan(trunk_accs={0.3: 0.190, 3.0: 0.192})
    seen: list[diagnostic.CellKey] = []

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        split_layer: int = diagnostic.REGISTERED_SPLIT,
        trunk_lr: float = 1.0,
        seed: int,
    ) -> diagnostic.DiagnosticCell:
        seen.append((arm, gamma, train_biases, seed, split_layer, trunk_lr))
        return _read_split(plan)(
            arm,
            gamma=gamma,
            train_biases=train_biases,
            split_layer=split_layer,
            trunk_lr=trunk_lr,
            seed=seed,
        )

    report = diagnostic._assemble_split(cell, point=diagnostic.BOX)
    assert len(seen) == 9
    assert len(set(seen)) == 9
    assert len(report.cells) == 9
    assert [row.n for row in report.rows] == [2, 1, 2, 2]
    assert report.verdict in {"refuse", "coordinate", "promote"}
    assert report.confirmation.seed == diagnostic.DIAGNOSTIC_SEEDS[-1]
    assert report.confirmation.split_layer == diagnostic.READOUT_SPLIT
    assert report.rows[0].activation_ratio == pytest.approx(210.0 / 453.0)


def test_the_split_json_carries_the_verdict_and_its_rulers(tmp_path: Path) -> None:
    report = diagnostic._assemble_split(
        _read_split(_split_plan(trunk_accs={0.3: 0.190, 3.0: 0.361})),
        point=diagnostic.BOX,
    )
    path = diagnostic.write_split_report(report, tmp_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["verdict"] == "promote"
    assert "trunk_lr" in raw["mechanism"]
    assert raw["point"]["lr"] == diagnostic.LR
    assert len(raw["rows"]) == 4
    assert {"mechanism", "reason", "trigger", "cells"} <= set(raw)
    markdown = (tmp_path / "split_position.md").read_text(encoding="utf-8")
    assert "T6e" in markdown
    assert "0.354" in markdown
    assert "trunk lr" in markdown


def _direction_key(
    arm: str,
    gamma: float,
    seed: int,
    *,
    orthogonal_init: bool = False,
    learned_feedback: bool = False,
) -> diagnostic.CellKey:
    return (
        arm,
        gamma,
        False,
        seed,
        diagnostic.REGISTERED_SPLIT,
        1.0,
        orthogonal_init,
        learned_feedback,
    )


def _direction_row(
    mechanism: str,
    *,
    acc: float = BASELINE,
    n: int = 2,
) -> diagnostic.DirectionRow:
    return diagnostic.DirectionRow(
        mechanism=mechanism,
        n=n,
        val_acc=acc,
        val_acc_sd=0.0,
        gain=acc - BASELINE,
        activations_mb=210.0,
        activation_ratio=1.06,
        floor=FLOOR,
    )


def _direction_gate(
    *,
    reference_acc: float = 0.364,
    rows: tuple[diagnostic.DirectionRow, ...] | None = None,
) -> diagnostic.UpdateVerdict:
    return diagnostic.direction_gate(
        reference_acc=reference_acc,
        baseline_acc=BASELINE,
        rows=rows
        if rows is not None
        else (
            _direction_row("orthogonal", acc=0.190),
            _direction_row("learned", acc=0.190),
        ),
        floor=FLOOR,
    )


def _direction_plan(
    *,
    reference_acc: float = 0.364,
    orthogonal_acc: float = 0.190,
    learned_acc: float = 0.190,
) -> dict[diagnostic.CellKey, diagnostic.DiagnosticCell]:
    cells: dict[diagnostic.CellKey, diagnostic.DiagnosticCell] = {}
    for seed in diagnostic.DIAGNOSTIC_SEEDS:
        cells[_direction_key("backprop+ckpt", 0.05, seed)] = _cell(
            "backprop+ckpt", 0.05, seed=seed, acc=reference_acc, activations_mb=453.0
        )
        cells[_direction_key("hybrid", 0.05, seed)] = _cell(
            "hybrid", 0.05, seed=seed, acc=BASELINE
        )
    for seed in diagnostic.DIAGNOSTIC_SEEDS:
        cells[_direction_key("hybrid", 0.05, seed, orthogonal_init=True)] = _cell(
            "hybrid", 0.05, seed=seed, acc=orthogonal_acc, orthogonal_init=True
        )
        cells[_direction_key("hybrid", 0.05, seed, learned_feedback=True)] = _cell(
            "hybrid", 0.05, seed=seed, acc=learned_acc, learned_feedback=True
        )
    best = "orthogonal" if orthogonal_acc >= learned_acc else "learned"
    cells[
        _direction_key(
            "hybrid",
            0.05,
            diagnostic.CONFIRMATION_SEED,
            orthogonal_init=best == "orthogonal",
            learned_feedback=best == "learned",
        )
    ] = _cell(
        "hybrid",
        0.05,
        seed=diagnostic.CONFIRMATION_SEED,
        acc=max(orthogonal_acc, learned_acc),
        orthogonal_init=best == "orthogonal",
        learned_feedback=best == "learned",
    )
    return cells


def _read_direction(
    cells: dict[diagnostic.CellKey, diagnostic.DiagnosticCell],
) -> Callable[..., diagnostic.DiagnosticCell]:
    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        orthogonal_init: bool = False,
        learned_feedback: bool = False,
        seed: int,
    ) -> diagnostic.DiagnosticCell:
        return cells[
            _direction_key(
                arm,
                gamma,
                seed,
                orthogonal_init=orthogonal_init,
                learned_feedback=learned_feedback,
            )
        ]

    return cell


def test_the_direction_ladder_is_two_fixes_at_the_registered_scale() -> None:
    assert diagnostic.DIRECTION_LADDER == (
        ("orthogonal", True, False),
        ("learned", False, True),
    )
    assert diagnostic.GAMMA_LADDER[0] == 0.05
    first, last = diagnostic.DIAGNOSTIC_SEEDS
    assert first != last


def test_the_direction_gate_promotes_a_learned_fit_that_reaches_the_floor() -> None:
    gate = _direction_gate(
        rows=(
            _direction_row("orthogonal", acc=0.190),
            _direction_row("learned", acc=0.362),
        )
    )
    assert gate.verdict == "promote"
    assert "learned feedback matrix" in gate.mechanism
    assert "0.354" in gate.reason
    assert "claim run" in gate.trigger


def test_the_direction_gate_promotes_an_orthogonal_rotation_that_reaches_the_floor() -> (
    None
):
    gate = _direction_gate(
        rows=(
            _direction_row("orthogonal", acc=0.360),
            _direction_row("learned", acc=0.190),
        )
    )
    assert gate.verdict == "promote"
    assert "orthogonal feedback matrix" in gate.mechanism


def test_a_direction_gain_without_the_floor_is_a_coordinate() -> None:
    gate = _direction_gate(
        rows=(
            _direction_row("orthogonal", acc=0.190),
            _direction_row("learned", acc=0.205),
        )
    )
    assert gate.verdict == "coordinate"
    assert "learned direction" in gate.mechanism
    assert "next edge" in gate.trigger


def test_a_direction_that_moves_nothing_queues_the_geometry() -> None:
    gate = _direction_gate(
        rows=(
            _direction_row("orthogonal", acc=0.188),
            _direction_row("learned", acc=0.186),
        )
    )
    assert gate.verdict == "refuse"
    assert "trunk's geometry" in gate.mechanism
    assert "0.188/0.186" in gate.reason
    assert "residual trunk" in gate.trigger


def test_the_direction_gate_invalidates_a_reference_below_the_floor() -> None:
    gate = _direction_gate(reference_acc=0.200)
    assert gate.verdict == "invalid"
    assert "reference" in gate.mechanism


def test_the_direction_assembly_prices_the_cells_at_the_pilot_box() -> None:
    plan = _direction_plan(learned_acc=0.361)
    seen: list[diagnostic.CellKey] = []

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        orthogonal_init: bool = False,
        learned_feedback: bool = False,
        seed: int,
    ) -> diagnostic.DiagnosticCell:
        seen.append(
            _direction_key(
                arm,
                gamma,
                seed,
                orthogonal_init=orthogonal_init,
                learned_feedback=learned_feedback,
            )
        )
        return _read_direction(plan)(
            arm,
            gamma=gamma,
            train_biases=train_biases,
            orthogonal_init=orthogonal_init,
            learned_feedback=learned_feedback,
            seed=seed,
        )

    report = diagnostic._assemble_direction(cell, point=diagnostic.BOX)
    assert len(seen) == 9
    assert len(set(seen)) == 9
    assert len(report.cells) == 9
    assert report.verdict == "promote"
    assert [row.n for row in report.rows] == [2, 2]
    assert report.confirmation.learned_feedback
    assert report.confirmation.seed == diagnostic.CONFIRMATION_SEED
    assert report.rows[0].activation_ratio == pytest.approx(210.0 / 453.0)


def test_the_direction_json_carries_the_outcome_and_its_rulers(
    tmp_path: Path,
) -> None:
    report = diagnostic._assemble_direction(
        _read_direction(_direction_plan(orthogonal_acc=0.361)), point=diagnostic.BOX
    )
    path = diagnostic.write_direction_report(report, tmp_path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["triage"].startswith("defect probe")
    assert raw["verdict"] == "promote"
    assert "orthogonal" in raw["mechanism"]
    assert raw["point"]["lr"] == diagnostic.LR
    assert len(raw["rows"]) == 2
    assert {"mechanism", "reason", "trigger", "cells"} <= set(raw)
    directions = {cell["learned_feedback"] for cell in raw["cells"]}
    assert directions == {True, False}
    markdown = (tmp_path / "direction.md").read_text(encoding="utf-8")
    assert "T6f" in markdown
    assert "0.354" in markdown
    assert "orthogonal" in markdown


def test_no_report_prints_a_verdict(tmp_path: Path) -> None:
    """The triage is mandatory: a report states a box, never a verdict."""
    reports = {
        "hybrid_update.md": diagnostic._markdown(
            diagnostic._assemble(_read(_plan()), point=diagnostic.BOX)
        ),
        "split_position.md": diagnostic._split_markdown(
            diagnostic._assemble_split(_read_split(_split_plan()), point=diagnostic.BOX)
        ),
        "direction.md": diagnostic._direction_markdown(
            diagnostic._assemble_direction(
                _read_direction(_direction_plan()), point=diagnostic.BOX
            )
        ),
    }
    for name, markdown in reports.items():
        assert "Gate outcome" in markdown, name
        assert "Verdict" not in markdown, name
    direction = diagnostic._assemble_direction(
        _read_direction(_direction_plan()), point=diagnostic.BOX
    )
    path = diagnostic.write_direction_report(direction, tmp_path / "dir")
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["triage"].startswith("defect probe")
    assert "Triage." in (tmp_path / "dir" / "direction.md").read_text(encoding="utf-8")
