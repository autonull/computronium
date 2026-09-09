"""OrthoAdam chaos probe (TODO15 §8.2 incidental finding): is the
depth-frontier OrthoAdam recipe trajectory-chaotic under microscopic
perturbations, or was the 0.747-vs-0.361 val gap a real decay effect?

Twin trajectories, ε→0: identical depth-50 mupc×OrthoAdam runs, seed 0,
differing ONLY by 1e-7 absolute noise on the initialized weights,
stepped interleaved in one loop. Val acc every 10 batches on the shared
eval draw; per-batch twin distance ‖Δθ‖ reported.

Verdict: twins diverge to different val accs → trajectory chaos (deep
OrthoAdam cells are distribution draws; single-seed cells at depth ≥ 32
are not reproducible measurements). Twins stay close → the §8.2 gap was
the decay, and depth-50 measurements are trustworthy.

uv run python scripts/probes/orthoadam_chaos.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import sys
import time

import torch
from torch.nn import functional

sys.path.insert(0, "scripts/probes")

from jpc_ortho_adam import _OrthoAdamWeights
from w4_depth_frontier import BETA, GAMMA, WIDTH, _flatten, evaluate

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
BATCHES = 30
EPS = 1e-7


def _twin(seed: int, perturb: bool):
    torch.manual_seed(seed)
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(WIDTH,) * DEPTH,
            init_scheme="mupc",
            residual=True,
        )
    )
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
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
    if perturb:
        gen = torch.Generator().manual_seed(1)
        with torch.no_grad():
            for w in weights:
                w.add_(torch.randn(w.shape, generator=gen) * EPS)
    opt = _OrthoAdamWeights(weights, lr=LR)
    return geometry, substrate, dynamics, layered, weights, opt


def main() -> int:
    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # D8 trap: seed BEFORE the loader draw
    train_data = list(_flatten(task.get_dataloader("train"), BATCHES))
    eval_data = list(_flatten(task.get_dataloader("test"), 20))

    ga, sa, da, la, wa, oa = _twin(0, perturb=False)
    gb, sb, db, lb, wb, ob = _twin(0, perturb=True)

    vals_a: list[float] = []
    vals_b: list[float] = []
    for step, (x, y) in enumerate(train_data, 1):
        for g, s, d, l, w, o in ((ga, sa, da, la, wa, oa), (gb, sb, db, lb, wb, ob)):
            free = d.settle(SystemState(x=x), g, s, None)
            del free
            d.settle(SystemState(x=x), g, s, y)
            eps = [e.detach() for e in d._last_errors]
            with torch.enable_grad():
                _, y_hat = d._build_forward_with_errors(
                    x, l.transitions, s, eps, residual=True
                )
                grads = torch.autograd.grad(
                    BETA * functional.cross_entropy(y_hat, y), w
                )
            o.step([t.detach() for t in grads])
        if step % 10 == 0:
            va = evaluate(da, ga, sa, eval_data)
            vb = evaluate(db, gb, sb, eval_data)
            dist = sum((a - b).norm().item() for a, b in zip(wa, wb, strict=True))
            vals_a.append(va)
            vals_b.append(vb)
            print(
                f"batch {step:>3}: A {va:.3f}  B {vb:.3f}  ‖Δθ‖ {dist:.3e}",
                flush=True,
            )

    gap = abs(vals_a[-1] - vals_b[-1])
    verdict = (
        f"CHAOTIC: ε={EPS:g} twins diverged (final val gap {gap:.3f}) — "
        "deep OrthoAdam cells are distribution draws"
        if gap > 0.05
        else f"STABLE: twins track (final val gap {gap:.3f}) — §8.2 gap "
        "attributable to weight decay"
    )
    print(f"\nVERDICT: {verdict}", flush=True)
    print(f"walltime {time.time() - t0:.1f}s (printed, never recorded)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
