"""The six protocol seams, one E1 exchange each (TODO98 P2).

A seam is two laws exchanging what they declare: the target reaches the
credit, token ids broadcast, the time axis unrolls, ``edge_index`` reaches
the topology, the settle converges, and both update paths run. Each check
is keyed by the seam's declaration in :mod:`computronium.primitives.surface`,
so a declared seam without a check fails the lock and a new check needs a
declaration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import torch

from computronium.core.label_channel import (
    LabelChannelSystem,
    label_augmented,
)
from computronium.core.system_trainer import compose_joint_system_from_configs
from computronium.experiment.kernel.compose import compose_configs
from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate
from computronium.ontology.dynamics import dynamics_from_config
from computronium.ontology.geometry import geometry_from_config
from computronium.ontology.substrate import DigitalSubstrate
from computronium.primitives.cases import (
    MICRO_BATCH,
    MICRO_INPUT_SHAPE,
    MICRO_OUTPUT_DIM,
    MICRO_TIME,
    build_case,
    cell_config,
)
from computronium.primitives.registry import get_primitive_spec
from computronium.primitives.surface import SEAMS
from computronium.state import CompositeState

if TYPE_CHECKING:
    from computronium.primitives.surface import Seam


class _Recorder:
    """An inner system that records the stream a seam hands it."""

    def train_step(self, x: torch.Tensor, y: torch.Tensor, **_: object) -> dict:
        self.x = x
        self.y = y
        return {}


def _label_channel(seam: Seam) -> None:
    """The target reaches the credit through the widened input."""
    spec = get_primitive_spec(seam.primitive_id)
    assert spec is not None
    config = cell_config(spec).credit
    assert config.label_channel, seam.primitive_id
    inner = _Recorder()
    system = LabelChannelSystem(
        inner, output_dim=config.label_dim, label_dim=config.label_dim
    )
    x = torch.zeros(MICRO_BATCH, MICRO_INPUT_SHAPE[0])
    y = torch.arange(MICRO_BATCH) % MICRO_OUTPUT_DIM
    system.train_step(x, y)
    assert torch.equal(inner.x, label_augmented(x, y, config.label_dim))


def _token_lane(seam: Seam) -> None:
    """Token ids broadcast through the token task."""
    spec = get_primitive_spec(seam.primitive_id)
    assert spec is not None
    case = build_case(spec, seam.task_id, {}, 0)
    ids = case.extra["state"]
    geometry = case.extra["geometry"]
    assert not ids.dtype.is_floating_point, seam.task_id
    assert ids.shape == (MICRO_BATCH, geometry.config.seq_len)
    logits = geometry(ids, DigitalSubstrate())
    assert logits.shape[0] == ids.numel(), seam.primitive_id


def _time_axis(seam: Seam) -> None:
    """``(time, batch, features)`` unrolls through the recurrent geometry."""
    assert seam.axis == "geometry"
    axes = dict(_AXIS_DEFAULTS)
    axes["geometry"] = seam.primitive_id.rsplit(".", 1)[-1]
    config = compose_configs(
        coordinate=_coordinate(axes),
        geometry={"num_layers": 1, "hidden_dim": 8, "sequence": True},
        input_shape=MICRO_INPUT_SHAPE,
        output_dim=MICRO_OUTPUT_DIM,
    )
    geometry = geometry_from_config(config.geometry)
    x = torch.randn(MICRO_TIME, MICRO_BATCH, geometry.config.input_dim)
    logits = geometry.forward(x, DigitalSubstrate())
    assert logits.shape[0] == x.shape[0], seam.primitive_id


def _graph_topology(seam: Seam) -> None:
    """``edge_index`` reaches the topology."""
    spec = get_primitive_spec(seam.primitive_id)
    assert spec is not None
    case = build_case(spec, seam.task_id, {}, 0)
    geometry = case.extra["geometry"]
    x = case.extra["state"]
    edge_index = geometry._edge_index
    assert x.shape[0] == int(edge_index.max()) + 1, seam.task_id
    logits = geometry(x, DigitalSubstrate())
    assert logits.shape == (x.shape[0], geometry.config.output_dim), seam.primitive_id


def _settle(seam: Seam) -> None:
    """The settle converges on one geometry."""
    spec = get_primitive_spec(seam.primitive_id)
    assert spec is not None
    case = build_case(spec, seam.task_id, {}, 0)
    cell = cell_config(spec)
    dynamics = dynamics_from_config(cell.dynamics)
    geometry = case.extra["geometry"]
    substrate = DigitalSubstrate()
    settled = dynamics.settle(case.extra["state"], geometry, substrate)
    assert settled.activations, seam.primitive_id
    first = float(dynamics.compute_energy(settled, geometry))
    converged = dynamics.settle(settled, geometry, substrate)
    assert float(dynamics.compute_energy(converged, geometry)) == pytest.approx(
        first, abs=1e-6
    )


def _joint_plasticity(seam: Seam) -> None:
    """Both the plastic and the parameter update path run."""
    spec = get_primitive_spec(seam.primitive_id)
    assert spec is not None
    cell = cell_config(spec)
    system = compose_joint_system_from_configs(
        cell.substrate,
        cell.geometry,
        cell.dynamics,
        cell.plasticity,
        cell.credit,
        cell.update,
        validate=True,
    )
    width = cell.geometry.input_dim
    psi = system.plasticity.initial_psi(system.context, batch_size=MICRO_BATCH)
    state = CompositeState(
        activity={
            "x": torch.randn(MICRO_BATCH, width),
            "h": torch.randn(MICRO_BATCH, width),
            "y": torch.randn(MICRO_BATCH, MICRO_OUTPUT_DIM),
            "target": torch.arange(MICRO_BATCH) % MICRO_OUTPUT_DIM,
        },
        plastic=psi,
        substrate={},
    )
    stepped = system.plasticity.step(psi, state, system.context)
    assert any(not torch.equal(psi[key], stepped[key]) for key in stepped), (
        seam.primitive_id
    )
    params = dict(system.geometry.params)
    names = [name for name, param in params.items() if param.dim() == 2]
    grads = [torch.ones_like(params[name]) for name in names]
    with torch.no_grad():
        updated = system.update.step(params, grads, system.geometry)
    assert any(not torch.equal(params[name], updated[name]) for name in names), (
        seam.primitive_id
    )


CHECKS = {
    "label channel": _label_channel,
    "token lane": _token_lane,
    "time axis": _time_axis,
    "graph topology": _graph_topology,
    "settle": _settle,
    "joint plasticity": _joint_plasticity,
}


def test_every_seam_has_a_check() -> None:
    """A declared seam without a check is a declaration, not evidence."""
    assert set(CHECKS) == {seam.name for seam in SEAMS}


@pytest.mark.parametrize("seam", SEAMS, ids=[seam.name for seam in SEAMS])
def test_seam_exchanges_what_it_declares(seam: Seam) -> None:
    """The seam's exemplar runs its exchange on a micro-cell."""
    CHECKS[seam.name](seam)
