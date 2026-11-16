"""Locks for the continual credit arms the C1 ladder needs.

The ladder is a measurement, so its arms must differ only in credit and
update: same stack, same init, and the config's learning rate must actually
reach the update rule (a ladder over a knob the runner ignores measures
nothing). The free-phase-only arm is also what caught ``_finalize_output``
dropping the loss it had just computed.
"""

from __future__ import annotations

import math

import torch

from computronium.core.continual import CLConfig, create_local_arm
from computronium.core.continual.runner import _apply_task_boundary_setup, _create_arm

LADDER_LR = 0.05


def test_config_lr_reaches_every_credit_arm() -> None:
    config = CLConfig(
        input_dim=64, hidden_dim=16, output_dim=10, lr=LADDER_LR, device="cpu"
    )
    for arm in ("backprop", "local", "local_ewc", "backprop_ewc"):
        model, _ = _create_arm(arm, config, "cpu")
        assert model.update.config.step_size == LADDER_LR


def test_local_arm_trains_through_the_continual_step() -> None:
    model = create_local_arm(64, 16, 10, "cpu", lr=0.05)
    before = {
        name: tensor.clone()
        for name, tensor in model.geometry.params.items()
        if tensor.ndim == 2
    }
    losses = []
    for _ in range(20):
        metrics = model.train_step(torch.randn(1, 64), torch.tensor([0]), task_id=0)
        losses.append(metrics["loss"])

    assert all(math.isfinite(loss) for loss in losses)
    assert sum((model.geometry.params[n] - before[n]).abs().sum() for n in before) > 0


def test_consolidation_arms_carry_state_after_a_boundary() -> None:
    config = CLConfig(input_dim=64, hidden_dim=16, output_dim=10, device="cpu")
    for arm in ("local_ewc", "backprop_ewc"):
        model, extra = _create_arm(arm, config, "cpu")
        update = extra["update"]
        update.consolidate(model.geometry.params)
        assert update.state_bytes() > 0


def test_train_order_is_seeded_independently_of_model_rng() -> None:
    """Each arm at one seed sees one data order, whatever its credit draws.

    ``PepitaCredit`` lazily draws a feedback matrix from the global RNG; if
    the train loader shares that stream, the control and treatment see
    different orders and the paired comparison is confounded.
    """
    from torch.utils.data import RandomSampler

    from computronium.core.continual.runner import _create_task_loaders

    loaders, _ = _create_task_loaders(
        CLConfig(seed=7, batch_size=1, num_workers=0), "cpu"
    )
    seeds = [
        loader.sampler.generator.initial_seed()
        for loader in loaders
        if isinstance(loader.sampler, RandomSampler)
    ]
    assert seeds == [7 + task for task in range(5)]


def test_credit_state_carries_the_global_task_target() -> None:
    """The credit's own second pass must see the task's global class index.

    A PEPITA step on task 1 (classes 2/3) that reads local labels 0/1 trains
    the task-0 logits: the cell is a label-channel defect, not an algorithm
    coordinate. The masked loss still uses the local label.
    """
    from computronium.core.continual.training import _run_settling_phases
    from computronium.ontology import Phase

    model = create_local_arm(64, 16, 10, "cpu", lr=0.01)
    states, _ = _run_settling_phases(
        model.substrate,
        model.geometry,
        model.dynamics,
        model.credit,
        torch.randn(1, 64),
        torch.tensor([1]),
        task_start=2,
        task_end=4,
    )
    assert states[Phase.FREE].y.item() == 3


def test_task_boundary_anchors_without_erasing_importance() -> None:
    """A task start moves the anchor; it must not recompute the Fisher.

    The runner anchored every new task by calling ``consolidate`` on unchanged
    parameters, which recomputed ``Fisher = drift² + damping`` from a zero
    drift. Every EWC arm then trained under a uniform damping term instead of
    the importance measured at the previous boundary -- the C2 ladder's knob
    was inert because of it.
    """
    config = CLConfig(
        input_dim=64,
        hidden_dim=16,
        output_dim=10,
        device="cpu",
        ewc_lambda=10.0,
    )
    model, extra = _create_arm("backprop_ewc", config, "cpu")
    update = extra["update"]
    old = {k: v.clone() + 0.01 for k, v in model.geometry.params.items()}
    update.consolidate(model.geometry.params, old_params=old)
    importance = {k: v.clone() for k, v in update._fisher.items()}
    assert all(v.max() > 1e-3 for v in importance.values())

    _apply_task_boundary_setup("backprop_ewc", model, extra)

    for name, value in importance.items():
        assert torch.equal(update._fisher[name], value), name
    for name in update._old_params:
        assert torch.equal(update._old_params[name], model.geometry.params[name])
