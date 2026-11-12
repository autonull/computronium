"""Lock: the space refuses a cell the pipeline cannot train honestly (N1).

Two refusals the TODO88 credit sweep needed:

1. **Graph tasks are graph-geometry exclusive.** ``GraphSystemTrainer`` calls
   ``system.forward(x, edge_index, batch)`` on every step, so a graph task on
   feedforward/recurrent/causal-transformer geometry dies inside the forward
   signature (Experiment 13: five FAILs, all ``…forward() takes from 2 to 3
   positional arguments``).
2. **``local_contrastive`` is unavailable.** Its contract reads the label from
   the last ``label_dim`` input features; the kernel gives it the task's own
   width, so it sliced the last 10 pixels as the "label" and trained a
   contrast against noise (mnist 0.11-0.12 over 10 epochs, loss 17 -> 3459).
   The row is excluded until the label channel and label-sweep readout exist.

Falsified by reverting either: the forward-signature cell is proposed again, or
the credit row is available and a sweep spends cells on chance-level training.
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


def test_local_contrastive_row_is_unavailable_with_a_reason() -> None:
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    spec = get_axis_spec(StructuralAxis.CREDIT, "local_contrastive")
    assert spec is not None
    assert spec.available is False
    assert "label-augmented" in (spec.unavailable_reason or "")


def test_a_space_declaring_local_contrastive_holds_no_credit() -> None:
    """A declaration that names it measures zero cells, not chance-level ones."""
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
    assert space.primitives(StructuralAxis.CREDIT) == ()
