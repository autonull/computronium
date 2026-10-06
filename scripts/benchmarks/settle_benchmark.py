#!/usr/bin/env python
"""Microbenchmarks for core operations.

Run with: uv run python scripts/benchmarks/settle_benchmark.py
"""

from __future__ import annotations

import time
import statistics

import torch

from computronium.ontology.dynamics import (
    EnergyMinimizationDynamics,
    PredictiveSettlingDynamics,
    PCALMDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig
from computronium.ontology.system import SystemState


def _make_test_system(hidden_dim: int = 128, num_layers: int = 3, batch: int = 32):
    """Create a test system for benchmarking."""
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=hidden_dim,
            output_dim=hidden_dim,
            hidden_dims=(hidden_dim,) * num_layers,
        )
    )
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    x = torch.randn(batch, hidden_dim)
    return geometry, substrate, x


def benchmark_settle(dynamics_name: str, dynamics_cls, config, geometry, substrate, x, num_runs: int = 5):
    """Benchmark a dynamics settle method."""
    # Warmup
    for _ in range(2):
        dynamics = dynamics_cls(config)
        state = SystemState(x=x, y=None)
        dynamics.settle(state, geometry, substrate)

    # Benchmark
    times = []
    for _ in range(num_runs):
        dynamics = dynamics_cls(config)
        state = SystemState(x=x, y=None)
        
        start = time.perf_counter()
        dynamics.settle(state, geometry, substrate)
        end = time.perf_counter()
        
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    stdev_time = statistics.stdev(times) if len(times) > 1 else 0
    print(f"{dynamics_name}: {mean_time*1000:.2f}ms ± {stdev_time*1000:.2f}ms (mean ± std over {num_runs} runs)")
    return mean_time


def main():
    print("=" * 60)
    print("Settle Loop Microbenchmarks")
    print("=" * 60)
    
    # Test configurations
    configs = [
        ("Small (hidden=64, layers=2, batch=16)", 64, 2, 16),
        ("Medium (hidden=128, layers=3, batch=32)", 128, 3, 32),
        ("Large (hidden=256, layers=4, batch=64)", 256, 4, 64),
    ]
    
    for name, hidden_dim, num_layers, batch in configs:
        print(f"\n{name}:")
        geometry, substrate, x = _make_test_system(hidden_dim, num_layers, batch)
        
        # EnergyMinimizationDynamics
        config_em = StateDynamicsConfig.energy_minimization(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
        )
        benchmark_settle("  EnergyMinimization", EnergyMinimizationDynamics, config_em, 
                        geometry, substrate, x)
        
        # PredictiveSettlingDynamics
        config_ps = StateDynamicsConfig.predictive_settling(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
        )
        benchmark_settle("  PredictiveSettling", PredictiveSettlingDynamics, config_ps,
                        geometry, substrate, x)
        
        # PCALMDynamics
        config_pcalm = StateDynamicsConfig.pc_alm(
            max_steps=30,
            step_size=0.1,
            beta=0.5,
            rho=1.0,
        )
        benchmark_settle("  PCALM", PCALMDynamics, config_pcalm,
                        geometry, substrate, x)

    # Compiled path benchmark (PredictiveSettling)
    print("\n\nCompiled Path (PredictiveSettling):")
    geometry, substrate, x = _make_test_system(128, 3, 32)
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
    
    # Benchmark compiled
    times = []
    for _ in range(5):
        dynamics = PredictiveSettlingDynamics(config_compiled)
        state = SystemState(x=x, y=None)
        start = time.perf_counter()
        dynamics.settle(state, geometry, substrate)
        end = time.perf_counter()
        times.append(end - start)
    
    mean_time = statistics.mean(times)
    stdev_time = statistics.stdev(times)
    print(f"  PredictiveSettling (compiled): {mean_time*1000:.2f}ms ± {stdev_time*1000:.2f}ms")


if __name__ == "__main__":
    main()