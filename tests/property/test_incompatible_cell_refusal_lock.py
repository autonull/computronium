"""Lock: the space refuses a cell the pipeline cannot train honestly (N1).

**Graph tasks are graph-geometry exclusive.** ``GraphSystemTrainer`` calls
``system.forward(x, edge_index, batch)`` on every step, so a graph task on
feedforward/recurrent/causal-transformer geometry dies inside the forward
signature (Experiment 13: five FAILs, all ``…forward() takes from 2 to 3
positional arguments``).

The second refusal this lock carried — ``local_contrastive`` unavailable for
want of a label channel — is gone: N7 wired the channel
(``tests/property/test_label_channel_lock.py`` now owns that case).

Falsified by reverting the filter: the forward-signature cell is proposed again.
"""

from __future__ import annotations

from computronium.experiment.kernel.evaluate import task_shape
from computronium.experiment.kernel.search_space import (
    _is_geometry_task_compatible,
    search_space_from_spec,
)
from computronium.experiment.schema import (
    AxisSelection,
    RunSpec,
    StructuralAxis,
    get_axis_spec,
)

from ._specs import mechanism_spec


def test_graph_task_trains_only_on_graph_geometry() -> None:
    """A graph task rejects every node-mode geometry."""
    shape = task_shape("cora", "cpu")
    assert _is_geometry_task_compatible("graph", shape, "cora")
    for geometry in ("feedforward", "recurrent", "causal_transformer"):
        assert not _is_geometry_task_compatible(geometry, shape, "cora"), geometry


def test_non_graph_task_rejects_graph_geometry() -> None:
    """The converse: a vision task cannot supply an edge index."""
    shape = task_shape("mnist", "cpu")
    assert not _is_geometry_task_compatible("graph", shape, "mnist")
    assert _is_geometry_task_compatible("feedforward", shape, "mnist")


def test_local_contrastive_is_available_again() -> None:
    """N7 reverted G11: the credit has a label channel, so it is measurable."""
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    spec = get_axis_spec(StructuralAxis.CREDIT, "local_contrastive")
    assert spec is not None
    assert spec.available is True
    assert spec.unavailable_reason is None


def test_a_space_declaring_local_contrastive_holds_the_credit() -> None:
    """The row is proposed, not silently emptied out of the declaration."""
    base = mechanism_spec()
    spec = RunSpec(**{
        **base.model_dump(),
        "axes": tuple(
            AxisSelection(axis=StructuralAxis.CREDIT, primitives=("local_contrastive",))
            if selection.axis is StructuralAxis.CREDIT
            else selection
            for selection in base.axes
        ),
    })
    space = search_space_from_spec(spec, tasks=spec.task_names)
    assert space.primitives(StructuralAxis.CREDIT) == ("local_contrastive",)


def test_local_goodness_is_void_on_energy_minimization() -> None:
    """The FF goodness contrast stops being local when the settle unrolls.

    Measured (N9): same cell, mnist feedforward, 3 epochs — instantaneous
    0.9628, energy_minimization 0.0892 with free loss 1.87 -> 2.1e5.
    """
    from computronium.experiment.kernel.search_space import _compiled_void_constraints

    indep, _ = _compiled_void_constraints()
    compiled = dict(indep)
    name = "local_goodness_energy_minimization"
    assert name in compiled

    order = list(StructuralAxis)

    def selection(**overrides: str) -> tuple[str, ...]:
        values = {
            "substrate": "digital",
            "geometry": "feedforward",
            "dynamics": "instantaneous",
            "plasticity": "null",
            "credit": "local_goodness",
            "update": "adam",
            **overrides,
        }
        return (*tuple(values[axis.value] for axis in order), "")

    assert compiled[name](selection()) is True
    assert compiled[name](selection(dynamics="energy_minimization")) is False
    assert compiled[name](selection(credit="gradient", dynamics="energy_minimization"))
    assert compiled[name](selection()) is True
