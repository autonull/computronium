"""D19 — Depth headline under probe-free EMA harvest (TODO16 §1.1).

Wraps the d50_autopsy harvest instrument as a gallery demo: depth-{32, 50}
MLPs (784→128×N→10, mupc init, residual, OrthoAdam), 150 batches, one
training run per depth evaluated two ways — final-step weights vs
streaming EMA(0.99) weights. EMA ≥ final-step at every depth is the
harvest headline; depth-50 EMA ≥ 0.75 is the depth headline.

Measured (2026-09-09, mnist quick): see record.
"""

import sys
import time
from itertools import islice

import pytest
import torch
from torch.nn import functional

sys.path.insert(0, "scripts/probes")

from jpc_ortho_adam import _OrthoAdamWeights
from w4_depth_frontier import _flatten, evaluate

from computronium import (
    DigitalSubstrate,
    ErrorPredictiveCodingDynamics,
    FeedforwardGeometry,
    GeometryConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    create_task,
)
from computronium.ontology._settle_kernel import extract_layered_params
from computronium.visualization._demo_api import bars_panel, figure_spec

BATCHES = 150
WIDTH = 128
LR = 1e-3
EMA_DECAY = 0.99
SEED = 0


def _run(depth: int, train_data, eval_data) -> dict[str, float]:
    torch.manual_seed(SEED)
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(WIDTH,) * depth,
            init_scheme="mupc",
            residual=True,
        )
    )
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    dynamics = ErrorPredictiveCodingDynamics(
        StateDynamicsConfig.error_predictive_coding(
            max_steps=depth,
            step_size=0.5,
            beta=0.5,
            convergence_threshold=0.0,
            convergence_start=depth + 1,
        )
    )
    layered = extract_layered_params(geometry)
    weights = [t[0] for t in layered.transitions]
    opt = _OrthoAdamWeights(weights, lr=LR)
    ema = [w.detach().clone() for w in weights]

    for x, y in train_data:
        dynamics.settle(SystemState(x=x), geometry, substrate, None)
        dynamics.settle(SystemState(x=x), geometry, substrate, y)
        eps = [e.detach() for e in dynamics._last_errors]
        with torch.enable_grad():
            _, y_hat = dynamics._build_forward_with_errors(
                x, layered.transitions, substrate, eps, residual=True
            )
            grads = torch.autograd.grad(
                0.5 * functional.cross_entropy(y_hat, y), weights
            )
        opt.step([g.detach() for g in grads])
        with torch.no_grad():
            for w, e in zip(weights, ema, strict=True):
                e.mul_(EMA_DECAY).add_(w.detach(), alpha=1 - EMA_DECAY)

    final_acc = evaluate(dynamics, geometry, substrate, eval_data)
    with torch.no_grad():
        for w, e in zip(weights, ema, strict=True):
            w.copy_(e)
    ema_acc = evaluate(dynamics, geometry, substrate, eval_data)
    return {"final": final_acc, "ema": ema_acc}


@pytest.mark.timeout(900)
def test_demo_depth_harvest(emit_run_record) -> None:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(SEED)  # seed BEFORE the loader draw (D8 trap)
    train_data = list(islice(task.get_dataloader("train"), BATCHES))
    eval_data = list(_flatten(task.get_dataloader("test"), 20))

    arms = {f"depth_{d}": _run(d, train_data, eval_data) for d in (32, 50)}
    for label, accs in arms.items():
        print(f"{label}: final {accs['final']:.3f}  ema {accs['ema']:.3f}")
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")

    record = {
        "batches": BATCHES,
        "width": WIDTH,
        "lr": LR,
        "ema_decay": EMA_DECAY,
        "seed": SEED,
        "arms": arms,
        "figure": figure_spec(
            "D19 — Probe-free EMA harvest vs final-step weights (depth headline)",
            bars_panel(
                {
                    label: {"final_step": accs["final"], "ema_harvest": accs["ema"]}
                    for label, accs in arms.items()
                },
                xlabel="",
                ylabel="test accuracy",
                chance=0.1,
            ),
        ),
    }
    emit_run_record("D19", "depth_harvest", record)

    for accs in arms.values():
        assert accs["ema"] >= accs["final"]
    assert arms["depth_50"]["ema"] >= 0.75
