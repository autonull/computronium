"""Continual learning benchmark runner."""

from __future__ import annotations

import copy
import json
import random
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, TypedDict

import torch

from computronium.core.continual.arms import (
    create_backprop_arm,
    create_ewc_arm,
    create_fast_weight_arm,
    create_lwf_arm,
    create_replay_arm,
    create_si_arm,
)
from computronium.core.continual.constants import CL_NUM_TASKS
from computronium.core.continual.metrics import CLConfig, CLMetrics, compute_cl_metrics
from computronium.core.continual.stability import (
    check_stability,
    create_stability_guard,
    make_transition_fn,
)
from computronium.core.continual.training import _lwf_train_step, _si_train_step
from computronium.domains.base import TaskSplit
from computronium.domains.vision import SplitMNIST

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


def _create_task_loaders(config: CLConfig, device_str: str) -> tuple[list, list]:
    """Create train and test data loaders for all tasks."""
    task_loaders = []
    for task_id in range(CL_NUM_TASKS):
        task = SplitMNIST(
            task_id=task_id,
            batch_size=config.batch_size,
            device=device_str,
            num_workers=config.num_workers,
        )
        task.setup()
        task_loaders.append(task.get_dataloader(TaskSplit.TRAIN))

    test_loaders = []
    for task_id in range(CL_NUM_TASKS):
        task = SplitMNIST(
            task_id=task_id,
            batch_size=config.batch_size,
            device=device_str,
            num_workers=config.num_workers,
        )
        task.setup()
        test_loaders.append(task.get_dataloader(TaskSplit.TEST))

    return task_loaders, test_loaders


def _create_arm(
    arm_name: str, config: CLConfig, device_str: str
) -> tuple["ContinualJointSystem", _ArmExtra]:
    """Create continual learning arm model and extra components."""
    extra: _ArmExtra = {}

    if arm_name == "fast_weights":
        model = create_fast_weight_arm(
            config.input_dim, config.hidden_dim, config.output_dim, device_str
        )
    elif arm_name == "ewc":
        model, update = create_ewc_arm(
            config.input_dim,
            config.hidden_dim,
            config.output_dim,
            device_str,
            config.ewc_lambda,
        )
        extra["update"] = update
    elif arm_name == "backprop":
        model = create_backprop_arm(
            config.input_dim, config.hidden_dim, config.output_dim, device_str
        )
    elif arm_name == "replay":
        model, buffer = create_replay_arm(
            config.input_dim,
            config.hidden_dim,
            config.output_dim,
            device_str,
            config.replay_capacity,
        )
        extra["buffer"] = buffer
    elif arm_name == "lwf":
        model, lwf_loss = create_lwf_arm(
            config.input_dim, config.hidden_dim, config.output_dim, device_str
        )
        extra["lwf_loss"] = lwf_loss
    elif arm_name == "si":
        model, si = create_si_arm(
            config.input_dim, config.hidden_dim, config.output_dim, device_str
        )
        extra["si"] = si
    else:
        raise ValueError(f"Unknown arm: {arm_name}")

    return model, extra


def _setup_stability_guard(config: CLConfig, model: "ContinualJointSystem"):
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
    arm_name: str, model: "ContinualJointSystem", extra: _ArmExtra
) -> None:
    """Apply arm-specific setup at task boundary."""
    if arm_name == "fast_weights":
        model.reset_plastic_state()
    elif arm_name == "ewc":
        update = extra.get("update")
        if update is not None:
            update.consolidate(model.geometry.params)  # type: ignore[attr-defined]
    elif arm_name == "lwf":
        lwf_loss = extra.get("lwf_loss")
        if lwf_loss is not None:
            prev_model = copy.deepcopy(model)
            lwf_loss.set_prev_model(prev_model)  # type: ignore[attr-defined]
    elif arm_name == "si":
        si = extra.get("si")
        if si is not None:
            si.start_task()  # type: ignore[attr-defined]


def _run_training_step(
    arm_name: str,
    model: "ContinualJointSystem",
    x: torch.Tensor,
    y: torch.Tensor,
    task_id: int,
    extra: _ArmExtra,
) -> dict[str, float]:
    """Run a single training step based on arm type."""
    if arm_name == "lwf":
        lwf_loss_fn = extra.get("lwf_loss")
        if lwf_loss_fn is not None:
            return _lwf_train_step(model, x, y, task_id, lwf_loss_fn)  # type: ignore[arg-type]
    elif arm_name == "si":
        si_tracker = extra.get("si")
        if si_tracker is not None:
            return _si_train_step(model, x, y, task_id, si_tracker)  # type: ignore[arg-type]
    return model.train_step(x, y, task_id=task_id)


def _update_replay_buffer(
    arm_name: str, extra: _ArmExtra, x: torch.Tensor, y: torch.Tensor, task_id: int
) -> None:
    """Update replay buffer if applicable."""
    if arm_name == "replay":
        buffer = extra.get("buffer")
        if buffer is not None:
            buffer.add(x, y, task_id)  # type: ignore[attr-defined]


def _run_replay_training(
    arm_name: str,
    model: "ContinualJointSystem",
    extra: _ArmExtra,
    config: CLConfig,
) -> None:
    """Run replay training if buffer has samples."""
    if arm_name == "replay":
        buffer = extra.get("buffer")
        if buffer is not None and len(buffer) > 0:  # type: ignore[arg-type]
            sample_size = min(config.batch_size, len(buffer))  # type: ignore[arg-type]
            rx, ry, rt = buffer.sample(sample_size)  # type: ignore[attr-defined]
            replay_task_id = rt[0].item()
            model.train_step(rx, ry, task_id=replay_task_id)


def _update_arm_importance(
    arm_name: str, model: "ContinualJointSystem", extra: _ArmExtra
) -> None:
    """Update importance weights for EWC/SI at end of task."""
    if arm_name == "ewc":
        update = extra.get("update")
        if update is not None:
            update.consolidate(model.geometry.params)  # type: ignore[attr-defined]
    elif arm_name == "si":
        si = extra.get("si")
        if si is not None:
            si.update_importance()  # type: ignore[attr-defined]


def _evaluate_task(
    model: "ContinualJointSystem",
    test_loader,
    eval_task_id: int,
    device: torch.device,
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
            task_start = eval_task_id * 2  # CL_CLASSES_PER_TASK
            task_end = task_start + 2
            task_logits = logits[:, task_start:task_end]
            pred = task_logits.argmax(dim=1)
            local_y = y % 2
            correct += (pred == local_y).sum().item()
            total += y.shape[0]
    return correct / total if total > 0 else 0.0


def _evaluate_tasks_so_far(
    model: "ContinualJointSystem",
    test_loaders: list,
    task_id: int,
    device: torch.device,
    accuracy_matrix: list[list[float]],
) -> None:
    """Evaluate on all tasks up to current task_id."""
    for eval_task_id in range(task_id + 1):
        acc = _evaluate_task(model, test_loaders[eval_task_id], eval_task_id, device)
        accuracy_matrix[eval_task_id][task_id] = acc


def _evaluate_periodic_tasks(
    model: "ContinualJointSystem",
    test_loaders: list,
    eval_task: int,
    device: torch.device,
    accuracy_matrix: list[list[float]],
) -> None:
    """Evaluate on tasks up to eval_task (for task-free protocol)."""
    for eval_task_id in range(eval_task + 1):
        acc = _evaluate_task(model, test_loaders[eval_task_id], eval_task_id, device)
        accuracy_matrix[eval_task_id][eval_task] = acc


def _run_task_incremental_protocol(
    model: "ContinualJointSystem",
    task_loaders: list,
    test_loaders: list,
    config: CLConfig,
    arm_name: str,
    extra: _ArmExtra,
    guard,
    transition_fn,
    guard_context,
    device: torch.device,
    accuracy_matrix: list[list[float]],
    stability_verdicts: list,
) -> None:
    """Run task-incremental continual learning protocol."""
    for task_id in range(CL_NUM_TASKS):
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
        _evaluate_tasks_so_far(model, test_loaders, task_id, device, accuracy_matrix)


def _run_task_free_protocol(
    model: "ContinualJointSystem",
    task_loaders: list,
    test_loaders: list,
    config: CLConfig,
    arm_name: str,
    extra: _ArmExtra,
    guard,
    transition_fn,
    guard_context,
    device: torch.device,
    accuracy_matrix: list[list[float]],
    stability_verdicts: list,
) -> None:
    """Run task-free continual learning protocol."""
    all_loaders = [iter(task_loaders[i]) for i in range(CL_NUM_TASKS)]
    total_batches = config.epochs_per_task * max(len(l) for l in task_loaders)

    for batch_idx in range(total_batches):
        task_id = batch_idx % CL_NUM_TASKS
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

        if batch_idx % (total_batches // CL_NUM_TASKS) == 0:
            eval_task = batch_idx // (total_batches // CL_NUM_TASKS)
            if eval_task < CL_NUM_TASKS:
                _evaluate_periodic_tasks(
                    model, test_loaders, eval_task, device, accuracy_matrix
                )


def _finalize_metrics(
    model: "ContinualJointSystem",
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
        model, test_loaders, CL_NUM_TASKS - 1, accuracy_matrix
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

    accuracy_matrix = [[0.0 for _ in range(CL_NUM_TASKS)] for _ in range(CL_NUM_TASKS)]
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
            guard,
            transition_fn,
            guard_context,
            device,
            accuracy_matrix,
            stability_verdicts,
        )
    elif protocol == "task_free":
        _run_task_free_protocol(
            model,
            task_loaders,
            test_loaders,
            config,
            arm_name,
            extra,
            guard,
            transition_fn,
            guard_context,
            device,
            accuracy_matrix,
            stability_verdicts,
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
