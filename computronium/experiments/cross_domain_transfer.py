"""Cross-Domain Transfer — Vision→Tabular/Vision Transfer Efficiency.

Tests whether local learning representations transfer better than backprop.
Measures transfer efficiency across domains.

Target domains are the ones the loader-based training path can actually
reach. The four this experiment used to name -- language, RL, graph,
time series -- cannot, and the reasons are properties of the tree rather
than of the experiment: the language lane yields token *indices* and the
5-D path has no embedding geometry, while the RL and graph tasks provide no
``(inputs, targets)`` dataloader at all. ``train_task`` refuses each with
that message rather than failing inside a geometry.

Usage:
    python -m computronium.experiments.cross_domain_transfer --source vision --targets tabular,vision --seeds 3
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

from computronium.core.rules import rule_system
from computronium.core.system_trainer.factory import param_count
from computronium.core.system_trainer.train_task import final_metrics, train_task
from computronium.validation.statistics import (
    cohens_d,
    permutation_test_p,
)

if TYPE_CHECKING:
    from computronium.ontology import System

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass(frozen=True, slots=True)
class TransferConfig:
    """Configuration for cross-domain transfer experiment."""

    source_domains: list[str] = field(default_factory=lambda: ["vision"])
    target_domains: list[str] = field(default_factory=lambda: ["tabular", "vision"])
    source_tasks: list[str] = field(default_factory=lambda: ["cifar10"])
    target_tasks: dict[str, list[str]] = field(
        default_factory=lambda: {"tabular": ["iris", "wine"], "vision": ["xor"]}
    )
    algorithms: list[str] = field(
        default_factory=lambda: ["ep", "fa", "pc", "hebbian", "backprop"]
    )
    finetune_epochs: int = 10
    pretrain_epochs: int = 20
    batch_size: int = 64
    learning_rate: float = 1e-3
    finetune_lr: float = 1e-4
    seeds: int = 3
    output_dir: str = "results/cross_domain_transfer"
    device: str = "auto"
    quick_mode: bool = False


def _resolve_device(device: str) -> str:
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def _run_target_arm(
    algorithm: str,
    task: str,
    epochs: int,
    lr: float,
    seed: int,
    config: TransferConfig,
) -> tuple[dict, System | None]:
    """Train one rule on one task and report its final metrics."""
    built: list[System] = []

    def factory(input_dim: int, output_dim: int) -> System:
        system = rule_system(
            algorithm,
            input_dim,
            output_dim,
            lr=lr,
            device=config.device,
        )
        built.append(system)
        return system

    start_time = time.time()
    history = train_task(
        factory,
        task,
        epochs,
        batch_size=config.batch_size,
        device=config.device,
        quick_mode=config.quick_mode,
        seed=seed,
    )
    elapsed = time.time() - start_time
    final = final_metrics(history)
    return (
        {
            "accuracy": final.get("val_acc", 0.0),
            "loss": final.get("val_loss", float("inf")),
            "time": elapsed,
            "params": param_count(built[0]) if built else 0,
            "success": bool(history),
        },
        built[0] if built else None,
    )


def _run_pretraining(
    algorithm: str,
    source_task: str,
    seed: int,
    config: TransferConfig,
) -> dict:
    """Phase 1: train on the source task, as a transferability baseline."""
    result, _ = _run_target_arm(
        algorithm,
        source_task,
        config.pretrain_epochs,
        config.learning_rate,
        seed,
        config,
    )
    return {
        "algorithm": algorithm,
        "source_task": source_task,
        "seed": seed,
        "pretrain_accuracy": result["accuracy"],
        "pretrain_loss": result["loss"],
        "pretrain_time": result["time"],
        "pretrain_params": result["params"],
        "success": result["success"],
    }


def _run_finetuning(
    algorithm: str,
    target_domain: str,
    target_task: str,
    seed: int,
    config: TransferConfig,
) -> dict:
    """Phase 2: train on the target task.

    ``weights_transferred`` is False on purpose and recorded on purpose: the
    removed trainer could not carry weights across domains of different input
    geometry, and the legacy code created a fresh trainer here while calling
    the phase "finetuning". The record says which it is.
    """
    result, _ = _run_target_arm(
        algorithm,
        target_task,
        config.finetune_epochs,
        config.finetune_lr,
        seed,
        config,
    )
    return {
        "algorithm": algorithm,
        "target_domain": target_domain,
        "target_task": target_task,
        "seed": seed,
        "finetune_accuracy": result["accuracy"],
        "finetune_loss": result["loss"],
        "finetune_time": result["time"],
        "finetune_params": result["params"],
        "weights_transferred": False,
        "success": result["success"],
    }


def _run_scratch_baseline(
    algorithm: str,
    target_domain: str,
    target_task: str,
    seed: int,
    config: TransferConfig,
) -> dict:
    """The from-scratch control for a target arm, at the source learning rate."""
    result, _ = _run_target_arm(
        algorithm,
        target_task,
        config.finetune_epochs,
        config.learning_rate,
        seed,
        config,
    )
    return {
        "algorithm": algorithm,
        "target_domain": target_domain,
        "target_task": target_task,
        "seed": seed,
        "scratch_accuracy": result["accuracy"],
        "scratch_loss": result["loss"],
        "scratch_time": result["time"],
        "scratch_params": result["params"],
        "success": result["success"],
    }


def run_transfer_experiment(config: TransferConfig) -> list[dict]:  # ruff: ignore[complex-structure]
    """Run cross-domain transfer experiments."""
    device = _resolve_device(config.device)
    config = dataclasses.replace(config, device=device)

    results = []

    total_pretrain = len(config.source_tasks) * len(config.algorithms) * config.seeds
    pretrain_count = 0

    # Phase 1: Pretraining
    logger.info(
        "Phase 1: Pretraining on source domain (%d experiments)", total_pretrain
    )
    for source_task in config.source_tasks:
        for algorithm in config.algorithms:
            for seed in range(config.seeds):
                pretrain_count += 1
                logger.info(
                    "[Pretrain %d/%d] %s on %s (seed=%d)",
                    pretrain_count,
                    total_pretrain,
                    algorithm,
                    source_task,
                    seed,
                )

                result = _run_pretraining(algorithm, source_task, seed, config)
                results.append({**result, "phase": "pretrain"})

    # Phase 2: Finetuning + Scratch baselines
    total_finetune = (
        len(config.source_tasks)
        * len(config.algorithms)
        * sum(len(tasks) for tasks in config.target_tasks.values())
        * config.seeds
    )
    total_scratch = (  # ruff: ignore[unused-variable]
        len(config.algorithms)
        * sum(len(tasks) for tasks in config.target_tasks.values())
        * config.seeds
    )

    logger.info("Phase 2: Finetuning (%d experiments)", total_finetune)
    finetune_count = 0

    for source_task in config.source_tasks:  # ruff: ignore[too-many-nested-blocks]
        for algorithm in config.algorithms:
            for target_domain, target_tasks in config.target_tasks.items():
                for target_task in target_tasks:
                    for seed in range(config.seeds):
                        finetune_count += 1
                        logger.info(
                            "[Finetune %d/%d] %s: %s→%s on %s (seed=%d)",
                            finetune_count,
                            total_finetune,
                            algorithm,
                            source_task,
                            target_domain,
                            target_task,
                            seed,
                        )

                        ft_result = _run_finetuning(
                            algorithm, target_domain, target_task, seed, config
                        )
                        results.append({
                            **ft_result,
                            "phase": "finetune",
                            "source_task": source_task,
                        })

                        # Scratch baseline (only once per algorithm/target/seed)
                        if source_task == config.source_tasks[0]:
                            scratch_result = _run_scratch_baseline(
                                algorithm, target_domain, target_task, seed, config
                            )
                            results.append({**scratch_result, "phase": "scratch"})

    return results


def _analyze_transfer_efficiency(results: list[dict]) -> dict:  # ruff: ignore[too-many-locals]
    """Analyze transfer efficiency: finetune vs scratch."""
    import pandas as pd

    df = pd.DataFrame(results)
    if df.empty:
        return {}

    df = df[df["success"]].copy()
    analysis = {}

    for target_domain in df["target_domain"].unique():
        if pd.isna(target_domain):
            continue
        domain_df = df[df["target_domain"] == target_domain]
        domain_analysis = {}

        for target_task in domain_df["target_task"].unique():
            if pd.isna(target_task):
                continue
            task_df = domain_df[domain_df["target_task"] == target_task]
            task_analysis = {}

            for algorithm in task_df["algorithm"].unique():
                if pd.isna(algorithm):
                    continue
                algo_df = task_df[task_df["algorithm"] == algorithm]

                finetune_df = algo_df[algo_df["phase"] == "finetune"]
                scratch_df = algo_df[algo_df["phase"] == "scratch"]

                if finetune_df.empty or scratch_df.empty:
                    continue

                ft_acc = finetune_df["finetune_accuracy"].mean()
                scratch_acc = scratch_df["scratch_accuracy"].mean()

                # Transfer benefit
                benefit_pp = (ft_acc - scratch_acc) * 100
                relative_improvement = benefit_pp / (scratch_acc * 100 + 1e-6) * 100

                # Statistical test
                ft_accs = finetune_df["finetune_accuracy"].values
                scratch_accs = scratch_df["scratch_accuracy"].values
                if len(ft_accs) >= 2 and len(scratch_accs) >= 2:
                    p_val = permutation_test_p(
                        ft_accs, scratch_accs, n_permutations=500
                    )
                    d = cohens_d(ft_accs, scratch_accs)
                else:
                    p_val = 1.0
                    d = 0.0

                task_analysis[algorithm] = {
                    "finetune_accuracy": float(ft_acc),
                    "scratch_accuracy": float(scratch_acc),
                    "transfer_benefit_pp": float(benefit_pp),
                    "relative_improvement_pct": float(relative_improvement),
                    "p_value": float(p_val),
                    "cohens_d": float(d),
                    "significant": p_val < 0.05,
                }

            domain_analysis[target_task] = task_analysis

        analysis[target_domain] = domain_analysis

    return analysis


def _compare_local_vs_global(results: list[dict]) -> dict:  # ruff: ignore[complex-structure]
    """Compare local learning (EP, FA, PC, Hebbian) vs global (backprop) transfer."""
    import pandas as pd

    df = pd.DataFrame(results)
    if df.empty:
        return {}

    df = df[df["success"]].copy()
    comparison = {}

    local_algos = ["ep", "fa", "pc", "hebbian"]
    global_algo = "backprop"

    for target_domain in df["target_domain"].unique():
        if pd.isna(target_domain):
            continue
        domain_df = df[df["target_domain"] == target_domain]

        for target_task in domain_df["target_task"].unique():
            if pd.isna(target_task):
                continue
            task_df = domain_df[domain_df["target_task"] == target_task]

            local_benefits = []
            for algo in local_algos:
                if algo in task_df["algorithm"].values:
                    algo_df = task_df[task_df["algorithm"] == algo]
                    ft_df = algo_df[algo_df["phase"] == "finetune"]
                    scratch_df = algo_df[algo_df["phase"] == "scratch"]
                    if not ft_df.empty and not scratch_df.empty:
                        benefit = (
                            ft_df["finetune_accuracy"].mean()
                            - scratch_df["scratch_accuracy"].mean()
                        ) * 100
                        local_benefits.append(benefit)

            global_benefit = 0
            if global_algo in task_df["algorithm"].values:
                algo_df = task_df[task_df["algorithm"] == global_algo]
                ft_df = algo_df[algo_df["phase"] == "finetune"]
                scratch_df = algo_df[algo_df["phase"] == "scratch"]
                if not ft_df.empty and not scratch_df.empty:
                    global_benefit = (
                        ft_df["finetune_accuracy"].mean()
                        - scratch_df["scratch_accuracy"].mean()
                    ) * 100

            if local_benefits:
                comparison[f"{target_domain}/{target_task}"] = {
                    "local_mean_benefit_pp": float(np.mean(local_benefits)),
                    "local_std_benefit_pp": float(np.std(local_benefits)),
                    "global_benefit_pp": float(global_benefit),
                    "local_better": np.mean(local_benefits) > global_benefit,
                }

    return comparison


def _save_results(results: list[dict], output_dir: str) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with Path(output_path / "raw_results.jsonl").open("w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, default=str) + "\n")

    import pandas as pd

    df = pd.DataFrame(results)
    df.to_parquet(output_path / "results.parquet", index=False)

    logger.info("Saved results to %s", output_path)


def _generate_report(
    transfer_analysis: dict,
    local_vs_global: dict,
    output_dir: str,
) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with Path(output_path / "transfer_report.md").open("w", encoding="utf-8") as f:
        f.write("# Cross-Domain Transfer Report\n\n")

        f.write("## Transfer Efficiency (Finetune vs Scratch)\n\n")
        for domain, domain_analysis in transfer_analysis.items():
            f.write(f"### {domain}\n\n")
            for task, task_analysis in domain_analysis.items():
                f.write(f"#### {task}\n\n")
                f.write(
                    "| Algorithm | Finetune Acc | Scratch Acc | Benefit (pp) | Rel. Imp. (%) | p-value | d |\n"
                )
                f.write(
                    "|-----------|--------------|-------------|--------------|---------------|---------|---|\n"
                )
                for algo, stats in sorted(
                    task_analysis.items(),
                    key=lambda x: -x[1].get("transfer_benefit_pp", 0),
                ):
                    f.write(
                        f"| {algo} | {stats.get('finetune_accuracy', 0):.4f} | "
                        f"{stats.get('scratch_accuracy', 0):.4f} | "
                        f"{stats.get('transfer_benefit_pp', 0):+.2f} | "
                        f"{stats.get('relative_improvement_pct', 0):+.1f} | "
                        f"{stats.get('p_value', 1):.4f} | "
                        f"{stats.get('cohens_d', 0):.2f} |\n"
                    )
                f.write("\n")

        f.write("## Local vs Global Learning Transfer\n\n")
        f.write(
            "| Target | Local Mean Benefit (pp) | Global Benefit (pp) | Local Better? |\n"
        )
        f.write(
            "|--------|------------------------|---------------------|---------------|\n"
        )
        for target, stats in local_vs_global.items():
            f.write(
                f"| {target} | {stats.get('local_mean_benefit_pp', 0):+.2f} ± {stats.get('local_std_benefit_pp', 0):.2f} | "
                f"{stats.get('global_benefit_pp', 0):+.2f} | "
                f"{'✓' if stats.get('local_better', False) else '✗'} |\n"
            )
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Cross-Domain Transfer Experiment")
    parser.add_argument("--source", default="vision", help="Source domain")
    parser.add_argument(
        "--targets", default="tabular,vision", help="Target domains"
    )
    parser.add_argument("--source-tasks", default="cifar10", help="Source tasks")
    parser.add_argument(
        "--algorithms", default="ep,fa,pc,hebbian,backprop", help="Algorithms"
    )
    parser.add_argument(
        "--pretrain-epochs", type=int, default=20, help="Pretrain epochs"
    )
    parser.add_argument(
        "--finetune-epochs", type=int, default=10, help="Finetune epochs"
    )
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Pretrain learning rate")
    parser.add_argument(
        "--finetune-lr", type=float, default=1e-4, help="Finetune learning rate"
    )
    parser.add_argument("--seeds", type=int, default=3, help="Seeds per config")
    parser.add_argument(
        "--output-dir", default="results/cross_domain_transfer", help="Output directory"
    )
    parser.add_argument("--device", default="auto", help="Device (auto, cuda, cpu)")
    parser.add_argument("--quick", action="store_true", help="Quick mode")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    config = TransferConfig(
        source_domains=[args.source],
        target_domains=args.targets.split(","),
        source_tasks=args.source_tasks.split(","),
        algorithms=args.algorithms.split(","),
        pretrain_epochs=args.pretrain_epochs if not args.quick else 3,
        finetune_epochs=args.finetune_epochs if not args.quick else 2,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        finetune_lr=args.finetune_lr,
        seeds=args.seeds,
        output_dir=args.output_dir,
        device=args.device,
        quick_mode=args.quick,
    )

    logger.info("Starting Cross-Domain Transfer Experiment")

    # Run experiments
    results = run_transfer_experiment(config)

    # Save results
    _save_results(results, config.output_dir)

    # Analyze transfer efficiency
    transfer_analysis = _analyze_transfer_efficiency(results)
    with Path(Path(config.output_dir) / "transfer_analysis.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(transfer_analysis, f, indent=2, default=str)

    # Compare local vs global
    local_vs_global = _compare_local_vs_global(results)
    with Path(Path(config.output_dir) / "local_vs_global.json").open(
        "w", encoding="utf-8"
    ) as f:
        json.dump(local_vs_global, f, indent=2, default=str)

    # Generate report
    _generate_report(transfer_analysis, local_vs_global, config.output_dir)

    logger.info("Cross-Domain Transfer complete. Results in %s", config.output_dir)


if __name__ == "__main__":
    main()
