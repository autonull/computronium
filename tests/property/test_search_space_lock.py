"""Lock: the search space is computed from the spec, never tabulated (TODO46 §3.3).

The hand-rolled enumerator truncated every axis with a literal (``[:3]``,
``[:2]``), stamped ``Schedule(fidelity="L0", seed=42, ..., task_id="default")``
on every cell, and supplied hyperparameters from a 40-entry hand-maintained
table with seven ``input_dim: 784`` sites. This is the space those defects made
unfixable, stated as tests:

* the snapshot holds exactly the primitives the spec permits
* a spec that sweeps a hyperparameter yields cells at more than one value
* a swept value is carried only when the cell's own selection can use it
* the schedule comes from the spec, and its task is the spec's task
* the task's shape reaches geometry — never a literal
* a spec naming an unknown hyperparameter fails naming it
* the candidate stream is deterministic and duplicate-free
"""

from __future__ import annotations

import pytest

from computronium.experiment.execution.search_space import (
    generate_candidates,
    iter_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    Domain,
    Scale,
    StructuralAxis,
)
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.schema.harvest import harvest_schema
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec

_DIGITS_WIDTH = 64  # 8x8 flattened: the shape `digits` must reach geometry as


def _spec(**overrides: object) -> RunSpec:
    fields: dict[str, object] = {
        "profile": "lock",
        "task": "digits",
        "objectives": ("validation_accuracy",),
        "fidelity": "L0",
        "n_seeds": 1,
        "epochs": 2,
        "seed": 7,
    }
    fields.update(overrides)
    return RunSpec(**fields)  # type: ignore[arg-type]


def _narrowed_spec(
    *,
    dynamics: tuple[str, ...] = ("energy_minimization", "instantaneous"),
    credit: tuple[str, ...] = ("gradient", "pepita"),
    update: tuple[str, ...] = ("euclidean", "adam"),
    geometry: tuple[str, ...] = ("feedforward",),
    **overrides: object,
) -> RunSpec:
    return _spec(
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=geometry),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=dynamics),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=credit),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=update),
        ),
        **overrides,
    )


def test_snapshot_holds_exactly_the_specified_primitives() -> None:
    spec = _narrowed_spec(credit=("gradient",))
    space = search_space_from_spec(spec)
    assert space.primitives(StructuralAxis.CREDIT) == ("gradient",)
    assert len(space.primitives(StructuralAxis.SUBSTRATE)) == 1
    assert space.tasks == ("digits",)
    assert [o.name for o in space.objectives] == ["validation_accuracy"]


def test_unspecified_axis_keeps_every_available_primitive() -> None:
    space = search_space_from_spec(_spec())
    available = tuple(
        sorted(
            n for n, s in AXES_REGISTRIES[StructuralAxis.UPDATE].items() if s.available
        )
    )
    assert space.primitives(StructuralAxis.UPDATE) == available


def test_a_swept_hyperparameter_yields_more_than_one_value() -> None:
    """TODO43 R2: a searched coordinate is expressible and actually varies."""
    spec = _narrowed_spec(
        hyperparameters={"step_size": Domain(lo=1e-4, hi=1e-1, scale=Scale.LOG)}
    )
    space = search_space_from_spec(spec)
    cells = generate_candidates(spec, space, limit=20)
    values = {c.params["step_size"] for c, _ in cells}
    assert len(values) > 1, f"step_size never varied: {values}"
    assert min(values) == pytest.approx(1e-4)
    assert max(values) == pytest.approx(1e-1)


def test_unswept_hyperparameters_carry_no_dead_config() -> None:
    """The coordinate carries only what it sweeps; the harvest fills the rest."""
    spec = _narrowed_spec()
    cells = generate_candidates(spec, search_space_from_spec(spec), limit=5)
    assert [c.params for c, _ in cells] == [{}] * len(cells)


def test_a_swept_value_reaches_only_cells_that_can_use_it() -> None:
    """Availability decides: an inactive knob is not carried, then dropped at compose.

    ``beta`` is active only for settling dynamics (abc3 §3.1's availability
    predicate), so an ``instantaneous`` cell must not carry it even when the
    run sweeps it.
    """
    spec = _narrowed_spec(
        dynamics=("instantaneous", "energy_minimization"),
        credit=("thermodynamic_contrast",),
        hyperparameters={"beta": Domain(lo=0.01, hi=0.5, scale=Scale.LOG)},
    )
    space = search_space_from_spec(spec)
    cells = generate_candidates(spec, space, limit=12)
    assert cells
    for coordinate, _ in cells:
        active = harvest_schema().active(coordinate)
        assert not set(coordinate.params) & active.inactive
    settling = [c for c, _ in cells if c.dynamics == "energy_minimization"]
    plain = [c for c, _ in cells if c.dynamics == "instantaneous"]
    assert settling and all("beta" in c.params for c in settling)
    assert plain and all("beta" not in c.params for c in plain)


def test_schedule_comes_from_the_spec() -> None:
    spec = _narrowed_spec(fidelity="L1", epochs=4, n_seeds=3, seed=11, batch_limit=2)
    space = search_space_from_spec(spec)
    for _, schedule in generate_candidates(spec, space, limit=4):
        assert (schedule.fidelity, schedule.epochs) == ("L1", 4)
        assert (schedule.n_seeds, schedule.seed) == (3, 11)
        assert (schedule.batch_limit, schedule.task_id) == (2, "digits")


def test_a_spec_without_a_task_fails() -> None:
    """A run that measures no task is a run that measures nothing (D14)."""
    with pytest.raises(ValueError, match="names no task"):
        RunSpec(profile="lock", objectives=("validation_accuracy",))


def test_task_shape_reaches_geometry_not_a_literal() -> None:
    """The composed geometry's width is the task's, whatever the space was."""
    from computronium.experiment.execution.compose import compose_cell_system
    from computronium.experiment.execution.evaluate import task_shape

    spec = _narrowed_spec()
    coordinate, _ = generate_candidates(spec, search_space_from_spec(spec), limit=1)[0]
    shape = task_shape("digits")
    width = shape.input_dim
    cell = compose_cell_system(
        coordinate=coordinate,
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
    )
    assert cell.params["geometry.input_dim"] == width
    assert cell.params["geometry.input_dim"] != 784
    assert width == _DIGITS_WIDTH  # digits is 8x8; the plan's measured shape


def test_the_stream_is_deterministic_and_duplicate_free() -> None:
    spec = _narrowed_spec()
    space = search_space_from_spec(spec)
    first = generate_candidates(spec, space, limit=8)
    second = generate_candidates(spec, space, limit=8)
    keys = [c.measurement_key(s) for c, s in first]
    assert keys == [c.measurement_key(s) for c, s in second]
    assert len(set(keys)) == len(keys)


def test_two_axes_are_not_locked_to_each_other() -> None:
    """Every combination of two varying axes appears: no diagonal walk.

    Taking the k-th primitive on every axis advances two axes of equal length
    together, so a run declaring two dynamics x two geometries measures two
    cells and calls them four. The combinations are the property; the order
    they arrive in is not.
    """
    spec = _narrowed_spec(
        dynamics=("energy_minimization", "instantaneous"),
        credit=("gradient", "pepita"),
        geometry=("feedforward", "recurrent"),
    )
    cells = generate_candidates(spec, search_space_from_spec(spec), limit=64)
    pairs = {(c.dynamics, c.geometry) for c, _ in cells}

    assert pairs == {
        ("energy_minimization", "feedforward"),
        ("energy_minimization", "recurrent"),
        ("instantaneous", "feedforward"),
        ("instantaneous", "recurrent"),
    }


def test_every_declared_primitive_reaches_the_stream() -> None:
    """A narrowed axis is fully represented: no value is never proposed."""
    spec = _narrowed_spec(
        dynamics=("energy_minimization", "instantaneous", "diffusion"),
        credit=("gradient", "pepita", "homeostatic"),
        update=("euclidean", "adam", "lion"),
    )
    space = search_space_from_spec(spec)
    cells = generate_candidates(spec, space, limit=3 * 3 * 3)
    for axis, expected in (
        ("dynamics", {"energy_minimization", "instantaneous", "diffusion"}),
        ("credit", {"gradient", "pepita", "homeostatic"}),
        ("update", {"euclidean", "adam", "lion"}),
    ):
        assert {getattr(c, axis) for c, _ in cells} == expected


def test_a_spec_domain_outside_the_harvested_one_is_rejected() -> None:
    """The harvested declaration is the primitive's truth; a spec may only narrow."""
    harvested = harvest_schema().by_name()["step_size"].domain
    spec = _narrowed_spec(
        hyperparameters={
            "step_size": Domain(lo=1e9, hi=1e12, scale=Scale.LOG),
        }
    )
    assert float(harvested.hi) < 1e9  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="outside the harvested domain"):
        list(iter_candidates(spec, search_space_from_spec(spec)))


def test_an_unknown_hyperparameter_names_itself() -> None:
    with pytest.raises(ValueError, match="not_a_knob"):
        _spec(hyperparameters={"not_a_knob": Domain(lo=0.0, hi=1.0)})


def test_a_coordinate_carries_only_registered_primitives() -> None:
    spec = _narrowed_spec()
    space = search_space_from_spec(spec)
    for coordinate, _ in generate_candidates(spec, space, limit=6):
        assert isinstance(coordinate, Coordinate)
        for axis in StructuralAxis:
            primitive = getattr(coordinate, axis.value)
            assert primitive in AXES_REGISTRIES[axis]


_COMPOSABLE_TOPOLOGIES = (
    "feedforward",
    "recurrent",
    "attention",
    "causal_transformer",
    "tile",
    "tile_mesh",
    "conv",
    "spatial_lattice",
    "ntm",
)


@pytest.mark.parametrize("topology", _COMPOSABLE_TOPOLOGIES)
def test_each_topology_composes_as_itself(topology: str) -> None:
    """The coordinate's geometry primitive decides the topology, not a default.

    Reading the topology out of the geometry mapping defaulted every cell to
    ``feedforward``, so every non-MLP cell was compiled as an MLP and then
    rejected for carrying keys an MLP has no use for (D2's residual shape).
    """
    from computronium.experiment.execution.compose import (
        ProposalComposeError,
        compose_cell_system,
    )

    coordinate = Coordinate(
        substrate="digital",
        geometry=topology,
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params={},
    )
    cell = compose_cell_system(
        coordinate=coordinate, geometry={}, input_shape=(1, 8, 8), output_dim=10
    )
    assert cell.config.geometry.topology_type == topology
    with pytest.raises(ProposalComposeError, match="Unknown topology"):
        compose_cell_system(
            coordinate=Coordinate(**{**coordinate.to_dict(), "geometry": "nope"}),
            geometry={},
            input_shape=(1, 8, 8),
            output_dim=10,
        )


def test_every_generated_cell_composes_for_the_task_shape() -> None:
    """A proposed cell is one the evaluator can build: legality filters the space.

    Cross-axis legality lives in ``SystemConfig.validate``, so the space asks
    that mechanism rather than re-declaring its rules as availability
    predicates — a cell that cannot compose is not worth a training run.
    """
    from computronium.experiment.execution.compose import compose_configs
    from computronium.experiment.execution.evaluate import task_shape

    spec = _spec()
    cells = generate_candidates(
        spec, search_space_from_spec(spec), shape=task_shape, limit=12
    )
    # Variety across axes is not asserted here: the walk is a factorial, so a
    # short prefix shares its outer axes. `test_two_axes_are_not_locked_to_each
    # _other` states that property, and the campaign gate states it on records.
    assert len(cells) == 12
    shape = task_shape("digits")
    for coordinate, _ in cells:
        config = compose_configs(
            coordinate=coordinate,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
        )
        assert config.geometry.topology_type == coordinate.geometry


def test_the_stream_needs_no_shape_to_be_well_formed() -> None:
    """Without a resolver the stream is the same shape, minus the legality filter."""
    from computronium.experiment.execution.evaluate import TaskShape

    spec = _narrowed_spec()
    unfiltered = generate_candidates(spec, search_space_from_spec(spec), limit=5)
    filtered = generate_candidates(
        spec,
        search_space_from_spec(spec),
        limit=5,
        shape=lambda _: TaskShape((1, 8, 8), 10),
    )
    assert unfiltered == filtered
