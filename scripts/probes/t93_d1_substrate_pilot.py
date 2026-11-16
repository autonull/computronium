"""D1 pilot: ternary/memristive + energy_min settling vs digital backprop.

Question (TODO93 §6a track D): on a constrained substrate, does an
energy-minimisation learner reach digital parity at lower state per step?
This probe priced the cell and chose the ladder's LR box before the ladder
was written; it informed `validation/substrate_ladder.py` (D1).

Measured 2026-11-16, CPU, MNIST quick mode, feedforward 784-32-10, batch 32,
600 batches, one epoch, beta 0.5, energy_min settling at 10 steps.

| arm | lr 3e-2 | lr 1e-2 | lr 3e-3 |
|---|---|---|---|
| digital backprop (control) | 0.908 | 0.923 | 0.909 |
| digital eqprop | 0.913 | 0.909 | 0.896 |
| ternary eqprop | 0.477 | 0.381 | 0.802 |
| memristive eqprop | 0.874 | 0.905 | 0.895 |

Findings:

1. LR 1e-2 is live for digital/memristive, but it collapses ternary to
   0.381; ternary peaks at 3e-3. A shared LR would have refused the
   substrate for the LR's defect, so the ladder gives each arm its own
   3-point LR viability ladder (CORRECTION 17).
2. memristive reads 0.905 at 1e-2 against the digital rule's 0.909, i.e.
   parity inside 1 pp at 2 B/weight against 4 B/weight -- the cell to ladder.
3. ternary's best (0.802 at 3e-3) is ~10 pp below the rule's digital point
   at the same LR box; the ladder prices it rather than assuming it.
4. Cost: 13-33 s/epoch at 600 batches, so the 25-cell ladder fits one
   session on CPU.

"""

from __future__ import annotations

import itertools
import time

import torch

from computronium import (
    BackpropCredit,
    CreditAssignmentConfig,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    MemristiveSubstrate,
    NullPlasticity,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    ThermodynamicContrast,
    compose_joint_system,
)
from computronium.domains.base import TaskSplit
from computronium.ontology import TernarySubstrate

INPUT_DIM, NUM_CLASSES, HIDDEN = 784, 10, 32
BATCH, CAP, STEPS, BETA, LR = 32, 600, 10, 0.5, 0.1


class _Cap:
    def __init__(self, loader, cap: int) -> None:
        self._loader, self._cap = loader, cap

    def __iter__(self):
        return itertools.islice(self._loader, self._cap)

    def __len__(self) -> int:
        return min(len(self._loader), self._cap)


def _system(arm: str, lr: float, steps: int = STEPS):
    torch.manual_seed(0)
    substrate = {
        "digital": DigitalSubstrate(SubstrateConfig.digital()),
        "ternary": TernarySubstrate(SubstrateConfig.ternary()),
        "memristive": MemristiveSubstrate(SubstrateConfig.memristive()),
    }[arm.split("_")[0]]
    if arm.endswith("backprop"):
        dynamics, credit = (
            InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
            BackpropCredit(CreditAssignmentConfig.gradient()),
        )
    else:
        dynamics = EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(
                max_steps=steps, beta=BETA, compiled=False
            )
        )
        credit = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
        )
    return compose_joint_system(
        substrate=substrate,
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=INPUT_DIM, output_dim=NUM_CLASSES, hidden_dims=(HIDDEN,)
            )
        ),
        dynamics=dynamics,
        plasticity=NullPlasticity(),
        credit=credit,
        update=EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=lr, grad_clip=1e9)
        ),
    )


def _accuracy(system, loader) -> float:
    correct = total = 0
    with torch.no_grad():
        for x, y in loader:
            logits = system.geometry(x.view(x.size(0), -1))
            correct += int((logits.argmax(-1) == y).sum())
            total += int(y.numel())
    return correct / total


def main() -> None:
    from computronium import create_task

    task = create_task("mnist", device="cpu", quick_mode=True)
    task.setup()
    train = task.get_dataloader(TaskSplit.TRAIN)
    test = task.get_dataloader(TaskSplit.TEST)

    arms = (
        "digital_backprop",
        "digital_eqprop",
        "ternary_eqprop",
        "memristive_eqprop",
    )
    for arm in arms:
        for lr in (0.03, 0.01, 0.003):
            system = _system(arm, lr)
            started = time.perf_counter()
            for x, y in _Cap(train, CAP):
                system.train_step(x.view(x.size(0), -1), y)
            elapsed = time.perf_counter() - started
            print(
                f"{arm:22s} lr={lr:g} acc={_accuracy(system, test):.3f} "
                f"cap={CAP} total={elapsed:6.1f}s",
                flush=True,
            )


if __name__ == "__main__":
    main()
