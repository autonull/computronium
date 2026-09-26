"""TileNet Scaling Sweep — Depth/Width Scaling Laws Across Algorithms.

Scaling law analysis for TileNet across PC, EP, FA, TP, Hebbian, SNN, and backprop
on MNIST and CIFAR-10. Produces scaling law plots and Pareto frontiers.

Usage:
    python -m computronium.experiments.tile_scaling --tasks mnist,cifar10 --algorithms all --depths 2,4,6,8,10,12 --widths 32,64,128,256 --seeds 3
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import torch

from computronium.analysis.pareto import ParetoFrontier, compute_pareto_frontier
from computronium.analysis.scaling import ScalingLawFitter, fit_power_law
from computronium.core.rules import rule_system
from computronium.core.system_trainer.factory import param_count
from computronium.core.system_trainer.train_task import final_metrics, train_task

if TYPE_CHECKING:
    from computronium.ontology import System

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass(frozen=True, slots=True)
class ScalingConfig:
    """Configuration for scaling sweep."""

    tasks: list[str] = field(default_factory=lambda: ["mnist", "cifar10"])
    algorithms: list[str] = field(
        default_factory=lambda: ["ep", "fa", "tp", "pc", "hebbian", "snn", "backprop"]
    )
    depths: list[int] = field(default_factory=lambda: [2, 4, 6, 8, 10, 12])
    widths: list[int] = field(default_factory=lambda: [32, 64, 128, 256])
    seeds: int = 3
    epochs: int = 10
    batch_size: int = 64
    learning_rate: float = 1e-3
    output_dir: str = "results/scaling_sweep"
    device: str = "auto"


def _resolve_device(device: str) -> str:
    """Resolve device string."""
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def _run_single_experiment(
    algorithm: str,
    task: str,
    depth: int,
    width: int,
    seed: int,
    config: ScalingConfig,
) -> dict:
    """Run a single training experiment: one rule, one depth, one width."""
    built: list[System] = []

    def factory(input_dim: int, output_dim: int) -> System:
        system = rule_system(
            algorithm,
            input_dim,
            output_dim,
            hidden_dims=(width,) * depth,
            lr=config.learning_rate,
            device=config.device,
        )
        built.append(system)
        return system

    start_time = time.time()
    history = train_task(
        factory,
        task,
        config.epochs,
        batch_size=config.batch_size,
        device=config.device,
        seed=seed,
    )
    elapsed = time.time() - start_time
    final = final_metrics(history)
    return {
        "model": algorithm,
        "algorithm": algorithm,
        "task": task,
        "depth": depth,
        "width": width,
        "seed": seed,
        "accuracy": final.get("val_acc", 0.0),
        "loss": final.get("val_loss", float("inf")),
        "time": elapsed,
        "params": param_count(built[0]) if built else 0,
        "success": bool(history),
    }


def run_scaling_sweep(config: ScalingConfig) -> list[dict]:
    """Run the full scaling sweep."""
    results = []
    device = _resolve_device(config.device)
    config = dataclasses.replace(config, device=device)

    total_experiments = (
        len(config.tasks)
        * len(config.algorithms)
        * len(config.depths)
        * len(config.widths)
        * config.seeds
    )

    logger.info("Starting scaling sweep: %d total experiments", total_experiments)
    logger.info("Tasks: %s", config.tasks)
    logger.info("Algorithms: %s", config.algorithms)
    logger.info("Depths: %s", config.depths)
    logger.info("Widths: %s", config.widths)
    logger.info("Seeds per config: %d", config.seeds)

    exp_count = 0
    for task in config.tasks:  # ruff: ignore[too-many-nested-blocks]
        for algorithm in config.algorithms:
            for depth in config.depths:
                for width in config.widths:
                    for seed in range(config.seeds):
                        exp_count += 1
                        logger.info(
                            "[%d/%d] %s on %s: depth=%d width=%d seed=%d",
                            exp_count,
                            total_experiments,
                            algorithm,
                            task,
                            depth,
                            width,
                            seed,
                        )

                        try:
                            result = _run_single_experiment(
                                algorithm, task, depth, width, seed, config
                            )
                            results.append(result)
                        except Exception as e:
                            logger.exception(
                                "Experiment failed: %s on %s depth=%d width=%d seed=%d",
                                algorithm,
                                task,
                                depth,
                                width,
                                seed,
                            )
                            results.append({
                                "model": algorithm,
                                "task": task,
                                "depth": depth,
                                "width": width,
                                "seed": seed,
                                "accuracy": 0.0,
                                "loss": float("inf"),
                                "time": 0.0,
                                "params": 0,
                                "success": False,
                                "error": str(e),
                            })

    return results


def _aggregate_results(results: list[dict]) -> list[dict]:
    """Aggregate results across seeds."""
    import pandas as pd

    df = pd.DataFrame(results)
    if df.empty:
        return []

    # Group by task, model, depth, width
    grouped = (
        df
        .groupby(["task", "model", "depth", "width"])
        .agg({
            "accuracy": ["mean", "std", "count"],
            "loss": ["mean", "std"],
            "time": "mean",
            "params": "mean",
            "success": "sum",
        })
        .reset_index()
    )

    # Flatten column names
    grouped.columns = [
        "_".join(col).strip("_") if col[1] else col[0] for col in grouped.columns.values
    ]

    return grouped.to_dict("records")


def _save_results(results: list[dict], output_dir: str) -> None:
    """Save results to disk."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Raw results
    with Path(output_path / "raw_results.jsonl").open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")

    # Aggregated
    aggregated = _aggregate_results(results)
    with Path(output_path / "aggregated_results.json").open("w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=2, default=str)

    logger.info("Saved results to %s", output_path)


def _analyze_scaling_laws(results: list[dict], output_dir: str) -> None:
    """Fit scaling laws to the results."""
    import pandas as pd

    df = pd.DataFrame(results)
    if df.empty:
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fitter = ScalingLawFitter()

    for task in df["task"].unique():
        task_df = df[df["task"] == task]
        for model in task_df["model"].unique():
            model_df = task_df[task_df["model"] == model]

            # Width scaling (fix depth at median)
            median_depth = model_df["depth"].median()
            width_df = model_df[model_df["depth"] == median_depth]
            if len(width_df) >= 3:
                try:  # noqa: PLR0915
                    params = width_df["params"].values
                    acc = width_df["accuracy_mean"].values
                    valid = (params > 0) & np.isfinite(acc)
                    if valid.sum() >= 3:
                        law = fit_power_law(params[valid], acc[valid])
                        fitter.add_fit(f"{task}_{model}_width", law)
                except Exception as e:
                    logger.warning(
                        "Width scaling fit failed for %s/%s: %s", task, model, e
                    )

            # Depth scaling (fix width at median)
            median_width = model_df["width"].median()
            depth_df = model_df[model_df["width"] == median_width]
            if len(depth_df) >= 3:
                try:  # noqa: PLR0915
                    params = depth_df["params"].values
                    acc = depth_df["accuracy_mean"].values
                    valid = (params > 0) & np.isfinite(acc)
                    if valid.sum() >= 3:
                        law = fit_power_law(params[valid], acc[valid])
                        fitter.add_fit(f"{task}_{model}_depth", law)
                except Exception as e:
                    logger.warning(
                        "Depth scaling fit failed for %s/%s: %s", task, model, e
                    )

    # Save scaling law fits
    fitter.save(output_path / "scaling_laws.json")

    # Generate scaling law plots
    fitter.plot_all(output_path / "scaling_plots")


def _compute_pareto_frontiers(results: list[dict], output_dir: str) -> None:
    """Compute Pareto frontiers for each task."""
    import pandas as pd

    df = pd.DataFrame(results)
    if df.empty:
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for task in df["task"].unique():
        task_df = df[df["task"] == task]

        # Multi-objective: maximize accuracy, minimize params, minimize time
        frontier = compute_pareto_frontier(
            task_df,
            objectives=["accuracy", "params", "time"],
            directions=["maximize", "minimize", "minimize"],
        )

        frontier.to_json(output_path / f"pareto_{task}.json", orient="records")

        # Plot
        try:
            pareto_obj = ParetoFrontier(frontier)
            pareto_obj.plot(output_path / f"pareto_{task}.html")
        except Exception as e:
            logger.warning("Pareto plot failed for %s: %s", task, e)


def main():
    parser = argparse.ArgumentParser(description="TileNet Scaling Sweep Experiment")
    parser.add_argument(
        "--tasks", default="mnist,cifar10", help="Comma-separated tasks"
    )
    parser.add_argument(
        "--algorithms",
        default="ep,fa,tp,pc,hebbian,snn,backprop",
        help="Comma-separated algorithms",
    )
    parser.add_argument(
        "--depths", default="2,4,6,8,10,12", help="Comma-separated depths"
    )
    parser.add_argument(
        "--widths", default="32,64,128,256", help="Comma-separated widths"
    )
    parser.add_argument("--seeds", type=int, default=3, help="Seeds per config")
    parser.add_argument("--epochs", type=int, default=10, help="Epochs per run")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument(
        "--output-dir", default="results/scaling_sweep", help="Output directory"
    )
    parser.add_argument("--device", default="auto", help="Device (auto, cuda, cpu)")
    parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    config = ScalingConfig(
        tasks=args.tasks.split(","),
        algorithms=args.algorithms.split(","),
        depths=[int(d) for d in args.depths.split(",")],
        widths=[int(w) for w in args.widths.split(",")],
        seeds=args.seeds,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        output_dir=args.output_dir,
        device=args.device,
    )

    logger.info("Starting TileNet Scaling Sweep")

    # Run experiments
    results = run_scaling_sweep(config)

    # Save raw results
    _save_results(results, config.output_dir)

    if not args.skip_analysis:
        # Analyze scaling laws
        _analyze_scaling_laws(results, config.output_dir)

        # Compute Pareto frontiers
        _compute_pareto_frontiers(results, config.output_dir)

    logger.info("Scaling sweep complete. Results in %s", config.output_dir)


if __name__ == "__main__":
    main()
