"""Lock: an axis declares what binds it (TODO95 D8 / P0.75).

Nine substrates "passed" on an MLP read through accuracy, five credits declared
error-blind read no label, and updates ran at a shared step. Each cell now says
whether its varied axis could act at that box. This test fails if a condition
disappears, if an axis has no condition, or if the screen stops stamping it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.sec_binding import BINDING_CONDITIONS, binding_reason


def test_every_axis_declares_a_condition() -> None:
    assert set(BINDING_CONDITIONS) == set(StructuralAxis)
    for axis, condition in BINDING_CONDITIONS.items():
        assert condition.axis is axis
        assert condition.requires


@pytest.mark.parametrize(
    ("axis", "name", "criterion", "own_knobs", "inert"),
    [
        ("substrate", "digital", "val_acc", False, True),
        ("substrate", "digital", "energy", False, False),
        ("credit", "homeostatic", "val_acc", False, True),
        ("credit", "temporal_trace", "val_acc", False, True),
        ("credit", "gradient", "val_acc", False, False),
        ("dynamics", "instantaneous", "val_acc", False, True),
        ("dynamics", "energy_minimization", "val_acc", False, False),
        ("plasticity", "null", "val_acc", False, True),
        ("plasticity", "fast_weights", "val_acc", False, False),
        ("update", "adam", "val_acc", False, True),
        ("update", "adam", "val_acc", True, False),
        ("geometry", "feedforward", "val_acc", False, False),
    ],
)
def test_a_binding_condition_names_the_unmet_case(
    axis: str, name: str, criterion: str, own_knobs: bool, inert: bool
) -> None:
    reason = binding_reason(axis, name, criterion=criterion, own_knobs=own_knobs)
    assert (reason is not None) is inert


def test_the_screen_stamps_the_binding(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from computronium.experiment import sec_loop
    from computronium.experiment.kernel.evaluate import CellEvaluation
    from computronium.experiment.sec_census import PrimitiveCensusEntry

    entry = PrimitiveCensusEntry(
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

    def _fake(*_args: object, **_kwargs: object) -> CellEvaluation:
        return CellEvaluation(
            metrics={"val_acc": 0.9, "loss": 0.5},
            params={},
            param_count=100,
            walltime_s=0.1,
            epochs_completed=1,
            task_id="mnist",
        )

    monkeypatch.setattr(sec_loop, "evaluate_cell", _fake)
    result = sec_loop.run_p0_track(
        tmp_path, [entry], max_primitives=1, breadth="full", device="cpu"
    )

    cell = result["cells"][0]
    assert cell["binding"] == "inert"
    assert "step size" in cell["binding_reason"]
    assert (
        cell["ruler"] == "val_acc on mnist (primary validation_accuracy, chance 0.100)"
    )
