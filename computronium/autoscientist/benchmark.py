"""Inference benchmarking for promotion tiers (TODO31 Phase 3.3).

Measures latency and throughput on promoted cells (L1+) to populate
the KB with latency_ms and throughput_samples_s metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import torch

if TYPE_CHECKING:
    from computronium.autoscientist.bridge import ExperimentProposal

__all__ = [
    "InferenceMetrics",
    "benchmark_inference",
    "benchmark_inference_from_campaign_result",
    "benchmark_inference_on_system",
]


@dataclass(frozen=True, slots=True)
class InferenceMetrics:
    """Inference performance metrics."""

    latency_ms: float  # Mean latency per batch (ms)
    throughput_samples_s: float  # Samples per second
    latency_p50_ms: float  # Median latency
    latency_p95_ms: float  # 95th percentile latency
    latency_p99_ms: float  # 99th percentile latency


def benchmark_inference(
    proposal: ExperimentProposal,
    task_name: str,
    *,
    warmup_batches: int = 5,
    benchmark_batches: int = 50,
    batch_size: int = 64,
    device: str | None = None,
) -> InferenceMetrics:
    """Run inference benchmark on a composed system.

    Args:
        proposal: Experiment proposal with model, geometry, dynamics, etc.
        task_name: Task name for dataloader creation.
        warmup_batches: Number of warmup batches (not counted).
        benchmark_batches: Number of batches to measure.
        batch_size: Batch size for benchmarking.
        device: Device to run on (auto-detect if None).

    Returns:
        InferenceMetrics with latency and throughput measurements.
    """
    from computronium.autoscientist.compose import compose_proposal_system
    from computronium.core.utils.device import get_device
    from computronium.domains.factory import create_task

    target_device = get_device() if device is None else torch.device(device)
    task = create_task(
        task_name, device=str(target_device), quick_mode=True, num_workers=0
    )
    task.setup()

    # Compose the system
    system = compose_proposal_system(  # type: ignore[misc]
        proposal.model,
        input_dim=task.input_dim,
        output_dim=task.output_dim,
        lr=0.0,  # Not used for inference
        geometry=proposal.geometry or {},
        dynamics=proposal.dynamics,
        credit=proposal.credit,
        update=proposal.update,
    )
    system.to(target_device)  # type: ignore[attr-defined]
    system.eval()  # type: ignore[attr-defined]

    # Get dataloader
    loader = task.get_dataloader("val")
    if loader is None:
        # Fallback: synthetic data
        input_dim = task.input_dim
        if isinstance(input_dim, tuple | list):
            input_dim = int(torch.prod(torch.tensor(input_dim)).item())
        synthetic_loader = [
            (
                torch.randn(batch_size, input_dim, device=target_device),
                torch.randint(0, task.output_dim, (batch_size,), device=target_device),
            )
            for _ in range(warmup_batches + benchmark_batches)
        ]
        loader = synthetic_loader

    # Warmup
    with torch.no_grad():
        for i, (batch_inputs, _) in enumerate(loader):
            if i >= warmup_batches:
                break
            batch_inputs = batch_inputs.to(target_device)  # ruff: ignore[redefined-loop-name]
            _ = system(batch_inputs)

    # Benchmark
    latencies: list[float] = []
    total_samples = 0

    with torch.no_grad():
        for i, (batch_inputs, _) in enumerate(loader):
            if i >= benchmark_batches:
                break
            batch_inputs = batch_inputs.to(target_device)  # ruff: ignore[redefined-loop-name]
            batch_size_actual = batch_inputs.shape[0]
            total_samples += batch_size_actual

            start = time.perf_counter()
            _ = system(batch_inputs)
            if target_device.type == "cuda":
                torch.cuda.synchronize()
            end = time.perf_counter()

            latencies.append((end - start) * 1000.0)  # ms

    if not latencies:
        return InferenceMetrics(
            latency_ms=0.0,
            throughput_samples_s=0.0,
            latency_p50_ms=0.0,
            latency_p95_ms=0.0,
            latency_p99_ms=0.0,
        )

    import numpy as np

    latencies_np = np.array(latencies)
    total_time_s = latencies_np.sum() / 1000.0

    return InferenceMetrics(
        latency_ms=float(latencies_np.mean()),
        throughput_samples_s=float(total_samples / total_time_s)
        if total_time_s > 0
        else 0.0,
        latency_p50_ms=float(np.percentile(latencies_np, 50)),
        latency_p95_ms=float(np.percentile(latencies_np, 95)),
        latency_p99_ms=float(np.percentile(latencies_np, 99)),
    )


def benchmark_inference_on_system(
    system: torch.nn.Module,
    task_name: str,
    *,
    warmup_batches: int = 5,
    benchmark_batches: int = 50,
    batch_size: int = 64,
    device: str | None = None,
) -> InferenceMetrics:
    """Run inference benchmark on an already-composed system.

    Args:
        system: Pre-composed PyTorch module.
        task_name: Task name for dataloader creation.
        warmup_batches: Number of warmup batches.
        benchmark_batches: Number of batches to measure.
        batch_size: Batch size for benchmarking.
        device: Device to run on.

    Returns:
        InferenceMetrics with latency and throughput measurements.
    """
    from computronium.core.utils.device import get_device
    from computronium.domains.factory import create_task

    target_device = get_device() if device is None else torch.device(device)
    task = create_task(
        task_name, device=str(target_device), quick_mode=True, num_workers=0
    )
    task.setup()

    system.to(target_device)  # type: ignore[attr-defined]
    system.eval()  # type: ignore[attr-defined]

    loader = task.get_dataloader("val")
    if loader is None:
        input_dim = task.input_dim
        if isinstance(input_dim, tuple | list):
            input_dim = int(torch.prod(torch.tensor(input_dim)).item())
        synthetic_loader = [
            (
                torch.randn(batch_size, input_dim, device=target_device),
                torch.randint(0, task.output_dim, (batch_size,), device=target_device),
            )
            for _ in range(warmup_batches + benchmark_batches)
        ]
        loader = synthetic_loader

    # Warmup
    with torch.no_grad():
        for i, (batch_inputs, _) in enumerate(loader):
            if i >= warmup_batches:
                break
            batch_inputs = batch_inputs.to(target_device)  # ruff: ignore[redefined-loop-name]
            _ = system(batch_inputs)

    # Benchmark
    latencies: list[float] = []
    total_samples = 0

    with torch.no_grad():
        for i, (batch_inputs, _) in enumerate(loader):
            if i >= benchmark_batches:
                break
            batch_inputs = batch_inputs.to(target_device)  # ruff: ignore[redefined-loop-name]
            batch_size_actual = batch_inputs.shape[0]
            total_samples += batch_size_actual

            start = time.perf_counter()
            _ = system(batch_inputs)
            if target_device.type == "cuda":
                torch.cuda.synchronize()
            end = time.perf_counter()

            latencies.append((end - start) * 1000.0)

    if not latencies:
        return InferenceMetrics(
            latency_ms=0.0,
            throughput_samples_s=0.0,
            latency_p50_ms=0.0,
            latency_p95_ms=0.0,
            latency_p99_ms=0.0,
        )

    import numpy as np

    latencies_np = np.array(latencies)
    total_time_s = latencies_np.sum() / 1000.0

    return InferenceMetrics(
        latency_ms=float(latencies_np.mean()),
        throughput_samples_s=float(total_samples / total_time_s)
        if total_time_s > 0
        else 0.0,
        latency_p50_ms=float(np.percentile(latencies_np, 50)),
        latency_p95_ms=float(np.percentile(latencies_np, 95)),
        latency_p99_ms=float(np.percentile(latencies_np, 99)),
    )


def benchmark_inference_from_campaign_result(
    result: dict[str, object],
    *,
    warmup_batches: int = 5,
    benchmark_batches: int = 50,
    batch_size: int = 64,
) -> InferenceMetrics | None:
    """Run inference benchmark from a campaign result dict.

    Reconstructs the system from the proposal in the result and runs
    the benchmark. Used during L1/L2 promotion.

    Args:
        result: Campaign result dict with 'proposal' and 'task'.
        warmup_batches: Number of warmup batches.
        benchmark_batches: Number of batches to measure.
        batch_size: Batch size for benchmarking.

    Returns:
        InferenceMetrics or None if reconstruction fails.
    """
    proposal_data = result.get("proposal")
    if not proposal_data:
        return None

    try:
        from computronium.autoscientist.bridge import ExperimentProposal

        proposal = ExperimentProposal(**proposal_data)  # type: ignore[arg-type]
        task_name = str(result.get("task", str(proposal.task or "mnist")))
        return benchmark_inference(
            proposal,
            task_name,
            warmup_batches=warmup_batches,
            benchmark_batches=benchmark_batches,
            batch_size=batch_size,
        )
    except Exception:
        return None
