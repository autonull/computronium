#!/usr/bin/env python
"""Canonical experiment runner — single time-boxed loop.

Replaces the tiered runner with one loop that runs until the deadline.
Nothing else stops it.

Usage:
    uv run scripts/run_experiment.py --hours N --device auto|cpu|cuda \
        --store results/exp.db [--axes ...] [--policy ...]

Architecture:
    deadline = Deadline.from_hours(hours)          # persisted, monotonic
    stream   = CellStream(spec, space, policy)     # unbounded, advancing
    sizer    = BatchSizer(deadline, timing)        # budget-sized n_propose
    while not deadline.soft_expired() and not shutdown_requested:
        k = sizer.n_propose()                      # from remaining time × median cell time
        if not sizer.can_start(k):                 # not enough time for a safe batch
            break
        batch = stream.next(k)                     # screened; mints fresh cells in exploit mode
        run_and_record(batch)                      # admission-gated, failure-isolated
    write_report()                                 # from the report reserve
"""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from computronium.experiment.execution.campaign import run_campaign
from computronium.experiment.execution.deadline import (
    Deadline,
)
from computronium.experiment.schema import RunSpec


@dataclass(frozen=True, slots=True)
class RunExperimentConfig:
    """Configuration for the canonical experiment runner."""

    hours: float
    device: str  # "cpu" | "cuda"
    store: str
    axes: dict[str, list[str]] | None = None
    policy: str = "round_robin_grid"
    seed: int = 42
    epochs: int = 10
    n_seeds: int = 3
    param_budget: int = 500_000
    max_params: int = 500_000
    fidelity: str = "L0"
    batch_limit: int = 0
    max_parallel: int = 1
    max_rounds: int | None = None
    min_rounds: int = 1
    num_workers: int = 0
    precision: str = "fp32"
    deterministic: bool = True
    checkpoint_every_n: int = 0
    objectives: tuple[str, ...] = ("validation_accuracy", "param_count", "walltime_total")
    profile: str = "production-map"


def _signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\nReceived signal {signum}, initiating graceful shutdown...")
    sys.exit(130)


def _resolve_device(device: str) -> str:
    """Resolve device string to actual device."""
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def _build_run_spec(config: RunExperimentConfig, resolved_device: str) -> RunSpec:
    """Build RunSpec from experiment config."""
    import json

    # Build overrides from config
    overrides = {
        "device": resolved_device,
        "epochs": config.epochs,
        "n_seeds": config.n_seeds,
        "param_budget": config.param_budget,
        "fidelity": config.fidelity,
        "batch_limit": config.batch_limit,
        "seed": config.seed,
        "policy": config.policy,
        "objectives": list(config.objectives),
        "num_workers": config.num_workers,
        "precision": config.precision,
        "deterministic": config.deterministic,
        "checkpoint_every_n": config.checkpoint_every_n,
        "max_rounds": config.max_rounds,
        "min_rounds": config.min_rounds,
    }

    # Add axes if specified (as axes dict with StructuralAxis enum keys)
    if config.axes:
        from computronium.experiment.schema.axis import StructuralAxis

        axes_dict = {}
        axis_mapping = {
            "substrates": StructuralAxis.SUBSTRATE,
            "geometries": StructuralAxis.GEOMETRY,
            "dynamics": StructuralAxis.DYNAMICS,
            "credits": StructuralAxis.CREDIT,
            "updates": StructuralAxis.UPDATE,
            "plasticities": StructuralAxis.PLASTICITY,
        }
        for axis_name, primitives in config.axes.items():
            if axis_name in axis_mapping:
                axes_dict[axis_mapping[axis_name]] = tuple(primitives)
        overrides["axes"] = axes_dict

    # Create mock args for _resolve_spec
    args = argparse.Namespace()
    args.profile = config.profile
    args.spec = None
    args.overrides = json.dumps(overrides)
    args.task = None
    args.dry_run = False
    args.device = resolved_device
    args.store = config.store
    args.run_id = None

    from computronium.experiment.surface.cli import _resolve_spec

    return _resolve_spec(args)


async def _run_single_experiment(config: RunExperimentConfig) -> int:
    """Run a single experiment with deadline enforcement."""
    from computronium.experiment.execution.deadline import Deadline

    resolved_device = _resolve_device(config.device)
    print(f"Resolved device: {resolved_device}")

    # Create hard deadline
    deadline = Deadline.from_hours(config.hours)
    print(f"Hard deadline: {deadline.remaining_soft_seconds() / 3600:.2f}h from now")

    # Build run spec
    spec = _build_run_spec(config, resolved_device)

    # Create deadline-aware campaign
    campaign_file = f"campaign_exp_{config.policy}_{config.hours}h.yaml"
    campaign_path = Path(campaign_file)

    # Generate campaign YAML
    _create_deadline_campaign_yaml(
        config, spec, deadline, campaign_path, resolved_device
    )
    print(f"Campaign YAML written to: {campaign_path}")

    # Run campaign
    print(f"Starting experiment at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    start_time = time.time()

    result = await run_campaign(
        campaign_path,
        parallel=config.max_parallel,
        device=resolved_device,
    )

    elapsed = time.time() - start_time
    print(f"\nExperiment completed in {elapsed:.1f}s ({elapsed / 3600:.2f}h)")

    # Print summary
    _print_summary(result, elapsed, config.hours)

    return 0


def _create_deadline_campaign_yaml(
    config: RunExperimentConfig,
    spec: RunSpec,
    deadline: Deadline,
    output_path: Path,
    device: str,
) -> None:
    """Generate campaign YAML using deadline (no prediction)."""
    import yaml

    from computronium.experiment.schema.axis import StructuralAxis

    store_path = config.store

    # Get selected primitives using StructuralAxis enum
    substrates = list(spec.selected_primitives(StructuralAxis.SUBSTRATE))
    geometries = list(spec.selected_primitives(StructuralAxis.GEOMETRY))
    dynamics = list(spec.selected_primitives(StructuralAxis.DYNAMICS))
    credits = list(spec.selected_primitives(StructuralAxis.CREDIT))
    updates = list(spec.selected_primitives(StructuralAxis.UPDATE))
    plasticities = list(spec.selected_primitives(StructuralAxis.PLASTICITY))

    data = {
        "meta": {
            "name": f"exp_{config.policy}_{config.hours}h",
            "description": f"Experiment: {config.policy}, {config.hours}h deadline, {device}",
            "time_budget_hours": config.hours,
            "device": device,
        },
        "compute": {
            "device": device,
            "max_parallel": config.max_parallel,
            "max_wall_hours": config.hours * 1.1,  # 10% buffer
        },
        "store": store_path,
        "search_space": {
            "base": {
                "hidden_dim": [64, 128, 256],
                "num_layers": [2, 3, 4],
                "lr": [1e-4, 1e-3, 1e-2, "log"],
                "batch_size": [128, 256],
            }
        },
        "constraints": ["estimate(config) <= 500000"],
        "protocols": {
            "default": "end2end",
            "overrides": {
                "fa_mlp": "layerwise",
                "three_factor_hebbian": "layerwise",
            },
        },
        "arms": {
            "adaptive": {
                "input_dim": 784,
                "num_classes": 10,
                "flatten": True,
                "max_params": config.max_params,
                "substrates": substrates,
                "geometries": geometries,
                "dynamics": dynamics,
                "credits": credits,
                "updates": updates,
                "plasticities": plasticities,
            }
        },
        "tasks": [
            {
                "name": "mnist",
                "epochs": config.epochs,
                "input_dim": 784,
                "num_classes": 10,
            }
        ],
        "hpo": {
            "sampler": "nsga2",
            "objectives": list(config.objectives),
            "n_trials": 100,
            "n_startup_trials": 10,
            "n_seeds": config.n_seeds,
        },
        "resources": {
            "max_wall_hours": config.hours * 1.1,
            "max_epoch_time_sec": 120,
            "early_stop_patience": 10,
        },
        "output": {
            "db": store_path,
            "artifacts_dir": f"artifacts/exp_{config.policy}_{config.hours}h",
            "log_level": "INFO",
            "emit_every": 5,
        },
        "reproducibility": {
            "seed": config.seed,
            "capture_env": True,
            "artifact_hash": True,
        },
        "runs": [
            {
                "name": "main",
                "profile": config.profile,
                "overrides": {
                    "substrates": substrates,
                    "geometries": geometries,
                    "dynamics": dynamics,
                    "credits": credits,
                    "updates": updates,
                    "plasticities": plasticities,
                    "tasks": ["mnist"],
                    "hpo": {"n_trials": 100, "n_seeds": config.n_seeds},
                    "epochs": config.epochs,
                    "budget_seconds": deadline.remaining_soft_seconds(),
                },
                "depends_on": [],
            }
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def _print_summary(result: dict[str, Any], elapsed: float, budget_hours: float) -> None:
    """Print experiment summary."""
    print("=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"Campaign: {result.get('campaign', 'unknown')}")
    print(f"Total runs: {result.get('total_runs', 0)}")
    print(f"Completed: {result.get('completed', 0)}")
    print(f"Failed: {result.get('failed', 0)}")
    print(f"Elapsed: {elapsed:.1f}s ({elapsed / 3600:.2f}h)")
    print(f"Budget: {budget_hours:.2f}h")
    print(f"Utilization: {elapsed / (budget_hours * 3600):.1%}")

    # Budget utilization check
    budget_s = budget_hours * 3600
    eps = max(0.02 * budget_s, 5.0)  # 2% or 5s, whichever is larger
    grace = 30.0

    if abs(elapsed - budget_s) <= eps:
        print(
            f"✅ Budget utilization: PASS (elapsed={elapsed:.1f}s, budget={budget_s:.1f}s, eps={eps:.1f}s)"
        )
    elif elapsed <= budget_s + grace:
        print(
            f"⚠️  Budget utilization: WITHIN GRACE (elapsed={elapsed:.1f}s, budget={budget_s:.1f}s, grace={grace:.1f}s)"
        )
    else:
        print(
            f"❌ Budget utilization: OVERSHOOT (elapsed={elapsed:.1f}s, budget={budget_s:.1f}s, grace={grace:.1f}s)"
        )

    # Check for records
    total_records = sum(
        r.get("completed", 0) for r in result.get("run_results", {}).values()
    )
    if total_records > 0:
        print(f"✅ Records collected: {total_records}")
    else:
        print("❌ No records collected!")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical experiment runner — single time-boxed loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run 1-hour experiment on GPU
  uv run scripts/run_experiment.py --hours 1 --device cuda --store results/exp_1h.db

  # Run 30-minute experiment on CPU with custom policy
  uv run scripts/run_experiment.py --hours 0.5 --device cpu --policy model_based --store results/exp_30m.db

  # Run with custom axes
  uv run scripts/run_experiment.py --hours 1 --device cuda --store results/exp.db \\
      --substrates digital,memristive --geometries feedforward,recurrent
        """,
    )

    parser.add_argument(
        "--hours",
        type=float,
        required=True,
        help="Time budget in hours (hard deadline enforcement)",
    )
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Device to run on (default: auto)",
    )
    parser.add_argument(
        "--store",
        type=str,
        default="results/experiment.db",
        help="DuckDB store path (default: results/experiment.db)",
    )
    parser.add_argument(
        "--policy",
        type=str,
        default="round_robin_grid",
        choices=[
            "round_robin_grid",
            "stratified_random",
            "uniform_random",
            "model_based",
            "evolution",
            "synthesis",
            "strategy_progression",
            "trainer_driven",
        ],
        help="Policy for cell selection (default: round_robin_grid)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=10,
        help="Epochs per cell (default: 10)",
    )
    parser.add_argument(
        "--n-seeds",
        type=int,
        default=3,
        help="Number of seeds per cell (default: 3)",
    )
    parser.add_argument(
        "--param-budget",
        type=int,
        default=500_000,
        help="Parameter budget per cell (default: 500000)",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=None,
        help="Maximum rounds (default: None = unlimited until deadline)",
    )
    parser.add_argument(
        "--substrates",
        type=str,
        help="Comma-separated list of substrates",
    )
    parser.add_argument(
        "--geometries",
        type=str,
        help="Comma-separated list of geometries",
    )
    parser.add_argument(
        "--dynamics",
        type=str,
        help="Comma-separated list of dynamics",
    )
    parser.add_argument(
        "--credits",
        type=str,
        help="Comma-separated list of credits",
    )
    parser.add_argument(
        "--updates",
        type=str,
        help="Comma-separated list of updates",
    )
    parser.add_argument(
        "--plasticities",
        type=str,
        help="Comma-separated list of plasticities",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="production-map",
        help="Profile name (default: production-map)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate campaign YAML and exit",
    )

    args = parser.parse_args()

    # Set up signal handlers
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Build axes dict from CLI args
    axes = {}
    for axis_name in [
        "substrates",
        "geometries",
        "dynamics",
        "credits",
        "updates",
        "plasticities",
    ]:
        value = getattr(args, axis_name)
        if value:
            axes[axis_name] = [v.strip() for v in value.split(",")]

    config = RunExperimentConfig(
        hours=args.hours,
        device=args.device,
        store=args.store,
        axes=axes if axes else None,
        policy=args.policy,
        seed=args.seed,
        epochs=args.epochs,
        n_seeds=args.n_seeds,
        param_budget=args.param_budget,
        max_rounds=args.max_rounds,
        profile=args.profile,
    )

    # Ensure results directory exists
    Path("results").mkdir(exist_ok=True)
    Path("artifacts").mkdir(exist_ok=True)

    if args.dry_run:
        print("DRY RUN - would execute experiment with config:")
        print(f"  Hours: {config.hours}")
        print(f"  Device: {config.device}")
        print(f"  Store: {config.store}")
        print(f"  Policy: {config.policy}")
        print(f"  Axes: {config.axes}")
        return 0

    return asyncio.run(_run_single_experiment(config))


if __name__ == "__main__":
    sys.exit(main())
