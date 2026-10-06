#!/usr/bin/env python
"""Kernel cache benchmark: measure cold vs warm torch.compile/Triton cache impact.

Run with: uv run python scripts/benchmarks/kernel_cache_benchmark.py
"""

from __future__ import annotations

import argparse
import shutil
import statistics
import time
from dataclasses import dataclass
from pathlib import Path

import torch

from computronium.ontology.dynamics import (
    EnergyMinimizationDynamics,
    PCALMDynamics,
    PredictiveSettlingDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.system import SystemState


@dataclass
class CacheBenchmarkResult:
    name: str
    cold_mean_ms: float
    cold_stdev_ms: float
    warm_mean_ms: float
    warm_stdev_ms: float
    speedup: float
    cache_dir_size_mb: float


def _make_test_system(
    hidden_dim: int = 128, num_layers: int = 3, batch: int = 32, device: str = "cpu"
):
    """Create a test system for benchmarking."""
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=hidden_dim,
            output_dim=hidden_dim,
            hidden_dims=(hidden_dim,) * num_layers,
        )
    ).to(device)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=device))
    x = torch.randn(batch, hidden_dim, device=device)
    return geometry, substrate, x


def _get_cache_size_mb() -> float:
    """Get the size of torch inductor cache in MB."""
    from torch._inductor import codecache

    cache_dir = Path(codecache.cache_dir())
    if not cache_dir.exists():
        return 0.0
    total = sum(f.stat().st_size for f in cache_dir.rglob("*") if f.is_file())
    return total / (1024 * 1024)


def _clear_cache() -> None:
    """Clear the torch inductor cache (but preserve precompiled headers)."""
    from torch._inductor import codecache

    cache_dir = Path(codecache.cache_dir())
    if cache_dir.exists():
        # Remove only the subdirectories, not precompiled_headers
        for item in cache_dir.iterdir():
            if item.name != "precompiled_headers":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()


def benchmark_dynamics(
    dynamics_name: str,
    dynamics_cls,
    config,
    geometry,
    substrate,
    x,
    num_runs: int = 5,
    device: str = "cpu",
) -> CacheBenchmarkResult:
    """Benchmark a dynamics settle method with cold and warm cache."""
    # Warmup compilation (not counted in cold timing)
    for _ in range(2):
        dynamics = dynamics_cls(config)
        state = SystemState(x=x, y=None)
        dynamics.settle(state, geometry, substrate)
    if device == "cuda":
        torch.cuda.synchronize()

    # Cold run: clear cache first
    _clear_cache()
    cold_times = []
    for _ in range(num_runs):
        dynamics = dynamics_cls(config)
        state = SystemState(x=x, y=None)
        start = time.perf_counter()
        dynamics.settle(state, geometry, substrate)
        if device == "cuda":
            torch.cuda.synchronize()
        end = time.perf_counter()
        cold_times.append(end - start)

    cold_mean = statistics.mean(cold_times) * 1000
    cold_stdev = statistics.stdev(cold_times) * 1000 if len(cold_times) > 1 else 0

    # Warm runs: cache is now populated
    warm_times = []
    for _ in range(num_runs):
        dynamics = dynamics_cls(config)
        state = SystemState(x=x, y=None)
        start = time.perf_counter()
        dynamics.settle(state, geometry, substrate)
        if device == "cuda":
            torch.cuda.synchronize()
        end = time.perf_counter()
        warm_times.append(end - start)

    warm_mean = statistics.mean(warm_times) * 1000
    warm_stdev = statistics.stdev(warm_times) * 1000 if len(warm_times) > 1 else 0

    speedup = cold_mean / warm_mean if warm_mean > 0 else 0
    cache_size = _get_cache_size_mb()

    print(
        f"  {dynamics_name}: cold={cold_mean:.2f}±{cold_stdev:.2f}ms, "
        f"warm={warm_mean:.2f}±{warm_stdev:.2f}ms, speedup={speedup:.2f}x, "
        f"cache={cache_size:.1f}MB"
    )
    return CacheBenchmarkResult(
        name=dynamics_name,
        cold_mean_ms=cold_mean,
        cold_stdev_ms=cold_stdev,
        warm_mean_ms=warm_mean,
        warm_stdev_ms=warm_stdev,
        speedup=speedup,
        cache_dir_size_mb=cache_size,
    )


def run_cache_benchmarks(device: str = "cpu") -> list[CacheBenchmarkResult]:
    """Run cache benchmarks on specified device."""
    print("=" * 70)
    print(f"Kernel Cache Benchmarks (device={device})")
    print("=" * 70)

    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, skipping GPU benchmarks")
        return []

    results = []

    # Test configurations
    configs = [
        ("Medium (hidden=128, layers=3, batch=32)", 128, 3, 32),
    ]

    for name, hidden_dim, num_layers, batch in configs:
        print(f"\n{name}:")
        geometry, substrate, x = _make_test_system(
            hidden_dim, num_layers, batch, device
        )

        # EnergyMinimizationDynamics (compiled)
        config_em = StateDynamicsConfig.energy_minimization(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
            compiled=True,
        )
        results.append(
            benchmark_dynamics(
                "  EnergyMinimization (compiled)",
                EnergyMinimizationDynamics,
                config_em,
                geometry,
                substrate,
                x,
                device=device,
            )
        )

        # PredictiveSettlingDynamics (compiled)
        config_ps = StateDynamicsConfig.predictive_settling(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
            compiled=True,
        )
        results.append(
            benchmark_dynamics(
                "  PredictiveSettling (compiled)",
                PredictiveSettlingDynamics,
                config_ps,
                geometry,
                substrate,
                x,
                device=device,
            )
        )

        # PCALMDynamics (compiled)
        config_pcalm = StateDynamicsConfig.pc_alm(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
            rho=1.0,
            compiled=True,
        )
        results.append(
            benchmark_dynamics(
                "  PCALM (compiled)",
                PCALMDynamics,
                config_pcalm,
                geometry,
                substrate,
                x,
                device=device,
            )
        )

    return results


def print_summary(results: list[CacheBenchmarkResult], device: str) -> None:
    """Print summary table."""
    print("\n" + "=" * 90)
    print(f"CACHE BENCHMARK SUMMARY ({device.upper()})")
    print("=" * 90)
    print(
        f"{'Dynamics':<35} {'Cold (ms)':>12} {'Warm (ms)':>12} {'Speedup':>10} {'Cache (MB)':>12}"
    )
    print("-" * 90)
    for r in results:
        print(
            f"{r.name:<35} {r.cold_mean_ms:>12.2f} {r.warm_mean_ms:>12.2f} "
            f"{r.speedup:>10.2f}x {r.cache_dir_size_mb:>12.1f}"
        )


def main():
    parser = argparse.ArgumentParser(description="Kernel cache benchmarks")
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="Device to run benchmarks on",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of runs per benchmark",
    )
    args = parser.parse_args()

    results = run_cache_benchmarks(args.device)
    print_summary(results, args.device)


if __name__ == "__main__":
    main()
