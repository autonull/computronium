"""TODO23 integration validation — full loop on 5 problem classes.

Each class is a distinct `ProblemSpec` scenario; the loop is
specify → synthesize → build → train (stability guard + harvest) →
[adapt for the continual class]. The ψ mechanism classes (temporal_psi
recipes) build a readout component rather than a trainable System — for
those, the loop trains the frozen backbone and adapts it ψ-only (the
mechanism's own semantics, TODO17).
"""

from __future__ import annotations

import torch
from computronium_lab import Constraints, Lab, TrainOptions

SCENARIOS: dict[str, dict[str, object]] = {
    "vision": {"dataset": "mnist_cifar", "constraints": {}},
    "tabular": {"dataset": "tabular_uci", "constraints": {}},
    "local_credit": {"dataset": "synthetic", "constraints": {"local_credit": True}},
    "latency_budget": {"dataset": "synthetic", "constraints": {"latency_ms": 10.0}},
    "continual": {"dataset": "synthetic", "constraints": {"continual": True}},
}


def _task_stream() -> list[tuple[torch.Tensor, torch.Tensor]]:
    gen = torch.Generator().manual_seed(1)
    return [(torch.randn(32, 32, generator=gen), torch.zeros(32, dtype=torch.long))]


def _loop(cfg: dict[str, object]) -> dict[str, object]:
    lab = Lab(seed=0)
    spec = lab.specify(
        "classification",
        str(cfg["dataset"]),
        constraints=Constraints(**cfg["constraints"]),  # type: ignore[arg-type]
    )
    result = lab.synthesize(spec)
    built = result.build(spec)
    summary: dict[str, object] = {
        "mechanism": result.name,
        "exploratory": result.exploratory,
    }

    if not hasattr(built, "geometry"):
        # ψ mechanism: frozen backbone + ψ readout (TODO17 semantics)
        backbone = lab.compose("backprop_mlp", input_dim=spec.input_dim)
        lab.train(
            backbone, epochs=1, spec=spec, options=TrainOptions(stability_guard=True)
        )
        adapted = lab.adapt(backbone, _task_stream(), mode="temporal", episodes=2)
        summary["theta_invariant"] = adapted.theta.bitwise_invariant
        return summary

    training = lab.train(
        built, epochs=1, spec=spec, options=TrainOptions(stability_guard=True)
    )
    summary["trained"] = "loss" in training.metrics
    if spec.constraints.continual:
        adapted = lab.adapt(built, _task_stream(), mode="temporal", episodes=2)
        summary["theta_invariant"] = adapted.theta.bitwise_invariant
    return summary


def test_full_loop_five_problem_classes() -> None:
    for name, cfg in SCENARIOS.items():
        summary = _loop(cfg)
        assert summary["mechanism"], f"{name}: no mechanism synthesized"
        assert "theta_invariant" not in summary or summary["theta_invariant"], (
            f"{name}: θ invariance failed"
        )
        print(f"{name}: {summary}")
