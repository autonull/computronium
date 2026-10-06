#!/usr/bin/env python
"""Microbenchmarks for core operations.

Run with: uv run python scripts/benchmarks/settle_benchmark.py
Run GPU benchmarks: uv run python scripts/benchmarks/settle_benchmark.py --device cuda
"""

from __future__ import annotations

import argparse
import statistics
import time
from dataclasses import dataclass

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
class BenchmarkResult:
    name: str
    device: str
    mean_ms: float
    stdev_ms: float
    num_runs: int
    peak_memory_mb: float | None = None


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


def _measure_memory(device: str) -> float | None:
    """Measure peak GPU memory in MB."""
    if device == "cuda" and torch.cuda.is_available():
        torch.cuda.synchronize()
        return torch.cuda.max_memory_allocated() / (1024**2)
    return None


def _reset_memory(device: str) -> None:
    """Reset peak memory stats."""
    if device == "cuda" and torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()


def benchmark_settle(
    dynamics_name: str,
    dynamics_cls,
    config,
    geometry,
    substrate,
    x,
    num_runs: int = 5,
    device: str = "cpu",
) -> BenchmarkResult:
    """Benchmark a dynamics settle method."""
    # Warmup
    for _ in range(2):
        dynamics = dynamics_cls(config)
        state = SystemState(x=x, y=None)
        dynamics.settle(state, geometry, substrate)

    if device == "cuda":
        torch.cuda.synchronize()
        _reset_memory(device)

    # Benchmark
    times = []
    peak_mem = 0.0
    for _ in range(num_runs):
        dynamics = dynamics_cls(config)
        state = SystemState(x=x, y=None)

        start = time.perf_counter()
        dynamics.settle(state, geometry, substrate)
        if device == "cuda":
            torch.cuda.synchronize()
        end = time.perf_counter()

        times.append(end - start)
        mem = _measure_memory(device)
        if mem is not None:
            peak_mem = max(peak_mem, mem)

    mean_time = statistics.mean(times)
    stdev_time = statistics.stdev(times) if len(times) > 1 else 0
    peak_mb = peak_mem if peak_mem > 0 else None

    mem_str = f", peak_mem={peak_mb:.1f}MB" if peak_mb else ""
    print(
        f"{dynamics_name}: {mean_time * 1000:.2f}ms ± {stdev_time * 1000:.2f}ms (mean ± std over {num_runs} runs{mem_str})"
    )
    return BenchmarkResult(
        name=dynamics_name,
        device=device,
        mean_ms=mean_time * 1000,
        stdev_ms=stdev_time * 1000,
        num_runs=num_runs,
        peak_memory_mb=peak_mb,
    )


def run_benchmarks(device: str = "cpu") -> list[BenchmarkResult]:
    """Run all benchmarks on specified device."""
    print("=" * 60)
    print(f"Settle Loop Microbenchmarks (device={device})")
    print("=" * 60)

    if device == "cuda" and not torch.cuda.is_available():
        print("CUDA not available, skipping GPU benchmarks")
        return []

    results = []

    # Test configurations
    configs = [
        ("Small (hidden=64, layers=2, batch=16)", 64, 2, 16),
        ("Medium (hidden=128, layers=3, batch=32)", 128, 3, 32),
        ("Large (hidden=256, layers=4, batch=64)", 256, 4, 64),
    ]

    for name, hidden_dim, num_layers, batch in configs:
        print(f"\n{name}:")
        geometry, substrate, x = _make_test_system(
            hidden_dim, num_layers, batch, device
        )

        # EnergyMinimizationDynamics
        config_em = StateDynamicsConfig.energy_minimization(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
        )
        results.append(
            benchmark_settle(
                "  EnergyMinimization",
                EnergyMinimizationDynamics,
                config_em,
                geometry,
                substrate,
                x,
                device=device,
            )
        )

        # PredictiveSettlingDynamics
        config_ps = StateDynamicsConfig.predictive_settling(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
        )
        results.append(
            benchmark_settle(
                "  PredictiveSettling",
                PredictiveSettlingDynamics,
                config_ps,
                geometry,
                substrate,
                x,
                device=device,
            )
        )

        # PCALMDynamics
        config_pcalm = StateDynamicsConfig.pc_alm(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
            rho=1.0,
        )
        results.append(
            benchmark_settle(
                "  PCALM",
                PCALMDynamics,
                config_pcalm,
                geometry,
                substrate,
                x,
                device=device,
            )
        )

    # Compiled path benchmark (PredictiveSettling)
    results.append(_benchmark_compiled_predictive_settling(device))

    return results


def _benchmark_compiled_predictive_settling(device: str) -> BenchmarkResult:
    """Benchmark compiled PredictiveSettling."""
    print("\n\nCompiled Path (PredictiveSettling):")
    geometry, substrate, x = _make_test_system(128, 3, 32, device)
    config_compiled = StateDynamicsConfig.predictive_settling(
        max_steps=30,
        step_size=0.1,
        beta=0.5,
        compiled=True,
    )

    # Warmup compilation
    dynamics = PredictiveSettlingDynamics(config_compiled)
    state = SystemState(x=x, y=None)
    dynamics.settle(state, geometry, substrate)

    if device == "cuda":
        torch.cuda.synchronize()
        _reset_memory(device)

    # Benchmark compiled
    times = []
    peak_mem = 0.0
    for _ in range(5):
        dynamics = PredictiveSettlingDynamics(config_compiled)
        state = SystemState(x=x, y=None)
        start = time.perf_counter()
        dynamics.settle(state, geometry, substrate)
        if device == "cuda":
            torch.cuda.synchronize()
        end = time.perf_counter()
        times.append(end - start)
        mem = _measure_memory(device)
        if mem is not None:
            peak_mem = max(peak_mem, mem)

    mean_time = statistics.mean(times)
    stdev_time = statistics.stdev(times)
    peak_mb = peak_mem if peak_mem > 0 else None
    mem_str = f", peak_mem={peak_mb:.1f}MB" if peak_mb else ""
    print(
        f"  PredictiveSettling (compiled): {mean_time * 1000:.2f}ms ± {stdev_time * 1000:.2f}ms{mem_str}"
    )
    return BenchmarkResult(
        name="  PredictiveSettling (compiled)",
        device=device,
        mean_ms=mean_time * 1000,
        stdev_ms=stdev_time * 1000,
        num_runs=5,
        peak_memory_mb=peak_mb,
    )


def print_summary(results: list[BenchmarkResult], device: str) -> None:
    """Print summary table."""
    print("\n" + "=" * 80)
    print(f"SUMMARY ({device.upper()})")
    print("=" * 80)
    print(f"{'Dynamics':<35} {'Mean (ms)':>10} {'Std (ms)':>10} {'Peak Mem (MB)':>15}")
    print("-" * 80)
    for r in results:
        mem_str = f"{r.peak_memory_mb:.1f}" if r.peak_memory_mb else "N/A"
        print(f"{r.name:<35} {r.mean_ms:>10.2f} {r.stdev_ms:>10.2f} {mem_str:>15}")


def main():
    parser = argparse.ArgumentParser(description="Settle loop microbenchmarks")
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="Device to run benchmarks on",
    )
    args = parser.parse_args()

    results = run_benchmarks(args.device)
    print_summary(results, args.device)


if __name__ == "__main__":
    main()
