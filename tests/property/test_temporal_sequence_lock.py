"""Locks for the temporal axis's sequence geometry + loader (TODO93 §19).

The three temporal credits were locked on the sequence contract while no
pipeline could feed them: every loader yielded 2-D batches. These locks are
the build's capability, and each fails if its mechanism is removed:

- the geometry's unroll is the equations (a second copy of the chain, or a
  wrong recurrent input, breaks the equality);
- the credit reads *that* unroll (a private second unroll leaves the spy's
  counter at zero);
- a 2-D state and a geometry without a time axis are refused by name;
- the loader yields the time axis first, with a cue and a constant label;
- the loss supervises every step, and the 2-D LM layout is unchanged;
- one recurrent cell with ``eligibility_prop`` trains above chance.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pytest
import torch
from torch import nn

from computronium import (
    DigitalSubstrate,
    EuclideanUpdate,
    InstantaneousDynamics,
    NullPlasticity,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
)
from computronium.core.losses import cross_entropy, fold_time
from computronium.core.pipeline import task_loss
from computronium.domains.factory import create_task
from computronium.ontology.credit import (
    CreditAssignment,
    CreditAssignmentConfig,
    EligibilityPropCredit,
    Phase,
)
from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry
from computronium.ontology.system import SystemConfig, SystemState
from computronium.state import CompositeState
from computronium.state.transitions import PlasticityConfig

if TYPE_CHECKING:
    from computronium.domains.sequence import SequenceTask

_TIME, _BATCH, _INPUT, _HIDDEN, _CLASSES = 5, 4, 3, 6, 3


def _geometry(*, sequence: bool = True) -> RecurrentGeometry:
    torch.manual_seed(0)
    return RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=_INPUT,
            output_dim=_CLASSES,
            hidden_dims=(_HIDDEN,),
            init_scale=0.3,
            sequence=sequence,
        )
    )


def _batch() -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(7)
    return (
        torch.randn((_TIME, _BATCH, _INPUT), generator=generator),
        torch.randint(0, _CLASSES, (_TIME, _BATCH), generator=generator),
    )


def _states(x: torch.Tensor, y: torch.Tensor) -> dict[Phase, CompositeState]:
    return {
        Phase.FREE: CompositeState(activity={"x": x, "y": y}, plastic={}, substrate={})
    }


def _equations(
    geometry: RecurrentGeometry, x: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """The unroll written from the equations, independently of the geometry."""
    linears = [layer for layer in geometry._layers if isinstance(layer, nn.Linear)]
    linear_in, linear_out = linears
    recurrent = geometry._recurrent_weight
    assert recurrent is not None
    hidden = torch.zeros((_BATCH, _HIDDEN))
    states = []
    for step in range(_TIME):
        hidden = torch.tanh(
            x[step] @ linear_in.weight.T + hidden @ recurrent.T + linear_in.bias
        )
        states.append(hidden)
    stack = torch.stack(states)
    return stack, stack @ linear_out.weight.T + linear_out.bias


def test_the_sequence_geometry_is_the_equations() -> None:
    """The geometry's unroll equals the chain written from the equations."""
    geometry = _geometry()
    x, _ = _batch()
    expected_states, expected_logits = _equations(geometry, x)
    states, logits = geometry.sequence_states(x)
    assert torch.allclose(states, expected_states, atol=1e-6)
    assert torch.allclose(logits, expected_logits, atol=1e-6)
    assert tuple(logits.shape) == (_TIME, _BATCH, _CLASSES)
    assert torch.equal(geometry.forward(x), logits)


def test_the_temporal_credit_unrolls_through_the_geometry() -> None:
    """The credit calls the geometry's unroll, not a private copy."""
    geometry = _geometry()
    x, y = _batch()
    calls: list[tuple[int, ...]] = []
    original = geometry.sequence_states

    def spy(batch: torch.Tensor, substrate=None):
        calls.append(tuple(batch.shape))
        return original(batch, substrate)

    geometry.sequence_states = spy  # type: ignore[method-assign]
    credit = EligibilityPropCredit(CreditAssignmentConfig.eligibility_prop())
    credit.compute_pseudo_gradient(_states(x, y), None, geometry)
    assert calls == [(x.shape[0], x.shape[1], x.shape[2])]


def test_a_sequence_geometry_refuses_a_two_dimensional_batch() -> None:
    """A state with no time axis is refused by name, not by a shape crash."""
    geometry = _geometry()
    with pytest.raises(ValueError, match="sequence"):
        geometry.forward(torch.randn((_BATCH, _INPUT)))


def test_a_temporal_credit_requires_a_sequence_geometry() -> None:
    """The config gate refuses a time-major credit without a time axis."""

    def system(*, sequence: bool) -> SystemConfig:
        return SystemConfig(
            substrate=SubstrateConfig.digital(device="cpu"),
            geometry=GeometryConfig.recurrent(
                input_dim=_INPUT,
                output_dim=_CLASSES,
                hidden_dims=(_HIDDEN,),
                sequence=sequence,
            ),
            dynamics=StateDynamicsConfig.instantaneous(),
            credit=CreditAssignmentConfig.eligibility_prop(),
            update=ParameterUpdateConfig.euclidean(),
            plasticity=PlasticityConfig.null(),
        )

    system(sequence=True).validate()
    with pytest.raises(ValueError, match="eligibility_prop"):
        system(sequence=False).validate()


def test_the_loader_yields_the_time_axis_first() -> None:
    """The batch is ``(time, batch, input)`` and the cue is one-hot at its step."""
    task = cast(
        "SequenceTask", create_task("delayed_cue", device="cpu", quick_mode=True)
    )
    task.setup()
    x, y = next(iter(task.train_dataloader))
    assert x.shape == (task.time, x.shape[1], task.classes)
    assert y.shape == (task.time, x.shape[1])
    assert torch.equal(y, y[:1].expand_as(y)), "the class is the label at every step"
    cue = x[task.cue_step].argmax(dim=-1)
    assert torch.equal(cue, y[0]), "the cue names the class"
    assert torch.equal(
        x[task.cue_step].gather(1, cue[:, None]).squeeze(1),
        torch.ones_like(cue, dtype=x.dtype),
    ), "the cue is one-hot, not a scaled noise row"


def test_the_loss_folds_the_time_axis() -> None:
    """Every step is supervised; the 2-D LM layout keeps its last-step head."""
    generator = torch.Generator().manual_seed(13)
    logits = torch.randn((_TIME, _BATCH, _CLASSES), generator=generator)
    y = torch.randint(0, _CLASSES, (_TIME, _BATCH), generator=generator)
    folded, targets = fold_time(logits, y)
    expected = cross_entropy(folded, targets)
    state = SystemState(activations=logits)
    assert torch.allclose(task_loss(state, y, sequence=True), expected)
    assert state.metrics is not None
    assert 0.0 <= float(state.metrics["accuracy"]) <= 1.0

    # The 2-D head is the same read: the flag is the caller's declaration,
    # not a property inferred from the rank (an LM head is (batch, time,
    # vocab) and keeps its own last-step rule outside this path).
    flat_logits = torch.randn((_BATCH, _CLASSES), generator=generator)
    flat_targets = torch.randint(0, _CLASSES, (_BATCH,), generator=generator)
    flat_state = SystemState(activations=flat_logits)
    assert torch.allclose(
        task_loss(flat_state, flat_targets),
        cross_entropy(flat_logits, flat_targets),
    )


def test_a_recurrent_cell_with_e_prop_trains_above_chance() -> None:
    """The capability card: the build trains a cell, end to end."""
    from computronium import compose_joint_system

    torch.manual_seed(71)
    geometry = RecurrentGeometry(
        GeometryConfig.recurrent(
            input_dim=10,
            output_dim=10,
            hidden_dims=(32,),
            sequence=True,
        )
    )
    system = compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=geometry,
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        plasticity=NullPlasticity(),
        credit=cast(
            "CreditAssignment",
            EligibilityPropCredit(CreditAssignmentConfig.eligibility_prop()),
        ),
        update=EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=0.3, grad_clip=1e9)
        ),
    )
    task = cast(
        "SequenceTask",
        create_task(
            "delayed_cue",
            device="cpu",
            time=12,
            cue_step=2,
            classes=10,
            n_train=1024,
            n_val=512,
        ),
    )
    task.setup()
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=3, device="cpu", seed=71),
        train_data=task.train_dataloader,
        val_data=task.val_dataloader,
    )
    history = trainer.fit()
    assert history[-1]["val_acc"] > 0.25, (
        "the temporal cell must clear 2.5x chance on the delayed-cue box; "
        f"read {history[-1]['val_acc']:.3f}"
    )
