"""Temporal-ψ readout migration demo (D21, TODO19 rounds 7-8).

The frozen-backbone task-switching result, wired through the CORE
plasticity config surface: a MNIST backbone (784-64-2, gradient credit)
is trained on digit>=5 and then bitwise-frozen; the ψ laws — instantiated
from ``PlasticityConfig.temporal_psi`` / ``.conflict_adaptive`` through
the system-trainer dispatch — adapt the readout on an alternating
parity / INVERTED-parity stream. Demonstrates the round-7/8 governed
results at demo scale:

- temporal (ρ<1) migrates between the conflicting mappings;
- closed-form (ρ=1) blends them and collapses on the inverted phase;
- the conflict-adaptive law self-switches ρ with no boundaries handed in.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import torch
from torch import Tensor

from computronium import (
    CreditAssignmentConfig,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    compose_system_from_configs,
)
from computronium.core.pipeline import forward_pass, run_train_step
from computronium.core.plasticity.adaptive_psi import ConflictAdaptivePsiPlasticity
from computronium.core.plasticity.temporal_psi import TemporalPsiPlasticity

if TYPE_CHECKING:
    from computronium.state.transitions import PlasticityConfig

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class MigrationDemoConfig:
    """Demo scale: one seed, small backbone, three stream phases."""

    stage_a_episodes: int = 250
    phase_episodes: int = 60
    batch_size: int = 64
    probe_batches: int = 10
    hidden_dim: int = 64
    lr: float = 0.1
    ridge_lambda: float = 1e-3
    seed: int = 0
    train_pool: int = 10_000


@dataclass(frozen=True, slots=True)
class MigrationTask:
    """MNIST batches under the digit>=5 backbone task and parity phases."""

    xtr: Tensor
    ytr: Tensor
    xte: Tensor
    yte: Tensor

    @classmethod
    def load(cls, config: MigrationDemoConfig) -> MigrationTask:
        from torchvision import transforms
        from torchvision.datasets import MNIST

        def stack(train: bool) -> tuple[Tensor, Tensor]:
            ds = MNIST(
                str(REPO_ROOT / "data"),
                train=train,
                download=False,
                transform=transforms.ToTensor(),
            )
            xs = torch.stack([ds[i][0] for i in range(len(ds))]).float()
            ys = torch.tensor([int(ds[i][1]) for i in range(len(ds))])
            return xs.view(len(ds), -1), ys

        xtr, ytr = stack(True)
        xte, yte = stack(False)
        gen = torch.Generator().manual_seed(1234)
        pool = torch.randperm(len(xtr), generator=gen)[: config.train_pool]
        return cls(xtr[pool], ytr[pool], xte, yte)


def _parity(y: Tensor, flip: int) -> Tensor:
    return (y % 2 == 0).long() ^ flip


class _Stream:
    """Batch streams over one task instance with a per-call generator."""

    def __init__(self, task: MigrationTask, seed: int) -> None:
        self.task = task
        self.gen = torch.Generator().manual_seed(seed)

    def batch(self, flip: int, batch_size: int) -> tuple[Tensor, Tensor]:
        task = self.task
        idx = torch.randint(0, len(task.xtr), (batch_size,), generator=self.gen)
        return task.xtr[idx], _parity(task.ytr[idx], flip)

    def digit_batches(self, batch_size: int) -> tuple[Tensor, Tensor]:
        task = self.task
        idx = torch.randint(0, len(task.xtr), (batch_size,), generator=self.gen)
        return task.xtr[idx], (task.ytr[idx] >= 5).long()

    def probe(self, flip: int, batches: int, batch_size: int):
        task = self.task
        idx = torch.randperm(len(task.xte), generator=self.gen)[
            : batches * batch_size
        ].view(batches, batch_size)
        return [(task.xte[i], _parity(task.yte[i], flip)) for i in idx]


def build_backbone(config: MigrationDemoConfig, task: MigrationTask):
    """Train the digit>=5 backbone; return (system, mastery)."""
    system = compose_system_from_configs(
        SubstrateConfig.digital(),
        GeometryConfig.feedforward(
            input_dim=784, output_dim=2, hidden_dims=(config.hidden_dim,)
        ),
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=config.lr),
    )
    stream = _Stream(task, config.seed)
    for _ in range(config.stage_a_episodes):
        x, y = stream.digit_batches(config.batch_size)
        run_train_step(
            system.substrate,
            system.geometry,
            system.dynamics,
            system.credit,
            system.update,
            x,
            y,
        )
    return system, stream


def _settled(system, x: Tensor):
    state = SystemState(x=x)
    state.activations = forward_pass(system.substrate, system.geometry, x)
    return system.dynamics.settle(state, system.geometry, system.substrate, target=None)


def _out(acts) -> Tensor:
    return acts[-1] if isinstance(acts, list) else acts


def probe_accuracy(
    system,
    plasticity,
    psi: dict[str, Tensor],
    stream: _Stream,
    config: MigrationDemoConfig,
    flip: int,
) -> float:
    correct = total = 0
    with torch.no_grad():
        for x, y in stream.probe(flip, config.probe_batches, config.batch_size):
            acts = plasticity.modulate(_settled(system, x).activations, psi)
            correct += (_out(acts).argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def run_stream(
    system,
    plasticity: TemporalPsiPlasticity | ConflictAdaptivePsiPlasticity,
    stream: _Stream,
    config: MigrationDemoConfig,
    phases: tuple[int, ...] = (0, 1),
) -> dict[str, object]:
    """Run the alternating parity stream under a frozen θ; per-phase readouts."""
    from computronium.state.composite import CompositeState

    for p in system.geometry.params.values():
        p.requires_grad_(False)
    psi: dict[str, Tensor] = {}
    phase_accs: list[float] = []
    rho_used: list[float] = []
    for flip in phases:
        for _ in range(config.phase_episodes):
            x, y = stream.batch(flip, config.batch_size)
            with torch.no_grad():
                acts = _settled(system, x).activations
                act_list = acts if isinstance(acts, list) else [acts]
                activity = {
                    "x": x,
                    "h": act_list[-2],
                    "y": _out(acts),
                    "target": y,
                }
                z = CompositeState(activity=activity, plastic={}, substrate={})
                psi = plasticity.step(psi, z, None)  # type: ignore[arg-type]
                if "rho_used" in psi:
                    rho_used.append(psi["rho_used"].item())
        phase_accs.append(probe_accuracy(system, plasticity, psi, stream, config, flip))
    return {
        "phase_accs": phase_accs,
        "rho_used": rho_used,
        "psi": psi,
    }


def frozen_null_accuracy(
    system, stream: _Stream, config: MigrationDemoConfig, flip: int
) -> float:
    correct = total = 0
    with torch.no_grad():
        for x, y in stream.probe(flip, config.probe_batches, config.batch_size):
            acts = _settled(system, x).activations
            correct += (_out(acts).argmax(-1) == y).sum().item()
            total += len(y)
    return correct / total


def plasticity_from_config(
    config: PlasticityConfig,
) -> TemporalPsiPlasticity | ConflictAdaptivePsiPlasticity:
    """Instantiate the ψ law through the core trainer-path dispatch."""
    from computronium.core.system_trainer.spec import _plasticity_from_config

    law = _plasticity_from_config(config)
    if not isinstance(law, (TemporalPsiPlasticity, ConflictAdaptivePsiPlasticity)):
        raise TypeError(f"unexpected plasticity law for {config.plasticity_type}")
    return law


__all__ = [
    "MigrationDemoConfig",
    "MigrationTask",
    "build_backbone",
    "frozen_null_accuracy",
    "plasticity_from_config",
    "probe_accuracy",
    "run_stream",
]
