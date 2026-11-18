"""Lock: a screen records; it never adjudicates (TODO95 D5).

``run_p0_track`` computed ``PASS`` above a local ``chance = 0.1`` — a second bar
beside the kernel's, and a capability judgment from one seed. A screen emits the
number, the box and the cost; it names a DEFECT only for an execution fact. A
judgment requires a pre-registered comparison at a calibrated box.

This test fails if a verdict key or a bar comparison returns to the screen.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from computronium.experiment import sec_loop
from computronium.experiment.kernel.evaluate import CellEvaluation
from computronium.experiment.sec_census import PrimitiveCensusEntry

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
    cell = _screen(monkeypatch, tmp_path, 0.93)["cells"][0]
    assert cell["box"]["task"] == "mnist"
    assert cell["box"]["batch_limit"] == sec_loop.P0_BATCH_LIMIT
    assert cell["box"]["epochs"] == sec_loop.P0_EPOCHS
    assert cell["box"]["seed"] == sec_loop.P0_SEED
    assert cell["param_count"] == 100
    assert cell["within_ceiling"] is True
