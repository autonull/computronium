"""Batched multi-seed evaluation utilities.

Experimental: vectorizes training across seeds using torch.vmap.
Currently supports simple feedforward + backprop configurations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.core.system_trainer.config import SystemTrainerConfig
    from computronium.core.system_trainer.trainer import _DataProvider
    from computronium.ontology import System


@dataclass
class MultiSeedResult:
    """Results from multi-seed evaluation."""

    seeds: list[int]
    metrics_per_seed: list[dict[str, float]]
    mean_metrics: dict[str, float]
    std_metrics: dict[str, float]


def _make_vmap_compatible_system(
    system_factory: Callable[[int], System],
    seeds: list[int],
) -> tuple[System, list[dict[str, Tensor]]]:
    """Create a system with stacked parameters for vmap.

    Args:
        system_factory: Function that creates a System given a seed.
        seeds: List of seeds to evaluate.

    Returns:
        Tuple of (base_system, list_of_param_dicts) where each param_dict
        contains the geometry parameters for that seed.
    """
    systems = [system_factory(seed) for seed in seeds]
    base_system = systems[0]

    # Collect parameters per seed
    param_dicts = []
    for sys in systems:
        params = {
            name: p.detach().clone().requires_grad_(True)
            for name, p in sys.geometry.params.items()
        }
        param_dicts.append(params)

    return base_system, param_dicts


def _vmap_train_step(
    base_system: System,
    param_dicts: list[dict[str, Tensor]],
    x: Tensor,
    y: Tensor,
    seeds: list[int],
) -> list[dict[str, float]]:
    """Vectorized train_step across seeds using torch.vmap.

    Note: This is a simplified implementation that works for feedforward
    geometries with backprop credit. Full support requires vmap-compatible
    credit/settle/update implementations.
    """
    # Stack parameters along seed dimension
    stacked_params = {}
    for name in param_dicts[0]:
        stacked_params[name] = torch.stack([p[name] for p in param_dicts], dim=0)

    # For now, fall back to sequential execution
    # TODO: Implement true vmap when all components support it
    results = []
    for i, seed in enumerate(seeds):
        # Create system with seed-specific params
        system = base_system
        for name, param in stacked_params.items():
            system.geometry.params[name].data.copy_(param[i])

        torch.manual_seed(seed)
        metrics = system.train_step(x, y)
        results.append(metrics)

    return results


def run_multi_seed_evaluation(
    system_factory: Callable[[int], System],
    train_data: _DataProvider,
    config: SystemTrainerConfig,
    seeds: list[int],
    val_data: _DataProvider | None = None,
    max_batches: int | None = None,
) -> MultiSeedResult:
    """Run evaluation across multiple seeds.

    Args:
        system_factory: Function that creates a System given a seed.
        train_data: Training data provider.
        config: Trainer configuration.
        seeds: List of seeds to evaluate.
        val_data: Optional validation data.
        max_batches: Optional limit on batches per epoch.

    Returns:
        MultiSeedResult with per-seed and aggregate metrics.
    """
    from computronium.core.system_trainer.trainer import SystemTrainer

    all_seed_metrics: list[list[dict[str, float]]] = []

    for seed in seeds:
        torch.manual_seed(seed)
        system = system_factory(seed)
        trainer = SystemTrainer(
            system=system,
            config=config,
            train_data=train_data,
            val_data=val_data,
        )

        if max_batches:
            original_limit = config.limit_train_batches
            config.limit_train_batches = max_batches

        history = trainer.fit()

        if max_batches:
            config.limit_train_batches = original_limit

        # Extract final epoch metrics
        final_metrics = history[-1] if history else {}
        all_seed_metrics.append([final_metrics])

    # Compute aggregate statistics
    if not all_seed_metrics:
        return MultiSeedResult(
            seeds=seeds,
            metrics_per_seed=[],
            mean_metrics={},
            std_metrics={},
        )

    # Flatten: we have list of [epoch_metrics] per seed, take last epoch
    seed_final_metrics = [m[-1] for m in all_seed_metrics if m]

    mean_metrics = {}
    std_metrics = {}
    if seed_final_metrics:
        keys = seed_final_metrics[0].keys()
        for key in keys:
            values = [m[key] for m in seed_final_metrics]
            mean_metrics[key] = sum(values) / len(values)
            if len(values) > 1:
                variance = sum((v - mean_metrics[key]) ** 2 for v in values) / (
                    len(values) - 1
                )
                std_metrics[key] = variance**0.5
            else:
                std_metrics[key] = 0.0

    return MultiSeedResult(
        seeds=seeds,
        metrics_per_seed=seed_final_metrics,
        mean_metrics=mean_metrics,
        std_metrics=std_metrics,
    )


def run_multi_seed_parallel(
    system_factory: Callable[[int], System],
    train_data: _DataProvider,
    config: SystemTrainerConfig,
    seeds: list[int],
    val_data: _DataProvider | None = None,
    max_batches: int | None = None,
    num_workers: int = 4,
) -> MultiSeedResult:
    """Run multi-seed evaluation in parallel using threading.

    This is a practical implementation for parallelism that works with
    locally defined factories. Uses threading instead of multiprocessing
    to avoid pickling issues with local functions and generators.

    Note: Due to Python's GIL, this provides limited speedup for CPU-bound
    training. For true parallelism, use multiprocessing with a top-level
    factory function (not a local closure).
    """
    import concurrent.futures

    from computronium.core.system_trainer.trainer import SystemTrainer

    # Materialize data for thread safety
    train_batches = list(train_data)
    val_batches = list(val_data) if val_data is not None else None

    def _run_single_seed(seed: int) -> dict[str, float]:
        import torch

        torch.manual_seed(seed)
        system = system_factory(seed)
        trainer = SystemTrainer(
            system=system,
            config=config,
            train_data=train_batches,
            val_data=val_batches,
        )

        if max_batches:
            original_limit = config.limit_train_batches
            config.limit_train_batches = max_batches

        history = trainer.fit()

        if max_batches:
            config.limit_train_batches = original_limit

        return history[-1] if history else {}

    # Use threading for parallelism (avoids pickling issues)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        seed_metrics = list(executor.map(_run_single_seed, seeds))

    # Compute aggregate statistics
    mean_metrics = {}
    std_metrics = {}
    if seed_metrics:
        keys = seed_metrics[0].keys()
        for key in keys:
            values = [m[key] for m in seed_metrics]
            mean_metrics[key] = sum(values) / len(values)
            if len(values) > 1:
                variance = sum((v - mean_metrics[key]) ** 2 for v in values) / (
                    len(values) - 1
                )
                std_metrics[key] = variance**0.5
            else:
                std_metrics[key] = 0.0

    return MultiSeedResult(
        seeds=seeds,
        metrics_per_seed=seed_metrics,
        mean_metrics=mean_metrics,
        std_metrics=std_metrics,
    )


def run_multi_seed_multiprocess(
    system_factory: Callable[[int], System],
    train_data: _DataProvider,
    config: SystemTrainerConfig,
    seeds: list[int],
    val_data: _DataProvider | None = None,
    max_batches: int | None = None,
    num_workers: int = 4,
) -> MultiSeedResult:
    """Run multi-seed evaluation in parallel using multiprocessing.

    This provides true CPU parallelism by spawning separate processes.
    Requires `system_factory` to be a top-level function (not a closure or
    lambda) so it can be pickled and sent to worker processes.

    The train/val data providers must also be picklable (e.g., lists of
    batches, not generators).

    Args:
        system_factory: Top-level function that creates a System given a seed.
        train_data: Training data provider (must be picklable).
        config: Trainer configuration (must be picklable).
        seeds: List of seeds to evaluate.
        val_data: Optional validation data provider (must be picklable).
        max_batches: Optional limit on batches per epoch.
        num_workers: Number of worker processes.

    Returns:
        MultiSeedResult with per-seed and aggregate metrics.
    """
    import multiprocessing as mp
    from functools import partial

    # Materialize data for pickling
    train_batches = list(train_data)
    val_batches = list(val_data) if val_data is not None else None

    # Use spawn context for CUDA safety
    ctx = mp.get_context("spawn")

    def _run_single_seed(
        seed: int,
        factory: Callable[[int], System],
        train_data_local: list[tuple[Tensor, Tensor]],
        val_data_local: list[tuple[Tensor, Tensor]] | None,
        config_local: SystemTrainerConfig,
        max_batches_local: int | None,
    ) -> dict[str, float]:
        import torch

        from computronium.core.system_trainer.trainer import SystemTrainer

        torch.manual_seed(seed)
        system = factory(seed)
        trainer = SystemTrainer(
            system=system,
            config=config_local,
            train_data=train_data_local,
            val_data=val_data_local,
        )

        if max_batches_local:
            original_limit = config_local.limit_train_batches
            config_local.limit_train_batches = max_batches_local

        history = trainer.fit()

        if max_batches_local:
            config_local.limit_train_batches = original_limit

        return history[-1] if history else {}

    # Prepare partial function with picklable arguments
    worker_fn = partial(
        _run_single_seed,
        factory=system_factory,
        train_data_local=train_batches,
        val_data_local=val_batches,
        config_local=config,
        max_batches_local=max_batches,
    )

    with ctx.Pool(processes=num_workers) as pool:
        seed_metrics = pool.map(worker_fn, seeds)

    # Compute aggregate statistics
    mean_metrics = {}
    std_metrics = {}
    if seed_metrics:
        keys = seed_metrics[0].keys()
        for key in keys:
            values = [m[key] for m in seed_metrics]
            mean_metrics[key] = sum(values) / len(values)
            if len(values) > 1:
                variance = sum((v - mean_metrics[key]) ** 2 for v in values) / (
                    len(values) - 1
                )
                std_metrics[key] = variance**0.5
            else:
                std_metrics[key] = 0.0

    return MultiSeedResult(
        seeds=seeds,
        metrics_per_seed=seed_metrics,
        mean_metrics=mean_metrics,
        std_metrics=std_metrics,
    )


__all__ = [
    "MultiSeedResult",
    "_make_vmap_compatible_system",
    "_vmap_train_step",
    "run_multi_seed_evaluation",
    "run_multi_seed_multiprocess",
    "run_multi_seed_parallel",
]
