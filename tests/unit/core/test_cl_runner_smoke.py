"""Regression locks for the CL runner's matched-plasticity arms.

Two latent defects had no coverage: the protocol call sites passed
keyword-only fields positionally, and ``_finalize_metrics`` read
``fast_weights_dim`` instead of ``fast_weight_dim``. Both crashed
``run_continual_learning``. Removing either fix fails these tests.
"""

from __future__ import annotations

from computronium.core.continual import (
    CL_NUM_TASKS,
    CLConfig,
    create_plasticity_arm,
    run_continual_learning,
)
from computronium.core.joint.transition import NullPlasticity


def test_matched_arms_vary_only_plasticity() -> None:
    control = create_plasticity_arm(
        "null", input_dim=64, hidden_dim=16, output_dim=10, device="cpu"
    )
    treatment = create_plasticity_arm(
        "fast_weights", input_dim=64, hidden_dim=16, output_dim=10, device="cpu"
    )
    assert isinstance(control.plasticity, NullPlasticity)
    assert getattr(treatment.plasticity, "fast_weight_dim", None) == 512
    assert type(control.geometry) is type(treatment.geometry)
    assert type(control.credit) is type(treatment.credit)


def test_continual_runner_completes_one_epoch_per_task() -> None:
    metrics = run_continual_learning(
        "matched_null",
        CLConfig(epochs_per_task=1, hidden_dim=64, seed=62, device="cpu"),
        "task_incremental",
    )
    assert len(metrics.final_accuracies) == CL_NUM_TASKS
    assert len(metrics.accuracy_matrix) == CL_NUM_TASKS
    assert metrics.avg_forgetting >= 0.0
