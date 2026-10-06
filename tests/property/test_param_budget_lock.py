"""Lock: a declared parameter ceiling sizes the cell, and the cell honours it.

TODO46 §8 session 6, the first of the remaining-work items. Three claims, each
of which was false before:

* a spec's ceiling reaches the composition **and** the space, so the space
  never screens a small cell for a run that will train a large one
* derived sizing is fitted against the built module's parameter count, not
  against an estimate of it — the estimators under-counted conv (channels
  alone, no spatial extent) and NTM (memory slots alone), so a cell was
  declared legal at four times its ceiling
* a cell that cannot honour its ceiling does not pass the gate, and says so

The geometry rows are here too, because a registered primitive the kernel cannot
train is a claim the run makes and then withdraws per cell (``tile`` had a
backend alias and no factory; ``nca`` has a state-grid contract the trainer
does not meet, and is retired with its reason recorded).
"""

from __future__ import annotations

import pytest

from computronium.experiment.execution.compose import (
    compose_cell_system,
    geometry_param_count,
)
from computronium.experiment.execution.evaluate import cell_record, task_shape
from computronium.experiment.execution.search_space import (
    generate_candidates,
    search_space_from_spec,
)
from computronium.experiment.schema import (
    AXES_REGISTRIES,
    StructuralAxis,
    Coordinate,
    Provenance,
    Schedule,
    FailureCause,
    GateVerdict,
    PARAM_BUDGET_TOLERANCE,
    MEASURED_PARAM_BUDGET,
    RunSpec,
)

_TRAINABLE_TOPOLOGIES = (
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

# A cell over this ceiling cannot be composed at any budget: the floor of a
# geometry is larger than the budget itself, which is how the gate is exercised
# without a huge cell.
_UNREACHABLE_CEILING = 10


def _spec(param_budget: int = MEASURED_PARAM_BUDGET) -> RunSpec:
    return RunSpec(
        profile="ceiling",
        task="digits",
        objectives=("validation_accuracy",),
        epochs=1,
        param_budget=param_budget,
    )


def _coordinate(topology: str, **params: object) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry=topology,
        dynamics="instantaneous",
        plasticity="null",
        credit="gradient",
        update="euclidean",
        params=dict(params),
    )


def _schedule(param_budget: int = MEASURED_PARAM_BUDGET) -> Schedule:
    return Schedule(
        fidelity="L0",
        seed=0,
        n_seeds=1,
        epochs=1,
        batch_limit=2,
        budget_id="ceiling",
        task_id="digits",
        param_budget=param_budget,
    )


def _provenance() -> Provenance:
    return Provenance(
        env={},
        dataset="digits",
        dataset_version="1.0",
        code_sha="test",
        policy="test",
        links={"run_id": "ceiling"},
    )


@pytest.mark.parametrize("topology", _TRAINABLE_TOPOLOGIES)
def test_a_ceiling_bounds_every_trainable_geometry(topology: str) -> None:
    """Derived sizing is fitted to the built module, so every cell fits."""
    shape = task_shape("digits")
    cell = compose_cell_system(
        coordinate=_coordinate(topology),
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=MEASURED_PARAM_BUDGET,
    )
    assert cell.param_count <= MEASURED_PARAM_BUDGET * (1 + PARAM_BUDGET_TOLERANCE)
    assert cell.param_count == geometry_param_count(cell.config.geometry)


def test_the_space_screens_at_the_size_the_run_will_train() -> None:
    """A proposed cell is one the evaluator can build *and* afford."""
    spec = _spec()
    cells = generate_candidates(
        spec, search_space_from_spec(spec), shape=task_shape, limit=8
    )
    assert cells
    shape = task_shape("digits")
    for coordinate, schedule in cells:
        assert schedule.param_budget == MEASURED_PARAM_BUDGET
        cell = compose_cell_system(
            coordinate=coordinate,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=schedule.param_budget,
        )
        assert cell.param_count <= MEASURED_PARAM_BUDGET * (1 + PARAM_BUDGET_TOLERANCE)


def test_a_ceiling_changes_the_measurement_not_the_cell() -> None:
    """The ceiling is part of the schedule, so cells differing only by it differ."""
    coordinate = _coordinate("feedforward")
    bounded, unbounded = _schedule(), _schedule(0)
    assert coordinate.cell_key() == coordinate.cell_key()
    assert coordinate.measurement_key(bounded) != coordinate.measurement_key(unbounded)
    assert bounded.to_dict()["param_budget"] == MEASURED_PARAM_BUDGET
    assert Schedule.from_dict(bounded.to_dict()) == bounded


def test_a_swept_width_is_honoured_while_the_ceiling_sizes_the_depth() -> None:
    """Honouring one knob must not silently discard the other."""
    shape = task_shape("digits")
    cell = compose_cell_system(
        coordinate=_coordinate("feedforward", hidden_dim=16),
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=MEASURED_PARAM_BUDGET,
    )
    assert cell.config.geometry.hidden_dims == (16,) * cell.config.geometry.num_layers


def test_a_cell_that_cannot_honour_its_ceiling_does_not_pass() -> None:
    """A ceiling nobody can meet is reported, not absorbed."""
    record = cell_record(
        _coordinate("feedforward"), _schedule(_UNREACHABLE_CEILING), _provenance(), {}
    )
    assert record.status.gate_verdict is GateVerdict.FAIL
    assert str(_UNREACHABLE_CEILING) in record.status.defect
    assert record.status.cause is FailureCause.CONSTRAINT_VIOLATION


def test_the_tolerance_is_declared_once() -> None:
    """The registered predicate and the gate read the same number."""
    from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY

    predicate = str(CONSTRAINTS_REGISTRY["param_budget_fairness"].predicate)
    assert str(1 + PARAM_BUDGET_TOLERANCE) in predicate


def test_the_task_shape_reaches_a_spatial_topology() -> None:
    """Conv channels and extent are the task's, not 3x28x28 (D16)."""
    shape = task_shape("digits")
    cell = compose_cell_system(
        coordinate=_coordinate("conv"),
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=MEASURED_PARAM_BUDGET,
    )
    assert cell.config.geometry.in_channels == shape.input_shape[0]
    assert cell.config.geometry.input_hw == shape.input_shape[1:]


@pytest.mark.parametrize("name", ("tile", "tile_mesh", "conv", "ntm"))
def test_a_registered_geometry_is_composable(name: str) -> None:
    """A registered row the composer cannot build is a claim the run withdraws."""
    assert AXES_REGISTRIES[StructuralAxis.GEOMETRY][name].available
    shape = task_shape("digits")
    cell = compose_cell_system(
        coordinate=_coordinate(name),
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
    )
    assert cell.config.geometry.topology_type == name


def test_an_unhonourable_primitive_is_retired_with_its_reason() -> None:
    """R78: a retired row is excluded from the space and says why (nca)."""
    spec = _spec()
    nca = AXES_REGISTRIES[StructuralAxis.GEOMETRY]["nca"]
    assert not nca.available
    assert "NcaGeometry.step" in (nca.unavailable_reason or "")
    assert "nca" not in search_space_from_spec(spec).primitives(StructuralAxis.GEOMETRY)


def test_the_geometry_alias_table_does_not_grow() -> None:
    """``_GEOMETRY_ALIASES`` is a §3.0 violation in miniature; hold it at one."""
    from computronium.experiment.execution.compose import _GEOMETRY_ALIASES

    assert _GEOMETRY_ALIASES == {"num_layers": "depth"}
