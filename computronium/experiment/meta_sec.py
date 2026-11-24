"""Meta-SEC Engine: Bayesian optimization of SEC hyperparameters from cells.jsonl.

Reads experimental history and optimizes:
- LADDER_FACTORS: 3-5 points, log-spaced
- CLAIM_SEEDS: 3, 5, 7, 10
- MIN_EFFECT_SIZE: 0.5-1.2 per family
- Fidelity schedule: L0 only, L0→L1, L0→L2
- semaphore_limit: 1, 2, 4, 8

Objective: maximize claims_per_gpu_hour
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    import optuna
except ImportError:
    optuna = None

from computronium.experiment.sec_all_axes import (
    MIN_EFFECT_SIZE_BY_FAMILY,
)

__all__ = [
    "MetaSECConfig",
    "MetaSECObjective",
    "analyze_cells_jsonl",
    "run_meta_sec",
]


@dataclass(frozen=True, slots=True)
class MetaSECConfig:
    """Configuration for meta-SEC optimization."""

    cells_path: Path = Path("results/sec/cells.jsonl")
    n_trials: int = 50
    timeout_s: float = 3600.0
    study_name: str = "meta_sec"
    storage: str | None = None  # e.g., "sqlite:///meta_sec.db"
    seed: int = 42


def _parse_cells(cells_path: Path) -> list[dict[str, Any]]:
    """Parse cells.jsonl into a list of normalized records."""
    parsed = []
    with cells_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            screen = c.get("screen", {})
            record = c.get("record")
            parsed.append({
                "axis": _extract_axis(screen.get("primitive", "")),
                "primitive": _extract_primitive(screen.get("primitive", "")),
                "status": screen.get("status", "unknown"),
                "reason": screen.get("reason", ""),
                "walltime_s": record.get("walltime_s", 0) if record else 0,
                "val_acc": record.get("val_acc", 0) if record else 0,
                "task_id": screen.get("box", {}).get("task_id", "unknown"),
            })
    return parsed


def _compute_stats(parsed: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute statistics from parsed cell records."""
    total = len(parsed)
    measured = sum(1 for c in parsed if c.get("status") == "MEASURED")
    refused = sum(1 for c in parsed if c.get("status") in {"REFUSED", "UNAVAILABLE"})
    defects = sum(1 for c in parsed if c.get("status") == "DEFECT")
    unavailable = sum(1 for c in parsed if c.get("status") == "UNAVAILABLE")

    walltimes = [c.get("walltime_s", 0) for c in parsed if c.get("walltime_s")]
    avg_walltime = float(np.mean(walltimes)) if walltimes else 0.0

    # Count by axis/primitive
    by_axis_primitive = {}
    for c in parsed:
        key = f"{c['axis']}.{c['primitive']}"
        by_axis_primitive[key] = by_axis_primitive.get(key, 0) + 1

    # Refusal reasons
    refusal_reasons = {}
    for c in parsed:
        if c.get("status") in {"REFUSED", "UNAVAILABLE", "UNIMPLEMENTED"}:
            reason = c.get("reason", "unknown")
            reason_short = reason[:100] if len(reason) > 100 else reason
            refusal_reasons[reason_short] = refusal_reasons.get(reason_short, 0) + 1

    # Claims (measured cells with val_acc > chance)
    claims = sum(
        1
        for c in parsed
        if c.get("status") == "MEASURED" and c.get("val_acc", 0) > 0.15
    )

    return {
        "total_cells": total,
        "measured": measured,
        "refused": refused,
        "defects": defects,
        "unavailable": unavailable,
        "claims": claims,
        "avg_walltime_s": avg_walltime,
        "by_axis_primitive": by_axis_primitive,
        "refusal_reasons": refusal_reasons,
    }


def analyze_cells_jsonl(cells_path: Path) -> dict[str, Any]:
    """Analyze cells.jsonl for meta-SEC insights.

    Returns:
        Dict with statistics: total cells, claims, refusals, avg walltime, etc.
    """
    if not cells_path.exists():
        return {"error": f"File not found: {cells_path}"}

    parsed = _parse_cells(cells_path)
    if not parsed:
        return {"error": "No cells found"}

    return _compute_stats(parsed)


def _extract_axis(primitive_str: str) -> str:
    """Extract axis from primitive string like 'primitive.credit_assignment.gradient'."""
    parts = primitive_str.split(".")
    if len(parts) >= 2:
        axis_map = {
            "credit_assignment": "credit",
            "state_dynamics": "dynamics",
            "geometry": "geometry",
            "parameter_update": "update",
            "plasticity": "plasticity",
            "substrate": "substrate",
        }
        return axis_map.get(parts[1], parts[1])
    return "unknown"


def _extract_primitive(primitive_str: str) -> str:
    """Extract primitive name from 'primitive.credit_assignment.gradient'."""
    parts = primitive_str.split(".")
    return parts[-1] if parts else "unknown"


class MetaSECObjective:
    """Meta-objective: claims per GPU-hour."""

    def __init__(self, cells_path: Path):
        self.cells_path = cells_path
        self.baseline_stats = analyze_cells_jsonl(cells_path)

    def __call__(self, trial: Any) -> float:
        if optuna is None:
            raise RuntimeError("optuna not installed")

        # Sample hyperparameters
        n_ladder_points = trial.suggest_int("n_ladder_points", 3, 5)
        ladder_factors = self._sample_ladder_factors(trial, n_ladder_points)

        claim_seeds = trial.suggest_categorical("claim_seeds", [3, 5, 7, 10])

        min_effect_size = {}
        for family in MIN_EFFECT_SIZE_BY_FAMILY:
            base = MIN_EFFECT_SIZE_BY_FAMILY[family]
            min_effect_size[family] = trial.suggest_float(
                f"min_d_{family}", base * 0.5, base * 1.5
            )

        fidelity_schedule = trial.suggest_categorical(
            "fidelity_schedule", ["L0", "L0_L1", "L0_L2"]
        )

        semaphore = trial.suggest_categorical("semaphore", [1, 2, 4, 8])

        # Simulate SEC run with these params (proxy objective)
        score = self._simulate_sec_run(
            ladder_factors=ladder_factors,
            claim_seeds=claim_seeds,
            min_effect_size=min_effect_size,
            fidelity_schedule=fidelity_schedule,
            semaphore=semaphore,
        )

        return score

    def _sample_ladder_factors(self, trial: Any, n_points: int) -> list[float]:
        """Sample log-spaced ladder factors."""
        log_min = trial.suggest_float("ladder_log_min", -3.0, -1.0)
        log_max = trial.suggest_float("ladder_log_max", 0.0, 2.0)
        return [
            10 ** (log_min + i * (log_max - log_min) / (n_points - 1))
            for i in range(n_points)
        ]

    def _simulate_sec_run(
        self,
        ladder_factors: list[float],
        claim_seeds: int,
        min_effect_size: dict[str, float],
        fidelity_schedule: str,
        semaphore: int,
    ) -> float:
        """Proxy simulation of SEC run cost and yield.

        Uses baseline stats to estimate claims per GPU-hour.
        """
        baseline = self.baseline_stats
        if "error" in baseline:
            return 0.0

        # Estimate cost
        n_primitives = len(baseline.get("by_axis_primitive", {}))
        n_tasks = 3  # MNIST, iris, cora (representative)

        # Ladder cost: n_primitives * n_tasks * n_ladder_points * 1 seed
        ladder_cells = n_primitives * n_tasks * len(ladder_factors)

        # Rung 2 cost: viable_primitives * n_tasks * claim_seeds * 2 arms
        viable_rate = baseline.get("measured", 1) / max(
            baseline.get("total_cells", 1), 1
        )
        rung2_cells = int(n_primitives * viable_rate * n_tasks * claim_seeds * 2)

        # Fidelity multiplier
        fidelity_mult = {"L0": 1.0, "L0_L1": 2.5, "L0_L2": 4.0}[fidelity_schedule]

        total_cell_equivalents = (ladder_cells + rung2_cells) * fidelity_mult

        # Parallelization factor
        parallel_factor = min(semaphore, 8)

        # Estimated GPU-hours (rough proxy)
        avg_walltime = baseline.get("avg_walltime_s", 60)
        gpu_hours = total_cell_equivalents * avg_walltime / 3600 / parallel_factor

        # Estimated claims (viable primitives that pass effect size)
        # Roughly: viable_rate * effect_size_pass_rate
        effect_pass_rate = 0.3  # Rough estimate
        estimated_claims = n_primitives * viable_rate * effect_pass_rate

        # Objective: claims per GPU-hour
        if gpu_hours > 0:
            return estimated_claims / gpu_hours
        return 0.0


def run_meta_sec(config: MetaSECConfig | None = None) -> dict[str, Any]:
    """Run meta-SEC Bayesian optimization.

    Args:
        config: MetaSECConfig, or None for defaults.

    Returns:
        Dict with best params, best value, and study info.
    """
    if optuna is None:
        raise RuntimeError("optuna required: pip install optuna")

    config = config or MetaSECConfig()

    study = optuna.create_study(
        study_name=config.study_name,
        storage=config.storage,
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=config.seed),
        load_if_exists=True,
    )

    objective = MetaSECObjective(config.cells_path)

    study.optimize(objective, n_trials=config.n_trials, timeout=config.timeout_s)

    return {
        "best_params": study.best_params,
        "best_value": study.best_value,
        "n_trials": len(study.trials),
        "baseline_stats": objective.baseline_stats,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Meta-SEC optimization")
    parser.add_argument("--n-trials", type=int, default=50)
    parser.add_argument("--timeout", type=float, default=3600)
    parser.add_argument("--cells", type=str, default="results/sec/cells.jsonl")
    parser.add_argument("--storage", type=str, default=None)

    args = parser.parse_args()

    config = MetaSECConfig(
        cells_path=Path(args.cells),
        n_trials=args.n_trials,
        timeout_s=args.timeout,
        storage=args.storage,
    )

    result = run_meta_sec(config)
    print(json.dumps(result, indent=2))
