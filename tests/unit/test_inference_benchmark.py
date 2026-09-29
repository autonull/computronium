"""Inference-benchmark reconstruction over shape-reporting tasks.

The L1/L2 promotion path benchmarks inference from a campaign result, and its
latency silently vanished (`latency_ms=0.0`) for every promoted cell whose task
reports an unflattened input shape.
"""

from __future__ import annotations

import pytest

from computronium.autoscientist.benchmark import benchmark_inference
from computronium.autoscientist.bridge import ExperimentProposal

pytestmark = pytest.mark.filterwarnings("ignore::UserWarning")


@pytest.mark.parametrize("task", ["spiral", "mnist"])
def test_benchmark_inference_sizes_geometry_from_flat_input_dim(task: str) -> None:
    """Benchmarking composes a geometry, so a shape-shaped input_dim must flatten.

    Regression test for: ``benchmark_inference`` passed the task's raw
    ``input_dim`` to ``compose_proposal_system``; vision tasks report
    ``(C, H, W)``, geometry construction raised ``TypeError``, and the
    caller's blanket ``except`` turned the failure into a missing metric
    instead of a reported one.
    """
    proposal = ExperimentProposal(
        hypothesis="latency probe",
        model="feedforward_mlp",
        task=task,
        geometry={
            "topology_type": "feedforward",
            "depth": 2,
            "hidden_dim": 16,
        },
        dynamics="instantaneous",
        credit="local_goodness",
        update="euclidean",
    )

    metrics = benchmark_inference(
        proposal, task, warmup_batches=1, benchmark_batches=2, batch_size=8
    )

    assert metrics.latency_ms > 0.0
    assert metrics.throughput_samples_s > 0.0
