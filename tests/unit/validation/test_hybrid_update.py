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


def _cell(
    arm: str,
    gamma: float,
    *,
    train_biases: bool = False,
    seed: int = 21,
    acc: float = BASELINE,
    activations_mb: float | None = 210.0,
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


def _plan(
    *,
    reference_acc: float = 0.364,
    hybrid_acc: dict[float, float] | None = None,
    bias_gain: float = 0.0,
    head_only_acc: float = 0.201,
    sibling_accs: dict[float, float] | None = None,
) -> dict[tuple[str, float, bool, int], diagnostic.DiagnosticCell]:
    """The cells a fake measurement returns, keyed like the cell log."""
    accs = (
        hybrid_acc if hybrid_acc is not None else {0.05: 0.184, 0.3: 0.190, 1.0: 0.200}
    )
    sibling_accs = (
        sibling_accs
        if sibling_accs is not None
        else {0.05: 0.3995, 0.3: 0.4051, 1.0: 0.3837}
    )
    cells: dict[tuple[str, float, bool, int], diagnostic.DiagnosticCell] = {}
    for seed in diagnostic.DIAGNOSTIC_SEEDS:
        cells["backprop+ckpt", 0.05, False, seed] = _cell(
            "backprop+ckpt", 0.05, seed=seed, acc=reference_acc, activations_mb=453.0
        )
        base = accs[diagnostic.GAMMA_LADDER[0]]
        cells["hybrid", 0.05, False, seed] = _cell("hybrid", 0.05, seed=seed, acc=base)
        cells["hybrid", 0.05, True, seed] = _cell(
            "hybrid", 0.05, train_biases=True, seed=seed, acc=base + bias_gain
        )
    first = diagnostic.DIAGNOSTIC_SEEDS[0]
    last = diagnostic.DIAGNOSTIC_SEEDS[-1]
    best = max(accs, key=lambda gamma: accs[gamma])
    for gamma, acc in accs.items():
        cells["hybrid", gamma, False, first] = _cell(
            "hybrid", gamma, seed=first, acc=acc
        )
    cells["hybrid", best, False, last] = _cell(
        "hybrid", best, seed=last, acc=accs[best]
    )
    cells["hybrid", diagnostic.HEAD_ONLY_GAMMA, False, first] = _cell(
        "hybrid", diagnostic.HEAD_ONLY_GAMMA, seed=first, acc=head_only_acc
    )
    for gamma, acc in sibling_accs.items():
        cells[diagnostic.SIBLING_ARM, gamma, False, first] = _cell(
            diagnostic.SIBLING_ARM, gamma, seed=first, acc=acc
        )
    return cells


def _read(
    cells: dict[tuple[str, float, bool, int], diagnostic.DiagnosticCell],
) -> Callable[..., diagnostic.DiagnosticCell]:
    def cell(
        arm: str, *, gamma: float, train_biases: bool = False, seed: int
    ) -> diagnostic.DiagnosticCell:
        return cells[arm, gamma, train_biases, seed]

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
        return plan[arm, gamma, train_biases, seed]

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
    assert cells["hybrid", 0.3, False, 21] == first
    path.write_text(path.read_text(encoding="utf-8") * 2, encoding="utf-8")
    assert diagnostic.read_cells(path) == cells
    assert asdict(first)["arm"] == "hybrid"
