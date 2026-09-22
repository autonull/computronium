"""Continual learning training step functions."""

from __future__ import annotations

from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

from computronium.core.continual.constants import CL_CLASSES_PER_TASK
from computronium.core.pipeline import forward_pass
from computronium.ontology import Phase, SystemState
from computronium.state import CompositeState

if TYPE_CHECKING:
    from computronium.core.continual.system import ContinualJointSystem


@runtime_checkable
class _HasComponents(Protocol):
    plasticity: Any
    context: Any
    substrate: Any
    geometry: Any
    dynamics: Any
    credit: Any
    update: Any


def _masked_task_loss(state: SystemState, local_y: Tensor, task_start: int, task_end: int) -> Tensor:
    """Compute cross-entropy loss only on task-relevant logits."""
    acts = state.activations
    if acts is None:
        return torch.tensor(0.0, device=local_y.device)
    logits = acts[-1] if isinstance(acts, list) else acts  # [batch, 10]
    task_logits = logits[:, task_start:task_end]  # [batch, 2]
    loss = F.cross_entropy(task_logits, local_y)
    with torch.no_grad():
        acc = (task_logits.argmax(dim=-1) == local_y).float().mean().item()
    state.metrics = {**state.metrics, "nudged_fit_accuracy": acc}
    return loss


def _prepare_psi(
    plasticity: Any,
    context: Any,
    x: Tensor,
    existing_psi: dict[str, Tensor] | None = None,
) -> dict[str, Tensor] | None:
    """Initialize or prepare plastic state for current batch."""
    psi = existing_psi
    if psi is None and hasattr(plasticity, "initial_psi") and plasticity is not None:
        psi = plasticity.initial_psi(context, batch_size=x.shape[0])

    if psi is not None:
        device = x.device
        batch_size = x.shape[0]
        new_psi: dict[str, Tensor] = {}
        for k, v in psi.items():
            if v.shape[0] != batch_size:
                if v.shape[0] == 1:
                    new_psi[k] = v.expand(batch_size, -1).to(device)
                else:
                    new_psi[k] = v[:batch_size].to(device)
            else:
                new_psi[k] = v.to(device)
        psi = new_psi

    return psi


def _run_settling_phases(
    substrate: Any,
    geometry: Any,
    dynamics: Any,
    credit: Any,
    x: Tensor,
    local_y: Tensor,
    task_start: int,
    task_end: int,
) -> tuple[dict[Phase, SystemState], Any]:
    """Run settling for all credit phases and return states and initial activations."""
    grad_ctx = nullcontext() if credit.requires_autograd else torch.no_grad()
    with grad_ctx:
        states: dict[Phase, SystemState] = {}
        initial_activations = forward_pass(substrate, geometry, x)

        for phase in credit.phases:
            state = SystemState(x=x, y=local_y)
            state.activations = initial_activations
            target = local_y + task_start if phase is Phase.NUDGED else None
            settled = dynamics.settle(state, geometry, substrate, target=target)
            if phase is Phase.NUDGED:
                settled.loss = _masked_task_loss(settled, local_y, task_start, task_end)
            settled.energy = dynamics.compute_energy(settled, geometry)
            states[phase] = settled

    return states, initial_activations


def _finalize_output(
    states: dict[Phase, SystemState],
    dynamics: Any,
    geometry: Any,
    initial_activations: Any,
    local_y: Tensor,
    task_start: int,
    task_end: int,
) -> SystemState:
    """Finalize output state with loss and energy."""
    output = states.get(Phase.NUDGED, states.get(Phase.FREE))
    if output is None:
        output = SystemState(x=initial_activations, y=local_y)  # type: ignore[arg-type]
        output.activations = initial_activations
    loss = output.loss
    if loss is None:
        loss = _masked_task_loss(output, local_y, task_start, task_end)
    elif not isinstance(loss, Tensor):
        loss = torch.as_tensor(loss)
    if output.energy is None:
        output.energy = dynamics.compute_energy(output, geometry)
    return output


def _step_plasticity(
    plasticity: Any,
    psi: dict[str, Tensor] | None,
    output: SystemState,
    x: Tensor,
    context: Any,
) -> dict[str, Tensor] | None:
    """Step plasticity (ψ update) if present."""
    if psi is not None and hasattr(plasticity, "step") and plasticity is not None:
        acts = output.activations
        if acts is not None:
            final_acts = acts[-1] if isinstance(acts, list) else acts
            z = CompositeState(
                activity={"x": x, "y": final_acts},
                plastic=psi,
                substrate={},
            )
            psi = plasticity.step(psi, z, context)
    return psi


def _compute_metrics(output: SystemState) -> dict[str, float]:
    """Compute metrics from settled output."""
    loss_val = output.loss.item() if isinstance(output.loss, Tensor) else float(output.loss)  # type: ignore[return-value]
    energy_val = (
        output.energy.item()
        if isinstance(output.energy, Tensor)
        else float(output.energy)
        if output.energy is not None
        else 0.0
    )
    metrics: dict[str, float] = {
        "loss": loss_val,
        "energy": energy_val,
        "nudged_fit_accuracy": output.metrics.get("nudged_fit_accuracy", 0.0),
    }
    metrics.update({
        k: v
        for k, v in output.metrics.items()
        if isinstance(v, (int, float)) and k not in {"accuracy", "nudged_fit_accuracy"}
    })
    return metrics


def run_continual_train_step(
    joint_system: _HasComponents,
    x: Tensor,
    y: Tensor,
    task_id: int,
    psi: dict[str, Tensor] | None = None,
) -> tuple[dict[str, float], dict[str, Tensor] | None]:
    """Execute one training step through the joint system with task-masked loss and plasticity stepping.

    The joint system outputs 10-class logits. We mask the loss to only the
    current task's 2 classes (task_id * 2 : task_id * 2 + 2).

    The labels y are already 0/1 (local to the task) from SplitMNIST.

    This uses the joint system's credit assignment and parameter update,
    ensuring ψ/θ decoupling (FastWeightPlasticity) and other components
    are actually invoked. Also steps the plasticity to update ψ.

    Returns:
        Tuple of (metrics, updated_psi)
    """
    local_y = y
    task_start = task_id * CL_CLASSES_PER_TASK
    task_end = task_start + CL_CLASSES_PER_TASK

    # Get the joint system components
    substrate = joint_system.substrate
    geometry = joint_system.geometry
    dynamics = joint_system.dynamics
    credit = joint_system.credit
    update = joint_system.update
    plasticity = joint_system.plasticity

    # Initialize plastic state if needed
    psi = _prepare_psi(plasticity, joint_system.context, x, psi)

    # Run settling phases
    states, initial_activations = _run_settling_phases(
        substrate, geometry, dynamics, credit, x, local_y, task_start, task_end
    )

    # Finalize output
    output = _finalize_output(
        states, dynamics, geometry, initial_activations, local_y, task_start, task_end
    )

    # Compute pseudo-gradients and update parameters
    loss = output.loss
    pseudo_grads = credit.compute_pseudo_gradient(states, loss, geometry)  # type: ignore[attr-defined]
    geometry.update_params(update.step(geometry.params, pseudo_grads, geometry))  # type: ignore[attr-defined]

    # Step plasticity if present (ψ update)
    psi = _step_plasticity(plasticity, psi, output, x, joint_system.context)

    metrics = _compute_metrics(output)
    return metrics, psi


def _continual_step(
    model: _HasComponents,
    x: Tensor,
    y: Tensor,
    task_id: int,
    extra_loss_fn: Callable[[_HasComponents, SystemState, int], Tensor | None],
    si_tracker: Any = None,
) -> dict[str, float]:
    """Run the joint training pipeline, folding an extra loss term into the task loss.

    ``extra_loss_fn(model, output, task_id)`` returns an additive regularizer /
    distillation term (or None). The combined loss drives credit assignment so the
    term actually influences ``theta`` (unlike a post-hoc ``.backward()`` with no
    optimizer step).

    If si_tracker is provided, accumulates pseudo-gradients for SI importance computation.
    """
    substrate = model.substrate
    geometry = model.geometry
    dynamics = model.dynamics
    credit = model.credit
    update = model.update
    plasticity = model.plasticity

    task_start = task_id * CL_CLASSES_PER_TASK
    task_end = task_start + CL_CLASSES_PER_TASK
    local_y = y

    psi = _prepare_psi(plasticity, model.context, x, getattr(model, "_psi", None))

    # Run settling phases
    states, initial_activations = _run_settling_phases(
        substrate, geometry, dynamics, credit, x, local_y, task_start, task_end
    )

    # Finalize output
    output = _finalize_output(
        states, dynamics, geometry, initial_activations, local_y, task_start, task_end
    )

    # Combine task loss with extra loss
    loss = output.loss
    if not isinstance(loss, Tensor):
        loss = torch.as_tensor(loss) if loss is not None else torch.tensor(0.0, device=x.device)
    extra = extra_loss_fn(model, output, task_id)
    total_loss: Tensor = loss if extra is None else loss + extra

    # Compute pseudo-gradients
    pseudo_grads = credit.compute_pseudo_gradient(states, total_loss, geometry)  # type: ignore[attr-defined]

    # Accumulate pseudo-gradients for SI if tracker provided
    if si_tracker is not None:
        si_tracker.accumulate_pseudo_grads(pseudo_grads, geometry)  # type: ignore[attr-defined]

    # Update parameters
    geometry.update_params(update.step(geometry.params, pseudo_grads, geometry))  # type: ignore[attr-defined]

    # Step plasticity
    psi = _step_plasticity(plasticity, psi, output, x, model.context)
    model._psi = psi  # type: ignore[attr-defined]

    # Compute metrics
    loss_val = total_loss.item() if isinstance(total_loss, Tensor) else float(total_loss)
    energy_val = (
        output.energy.item()
        if isinstance(output.energy, Tensor)
        else float(output.energy)
        if output.energy is not None
        else 0.0
    )
    metrics: dict[str, float] = {
        "loss": loss_val,
        "energy": energy_val,
        "nudged_fit_accuracy": output.metrics.get("nudged_fit_accuracy", 0.0),
    }
    metrics.update({
        k: v
        for k, v in output.metrics.items()
        if isinstance(v, (int, float)) and k not in {"accuracy", "nudged_fit_accuracy"}
    })
    return metrics


def _lwf_train_step(
    model: _HasComponents,
    x: Tensor,
    y: Tensor,
    task_id: int,
    lwf_loss_fn: Any,
) -> dict[str, float]:
    """LwF training step: task CE + distillation from a frozen previous model."""
    prev_logits = None
    prev_model = lwf_loss_fn.prev_model
    if prev_model is not None and task_id > 0:
        prev_model.eval()
        with torch.no_grad():
            prev_logits = prev_model(x, task_id=task_id)

    model.train()  # type: ignore[attr-defined]

    def extra_loss_fn(_model: _HasComponents, output: SystemState, tid: int) -> Tensor | None:
        if prev_logits is None:
            return None
        logits = (
            output.activations[-1]
            if isinstance(output.activations, list)
            else output.activations
        )
        return lwf_loss_fn.distill_only(logits, tid, prev_logits)  # type: ignore[attr-defined]

    return _continual_step(model, x, y, task_id, extra_loss_fn)


def _si_train_step(
    model: _HasComponents,
    x: Tensor,
    y: Tensor,
    task_id: int,
    si_tracker: Any,
) -> dict[str, float]:
    """SI training step: task loss + importance-weighted consolidation penalty."""
    model.train()  # type: ignore[attr-defined]

    def extra_loss_fn(_model: _HasComponents, _output: SystemState, _tid: int) -> Tensor:
        return si_tracker.regularization_loss()  # type: ignore[attr-defined]

    return _continual_step(model, x, y, task_id, extra_loss_fn, si_tracker=si_tracker)


__all__ = [
    "_continual_step",
    "_lwf_train_step",
    "_masked_task_loss",
    "_si_train_step",
    "run_continual_train_step",
]