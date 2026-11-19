"""Lock: the interaction slice has power (TODO95 S3).

The census measured one axis at a time; the interaction slice asks which two
axes change each other. This lock pins the pair (variance over bound rows,
never a swapped or refused row), the 2×2 residual, the one-seed screen versus
the three-seed confirm, and the refusal of a slice whose control sits inside
the bar. A pair without power is marked, never reported.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from computronium.experiment import sec_loop
from computronium.experiment.kernel.evaluate import CellEvaluation
from computronium.experiment.sec_census import MAP_VERSION, build_census
from computronium.experiment.sec_interaction import (
    INTERACTION_SEEDS,
    axis_spreads,
    bound_rows,
    interaction_effect,
    plan_slice,
)
from computronium.experiment.sec_loop import legal_levels

if TYPE_CHECKING:
    from pathlib import Path

_BASE = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "euclidean",
    "task": "mnist",
    "fidelity": "L0",
    "batch_size": 32,
    "batch_limit": 375,
    "epochs": 1,
}


def _row(primitive: str, axis: str, val_acc: float, binding: str = "bound", **extra):
    return {
        "primitive": primitive,
        "axis": axis,
        "status": "measured",
        "binding": binding,
        "swapped": False,
        "measurement": {"val_acc": val_acc, "loss": 1.0},
        **extra,
    }


def _rows() -> list[dict]:
    return [
        # Credit: variance 0.1008 over its three bound rows.
        _row("primitive.credit_assignment.gradient", "credit_assignment", 0.89),
        _row(
            "primitive.credit_assignment.local_supervision", "credit_assignment", 0.60
        ),
        _row("primitive.credit_assignment.target_inversion", "credit_assignment", 0.12),
        # Dynamics: variance 0.1369 over its two bound rows; the base level is
        # inert, so it is the factorial's baseline, not a ranked row.
        _row(
            "primitive.state_dynamics.instantaneous",
            "state_dynamics",
            0.89,
            binding="inert",
        ),
        _row("primitive.state_dynamics.energy_minimization", "state_dynamics", 0.86),
        _row(
            "primitive.state_dynamics.error_predictive_coding", "state_dynamics", 0.12
        ),
        # Geometry: variance 0.0841, ranked below dynamics.
        _row("primitive.geometry.feedforward", "geometry", 0.89),
        _row("primitive.geometry.conv", "geometry", 0.30),
        # A swapped row and a refused row never rank: their variance would
        # win the pair if the box were ignored (TODO95 D3).
        _row(
            "primitive.substrate.digital",
            "substrate",
            0.0,
            swapped=True,
        ),
        {
            "primitive": "primitive.plasticity.null",
            "axis": "plasticity",
            "status": "refused",
            "binding": None,
            "swapped": False,
            "trigger": "no ψ lifecycle at this box",
            "measurement": None,
        },
    ]


def _map(rows: list[dict] | None = None) -> dict:
    primitives = {row["primitive"]: dict(row) for row in rows or _rows()}
    return {
        "version": MAP_VERSION,
        "base": _BASE,
        "primitives": primitives,
    }


def _write_map(tmp_path: Path, rows: list[dict] | None = None) -> None:
    (tmp_path / "map.json").write_text(json.dumps(_map(rows)))


def _evaluation(val_acc: float) -> CellEvaluation:
    return CellEvaluation(
        metrics={"val_acc": val_acc, "loss": 1.0},
        params={},
        param_count=100,
        walltime_s=0.1,
        epochs_completed=1,
        task_id="mnist",
    )


_TABLE = {
    ("gradient", "instantaneous"): 0.89,
    ("target_inversion", "instantaneous"): 0.12,
    ("gradient", "energy_minimization"): 0.86,
    ("target_inversion", "energy_minimization"): 0.72,
}


def _table(*args, **_kwargs) -> CellEvaluation:
    coordinate, schedule = args[0], args[1]
    base = _TABLE[coordinate.credit, coordinate.dynamics]
    return _evaluation(base + 0.01 * (schedule.seed - 1))


def test_the_pair_is_the_two_axes_with_the_most_variance() -> None:
    plan = plan_slice(_map(), legal=legal_levels)

    assert plan is not None
    assert plan.axes == ("dynamics", "credit")
    assert [spread.axis for spread in plan.spreads] == [
        "dynamics",
        "credit",
        "geometry",
    ]
    assert plan.levels["dynamics"] == ("instantaneous", "energy_minimization")
    assert plan.levels["credit"] == ("gradient", "target_inversion")


def test_a_swapped_or_refused_row_never_ranks() -> None:
    """A row that differs elsewhere is not a comparable cell (TODO95 D3)."""
    map_data = _map()
    assert map_data["primitives"]["primitive.substrate.digital"]["swapped"]
    rows = {(row["axis"], row["binding"]) for row in bound_rows(map_data)}

    assert ("substrate", "bound") not in rows
    assert ("plasticity", "bound") not in rows
    assert all(row["axis"] != "substrate" for row in bound_rows(map_data))


def test_an_inert_base_level_is_the_baseline_not_a_ranked_row() -> None:
    spreads = {spread.axis: spread for spread in axis_spreads(_map())}

    assert spreads["dynamics"].binds_at_base is False
    assert spreads["dynamics"].base == "instantaneous"
    assert spreads["credit"].binds_at_base is True


def test_the_slice_varies_only_the_pair() -> None:
    plan = plan_slice(_map(), legal=legal_levels)
    assert plan is not None
    combinations = plan.combinations()

    assert len(combinations) == 4
    assert combinations[0] == {
        "dynamics": "instantaneous",
        "credit": "gradient",
    }
    for levels in combinations:
        assert set(levels) == {"dynamics", "credit"}


def test_the_effect_is_a_difference_in_differences() -> None:
    from computronium.experiment.sec_interaction import InteractionCell

    plan = plan_slice(_map(), legal=legal_levels)
    assert plan is not None
    first, second = plan.pair
    cells = [
        InteractionCell(
            levels=levels,
            seed=seed,
            status="measured",
            val_acc=_TABLE[levels["credit"], levels["dynamics"]],
            loss=1.0,
            walltime_s=1.0,
            replay_hash=None,
            box={},
        )
        for levels in plan.combinations()
        for seed in range(INTERACTION_SEEDS)
    ]
    effect = interaction_effect(plan, cells)

    assert effect is not None
    assert effect.effect == pytest.approx(0.72 - 0.12 - 0.86 + 0.89)
    assert effect.seeds == INTERACTION_SEEDS
    assert (first.axis, second.axis) == ("dynamics", "credit")


def test_one_seed_carries_no_interval() -> None:
    from computronium.experiment.sec_interaction import InteractionCell

    plan = plan_slice(_map(), legal=legal_levels)
    assert plan is not None
    cells = [
        InteractionCell(
            levels=levels,
            seed=0,
            status="measured",
            val_acc=_TABLE[levels["credit"], levels["dynamics"]],
            loss=1.0,
            walltime_s=1.0,
            replay_hash=None,
            box={},
        )
        for levels in plan.combinations()
    ]
    effect = interaction_effect(plan, cells)

    assert effect is not None
    assert effect.seeds == 1
    assert (effect.lower, effect.upper, effect.spans_zero) == (None, None, None)


def test_a_constant_arm_marks_the_slice_without_power(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The acceptance case: a control inside the bar prices no cell."""
    _write_map(tmp_path)
    monkeypatch.setattr(sec_loop, "evaluate_cell", lambda *_a, **_k: _evaluation(0.1))

    result = sec_loop.run_p3_track(tmp_path, device="cpu")

    assert result is not None
    layer = result["interaction"]
    assert layer["status"] == "no_power"
    assert layer["effect"] is None
    assert "control at chance" in layer["stop_reason"]
    assert sum(cell["status"] == "refused" for cell in layer["cells"]) == 3


def test_the_slice_confirms_at_three_seeds(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_map(tmp_path)
    monkeypatch.setattr(sec_loop, "evaluate_cell", _table)

    result = sec_loop.run_p3_track(tmp_path, device="cpu")

    assert result is not None
    layer = result["interaction"]
    assert layer["status"] == "measured"
    assert layer["pair"] == ["dynamics", "credit"]
    assert len(layer["cells"]) == 4 * INTERACTION_SEEDS
    effect = layer["effect"]
    assert effect["seeds"] == INTERACTION_SEEDS
    assert effect["effect"] == pytest.approx(0.63)
    assert effect["lower"] < effect["effect"] < effect["upper"]
    assert effect["lower"] != effect["upper"]
    assert layer["screened"]["seeds"] == 1
    assert layer["screened"]["lower"] is None


def test_every_cell_carries_its_box_and_replay_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_map(tmp_path)
    monkeypatch.setattr(sec_loop, "evaluate_cell", _table)

    result = sec_loop.run_p3_track(tmp_path, device="cpu")

    assert result is not None
    for cell in result["cells"]:
        assert set(cell["levels"]) == {"dynamics", "credit"}
        box = cell["box"]
        assert box["task"] == "mnist"
        assert box["batch_size"] == _BASE["batch_size"]
        assert box["epochs"] == _BASE["epochs"]
        assert box["seed"] == cell["seed"]
        assert cell["replay_hash"]
        for fixed in ("substrate", "geometry", "plasticity", "update"):
            assert box[fixed] == _BASE[fixed], fixed


def test_the_map_keeps_the_interaction_of_a_later_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_map(tmp_path)
    monkeypatch.setattr(sec_loop, "evaluate_cell", _table)
    entries = build_census()

    result = sec_loop.run_p3_track(tmp_path, device="cpu")
    assert result is not None
    sec_loop.update_map(tmp_path, entries, None, p3_result=result)
    layer = json.loads((tmp_path / "map.json").read_text())["interaction"]
    assert layer["pair"] == ["dynamics", "credit"]

    sec_loop.update_map(tmp_path, entries, {"cells": []})
    kept = json.loads((tmp_path / "map.json").read_text())["interaction"]
    assert kept == layer


def test_the_interaction_layer_prints_the_interval(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys
) -> None:
    _write_map(tmp_path)
    monkeypatch.setattr(sec_loop, "evaluate_cell", _table)

    result = sec_loop.run_p3_track(tmp_path, device="cpu")
    assert result is not None
    sec_loop.update_map(tmp_path, build_census(), None, p3_result=result)
    printed = capsys.readouterr().out

    assert "Interaction: dynamics × credit" in printed
    assert "effect:" in printed


def test_no_map_refuses_the_slice(tmp_path: Path) -> None:
    assert sec_loop.run_p3_track(tmp_path, device="cpu") is None


def test_an_arm_the_validator_refuses_is_not_a_factor_level() -> None:
    """The largest 2×2 the box accepts seats the slice, not a swapped arm."""
    unseated = plan_slice(_map())
    assert unseated is not None
    assert unseated.levels["dynamics"] == (
        "instantaneous",
        "error_predictive_coding",
    )

    plan = plan_slice(
        _map(),
        legal=lambda levels: levels["dynamics"] != "error_predictive_coding",
    )

    assert plan is not None
    assert plan.levels["dynamics"] == ("instantaneous", "energy_minimization")
    assert plan.levels["credit"] == ("gradient", "target_inversion")


def test_a_pair_with_no_legal_2x2_is_refused() -> None:
    assert plan_slice(_map(), legal=lambda _levels: False) is None


def test_every_run_carries_its_own_replay_hash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A cell's hash names its seed, or three seeds share one record."""
    _write_map(tmp_path)
    monkeypatch.setattr(sec_loop, "evaluate_cell", _table)

    result = sec_loop.run_p3_track(tmp_path, device="cpu")

    assert result is not None
    hashes = [cell["replay_hash"] for cell in result["cells"]]
    assert len(hashes) == 4 * INTERACTION_SEEDS
    assert len(set(hashes)) == len(hashes)
