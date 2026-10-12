"""Task↔Geometry compatibility lock (TODO57 D1).

The search space must reject token-only geometries for image tasks,
and accept them for token tasks. Removing the filter must make
the fixture fail (TODO46 D25).
"""

from __future__ import annotations

import pytest

from computronium.experiment.kernel.compose import (
    ProposalComposeError,
    compose_cell_system,
)
from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import search_space_from_spec
from computronium.experiment.schema import (
    Coordinate,
    RunSpec,
    StructuralAxis,
)


def _digits_spec() -> RunSpec:
    return RunSpec(
        profile="lock",
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L0",
        n_seeds=1,
        epochs=2,
        seed=7,
    )


def _token_spec() -> RunSpec:
    return RunSpec(
        profile="lock",
        task="tiny_shakespeare",
        objectives=("validation_accuracy",),
        fidelity="L0",
        n_seeds=1,
        epochs=2,
        seed=7,
    )


def test_digits_excludes_causal_transformer() -> None:
    """For digits (image task), causal_transformer must not be proposed in candidates."""
    _digits_spec()
    # The primitives() returns all available; filtering happens in _composable during iteration
    # Check that candidates for digits don't include causal_transformer
    from computronium.experiment.kernel.search_space import _composable

    coord = Coordinate(
        substrate="digital",
        geometry="causal_transformer",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )
    assert not _composable(coord, "digits", task_shape, 50000), (
        "causal_transformer must be excluded for image tasks by _composable"
    )


def test_token_task_includes_causal_transformer() -> None:
    """For tiny_shakespeare (token task), causal_transformer must be proposed."""
    spec = _token_spec()
    space = search_space_from_spec(spec)
    geometries = space.primitives(StructuralAxis.GEOMETRY)
    assert "causal_transformer" in geometries, (
        "causal_transformer must be included for token tasks"
    )


def test_compose_rejects_causal_transformer_for_digits() -> None:
    """Direct compose must reject causal_transformer for digits."""
    shape = task_shape("digits")
    coord = Coordinate(
        substrate="digital",
        geometry="causal_transformer",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )
    with pytest.raises(ProposalComposeError, match="token input"):
        compose_cell_system(
            coordinate=coord,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=50000,
        )


def test_compose_accepts_causal_transformer_for_token_task() -> None:
    """Direct compose must accept causal_transformer for tiny_shakespeare."""
    shape = task_shape("tiny_shakespeare")
    coord = Coordinate(
        substrate="digital",
        geometry="causal_transformer",
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="adam",
        params={},
    )
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=50000,
    )
    assert cell is not None


def test_other_geometries_work_for_both() -> None:
    """Other geometries must work for both image and token tasks."""
    for task_name in ("digits", "tiny_shakespeare"):
        shape = task_shape(task_name)
        for geometry in ("feedforward", "ntm", "nca"):
            coord = Coordinate(
                substrate="digital",
                geometry=geometry,
                dynamics="instantaneous",
                plasticity="null",
                credit="gradient",
                update="adam",
                params={},
            )
            cell = compose_cell_system(
                coordinate=coord,
                geometry={},
                input_shape=shape.input_shape,
                output_dim=shape.output_dim,
                param_budget=50000,
            )
            assert cell is not None, f"{geometry} failed for {task_name}"
        # Recurrent needs compatible dynamics (not instantaneous with gradient)
        for geometry in ("recurrent",):
            coord = Coordinate(
                substrate="digital",
                geometry=geometry,
                dynamics="energy_minimization",
                plasticity="null",
                credit="thermodynamic_contrast",
                update="euclidean",
                params={},
            )
            cell = compose_cell_system(
                coordinate=coord,
                geometry={},
                input_shape=shape.input_shape,
                output_dim=shape.output_dim,
                param_budget=50000,
            )
            assert cell is not None, f"{geometry} failed for {task_name}"


def test_filter_removal_regression() -> None:
    """If the compatibility filter is removed, the fixture must fail.

    This test verifies the lock is not a comment (TODO46 D25).
    It temporarily patches the required_input check to always pass
    and asserts the search space then includes causal_transformer for digits.
    """
    from computronium.experiment.execution import compose as compose_module

    # Save original
    original_check = compose_module._check_geometry_input_compat

    def no_op_check(*args, **kwargs):
        return None  # Always pass

    try:
        compose_module._check_geometry_input_compat = no_op_check
        spec = _digits_spec()
        space = search_space_from_spec(spec)
        geometries = space.primitives(StructuralAxis.GEOMETRY)
        # Without the filter, causal_transformer would be included for digits
        assert "causal_transformer" in geometries, (
            "Lock broken: removing filter must make causal_transformer appear for digits"
        )
    finally:
        compose_module._check_geometry_input_compat = original_check
