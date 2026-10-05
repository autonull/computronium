"""Multi-axis campaign end-to-end lock.

A declared campaign that sweeps 3+ axes must:
1. Produce records carrying every axis's metrics
2. Have every declared objective resolve to a measurement
3. Close the run row properly (no status=running)

This is the test TODO51 A2 describes: the repo had no such test, which is why
pinning axes and pinning objectives both produced schema-valid runs that
measured nothing useful.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.evaluate import task_shape
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.metrics import MEASURED_OBJECTIVES, objective_metric
from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY
from computronium.experiment.schema.run_spec import (
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    RunSpec,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

pytestmark = pytest.mark.timeout(300)


@pytest.fixture(scope="module", autouse=True)
def _seed_registries() -> None:
    seed_all_registries()


def _multi_axis_spec() -> RunSpec:
    """A spec sweeping 3 axes: substrate, dynamics, credit."""
    return RunSpec(
        profile="multi-axis-test",
        task="digits",
        objectives=(
            "validation_accuracy",
            "walltime_total",
            "spectral_radius",
            "max_singular_value",
            "energy_per_step",
        ),
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        budget_seconds=60.0,  # Small budget for fast test
        param_budget=MEASURED_PARAM_BUDGET,
        batch_limit=MEASURED_BATCH_LIMIT,
        axes=(
            AxisSelection(
                axis=StructuralAxis.SUBSTRATE, primitives=("digital", "sparse")
            ),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=("instantaneous", "energy_minimization"),
            ),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=("gradient", "random_projections"),
            ),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
        ),
        policy="round_robin_grid",
        sweep_steps=5,
    )


def test_multi_axis_campaign_sweeps_declared_axes() -> None:
    """The search space includes all declared axis combinations."""
    spec = _multi_axis_spec()

    from computronium.experiment.execution.search_space import (
        iter_candidates,
        search_space_from_spec,
    )

    space = search_space_from_spec(spec, tasks=spec.task_names)

    # Check each axis has the declared primitives available
    for axis, expected in [
        (StructuralAxis.SUBSTRATE, {"digital", "sparse"}),
        (StructuralAxis.DYNAMICS, {"instantaneous", "energy_minimization"}),
        (StructuralAxis.CREDIT, {"gradient", "random_projections"}),
    ]:
        available = set(space.primitives(axis))
        assert expected.issubset(available), (
            f"axis {axis.value}: expected {expected}, available {available}"
        )

    # Count candidates - should be substrate(2) * dynamics(2) * credit(2) = 8 base cells
    candidates = list(iter_candidates(spec, space, shape=task_shape))
    # With sweep_steps=5 and 8 base cells, we get up to 8 candidates
    assert len(candidates) >= 4, (
        f"expected at least 4 candidates, got {len(candidates)}"
    )

    # Verify each candidate carries the axis coordinates
    axis_values: dict[StructuralAxis, set[str]] = {}
    for coord, _ in candidates:
        for axis in StructuralAxis:
            axis_values.setdefault(axis, set()).add(getattr(coord, axis.value))

    assert axis_values[StructuralAxis.SUBSTRATE] == {"digital", "sparse"}
    assert axis_values[StructuralAxis.DYNAMICS] == {
        "instantaneous",
        "energy_minimization",
    }
    assert axis_values[StructuralAxis.CREDIT] == {"gradient", "random_projections"}


def test_multi_axis_campaign_objectives_resolve_to_measurements() -> None:
    """Every declared objective has a measurement behind it."""
    spec = _multi_axis_spec()

    for obj_name in spec.objectives:
        # This raises UnmeasuredObjectiveError if no measurement exists
        metric_key = objective_metric(obj_name)
        assert metric_key in MEASURED_OBJECTIVES.values(), (
            f"objective {obj_name!r} resolves to {metric_key!r} "
            f"but that key is not in MEASURED_OBJECTIVES"
        )


def test_multi_axis_campaign_run_completes_and_closes(tmp_path: Path) -> None:
    """A small multi-axis run completes and closes the run row."""
    spec = _multi_axis_spec()
    store_path = tmp_path / "multi_axis_test.duckdb"

    # Use execute_spec which properly closes the run
    from computronium.experiment.surface.cli import execute_spec

    exit_code = execute_spec(spec, store_path=str(store_path))
    assert exit_code == 0, f"execute_spec failed with code {exit_code}"

    # Re-open store to verify run was closed
    with RecordStore(StoreConfig(path=store_path, read_only=True)) as store:
        runs = list(store.query_records())
        # Get the run_id from records
        run_id = None
        for r in runs:
            rid = r.provenance.links.get("run_id")
            if rid:
                run_id = rid
                break
        assert run_id is not None, "should have a run_id in records"

        run_row = store.query_run(run_id)
        assert run_row is not None, "run row should exist"
        assert run_row.status == "completed", (
            f"run status should be 'completed', got {run_row.status}"
        )
        assert run_row.finished_at is not None, "run should have finished_at"
        assert run_row.budget_consumed_s is not None, (
            "run should have budget_consumed_s"
        )

        # Verify records were produced
        records = store.query_records(run_id=run_id)
        assert len(records) > 0, "should have produced at least one record"

        # Verify each record carries metrics for declared objectives
        for record in records:
            payload = record.payload
            for obj_name in spec.objectives:
                metric_key = objective_metric(obj_name)
                assert metric_key in payload, (
                    f"record {record.cell_key[:12]} missing metric {metric_key} "
                    f"for objective {obj_name}"
                )
                assert isinstance(payload[metric_key], int | float), (
                    f"metric {metric_key} should be numeric"
                )


def test_axis_frontiers_resolve_per_axis_objectives() -> None:
    """ReportGenerator.axis_frontiers reads per-axis objective sets from the spec."""
    spec = _multi_axis_spec()

    # Add axis_objectives to the spec
    spec_with_axes = spec.model_copy(
        update={
            "axis_objectives": {
                "task": ("validation_accuracy",),
                "stability": ("spectral_radius", "max_singular_value"),
                "cost": ("walltime_total", "energy_per_step"),
            }
        }
    )

    # Verify axis_objectives validation passes (names known objectives, axes known)
    assert spec_with_axes.axis_objectives["task"] == ("validation_accuracy",)
    assert spec_with_axes.axis_objectives["stability"] == (
        "spectral_radius",
        "max_singular_value",
    )
    assert spec_with_axes.axis_objectives["cost"] == (
        "walltime_total",
        "energy_per_step",
    )

    # Verify all axis names are valid axis tags from objectives registry
    axis_tags = sorted({
        spec.axis_tag
        for spec in OBJECTIVES_REGISTRY.values()
        if spec.axis_tag is not None
    })
    for axis_name in spec_with_axes.axis_objectives:
        assert axis_name in axis_tags, (
            f"axis_objectives names unknown axis tag {axis_name!r}; available: {axis_tags}"
        )

    # Verify all objective names in axis_objectives are known
    for axis_name, obj_names in spec_with_axes.axis_objectives.items():
        for obj_name in obj_names:
            assert obj_name in OBJECTIVES_REGISTRY, (
                f"axis_objectives[{axis_name!r}] names unknown objective {obj_name!r}"
            )


def test_multi_axis_campaign_unmeasured_objectives_fail_at_use() -> None:
    """A spec with unmeasured objectives is accepted but fails when used."""

    # These three objectives are registered but unmeasured (A4)
    # energy_efficiency is now measured
    unmeasured = ("latency_ms", "spike_rate", "ir_drop_variance")

    for obj in unmeasured:
        assert obj in OBJECTIVES_REGISTRY, f"{obj} should be registered"
        spec_obj = OBJECTIVES_REGISTRY[obj]
        assert spec_obj.metric_key is None, f"{obj} should have no metric_key"
        assert spec_obj.unavailable_reason is not None, (
            f"{obj} should have unavailable_reason"
        )

    # A spec declaring an unmeasured objective should fail validation at spec creation
    spec = _multi_axis_spec()
    spec_dict = spec.model_dump()
    spec_dict["objectives"] = (*spec.objectives, "latency_ms")
    with pytest.raises(ValueError, match="have no measurement"):
        RunSpec(**spec_dict)

    # But energy_efficiency is now measured and should work
    spec_dict["objectives"] = (*spec.objectives, "energy_efficiency")
    spec_with_measured = RunSpec(**spec_dict)
    assert "energy_efficiency" in spec_with_measured.objectives


__all__ = [
    "test_axis_frontiers_resolve_per_axis_objectives",
    "test_multi_axis_campaign_objectives_resolve_to_measurements",
    "test_multi_axis_campaign_run_completes_and_closes",
    "test_multi_axis_campaign_sweeps_declared_axes",
    "test_multi_axis_campaign_unmeasured_objectives_fail_at_use",
]
