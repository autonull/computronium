"""TODO92 §3.10: the last interaction — plasticity × task (retention).

Question: with every other axis fixed
(digital/feedforward/instantaneous/null-prior/gradient/euclidean), does
`fast_weights` plasticity reduce forgetting across SplitMNIST tasks relative to
`null`?

The CL runner's `fast_weights` arm also changes dynamics, credit and update, so
it is a four-axis contrast. This probe uses `create_plasticity_arm`, which
varies only the plasticity axis. Retention is read from the runner's own
metrics: `avg_forgetting` (primary, lower is better), `final_accuracies[0]` and
`backward_transfer` (secondary).

- ``--pilot``: one seed, one epoch per task, both arms. Prices the run and
  answers rung 1 (does each arm train?).
- full run: seeds 62-66, 5 epochs per task, prints per-arm mean/SD and the
  paired `null - fast` forgetting difference with a bootstrap CI.

Measured 2026-11-15 (seeds 62-66, 5 epochs per task, CPU, 10 runs, ~24 min):
null forgetting **0.0417 ± 0.0051**, `fast_weights` **0.0425 ± 0.0053**; paired
null − fast = **−0.0008**, 95% CI [−0.0021, +0.0006], p=0.37, dz=−0.42. The CI
lies inside the pre-registered ±0.01 margin: **no plasticity × task
interaction** at this coordinate, and `fast_weights` costs **8.9× walltime**
(255.5 s vs 28.6 s per run).

Walltime printed, never recorded as a claim.

Run: uv run python scripts/probes/t92_plasticity_task.py --pilot
     uv run python scripts/probes/t92_plasticity_task.py
"""

from __future__ import annotations

import argparse
import statistics
import time

from computronium.core.continual import CLConfig, run_continual_learning
from computronium.validation.preregistration import paired_comparison

__all__ = ["main"]

ARMS: dict[str, str] = {
    "null": "matched_null",
    "fast_weights": "matched_fast_weights",
}
SEEDS = (62, 63, 64, 65, 66)


def _run(arm: str, seed: int, epochs: int, device: str):
    config = CLConfig(epochs_per_task=epochs, seed=seed, device=device)
    return run_continual_learning(ARMS[arm], config, "task_incremental")


def _print(arm: str, seed: int, epochs: int, device: str) -> None:
    started = time.perf_counter()
    metrics = _run(arm, seed, epochs, device)
    print(
        f"{arm:13} seed={seed:2} epochs/task={epochs} "
        f"forgetting={metrics.avg_forgetting:.4f} "
        f"final0={metrics.final_accuracies[0]:.4f} "
        f"bwt={metrics.backward_transfer:+.4f} "
        f"({time.perf_counter() - started:.1f}s)",
        flush=True,
    )


def _pilot(seed: int, epochs: int, device: str) -> int:
    for arm in ARMS:
        _print(arm, seed, epochs, device)
    return 0


def _full(seeds: tuple[int, ...], epochs: int, device: str) -> int:
    forgetting: dict[str, list[float]] = {arm: [] for arm in ARMS}
    final0: dict[str, list[float]] = {arm: [] for arm in ARMS}
    bwt: dict[str, list[float]] = {arm: [] for arm in ARMS}
    for seed in seeds:
        for arm in ARMS:
            started = time.perf_counter()
            metrics = _run(arm, seed, epochs, device)
            forgetting[arm].append(metrics.avg_forgetting)
            final0[arm].append(metrics.final_accuracies[0])
            bwt[arm].append(metrics.backward_transfer)
            print(
                f"{arm:13} seed={seed:2} forgetting={metrics.avg_forgetting:.4f} "
                f"final0={metrics.final_accuracies[0]:.4f} "
                f"bwt={metrics.backward_transfer:+.4f} "
                f"({time.perf_counter() - started:.1f}s)",
                flush=True,
            )
    for arm in ARMS:
        values = forgetting[arm]
        print(
            f"{arm:13}: forgetting mean={statistics.mean(values):.4f} "
            f"sd={statistics.stdev(values):.4f} "
            f"final0 mean={statistics.mean(final0[arm]):.4f} "
            f"bwt mean={statistics.mean(bwt[arm]):+.4f}"
        )
    result = paired_comparison(forgetting["null"], forgetting["fast_weights"], seed=0)
    print(
        f"paired null - fast_weights forgetting: {result.mean_diff:+.4f} "
        f"95% CI [{result.ci_lower:+.4f}, {result.ci_upper:+.4f}] "
        f"p={result.p_value:.4f} dz={result.cohens_dz:.2f}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--seed", type=int, default=62)
    parser.add_argument("--epochs-per-task", type=int, default=5)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)
    if args.pilot:
        return _pilot(args.seed, args.epochs_per_task, args.device)
    return _full(SEEDS, args.epochs_per_task, args.device)


if __name__ == "__main__":
    raise SystemExit(main())
