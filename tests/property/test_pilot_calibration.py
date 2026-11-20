"""Lock: the bar is calibrated and the slice has power (TODO95 S2).

A bar at the chance rate alone is a coin flip, and a 1-seed control cannot
tell a slice from noise. This lock pins the 2σ band at the task's declared
resolution, the 3-seed control, the task-family refusal, the own-knobs box and
the resource vector beside the number. A constant control must refuse its slice
before it is priced, or the fixture would pass with the mechanism removed.
"""

from __future__ import annotations

import math

import pytest

from computronium.experiment import sec_loop
from computronium.experiment.kernel.evaluate import CellEvaluation
from computronium.experiment.registry.task_registry import (
    PassBar,
    TaskRegistry,
    primary_pass_bar,
)
from computronium.experiment.sec_census import build_census
from computronium.experiment.sec_pilot import (
    Calibration,
    base_schedule,
    calibrate_control,
    own_knob_params,
    refusal_for,
    resource_vector,
)
from computronium.ontology.update import ParameterUpdateConfig

_TASK = "mnist"


def _entry(primitive_id: str):
    return {entry.id: entry for entry in build_census()}[primitive_id]


def _evaluation(val_acc: float, task_id: str = _TASK) -> CellEvaluation:
    return CellEvaluation(
        metrics={"val_acc": val_acc, "loss": 1.0},
        params={},
        param_count=100,
        walltime_s=1.0,
        epochs_completed=1,
        task_id=task_id,
    )


def _constant(val_acc: float):
    return lambda *_args, **_kwargs: _evaluation(val_acc)


def test_the_bar_is_the_floor_plus_2_sigma() -> None:
    bar = primary_pass_bar(TaskRegistry().get(_TASK))

    assert bar is not None
    assert bar.floor == pytest.approx(0.1)
    assert bar.resolution == 10_000
    assert bar.sigma is not None
    assert bar.sigma == pytest.approx(math.sqrt(0.1 * 0.9 / 10_000))
    assert bar.value == pytest.approx(0.1 + 2.0 * bar.sigma)
    assert bar.value > bar.floor


def test_the_p0_box_is_the_declared_base() -> None:
    """One box, one source: P0 and the pilot read the same schedule."""
    from computronium.experiment.sec_pilot import base_schedule

    schedule = base_schedule(_TASK)
    assert schedule is not None
    assert (schedule.task_id, schedule.batch_size, schedule.batch_limit) == (
        _TASK,
        32,
        375,
    )


def test_an_undeclared_resolution_keeps_the_chance_floor() -> None:
    """A task with no declared ruler resolution is uncalibrated, not invented."""
    bar = primary_pass_bar(TaskRegistry().get("digits"))

    assert bar is not None
    assert (bar.value, bar.floor, bar.sigma, bar.resolution) == (0.1, 0.1, None, None)


def test_the_family_filter_refuses_a_sequence_credit_on_vision() -> None:
    sequence_credit = _entry("primitive.credit_assignment.unbiased_rtrl")
    universal = _entry("primitive.credit_assignment.gradient")

    reason = refusal_for(sequence_credit, _TASK)
    assert reason is not None
    assert "sequence" in reason
    assert refusal_for(universal, _TASK) is None
    assert refusal_for(sequence_credit, "digits") is None or "sequence" in (
        refusal_for(sequence_credit, "digits") or ""
    )


def test_a_constant_control_refuses_its_slice(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The acceptance case: a control inside the band cannot price a cell."""
    monkeypatch.setattr(sec_loop, "evaluate_cell", _constant(0.1))

    result = sec_loop.run_p0_track(tmp_path, build_census(), max_primitives=3)

    assert result["control_val_acc"] == pytest.approx(0.1)
    assert result["control_spread"] == pytest.approx(0.0)
    assert result["pause_r"] is True
    assert result["measured"] == 0
    assert all(cell["status"] == "UNAVAILABLE" for cell in result["cells"])
    assert all("control at chance" in cell["reason"] for cell in result["cells"])


def test_a_control_above_the_bar_prices_the_slice(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    monkeypatch.setattr(sec_loop, "evaluate_cell", _constant(0.5))

    result = sec_loop.run_p0_track(
        tmp_path,
        [_entry("primitive.credit_assignment.gradient")],
        max_primitives=1,
    )

    assert result["pause_r"] is False
    assert result["measured"] == 1
    assert result["control_val_acc"] == pytest.approx(0.5)
    assert result["control_spread"] == pytest.approx(0.0)


def test_own_knobs_are_the_declared_config_defaults() -> None:
    params = own_knob_params("update", "adam")

    assert params["update.step_size"] == ParameterUpdateConfig.adam().step_size
    assert params["update.momentum"] == ParameterUpdateConfig.adam().momentum
    # A geometry factory needs the task's shape: it has no viability box.
    assert own_knob_params("geometry", "feedforward") == {}


def test_the_own_knobs_box_binds_an_update_row() -> None:
    from computronium.experiment.sec_binding import binding_reason

    assert binding_reason("update", "adam", criterion="val_acc", own_knobs=False)
    assert binding_reason("update", "adam", criterion="val_acc", own_knobs=True) is None

    entry = _entry("primitive.parameter_update.adam")
    base = sec_loop._iter_legal_coordinates(entry, limit=1)
    own = sec_loop._iter_legal_coordinates(entry, limit=1, own_knobs=True)
    assert base and own
    assert own[0].params["update.step_size"] == pytest.approx(
        ParameterUpdateConfig.adam().step_size
    )


def test_the_resource_vector_carries_memory_and_energy() -> None:
    assert resource_vector({"memory_usage": 12.5, "energy_per_step": 0.3}) == {
        "memory_mb": 12.5,
        "energy_per_batch": 0.3,
    }
    assert resource_vector({}) == {"memory_mb": None, "energy_per_batch": None}


def test_calibrate_control_measures_the_three_seed_base() -> None:
    schedule = base_schedule(_TASK)
    assert schedule is not None

    calibration = calibrate_control(schedule, evaluate=_constant(0.2))

    assert calibration is not None
    assert calibration.seeds == 3
    assert calibration.control_mean == pytest.approx(0.2)
    assert calibration.has_power is True


def test_a_calibration_inside_the_bar_has_no_power() -> None:
    maximize = PassBar("val_acc", "maximize", 0.5)
    minimize = PassBar("val_loss", "minimize", 0.5)

    assert Calibration(_TASK, maximize, 0.5, 0.0, 3).has_power is False
    assert Calibration(_TASK, maximize, 0.6, 0.0, 3).has_power is True
    assert Calibration(_TASK, maximize, math.nan, 0.0, 3).has_power is False
    # A ceiling bar clears from below: a perplexity of 21 beats a bar of 27.
    assert Calibration(_TASK, minimize, 0.4, 0.0, 3).has_power is True
    assert Calibration(_TASK, minimize, 0.6, 0.0, 3).has_power is False


def test_the_base_coordinate_is_the_boxes_declaration() -> None:
    """One source: a screen, a calibration and P3 read the box's own axes."""
    assert sec_loop._base_axes("mnist")["geometry"] == "feedforward"
    assert sec_loop._base_axes("cora")["geometry"] == "graph"
    assert sec_loop._base_axes("tiny_shakespeare")["geometry"] == ("causal_transformer")
    assert sec_loop._base_axes("spiking_mnist")["substrate"] == "neuromorphic"


def test_calibrate_control_runs_at_the_box_coordinate() -> None:
    """The LM base composes on its causal transformer, not the default MLP."""
    schedule = base_schedule("tiny_shakespeare")
    assert schedule is not None
    seen: list[str] = []

    def capture(coordinate, _schedule):
        seen.append(coordinate.geometry)
        return _evaluation(0.2, "tiny_shakespeare")

    calibration = calibrate_control(schedule, evaluate=capture)

    assert calibration is not None
    assert seen == ["causal_transformer"] * 3


def test_calibrate_control_records_cost_and_replay() -> None:
    schedule = base_schedule(_TASK)
    assert schedule is not None

    calibration = calibrate_control(schedule, evaluate=_constant(0.2))
    replay = calibrate_control(schedule, evaluate=_constant(0.2))

    assert calibration is not None
    assert replay is not None
    assert calibration.param_count == 100
    assert calibration.cell_seconds >= 0.0
    assert calibration.replay == replay.replay


def test_the_payload_carries_the_calibrated_bar() -> None:
    from computronium.experiment.kernel.evaluate import clears_task_bar

    bar = PassBar("val_acc", "maximize", 0.106, floor=0.1, resolution=10_000)
    assert clears_task_bar(bar, {"val_acc": 0.103}) is False
    assert clears_task_bar(bar, {"val_acc": 0.11}) is True


@pytest.mark.xfail(
    strict=True,
    reason=(
        "the graph base composes at 200,967 parameters over its declared "
        "200,000 ceiling: explicit geometry.hidden_dim bypasses the ceiling "
        "in _fit_geometry, so the sizing path never enforces the budget"
    ),
)
def test_the_graph_base_fits_its_declared_ceiling() -> None:
    from computronium.experiment.kernel.evaluate import (
        _compose_cell,
        _task,
        _task_shape,
    )

    schedule = base_schedule("cora")
    assert schedule is not None
    task = _task("cora", "cpu")
    cell = _compose_cell(
        sec_loop._coordinate(sec_loop._base_axes("cora")),
        None,
        _task_shape(task),
        schedule.param_budget,
        task,
    )
    assert cell.param_count <= schedule.param_budget
