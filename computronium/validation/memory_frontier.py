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
from computronium.core.system_trainer._resources import BINDING_SHARE, binding_verdict
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
    "ACTIVATION_RATIO_MAX",
    "ADMISSION_BUDGET_MB",
    "ARMS",
    "CLAIM_ARMS",
    "CLAIM_SEEDS",
    "COMMITTED_REGISTRATION",
    "DECLARED_C",
    "DELTA",
    "DEPTH_RUNG",
    "FLOOR_MARGIN",
    "FROZEN_LR",
    "INSTRUMENT_DEPTH",
    "LADDER_SEEDS",
    "LR_LADDER",
    "N_MAX",
    "PILOT_SEEDS",
    "REGISTRATION_DATE",
    "STREAM_LR_LADDER",
    "BindingAppendix",
    "BindingRow",
    "ClaimCell",
    "DepthCell",
    "DepthRung",
    "InstrumentControl",
    "MemoryFrontierRegistration",
    "PilotPoint",
    "PilotReport",
    "ScreenVerdict",
    "build_registration",
    "claim_ladder",
    "depth_rung",
    "register_memory_frontier",
    "run_learning_ladder",
    "run_pilot",
    "run_screen",
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

#: T6a registers the depth rung the plain stack can still train: T6c refused
#: the L=32 pass, and the plain stack stops learning between L=4 and L=16.
DEPTH_RUNG = (4, 8)
#: The instrument control's depth: two deltas above the claim point measure c
#: at W=512/B=2048 without the 8 GB pilot's 4.5 GiB allocation (OOM guard).
INSTRUMENT_DEPTH = 16
#: The claim's two arms plus the plain arm the binding gate reads.
CLAIM_ARMS = ("hybrid", "backprop+ckpt", "backprop")
ACTIVATION_RATIO_MAX = 0.5
N_MAX = 5
REGISTRATION_DATE = "2026-11-16"
COMMITTED_REGISTRATION = (
    Path(__file__).resolve().parents[2]
    / "configs"
    / "preregistrations"
    / "t93_memory_frontier_registered.json"
)

ARMS = ("backprop", "backprop+ckpt", "hybrid", "local")
LR_LADDER = (0.1, 0.3, 1.0)
#: The pre-registered material effect: one percentage point of accuracy.
DELTA = 0.01
#: The held-out test split's binomial resolution (~0.3 pp at 10k samples).
ACCURACY_RESOLUTION = 0.003
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
class InstrumentControl:
    """Does the calibration cell read ``c·L·B·W·4`` within tolerance?"""

    point: PilotPoint
    measured_c: float
    spread: float
    tolerance: float
    calibration: tuple[CalibrationRow, ...]

    @property
    def passed(self) -> bool:
        return self.spread < self.tolerance and (
            abs(self.measured_c - DECLARED_C) / DECLARED_C < self.tolerance
        )


@dataclass(frozen=True, slots=True)
class ClaimCell:
    """One registered (arm, depth, seed) cell, priced but not measured.

    ``activations_mb`` and ``peak_mb`` are the **plain** arm's ceiling for the
    same geometry: a checkpointed or hybrid claim cell retains no more than the
    plain stack, so admission is conservative rather than optimistic.
    """

    arm: str
    depth: int
    seed: int
    lr: float
    width: int
    batch: int
    steps: int
    activations_mb: float
    params_mb: float
    peak_mb: float
    affordable: bool
    runnable: bool
    measured: bool = False
    skipped_reason: str = ""


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


@dataclass(frozen=True, slots=True)
class BindingRow:
    """One row of the binding arithmetic: peak, share, and the gate verdict."""

    depth: int
    width: int
    batch: int
    activations_mb: float
    params_mb: float
    peak_mb: float
    activation_share: float
    binding: bool


@dataclass(frozen=True, slots=True)
class BindingAppendix:
    """The binding arithmetic at the claim box and the measured pilot point."""

    share_floor: float
    c: float
    rows: tuple[BindingRow, ...]
    pilot_appendix: BindingRow


@dataclass(frozen=True, slots=True)
class ScreenVerdict:
    """The cheap falsifier at the registered rung: rung 2, not the claim.

    ``hybrid`` and ``baseline`` are the best ladder points on the ladder seed;
    ``confirmation_hybrid``/``confirmation_baseline`` repeat them on the
    disjoint confirmation seed. The screen can refuse the claim, in which case
    the claim run is not scheduled; a candidate screen is the trigger for it.
    """

    hybrid: ArmCell
    baseline: ArmCell
    confirmation_hybrid: ArmCell
    confirmation_baseline: ArmCell

    @property
    def floor(self) -> float:
        return self.baseline.val_acc - DELTA

    @property
    def activation_ratio(self) -> float | None:
        if not self.hybrid.activations_mb or not self.baseline.activations_mb:
            return None
        return self.hybrid.activations_mb / self.baseline.activations_mb

    @property
    def confirmation_ratio(self) -> float | None:
        if (
            not self.confirmation_hybrid.activations_mb
            or not self.confirmation_baseline.activations_mb
        ):
            return None
        return (
            self.confirmation_hybrid.activations_mb
            / self.confirmation_baseline.activations_mb
        )

    @property
    def meets_accuracy(self) -> bool:
        return self.hybrid.val_acc >= self.floor

    @property
    def meets_memory(self) -> bool:
        ratio = self.activation_ratio
        return ratio is not None and ratio <= ACTIVATION_RATIO_MAX

    @property
    def confirmation_met(self) -> bool:
        ratio = self.confirmation_ratio
        return (
            self.confirmation_hybrid.val_acc >= self.floor
            and ratio is not None
            and ratio <= ACTIVATION_RATIO_MAX
        )

    @property
    def verdict(self) -> str:
        if not self.meets_memory:
            return "refuse"
        if not self.meets_accuracy:
            marginal = abs(self.hybrid.val_acc - self.floor) < ACCURACY_RESOLUTION
            return "coordinate" if marginal else "refuse"
        if not self.confirmation_met:
            return "coordinate"
        if abs(self.hybrid.val_acc - self.floor) < ACCURACY_RESOLUTION:
            return "coordinate"
        return "candidate"

    @property
    def reason(self) -> str:
        ratio = self.activation_ratio
        parts = [
            f"hybrid {self.hybrid.val_acc:.3f} vs floor {self.floor:.3f} "
            f"({'met' if self.meets_accuracy else 'below'})",
            f"activation set {ratio:.2f}× the checkpointed arm "
            f"({'met' if self.meets_memory else 'above'} the "
            f"{ACTIVATION_RATIO_MAX:.1f}× bar)"
            if ratio is not None
            else "activation set unmeasured",
        ]
        if not self.confirmation_met:
            parts.append("the confirmation seed does not repeat the screen")
        return "; ".join(parts)

    @property
    def trigger(self) -> str:
        return (
            "T6c re-opens with LayerNorm (c≈2) or the Innocenti init, or a "
            "depth where the hybrid's memory crossover and the stack's "
            "trainability meet (L≥16)"
        )


@dataclass(frozen=True, slots=True)
class MemoryFrontierRegistration:
    """T6a: the memory-frontier claim, written before the claim cells run.

    The registration fixes the claim, the depth rung, the per-arm frozen
    learning rate, the claim seeds, the minimal ladder (30 priced cells), both
    positive controls, the binding arithmetic, and the stop rule. It is not a
    result: every registered cell is ``measured=False`` until a later session
    runs the claim.

    The claim is W1's sharper form -- accuracy within :data:`threshold` of the
    checkpointed arm at no more than :data:`ACTIVATION_RATIO_MAX` its activation
    bytes -- so no hypervolume reference point must be fixed. The alternative
    (a hypervolume reference) is deliberately not registered.
    """

    claim: str
    metric: str
    threshold: float
    alpha: float
    min_seeds: int
    created: str
    point: PilotPoint
    depth_rung: tuple[int, int]
    pilot_seeds: tuple[int, ...]
    ladder_seeds: tuple[int, ...]
    claim_seeds: tuple[int, ...]
    data_seed: int
    lr_ladder: tuple[dict[str, object], ...]
    lrs: dict[str, float]
    instrument: InstrumentControl
    learning: LearningControl
    claim_cells: tuple[ClaimCell, ...]
    binding: BindingAppendix
    screen: ScreenVerdict | None
    stop_rule: str

    @property
    def controls_passed(self) -> bool:
        return self.instrument.passed and self.learning.passed

    @property
    def decision(self) -> str:
        return "activation_ratio<=0.5x at accuracy within delta"

    def to_dict(self) -> dict[str, object]:
        return {
            "claim": self.claim,
            "metric": self.metric,
            "threshold": self.threshold,
            "alpha": self.alpha,
            "min_seeds": self.min_seeds,
            "created": self.created,
            "point": asdict(self.point),
            "box": {
                "task": "cifar10",
                "train_subset": TRAIN_SUBSET,
                "test_samples": TEST_SAMPLES,
                "fidelity": "L0",
                "device": "cuda",
                "depth": self.point.depth,
                "depth_rung": list(self.depth_rung),
                "width": self.point.width,
                "batch": self.point.batch,
                "steps": self.point.steps,
                "epochs": self.point.epochs,
                "batches_per_epoch": self.point.batches_per_epoch,
                "dtype": "fp32",
                "delta": self.threshold,
                "floor": self.learning.floor,
                "n_max": self.min_seeds,
                "admission_budget_mb": ADMISSION_BUDGET_MB,
                "depth_trigger": (
                    "T6c re-opens with LayerNorm (c≈2) or the Innocenti "
                    "depth-scaled init; until then the rung stays L=4→8"
                ),
            },
            "depth_rung": list(self.depth_rung),
            "pilot_seeds": list(self.pilot_seeds),
            "ladder_seeds": list(self.ladder_seeds),
            "claim_seeds": list(self.claim_seeds),
            "data_seed": self.data_seed,
            "lr_ladder": [dict(row) for row in self.lr_ladder],
            "lrs": dict(self.lrs),
            "controls": {
                "instrument": asdict(self.instrument)
                | {"passed": self.instrument.passed},
                "learning": asdict(self.learning),
            },
            "decision": self.decision,
            "claim_cells": [asdict(cell) for cell in self.claim_cells],
            "binding": asdict(self.binding),
            "screen": None
            if self.screen is None
            else {
                **asdict(self.screen),
                "verdict": self.screen.verdict,
                "reason": self.screen.reason,
                "trigger": self.screen.trigger,
                "floor": self.screen.floor,
                "activation_ratio": self.screen.activation_ratio,
                "confirmation_ratio": self.screen.confirmation_ratio,
            },
            "stop_rule": self.stop_rule,
        }

    def markdown(self) -> str:
        lines = [
            f"# Memory frontier registration ({self.created})",
            "",
            self.claim,
            "",
            f"Depth rung L={self.depth_rung[0]}→{self.depth_rung[1]} at "
            f"W={self.point.width}, B={self.point.batch}, "
            f"{self.point.steps} steps, {self.threshold:.1%} delta, "
            f"n_max={self.min_seeds}.",
            "",
            f"Instrument control {'PASS' if self.instrument.passed else 'FAIL'} "
            f"(c={self.instrument.measured_c:.3f}, spread "
            f"{self.instrument.spread:.1%}); learning control "
            f"{'PASS' if self.learning.passed else 'FAIL'} "
            f"(backprop {self.learning.backprop_acc:.3f} vs floor "
            f"{self.learning.floor:.3f}).",
            "",
            "| Arm | LR | val_acc |",
            "|---|---|---|",
        ]
        lines.extend(
            f"| `{row['arm']}` | {row['lr']} | {row['val_acc']} |"
            for row in self.lr_ladder
        )
        if self.screen is not None:
            lines.extend([
                "",
                f"**Screen ({self.screen.verdict}).** {self.screen.reason}.",
                f"Trigger: {self.screen.trigger}.",
            ])
        lines.extend([
            "",
            "| Arm | Depth | Seeds | LR | Peak MB | Admitted | Measured |",
            "|---|---|---|---|---|---|---|",
        ])
        lines.extend(
            f"| `{row.arm}` | {row.depth} | {len(self.claim_seeds)} | "
            f"{row.lr} | {row.peak_mb} | {row.affordable} | {row.measured} |"
            for row in self.claim_cells
        )
        lines.extend(["", f"**Stop rule.** {self.stop_rule}", ""])
        return "\n".join(lines)

    def write(self, output_dir: Path) -> Path:
        """Write the registration and its table to the result directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "memory_frontier.registered.json"
        path.write_text(json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8")
        (output_dir / "memory_frontier.registered.md").write_text(
            self.markdown(), encoding="utf-8"
        )
        return path

    def commit(self, path: Path = COMMITTED_REGISTRATION) -> Path:
        """Commit the registration to the repo; never overwrite an existing one."""
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(self.to_dict(), indent=2) + "\n", encoding="utf-8"
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
    lrs: Mapping[str, float] = FROZEN_LR,
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
            lr=lrs[arm],
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


def _best_lr(points: Mapping[str, float]) -> float:
    """The ladder's best point; a tie keeps the smaller LR."""
    return float(max(sorted(points, key=float), key=lambda lr: points[lr]))


def _registered_cell(
    point: PilotPoint, arm: str, *, depth: int, seed: int, lr: float, c: float
) -> ClaimCell:
    """Price one claim cell with the plain arm's ceiling for its geometry."""
    scaled = point.scaled(depth=depth)
    runnable = scaled.batch <= TRAIN_SUBSET
    return ClaimCell(
        arm=arm,
        depth=depth,
        seed=seed,
        lr=lr,
        width=scaled.width,
        batch=scaled.batch,
        steps=scaled.steps,
        activations_mb=round(scaled.activation_mb(c=c), 1),
        params_mb=round(scaled.params_mb(), 1),
        peak_mb=round(scaled.peak_mb(c=c), 1),
        affordable=scaled.affordable(),
        runnable=runnable,
        skipped_reason=""
        if runnable
        else f"batch exceeds the fixed {TRAIN_SUBSET}-image train subset",
    )


def _claim_cells(
    point: PilotPoint, lrs: Mapping[str, float], *, c: float = DECLARED_C
) -> tuple[ClaimCell, ...]:
    """The minimal claim ladder: 3 arms × 2 depths × 5 paired seeds."""
    return tuple(
        _registered_cell(point, arm, depth=depth, seed=seed, lr=lrs[arm], c=c)
        for arm in CLAIM_ARMS
        for depth in DEPTH_RUNG
        for seed in CLAIM_SEEDS
    )


def _binding(point: PilotPoint, *, measured_c: float) -> BindingAppendix:
    """The binding appendix: arithmetic at the claim box and the pilot point."""

    def row(source: PilotPoint, depth: int) -> BindingRow:
        scaled = source.scaled(depth=depth)
        activations = scaled.activation_mb(c=measured_c)
        params = scaled.params_mb()
        peak = activations + 2 * params
        return BindingRow(
            depth=scaled.depth,
            width=scaled.width,
            batch=scaled.batch,
            activations_mb=round(activations, 1),
            params_mb=round(params, 1),
            peak_mb=round(peak, 1),
            activation_share=round(activations / peak, 3),
            binding=activations / peak >= BINDING_SHARE,
        )

    return BindingAppendix(
        share_floor=BINDING_SHARE,
        c=measured_c,
        rows=tuple(row(point, depth) for depth in DEPTH_RUNG),
        pilot_appendix=row(PilotPoint(), PilotPoint().depth),
    )


def build_registration(
    *,
    point: PilotPoint,
    ladder: Mapping[str, Mapping[str, float]],
    instrument: InstrumentControl,
    learning: LearningControl,
    screen: ScreenVerdict | None = None,
    lrs: Mapping[str, float] | None = None,
    c: float = DECLARED_C,
    created: str = REGISTRATION_DATE,
) -> MemoryFrontierRegistration:
    """Build T6a's registration from the measured ladder and both controls.

    This is the pure half of the runner: it prices the claim ladder and fixes
    the stop rule without measuring a claim cell. The claim's rule is the
    sharper W1 form -- accuracy within ``delta`` at ≤0.5× activation bytes --
    so no hypervolume reference point is registered.
    """
    frozen = dict(lrs or {arm: _best_lr(points) for arm, points in ladder.items()})
    if not instrument.passed or not learning.passed:
        raise ValueError("a failed positive control invalidates the registration")
    rows = tuple(
        {
            "arm": arm,
            "lr": float(lr),
            "val_acc": round(points[lr], 4),
            "seed": LADDER_SEEDS[0],
        }
        for arm, points in ladder.items()
        for lr in sorted(points, key=float)
    )
    return MemoryFrontierRegistration(
        claim=(
            "at the registered L=4→8 rung on CIFAR-10, the hybrid reaches the "
            "checkpointed arm's accuracy within delta at no more than 0.5× its "
            "activation bytes, at matched steps, width, batch, and optimizer"
        ),
        metric="val_acc",
        threshold=DELTA,
        alpha=0.05,
        min_seeds=N_MAX,
        created=created,
        point=point,
        depth_rung=DEPTH_RUNG,
        pilot_seeds=PILOT_SEEDS,
        ladder_seeds=LADDER_SEEDS,
        claim_seeds=CLAIM_SEEDS,
        data_seed=DATA_SEED,
        lr_ladder=rows,
        lrs=frozen,
        instrument=instrument,
        learning=learning,
        claim_cells=_claim_cells(point, frozen, c=c),
        binding=_binding(point, measured_c=c),
        screen=screen,
        stop_rule=(
            "At n_max=5 paired seeds, promote only if the hybrid's paired 95% "
            "activation-ratio interval lies at or below 0.5× and its accuracy "
            "lies at or above the checkpointed arm's minus delta; if either "
            "interval straddles its bar, record a coordinate with the trigger; "
            "if the hybrid misses both, refuse with the measured mechanism. "
            "Do not extend depth past L=8 until T6c re-opens."
        ),
    )


def _screen(
    point: PilotPoint,
    *,
    lrs: Mapping[str, float],
    seeds: tuple[int, ...],
    device: str,
    data: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
) -> ScreenVerdict:
    """Run the hybrid and the checkpointed arm at the frozen LR on two seeds."""
    x_train, y_train, x_test, y_test = data

    def cell(arm: str, seed: int) -> ArmCell:
        return _measure(
            arm,
            point,
            lr=lrs[arm],
            seed=seed,
            device=device,
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
        )

    return ScreenVerdict(
        hybrid=cell("hybrid", seeds[0]),
        baseline=cell("backprop+ckpt", seeds[0]),
        confirmation_hybrid=cell("hybrid", seeds[1]),
        confirmation_baseline=cell("backprop+ckpt", seeds[1]),
    )


def run_screen(
    point: PilotPoint | None = None,
    *,
    lrs: Mapping[str, float] = FROZEN_LR,
    seeds: tuple[int, ...] = LADDER_SEEDS[:2],
    device: str = "cuda",
) -> ScreenVerdict:
    """The rung-2 screen at the registered point: the claim's cheap falsifier."""
    return _screen(
        point or PilotPoint(depth=DEPTH_RUNG[-1], width=512, batch=2048, steps=200),
        lrs=lrs,
        seeds=seeds,
        device=device,
        data=_cifar(),
    )


def register_memory_frontier(
    *, device: str = "cuda", output_dir: Path = Path("results/t93_a")
) -> MemoryFrontierRegistration:
    """Run T6a: the per-arm LR ladder at L=8 and both positive controls.

    The ladder is a screen; its best point per arm is frozen in the
    registration, and the claim cells are priced but never run here. A failed
    control invalidates the run instead of producing a registration.

    Raises:
        RuntimeError: On a non-CUDA device, an unaffordable point, or a failed
            positive control.
    """
    if device != "cuda" and not device.startswith("cuda:"):
        raise RuntimeError("the memory frontier registration needs CUDA controls")
    point = PilotPoint(depth=DEPTH_RUNG[-1], width=512, batch=2048, steps=200)
    if not point.affordable():
        raise RuntimeError(
            f"registration point needs {point.peak_mb():.0f} MB > budget "
            f"{ADMISSION_BUDGET_MB:.0f} MB"
        )
    x_train, y_train, x_test, y_test = _cifar()
    ladder = _learning_ladder(
        point,
        seeds=LADDER_SEEDS[:1],
        device=device,
        data=(x_train, y_train, x_test, y_test),
    )
    lrs = {arm: _best_lr(points) for arm, points in ladder.items()}
    pilot = PilotPoint(depth=INSTRUMENT_DEPTH, width=512, batch=2048, steps=200)
    measured_c, spread, calibration = _calibrate(
        pilot,
        device=device,
        seed=PILOT_SEEDS[0],
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )
    instrument = InstrumentControl(
        point=pilot,
        measured_c=measured_c,
        spread=spread,
        tolerance=0.10,
        calibration=calibration,
    )
    learning = _learning_control(
        point,
        lrs=lrs,
        device=device,
        seed=LADDER_SEEDS[0],
        x_train=x_train,
        y_train=y_train,
        x_test=x_test,
        y_test=y_test,
    )
    screen = _screen(
        point,
        lrs=lrs,
        seeds=LADDER_SEEDS,
        device=device,
        data=(x_train, y_train, x_test, y_test),
    )
    registration = build_registration(
        point=point,
        ladder=ladder,
        lrs=lrs,
        instrument=instrument,
        learning=learning,
        screen=screen,
        c=measured_c,
    )
    registration.write(output_dir)
    registration.commit()
    return registration


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


def _learning_ladder(
    point: PilotPoint,
    *,
    seeds: tuple[int, ...],
    device: str,
    data: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
) -> dict[str, dict[str, float]]:
    """The per-arm LR ladder at one point; one CIFAR load serves every cell."""
    x_train, y_train, x_test, y_test = data
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


def run_learning_ladder(
    point: PilotPoint | None = None,
    *,
    seeds: tuple[int, ...] = LADDER_SEEDS[:1],
    device: str = "cuda",
) -> dict[str, dict[str, float]]:
    """The per-arm LR viability ladder: three points, one seed each.

    Returns:
        ``{arm: {lr: val_acc}}`` for every arm and ladder point.
    """
    return _learning_ladder(
        point or PilotPoint(depth=8),
        seeds=seeds,
        device=device,
        data=_cifar(),
    )


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
    parser.add_argument(
        "--register",
        action="store_true",
        help="run T6a: the L=8 LR ladder and both controls, then register",
    )
    parser.add_argument(
        "--registration-dir",
        type=Path,
        default=Path("results/t93_a"),
        help="where the registration table is written",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if args.register:
        registration = register_memory_frontier(
            device=args.device, output_dir=args.registration_dir
        )
        logger.info(
            "registration: L=%d→%d lrs=%s controls=%s cells=%d committed=%s",
            registration.depth_rung[0],
            registration.depth_rung[1],
            json.dumps(registration.lrs),
            "PASS" if registration.controls_passed else "FAIL",
            len(registration.claim_cells),
            COMMITTED_REGISTRATION,
        )
        if registration.screen is not None:
            logger.info(
                "screen: %s (%s) trigger: %s",
                registration.screen.verdict,
                registration.screen.reason,
                registration.screen.trigger,
            )
        return
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
