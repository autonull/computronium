"""D1 defect probe: is the ternary degradation a frozen-scale defect?

The ontology ternary substrate re-derives alpha and the TWN threshold from the
current latent weights on every forward. A quantised function whose scale moves
under the optimizer is a different map at each step -- a candidate mechanism
for ternary's degradation at LR 1e-2. This probe freezes both per layer at
first sight (TWN's published threshold from the init) and re-measures the same
box. It informed ``validation/substrate_ladder.py`` (D1) and rejected the fix.

Measured 2026-11-16, CPU, MNIST quick mode, 784-32-10, batch 32, 600 batches,
energy_min settling at 10 steps, thermodynamic contrast, beta 0.5.

| lr | moving alpha | frozen alpha |
|---|---|---|
| 1e-4 | 0.505 | 0.505 |
| 3e-4 | 0.633 | 0.634 |
| 1e-3 | 0.688 | 0.692 |
| 1e-2 | 0.381 | 0.452 |

Finding: freezing alpha and the threshold moves the cell by at most 7 pp at
LR 1e-2 and by under 0.5 pp where the cell is alive. The moving scale is
**not** the mechanism of the degradation; the mechanism is the 3-level
quantisation's LR sensitivity at this box. No code fix was applied, and the
ladder gives each arm its own LR ladder instead (CORRECTION 17). A frozen-scale
"fix" here would have been a knob sweep passed off as a defect repair.
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
BATCH, CAP, STEP = 32, 600, 0.5


class FrozenAlphaTernary(TernarySubstrate):
    """TWN with alpha and threshold frozen per layer at first sight."""

    def __init__(self, config=None) -> None:
        super().__init__(config)
        self._scale: dict[int, tuple[float, float]] = {}

    def _frozen(self, w: torch.Tensor) -> tuple[float, float]:
        key = id(w)
        if key not in self._scale:
            mean = w.abs().mean().item()
            threshold = 0.7 * mean
            mask = w.abs() > threshold
            alpha = w[mask].abs().mean().item() if mask.any() else mean
            self._scale[key] = (alpha, threshold)
        return self._scale[key]

    def quantize_weights(self, w: torch.Tensor) -> torch.Tensor:
        alpha, threshold = self._frozen(w)
        q = alpha * torch.sign(w) * (w.abs() > threshold).to(w.dtype)
        return q.detach() + (w - w.detach())


class _Cap:
    def __init__(self, loader, cap: int) -> None:
        self._loader, self._cap = loader, cap

    def __iter__(self):
        return itertools.islice(self._loader, self._cap)

    def __len__(self) -> int:
        return min(len(self._loader), self._cap)


def _system(arm: str, lr: float, steps: int = 10):
    torch.manual_seed(0)
    substrate = {
        "digital": DigitalSubstrate(SubstrateConfig.digital()),
        "ternary": TernarySubstrate(SubstrateConfig.ternary()),
        "frozen": FrozenAlphaTernary(SubstrateConfig.ternary()),
    }[arm]
    if arm == "backprop":
        dynamics, credit = (
            InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
            BackpropCredit(CreditAssignmentConfig.gradient()),
        )
    else:
        dynamics = EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(
                max_steps=steps, beta=STEP, compiled=False
            )
        )
        credit = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=STEP)
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

    for arm in ("ternary", "frozen"):
        for lr in (0.0001, 0.0003, 0.001, 0.01):
            system = _system(arm, lr)
            started = time.perf_counter()
            for x, y in _Cap(train, CAP):
                system.train_step(x.view(x.size(0), -1), y)
            print(
                f"{arm:8s} lr={lr:g} acc={_accuracy(system, test):.3f} "
                f"total={time.perf_counter() - started:5.1f}s",
                flush=True,
            )


if __name__ == "__main__":
    main()
