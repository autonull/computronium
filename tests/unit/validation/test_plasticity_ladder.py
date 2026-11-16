"""The C1 and C2 gates must promote only on the pre-registered condition.

The ladder's verdict is a predicate the repository evaluates: a local arm at
the floor on two seeds promotes; at the floor on one seed it refuses; a
control below the floor invalidates the run rather than promoting the
treatment. C2 adds retention: a forgetting win must clear δ at a matched
per-step cost, a flat top rung closes the track at its saturation point, and a
cell log replays the gate without re-running measured cells. Removing any of
those checks fails a test here.
"""

from __future__ import annotations

import json
from dataclasses import asdict

from computronium.validation.plasticity_ladder import (
    FLOOR,
    LadderCell,
    _retention_verdict,
    _verdict,
    replay_consolidation,
    run_consolidation_ladder,
)


def _cell(arm: str, acc: float, seed: int = 0) -> LadderCell:
    return LadderCell(
        stage="plasticity",
        arm=arm,
        knob=0.01,
        seed=seed,
        mean_final_acc=acc,
        last_task_acc=acc,
        backward_transfer=0.0,
        avg_forgetting=0.0,
        state_mb=0.0,
        time_s=0.0,
        accuracy_matrix=(),
    )


def test_two_seeds_above_floor_promote() -> None:
    best = {"local": _cell("local", FLOOR + 0.05), "backprop": _cell("backprop", 0.8)}
    verdict, _ = _verdict(best, (_cell("local", FLOOR + 0.01, seed=42),))
    assert verdict == "promote"


def test_confirmation_seed_below_floor_refuses() -> None:
    best = {"local": _cell("local", FLOOR + 0.05), "backprop": _cell("backprop", 0.8)}
    verdict, _ = _verdict(best, (_cell("local", FLOOR - 0.05, seed=42),))
    assert verdict == "refuse"


def test_control_at_chance_invalidates_the_run() -> None:
    best = {"local": _cell("local", FLOOR + 0.05), "backprop": _cell("backprop", 0.5)}
    verdict, _ = _verdict(best, (_cell("local", FLOOR + 0.01, seed=42),))
    assert verdict == "invalid-control"


def _retention_cell(
    arm: str,
    acc: float,
    forgetting: float,
    *,
    knob: float,
    seed: int = 41,
    time_s: float = 220.0,
) -> LadderCell:
    return LadderCell(
        stage="consolidation",
        arm=arm,
        knob=knob,
        seed=seed,
        mean_final_acc=acc,
        last_task_acc=acc,
        backward_transfer=-forgetting,
        avg_forgetting=forgetting,
        state_mb=0.0,
        time_s=time_s,
        accuracy_matrix=(),
    )


def _retention_setup(
    local_forgetting: float = 0.04,
    control_forgetting: float = 0.10,
    *,
    local_time: float = 220.0,
    top: tuple[float, float] | None = None,
) -> tuple[tuple[LadderCell, ...], dict[str, LadderCell], tuple[LadderCell, ...]]:
    ladder = (
        _retention_cell(
            "backprop_ewc", 0.90, control_forgetting, knob=10.0, time_s=200.0
        ),
        _retention_cell(
            "local_ewc", 0.90, local_forgetting, knob=10.0, time_s=local_time
        ),
    )
    cells = ladder
    if top is not None:
        acc, forgetting = top
        cells = (*ladder, _retention_cell("local_ewc", acc, forgetting, knob=100.0))
    best = {c.arm: c for c in ladder}
    confirmation = (
        _retention_cell("local_ewc", 0.90, local_forgetting, knob=10.0, seed=42),
    )
    return cells, best, confirmation


def test_retention_win_promotes_to_c2b() -> None:
    cells, best, confirmation = _retention_setup()
    verdict, reason = _retention_verdict(cells, best, confirmation, 0.001)
    assert verdict == "promote"
    assert "forgets" in reason


def test_retention_win_with_control_below_floor_invalidates() -> None:
    cells, best, confirmation = _retention_setup(control_forgetting=0.5)
    best["backprop_ewc"] = _retention_cell("backprop_ewc", FLOOR - 0.05, 0.5, knob=10.0)
    verdict, _ = _retention_verdict(cells, best, confirmation, 0.001)
    assert verdict == "invalid-control"


def test_retention_undefined_when_local_cannot_learn() -> None:
    cells, best, confirmation = _retention_setup()
    best["local_ewc"] = _retention_cell("local_ewc", FLOOR - 0.05, 0.0, knob=10.0)
    verdict, reason = _retention_verdict(cells, best, confirmation, 0.001)
    assert verdict == "refuse"
    assert "retention is undefined" in reason


def test_confirmation_seed_below_floor_refuses_the_retention_claim() -> None:
    cells, best, _ = _retention_setup()
    below = (_retention_cell("local_ewc", FLOOR - 0.05, 0.04, knob=10.0, seed=42),)
    verdict, _ = _retention_verdict(cells, best, below, 0.001)
    assert verdict == "refuse"


def test_cost_mismatch_invalidates_the_comparison() -> None:
    cells, best, confirmation = _retention_setup(local_time=400.0)
    verdict, reason = _retention_verdict(cells, best, confirmation, 0.001)
    assert verdict == "invalid-cost"
    assert "2.00x" in reason


def test_flat_top_rung_closes_c_at_the_saturation_point() -> None:
    cells, best, confirmation = _retention_setup(
        local_forgetting=0.095, top=(0.89, 0.090)
    )
    verdict, reason = _retention_verdict(cells, best, confirmation, 0.001)
    assert verdict == "close"
    assert "lambda=100" in reason


def test_improving_top_rung_is_not_saturation() -> None:
    cells, best, confirmation = _retention_setup(
        local_forgetting=0.095, top=(0.89, 0.060)
    )
    verdict, _ = _retention_verdict(cells, best, confirmation, 0.001)
    assert verdict == "refuse"


def test_a_rigid_top_rung_is_not_saturation() -> None:
    cells, best, confirmation = _retention_setup(
        local_forgetting=0.095, top=(FLOOR - 0.05, 0.0)
    )
    verdict, reason = _retention_verdict(cells, best, confirmation, 0.001)
    assert verdict == "refuse"
    assert "not saturated" in reason


def test_replay_recomputes_the_gate_from_the_cell_log(tmp_path) -> None:
    cells, _, confirmation = _retention_setup()
    log = tmp_path / "consolidation.cells.jsonl"
    rows = [json.dumps(asdict(c)) for c in (*cells, *confirmation)]
    log.write_text("\n".join((*rows, rows[0])) + "\n", encoding="utf-8")
    report = replay_consolidation(progress=log, lr=0.001)
    assert report.verdict == "promote"
    assert len(report.cells) == 2
    assert len(report.confirmation) == 1


def test_resume_does_not_re_run_measured_cells(tmp_path, monkeypatch) -> None:
    accs = {1.0: 0.90, 10.0: 0.91, 100.0: 0.89}
    ladder = [
        _retention_cell(arm, accs[knob], forgetting, knob=knob, time_s=300.0)
        for knob in (1.0, 10.0, 100.0)
        for arm, forgetting in (("backprop_ewc", 0.10), ("local_ewc", 0.04))
    ]
    confirmation = [
        _retention_cell(arm, 0.90, forgetting, knob=10.0, seed=42, time_s=300.0)
        for arm, forgetting in (("backprop_ewc", 0.10), ("local_ewc", 0.04))
    ]
    log = tmp_path / "consolidation.cells.jsonl"
    log.write_text(
        "\n".join(json.dumps(asdict(c)) for c in (*ladder, *confirmation)) + "\n",
        encoding="utf-8",
    )

    def _fail(**_: object) -> LadderCell:
        raise AssertionError("a measured cell was re-run")

    monkeypatch.setattr("computronium.validation.plasticity_ladder._run_cell", _fail)
    report = run_consolidation_ladder(lr=0.001, progress=log)
    assert report.verdict == "promote"
    assert len(report.cells) == 6
