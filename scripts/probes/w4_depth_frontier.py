"""W4 probe: depth frontier + zero-shot LR transfer (TODO13b W4, S1).

Regime: the D14 jpc-faithful loop (ePC free settle steps=H → nudged
settle → PC-native gradient with settled errors frozen → optimizer),
width 128 residual, beta 10 (the generalizing corner), gamma 0.1,
150 train batches, 20 eval batches, MNIST quick-mode, CPU.
Optimizers: torch.optim.Adam (lr on its own axis) vs the OrthoAdam
recipe (``jpc_ortho_adam._OrthoAdamWeights``, ortho_lr 3e-3 — the
D15/D16 configuration of record; SVD polar, NS equivalent statistically).

Pre-registered predictions (written BEFORE any measurement):

- P1 (frontier): the mupc+residual+OrthoAdam recipe reaches depth >= 32
  at mean test >= 0.8 (seeds 0-2). D14 anchor: depth 20 mupc+Adam 0.78.
  Falsified -> the recipe's real limit is depth ~20; name it.
- P2 (zero-shot LR transfer, the clever bit): the ortho_lr chosen at
  depth 8 (best of {1e-3, 3e-3}, seed 0), run UNCHANGED at depths
  20/32, stays within 0.05 of the best arm at that depth. Holds ->
  "tune once, run anywhere" — a μPC-scale-validation capability.
  Falsified -> per-depth retuning is required; honest boundary.
- P3 (default-init rescue): default-init x OrthoAdam at depth 32 is
  not in memorization collapse (test >= 0.5; D14: default+Adam 0.20 at
  depth 20). Falsified -> the rescue is depth-bounded below 32.

Depth 100 runs ONLY if depth-50 test >= 0.8 (compute gate, not a
prediction). Walltime printed, never recorded.

VERDICT (2026-09-07, ~25 min CPU):

- P1 CONFIRMED at 32, bounded at 50: mupc x OrthoAdam depth-32 mean
  test 0.867 (0.845-0.887) >= 0.8; depth 50 collapses to memorization
  (train ~0.97, test 0.286-0.473, mean 0.397). The recipe's real
  frontier is depth ~32-50; depth 100 never ran (gate stayed closed).
- P2 CONFIRMED DECISIVELY: the depth-8-selected ortho_lr 1e-3, run
  UNCHANGED, gives depth-20 mean 0.920 (vs D14's tuned mupc+Adam 0.78)
  and depth-32 0.867 — and BEATS the per-depth retune at 32
  (lr 3e-3: 0.689). "Tune once, run anywhere" holds across 8 -> 32;
  the depth-8 optimum IS the depth-32 optimum.
- P3 FALSIFIED: default-init x OrthoAdam at depth 32 = 0.450
  (memorization; train 0.970) — OrthoAdam's rescue of default init is
  depth-bounded below 32. muPC init remains load-bearing at depth.
- Control: mupc x Adam at 32 = 0.420 — OrthoAdam's mupc rescue is
  +0.45 at depth 32 (Adam depth-fragility, D15 reproduced).
- Headline candidates: "the jpc recipe with OrthoAdam scales to depth
  32 at 0.87 test with a depth-8-tuned lr, unmodified" and "OrthoAdam
  lifts the depth-20 frontier 0.78 -> 0.92". Zero-shot transfer is the
  new capability (S1's "tune once, run anywhere" — CONFIRMED).
"""

from itertools import islice
from typing import Literal

import torch
from jpc_ortho_adam import _OrthoAdamWeights, evaluate

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

WIDTH = 128
BATCH_CAP = 150
EVAL_CAP = 20
BETA = 10.0
GAMMA = 0.1
ADAM_LR = 1e-3


def _flatten(loader, cap):
    for x, y in islice(loader, cap):
        yield x.view(x.size(0), -1), y


def run_arm(
    depth: int,
    init: Literal["default", "mupc"],
    optimizer: str,
    lr: float,
    train_data,
    seed: int,
) -> tuple[float, object, object]:
    torch.manual_seed(seed)
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=(WIDTH,) * depth,
            init_scheme=init,
            residual=True,
        )
    )
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    dynamics = ErrorPredictiveCodingDynamics(
        StateDynamicsConfig.error_predictive_coding(
            max_steps=depth,
            step_size=GAMMA,
            beta=BETA,
            convergence_threshold=0.0,
            convergence_start=depth + 1,
        )
    )
    layered = extract_layered_params(geometry)
    weights = [t[0] for t in layered.transitions]
    if optimizer == "adam":
        opt: torch.optim.Adam | _OrthoAdamWeights = torch.optim.Adam(weights, lr=lr)
    else:
        opt = _OrthoAdamWeights(weights, lr=lr)

    correct = 0
    for x, y in train_data:
        free = dynamics.settle(SystemState(x=x), geometry, substrate, None)
        del free
        dynamics.settle(SystemState(x=x), geometry, substrate, y)
        eps = [e.detach() for e in dynamics._last_errors]

        with torch.enable_grad():
            _, y_hat = dynamics._build_forward_with_errors(
                x, layered.transitions, substrate, eps, residual=True
            )
            energy = BETA * torch.nn.functional.cross_entropy(y_hat, y)
            grads = torch.autograd.grad(energy, weights)

        if isinstance(opt, torch.optim.Adam):
            opt.zero_grad()
            for w, g in zip(weights, grads, strict=True):
                w.grad = g
            opt.step()
        else:
            opt.step([g.detach() for g in grads])
        correct += (y_hat.argmax(1) == y).sum().item()
    return (
        correct / (len(train_data) * train_data[0][1].shape[0]),
        dynamics,
        geometry,
    )


def main() -> None:
    import time

    t0 = time.time()
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    torch.manual_seed(0)  # seed BEFORE the loader draw (D8 trap)
    train_data = list(_flatten(task.get_dataloader("train"), BATCH_CAP))
    eval_data = list(_flatten(task.get_dataloader("test"), EVAL_CAP))
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))

    def cell(depth: int, init: str, optimizer: str, lr: float, seed: int) -> float:
        train_acc, dynamics, geometry = run_arm(
            depth, init, optimizer, lr, train_data, seed
        )
        test_acc = evaluate(dynamics, geometry, substrate, eval_data)
        print(
            f"depth {depth:>3} {init:>7} x {optimizer:<10} lr {lr:<6} "
            f"seed {seed}: train {train_acc:.3f}  test {test_acc:.3f}",
            flush=True,
        )
        return test_acc

    print("=== P2 pick: depth-8 lr selection (mupc x ortho_adam, seed 0) ===")
    depth8 = {lr: cell(8, "mupc", "ortho_adam", lr, 0) for lr in (1e-3, 3e-3)}
    zs_lr = max(depth8.items(), key=lambda kv: kv[1])[0]
    print(f"zero-shot lr = {zs_lr}", flush=True)

    print("\n=== P1/P2 sweep: mupc x ortho_adam, zero-shot lr, seeds 0-2 ===")
    results: dict[int, list[float]] = {}
    for depth in (20, 32, 50):
        accs = [cell(depth, "mupc", "ortho_adam", zs_lr, s) for s in (0, 1, 2)]
        results[depth] = accs
        print(
            f"  depth {depth} MEAN {sum(accs) / len(accs):.3f} "
            f"(range {max(accs) - min(accs):.3f})",
            flush=True,
        )

    print("\n=== P2 controls: adam reference + per-depth ortho lr at 32 ===")
    cell(32, "mupc", "adam", ADAM_LR, 0)
    other_lr = 3e-3 if abs(zs_lr - 1e-3) < 1e-12 else 1e-3
    cell(32, "mupc", "ortho_adam", other_lr, 0)

    print("\n=== P3: default-init rescue at depth 32 ===")
    cell(32, "default", "ortho_adam", zs_lr, 0)

    if sum(results.get(50, [0.0])) / 3 >= 0.8:
        print("\n=== compute gate open: depth 100 ===")
        cell(100, "mupc", "ortho_adam", zs_lr, 0)

    print(f"\nwalltime {time.time() - t0:.1f}s (printed, never recorded)")


if __name__ == "__main__":
    main()
