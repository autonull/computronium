"""Depth-50 Autopsy (TODO15 §1.2): classify the 150-batch collapse
(0.397 mean test acc, w4_depth_frontier P1/P2 sweep) as init / optimizer
/ memorization / data-budget failure — 10-50 batches, no verdict run.

Instruments (pre-registered, TODO15 §1.2):
- first forward: activation ratio ‖a_50‖/‖a_1‖
- first backward: gradient ratio ‖g_1‖/‖g_50‖
- loss velocity (L_1 − L_10)/L_1 over the first 10 batches
- at batch 50: train acc vs val acc

Verdict thresholds: activation or gradient ratio < 0.01 or > 100 →
init failure; velocity < 1% with healthy gradients → optimizer failure;
train ≫ val at batch 50 → memorization; all healthy → data-budget.

uv run python scripts/probes/d50_autopsy.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import itertools
import time
from itertools import islice

import torch
from torch.nn import functional


from jpc_ortho_adam import _OrthoAdamWeights
from w4_depth_frontier import (
    BETA,
    GAMMA,
    WIDTH,
    _flatten,
    evaluate,
)

from computronium import (  # type: ignore[attr-defined]
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

DEPTH = 50
LR = 1e-3
AUTOPSY_BATCHES = 50
WEIGHT_DECAY = 0.0
HARVEST = False
EMA = False
PROBE_FREE = False
SEED = 0
DEVICE = "cpu"
TASK = "mnist"
INPUT_DIM = 784


def main() -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-statements]
    t0 = time.time()
    task = create_task(TASK, device=DEVICE, quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(SEED)  # D8 trap: seed BEFORE the loader draw
    train_data = [
        (x.to(DEVICE), y.to(DEVICE))
        for x, y in islice(
            (
                (x.to(DEVICE), y.to(DEVICE))
                for x, y in itertools.cycle(task.get_dataloader("train"))
            ),
            AUTOPSY_BATCHES,
        )
    ]
    eval_data = [
        (x.to(DEVICE), y.to(DEVICE))
        for x, y in _flatten(task.get_dataloader("test"), 20)
    ]

    torch.manual_seed(SEED)
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=INPUT_DIM,
            output_dim=10,
            hidden_dims=(WIDTH,) * DEPTH,
            init_scheme="mupc",
            residual=True,
        )
    ).to(DEVICE)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device=DEVICE))
    dynamics = ErrorPredictiveCodingDynamics(
        StateDynamicsConfig.error_predictive_coding(
            max_steps=DEPTH,
            step_size=GAMMA,
            beta=BETA,
            convergence_threshold=0.0,
            convergence_start=DEPTH + 1,
        )
    )
    layered = extract_layered_params(geometry)
    weights = [t[0] for t in layered.transitions]
    opt = _OrthoAdamWeights(weights, lr=LR)
    ema_decay = 0.99
    ema = [w.detach().clone() for w in weights] if EMA else []

    losses: list[float] = []
    correct = 0
    act_ratio: float = 0.0
    grad_ratio: float = 0.0
    best_val = 0.0
    best_step = 0
    for step, (x, y) in enumerate(train_data):
        free = dynamics.settle(SystemState(x=x), geometry, substrate, None)
        if step == 0:
            with torch.no_grad():
                acts = geometry.forward_with_intermediates(x, substrate)
                norms = [a.norm().item() for a in acts]
                act_ratio = norms[-2] / max(norms[1], 1e-30)
            print(f"activation norms a1={norms[1]:.3f} a50={norms[-2]:.3f}", flush=True)
        del free
        dynamics.settle(SystemState(x=x), geometry, substrate, y)
        eps = [e.detach() for e in dynamics._last_errors]

        with torch.enable_grad():
            _, y_hat = dynamics._build_forward_with_errors(
                x, layered.transitions, substrate, eps, residual=True
            )
            energy = BETA * functional.cross_entropy(y_hat, y)
            grads = torch.autograd.grad(energy, weights)
            if step == 0:
                grad_ratio = grads[0].norm().item() / max(
                    grads[-1].norm().item(), 1e-30
                )
            losses.append(functional.cross_entropy(y_hat, y).item())

        if isinstance(opt, torch.optim.Adam):
            opt.zero_grad()
            for w, g in zip(weights, grads, strict=True):
                w.grad = g
            opt.step()
        else:
            opt.step([g.detach() for g in grads])
        if WEIGHT_DECAY > 0:
            with torch.no_grad():
                for w in weights:
                    w.mul_(1 - LR * WEIGHT_DECAY)
        correct += (y_hat.argmax(1) == y).sum().item()
        if EMA:
            with torch.no_grad():
                for w, e in zip(weights, ema, strict=True):
                    e.mul_(ema_decay).add_(w.detach(), alpha=1 - ema_decay)
        if HARVEST and not PROBE_FREE and step % 10 == 0:
            val = evaluate(dynamics, geometry, substrate, eval_data)
            if val > best_val:
                best_val, best_step = val, step
            print(f"  batch {step:>3} val {val:.3f}", flush=True)

    if HARVEST:
        if not PROBE_FREE:
            print(f"best val {best_val:.3f} @ batch {best_step}", flush=True)
        if EMA:
            with torch.no_grad():
                for w, e in zip(weights, ema, strict=True):
                    w.copy_(e)
            ema_val = evaluate(dynamics, geometry, substrate, eval_data)
            print(f"EMA(0.99) final val {ema_val:.3f}", flush=True)
            best_val = max(best_val, ema_val)
        verdict = f"VAL-PEAK HARVEST {'PASSES the 0.75 gate' if best_val >= 0.75 else 'fails the 0.75 gate'}"
        print(f"\nVERDICT: {verdict}", flush=True)
        print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
        return 0
    velocity = (losses[0] - losses[min(9, len(losses) - 1)]) / losses[0]
    train_acc = correct / (AUTOPSY_BATCHES * train_data[0][1].shape[0])
    with torch.enable_grad():
        val_acc = evaluate(dynamics, geometry, substrate, eval_data)
    print(f"activation ratio ‖a50‖/‖a1‖ = {act_ratio:.4e}", flush=True)
    print(f"gradient ratio ‖g1‖/‖g50‖ = {grad_ratio:.4e}", flush=True)
    print(
        f"loss L1 {losses[0]:.4f} → L10 {losses[9]:.4f}  velocity {velocity:.4f}",
        flush=True,
    )
    print(
        f"batch-{AUTOPSY_BATCHES}: train acc {train_acc:.3f}  val acc {val_acc:.3f}",
        flush=True,
    )

    dyn_bad = (
        act_ratio < 0.01 or act_ratio > 100 or grad_ratio < 0.01 or grad_ratio > 100
    )
    if dyn_bad:
        verdict = "INIT/VANISHING failure → μPC init rescale cell"
    elif velocity < 0.01:
        verdict = "OPTIMIZER/LR failure → Muon 0.02 vs OrthoAdam 0.01 screen"
    elif train_acc > 2 * val_acc:
        verdict = "MEMORIZATION failure → weight decay / dropout cell"
    else:
        verdict = "HEALTHY → data-budget boundary (not dynamical)"
    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


def main_entry() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batches", type=int, default=50)
    parser.add_argument("--wd", type=float, default=0.0)
    parser.add_argument("--harvest", action="store_true")
    parser.add_argument("--probe-free", action="store_true")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--depth", type=int, default=50)
    parser.add_argument("--ema", action="store_true")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--task", default="mnist")
    parser.add_argument("--input-dim", type=int, default=784)
    args = parser.parse_args()
    globals()["AUTOPSY_BATCHES"] = args.batches
    globals()["WEIGHT_DECAY"] = args.wd
    globals()["HARVEST"] = args.harvest
    globals()["SEED"] = args.seed
    globals()["DEPTH"] = args.depth
    globals()["EMA"] = args.ema
    globals()["PROBE_FREE"] = args.probe_free
    globals()["DEVICE"] = args.device
    globals()["TASK"] = args.task
    globals()["INPUT_DIM"] = args.input_dim
    return main()


if __name__ == "__main__":
    raise SystemExit(main_entry())
