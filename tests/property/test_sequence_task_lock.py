"""Locks for the schedulable time axis (TODO93 §8.1 row 1b).

The temporal build landed the sequence geometry, the time-major loader, and the
per-step loss, but ``delayed_cue`` was a fixture: no registry row meant a run
could not name it, the declared space did not reflect its loader, and the smoke
cell it trained was not the cell the axis reads. These locks are the
registration:

1. the task is schedulable and its enriched row declares the axis;
2. its declared space admits only a cell that reads the time axis, and a flat
   task refuses a sequence credit (both directions of one rule);
3. the loader's own declaration agrees with the batch it emits;
4. the smoke cell, built from the declared space, reports a bar verdict — the
   axis is reachable from a run rather than only from a fixture;
5. the settle Jacobian refuses a time-major state (it has no fixed point).
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
import torch

_TREATMENT = "eligibility_prop"
_SEQUENCE_CREDITS = frozenset({"eligibility_prop", "rtrl_reference", "unbiased_rtrl"})


def _registry():
    from computronium.experiment.registry.task_registry import get_task_registry

    return get_task_registry()


@pytest.mark.timeout(60)
def test_delayed_cue_is_a_schedulable_task() -> None:
    """The name is in the schedulable set and its row declares the axis."""
    from computronium.domains.base import DomainType
    from computronium.domains.registry import SUPPORTED_TASKS

    assert "delayed_cue" in SUPPORTED_TASKS
    spec = _registry().get("delayed_cue")
    assert spec is not None
    assert spec.domain is DomainType.MEMORY
    assert spec.geometry_hint == "recurrent"
    assert spec.input_shape == (10,)
    assert spec.output_dim == 10
    assert spec.primary_objective == "validation_accuracy"


@pytest.mark.timeout(60)
def test_the_declared_space_admits_only_a_cell_that_reads_the_time_axis() -> None:
    """Every admitted cell for the task unrolls the axis the loader emits."""
    from computronium.experiment.surface.combinations import declared_space

    space = declared_space("delayed_cue")
    assert space.cells, "the task's declared space is empty"
    geometries = {cell[1] for cell in space.cells}
    credits = {cell[4] for cell in space.cells}
    assert geometries == {"recurrent"}
    assert credits <= _SEQUENCE_CREDITS
    assert _TREATMENT in credits


@pytest.mark.timeout(60)
def test_a_flat_task_refuses_a_sequence_credit_by_the_same_rule() -> None:
    """The layout rule is one rule: it also refuses the flat-task direction."""
    from computronium.experiment.kernel.search_space import (
        BATCH_LAYOUT_RULE,
        _batch_layout_rule,
    )
    from computronium.experiment.schema import Coordinate
    from computronium.experiment.surface.combinations import declared_space

    space = declared_space("iris")
    assert not {cell[4] for cell in space.cells} & _SEQUENCE_CREDITS
    refused = dict(space.refused)
    assert BATCH_LAYOUT_RULE in refused[f"credit={_TREATMENT}"]

    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit=_TREATMENT,
        update="adam",
        params={},
    )
    assert _batch_layout_rule(coordinate, "flat") is not None
    assert _batch_layout_rule(coordinate, "time_major") is None


@pytest.mark.parametrize(
    ("task_id", "layout", "rank"),
    [("delayed_cue", "time_major", 3), ("iris", "flat", 2)],
)
def test_the_task_declares_the_batch_its_loader_emits(
    task_id: str, layout: str, rank: int
) -> None:
    """The declaration is checkable against one batch of the real loader."""
    from computronium.domains.factory import create_task

    task = create_task(task_id, device="cpu", quick_mode=True)
    task.setup()
    assert task.batch_layout == layout
    batch_x, _ = next(iter(task.get_dataloader("train")))
    assert batch_x.dim() == rank


@pytest.mark.timeout(120)
def test_the_smoke_cell_reports_a_bar_verdict() -> None:
    """The axis is reachable from a run: one batch, then the gate's ruler."""
    from computronium.experiment.surface.combinations import smoke_task

    result = smoke_task("delayed_cue")
    assert result.verdict in {"PASS", "FAIL"}
    assert result.cause in {None, "divergence"}, result.defect
    selection = dict(
        zip(
            (
                "substrate",
                "geometry",
                "dynamics",
                "plasticity",
                "credit",
                "update",
            ),
            result.selection,
            strict=True,
        )
    )
    assert selection["geometry"] == "recurrent"
    assert selection["credit"] in _SEQUENCE_CREDITS


@pytest.mark.timeout(60)
def test_the_settle_jacobian_refuses_a_time_major_state() -> None:
    """A ``(time, batch, hidden)`` state has no fixed point to linearize."""
    from computronium.ontology import DigitalSubstrate, SubstrateConfig
    from computronium.ontology.dynamics import StateDynamicsConfig
    from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry

    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=10, output_dim=10, hidden_dims=(16,), sequence=True
        )
    )
    system = SimpleNamespace(
        geometry=geometry,
        dynamics=SimpleNamespace(config=StateDynamicsConfig.instantaneous()),
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
    )
    from computronium.experiment.execution.settle_operator import (
        settle_step_operator_at_state,
    )

    acts = [
        torch.randn(12, 8, 10),
        torch.randn(12, 8, 16),
        torch.randn(12, 8, 10),
    ]
    assert settle_step_operator_at_state(system, acts) is None
