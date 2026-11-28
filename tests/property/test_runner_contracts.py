"""W64: the four experiment runners, locked on the rules they decide.

``experiment/runners`` was imported by no test at all (0% of its statements),
so every rule below was unchecked: a scaling grid could repeat a point, an
ablation variant could pin an axis it was told to fix, a replay could call a
drop in a metric "stable", and a comparison could raise where it should
refuse. Each is a *decision* the runner makes, not an artifact it produced, so
each is asserted directly — no store, no training cell (D6).
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest

from computronium.experiment.runners.ablation import AblationRunner, AblationSpec
from computronium.experiment.runners.comparison import ComparisonRunner, ComparisonSpec
from computronium.experiment.runners.replay import classify_changes
from computronium.experiment.runners.scaling import (
    ScalingRunner,
    ScalingSpec,
    _spaced_values,
)
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate

_ABLATION_SPEC = {
    "vary": StructuralAxis.CREDIT,
    "fix": {StructuralAxis.GEOMETRY: "feedforward"},
    "n_seeds": 1,
}
_BASE_COORD = Coordinate(
    substrate="digital",
    geometry="feedforward",
    dynamics="instantaneous",
    plasticity="null",
    credit="gradient",
    update="euclidean",
    params={"hidden_dims": 16},
)


def test_the_scaling_grid_is_the_declared_product() -> None:
    """Every factor value appears in every combination, once."""
    runner = ScalingRunner(
        ScalingSpec(vary=["hidden_dims", "beta"], n_points_per_dim=3, n_seeds=1)
    )
    grid = runner._generate_parameter_grid()

    assert len(grid) == 9
    assert len({tuple(sorted(cell.items())) for cell in grid}) == 9
    betas = sorted({cell["beta"] for cell in grid})
    assert betas[0] == 0.1
    assert betas[-1] == 2.0
    assert math.isclose(betas[1], 0.1 * 20**0.5)
    assert all(isinstance(cell["hidden_dims"], int) for cell in grid)
    assert {cell["hidden_dims"] for cell in grid} == {16, 91, 512}


def test_a_log_spaced_axis_keeps_its_ratio_and_endpoints() -> None:
    values = _spaced_values(16.0, 512.0, 5, log_scale=True)

    assert values[0] == 16.0
    assert values[-1] == 512.0
    ratios = [b / a for a, b in itertools.pairwise(values)]
    assert all(math.isclose(r, ratios[0]) for r in ratios)


def test_one_point_per_dimension_is_the_low_end() -> None:
    """A single point is a grid of one cell, not a division by zero."""
    runner = ScalingRunner(ScalingSpec(vary=["hidden_dims"], n_points_per_dim=1))
    assert runner._generate_parameter_grid() == [{"hidden_dims": 16}]


def test_a_scaled_coordinate_keeps_the_axes_it_did_not_sweep() -> None:
    runner = ScalingRunner(ScalingSpec(vary=["beta"]))
    scaled = runner._build_coordinate_with_params(_BASE_COORD, {"beta": 0.5})

    assert scaled.params == {"hidden_dims": 16, "beta": 0.5}
    for axis in StructuralAxis:
        assert getattr(scaled, axis.value) == getattr(_BASE_COORD, axis.value)


def test_a_replay_cell_is_classified_by_its_worst_metric() -> None:
    """A drop outranks a rise: a cell that lost accuracy is not 'improved'."""
    split = classify_changes(
        {"accuracy": 0.80, "walltime_total": 1.5},
        {"accuracy": 0.90, "walltime_total": 1.0},
        ["accuracy", "walltime_total"],
        tolerance=0.02,
    )

    assert [m["metric"] for m in split["regressed"]] == ["accuracy"]
    assert [m["metric"] for m in split["improved"]] == ["walltime_total"]
    assert split["stable"] == []


def test_a_replay_metric_without_a_baseline_is_not_stable() -> None:
    """An incomparable metric is absent from the split, not counted as equal."""
    split = classify_changes(
        {"accuracy": 0.9, "walltime_total": 5.0, "epochs_run": 3.0},
        {"accuracy": 0.9},
        ["accuracy", "walltime_total", "epochs_run"],
        tolerance=0.02,
    )

    assert [m["metric"] for m in split["stable"]] == ["accuracy"]
    assert split["regressed"] == []
    assert split["improved"] == []


def test_a_replay_skips_a_zero_baseline() -> None:
    split = classify_changes({"loss": 1.0}, {"loss": 0.0}, ["loss"], tolerance=0.02)

    assert split == {"regressed": [], "improved": [], "stable": []}


def test_an_ablation_variant_pins_only_the_varied_axis() -> None:
    runner = AblationRunner(AblationSpec(**_ABLATION_SPEC))
    variant = runner._build_variant_spec("gradient")
    pinned = {selection.axis: selection.primitives for selection in variant.axes}

    assert pinned[StructuralAxis.CREDIT] == ("gradient",)
    assert pinned[StructuralAxis.GEOMETRY] == ("feedforward",)
    assert len(pinned[StructuralAxis.UPDATE] or ()) > 1
    assert variant.n_seeds == runner.spec.n_seeds


def test_an_ablation_variant_is_not_the_base_spec() -> None:
    runner = AblationRunner(AblationSpec(**_ABLATION_SPEC))

    assert runner._build_variant_spec("gradient") != runner.base_spec
    assert runner._build_variant_spec("gradient") != runner._build_variant_spec(
        "pepita"
    )


def test_a_missing_arm_cannot_be_compared() -> None:
    """No samples is 'no evidence' (p = 1), never an exception."""
    runner = ComparisonRunner(
        ComparisonSpec(
            arm_a={StructuralAxis.CREDIT: "gradient"},
            arm_b={StructuralAxis.UPDATE: "euclidean"},
            n_seeds=1,
        )
    )

    assert runner._statistical_test([], [0.5, 0.6], "t_test") == 1.0
    assert runner._statistical_test([0.5], [], "bootstrap") == 1.0


def test_an_unknown_test_is_refused_by_name() -> None:
    runner = ComparisonRunner(
        ComparisonSpec(
            arm_a={StructuralAxis.CREDIT: "gradient"},
            arm_b={StructuralAxis.UPDATE: "euclidean"},
            n_seeds=1,
        )
    )

    with pytest.raises(ValueError, match="wilcoxon"):
        runner._statistical_test([0.5], [0.6], "wilcoxon")


def test_the_bootstrap_separates_a_shift_from_an_empty_difference() -> None:
    """A separated arm is significant; identical samples cannot be."""
    runner = ComparisonRunner(
        ComparisonSpec(
            arm_a={StructuralAxis.CREDIT: "gradient"},
            arm_b={StructuralAxis.UPDATE: "euclidean"},
            n_seeds=5,
        )
    )

    np.random.seed(0)
    shifted = runner._bootstrap_test([10.0] * 5, [0.0] * 5, n_iter=2000)
    same = runner._bootstrap_test([0.7] * 5, [0.7] * 5, n_iter=2000)

    assert shifted < 0.05
    assert same == 1.0
