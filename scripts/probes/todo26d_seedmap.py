"""TODO26d Round 3b — re-diagnosis after the RED×3 gate.

1. Seed map: residual+μPC+LocalAdam (ePC credit) across 5 seeds ×
   depth {12,20,30} × lr {1e-3, 3e-3, 1e-2} on sign-of-mean. Question:
   is the depth-20 seed collapse (0.849/0.633/0.854) an outlier or a
   systematic instability? Does depth 30 hold across seeds?

2. Readout ceiling: is ψ's ~0.73 plateau the frozen-features linear
   ceiling? Fit a full ridge readout on the frozen net's penultimate
   activations with 3000 fresh Task-B samples — the accuracy ANY linear
   readout on these frozen features can reach. If ceiling ≈ 0.73, the ψ
   law is already optimal in its class and the 0.95 bar is a
   feature-quality problem, not an optimization problem.

3. MNIST operating-point alignment: re-run the residual+μPC MNIST cell
   at the recorded positive operating point (mupc_residual_regime:
   Euclid 0.2, sPC 60 steps compiled, 600 batches, width 128, depth 8)
   before concluding anything about μPC under local optimizers.

Run: uv run python scripts/probes/todo26d_seedmap.py
Walltime printed, never recorded.
"""

from __future__ import annotations

import time
from itertools import islice

import torch
from torch import Tensor

from computronium import (
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    ErrorPredictiveCodingDynamics,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    LocalAdamUpdate,
    ParameterUpdateConfig,
    PredictiveSettlingDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    SystemTrainer,
    SystemTrainerConfig,
    ThermodynamicContrast,
    compose_system,
    create_task,
)
from computronium.core.pipeline import forward_pass, run_train_step
from computronium.experiments.joint.tasks import create_switching_task

INPUT_DIM = 16
WIDTH = 32
BATCH = 64
BETA = 0.5
DEVICE = "cpu"
SEEDS = (0, 1, 2, 3, 4)


def _epc_system(depth: int, lr: float, seed: int):
    torch.manual_seed(seed)
    return compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=4 * INPUT_DIM,
                output_dim=2,
                hidden_dims=(WIDTH,) * depth,
                residual=True,
                init_scheme="mupc",
            )
        ),
        dynamics=ErrorPredictiveCodingDynamics(
            StateDynamicsConfig.error_predictive_coding(
                max_steps=5, step_size=0.5, beta=BETA
            )
        ),
        credit=ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
        ),
        update=LocalAdamUpdate(
            ParameterUpdateConfig.local_adam(step_size=lr, momentum=0.9)
        ),
    )


def seed_map() -> None:
    print("== Seed map: residual+mupc+LocalAdam, sign-of-mean ==", flush=True)
    data = [create_switching_task(BATCH, 4, INPUT_DIM, phase="A") for _ in range(60)]
    for depth in (12, 20, 30):
        for lr in (1e-3, 3e-3, 1e-2):
            accs = []
            for seed in SEEDS:
                system = _epc_system(depth, lr, seed)
                acc = SystemTrainer(
                    system=system,
                    config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=seed),
                    train_data=data,
                ).fit()[-1]["train_acc"]
                accs.append(acc)
            mean = sum(accs) / len(accs)
            print(
                f"depth {depth:>2} lr {lr:g}: seeds "
                f"[{' '.join(f'{a:.3f}' for a in accs)}]  mean {mean:.3f}  "
                f"min {min(accs):.3f}  max {max(accs):.3f}",
                flush=True,
            )


def _trained_theta_system():
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=4 * INPUT_DIM, output_dim=2, hidden_dims=(64, 64)
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=BackpropCredit(CreditAssignmentConfig.gradient()),
        update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.05)),
    )
    for _ in range(300):
        x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase="A")
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x.reshape(BATCH, -1),
            y,
        )
    return system


def _frozen_features(system, phase: str, n: int) -> tuple[Tensor, Tensor]:
    xs: list[Tensor] = []
    ys: list[Tensor] = []
    with torch.no_grad():
        while sum(t.shape[0] for t in xs) < n:
            x, y = create_switching_task(BATCH, 4, INPUT_DIM, phase=phase)
            state = SystemState(x=x.reshape(BATCH, -1))
            state.activations = forward_pass(
                system.substrate, system.geometry, x.reshape(BATCH, -1)
            )
            settled = system.dynamics.settle(
                state,
                system.geometry,
                system.substrate,
                target=None,  # type: ignore[arg-type]
            )
            acts = settled.activations
            assert isinstance(acts, list)
            xs.append(acts[-2])
            ys.append(y)
    return torch.cat(xs)[:n], torch.cat(ys)[:n]


def readout_ceiling() -> None:
    print("== Readout ceiling: linear ridge on frozen Task-B features ==", flush=True)
    torch.manual_seed(0)
    system = _trained_theta_system()
    for p in system.geometry.params.values():
        p.requires_grad_(False)
    xf, yf = _frozen_features(system, "B", 3000)
    xe, ye = _frozen_features(system, "B", 512)
    h_aug = torch.cat((xf, torch.ones(xf.shape[0], 1)), dim=-1)
    g = h_aug.T @ h_aug
    lam = 1e-3 * g.diagonal().mean()
    onehot = torch.nn.functional.one_hot(yf, 2).float()
    m = torch.linalg.solve(g + lam * torch.eye(g.shape[0]), h_aug.T @ onehot)
    e_aug = torch.cat((xe, torch.ones(xe.shape[0], 1)), dim=-1)
    acc = ((e_aug @ m).argmax(-1) == ye).float().mean().item()
    print(f"ridge readout on frozen features: Task-B acc {acc:.3f}", flush=True)


def mnist_operating_point() -> None:
    print("== MNIST operating-point alignment (recorded recipe) ==", flush=True)
    print(
        "(Euclid 0.2, sPC 60 steps compiled, 600 batches, width 128, depth 8)",
        flush=True,
    )
    task = create_task("mnist", device=DEVICE, quick_mode=True, num_workers=0)
    task.setup()
    train = [
        (x.view(x.size(0), -1), y)
        for x, y in islice(task.get_dataloader("train"), 600)  # type: ignore[attr-defined]
    ]
    for scheme in ("mupc", "default"):
        torch.manual_seed(0)
        system = compose_system(
            substrate=DigitalSubstrate(SubstrateConfig.digital(device=DEVICE)),
            geometry=FeedforwardGeometry(
                GeometryConfig.feedforward(
                    input_dim=784,
                    output_dim=10,
                    hidden_dims=(128,) * 8,
                    residual=True,
                    init_scheme=scheme,
                )
            ),
            dynamics=PredictiveSettlingDynamics(
                StateDynamicsConfig.predictive_settling(max_steps=60, compiled=True)
            ),
            credit=ThermodynamicContrast(
                CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
            ),
            update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.2)),
        )
        acc = SystemTrainer(
            system=system,
            config=SystemTrainerConfig(max_epochs=1, device=DEVICE, seed=42),
            train_data=train,
        ).fit()[-1]["train_acc"]
        print(
            f"MNIST depth 8 residual {scheme} (recorded op-point): acc {acc:.3f}",
            flush=True,
        )


def main() -> None:
    t0 = time.perf_counter()
    seed_map()
    readout_ceiling()
    mnist_operating_point()
    print(f"total walltime {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
