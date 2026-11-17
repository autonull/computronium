"""F1's gate must promote only from a family ladder with a confirmation seed.

The composition screen asks a predicate the repository evaluates: does a legal
6-axis composition beat the best single-axis default by the pre-registered
delta at matched forward-equivalents? A screen winner that does not survive its
own family ladder is a coordinate, a flat screen is a refusal with a knob box,
and a reference below the floor or a drifting control invalidates the run. The
tests pin the gate, the family selection, the width ladder, and the cell-log
replay without training a model.
"""

from __future__ import annotations

import json

import pytest

from computronium.experiment.schema.coordinate import Coordinate
from computronium.validation import composition_ladder as cl

_AXIS_VALUES: dict[str, str] = {
    "substrate": "ternary",
    "geometry": "attention",
    "dynamics": "lazy",
    "plasticity": "routing",
    "credit": "pepita",
    "update": "adam",
}


def _cell(
    stage: str,
    *,
    acc: float | None,
    axis: str = "",
    credit: str = "gradient",
    seed: int = 42,
    width: int = 1,
    refused: bool = False,
) -> cl.CompositionCell:
    """A synthetic row; no model is trained."""
    values = {**cl.DEFAULT_VALUES, "credit": credit}
    if axis in _AXIS_VALUES:
        values[axis] = _AXIS_VALUES[axis]
    return cl.CompositionCell(
        stage=stage,
        axis=axis,
        width=width,
        seed=seed,
        batch_limit=cl.BATCH_LIMIT,
        **values,
        params={},
        val_acc=None if refused else acc,
        param_count=100,
        forward_equivalents=cl.BATCH_LIMIT,
        walltime_s=1.0,
        refused=refused,
        reason="refused" if refused else "",
        measurement_key=f"{stage}|{axis}|{credit}|{seed}|{acc}|{width}",
    )


def _reference(acc: float = 0.80) -> tuple[cl.CompositionCell, ...]:
    return (
        _cell("reference", acc=0.10, axis="default"),
        _cell("reference", acc=acc, axis="update", seed=42),
    )


def _screen(
    credits: tuple[str, ...], accs: tuple[float, ...]
) -> tuple[cl.CompositionCell, ...]:
    return tuple(
        _cell("screen", acc=acc, credit=credit, width=3)
        for credit, acc in zip(credits, accs, strict=True)
    )


def test_width_counts_only_the_axes_that_leave_the_default_cell() -> None:
    default = Coordinate(**cl.DEFAULT_VALUES, params={})
    assert cl._width(default) == 0
    changed = Coordinate(**{**cl.DEFAULT_VALUES, "update": "adam"}, params={})
    assert cl._width(changed) == 1
    full = Coordinate(
        substrate="ternary",
        geometry="recurrent",
        dynamics="energy_minimization",
        plasticity="routing",
        credit="pepita",
        update="adam",
        params={},
    )
    assert cl._width(full) == 6


def test_family_selection_uses_a_median_and_refuses_a_singleton() -> None:
    screen = (
        _cell("screen", acc=0.9, credit="pepita"),
        _cell("screen", acc=0.1, credit="pepita"),
        _cell("screen", acc=0.6, credit="local_goodness"),
        _cell("screen", acc=0.7, credit="local_goodness"),
        _cell("screen", acc=0.95, credit="gradient"),
    )
    assert cl._best_family(screen) == "local_goodness"


def test_no_family_with_two_measured_cells_is_a_coordinate(monkeypatch) -> None:
    monkeypatch.setattr(cl, "MIN_SCREEN_MEASURED", 1)
    gate = cl._gate(
        reference=_reference(0.80),
        controls=(_cell("control", acc=0.81, axis="update", seed=43),),
        screen=(
            _cell("screen", acc=0.90, credit="pepita"),
            _cell("screen", acc=0.80, credit="pepita", refused=True),
        ),
        ladder=(),
    )
    assert gate.verdict == "coordinate"
    assert "no credit family" in gate.reason


def test_a_family_ladder_at_the_bar_with_its_confirmation_promotes(monkeypatch) -> None:
    monkeypatch.setattr(cl, "MIN_SCREEN_MEASURED", 2)
    gate = cl._gate(
        reference=_reference(0.800),
        controls=(_cell("control", acc=0.810, axis="update", seed=43),),
        screen=_screen(("pepita", "pepita"), (0.700, 0.780)),
        ladder=(
            _cell("ladder", acc=0.820, axis="pepita", seed=42, width=4),
            _cell("ladder", acc=0.830, axis="pepita", seed=43, width=4),
        ),
    )
    assert gate.verdict == "promote"
    assert gate.best_ladder_acc == pytest.approx(0.820)


def test_a_ladder_point_that_does_not_reproduce_is_a_coordinate(monkeypatch) -> None:
    monkeypatch.setattr(cl, "MIN_SCREEN_MEASURED", 2)
    gate = cl._gate(
        reference=_reference(0.800),
        controls=(_cell("control", acc=0.810, axis="update", seed=43),),
        screen=_screen(("pepita", "pepita"), (0.700, 0.780)),
        ladder=(
            _cell("ladder", acc=0.820, axis="pepita", seed=42, width=4),
            _cell("ladder", acc=0.805, axis="pepita", seed=43, width=4),
        ),
    )
    assert gate.verdict == "coordinate"
    assert "did not reproduce" in gate.reason


def test_a_screen_winner_below_its_ladder_is_a_coordinate(monkeypatch) -> None:
    monkeypatch.setattr(cl, "MIN_SCREEN_MEASURED", 2)
    gate = cl._gate(
        reference=_reference(0.800),
        controls=(_cell("control", acc=0.810, axis="update", seed=43),),
        screen=_screen(("pepita", "pepita"), (0.700, 0.820)),
        ladder=(
            _cell("ladder", acc=0.805, axis="pepita", seed=42, width=2),
            _cell("ladder", acc=0.810, axis="pepita", seed=43, width=2),
        ),
    )
    assert gate.verdict == "coordinate"
    assert "did not survive" in gate.reason


def test_a_flat_screen_refuses_composition_at_the_box() -> None:
    gate = cl._gate(
        reference=_reference(0.889),
        controls=(_cell("control", acc=0.891, axis="update", seed=43),),
        screen=_screen(
            tuple(["pepita"] * 25 + ["local_goodness"] * 25),
            tuple([0.80] * 50),
        ),
        ladder=(
            _cell("ladder", acc=0.81, axis="pepita", seed=42, width=2),
            _cell("ladder", acc=0.82, axis="pepita", seed=43, width=2),
        ),
    )
    assert gate.verdict == "refuse"
    assert "flat at this box" in gate.reason
    assert "Re-open" in gate.reason


def test_a_reference_below_the_floor_invalidates_the_run() -> None:
    gate = cl._gate(
        reference=_reference(0.30),
        controls=(_cell("control", acc=0.31, axis="update", seed=43),),
        screen=_screen(("pepita", "pepita"), (0.70, 0.75)),
        ladder=(),
    )
    assert gate.verdict == "invalid-reference"


def test_a_control_that_drifts_beyond_the_band_invalidates_the_run() -> None:
    gate = cl._gate(
        reference=_reference(0.80),
        controls=(_cell("control", acc=0.60, axis="update", seed=43),),
        screen=_screen(("pepita", "pepita"), (0.70, 0.75)),
        ladder=(),
    )
    assert gate.verdict == "invalid-control"


def test_a_screen_below_the_measured_minimum_is_a_coordinate() -> None:
    gate = cl._gate(
        reference=_reference(0.80),
        controls=(_cell("control", acc=0.81, axis="update", seed=43),),
        screen=_screen(("pepita", "pepita"), (0.70, 0.75)),
        ladder=(),
    )
    assert gate.verdict == "coordinate"
    assert "only 2 of 2 screen cells trained" in gate.reason


def test_the_ladder_builds_widths_two_four_six_and_keeps_the_family() -> None:
    reference = (
        _cell("reference", acc=0.10, axis="default"),
        _cell("reference", acc=0.80, axis="geometry"),
        _cell("reference", acc=0.75, axis="substrate"),
        _cell("reference", acc=0.70, axis="dynamics"),
        _cell("reference", acc=0.65, axis="update"),
        _cell("reference", acc=0.60, axis="plasticity"),
    )
    screen = (
        _cell("screen", acc=0.78, credit="pepita", width=2),
        _cell("screen", acc=0.74, credit="pepita", width=2),
        _cell("screen", acc=0.60, credit="gradient", width=2),
        _cell("screen", acc=0.62, credit="gradient", width=2),
    )
    points = cl._ladder_coordinates(screen, reference)
    assert [width for _family, width, _coord in points] == list(cl.LADDER_WIDTHS)
    for family, width, coord in points:
        assert family == "pepita"
        assert coord.credit == "pepita"
        assert cl._width(coord) == width


def test_the_screen_sample_is_deterministic_and_multi_axis(monkeypatch) -> None:
    from computronium.experiment.schema.coordinate import Coordinate

    def cell(i: int) -> Coordinate:
        return Coordinate(
            **{**cl.DEFAULT_VALUES, "update": f"u{i % 5}", "geometry": "conv"},
            params={},
        )

    monkeypatch.setattr(
        cl,
        "iter_candidates",
        lambda *_args, **_kwargs: ((cell(i), object()) for i in range(200)),
    )
    first = cl._sample_screen(object(), object())
    second = cl._sample_screen(object(), object())
    assert len(first) == cl.SCREEN_CELLS
    assert first == second
    assert all(cl._width(coord) >= 2 for coord in first)


def test_the_cell_log_replays_the_gate_and_the_table(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(cl, "MIN_SCREEN_MEASURED", 2)
    progress = tmp_path / "cells.jsonl"
    cells = (
        *_reference(0.800),
        _cell("control", acc=0.810, axis="update", seed=43),
        *_screen(("pepita", "pepita"), (0.70, 0.78)),
        _cell("ladder", acc=0.820, axis="pepita", seed=42, width=4),
        _cell("ladder", acc=0.830, axis="pepita", seed=43, width=4),
    )
    for cell in cells:
        cl._write_cell(cell, progress)
    registration = cl.write_registration(tmp_path)
    report = cl.replay_composition_ladder(
        progress=progress, registration_path=registration
    )
    assert report.verdict == "promote"
    assert len(report.reference) == len(cells[:2])
    assert report.best_family == "pepita"
    payload = json.loads(registration.read_text())
    assert payload["threshold"] == cl.DELTA
    assert payload["min_seeds"] == 1


def test_the_report_writes_its_rulers_and_verdict(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(cl, "MIN_SCREEN_MEASURED", 2)
    cells = (
        *_reference(0.800),
        _cell("control", acc=0.810, axis="update", seed=43),
        *_screen(("pepita", "pepita"), (0.70, 0.78)),
        _cell("ladder", acc=0.820, axis="pepita", seed=42, width=4),
        _cell("ladder", acc=0.830, axis="pepita", seed=43, width=4),
    )
    report = cl._report(
        reference=cells[:2],
        controls=cells[2:3],
        screen=cells[3:5],
        ladder=cells[5:],
        registration=cl._registration("cpu"),
        device="cpu",
    )
    path = cl.write_report(report, tmp_path)
    markdown = (tmp_path / "composition.md").read_text()
    assert json.loads(path.read_text())["verdict"] == "promote"
    assert "matched forward-equivalents" in markdown
    assert "Verdict: promote" in markdown
    assert "composition.registered.json" in markdown


def test_the_reference_sweep_varies_every_axis_and_is_legal() -> None:
    from computronium.experiment.kernel.search_space import (
        search_space_from_spec,
    )
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    space = search_space_from_spec(cl._spec(), tasks=(cl.TASK_ID,))
    arms = cl._single_axis_arms(space)
    assert {axis for axis, _primitive, _coord in arms} == {
        "default",
        *cl.DEFAULT_VALUES,
    }
    assert all(cl._legal(coord) for _axis, _primitive, coord in arms)


def test_the_registration_is_written_before_the_first_cell(
    tmp_path, monkeypatch
) -> None:
    events: list[str] = []
    registration = tmp_path / "composition.registered.json"

    def register(*_args, **_kwargs):
        events.append("register")
        return registration

    def measure(*_args, **kwargs):
        events.append(f"measure:{kwargs['stage']}")
        return _cell(kwargs["stage"], acc=0.8)

    monkeypatch.setattr(cl, "write_registration", register)
    monkeypatch.setattr(cl, "_measure", measure)
    monkeypatch.setattr(
        cl, "search_space_from_spec", lambda *_args, **_kwargs: object()
    )
    monkeypatch.setattr(
        cl, "_single_axis_arms", lambda _space: (("update", "adam", _default()),)
    )
    monkeypatch.setattr(cl, "_sample_screen", lambda *_a: (_default(),))
    monkeypatch.setattr(cl, "_ladder_coordinates", lambda *_a: ())
    cl.run_composition_ladder(
        device="cpu", progress=tmp_path / "cells.jsonl", output_dir=tmp_path
    )
    assert events[0] == "register"
    assert events[1:] == [
        "measure:reference",
        "measure:control",
        "measure:screen",
    ]


def _default() -> Coordinate:
    return Coordinate(**cl.DEFAULT_VALUES, params={})


def test_replay_without_a_cell_log_raises(tmp_path) -> None:
    with pytest.raises(RuntimeError, match="no cells"):
        cl.replay_composition_ladder(progress=tmp_path / "missing.jsonl")
