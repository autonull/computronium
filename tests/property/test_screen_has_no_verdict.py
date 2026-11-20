"""Lock: a screen records; it never adjudicates (TODO95 D5).

``run_p0_track`` computed ``PASS`` above a local ``chance = 0.1`` — a second bar
beside the kernel's, and a capability judgment from one seed. A screen emits the
number, the box and the cost; it names a DEFECT only for an execution fact. A
judgment requires a pre-registered comparison at a calibrated box.

This test fails if a verdict key or a bar comparison returns to the screen.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from computronium.experiment import sec_loop
from computronium.experiment.kernel.evaluate import CellEvaluation
from computronium.experiment.sec_census import PrimitiveCensusEntry

if TYPE_CHECKING:
    from pathlib import Path

_ENTRY = PrimitiveCensusEntry(
    id="primitive.parameter_update.euclidean",
    axis="parameter_update",
    name="euclidean",
    task_families=("vision",),
    available=True,
    capability_card="reference coordinate",
    status="implemented",
    reference_entrypoint="",
    kernel_entrypoint=None,
    supported_backends=(),
)


def _fake(val_acc: float, param_count: int = 100) -> CellEvaluation:
    return CellEvaluation(
        metrics={"val_acc": val_acc, "loss": 0.5},
        params={},
        param_count=param_count,
        walltime_s=0.1,
        epochs_completed=1,
        task_id="mnist",
    )


def _screen(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, val_acc: float) -> dict:
    monkeypatch.setattr(sec_loop, "evaluate_cell", lambda *_a, **_k: _fake(val_acc))
    return sec_loop.run_p0_track(
        tmp_path, [_ENTRY], max_primitives=1, breadth="full", device="cpu"
    )


def test_a_screen_emits_a_measurement_and_no_verdict(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    result = _screen(monkeypatch, tmp_path, 0.93)
    assert result["measured"] == 1
    cell = result["cells"][0]
    assert cell["status"] == "MEASURED"
    assert cell["val_acc"] == pytest.approx(0.93)
    assert "viable" not in cell
    assert "PASS" not in str(result)


def test_a_chance_cell_is_still_a_measurement(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """One seed above chance is not a result; it is a number in a box."""
    result = _screen(monkeypatch, tmp_path, 0.11)
    assert result["cells"][0]["status"] == "MEASURED"
    assert result["measured"] == 1


def test_the_box_travels_with_the_measurement(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from computronium.experiment.sec_pilot import base_schedule

    base = base_schedule("mnist", "cpu")
    assert base is not None
    cell = _screen(monkeypatch, tmp_path, 0.93)["cells"][0]
    assert cell["box"]["task"] == "mnist"
    assert cell["box"]["batch_limit"] == base.batch_limit
    assert cell["box"]["epochs"] == base.epochs
    assert cell["box"]["seed"] == base.seed
    assert cell["param_count"] == 100
    assert cell["within_ceiling"] is True


def test_loop_has_no_bar(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A screen's status vocabulary has no verdict and no second bar."""
    from computronium.experiment.sec_loop import update_map

    result = _screen(monkeypatch, tmp_path, 0.93)
    cell = result["cells"][0]
    assert cell["record"]["status"]["gate_verdict"] == "PENDING"
    assert cell["record"]["status"]["maturity"] == "l0"
    assert cell["record"]["payload"]["pass_bar_cleared"] is None
    assert "viable" not in str(cell)
    update_map(tmp_path, [_ENTRY], result)
    map_row = json.loads((tmp_path / "map.json").read_text())["primitives"][_ENTRY.id]
    assert map_row["status"] == "measured"
    assert map_row["status"] not in {"pass", "viable", "unavailable", "coordinate"}


def test_a_screen_keeps_the_ladder_table(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A P0 write carries the S6b ladder records; it never rewrites the map.

    Measured 2026-11-20: a P0 run dropped ``ladders`` and every near-chance
    record with it. The map is a document with sections; a screen owns rows.
    """
    from computronium.experiment.sec_loop import update_map

    _screen(monkeypatch, tmp_path, 0.93)  # a cell at the box
    map_path = tmp_path / "map.json"
    update_map(tmp_path, [_ENTRY], _screen(monkeypatch, tmp_path, 0.93))
    document = json.loads(map_path.read_text())
    document["ladders"] = {"primitive.credit_assignment.forward_tangent": {"v": 1}}
    map_path.write_text(json.dumps(document))

    result = _screen(monkeypatch, tmp_path, 0.5)
    update_map(tmp_path, [_ENTRY], result)
    written = json.loads(map_path.read_text())
    assert written["ladders"] == {
        "primitive.credit_assignment.forward_tangent": {"v": 1}
    }
    assert written["primitives"][_ENTRY.id]["status"] == "measured"
