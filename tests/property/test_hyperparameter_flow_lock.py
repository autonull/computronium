"""Lock: a swept hyperparameter reaches every cell that can read it.

TODO61 §11.1. The search space's ``_cell_params`` decided whether a swept value
was carried by asking each primitive's config factory whether it accepted the
name. That is true for every axis but geometry, whose harvested names
(``hidden_dim``, ``num_layers``) are bridged to the composer's own keys
(``hidden_dim``, ``depth``) rather than handed to a factory. Every budgeted run
auto-sweeps ``hidden_dim``, so under the factory test no cell ever carried it:
records lost the width they were trained at and the display read
``[no hyperparams]`` for every production cell.

Two claims, complementary:

* a swept geometry width reaches every cell, and composition honours it
* a swept geometry knob a topology cannot size is dropped, not carried as dead
  config the harvest would reject
"""

from __future__ import annotations

from computronium.experiment.kernel import (
    compose_cell_system,
    generate_candidates,
    search_space_from_spec,
    task_shape,
)
from computronium.experiment.schema import (
    AxisSelection,
    Domain,
    RunSpec,
    StructuralAxis,
)

_SLIM_AXES = (
    AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
    AxisSelection(
        axis=StructuralAxis.GEOMETRY, primitives=("feedforward", "recurrent")
    ),
    AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=("instantaneous",)),
    AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
    # A local credit: recurrent + instantaneous + gradient is void, so gradient
    # would hide the recurrent topology from the walk.
    AxisSelection(axis=StructuralAxis.CREDIT, primitives=("target_inversion",)),
    AxisSelection(axis=StructuralAxis.UPDATE, primitives=("euclidean",)),
)


def _spec(**overrides: object) -> RunSpec:
    fields: dict[str, object] = {
        "profile": "flow",
        "task": "digits",
        "objectives": ("validation_accuracy",),
        "epochs": 1,
        "seed": 7,
        "param_budget": 10_000,
        "axes": _SLIM_AXES,
    }
    fields.update(overrides)
    return RunSpec(**fields)  # type: ignore[arg-type]


def test_a_swept_geometry_width_reaches_every_cell_it_can_size() -> None:
    """Every cell of a budgeted run carries the width it is composed at."""
    spec = _spec()
    assert "geometry.hidden_dim" in spec.hyperparameters  # the auto-narrow added it
    cells = generate_candidates(
        spec, search_space_from_spec(spec), shape=task_shape, limit=10
    )
    assert cells
    shape = task_shape("digits")
    for coordinate, schedule in cells:
        assert "geometry.hidden_dim" in coordinate.params, (
            f"a swept width is missing for {coordinate.geometry}: {coordinate.params}"
        )
        cell = compose_cell_system(
            coordinate=coordinate,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=schedule.param_budget,
        )
        width = int(float(coordinate.params["geometry.hidden_dim"]))
        assert cell.config.geometry.hidden_dims[0] == width, (
            "composition ignored the swept width"
        )


def test_a_swept_geometry_knob_a_topology_cannot_size_is_dropped() -> None:
    """``residual`` sizes a feedforward stack only; a recurrent cell must not carry it."""
    spec = _spec(
        hyperparameters={"geometry.residual": Domain(members=(True, False))},
    )
    cells = generate_candidates(
        spec, search_space_from_spec(spec), shape=task_shape, limit=200
    )
    feedforward = [c for c, _ in cells if c.geometry == "feedforward"]
    recurrent = [c for c, _ in cells if c.geometry == "recurrent"]
    assert feedforward and recurrent, "the walk must expose both topologies"
    assert all("geometry.residual" in c.params for c in feedforward)
    assert all("geometry.residual" not in c.params for c in recurrent)
