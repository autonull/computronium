"""P2 pilot: the memory frontier at one binding operating point (TODO93 T6).

The frontier's claim needs one measured operating point before it can be
registered. This module is that pilot: four arms at one point, two positive
controls, and the binding arithmetic the registration is written from.

The pilot is a *screen* (rung 0-2), not a claim. Its accuracy rows are
coordinates at ``steps`` steps, and the claim seeds are disjoint from the pilot
seeds by construction (:data:`PILOT_SEEDS`, :data:`LADDER_SEEDS`,
:data:`CLAIM_SEEDS`).

**The point.** ``c = 4.1`` per layer per batch per width (measured, T4a), so
``L=64/B=8192/W=1024`` needs 8.2 GiB of activations and does not fit an 8 GiB
card with 20 % headroom. The affordable point is L=32 at B=8192, which is what
:class:`PilotPoint` defaults to; :func:`claim_ladder` prices every registered
cell the same way.

**Controls.** The instrument control re-measures ``c`` at the pilot width and
batch from two depth deltas -- the appendix's coefficient must survive the
geometry it is priced at. The learning control asks whether plain backprop at
L=8 reaches the checkpointed arm's accuracy minus the floor at the same point;
a memory number from a stack that does not learn is not a frontier.

**Rulers.** Peak and its decomposition come from ``EpochResource``; walltime is
the epoch's own clock; forward-equivalents are measured against one forward pass
of the same batch (the FLOP counter is structure-derived, so it cannot see the
hybrid trunk's second pass and is reported only as a footnote).
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean, stdev
from types import MappingProxyType
from typing import TYPE_CHECKING

import torch

from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.core.system_trainer._resources import binding_verdict
from computronium.core.system_trainer.spec import compose_system_from_configs
from computronium.ontology import (
    CreditAssignmentConfig,
    GeometryConfig,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Mapping

    from computronium.ontology import System

logger = logging.getLogger(__name__)

__all__ = [
    "ADMISSION_BUDGET_MB",
    "ARMS",
    "CLAIM_SEEDS",
    "DECLARED_C",
    "FLOOR_MARGIN",
    "FROZEN_LR",
    "LADDER_SEEDS",
    "LR_LADDER",
    "PILOT_SEEDS",
    "STREAM_LR_LADDER",
    "DepthCell",
    "DepthRung",
    "PilotPoint",
    "PilotReport",
    "claim_ladder",
    "depth_rung",
    "run_learning_ladder",
    "run_pilot",
]

#: Activation coefficient measured on the claim geometry (TODO93 §4.1, T4a).
DECLARED_C = 4.1
#: The claim card, and the headroom the admission check must leave free.
CARD_MB = 8192.0
HEADROOM = 0.20
ADMISSION_BUDGET_MB = CARD_MB * (1.0 - HEADROOM)
#: ISO date the pilot arms were measured; the appendix rows carry it.
PILOT_DATE = "2026-11-16"

TRAIN_SUBSET = 10_000
#: CIFAR-10's test split holds 10k images; the full split is the ruler.
TEST_SAMPLES = 10_000
INPUT_DIM = 3 * 32 * 32
CLASSES = 10

#: Three disjoint seed sets: without the split, the floor is a peek.
PILOT_SEEDS = (11, 12, 13)
LADDER_SEEDS = (21, 22, 23)
CLAIM_SEEDS = (101, 102, 103, 104, 105)
DATA_SEED = 7

ARMS = ("backprop", "backprop+ckpt", "hybrid", "local")
LR_LADDER = (0.1, 0.3, 1.0)
#: The learning control's bar: the shallow checkpointed arm minus this margin.
FLOOR_MARGIN = 0.01
#: Best point of the L=8 ladder per arm; frozen before the claim seeds run.
FROZEN_LR: Mapping[str, float] = MappingProxyType({
    "backprop": 0.3,
    "backprop+ckpt": 0.3,
    "hybrid": 0.3,
    "local": 0.3,
})
_GAMMA = 0.05


@dataclass(frozen=True, slots=True)
class PilotPoint:
    """One operating point: depth, width, batch, and the step budget.

    ``depth`` counts Linear layers, as the geometry does (``depth-1`` hidden
    dims). ``steps`` is the training budget every arm shares; ``steps`` is
    divided by ``batches_per_epoch`` to get the epoch count the trainer needs,
    so the protocol is a step count, not a scheme-dependent "epoch".
    """

    depth: int = 32
    width: int = 1024
    batch: int = 8192
    steps: int = 200
    batches_per_epoch: int = 2
    stream_norm: bool = False
    input_dim: int = INPUT_DIM
    classes: int = CLASSES

    def __post_init__(self) -> None:
        if self.depth < 2:
            msg = f"depth must cover at least one hidden and one readout layer, got {self.depth}"
            raise ValueError(msg)
        if self.steps < self.batches_per_epoch:
            msg = f"steps={self.steps} is below batches_per_epoch={self.batches_per_epoch}"
            raise ValueError(msg)

    @property
    def hidden_dims(self) -> tuple[int, ...]:
        return (self.width,) * (self.depth - 1)

    @property
    def epochs(self) -> int:
        return max(1, self.steps // self.batches_per_epoch)

    def weight_count(self) -> int:
        """Weights and biases of the dense stack, excluding nothing."""
        first = self.input_dim * self.width + self.width
        middle = (self.depth - 2) * (self.width * self.width + self.width)
        readout = self.width * self.classes + self.classes
        return first + middle + readout

    def params_mb(self) -> float:
        return self.weight_count() * 4 / 2**20

    def activation_mb(
        self, *, c: float = DECLARED_C, depth: int | None = None
    ) -> float:
        """``c·L·B·W·4`` in MiB; the appendix's arithmetic, one expression."""
        layers = self.depth if depth is None else depth
        return c * layers * self.batch * self.width * 4 / 2**20

    def peak_mb(self, *, c: float = DECLARED_C) -> float:
        """Activations plus parameters plus one momentum buffer (measured 2×)."""
        return self.activation_mb(c=c) + 2 * self.params_mb()

    def affordable(
        self,
        *,
        c: float = DECLARED_C,
        budget_mb: float = ADMISSION_BUDGET_MB,
    ) -> bool:
        """Whether the plain-backprop arm fits the budget at this point."""
        return self.peak_mb(c=c) <= budget_mb

    def scaled(
        self,
        *,
        depth: int,
        batch: int | None = None,
        stream_norm: bool | None = None,
    ) -> PilotPoint:
        return PilotPoint(
            depth=depth,
            width=self.width,
            batch=self.batch if batch is None else batch,
            steps=self.steps,
            batches_per_epoch=self.batches_per_epoch,
            stream_norm=self.stream_norm if stream_norm is None else stream_norm,
            input_dim=self.input_dim,
            classes=self.classes,
        )


def _ladder_cell(point: PilotPoint, *, c: float = DECLARED_C) -> dict[str, object]:
    """One registered cell with its arithmetic, admission, and runnability."""
    runnable = point.batch <= TRAIN_SUBSET
    return {
        "depth": point.depth,
        "batch": point.batch,
        "width": point.width,
        "steps": point.steps,
        "activations_mb": round(point.activation_mb(c=c), 1),
        "peak_mb": round(point.peak_mb(c=c), 1),
        "affordable": point.affordable(c=c),
        "runnable": runnable,
        "skipped_reason": ""
        if runnable
        else f"batch exceeds the fixed {TRAIN_SUBSET}-image train subset",
    }


def claim_ladder(*, c: float = DECLARED_C) -> tuple[dict[str, object], ...]:
    """The registered ladder: the affordable points from §4.1, not the grid.

    ``B=16384`` is priced because §4.1 names it, but the fixed 10k-image train
    subset cannot fill a 16k batch, so that cell is registered as skipped rather
    than silently dropped. ``L=64`` at ``B=8192`` is priced and refused: 8.2 GiB
    of activations exceeds the card's admission budget.
    """
    return (
        _ladder_cell(PilotPoint(depth=8, batch=8192), c=c),
        _ladder_cell(PilotPoint(depth=16, batch=8192), c=c),
        _ladder_cell(PilotPoint(depth=32, batch=8192), c=c),
        _ladder_cell(PilotPoint(depth=16, batch=16384), c=c),
        _ladder_cell(PilotPoint(depth=64, batch=8192), c=c),
    )


class _Batches:
    """A fixed, re-iterable batch list (the trainer moves each batch)."""

    def __init__(self, x: torch.Tensor, y: torch.Tensor, batch: int) -> None:
        self._pairs = [
            (x[i : i + batch], y[i : i + batch]) for i in range(0, x.shape[0], batch)
        ]

    def __iter__(self) -> Iterator[tuple[torch.Tensor, torch.Tensor]]:
        return iter(self._pairs)

    def __len__(self) -> int:
        return len(self._pairs)


def _cifar() -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """The fixed 10k-image train subset and the full test split, as tensors.

    The subset is shuffled once under :data:`DATA_SEED` so the fixed order is
    declared, not inherited from the archive's class layout.
    """
    from computronium.data.vision import get_vision_dataset

    train = get_vision_dataset("cifar10", train=True, flatten=True)
    test = get_vision_dataset("cifar10", train=False, flatten=True)
    perm = torch.randperm(
        TRAIN_SUBSET, generator=torch.Generator().manual_seed(DATA_SEED)
    )
    indices = perm.tolist()
    x_train = torch.stack([train[i][0] for i in indices])
    y_train = torch.tensor([train[i][1] for i in indices])
    x_test = torch.stack([test[i][0] for i in range(TEST_SAMPLES)])
    y_test = torch.tensor([test[i][1] for i in range(TEST_SAMPLES)])
    return x_train, y_train, x_test, y_test


def _credit(arm: str) -> CreditAssignmentConfig:
    match arm:
        case "backprop" | "backprop+ckpt":
            return CreditAssignmentConfig.gradient()
        case "hybrid":
            return CreditAssignmentConfig.hybrid(gamma=_GAMMA)
        case "local":
            return CreditAssignmentConfig.pepita(gamma=_GAMMA)
        case other:
            msg = f"unknown arm {other!r}; expected one of {ARMS}"
            raise ValueError(msg)


def build_arm(arm: str, point: PilotPoint, *, lr: float, seed: int) -> System:
    """One arm at one point; the geometry, init, and update are shared.

    ``point.stream_norm`` is the depth rung's declared pass (TODO93 T6c): the
    stack's post-activations are rescaled to length sqrt(width) so the
    signal does not die with depth. It is a run setting, not a new
    primitive, and the plain arm's cells stay bit-identical.
    """
    if arm not in ARMS:
        msg = f"unknown arm {arm!r}; expected one of {ARMS}"
        raise ValueError(msg)
    torch.manual_seed(seed)
    system = compose_system_from_configs(
        substrate=SubstrateConfig.digital(),
        geometry=GeometryConfig.feedforward(
            input_dim=point.input_dim,
            output_dim=point.classes,
            hidden_dims=point.hidden_dims,
            stream_norm=point.stream_norm,
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        credit=_credit(arm),
        update=ParameterUpdateConfig.euclidean(step_size=lr),
    )
    if arm == "backprop+ckpt":
        system.geometry.set_gradient_checkpointing(max(1, math.isqrt(point.depth)))
    return system


def _accuracy(system: System, x: torch.Tensor, y: torch.Tensor, device: str) -> float:
    correct = 0
    with torch.no_grad():
        for i in range(0, x.shape[0], 1024):
            logits = system.geometry.forward(x[i : i + 1024].to(device))
            correct += int((logits.argmax(dim=1) == y[i : i + 1024].to(device)).sum())
    return correct / x.shape[0]


def _forward_seconds(system: System, x: torch.Tensor) -> float:
    """One forward pass of the full batch, warm, synchronised."""
    system.geometry.eval()
    with torch.no_grad():
        system.geometry.forward(x)
        torch.cuda.synchronize()
        started = time.perf_counter()
        for _ in range(3):
            system.geometry.forward(x)
        torch.cuda.synchronize()
    system.geometry.train()
    return (time.perf_counter() - started) / 3


@dataclass(frozen=True, slots=True)
class ArmCell:
    """One (arm, seed) cell: what it scored and what it cost."""

    arm: str
    seed: int
    depth: int
    batch: int
    steps: int
    lr: float
    val_acc: float
    walltime_s: float
    forward_equivalents: float
    peak_mb: float | None
    params_mb: float | None
    optimizer_mb: float | None
    activations_mb: float | None
    auxiliary_mb: float | None
    activation_share: float | None
    binding: bool | None

    @property
    def step_time_s(self) -> float:
        return self.walltime_s / self.steps


@dataclass(frozen=True, slots=True)
class ArmRow:
    """Per-arm mean and spread over the pilot seeds."""

    arm: str
    n: int
    val_acc: float
    val_acc_sd: float
    walltime_s: float
    forward_equivalents: float
    peak_mb: float | None
    activations_mb: float | None
    activation_share: float | None
    binding: bool | None


@dataclass(frozen=True, slots=True)
class CalibrationRow:
    """One depth of the instrument control, with its implied coefficient.

    ``implied_c`` is the coefficient of the segment ending at this depth: the
    depth delta cancels the batch-independent cuBLAS workspace floor, which is
    what makes this a calibration rather than a coincidence. The shallowest row
    has no segment and therefore no coefficient.
    """

    depth: int
    activations_mb: float
    implied_c: float | None


@dataclass(frozen=True, slots=True)
class LearningControl:
    """Does plain backprop reach the checkpointed arm's floor at L=8?"""

    depth: int
    steps: int
    backprop_acc: float
    checkpointed_acc: float
    floor: float
    margin: float
    passed: bool


@dataclass(frozen=True, slots=True)
class PilotReport:
    """The pilot's measured appendix: controls, rows, and the point they ran at."""

    point: PilotPoint
    measured_c: float
    c_spread: float
    calibration: tuple[CalibrationRow, ...]
    learning: LearningControl
    cells: tuple[ArmCell, ...]
    arms: tuple[ArmRow, ...]
    lrs: Mapping[str, float]
    date: str = PILOT_DATE

    @property
    def instrument_control_passed(self) -> bool:
        return (
            self.c_spread < 0.10
            and abs(self.measured_c - DECLARED_C) / DECLARED_C < 0.10
        )

    @property
    def controls_passed(self) -> bool:
        return self.instrument_control_passed and self.learning.passed

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date,
            "point": asdict(self.point),
            "declared_c": DECLARED_C,
            "measured_c": self.measured_c,
            "c_spread": self.c_spread,
            "instrument_control_passed": self.instrument_control_passed,
            "learning_control": asdict(self.learning),
            "controls_passed": self.controls_passed,
            "lrs": dict(self.lrs),
            "calibration": [asdict(row) for row in self.calibration],
            "cells": [asdict(cell) for cell in self.cells],
            "arms": [asdict(row) for row in self.arms],
        }

    def appendix_rows(self) -> list[dict[str, object]]:
        """The rows BENCHMARKS.md carries, one per arm, at the pilot point."""
        return [
            {
                "arm": row.arm,
                "val_acc": round(row.val_acc, 3),
                "val_acc_sd": round(row.val_acc_sd, 3),
                "activations_mb": None
                if row.activations_mb is None
                else round(row.activations_mb),
                "peak_mb": None if row.peak_mb is None else round(row.peak_mb),
                "activation_share": None
                if row.activation_share is None
                else round(row.activation_share, 3),
                "binding": row.binding,
                "forward_equivalents": round(row.forward_equivalents, 2),
                "walltime_s": round(row.walltime_s, 2),
                "n": row.n,
            }
            for row in self.arms
        ]

    def write(self, output_dir: Path) -> Path:
        """Write ``results.json`` and an ``appendix.md`` table; return the JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "results.json"
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        lines = [
            f"# Memory frontier pilot ({self.date})",
            "",
            f"Point: L={self.point.depth}, B={self.point.batch}, W={self.point.width}, "
            f"steps={self.point.steps}, fp32, CIFAR-10 10k subset / full test.",
            f"Measured c = {self.measured_c:.2f} (spread {self.c_spread:.1%}); "
            f"instrument control {'PASS' if self.instrument_control_passed else 'FAIL'}; "
            f"learning control {'PASS' if self.learning.passed else 'FAIL'} "
            f"(backprop {self.learning.backprop_acc:.3f} vs floor {self.learning.floor:.3f}).",
            "",
            "| Arm | n | val_acc | σ | Activations MB | Peak MB | Share | Binding | Fwd-eq | Walltime s |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for row in self.appendix_rows():
            lines.append(
                f"| `{row['arm']}` | {row['n']} | {row['val_acc']} | {row['val_acc_sd']} | "
                f"{row['activations_mb']} | {row['peak_mb']} | {row['activation_share']} | "
                f"{row['binding']} | {row['forward_equivalents']} | {row['walltime_s']} |"
            )
        (output_dir / "appendix.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        return path


def _measure(
    arm: str,
    point: PilotPoint,
    *,
    lr: float,
    seed: int,
    device: str,
    x_train: torch.Tensor,
    y_train: torch.Tensor,
    x_test: torch.Tensor,
    y_test: torch.Tensor,
) -> ArmCell:
    """Train one (arm, seed) cell and return its measured cost and accuracy."""
    torch.cuda.empty_cache()
    system = build_arm(arm, point, lr=lr, seed=seed)
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=point.epochs,
            batch_size=point.batch,
            limit_train_batches=point.batches_per_epoch,
            device=device,
            seed=seed,
            track_memory=True,
            track_flops=True,
            log_every_n_epochs=0,
        ),
        train_data=_Batches(x_train, y_train, point.batch),
    )
    started = time.perf_counter()
    trainer.fit()
    walltime = time.perf_counter() - started
    cost = max(
        trainer.epoch_resources,
        key=lambda resource: resource.peak_memory_mb or 0.0,
    )
    batch = x_train[: point.batch].to(device)
    forward_s = _forward_seconds(system, batch)
    forward_equivalents = (walltime / trainer.global_step) / forward_s
    return ArmCell(
        arm=arm,
        seed=seed,
        depth=point.depth,
        batch=point.batch,
        steps=trainer.global_step,
        lr=lr,
        val_acc=_accuracy(system, x_test, y_test, device),
        walltime_s=walltime,
        forward_equivalents=forward_equivalents,
        peak_mb=cost.peak_memory_mb,
        params_mb=cost.params_mb,
        optimizer_mb=cost.optimizer_mb,
        activations_mb=cost.activations_mb,
        auxiliary_mb=cost.auxiliary_mb,
        activation_share=cost.activation_share,
        binding=binding_verdict(cost),
    )


def _summarise(cells: Iterable[ArmCell]) -> tuple[ArmRow, ...]:
    grouped: dict[str, list[ArmCell]] = {}
    for cell in cells:
        grouped.setdefault(cell.arm, []).append(cell)
    rows = []
    for arm, arm_cells in grouped.items():
        accs = [cell.val_acc for cell in arm_cells]
        verdicts = [cell.binding for cell in arm_cells]
        rows.append(
            ArmRow(
                arm=arm,
                n=len(arm_cells),
                val_acc=fmean(accs),
                val_acc_sd=stdev(accs) if len(accs) > 1 else 0.0,
                walltime_s=fmean(cell.walltime_s for cell in arm_cells),
                forward_equivalents=fmean(
                    cell.forward_equivalents for cell in arm_cells
                ),
                peak_mb=_mean(cell.peak_mb for cell in arm_cells),
                activations_mb=_mean(cell.activations_mb for cell in arm_cells),
                activation_share=_mean(cell.activation_share for cell in arm_cells),
                binding=None
                if any(verdict is None for verdict in verdicts)
                else all(verdicts),
            )
        )
    return tuple(rows)


def _mean(values: Iterable[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return fmean(present) if present else None


def _layers_mb(point: PilotPoint, depth: int) -> float:
    """One layer's activations at this batch and width: ``L·B·W·4`` per layer."""
    return depth * point.batch * point.width * 4 / 2**20


def _calibrate(
    point: PilotPoint,
    *,
    device: str,
    seed: int,
    x_train: torch.Tensor,
    y_train: torch.Tensor,
    x_test: torch.Tensor,
    y_test: torch.Tensor,
) -> tuple[float, float, tuple[CalibrationRow, ...]]:
    """Re-measure ``c`` from two depth deltas at the pilot width and batch.

    Two equal-layer deltas give two independent coefficients; their spread is
    the control's tolerance, and the floor cancels in each delta.
    """
    depths = tuple(
        sorted({max(2, point.depth // 4), max(3, point.depth // 2), point.depth})
    )
    activations: list[float] = []
    for depth in depths:
        cell = _measure(
            "backprop",
            point.scaled(depth=depth),
            lr=FROZEN_LR["backprop"],
            seed=seed,
            device=device,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )
        if cell.activations_mb is None:
            msg = "instrument control needs a measured CUDA activation term"
            raise RuntimeError(msg)
        activations.append(cell.activations_mb)
    analytic = [_layers_mb(point, depth) for depth in depths]
    coefficients = [
        (deep - shallow) / (deep_analytic - shallow_analytic)
        for shallow, deep, shallow_analytic, deep_analytic in zip(
            activations[:-1], activations[1:], analytic[:-1], analytic[1:], strict=True
        )
    ]
    rows = (
        CalibrationRow(depth=depths[0], activations_mb=activations[0], implied_c=None),
        *(
            CalibrationRow(
                depth=depth, activations_mb=activation, implied_c=coefficient
            )
            for depth, activation, coefficient in zip(
                depths[1:], activations[1:], coefficients, strict=True
            )
        ),
    )
    measured = fmean(coefficients)
    spread = abs(coefficients[0] - coefficients[1]) / max(coefficients)
    return measured, spread, rows


def _learning_control(
    point: PilotPoint,
    *,
    device: str,
    seed: int,
    x_train: torch.Tensor,
    y_train: torch.Tensor,
    x_test: torch.Tensor,
    y_test: torch.Tensor,
) -> LearningControl:
    """Floor = checkpointed accuracy at L=8 − 1 pp; backprop must reach it."""
    shallow = point.scaled(depth=8)
    measured = {
        arm: _measure(
            arm,
            shallow,
            lr=FROZEN_LR[arm],
            seed=seed,
            device=device,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        ).val_acc
        for arm in ("backprop", "backprop+ckpt")
    }
    floor = measured["backprop+ckpt"] - FLOOR_MARGIN
    return LearningControl(
        depth=8,
        steps=shallow.steps,
        backprop_acc=measured["backprop"],
        checkpointed_acc=measured["backprop+ckpt"],
        floor=floor,
        margin=measured["backprop"] - floor,
        passed=measured["backprop"] >= floor,
    )


def run_pilot(
    point: PilotPoint | None = None,
    *,
    seeds: tuple[int, ...] = PILOT_SEEDS,
    device: str = "cuda",
    output_dir: Path | None = None,
) -> PilotReport:
    """Run the pilot: both controls, then every arm at the binding point.

    Args:
        point: The operating point; defaults to the affordable claim point.
        seeds: Pilot seeds (disjoint from :data:`CLAIM_SEEDS`).
        device: ``"cuda"`` is required -- CPU runs measure RSS, not the peak the
            decomposition decomposes.
        output_dir: Where ``results.json`` and ``appendix.md`` are written.

    Returns:
        The measured report, controls included.

    Raises:
        RuntimeError: On a non-CUDA device, or when the point is unaffordable.
    """
    point = point or PilotPoint()
    if device != "cuda" and not device.startswith("cuda:"):
        raise RuntimeError("the memory frontier pilot needs a CUDA peak measurement")
    if not point.affordable():
        raise RuntimeError(
            f"point L={point.depth}/B={point.batch}/W={point.width} needs "
            f"{point.peak_mb():.0f} MB > budget {ADMISSION_BUDGET_MB:.0f} MB"
        )
    torch.manual_seed(DATA_SEED)
    torch.manual_seed(DATA_SEED)
    x_train, y_train, x_test, y_test = _cifar()
    measured_c, spread, calibration = _calibrate(
        point,
        device=device,
        seed=PILOT_SEEDS[0],
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )
    learning = _learning_control(
        point,
        device=device,
        seed=LADDER_SEEDS[0],
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )
    cells = tuple(
        _measure(
            arm,
            point,
            lr=FROZEN_LR[arm],
            seed=seed,
            device=device,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )
        for arm in ARMS
        for seed in seeds
    )
    report = PilotReport(
        point=point,
        measured_c=measured_c,
        c_spread=spread,
        calibration=calibration,
        learning=learning,
        cells=cells,
        arms=_summarise(cells),
        lrs=dict(FROZEN_LR),
    )
    if output_dir is not None:
        report.write(output_dir)
    return report


def run_learning_ladder(
    *,
    depth: int = 8,
    seeds: tuple[int, ...] = LADDER_SEEDS[:1],
    device: str = "cuda",
) -> dict[str, dict[str, float]]:
    """The per-arm LR viability ladder at L=8: three points, one seed each.

    Returns:
        ``{arm: {lr: val_acc}}`` for every arm and ladder point.
    """
    point = PilotPoint(depth=depth)
    x_train, y_train, x_test, y_test = _cifar()
    results: dict[str, dict[str, float]] = {}
    for arm in ARMS:
        results[arm] = {}
        for lr in LR_LADDER:
            cells = [
                _measure(
                    arm,
                    point,
                    lr=lr,
                    seed=seed,
                    device=device,
                    x_train=x_train,
                    y_train=y_train,
                    x_test=x_test,
                    y_test=y_test,
                )
                for seed in seeds
            ]
            results[arm][str(lr)] = fmean(cell.val_acc for cell in cells)
    return results


STREAM_LR_LADDER = (3e-3, 1e-2, 3e-2)
"""The normalized stack's own LR box (TODO93 T6c), pre-registered.

The plain ladder's 0.1/0.3/1.0 edges diverge under unit-scale streams
(measured 2026-11-16: L=8 at 0.3 reads loss 3.4), so the depth rung's knob
is this interior box, not the arm's frozen LR.
"""


@dataclass(frozen=True, slots=True)
class DepthCell:
    """One rung cell: a depth, the pass, the LR, and what it scored."""

    depth: int
    stream_norm: bool
    lr: float
    seed: int
    val_acc: float
    activations_mb: float | None


@dataclass(frozen=True, slots=True)
class DepthRung:
    """The depth rung: the plain plateau against the normalized pass.

    The plain stack at the claim depth is pinned at chance (measured 0.100
    from step 200 on); the normalized pass must reach the shallow arm's
    floor to unblock the depth claim (TODO93 T6c). The floor is the learning
    control's, not a second definition of it.
    """

    floor: float
    plain: tuple[DepthCell, DepthCell]
    normalized_shallow: DepthCell
    normalized: tuple[DepthCell, ...]
    confirmation: DepthCell

    @property
    def plateaued(self) -> bool:
        """The plain claim-depth cell sits below the shallow floor."""
        return self.plain[-1].val_acc < self.floor

    @property
    def best(self) -> DepthCell:
        """The ladder's best deep point; a tie keeps the smaller LR."""
        return max(self.normalized, key=lambda cell: cell.val_acc)

    @property
    def left_the_plateau(self) -> bool:
        """The best deep point is above the plain claim-depth cell."""
        return self.best.val_acc > self.plain[-1].val_acc

    @property
    def reaches_floor(self) -> bool:
        """Both seeds of the best point, and its shallow cell, clear the floor."""
        return (
            self.normalized_shallow.val_acc >= self.floor
            and self.best.val_acc >= self.floor
            and self.confirmation.val_acc >= self.floor
        )

    @property
    def activation_ratio(self) -> float | None:
        """Best deep cell / plain claim-depth cell, in activation bytes."""
        plain = self.plain[-1].activations_mb
        best = self.best.activations_mb
        if not plain or best is None:
            return None
        return best / plain


def _depth_cell(cell: ArmCell, *, stream_norm: bool) -> DepthCell:
    return DepthCell(
        depth=cell.depth,
        stream_norm=stream_norm,
        lr=cell.lr,
        seed=cell.seed,
        val_acc=cell.val_acc,
        activations_mb=cell.activations_mb,
    )


def depth_rung(
    point: PilotPoint | None = None,
    *,
    seeds: tuple[int, ...] = LADDER_SEEDS,
    device: str = "cuda",
) -> DepthRung:
    """Measure the depth rung at one box: plateau, lift, and floor (T6c).

    Cells: the plain stack at L=8 and the claim depth, the floor from the
    learning control, the normalized pass's own LR ladder at the claim depth,
    its shallow cell at the best LR, and a confirmation seed at that point.

    Raises:
        RuntimeError: On a non-CUDA device.
    """
    point = point or PilotPoint()
    if device != "cuda" and not device.startswith("cuda:"):
        raise RuntimeError("the depth rung needs a CUDA peak measurement")
    x_train, y_train, x_test, y_test = _cifar()

    def cell(
        depth: int, *, lr: float, seed: int, stream_norm: bool = False
    ) -> DepthCell:
        measured = _measure(
            "backprop",
            point.scaled(depth=depth, stream_norm=stream_norm),
            lr=lr,
            seed=seed,
            device=device,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )
        return _depth_cell(measured, stream_norm=stream_norm)

    learning = _learning_control(
        point,
        device=device,
        seed=seeds[0],
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )
    plain = (
        cell(8, lr=FROZEN_LR["backprop"], seed=seeds[0]),
        cell(point.depth, lr=FROZEN_LR["backprop"], seed=seeds[0]),
    )
    normalized = tuple(
        cell(point.depth, lr=lr, seed=seeds[0], stream_norm=True)
        for lr in STREAM_LR_LADDER
    )
    best = max(normalized, key=lambda candidate: candidate.val_acc)
    return DepthRung(
        floor=learning.floor,
        plain=plain,
        normalized_shallow=cell(8, lr=best.lr, seed=seeds[0], stream_norm=True),
        normalized=normalized,
        confirmation=cell(point.depth, lr=best.lr, seed=seeds[-1], stream_norm=True),
    )


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cuda")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("results/memory_frontier")
    )
    parser.add_argument("--depth", type=int, default=32)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--batch", type=int, default=8192)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument(
        "--ladder", action="store_true", help="run the L=8 LR ladder only"
    )
    parser.add_argument(
        "--rung",
        action="store_true",
        help="run the depth rung (plain plateau vs the normalized pass) only",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.ladder:
        ladder = run_learning_ladder(device=args.device)
        logger.info("LR ladder: %s", json.dumps(ladder))
        return
    if args.rung:
        rung = depth_rung(
            PilotPoint(
                depth=args.depth,
                width=args.width,
                batch=args.batch,
                steps=args.steps,
            ),
            device=args.device,
        )
        logger.info("depth rung: %s", json.dumps(asdict(rung), default=str))
        logger.info(
            "floor=%.3f plain L=%d %.3f best %.3f lr=%g (%s) confirmation %.3f "
            "ratio=%s -> plateaued=%s left=%s floor_met=%s",
            rung.floor,
            rung.plain[-1].depth,
            rung.plain[-1].val_acc,
            rung.best.val_acc,
            rung.best.lr,
            "on" if rung.best.stream_norm else "off",
            rung.confirmation.val_acc,
            "n/a" if rung.activation_ratio is None else f"{rung.activation_ratio:.2f}x",
            rung.plateaued,
            rung.left_the_plateau,
            rung.reaches_floor,
        )
        return
    report = run_pilot(
        PilotPoint(
            depth=args.depth, width=args.width, batch=args.batch, steps=args.steps
        ),
        device=args.device,
        output_dir=args.output_dir,
    )
    logger.info("pilot rows: %s", json.dumps(report.appendix_rows()))
    logger.info(
        "c=%.2f spread=%.1f%% instrument=%s learning=%s",
        report.measured_c,
        report.c_spread * 100,
        "PASS" if report.instrument_control_passed else "FAIL",
        "PASS" if report.learning.passed else "FAIL",
    )


if __name__ == "__main__":
    _main()
