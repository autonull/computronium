"""One-step axis liveness: does an axis value change the computation it owns?

The ruler is the post-step geometry parameters after **one** ``train_step`` at a
fixed seed, not ``train_loss``: the trainer reports the loss *before* the
update, so a one-step loss cannot see a credit or update rule, and Lion's first
step is sign-like enough to match Adam's loss while its parameters differ by
6.3e-06. Parameters are the sensitive one-step trace.

Two controls keep the comparison honest:

* the reference is composed with the variant's pre-step geometry parameters, so
  component-initialization RNG cannot masquerade as a mechanism;
* a plasticity variant is compared against a **joint** null system, not the 5-D
  null, because the two system families take different pipeline paths. Measured
  2026-11-14 (TODO92 §3.9): the joint null is the comparison under which
  ``rule_state`` and ``substrate_coupled`` are bit-identical and ``fast_weights``
  is live.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

import torch

from computronium.core.label_channel import LabelChannelSystem
from computronium.core.system_trainer.factory import param_count
from computronium.core.system_trainer.joint import compose_joint_system_from_configs
from computronium.experiment.kernel.compose import compose_cell_system, compose_configs
from computronium.experiment.kernel.evaluate import TaskShape, task_shape
from computronium.experiment.schema.coordinate import Coordinate
from computronium.state.transitions import PlasticityConfig

if TYPE_CHECKING:
    from torch import Tensor

__all__ = [
    "CANONICAL",
    "copy_geometry_params",
    "describe",
    "one_step_fingerprint",
    "same_fingerprint",
]

CANONICAL: Final[dict[str, str]] = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}
BATCH: Final[int] = 4
NODES: Final[int] = 8
SEED: Final[int] = 42


def describe(selection: dict[str, str]) -> str:
    """The non-canonical axes of a selection, for a ledger row."""
    return ", ".join(
        f"{axis}={name}" for axis, name in selection.items() if name != CANONICAL[axis]
    )


def _inputs(
    task: str, geometry: str
) -> tuple[Tensor, Tensor, TaskShape, dict[str, Any]]:
    shape = task_shape(task, "cpu")
    if geometry == "graph":
        x = torch.randn(NODES, shape.input_shape[0])
        y = torch.randint(0, shape.output_dim, (NODES,))
        edge_index = torch.tensor(
            [list(range(NODES)), [(i + 1) % NODES for i in range(NODES)]],
            dtype=torch.long,
        )
        return x, y, shape, {"edge_index": edge_index.tolist()}
    flat = 1
    for extent in shape.input_shape:
        flat *= extent
    return (
        torch.randn(BATCH, flat),
        torch.randint(0, shape.output_dim, (BATCH,)),
        shape,
        {},
    )


def _compose_system(
    task: str, selection: dict[str, str], joint_null: bool
) -> tuple[Tensor, Tensor, Any, int]:
    x, y, shape, geometry = _inputs(task, selection["geometry"])
    coordinate = selection_to_coordinate(selection)
    if joint_null and selection["plasticity"] == "null":
        config = compose_configs(
            coordinate=coordinate,
            geometry=geometry,
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=0,
        )
        system = compose_joint_system_from_configs(
            config.substrate,
            config.geometry,
            config.dynamics,
            PlasticityConfig.null(),
            config.credit,
            config.update,
            validate=False,
        )
        count = param_count(system)
        label_dim = config.credit.label_dim if config.credit.label_channel else 0
        if label_dim:
            system = LabelChannelSystem(
                system, output_dim=shape.output_dim, label_dim=label_dim
            )
        return x, y, system, count
    cell = compose_cell_system(
        coordinate=coordinate,
        geometry=geometry,
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=0,
    )
    return x, y, cell.system, cell.param_count


def selection_to_coordinate(selection: dict[str, str]) -> Coordinate:
    """The ``Coordinate`` a six-name selection names (no params)."""
    return Coordinate(**selection, params={})


def _snapshot(system: Any) -> dict[str, Tensor]:
    return {
        name: tensor.detach().clone() for name, tensor in system.geometry.params.items()
    }


def copy_geometry_params(system: Any, initial: dict[str, Tensor]) -> None:
    """Put ``initial`` into ``system``'s geometry, shape-compatible names only."""
    with torch.no_grad():
        for name, tensor in system.geometry.params.items():
            source = initial.get(name)
            if source is not None and source.shape == tensor.shape:
                tensor.copy_(source)


def one_step_fingerprint(
    task: str,
    selection: dict[str, str],
    *,
    initial: dict[str, Tensor] | None = None,
    joint_null: bool = False,
    seed: int = SEED,
) -> tuple[dict[str, Tensor], dict[str, Tensor], int]:
    """Compose, optionally align the geometry, run one step, fingerprint it.

    Args:
        task: Task whose shape and graph structure the cell consumes.
        selection: Six-axis value names, no hyperparameters.
        initial: Pre-step geometry parameters to copy into the composed cell,
            so a variant and its reference start from the same weights.
        joint_null: Compose the reference as a 6-D joint system with null
            plasticity, not the 5-D null system.
        seed: Seed for composition and for the step.

    Returns:
        ``(before, after, param_count)``; ``before`` is reusable as the next
        cell's ``initial``.
    """
    torch.manual_seed(seed)
    x, y, system, count = _compose_system(task, selection, joint_null)
    if initial is not None:
        copy_geometry_params(system, initial)
    before = _snapshot(system)
    torch.manual_seed(seed)
    system.train_step(x, y)
    return before, _snapshot(system), count


def same_fingerprint(left: dict[str, Tensor], right: dict[str, Tensor]) -> bool:
    """Whether two geometry-parameter snapshots are bit-identical."""
    return left.keys() == right.keys() and all(
        torch.equal(left[name], right[name]) for name in left
    )
