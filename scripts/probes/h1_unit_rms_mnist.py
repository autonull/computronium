"""H1 probe (c) (TODO12b): MNIST-quick bp×unit_rms across the lr grid.

Verdict (2026-09-06): CONFIRMED as a measurement defect (the rule's
code is bitwise-exact — see h1_unit_rms_analytic.py); V1's "convergence
noise floor" is OVERTURNED. unit_rms trains on MNIST-quick at its own
lr scale and BEATS euclid at its working lr; the D16 chance cell was an
lr mislabel, not a broken rule or a noise floor.

Measured (bp, mlp 784-128-10, 150 batches, seed 0, CPU):
- unit_rms lr 0.001 -> 0.900   <- working lr; BEATS euclid's 0.878
- unit_rms lr 0.002 -> 0.872
- unit_rms lr 0.005 -> 0.692
- unit_rms lr 0.01  -> 0.188   (past the stability edge)
- unit_rms lr 0.02  -> 0.104   (the lr pinned by the A6 map: CHANCE)
- unit_rms lr 0.1   -> 0.102
- euclid   lr 0.1   -> 0.878   (control; D16 quoted 0.851, seed noise)

Mechanism: unit_rms's step_size is PER-ELEMENT displacement (the
normalized buffer has RMS 1, so per-tensor ‖Δθ‖ = lr·sqrt(n) — e.g.
316.8·lr at n=100352, constant across steps as observed). The D16/A6
grids borrowed euclid's lr scale; 0.02 on this geometry is a per-element
step 10-20× past its stability edge. The uaxis coverage test's
"unit_rms stays near chance at matched lr" assertion (lr 0.02) encodes
this mislabeled scale and must re-baseline to the working lr 0.001.
"""

import time

import torch
from torch import Tensor

from computronium import (
    BackpropCredit,
    DigitalSubstrate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    compose_system,
    create_task,
)
from computronium.ontology.update import EuclideanUpdate, UnitRMSUpdate

STEPS = 150


def _data() -> tuple[list[tuple[Tensor, Tensor]], list[tuple[Tensor, Tensor]]]:
    task = create_task("mnist", device="cpu", quick_mode=True, num_workers=0)
    task.setup()
    train = [(xb.view(xb.size(0), -1), yb) for xb, yb in task.get_dataloader("train")]
    test = [(xb.view(xb.size(0), -1), yb) for xb, yb in task.get_dataloader("test")]
    return train[:STEPS], test


def _accuracy(system, test) -> float:
    correct = total = 0
    with torch.no_grad():
        for xb, yb in test:
            state = system.dynamics.settle(
                SystemState(x=xb), system.geometry, system.substrate, None
            )
            acts = state.activations
            out = acts[-1] if isinstance(acts, list) else acts
            correct += (out.argmax(1) == yb).sum().item()
            total += yb.size(0)
    return correct / total


def main() -> None:
    t0 = time.perf_counter()
    train, test = _data()
    arms = [("unit_rms", lr) for lr in (0.001, 0.002, 0.005, 0.01)] + [("euclid", 0.1)]
    for rule, lr in arms:
        torch.manual_seed(0)
        from computronium import ParameterUpdateConfig

        system = compose_system(
            substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
            geometry=FeedforwardGeometry(
                GeometryConfig.feedforward(
                    input_dim=784, output_dim=10, hidden_dims=(128,)
                )
            ),
            dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
            credit=BackpropCredit(),
            update=(
                UnitRMSUpdate(
                    ParameterUpdateConfig.unit_rms(step_size=lr, momentum=0.9)
                )
                if rule == "unit_rms"
                else EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=lr))
            ),
        )
        disps: list[float] = []
        for xb, yb in train:
            pre = {k: v.clone() for k, v in system.geometry.params.items()}
            from computronium.core.pipeline import run_train_step

            run_train_step(
                system.substrate,
                system.geometry,
                system.dynamics,
                system.credit,
                system.update,
                xb,
                yb,
            )
            for name, v in system.geometry.params.items():
                g = v - pre[name]
                if g.norm() > 0:
                    # step direction vs pre-update gradient is logged via
                    # displacement consistency; EMA warmup shows in first
                    # steps only, so record per-tensor displacement norm.
                    disps.append(g.norm().item())
                    break
        disp = torch.tensor(disps)
        acc = _accuracy(system, test)
        print(
            f"{rule} lr={lr}: acc={acc:.3f} "
            f"disp first={disp[0].item():.4f} "
            f"disp median={disp.median().item():.4f} "
            f"(== lr post-warmup: {bool((disp[10:] - lr).abs().max() < 1e-5)})"
        )
    print(f"walltime: {time.perf_counter() - t0:.1f}s")


if __name__ == "__main__":
    main()
