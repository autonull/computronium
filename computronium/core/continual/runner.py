"""Continual learning benchmark runner."""

from __future__ import annotations

import copy
import json
import random
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypedDict, cast

import torch
from torch.utils.data import RandomSampler

from computronium.core.continual.arms import (
    create_backprop_arm,
    create_backprop_ewc_arm,
    create_ewc_arm,
    create_fast_weight_arm,
    create_local_arm,
    create_local_ewc_arm,
    create_lwf_arm,
    create_plasticity_arm,
    create_replay_arm,
    create_si_arm,
)
from computronium.core.continual.constants import (
    CL_CLASSES_PER_TASK,
    CL_NUM_TASKS,
    SPLIT_MNIST_TASKS,
)
from computronium.core.continual.metrics import CLConfig, CLMetrics, compute_cl_metrics
from computronium.core.continual.stability import (
    check_stability,
    create_stability_guard,
    make_transition_fn,
)
from computronium.core.continual.training import _lwf_train_step, _si_train_step
from computronium.domains.base import TaskSplit
from computronium.domains.vision import SplitMNIST, PermutedMNIST

if TYPE_CHECKING:
    from computronium.core.continual.system import ContinualJointSystem


class _ArmExtra(TypedDict, total=False):
    """Extra components returned by arm factories."""

    update: Any  # EWC update
    buffer: Any  # Replay buffer
    lwf_loss: Any  # LwF loss
    si: Any  # SI tracker


def _resolve_device(config: CLConfig) -> torch.device:
    """Resolve device string from config."""
    device_str = (
        "cuda"
        if config.device == "auto" and torch.cuda.is_available()
        else config.device
    )
    return torch.device(device_str)


_EVAL_BATCH_SIZE = 256


def _create_task_loaders(config: CLConfig, device_str: str) -> tuple[list, list]:
    """Create train and test data loaders for all tasks."""
    task_loaders = []
    for task_id in range(config.num_tasks):
        if config.num_tasks == 5 and config.classes_per_task == 2:
            # SplitMNIST
            task = SplitMNIST(
                task_id=task_id,
                batch_size=config.batch_size,
                device=device_str,
                num_workers=config.num_workers,
            )
        else:
            # PermutedMNIST or other multi-task vision
            task = PermutedMNIST(
                task_id=task_id,
                num_tasks=config.num_tasks,
                batch_size=config.batch_size,
                device=device_str,
                num_workers=config.num_workers,
            )
        task.setup()
        loader = task.get_dataloader(TaskSplit.TRAIN)
        if isinstance(loader.sampler, RandomSampler):
            loader.sampler.generator = torch.Generator().manual_seed(
                config.seed + task_id
            )
        task_loaders.append(loader)

    test_loaders = []
    for task_id in range(config.num_tasks):
        if config.num_tasks == 5 and config.classes_per_task == 2:
            task = SplitMNIST(
                task_id=task_id,
                batch_size=_EVAL_BATCH_SIZE,
                device=device_str,
                num_workers=config.num_workers,
            )
        else:
            task = PermutedMNIST(
                task_id=task_id,
                num_tasks=config.num_tasks,
                batch_size=_EVAL_BATCH_SIZE,
                device=device_str,
                num_workers=config.num_workers,
            )
        task.setup()
        test_loaders.append(task.get_dataloader(TaskSplit.TEST))

    return task_loaders, test_loaders


def _arm_backprop(
    config: CLConfig, device: str
) -> tuple[ContinualJointSystem, _ArmExtra]:
    return (
        create_backprop_arm(
            config.input_dim,
            config.hidden_dim,
            config.output_dim,
            device,
            config.lr,
            classes_per_task=config.classes_per_task,
        ),
        {},
    )


def _arm_local(config: CLConfig, device: str) -> tuple[ContinualJointSystem, _ArmExtra]:
    return (
        create_local_arm(
            config.input_dim,
            config.hidden_dim,
            config.output_dim,
            device,
            config.lr,
            classes_per_task=config.classes_per_task,
        ),
        {},
    )


def _arm_local_ewc(
    config: CLConfig, device: str
) -> tuple[ContinualJointSystem, _ArmExtra]:
    model, update = create_local_ewc_arm(
        config.input_dim,
        config.hidden_dim,
        config.output_dim,
        device,
        config.lr,
        config.ewc_lambda,
        classes_per_task=config.classes_per_task,
    )
    return model, {"update": update}


def _arm_backprop_ewc(
    config: CLConfig, device: str
) -> tuple[ContinualJointSystem, _ArmExtra]:
    model, update = create_backprop_ewc_arm(
        config.input_dim,
        config.hidden_dim,
        config.output_dim,
        device,
        config.lr,
        config.ewc_lambda,
        classes_per_task=config.classes_per_task,
    )
    return model, {"update": update}


def _arm_ewc(config: CLConfig, device: str) -> tuple[ContinualJointSystem, _ArmExtra]:
    model, update = create_ewc_arm(
        config.input_dim,
        config.hidden_dim,
        config.output_dim,
        device,
        config.ewc_lambda,
        config.lr,
        classes_per_task=config.classes_per_task,
    )
    return model, {"update": update}


def _arm_si(config: CLConfig, device: str) -> tuple[ContinualJointSystem, _ArmExtra]:
    model, si = create_si_arm(
        config.input_dim,
        config.hidden_dim,
        config.output_dim,
        device,
        config.lr,
        config.si_xi,
        classes_per_task=config.classes_per_task,
    )
    return model, {"si": si}


def _arm_replay(
    config: CLConfig, device: str
) -> tuple[ContinualJointSystem, _ArmExtra]:
    model, buffer = create_replay_arm(
        config.input_dim,
        config.hidden_dim,
        config.output_dim,
        device,
        config.replay_capacity,
        config.lr,
        classes_per_task=config.classes_per_task,
    )
    return model, {"buffer": buffer}


def _arm_lwf(config: CLConfig, device: str) -> tuple[ContinualJointSystem, _ArmExtra]:
    model, lwf_loss = create_lwf_arm(
        config.input_dim,
        config.hidden_dim,
        config.output_dim,
        device,
        config.lr,
        classes_per_task=config.classes_per_task,
    )
    return model, {"lwf_loss": lwf_loss}


def _arm_fast_weights(
    config: CLConfig, device: str
) -> tuple[ContinualJointSystem, _ArmExtra]:
    return (
        create_fast_weight_arm(
            config.input_dim,
            config.hidden_dim,
            config.output_dim,
            device,
            config.lr,
            classes_per_task=config.classes_per_task,
        ),
        {},
    )


def _arm_matched(plasticity: str) -> _ArmBuilder:
    def build(config: CLConfig, device: str) -> tuple[ContinualJointSystem, _ArmExtra]:
        return (
            create_plasticity_arm(
                plasticity,
                config.input_dim,
                config.hidden_dim,
                config.output_dim,
                device,
                classes_per_task=config.classes_per_task,
            ),
            {},
        )

    return build


_ArmBuilder = Callable[[CLConfig, str], tuple["ContinualJointSystem", _ArmExtra]]
_ARM_BUILDERS: dict[str, _ArmBuilder] = {
    "backprop": _arm_backprop,
    "local": _arm_local,
    "local_ewc": _arm_local_ewc,
    "backprop_ewc": _arm_backprop_ewc,
    "ewc": _arm_ewc,
    "si": _arm_si,
    "replay": _arm_replay,
    "lwf": _arm_lwf,
    "fast_weights": _arm_fast_weights,
    "matched_null": _arm_matched("null"),
    "matched_fast_weights": _arm_matched("fast_weights"),
}


def _create_arm(
    arm_name: str, config: CLConfig, device_str: str
) -> tuple[ContinualJointSystem, _ArmExtra]:
    """Create continual learning arm model and extra components."""
    try:
        builder = _ARM_BUILDERS[arm_name]
    except KeyError:
        raise ValueError(f"Unknown arm: {arm_name}") from None
    return builder(config, device_str)


def _setup_stability_guard(config: CLConfig, model: ContinualJointSystem):
    """Create stability guard and transition function."""
    guard = create_stability_guard(
        threshold=config.stability_threshold,
        statistic="fast_proxy",
        window=config.stability_window,
    )
    transition_fn = make_transition_fn(model)
    guard_context = model.context
    return guard, transition_fn, guard_context


def _apply_task_boundary_setup(
    arm_name: str, model: ContinualJointSystem, extra: _ArmExtra
) -> None:
    """Apply arm-specific setup at task boundary."""
    if arm_name == "fast_weights":
        model.reset_plastic_state()
    lwf_loss = extra.get("lwf_loss")
    if lwf_loss is not None:
        prev_model = copy.deepcopy(model)
        lwf_loss.set_prev_model(prev_model)  # type: ignore[attr-defined]
    update = extra.get("update")
    if update is not None:
        anchor = getattr(update, "anchor", None)
        if callable(anchor):
            anchor(model.geometry.params)  # type: ignore[attr-defined]
        else:
            update.consolidate(model.geometry.params)  # type: ignore[attr-defined]
    si = extra.get("si")
    if si is not None:
        si.start_task()  # type: ignore[attr-defined]


def _run_training_step(
    arm_name: str,
    model: ContinualJointSystem,
    x: torch.Tensor,
    y: torch.Tensor,
    task_id: int,
    extra: _ArmExtra,
) -> dict[str, float]:
    """Run a single training step based on the arm's extra components."""
    lwf_loss_fn = extra.get("lwf_loss")
    if lwf_loss_fn is not None:
        return _lwf_train_step(model, x, y, task_id, lwf_loss_fn)  # type: ignore[arg-type]
    si_tracker = extra.get("si")
    if si_tracker is not None:
        return _si_train_step(model, x, y, task_id, si_tracker)  # type: ignore[arg-type]
    return model.train_step(x, y, task_id=task_id)


def _update_replay_buffer(
    arm_name: str, extra: _ArmExtra, x: torch.Tensor, y: torch.Tensor, task_id: int
) -> None:
    """Update replay buffer if applicable."""
    buffer = extra.get("buffer")
    if buffer is not None:
        buffer.add(x, y, task_id)  # type: ignore[attr-defined]


def _run_replay_training(
    arm_name: str,
    model: ContinualJointSystem,
    extra: _ArmExtra,
    config: CLConfig,
) -> None:
    """Run replay training if buffer has samples."""
    buffer = extra.get("buffer")
    if buffer is not None and len(buffer) > 0:  # type: ignore[arg-type]
        sample_size = min(config.batch_size, len(buffer))  # type: ignore[arg-type]
        rx, ry, rt = buffer.sample(sample_size)  # type: ignore[attr-defined]
        replay_task_id = rt[0].item()
        model.train_step(rx, ry, task_id=replay_task_id)


def _update_arm_importance(
    arm_name: str, model: ContinualJointSystem, extra: _ArmExtra
) -> None:
    """Update importance weights for EWC/SI at end of task."""
    update = extra.get("update")
    if update is not None:
        update.consolidate(model.geometry.params)  # type: ignore[attr-defined]
    si = extra.get("si")
    if si is not None:
        si.update_importance()  # type: ignore[attr-defined]


def _evaluate_task(
    model: ContinualJointSystem,
    test_loader,
    eval_task_id: int,
    device: torch.device,
    classes_per_task: int,
) -> float:
    """Evaluate model on a single task."""
    model.set_task(eval_task_id)
    correct = 0
    total = 0
    model.eval()
    with torch.no_grad():
        for x, y in test_loader:
            x = x.view(x.shape[0], -1).to(device)
            y = y.to(device)
            logits = model(x, task_id=eval_task_id)
            task_start = eval_task_id * classes_per_task
            task_end = task_start + classes_per_task
            task_logits = logits[:, task_start:task_end]
            pred = task_logits.argmax(dim=1)
            local_y = y % classes_per_task
            correct += (pred == local_y).sum().item()
            total += y.shape[0]
    return correct / total if total > 0 else 0.0


def _evaluate_tasks_so_far(
    model: ContinualJointSystem,
    test_loaders: list,
    task_id: int,
    device: torch.device,
    accuracy_matrix: list[list[float]],
    classes_per_task: int,
) -> None:
    """Evaluate on all tasks up to current task_id."""
    for eval_task_id in range(task_id + 1):
        acc = _evaluate_task(model, test_loaders[eval_task_id], eval_task_id, device, classes_per_task)
        accuracy_matrix[eval_task_id][task_id] = acc


def _evaluate_periodic_tasks(
    model: ContinualJointSystem,
    test_loaders: list,
    eval_task: int,
    device: torch.device,
    accuracy_matrix: list[list[float]],
    classes_per_task: int,
) -> None:
    """Evaluate on tasks up to eval_task (for task-free protocol)."""
    for eval_task_id in range(eval_task + 1):
        acc = _evaluate_task(model, test_loaders[eval_task_id], eval_task_id, device, classes_per_task)
        accuracy_matrix[eval_task_id][eval_task] = acc


def _run_task_incremental_protocol(
    model: ContinualJointSystem,
    task_loaders: list,
    test_loaders: list,
    config: CLConfig,
    arm_name: str,
    extra: _ArmExtra,
    *,
    guard,
    transition_fn,
    guard_context,
    device: torch.device,
    accuracy_matrix: list[list[float]],
    stability_verdicts: list,
) -> None:
    """Run task-incremental continual learning protocol."""
    for task_id in range(config.num_tasks):
        model.set_task(task_id)
        _apply_task_boundary_setup(arm_name, model, extra)

        loader = task_loaders[task_id]

        for epoch in range(config.epochs_per_task):
            for batch_idx, (x, y) in enumerate(loader):
                x = x.view(x.shape[0], -1).to(device)
                y = y.to(device)

                _run_training_step(arm_name, model, x, y, task_id, extra)

                verdict = check_stability(
                    guard,
                    transition_fn,
                    x,
                    step=epoch * len(loader) + batch_idx,
                    context=guard_context,
                )
                stability_verdicts.append(verdict)

                _update_replay_buffer(arm_name, extra, x, y, task_id)
                _run_replay_training(arm_name, model, extra, config)

        _update_arm_importance(arm_name, model, extra)
        _evaluate_tasks_so_far(model, test_loaders, task_id, device, accuracy_matrix, config.classes_per_task)


def _run_task_free_protocol(
    model: ContinualJointSystem,
    task_loaders: list,
    test_loaders: list,
    config: CLConfig,
    arm_name: str,
    extra: _ArmExtra,
    *,
    guard,
    transition_fn,
    guard_context,
    device: torch.device,
    accuracy_matrix: list[list[float]],
    stability_verdicts: list,
) -> None:
    """Run task-free continual learning protocol."""
    all_loaders = [iter(task_loaders[i]) for i in range(config.num_tasks)]
    total_batches = config.epochs_per_task * max(len(l) for l in task_loaders)

    for batch_idx in range(total_batches):
        task_id = batch_idx % config.num_tasks
        model.set_task(task_id)

        try:
            x, y = next(all_loaders[task_id])
        except StopIteration:
            all_loaders[task_id] = iter(task_loaders[task_id])
            x, y = next(all_loaders[task_id])

        x = x.view(x.shape[0], -1).to(device)
        y = y.to(device)

        model.train_step(x, y, task_id=task_id)

        verdict = check_stability(
            guard, transition_fn, x, step=batch_idx, context=guard_context
        )
        stability_verdicts.append(verdict)

        _update_replay_buffer(arm_name, extra, x, y, task_id)
        _run_replay_training(arm_name, model, extra, config)

        if batch_idx % (total_batches // config.num_tasks) == 0:
            eval_task = batch_idx // (total_batches // config.num_tasks)
            if eval_task < config.num_tasks:
                _evaluate_periodic_tasks(
                    model, test_loaders, eval_task, device, accuracy_matrix, config.classes_per_task
                )


def _finalize_metrics(
    model: ContinualJointSystem,
    test_loaders: list,
    accuracy_matrix: list[list[float]],
    stability_verdicts: list,
    total_time: float,
    arm_name: str,
    extra: _ArmExtra,
    config: CLConfig,
) -> CLMetrics:
    """Compute and finalize CL metrics."""
    final_metrics = compute_cl_metrics(
        model, test_loaders, config.num_tasks - 1, accuracy_matrix, config.classes_per_task
    )
    final_metrics.total_time_s = total_time
    final_metrics.stability_verdicts = stability_verdicts
    final_metrics.max_jacobian_amplification = (
        max(v.statistic for v in stability_verdicts) if stability_verdicts else 0.0
    )

    if hasattr(model.plasticity, "fast_weight_dim"):
        final_metrics.plastic_state_bytes = (
            model.plasticity.fast_weight_dim * 4 * config.batch_size  # type: ignore[attr-defined]
        )
    for component in (extra.get("update"), extra.get("si")):
        state_bytes = getattr(component, "state_bytes", None)
        if callable(state_bytes):
            final_metrics.plastic_state_bytes = cast("float", state_bytes())
    if arm_name == "replay":
        buffer = extra.get("buffer")
        if buffer is not None:
            final_metrics.replay_buffer_bytes = buffer.memory_bytes()  # type: ignore[attr-defined]

    return final_metrics


def run_continual_learning(
    arm_name: str,
    config: CLConfig,
    protocol: str = "task_incremental",
) -> CLMetrics:
    """Run continual learning for one arm."""
    device = _resolve_device(config)
    device_str = str(device)
    torch.manual_seed(config.seed)
    random.seed(config.seed)

    task_loaders, test_loaders = _create_task_loaders(config, device_str)
    model, extra = _create_arm(arm_name, config, device_str)
    guard, transition_fn, guard_context = _setup_stability_guard(config, model)

    accuracy_matrix = [[0.0 for _ in range(config.num_tasks)] for _ in range(config.num_tasks)]
    stability_verdicts: list = []
    start_time = time.perf_counter()

    if protocol == "task_incremental":
        _run_task_incremental_protocol(
            model,
            task_loaders,
            test_loaders,
            config,
            arm_name,
            extra,
            guard=guard,
            transition_fn=transition_fn,
            guard_context=guard_context,
            device=device,
            accuracy_matrix=accuracy_matrix,
            stability_verdicts=stability_verdicts,
        )
    elif protocol == "task_free":
        _run_task_free_protocol(
            model,
            task_loaders,
            test_loaders,
            config,
            arm_name,
            extra,
            guard=guard,
            transition_fn=transition_fn,
            guard_context=guard_context,
            device=device,
            accuracy_matrix=accuracy_matrix,
            stability_verdicts=stability_verdicts,
        )
    else:
        raise ValueError(f"Unknown protocol: {protocol}")

    total_time = time.perf_counter() - start_time

    return _finalize_metrics(
        model,
        test_loaders,
        accuracy_matrix,
        stability_verdicts,
        total_time,
        arm_name,
        extra,
        config,
    )


def _aggregate_seed_results(seeds_list: list[dict[str, Any]]) -> dict[str, float]:
    """Aggregate metrics across seeds."""
    results: dict[str, float] = {}
    if not seeds_list:
        return results

    for key in [
        "avg_forgetting",
        "backward_transfer",
        "forward_transfer",
        "max_jacobian_amplification",
        "total_time_s",
    ]:
        vals = [float(s[key]) for s in seeds_list]
        mean_val = sum(vals) / len(vals)
        results[f"mean_{key}"] = mean_val
        results[f"std_{key}"] = (
            (sum((v - mean_val) ** 2 for v in vals) / len(vals)) ** 0.5
            if len(vals) > 1
            else 0.0
        )
    return results


def run_continual_learning_suite(
    arms: list[str],
    protocols: list[str],
    output_dir: str | Path,
    config: CLConfig | None = None,
    seeds: int = 3,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Run continual learning benchmark suite."""
    config = config or CLConfig()
    output_dir = Path(output_dir)

    device = (
        "cuda"
        if config.device == "auto" and torch.cuda.is_available()
        else config.device
    )
    config.device = device

    all_results: dict[str, dict[str, dict[str, Any]]] = {}

    for arm in arms:
        all_results[arm] = {}
        for protocol in protocols:
            print(f"\n=== {arm} / {protocol} ===")
            arm_results: dict[str, Any] = {"seeds": []}

            for seed in range(seeds):
                print(f"  Seed {seed}...")
                config.seed = seed
                metrics = run_continual_learning(arm, config, protocol)
                arm_results["seeds"].append({
                    "final_accuracies": metrics.final_accuracies,
                    "accuracy_matrix": metrics.accuracy_matrix,
                    "backward_transfer": metrics.backward_transfer,
                    "forward_transfer": metrics.forward_transfer,
                    "forgetting": metrics.forgetting,
                    "avg_forgetting": metrics.avg_forgetting,
                    "peak_memory_mb": metrics.peak_memory_mb,
                    "plastic_state_bytes": metrics.plastic_state_bytes,
                    "replay_buffer_bytes": metrics.replay_buffer_bytes,
                    "max_jacobian_amplification": metrics.max_jacobian_amplification,
                    "stability_kills": sum(
                        1
                        for v in metrics.stability_verdicts
                        if getattr(v, "kill", False)
                    ),
                    "total_time_s": metrics.total_time_s,
                })
                print(
                    f"    Avg forgetting: {metrics.avg_forgetting:.4f}, BWT: {metrics.backward_transfer:.4f}"
                )

            arm_results.update(_aggregate_seed_results(arm_results["seeds"]))
            all_results[arm][protocol] = arm_results

    output_dir.mkdir(parents=True, exist_ok=True)
    results_file = output_dir / "continual_learning_results.json"
    with results_file.open("w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to {results_file}")
    return all_results
    return all_results


__all__ = [
    "run_continual_learning",
    "run_continual_learning_suite",
]
