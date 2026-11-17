"""T6d and T6e -- the hybrid's update and the split's position (TODO93 §8.1).

T6a2 met the memory bar at the pass-carrying box (0.46x the checkpointed
arm's activation set under the stream-normalized pass) and refused on
accuracy: the baseline trains (0.364 against floor 0.354) while the hybrid
reads 0.184 / 0.201, 17 pp below. The refusal is therefore not the box; it
is the hybrid's own composed update. T6d asks which part of that update
binds, at the pilot box the trigger names (L=8/W=1024/B=8192, LR 0.3, 200
steps, CIFAR-10, two screen seeds, no claim seeds):

- ``train_biases``: the hybrid's trunk contrast also moves the trunk's
  biases -- one flag, no new knob;
- ``feedback_scale`` (gamma): the trunk's input-modulation scale, at its
  three-point ladder 0.05/0.3/1.0 and confirmed at the best point. The
  trunk's contrast is first order in gamma, so a gamma-locked scale is a
  factor-of-20 learning-rate handicap against the head's exact gradient;
- head-only (gamma=0): zero modulation, so the trunk's contrast is exactly
  zero and the head alone trains. The control states the head path's
  ceiling: when it reaches the floor while every trunk knob misses it, the
  trunk's update is destructive rather than mis-scaled.

T6d refused every knob and localised the mechanism at the split: the same
trunk rule as a whole stack trains (0.405) where the hybrid collapses.
T6e prices the split's position and the trunk's step (``--split``):

- ``split_layer``: the head on the last Linear only (7 trunk layers + one
  readout layer at the pilot box) against the registered two-layer head;
- ``trunk_lr``: a multiplier on the trunk's pseudo-gradients at the
  readout split, so the trunk and the head do not share one step size.

Both are screens, not claims: fourteen cells at most, disjoint from the
claim seeds, and priced rather than pre-registered. A mechanism that lifts
the hybrid to the checkpointed arm's floor earns the claim box; a knob that
moves it by at least delta without reaching the floor is a coordinate with
its next edge; a knob that moves nothing is a refusal that names the
mechanism and its trigger, not an algorithm verdict.

Run it with::

    uv run python -m computronium.validation.hybrid_update --run
    uv run python -m computronium.validation.hybrid_update --replay
    uv run python -m computronium.validation.hybrid_update --split
    uv run python -m computronium.validation.hybrid_update --split --replay
    uv run python -m computronium.validation.hybrid_update --direction
    uv run python -m computronium.validation.hybrid_update --direction --replay

T6e refused the position and the step, so T6f (``--direction``) prices the
trunk's **direction**: ``orthogonal_init`` (an orthonormalized draw) and
``learned_feedback`` (a ridge fit of B to the batch's boundary error), both
at the registered draw's Frobenius norm so the ladder compares direction at
one scale. A direction that reaches the floor is a promote; a real gain is a
coordinate; no movement refuses the direction and names the trunk's
geometry (a residual or a wider trunk) as the next variable.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import fmean, stdev
from typing import TYPE_CHECKING

import torch

from computronium.validation.memory_frontier import (
    ACCURACY_RESOLUTION,
    DELTA,
    HYBRID_GAMMA,
    LADDER_SEEDS,
    LEARNING_FLOOR,
    PilotPoint,
    cifar_splits,
    measure_cell,
)

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

__all__ = [
    "BOX",
    "CHANCE",
    "CONFIRMATION_SEED",
    "DATE",
    "DIAGNOSTIC_SEEDS",
    "DIRECTION_LADDER",
    "GAMMA_LADDER",
    "HEAD_ONLY_GAMMA",
    "LR",
    "READOUT_SPLIT",
    "REFERENCE_ARM",
    "REGISTERED_SPLIT",
    "SIBLING_ARM",
    "SPLIT_LADDER",
    "TRUNK_LR_LADDER",
    "CellKey",
    "DiagnosticCell",
    "DirectionReport",
    "DirectionRow",
    "HybridUpdateReport",
    "MechanismRow",
    "SplitPositionReport",
    "SplitRow",
    "UpdateVerdict",
    "direction_gate",
    "read_cells",
    "replay_diagnostic",
    "replay_direction_diagnostic",
    "replay_split_diagnostic",
    "run_diagnostic",
    "run_direction_diagnostic",
    "run_split_diagnostic",
    "split_gate",
    "update_gate",
    "write_direction_report",
    "write_report",
    "write_split_report",
]

#: The pilot box the T6a2 trigger names (L=8, W=1024, B=8192, 200 steps).
BOX = PilotPoint(depth=8, width=1024, batch=8192, steps=200)
#: The hybrid's frozen LR: the pilot ladder's best point, read per arm.
LR = 0.3
#: The trunk's modulation ladder; its first point is the registered arm.
GAMMA_LADDER = (HYBRID_GAMMA, 0.3, 1.0)
#: Zero modulation: the trunk's contrast is zero, so the head alone trains.
HEAD_ONLY_GAMMA = 0.0
#: The registered split: the head on the last two Linears (``-1`` is auto).
REGISTERED_SPLIT = -1
#: The readout split: the stack index of the last Linear (Linears and ReLUs
#: alternate from 0, so ``depth`` Linears end at ``2·(depth - 1)``).
READOUT_SPLIT = 2 * (BOX.depth - 1)
#: The split's position ladder (T6e): the registered head and a one-layer head.
SPLIT_LADDER = (REGISTERED_SPLIT, READOUT_SPLIT)
#: The trunk's own step multipliers (T6e): one box per point, at the readout
#: split, so the trunk and the head do not share a learning rate.
TRUNK_LR_LADDER = (0.3, 1.0, 3.0)
#: The checkpointed arm: the reference the floor is read from.
REFERENCE_ARM = "backprop+ckpt"
#: The whole-stack local rule: the same trunk, no head (the sibling control).
SIBLING_ARM = "local"
#: Chance on the box's 10 classes: a trunk point that collapses reads this.
CHANCE = 1 / BOX.classes
#: Two screen seeds, both disjoint from :data:`CLAIM_SEEDS`.
DIAGNOSTIC_SEEDS = LADDER_SEEDS[:2]
#: The confirmation seed (T6f): disjoint from the direction ladder's screen
#: seeds, so the promoted direction's second reading is not its own screen.
CONFIRMATION_SEED = LADDER_SEEDS[2]
DATE = "2026-11-17"
DEFAULT_OUT = Path("results/t93_a_stream")
#: The trunk's direction ladder (T6f): the two named fixes as
#: ``(label, orthogonal_init, learned_feedback)``. The registered draw is
#: the baseline cell, so the ladder prices direction at one scale.
DIRECTION_LADDER: tuple[tuple[str, bool, bool], ...] = (
    ("orthogonal", True, False),
    ("learned", False, True),
)

type CellKey = tuple[str, float, bool, int, int, float, bool, bool]


@dataclass(frozen=True, slots=True)
class DiagnosticCell:
    """One measured cell: the arm's knob, its seed, and what it scored.

    The arm, gamma, bias flag, split position, and trunk step are the
    cell's identity: a cell log keyed on them replays a report without
    retraining anything. ``split_layer`` and ``trunk_lr`` default to the
    registered arm, so a T6d log line still names its cell; the direction
    flags default to the registered draw, so a T6e log line does too.
    """

    arm: str
    gamma: float
    train_biases: bool
    seed: int
    val_acc: float
    walltime_s: float
    activations_mb: float | None
    peak_mb: float | None
    split_layer: int = REGISTERED_SPLIT
    trunk_lr: float = 1.0
    orthogonal_init: bool = False
    learned_feedback: bool = False


@dataclass(frozen=True, slots=True)
class MechanismRow:
    """One named knob's mean over its seeds, against the floor.

    ``gain`` is measured against the registered arm at the same box, so the
    row's own seeds decide whether the knob moves the hybrid at all;
    ``activation_ratio`` is the hybrid's activation set over the
    reference's -- the claim's memory half, restated at this box.
    """

    mechanism: str
    gamma: float | None
    train_biases: bool
    n: int
    val_acc: float
    val_acc_sd: float
    gain: float
    activations_mb: float | None
    activation_ratio: float | None
    floor: float

    @property
    def reaches_floor(self) -> bool:
        return self.val_acc >= self.floor


@dataclass(frozen=True, slots=True)
class UpdateVerdict:
    """The diagnostic's decision: a mechanism, its reason, and its trigger."""

    verdict: str
    mechanism: str
    reason: str
    trigger: str


@dataclass(frozen=True, slots=True)
class HybridUpdateReport:
    """T6d's measured cells, its knob rows, and the verdict they decide."""

    point: PilotPoint
    lr: float
    reference: tuple[DiagnosticCell, ...]
    baseline: tuple[DiagnosticCell, ...]
    train_biases: tuple[DiagnosticCell, ...]
    gamma_ladder: tuple[DiagnosticCell, ...]
    confirmation: DiagnosticCell
    head_only: DiagnosticCell
    sibling: tuple[DiagnosticCell, ...]
    rows: tuple[MechanismRow, ...]
    floor: float
    best_gamma: float
    verdict: str
    mechanism: str
    reason: str
    trigger: str
    date: str = DATE

    @property
    def reference_acc(self) -> float:
        return fmean(cell.val_acc for cell in self.reference)

    @property
    def baseline_acc(self) -> float:
        return fmean(cell.val_acc for cell in self.baseline)

    @property
    def sibling_acc(self) -> float:
        return max(cell.val_acc for cell in self.sibling)

    @property
    def cells(self) -> tuple[DiagnosticCell, ...]:
        """Every measured cell once, in the report's order.

        The ladder's first point is the baseline cell and the confirmation
        can repeat the baseline's second seed, so the union is deduplicated
        by the cell log's key rather than counted twice.
        """
        unique: dict[CellKey, DiagnosticCell] = {}
        for cell in (
            *self.reference,
            *self.baseline,
            *self.train_biases,
            *self.gamma_ladder,
            self.confirmation,
            self.head_only,
            *self.sibling,
        ):
            unique.setdefault(_key(cell), cell)
        return tuple(unique.values())

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date,
            "point": asdict(self.point) | {"lr": self.lr},
            "reference_acc": round(self.reference_acc, 4),
            "baseline_acc": round(self.baseline_acc, 4),
            "sibling_acc": round(self.sibling_acc, 4),
            "floor": round(self.floor, 4),
            "best_gamma": self.best_gamma,
            "verdict": self.verdict,
            "mechanism": self.mechanism,
            "reason": self.reason,
            "trigger": self.trigger,
            "rows": [asdict(row) for row in self.rows],
            "cells": [asdict(cell) for cell in self.cells],
        }


def _mean_acc(cells: tuple[DiagnosticCell, ...]) -> tuple[float, float]:
    accs = [cell.val_acc for cell in cells]
    return fmean(accs), stdev(accs) if len(accs) > 1 else 0.0


def _mean_mb(cells: tuple[DiagnosticCell, ...]) -> float | None:
    values = [cell.activations_mb for cell in cells if cell.activations_mb is not None]
    return fmean(values) if values else None


def _floor(reference: tuple[DiagnosticCell, ...]) -> float:
    """The checkpointed arm's mean minus delta: the claim's accuracy bar."""
    return fmean(cell.val_acc for cell in reference) - DELTA


def _ratio(
    cells: tuple[DiagnosticCell, ...], reference: tuple[DiagnosticCell, ...]
) -> float | None:
    """The hybrid's activation set over the reference's, or ``None`` unmeasured."""
    measured = _mean_mb(cells)
    base = _mean_mb(reference)
    if measured is None or base is None or base <= 0:
        return None
    return measured / base


def _row(
    mechanism: str,
    gamma: float | None,
    train_biases: bool,
    cells: tuple[DiagnosticCell, ...],
    *,
    baseline_acc: float,
    reference: tuple[DiagnosticCell, ...],
    floor: float,
) -> MechanismRow:
    """One knob's mean, its gain against the baseline, and its memory half."""
    acc, spread = _mean_acc(cells)
    return MechanismRow(
        mechanism=mechanism,
        gamma=gamma,
        train_biases=train_biases,
        n=len(cells),
        val_acc=acc,
        val_acc_sd=spread,
        gain=acc - baseline_acc,
        activations_mb=_mean_mb(cells),
        activation_ratio=_ratio(cells, reference),
        floor=floor,
    )


def _mechanism_rows(
    *,
    baseline: tuple[DiagnosticCell, ...],
    train_biases: tuple[DiagnosticCell, ...],
    ladder: tuple[DiagnosticCell, ...],
    confirmation: DiagnosticCell,
    reference: tuple[DiagnosticCell, ...],
    floor: float,
) -> tuple[MechanismRow, ...]:
    """The two knob rows, each on two seeds; the flag is priced first."""
    baseline_acc, _ = _mean_acc(baseline)
    best = max(ladder, key=lambda cell: cell.val_acc)
    return (
        _row(
            "train_biases",
            None,
            True,
            train_biases,
            baseline_acc=baseline_acc,
            reference=reference,
            floor=floor,
        ),
        _row(
            "feedback_scale",
            best.gamma,
            False,
            (best, confirmation),
            baseline_acc=baseline_acc,
            reference=reference,
            floor=floor,
        ),
    )


def _label(row: MechanismRow) -> str:
    """The knob a row names, in the report's terms."""
    if row.train_biases:
        return "train_biases"
    return f"feedback_scale={row.gamma:g}"


def _ratio_text(ratio: float | None) -> str:
    return (
        "an unmeasured activation set"
        if ratio is None
        else f"{ratio:.2f}x the reference's activation bytes"
    )


def update_gate(  # ruff: ignore[too-many-arguments]
    *,
    reference_acc: float,
    baseline_acc: float,
    rows: tuple[MechanismRow, ...],
    ladder: tuple[DiagnosticCell, ...],
    sibling: tuple[DiagnosticCell, ...],
    head_only_acc: float,
    floor: float,
    delta: float = DELTA,
    learning_floor: float = LEARNING_FLOOR,
    chance: float = CHANCE,
) -> UpdateVerdict:
    """Control, promote, coordinate, then refuse with the mechanism.

    The reference is the run's positive control: a checkpointed arm that
    does not train cannot decide the hybrid's gap, so it invalidates the
    diagnostic. The knobs are then ranked by their two-seed mean; a knob
    that reaches the floor is a mechanism (the flag first, because it adds
    no new knob), a knob that gains at least delta without reaching the
    floor is a coordinate, and no movement at all is a refusal whose
    mechanism is the ladder's shape and the head-only control's reading.

    ``ladder`` is the trunk's own gamma curve: its best point and the
    scales that collapse to chance are what the refusal names. ``sibling``
    is the same trunk rule as a whole stack (no head): when it trains above
    the hybrid by delta and does not collapse where the hybrid does, the
    composition -- the exact-gradient split -- is the mechanism, not the
    rule or its scale.
    """
    if reference_acc < max(floor, learning_floor):
        return UpdateVerdict(
            "invalid",
            "the checkpointed reference",
            (
                f"the reference reads {reference_acc:.3f} against the floor "
                f"{floor:.3f} at the pilot box; a reference that does not train "
                "cannot decide the hybrid's gap"
            ),
            (
                "re-measure the reference at L=8 with the pilot point; the "
                "diagnostic is read on the next run"
            ),
        )
    promoted = [row for row in rows if row.reaches_floor]
    if promoted:
        row = promoted[0]
        return UpdateVerdict(
            "promote",
            f"the hybrid trains once {_label(row)}",
            (
                f"{_label(row)} reads {row.val_acc:.3f} (sd {row.val_acc_sd:.3f} "
                f"over {row.n} seeds) against the floor {floor:.3f} = checkpoint "
                f"{reference_acc:.3f} - {delta * 100:.0f} pp, up "
                f"{row.gain * 100:+.1f} pp from the baseline {baseline_acc:.3f} "
                f"at {_ratio_text(row.activation_ratio)}"
            ),
            (
                "the claim run re-registers at the pilot box with this knob "
                "frozen: the accuracy bar is demonstrated at L=8, so the claim "
                "box's L=8->32 rung prices it next; the memory half is measured "
                "at this box, not assumed from the registered screen"
            ),
        )
    best = max(rows, key=lambda row: row.val_acc)
    if best.gain >= delta:
        return UpdateVerdict(
            "coordinate",
            f"{_label(best)} is a real gain, not the mechanism",
            (
                f"{_label(best)} moves the hybrid {best.gain * 100:+.1f} pp to "
                f"{best.val_acc:.3f} (sd {best.val_acc_sd:.3f} over {best.n} "
                f"seeds) but the floor is {floor:.3f} = checkpoint "
                f"{reference_acc:.3f} - {delta * 100:.0f} pp; the gap narrows "
                "and does not close"
            ),
            (
                f"the next gamma edge above the ladder "
                f"({2 * GAMMA_LADDER[-1]:g}) or a decoupled trunk learning "
                "rate; a claim run is not scheduled on a coordinate"
            ),
        )
    if head_only_acc >= floor:
        return UpdateVerdict(
            "refuse",
            "the trunk's own update is destructive",
            (
                f"with gamma=0 the head alone reads {head_only_acc:.3f} against "
                f"the floor {floor:.3f}, while every trunk knob stays below it "
                f"(best {best.val_acc:.3f}, {best.gain * 100:+.1f} pp from the "
                f"baseline {baseline_acc:.3f}); the head's exact gradient can "
                "classify the trunk's features and the local update destroys them"
            ),
            (
                "a trunk direction check at the same LR (a plain-gradient trunk "
                "against the local contrast) or a decoupled trunk learning rate: "
                "the knob ladder is exhausted, so a scale is not the next rung"
            ),
        )
    collapsed = [
        cell.gamma for cell in ladder if cell.val_acc <= chance + ACCURACY_RESOLUTION
    ]
    collapse_text = (
        "/".join(f"{gamma:g}" for gamma in collapsed)
        if collapsed
        else "nowhere on the ladder"
    )
    flag = next((row for row in rows if row.train_biases), None)
    flag_text = (
        f"the bias flag adds {flag.gain * 100:+.1f} pp, "
        if flag is not None
        else "the bias flag was not priced, "
    )
    sibling_best = max(sibling, key=lambda cell: cell.val_acc)
    if sibling_best.val_acc >= best.val_acc + delta:
        return UpdateVerdict(
            "refuse",
            "the composition, not the trunk's rule or its scale",
            (
                f"the same trunk rule as a whole stack reads "
                f"{sibling_best.val_acc:.3f} at gamma={sibling_best.gamma:g} "
                f"({(sibling_best.val_acc - floor) * 100:+.1f} pp against the floor "
                f"{floor:.3f}) and does not collapse where the hybrid does "
                f"(hybrid to {chance:.3f} at gamma={collapse_text}), while the "
                f"hybrid reads {best.val_acc:.3f} and its head alone "
                f"{head_only_acc:.3f}; {flag_text}the split is the mechanism, "
                f"not the trunk's scale"
            ),
            (
                "the split's position: a readout-only head (split_layer on "
                "the last Linear) or a decoupled trunk learning rate; the "
                "gamma ladder and the bias flag are priced at this box, and "
                "the sibling control shows where the limit sits"
            ),
        )
    return UpdateVerdict(
        "refuse",
        "the trunk's rule at this box, not the hybrid's split",
        (
            f"the same trunk rule as a whole stack reads "
            f"{sibling_best.val_acc:.3f} at gamma={sibling_best.gamma:g}, no "
            f"more than delta above the hybrid's {best.val_acc:.3f}, so the "
            f"rule does not train at this box either (head alone "
            f"{head_only_acc:.3f}, floor {floor:.3f}); another composition "
            f"cannot decide a box the rule itself fails"
        ),
        (
            "the box's geometry or a wider stack: the gamma ladder, the bias "
            "flag, and the head-only control are priced here, so the box is "
            "the next variable"
        ),
    )


def _report(
    *,
    point: PilotPoint,
    reference: tuple[DiagnosticCell, ...],
    baseline: tuple[DiagnosticCell, ...],
    train_biases: tuple[DiagnosticCell, ...],
    ladder: tuple[DiagnosticCell, ...],
    confirmation: DiagnosticCell,
    head_only: DiagnosticCell,
    sibling: tuple[DiagnosticCell, ...],
) -> HybridUpdateReport:
    """Assemble the rows and the gate from the measured cells."""
    floor = _floor(reference)
    rows = _mechanism_rows(
        baseline=baseline,
        train_biases=train_biases,
        ladder=ladder,
        confirmation=confirmation,
        reference=reference,
        floor=floor,
    )
    reference_acc, _ = _mean_acc(reference)
    baseline_acc, _ = _mean_acc(baseline)
    gate = update_gate(
        reference_acc=reference_acc,
        baseline_acc=baseline_acc,
        rows=rows,
        ladder=ladder,
        sibling=sibling,
        head_only_acc=head_only.val_acc,
        floor=floor,
    )
    return HybridUpdateReport(
        point=point,
        lr=LR,
        reference=reference,
        baseline=baseline,
        train_biases=train_biases,
        gamma_ladder=ladder,
        confirmation=confirmation,
        head_only=head_only,
        sibling=sibling,
        rows=rows,
        floor=floor,
        best_gamma=max(ladder, key=lambda cell: cell.val_acc).gamma,
        verdict=gate.verdict,
        mechanism=gate.mechanism,
        reason=gate.reason,
        trigger=gate.trigger,
    )


def _assemble(
    cell: Callable[..., DiagnosticCell], *, point: PilotPoint
) -> HybridUpdateReport:
    """The diagnostic's cell plan: reference, baseline, both knobs, head-only.

    Every mechanism shares the box, the LR, and the trainer; the ladder's
    shallow point is the baseline cell, so the run costs four new cells and
    reuses the baseline's second seed as the confirmation when gamma's best
    point is the registered scale.
    """
    first, last = DIAGNOSTIC_SEEDS[0], DIAGNOSTIC_SEEDS[-1]
    reference = tuple(
        cell(REFERENCE_ARM, gamma=HYBRID_GAMMA, seed=seed) for seed in DIAGNOSTIC_SEEDS
    )
    baseline = tuple(
        cell("hybrid", gamma=HYBRID_GAMMA, seed=seed) for seed in DIAGNOSTIC_SEEDS
    )
    train_biases = tuple(
        cell("hybrid", gamma=HYBRID_GAMMA, train_biases=True, seed=seed)
        for seed in DIAGNOSTIC_SEEDS
    )
    ladder = tuple(cell("hybrid", gamma=gamma, seed=first) for gamma in GAMMA_LADDER)
    best = max(ladder, key=lambda measured: measured.val_acc)
    return _report(
        point=point,
        reference=reference,
        baseline=baseline,
        train_biases=train_biases,
        ladder=ladder,
        confirmation=cell("hybrid", gamma=best.gamma, seed=last),
        head_only=cell("hybrid", gamma=HEAD_ONLY_GAMMA, seed=first),
        sibling=tuple(
            cell(SIBLING_ARM, gamma=gamma, seed=first) for gamma in GAMMA_LADDER
        ),
    )


def _key(cell: DiagnosticCell) -> CellKey:
    return (
        cell.arm,
        cell.gamma,
        cell.train_biases,
        cell.seed,
        cell.split_layer,
        cell.trunk_lr,
        cell.orthogonal_init,
        cell.learned_feedback,
    )


def read_cells(path: Path) -> dict[CellKey, DiagnosticCell]:
    """The cells a previous run measured, keyed by their identity."""
    if not path.exists():
        return {}
    cells: dict[CellKey, DiagnosticCell] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cell = DiagnosticCell(**json.loads(line))
            cells[_key(cell)] = cell
    return cells


class _CellLog:
    """The measured cells: a rerun reuses them and a replay reads them."""

    def __init__(self, path: Path | None) -> None:
        self.path = path
        self.cells = read_cells(path) if path is not None else {}

    def measure(  # ruff: ignore[too-many-arguments]
        self,
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        seed: int,
        point: PilotPoint,
        device: str,
        data: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
        split_layer: int = REGISTERED_SPLIT,
        trunk_lr: float = 1.0,
        orthogonal_init: bool = False,
        learned_feedback: bool = False,
    ) -> DiagnosticCell:
        key = (
            arm,
            gamma,
            train_biases,
            seed,
            split_layer,
            trunk_lr,
            orthogonal_init,
            learned_feedback,
        )
        if key not in self.cells:
            measured = measure_cell(
                arm,
                point,
                lr=LR,
                seed=seed,
                device=device,
                x_train=data[0],
                y_train=data[1],
                x_test=data[2],
                y_test=data[3],
                gamma=gamma,
                train_biases=train_biases,
                split_layer=split_layer,
                trunk_lr=trunk_lr,
                orthogonal_init=orthogonal_init,
                learned_feedback=learned_feedback,
            )
            cell = DiagnosticCell(
                arm=arm,
                gamma=gamma,
                train_biases=train_biases,
                seed=seed,
                val_acc=measured.val_acc,
                walltime_s=measured.walltime_s,
                activations_mb=measured.activations_mb,
                peak_mb=measured.peak_mb,
                split_layer=split_layer,
                trunk_lr=trunk_lr,
                orthogonal_init=orthogonal_init,
                learned_feedback=learned_feedback,
            )
            self.cells[key] = cell
            if self.path is not None:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(asdict(cell)) + "\n")
        return self.cells[key]


def _require_cuda(device: str) -> None:
    if device != "cuda" and not device.startswith("cuda:"):
        raise RuntimeError("the hybrid update diagnostic needs a CUDA peak measurement")


def run_diagnostic(
    point: PilotPoint = BOX,
    *,
    device: str = "cuda",
    log_path: Path | None = None,
) -> HybridUpdateReport:
    """Measure the two update knobs and the head-only control at the box.

    Args:
        point: The pilot box the T6a2 trigger names.
        device: ``"cuda"`` is required -- the cells need a measured peak.
        log_path: Where each measured cell is appended; a rerun reuses it.

    Raises:
        RuntimeError: On a non-CUDA device.
    """
    _require_cuda(device)
    log = _CellLog(log_path)
    data = cifar_splits()

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        seed: int,
    ) -> DiagnosticCell:
        return log.measure(
            arm,
            gamma=gamma,
            train_biases=train_biases,
            seed=seed,
            point=point,
            device=device,
            data=data,
        )

    return _assemble(cell, point=point)


def replay_diagnostic(*, log_path: Path, point: PilotPoint = BOX) -> HybridUpdateReport:
    """Rebuild the report from the cell log, without training a cell.

    Raises:
        RuntimeError: When a cell the report needs is missing from the log.
    """
    cells = read_cells(log_path)
    if not cells:
        raise RuntimeError(f"no cells in {log_path}; run the diagnostic first")

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        seed: int,
    ) -> DiagnosticCell:
        key = (arm, gamma, train_biases, seed, REGISTERED_SPLIT, 1.0, False, False)
        if key not in cells:
            raise RuntimeError(f"no measured cell for {key} in {log_path}")
        return cells[key]

    return _assemble(cell, point=point)


def _markdown(report: HybridUpdateReport) -> str:
    """The table a third party can read, with its rulers and its command."""
    point = report.point
    lines = [
        "# T6d -- the hybrid's update diagnostic (TODO93 track A)",
        "",
        f"**Box.** CIFAR-10 10k/10k, L={point.depth}, W={point.width}, "
        f"B={point.batch}, {point.steps} steps, LR {report.lr:g}, seeds "
        f"{', '.join(str(seed) for seed in DIAGNOSTIC_SEEDS)}, fp32. "
        f"Reference `{REFERENCE_ARM}`; sibling `{SIBLING_ARM}`; mechanisms "
        f"`train_biases`, "
        f"`feedback_scale` {GAMMA_LADDER}, head-only "
        f"gamma={HEAD_ONLY_GAMMA:g}.",
        "",
        f"Reference {report.reference_acc:.3f}; baseline "
        f"{report.baseline_acc:.3f}; sibling {report.sibling_acc:.3f} (the "
        f"whole-stack rule at the same box); floor {report.floor:.3f} "
        f"(reference - {DELTA * 100:.0f} pp); best gamma {report.best_gamma:g}.",
        "",
        "| mechanism | knob | seeds | val acc | sd | gain | activations MB | "
        "ratio | floor | reaches |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in report.rows:
        knob = "train_biases" if row.train_biases else f"gamma={row.gamma:g}"
        activations = (
            f"{row.activations_mb:.0f}" if row.activations_mb is not None else "—"
        )
        ratio = (
            f"{row.activation_ratio:.2f}x" if row.activation_ratio is not None else "—"
        )
        lines.append(
            f"| `{row.mechanism}` | {knob} | {row.n} | {row.val_acc:.3f} | "
            f"{row.val_acc_sd:.3f} | {row.gain * 100:+.1f} pp | {activations} | "
            f"{ratio} | {row.floor:.3f} | "
            f"{'yes' if row.reaches_floor else 'no'} |"
        )
    lines.extend([
        "",
        "| arm | gamma | split | trunk lr | seed | val acc | s | "
        "activations MB | peak MB |",
        "|---|---|---|---|---|---|---|---|---|",
    ])
    for cell in report.cells:
        activations = (
            f"{cell.activations_mb:.0f}" if cell.activations_mb is not None else "—"
        )
        peak = f"{cell.peak_mb:.0f}" if cell.peak_mb is not None else "—"
        position = "registered" if cell.split_layer < 0 else str(cell.split_layer)
        lines.append(
            f"| `{cell.arm}` | {cell.gamma:g} | {position} | {cell.trunk_lr:g} | "
            f"{cell.seed} | {cell.val_acc:.3f} | {cell.walltime_s:.1f} | "
            f"{activations} | {peak} |"
        )
    lines.extend([
        "",
        f"**Gate outcome: {report.verdict}** -- a box statement at the pilot "
        "box; the measurement stands and the mechanism stays open.",
        "",
        f"**Trigger.** {report.trigger}",
        "",
        "**Rulers.** val acc on the full 10k test split (1 sigma ~ 0.3 pp); "
        "activation bytes (peak - params - optimizer - auxiliary); walltime per "
        "cell; the floor is the checkpointed arm's mean minus delta, and the "
        "baseline is the registered hybrid at the same box.",
        "",
        "Command: `uv run python -m computronium.validation.hybrid_update "
        "--run`; replay the gate from the cell log with `... --replay`.",
        "",
    ])
    return "\n".join(lines)


def write_report(report: HybridUpdateReport, output_dir: str | Path) -> Path:
    """Write ``hybrid_update.json`` and ``hybrid_update.md``; return the JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "hybrid_update.json"
    path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    (output_dir / "hybrid_update.md").write_text(_markdown(report), encoding="utf-8")
    return path


@dataclass(frozen=True, slots=True)
class SplitRow:
    """One mechanism's mean over its seeds, against the reference's floor.

    A row is one point of a knob: ``split_layer`` (the head's position) or
    ``trunk_lr`` (the trunk's step multiplier), read beside the
    registered arm at the same box, LR, weight init, and update rule.
    """

    mechanism: str
    split_layer: int
    trunk_lr: float
    n: int
    val_acc: float
    val_acc_sd: float
    gain: float
    activations_mb: float | None
    activation_ratio: float | None
    floor: float

    @property
    def reaches_floor(self) -> bool:
        return self.val_acc >= self.floor


@dataclass(frozen=True, slots=True)
class SplitPositionReport:
    """T6e's measured cells, its knob rows, and the verdict they decide."""

    point: PilotPoint
    lr: float
    reference: tuple[DiagnosticCell, ...]
    baseline: tuple[DiagnosticCell, ...]
    split_ladder: tuple[DiagnosticCell, ...]
    trunk_lr_ladder: tuple[DiagnosticCell, ...]
    confirmation: DiagnosticCell
    rows: tuple[SplitRow, ...]
    floor: float
    verdict: str
    mechanism: str
    reason: str
    trigger: str
    date: str = DATE

    @property
    def reference_acc(self) -> float:
        return fmean(cell.val_acc for cell in self.reference)

    @property
    def baseline_acc(self) -> float:
        return fmean(cell.val_acc for cell in self.baseline)

    @property
    def cells(self) -> tuple[DiagnosticCell, ...]:
        """Every measured cell once, keyed by its identity."""
        unique: dict[CellKey, DiagnosticCell] = {}
        for cell in (
            *self.reference,
            *self.baseline,
            *self.split_ladder,
            *self.trunk_lr_ladder,
            self.confirmation,
        ):
            unique.setdefault(_key(cell), cell)
        return tuple(unique.values())

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date,
            "point": asdict(self.point) | {"lr": self.lr},
            "reference_acc": round(self.reference_acc, 4),
            "baseline_acc": round(self.baseline_acc, 4),
            "floor": round(self.floor, 4),
            "verdict": self.verdict,
            "mechanism": self.mechanism,
            "reason": self.reason,
            "trigger": self.trigger,
            "rows": [asdict(row) for row in self.rows],
            "cells": [asdict(cell) for cell in self.cells],
        }


def _split_label(row: SplitRow) -> str:
    """The knob a row names, in the report's terms."""
    if row.mechanism == "split_layer":
        return (
            "the head at the last Linear"
            if row.split_layer == READOUT_SPLIT
            else "the registered two-layer head"
        )
    return f"trunk_lr={row.trunk_lr:g}"


def _split_row(
    mechanism: str,
    cells: tuple[DiagnosticCell, ...],
    *,
    baseline_acc: float,
    reference: tuple[DiagnosticCell, ...],
    floor: float,
) -> SplitRow:
    """One knob point's mean, its gain, and its memory half."""
    acc, spread = _mean_acc(cells)
    first = cells[0]
    return SplitRow(
        mechanism=mechanism,
        split_layer=first.split_layer,
        trunk_lr=first.trunk_lr,
        n=len(cells),
        val_acc=acc,
        val_acc_sd=spread,
        gain=acc - baseline_acc,
        activations_mb=_mean_mb(cells),
        activation_ratio=_ratio(cells, reference),
        floor=floor,
    )


def _split_rows(
    *,
    baseline: tuple[DiagnosticCell, ...],
    readout: tuple[DiagnosticCell, ...],
    ladder: tuple[DiagnosticCell, ...],
    confirmation: DiagnosticCell,
    reference: tuple[DiagnosticCell, ...],
    floor: float,
) -> tuple[SplitRow, ...]:
    """The split's row on two seeds, then each trunk step beside it.

    The registered trunk step (1.0) at the readout split **is** the split
    row, so the two are one row read once. The best step is read on the
    confirmation seed; a step that is not the best keeps its one screen
    seed, so the table never claims a second seed it did not measure.
    """
    baseline_acc, _ = _mean_acc(baseline)
    best = max(ladder, key=lambda cell: cell.val_acc)
    rows = [
        _split_row(
            "split_layer",
            readout,
            baseline_acc=baseline_acc,
            reference=reference,
            floor=floor,
        )
    ]
    for cell in ladder:
        if cell.trunk_lr == 1.0:
            cells = readout
        elif cell.trunk_lr == best.trunk_lr:
            cells = (cell, confirmation)
        else:
            cells = (cell,)
        rows.append(
            _split_row(
                "trunk_lr",
                cells,
                baseline_acc=baseline_acc,
                reference=reference,
                floor=floor,
            )
        )
    return tuple(rows)


def split_gate(  # ruff: ignore[too-many-arguments]
    *,
    reference_acc: float,
    baseline_acc: float,
    rows: tuple[SplitRow, ...],
    ladder: tuple[DiagnosticCell, ...],
    floor: float,
    delta: float = DELTA,
    learning_floor: float = LEARNING_FLOOR,
) -> UpdateVerdict:
    """Control, promote the split, promote the trunk's step, then refuse.

    The split's position is the T6d mechanism, so it is read first: when
    the readout-only head reaches the floor, the head's depth is the fix.
    When it does not, the trunk's step is read at the readout split; a
    step that reaches the floor is the fix, a step that only gains is a
    coordinate, and no movement at all refuses the split and the step as
    one mechanism -- the trunk's **direction** -- with its own trigger.
    """
    if reference_acc < max(floor, learning_floor):
        return UpdateVerdict(
            "invalid",
            "the checkpointed reference",
            (
                f"the reference reads {reference_acc:.3f} against the floor "
                f"{floor:.3f} at the pilot box; a reference that does not train "
                "cannot decide the split's position"
            ),
            "re-measure the reference at the pilot box; the diagnostic is read "
            "on the next run",
        )
    split_row = next(row for row in rows if row.mechanism == "split_layer")
    if split_row.reaches_floor:
        return UpdateVerdict(
            "promote",
            "the head's depth: a readout-only head",
            (
                f"the readout-only head reads {split_row.val_acc:.3f} (sd "
                f"{split_row.val_acc_sd:.3f} over {split_row.n} seeds) against "
                f"the floor {floor:.3f} = checkpoint {reference_acc:.3f} - "
                f"{delta * 100:.0f} pp, up {split_row.gain * 100:+.1f} pp from "
                f"the registered arm's {baseline_acc:.3f} at "
                f"{_ratio_text(split_row.activation_ratio)}"
            ),
            (
                "the claim run re-registers at the pilot box with the split on "
                "the last Linear: the accuracy bar is demonstrated at L=8, so "
                "the claim box's L=8->32 rung prices it next"
            ),
        )
    best = max(
        (row for row in rows if row.mechanism == "trunk_lr"),
        key=lambda row: row.val_acc,
    )
    if best.reaches_floor:
        return UpdateVerdict(
            "promote",
            f"the decoupled trunk step ({_split_label(best)})",
            (
                f"{_split_label(best)} reads {best.val_acc:.3f} (sd "
                f"{best.val_acc_sd:.3f} over {best.n} seeds) against the floor "
                f"{floor:.3f}, up {best.gain * 100:+.1f} pp from the "
                f"registered arm's {baseline_acc:.3f}, while the readout-only "
                f"head alone reads {split_row.val_acc:.3f}"
            ),
            (
                "the claim run re-registers at the pilot box with the split on "
                "the last Linear and the trunk's step frozen; the memory half "
                "is read at the same box"
            ),
        )
    if best.gain >= delta:
        return UpdateVerdict(
            "coordinate",
            f"{_split_label(best)} is a real gain, not the mechanism",
            (
                f"{_split_label(best)} moves the hybrid {best.gain * 100:+.1f} pp "
                f"to {best.val_acc:.3f} (sd {best.val_acc_sd:.3f} over {best.n} "
                f"seeds) but the floor is {floor:.3f}; the split alone reads "
                f"{split_row.val_acc:.3f} ({split_row.gain * 100:+.1f} pp)"
            ),
            (
                f"the next trunk-step edge above the ladder "
                f"({2 * TRUNK_LR_LADDER[-1]:g}x) at the readout split; a claim "
                "run is not scheduled on a coordinate"
            ),
        )
    steps = "/".join(f"{cell.trunk_lr:g}" for cell in ladder)
    return UpdateVerdict(
        "refuse",
        "the trunk's direction, not its position or its step",
        (
            f"the readout-only head reads {split_row.val_acc:.3f} "
            f"({split_row.gain * 100:+.1f} pp from the registered arm "
            f"{baseline_acc:.3f}, so the position only loses accuracy) and the "
            f"trunk's step ladder {steps} reads {best.val_acc:.3f} at its best, "
            f"so neither the position nor the step reaches the floor "
            f"{floor:.3f} = checkpoint {reference_acc:.3f} - "
            f"{delta * 100:.0f} pp, at {_ratio_text(best.activation_ratio)}"
        ),
        (
            "a trunk-direction fix: the feedback matrix by ridge regression "
            "(`learned_feedback`) or an orthogonal init at the readout split, "
            "or a residual/wider trunk -- the position and the step are priced "
            "at this box, so the direction is the next variable"
        ),
    )


def _split_report(
    *,
    point: PilotPoint,
    reference: tuple[DiagnosticCell, ...],
    baseline: tuple[DiagnosticCell, ...],
    readout: tuple[DiagnosticCell, ...],
    ladder: tuple[DiagnosticCell, ...],
    confirmation: DiagnosticCell,
) -> SplitPositionReport:
    """Assemble the rows and the gate from the measured cells."""
    floor = _floor(reference)
    rows = _split_rows(
        baseline=baseline,
        readout=readout,
        ladder=ladder,
        confirmation=confirmation,
        reference=reference,
        floor=floor,
    )
    reference_acc, _ = _mean_acc(reference)
    baseline_acc, _ = _mean_acc(baseline)
    gate = split_gate(
        reference_acc=reference_acc,
        baseline_acc=baseline_acc,
        rows=rows,
        ladder=ladder,
        floor=floor,
    )
    return SplitPositionReport(
        point=point,
        lr=LR,
        reference=reference,
        baseline=baseline,
        split_ladder=readout,
        trunk_lr_ladder=ladder,
        confirmation=confirmation,
        rows=rows,
        floor=floor,
        verdict=gate.verdict,
        mechanism=gate.mechanism,
        reason=gate.reason,
        trigger=gate.trigger,
    )


def _assemble_split(
    cell: Callable[..., DiagnosticCell], *, point: PilotPoint
) -> SplitPositionReport:
    """T6e's cell plan: reference, baseline, the split ladder, the step ladder.

    The registered arms are the T6d cells, so a run with the T6d log
    retrains only the split's cells: two readout-only cells and the
    trunk's step ladder's outer points. The registered step (1.0) at the
    readout split is the split's own first seed, so the ladder reuses it
    and the confirmation is only measured when the best step is not 1.0.
    """
    reference = tuple(
        cell(REFERENCE_ARM, gamma=HYBRID_GAMMA, seed=seed) for seed in DIAGNOSTIC_SEEDS
    )
    baseline = tuple(
        cell("hybrid", gamma=HYBRID_GAMMA, seed=seed) for seed in DIAGNOSTIC_SEEDS
    )
    readout = tuple(
        cell("hybrid", gamma=HYBRID_GAMMA, split_layer=READOUT_SPLIT, seed=seed)
        for seed in DIAGNOSTIC_SEEDS
    )
    first, last = DIAGNOSTIC_SEEDS[0], DIAGNOSTIC_SEEDS[-1]
    ladder = tuple(
        readout[0]
        if trunk_lr == 1.0
        else cell(
            "hybrid",
            gamma=HYBRID_GAMMA,
            split_layer=READOUT_SPLIT,
            trunk_lr=trunk_lr,
            seed=first,
        )
        for trunk_lr in TRUNK_LR_LADDER
    )
    best = max(ladder, key=lambda measured: measured.val_acc)
    return _split_report(
        point=point,
        reference=reference,
        baseline=baseline,
        readout=readout,
        ladder=ladder,
        confirmation=readout[-1]
        if best.trunk_lr == 1.0
        else cell(
            "hybrid",
            gamma=HYBRID_GAMMA,
            split_layer=READOUT_SPLIT,
            trunk_lr=best.trunk_lr,
            seed=last,
        ),
    )


def run_split_diagnostic(
    point: PilotPoint = BOX,
    *,
    device: str = "cuda",
    log_path: Path | None = None,
) -> SplitPositionReport:
    """Measure the split's position and the trunk's step at the box.

    Args:
        point: The pilot box the T6a2 trigger names.
        device: ``"cuda"`` is required -- the cells need a measured peak.
        log_path: Where each measured cell is appended; a rerun reuses it.

    Raises:
        RuntimeError: On a non-CUDA device.
    """
    _require_cuda(device)
    log = _CellLog(log_path)
    data = cifar_splits()

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        split_layer: int = REGISTERED_SPLIT,
        trunk_lr: float = 1.0,
        seed: int,
    ) -> DiagnosticCell:
        return log.measure(
            arm,
            gamma=gamma,
            train_biases=train_biases,
            split_layer=split_layer,
            trunk_lr=trunk_lr,
            seed=seed,
            point=point,
            device=device,
            data=data,
        )

    return _assemble_split(cell, point=point)


def replay_split_diagnostic(
    *, log_path: Path, point: PilotPoint = BOX
) -> SplitPositionReport:
    """Rebuild T6e's report from the cell log, without training a cell.

    Raises:
        RuntimeError: When a cell the report needs is missing from the log.
    """
    cells = read_cells(log_path)
    if not cells:
        raise RuntimeError(f"no cells in {log_path}; run the diagnostic first")

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        split_layer: int = REGISTERED_SPLIT,
        trunk_lr: float = 1.0,
        seed: int,
    ) -> DiagnosticCell:
        key = (arm, gamma, train_biases, seed, split_layer, trunk_lr, False, False)
        if key not in cells:
            raise RuntimeError(f"no measured cell for {key} in {log_path}")
        return cells[key]

    return _assemble_split(cell, point=point)


def _split_markdown(report: SplitPositionReport) -> str:
    """The table a third party can read, with its rulers and its command."""
    point = report.point
    lines = [
        "# T6e -- the split's position (TODO93 track A)",
        "",
        f"**Box.** CIFAR-10 10k/10k, L={point.depth}, W={point.width}, "
        f"B={point.batch}, {point.steps} steps, LR {report.lr:g}, seeds "
        f"{', '.join(str(seed) for seed in DIAGNOSTIC_SEEDS)}, fp32. "
        f"Reference `{REFERENCE_ARM}`; split positions {SPLIT_LADDER} "
        f"(`{READOUT_SPLIT}` = a readout-only head); trunk steps "
        f"{TRUNK_LR_LADDER} on the registered gamma={HYBRID_GAMMA:g}.",
        "",
        f"Reference {report.reference_acc:.3f}; baseline "
        f"{report.baseline_acc:.3f}; floor {report.floor:.3f} (reference - "
        f"{DELTA * 100:.0f} pp).",
        "",
        "| mechanism | position | trunk lr | seeds | val acc | sd | gain | "
        "activations MB | ratio | floor | reaches |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in report.rows:
        activations = (
            f"{row.activations_mb:.0f}" if row.activations_mb is not None else "—"
        )
        ratio = (
            f"{row.activation_ratio:.2f}x" if row.activation_ratio is not None else "—"
        )
        position = "registered" if row.split_layer < 0 else f"layer {row.split_layer}"
        lines.append(
            f"| `{row.mechanism}` | {position} | {row.trunk_lr:g} | {row.n} | "
            f"{row.val_acc:.3f} | {row.val_acc_sd:.3f} | {row.gain * 100:+.1f} pp "
            f"| {activations} | {ratio} | {row.floor:.3f} | "
            f"{'yes' if row.reaches_floor else 'no'} |"
        )
    lines.extend([
        "",
        "| arm | gamma | split | trunk lr | seed | val acc | s | activations MB "
        "| peak MB |",
        "|---|---|---|---|---|---|---|---|---|",
    ])
    for cell in report.cells:
        position = "registered" if cell.split_layer < 0 else str(cell.split_layer)
        activations = (
            f"{cell.activations_mb:.0f}" if cell.activations_mb is not None else "—"
        )
        peak = f"{cell.peak_mb:.0f}" if cell.peak_mb is not None else "—"
        lines.append(
            f"| `{cell.arm}` | {cell.gamma:g} | {position} | {cell.trunk_lr:g} | "
            f"{cell.seed} | {cell.val_acc:.3f} | {cell.walltime_s:.1f} | "
            f"{activations} | {peak} |"
        )
    lines.extend([
        "",
        f"**Gate outcome: {report.verdict}** -- a box statement at the pilot "
        "box; the measurement stands and the mechanism stays open.",
        "",
        f"**Trigger.** {report.trigger}",
        "",
        "**Rulers.** val acc on the full 10k test split (1 sigma ~ 0.3 pp); "
        "activation bytes (peak - params - optimizer - auxiliary); walltime per "
        "cell; the floor is the checkpointed arm's mean minus delta, and the "
        "baseline is the registered hybrid at the same box.",
        "",
        "Command: `uv run python -m computronium.validation.hybrid_update "
        "--split`; replay the gate from the cell log with `... --split --replay`.",
        "",
    ])
    return "\n".join(lines)


def write_split_report(report: SplitPositionReport, output_dir: str | Path) -> Path:
    """Write ``split_position.json`` and ``split_position.md``; return the JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "split_position.json"
    path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    (output_dir / "split_position.md").write_text(
        _split_markdown(report), encoding="utf-8"
    )
    return path


@dataclass(frozen=True, slots=True)
class DirectionRow:
    """One direction's mean over its seeds, against the reference's floor.

    ``mechanism`` is the ladder's label (``orthogonal`` or ``learned``);
    both are read at the registered gamma and split, so the row prices
    the trunk's direction alone.
    """

    mechanism: str
    n: int
    val_acc: float
    val_acc_sd: float
    gain: float
    activations_mb: float | None
    activation_ratio: float | None
    floor: float

    @property
    def reaches_floor(self) -> bool:
        return self.val_acc >= self.floor


@dataclass(frozen=True, slots=True)
class DirectionReport:
    """T6f's measured cells, its direction rows, and the verdict."""

    point: PilotPoint
    lr: float
    reference: tuple[DiagnosticCell, ...]
    baseline: tuple[DiagnosticCell, ...]
    orthogonal: tuple[DiagnosticCell, ...]
    learned: tuple[DiagnosticCell, ...]
    confirmation: DiagnosticCell
    rows: tuple[DirectionRow, ...]
    floor: float
    verdict: str
    mechanism: str
    reason: str
    trigger: str
    triage: str = "defect probe (a box statement; the measurement stands)"
    date: str = DATE

    @property
    def reference_acc(self) -> float:
        return fmean(cell.val_acc for cell in self.reference)

    @property
    def baseline_acc(self) -> float:
        return fmean(cell.val_acc for cell in self.baseline)

    @property
    def cells(self) -> tuple[DiagnosticCell, ...]:
        """Every measured cell once, keyed by its identity."""
        unique: dict[CellKey, DiagnosticCell] = {}
        for cell in (
            *self.reference,
            *self.baseline,
            *self.orthogonal,
            *self.learned,
            self.confirmation,
        ):
            unique.setdefault(_key(cell), cell)
        return tuple(unique.values())

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date,
            "point": asdict(self.point) | {"lr": self.lr},
            "reference_acc": round(self.reference_acc, 4),
            "baseline_acc": round(self.baseline_acc, 4),
            "floor": round(self.floor, 4),
            "verdict": self.verdict,
            "triage": self.triage,
            "mechanism": self.mechanism,
            "reason": self.reason,
            "trigger": self.trigger,
            "rows": [asdict(row) for row in self.rows],
            "cells": [asdict(cell) for cell in self.cells],
        }


def _direction_row(
    mechanism: str,
    cells: tuple[DiagnosticCell, ...],
    *,
    baseline_acc: float,
    reference: tuple[DiagnosticCell, ...],
    floor: float,
) -> DirectionRow:
    """One direction's mean, its gain, and its memory half."""
    acc, spread = _mean_acc(cells)
    return DirectionRow(
        mechanism=mechanism,
        n=len(cells),
        val_acc=acc,
        val_acc_sd=spread,
        gain=acc - baseline_acc,
        activations_mb=_mean_mb(cells),
        activation_ratio=_ratio(cells, reference),
        floor=floor,
    )


def direction_gate(  # ruff: ignore[too-many-arguments]
    *,
    reference_acc: float,
    baseline_acc: float,
    rows: tuple[DirectionRow, ...],
    floor: float,
    delta: float = DELTA,
    learning_floor: float = LEARNING_FLOOR,
) -> UpdateVerdict:
    """Control, promote a direction that reaches the floor, then refuse.

    Both directions are read at the registered gamma and split, so a
    reading that moves nothing refuses the direction itself -- not the
    scale (T6d) and not the position or the step (T6e). The next
    variable is then the trunk's *geometry*: a residual or a wider
    trunk, never another pass over the same box.
    """
    if reference_acc < max(floor, learning_floor):
        return UpdateVerdict(
            "invalid",
            "the checkpointed reference",
            (
                f"the reference reads {reference_acc:.3f} against the floor "
                f"{floor:.3f} at the pilot box; a reference that does not "
                "train cannot decide the trunk's direction"
            ),
            "re-measure the reference at the pilot box; the diagnostic is "
            "read on the next run",
        )
    promoted = [row for row in rows if row.reaches_floor]
    if promoted:
        best = max(promoted, key=lambda row: row.val_acc)
        return UpdateVerdict(
            "promote",
            f"the trunk's direction: a {best.mechanism} feedback matrix",
            (
                f"the {best.mechanism} direction reads {best.val_acc:.3f} (sd "
                f"{best.val_acc_sd:.3f} over {best.n} seeds) against the floor "
                f"{floor:.3f} = checkpoint {reference_acc:.3f} - "
                f"{delta * 100:.0f} pp, up {best.gain * 100:+.1f} pp from the "
                f"registered draw's {baseline_acc:.3f} at "
                f"{_ratio_text(best.activation_ratio)}"
            ),
            (
                "the claim run re-registers at the pilot box with this "
                "direction frozen: the accuracy bar is demonstrated at L=8, so "
                "the claim box's L=8->32 rung prices it next; the memory half "
                "is measured at this box"
            ),
        )
    best = max(rows, key=lambda row: row.val_acc)
    if best.gain >= delta:
        return UpdateVerdict(
            "coordinate",
            f"the {best.mechanism} direction is a real gain, not the mechanism",
            (
                f"the {best.mechanism} direction moves the hybrid "
                f"{best.gain * 100:+.1f} pp to {best.val_acc:.3f} (sd "
                f"{best.val_acc_sd:.3f} over {best.n} seeds) but the floor is "
                f"{floor:.3f} = checkpoint {reference_acc:.3f} - "
                f"{delta * 100:.0f} pp; the gap narrows and does not close"
            ),
            (
                "the next edge on the same direction (its ridge rate or a "
                "second rotation) or a residual/wider trunk; a claim run is not "
                "scheduled on a coordinate"
            ),
        )
    readings = "/".join(f"{row.val_acc:.3f}" for row in rows)
    return UpdateVerdict(
        "refuse",
        "the trunk's geometry: a residual or a wider trunk (the fix queue)",
        (
            f"the directions read {readings} ({'/'.join(f'{row.gain * 100:+.1f} pp' for row in rows)} "
            f"from the registered draw {baseline_acc:.3f}, sd "
            f"{'/'.join(f'{row.val_acc_sd:.3f}' for row in rows)} over "
            f"{'/'.join(str(row.n) for row in rows)} seeds) at gamma="
            f"{HYBRID_GAMMA:g} and the registered split, so neither rotation "
            f"nor the ridge fit moves the cell at this box, at "
            f"{_ratio_text(rows[0].activation_ratio)}; the direction is a "
            "defect probe, not a verdict on the mechanism"
        ),
        (
            "the trunk's geometry: a residual trunk (the skip the split keeps) "
            "or a wider trunk; the direction is priced at this box, so the "
            "next variable is the stack the direction feeds, not another "
            "projection"
        ),
    )


def _direction_report(
    *,
    point: PilotPoint,
    reference: tuple[DiagnosticCell, ...],
    baseline: tuple[DiagnosticCell, ...],
    orthogonal: tuple[DiagnosticCell, ...],
    learned: tuple[DiagnosticCell, ...],
    confirmation: DiagnosticCell,
) -> DirectionReport:
    """Assemble the rows and the gate from the measured cells."""
    floor = _floor(reference)
    baseline_acc, _ = _mean_acc(baseline)
    rows = tuple(
        _direction_row(
            label,
            cells,
            baseline_acc=baseline_acc,
            reference=reference,
            floor=floor,
        )
        for label, cells in (("orthogonal", orthogonal), ("learned", learned))
    )
    reference_acc, _ = _mean_acc(reference)
    gate = direction_gate(
        reference_acc=reference_acc,
        baseline_acc=baseline_acc,
        rows=rows,
        floor=floor,
    )
    return DirectionReport(
        point=point,
        lr=LR,
        reference=reference,
        baseline=baseline,
        orthogonal=orthogonal,
        learned=learned,
        confirmation=confirmation,
        rows=rows,
        floor=floor,
        verdict=gate.verdict,
        mechanism=gate.mechanism,
        reason=gate.reason,
        trigger=gate.trigger,
    )


def _assemble_direction(
    cell: Callable[..., DiagnosticCell], *, point: PilotPoint
) -> DirectionReport:
    """T6f's cell plan: reference, baseline, both directions, confirmation.

    The registered arms are the T6d/T6e cells, so a run with the shared
    log retrains only the direction's cells: two seeds per direction plus
    the best direction's second seed. The registered draw is the
    baseline cell, so the ladder prices the direction alone.
    """
    reference = tuple(
        cell(REFERENCE_ARM, gamma=HYBRID_GAMMA, seed=seed) for seed in DIAGNOSTIC_SEEDS
    )
    baseline = tuple(
        cell("hybrid", gamma=HYBRID_GAMMA, seed=seed) for seed in DIAGNOSTIC_SEEDS
    )
    ladder: dict[str, tuple[DiagnosticCell, ...]] = {
        label: tuple(
            cell(
                "hybrid",
                gamma=HYBRID_GAMMA,
                orthogonal_init=orthogonal,
                learned_feedback=learned,
                seed=seed,
            )
            for seed in DIAGNOSTIC_SEEDS
        )
        for label, orthogonal, learned in DIRECTION_LADDER
    }
    best_label = max(
        ladder,
        key=lambda label: fmean(cell.val_acc for cell in ladder[label]),
    )
    orthogonal, learned = next(
        (rotated, fitted)
        for label, rotated, fitted in DIRECTION_LADDER
        if label == best_label
    )
    return _direction_report(
        point=point,
        reference=reference,
        baseline=baseline,
        orthogonal=ladder["orthogonal"],
        learned=ladder["learned"],
        confirmation=cell(
            "hybrid",
            gamma=HYBRID_GAMMA,
            orthogonal_init=orthogonal,
            learned_feedback=learned,
            seed=CONFIRMATION_SEED,
        ),
    )


def run_direction_diagnostic(
    point: PilotPoint = BOX,
    *,
    device: str = "cuda",
    log_path: Path | None = None,
) -> DirectionReport:
    """Measure the trunk's two directions (T6f) at the pilot box.

    Args:
        point: The pilot box the T6a2 trigger names.
        device: ``"cuda"`` is required -- the cells need a measured peak.
        log_path: Where each measured cell is appended; a rerun reuses it.

    Raises:
        RuntimeError: On a non-CUDA device.
    """
    _require_cuda(device)
    log = _CellLog(log_path)
    data = cifar_splits()

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        orthogonal_init: bool = False,
        learned_feedback: bool = False,
        seed: int,
    ) -> DiagnosticCell:
        return log.measure(
            arm,
            gamma=gamma,
            train_biases=train_biases,
            orthogonal_init=orthogonal_init,
            learned_feedback=learned_feedback,
            seed=seed,
            point=point,
            device=device,
            data=data,
        )

    return _assemble_direction(cell, point=point)


def replay_direction_diagnostic(
    *, log_path: Path, point: PilotPoint = BOX
) -> DirectionReport:
    """Rebuild T6f's report from the cell log, without training a cell.

    Raises:
        RuntimeError: When a cell the report needs is missing from the log.
    """
    cells = read_cells(log_path)
    if not cells:
        raise RuntimeError(f"no cells in {log_path}; run the diagnostic first")

    def cell(
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        orthogonal_init: bool = False,
        learned_feedback: bool = False,
        seed: int,
    ) -> DiagnosticCell:
        key = (
            arm,
            gamma,
            train_biases,
            seed,
            REGISTERED_SPLIT,
            1.0,
            orthogonal_init,
            learned_feedback,
        )
        if key not in cells:
            raise RuntimeError(f"no measured cell for {key} in {log_path}")
        return cells[key]

    return _assemble_direction(cell, point=point)


def _direction_markdown(report: DirectionReport) -> str:
    """The table a third party can read, with its rulers and its command."""
    point = report.point
    lines = [
        "# T6f -- the trunk's direction (TODO93 track A)",
        "",
        f"**Box.** CIFAR-10 10k/10k, L={point.depth}, W={point.width}, "
        f"B={point.batch}, {point.steps} steps, LR {report.lr:g}, seeds "
        f"{', '.join(str(seed) for seed in DIAGNOSTIC_SEEDS)}, fp32. "
        f"Reference `{REFERENCE_ARM}`; registered draw `hybrid`; directions "
        f"`{'`, `'.join(label for label, _, _ in DIRECTION_LADDER)}` at "
        f"gamma={HYBRID_GAMMA:g}, split registered, norm-matched.",
        "",
        f"Reference {report.reference_acc:.3f}; registered draw "
        f"{report.baseline_acc:.3f}; floor {report.floor:.3f} (reference - "
        f"{DELTA * 100:.0f} pp).",
        "",
        "| direction | seeds | val acc | sd | gain | floor | reaches | "
        "activations MB | ratio |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in report.rows:
        activations = (
            f"{row.activations_mb:.0f}" if row.activations_mb is not None else "—"
        )
        ratio = (
            f"{row.activation_ratio:.2f}x" if row.activation_ratio is not None else "—"
        )
        lines.append(
            f"| {row.mechanism} | {row.n} | {row.val_acc:.3f} | "
            f"{row.val_acc_sd:.3f} | {row.gain * 100:+.1f} pp | "
            f"{row.floor:.3f} | {'yes' if row.reaches_floor else 'no'} | "
            f"{activations} | {ratio} |"
        )
    lines.extend([
        "",
        "| arm | gamma | direction | seed | val acc | s | activations MB | peak MB |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for cell in report.cells:
        direction = (
            "learned"
            if cell.learned_feedback
            else "orthogonal"
            if cell.orthogonal_init
            else "random"
        )
        activations = (
            f"{cell.activations_mb:.0f}" if cell.activations_mb is not None else "—"
        )
        peak = f"{cell.peak_mb:.0f}" if cell.peak_mb is not None else "—"
        lines.append(
            f"| `{cell.arm}` | {cell.gamma:g} | {direction} | {cell.seed} | "
            f"{cell.val_acc:.3f} | {cell.walltime_s:.1f} | {activations} | {peak} |"
        )
    lines.extend([
        "",
        f"**Gate outcome: {report.verdict}** -- a box statement at the pilot "
        "box; the measurement stands and the mechanism stays open.",
        "",
        f"**Triage.** {report.triage}; the fix queue is {report.trigger}",
        "",
        f"**Reason.** {report.reason}",
        "",
        "**Rulers.** val acc on the full 10k test split (1 sigma ~ 0.3 pp); "
        "activation bytes (peak - params - optimizer - auxiliary); walltime per "
        "cell; the floor is the checkpointed arm's mean minus delta, and the "
        "baseline is the registered draw at the same box.",
        "",
        "Command: `uv run python -m computronium.validation.hybrid_update "
        "--direction`; replay the gate from the cell log with `... --direction "
        "--replay`.",
        "",
    ])
    return "\n".join(lines)


def write_direction_report(report: DirectionReport, output_dir: str | Path) -> Path:
    """Write ``direction.json`` and ``direction.md``; return the JSON."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "direction.json"
    path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    (output_dir / "direction.md").write_text(
        _direction_markdown(report), encoding="utf-8"
    )
    return path


def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--device", default="cuda" if torch.cuda.is_available() else "cpu"
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="measure the cells (the default; kept for symmetry with --replay)",
    )
    parser.add_argument(
        "--replay", action="store_true", help="rebuild the gate from the cell log"
    )
    parser.add_argument(
        "--split",
        action="store_true",
        help="run T6e (the split's position and the trunk's step) instead of T6d",
    )
    parser.add_argument(
        "--direction",
        action="store_true",
        help="run T6f (the trunk's orthogonal and learned direction) instead of T6d",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    log_path = args.out / "hybrid_update.cells.jsonl"
    if args.direction:
        direction = (
            replay_direction_diagnostic(log_path=log_path)
            if args.replay
            else run_direction_diagnostic(device=args.device, log_path=log_path)
        )
        logger.info(
            "T6f: reference=%.3f baseline=%.3f floor=%.3f rows=%s",
            direction.reference_acc,
            direction.baseline_acc,
            direction.floor,
            json.dumps([
                {
                    "mechanism": row.mechanism,
                    "val_acc": round(row.val_acc, 3),
                    "n": row.n,
                    "gain": round(row.gain, 3),
                    "reaches_floor": row.reaches_floor,
                }
                for row in direction.rows
            ]),
        )
        path = write_direction_report(direction, args.out)
        logger.info("wrote %s", path)
        logger.info("gate outcome: %s -- a box statement; %s", direction.verdict, direction.mechanism)
        return
    if args.split:
        splits = (
            replay_split_diagnostic(log_path=log_path)
            if args.replay
            else run_split_diagnostic(device=args.device, log_path=log_path)
        )
        logger.info(
            "T6e: reference=%.3f baseline=%.3f floor=%.3f rows=%s",
            splits.reference_acc,
            splits.baseline_acc,
            splits.floor,
            json.dumps([
                {
                    "mechanism": row.mechanism,
                    "split_layer": row.split_layer,
                    "trunk_lr": row.trunk_lr,
                    "val_acc": round(row.val_acc, 3),
                    "n": row.n,
                    "gain": round(row.gain, 3),
                    "reaches_floor": row.reaches_floor,
                }
                for row in splits.rows
            ]),
        )
        path = write_split_report(splits, args.out)
        logger.info("wrote %s", path)
        logger.info("gate outcome: %s -- a box statement; %s", splits.verdict, splits.mechanism)
        return
    report = (
        replay_diagnostic(log_path=log_path)
        if args.replay
        else run_diagnostic(device=args.device, log_path=log_path)
    )
    logger.info(
        "T6d: reference=%.3f baseline=%.3f floor=%.3f best gamma=%g rows=%s",
        report.reference_acc,
        report.baseline_acc,
        report.floor,
        report.best_gamma,
        json.dumps([
            {
                "mechanism": row.mechanism,
                "gamma": row.gamma,
                "val_acc": round(row.val_acc, 3),
                "gain": round(row.gain, 3),
                "reaches_floor": row.reaches_floor,
            }
            for row in report.rows
        ]),
    )
    logger.info("head-only: %.3f", report.head_only.val_acc)
    path = write_report(report, args.out)
    logger.info("wrote %s", path)
    logger.info("gate outcome: %s -- a box statement; %s", report.verdict, report.mechanism)


if __name__ == "__main__":
    _main()
