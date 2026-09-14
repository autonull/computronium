"""Extension-point tests: new problem classes, objectives, and curricula
plug in through the public registries without core edits (TODO24 §14)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import computronium_lab
from computronium_lab import Lab
from computronium_lab.research import (
    CLASS_BY_NAME,
    CURRICULA,
    CurriculumSpec,
    MeasurementRunner,
    objective_names,
    problem_class_defaults,
    register_curriculum,
    register_objective,
    register_problem_class,
)
from computronium_lab.research.corpus import _SPEC_DEFAULTS  # test cleanup only
from computronium_lab.synthesis.engine import OBJECTIVE_FIELDS
from computronium_lab.synthesis.spec import KNOWN_OBJECTIVES, ProblemSpec

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


class _ToyClass:
    """Minimal ProblemClassProtocol plug: no training, deterministic metrics."""

    name = "toy_demo"

    def __init__(self, spec: ProblemSpec) -> None:
        self.spec = spec

    def generate_task(self, seed: int) -> object:
        return {"seed": seed}

    def default_metrics(self) -> tuple[str, ...]:
        return ("accuracy",)

    def run_arm(
        self, lab: Lab, arm: str, seed: int, *, epochs: int
    ) -> dict[str, float]:
        return {"accuracy": 1.0}

    def control_arm(self, arm: str) -> str | None:
        return None


def test_register_problem_class_runs_through_runner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    register_problem_class(
        "toy_demo",
        _ToyClass,
        task="toy_task",
        dataset="toy_data",
        input_dim=4,
        num_classes=2,
    )
    try:
        assert CLASS_BY_NAME["toy_demo"] is _ToyClass
        assert problem_class_defaults("toy_demo")["dataset"] == "toy_data"
        report = MeasurementRunner(Lab(seed=0)).run(
            "toy_demo", ("toy_arm",), seeds=(0,), epochs=1, run_id="toy"
        )
        assert report.problem_class == "toy_demo"
        assert report.arms[0].summaries["accuracy"].mean == 1.0
        assert report.blocks == ()
    finally:
        del CLASS_BY_NAME["toy_demo"]
        del _SPEC_DEFAULTS["toy_demo"]
    assert "toy_demo" not in CLASS_BY_NAME


def test_register_problem_class_rejects_duplicates() -> None:
    try:
        register_problem_class(
            "toy_dup", _ToyClass, task="toy_task", dataset="toy_data"
        )
        try:
            register_problem_class(
                "toy_dup", _ToyClass, task="toy_task", dataset="toy_data"
            )
        except ValueError:
            pass
        else:
            raise AssertionError("duplicate problem class was admitted")
    finally:
        CLASS_BY_NAME.pop("toy_dup", None)
        _SPEC_DEFAULTS.pop("toy_dup", None)


def test_register_objective_flows_to_validation_and_kernel() -> None:
    register_objective("toy_speed", pareto_field="toy_ms", maximize=False)
    try:
        assert "toy_speed" in KNOWN_OBJECTIVES
        assert OBJECTIVE_FIELDS["toy_speed"] == ("toy_ms", False)
        assert "toy_speed" in objective_names()
        spec = Lab(seed=0).specify(
            "flat_classification", "gaussian_blob", objectives=("toy_speed",)
        )
        assert "toy_speed" in spec.objectives
    finally:
        KNOWN_OBJECTIVES.discard("toy_speed")
        OBJECTIVE_FIELDS.pop("toy_speed", None)
    assert "toy_speed" not in objective_names()


def test_register_objective_rejects_duplicates() -> None:
    try:
        register_objective("toy_dup_obj", pareto_field="toy_ms", maximize=False)
        try:
            register_objective("toy_dup_obj", pareto_field="toy_ms", maximize=False)
        except ValueError:
            pass
        else:
            raise AssertionError("duplicate objective was admitted")
    finally:
        KNOWN_OBJECTIVES.discard("toy_dup_obj")
        OBJECTIVE_FIELDS.pop("toy_dup_obj", None)


def test_register_curriculum() -> None:
    register_curriculum(CurriculumSpec(name="toy_switch", max_episodes=2))
    try:
        assert CURRICULA["toy_switch"].max_episodes == 2
        try:
            register_curriculum(CurriculumSpec(name="toy_switch"))
        except ValueError:
            pass
        else:
            raise AssertionError("duplicate curriculum was admitted")
    finally:
        del CURRICULA["toy_switch"]
    assert "toy_switch" not in CURRICULA


def test_extension_api_surface() -> None:
    for name in (
        "register_problem_class",
        "register_curriculum",
        "register_objective",
        "objective_names",
    ):
        assert callable(getattr(computronium_lab, name))
    assert set(objective_names()) >= {
        "accuracy",
        "adaptation_speed",
        "stability",
        "latency",
        "memory",
    }
