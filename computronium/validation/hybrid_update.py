"""T6d -- the hybrid's update diagnostic (TODO93 §8.1 ticket 12c).

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

The diagnostic is a screen, not a claim: eleven cells at most, disjoint
from the claim seeds, and priced rather than pre-registered. A mechanism
that lifts the hybrid to the checkpointed arm's floor earns the claim box;
a knob that moves it by at least delta without reaching the floor is a
coordinate with its next edge; a knob that moves nothing is a refusal that
names the mechanism and its trigger, not an algorithm verdict.

Run it with::

    uv run python -m computronium.validation.hybrid_update --run
    uv run python -m computronium.validation.hybrid_update --replay
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
    "DATE",
    "DIAGNOSTIC_SEEDS",
    "GAMMA_LADDER",
    "HEAD_ONLY_GAMMA",
    "LR",
    "REFERENCE_ARM",
    "SIBLING_ARM",
    "DiagnosticCell",
    "HybridUpdateReport",
    "MechanismRow",
    "UpdateVerdict",
    "read_cells",
    "replay_diagnostic",
    "run_diagnostic",
    "update_gate",
    "write_report",
]

#: The pilot box the T6a2 trigger names (L=8, W=1024, B=8192, 200 steps).
BOX = PilotPoint(depth=8, width=1024, batch=8192, steps=200)
#: The hybrid's frozen LR: the pilot ladder's best point, read per arm.
LR = 0.3
#: The trunk's modulation ladder; its first point is the registered arm.
GAMMA_LADDER = (HYBRID_GAMMA, 0.3, 1.0)
#: Zero modulation: the trunk's contrast is zero, so the head alone trains.
HEAD_ONLY_GAMMA = 0.0
#: The checkpointed arm: the reference the floor is read from.
REFERENCE_ARM = "backprop+ckpt"
#: The whole-stack local rule: the same trunk, no head (the sibling control).
SIBLING_ARM = "local"
#: Chance on the box's 10 classes: a trunk point that collapses reads this.
CHANCE = 1 / BOX.classes
#: Two screen seeds, both disjoint from :data:`CLAIM_SEEDS`.
DIAGNOSTIC_SEEDS = LADDER_SEEDS[:2]
DATE = "2026-11-17"
DEFAULT_OUT = Path("results/t93_a_stream")

type CellKey = tuple[str, float, bool, int]


@dataclass(frozen=True, slots=True)
class DiagnosticCell:
    """One measured cell: the arm's knob, its seed, and what it scored.

    The arm, gamma, and bias flag are the cell's identity: a cell log keyed
    on them replays a report without retraining anything.
    """

    arm: str
    gamma: float
    train_biases: bool
    seed: int
    val_acc: float
    walltime_s: float
    activations_mb: float | None
    peak_mb: float | None


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
            unique.setdefault(
                _key(cell.arm, cell.gamma, cell.train_biases, cell.seed), cell
            )
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


def _key(arm: str, gamma: float, train_biases: bool, seed: int) -> CellKey:
    return (arm, gamma, train_biases, seed)


def read_cells(path: Path) -> dict[CellKey, DiagnosticCell]:
    """The cells a previous run measured, keyed by arm, knob, flag, and seed."""
    if not path.exists():
        return {}
    cells: dict[CellKey, DiagnosticCell] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cell = DiagnosticCell(**json.loads(line))
            cells[_key(cell.arm, cell.gamma, cell.train_biases, cell.seed)] = cell
    return cells


class _CellLog:
    """The measured cells: a rerun reuses them and a replay reads them."""

    def __init__(self, path: Path | None) -> None:
        self.path = path
        self.cells = read_cells(path) if path is not None else {}

    def measure(
        self,
        arm: str,
        *,
        gamma: float,
        train_biases: bool = False,
        seed: int,
        point: PilotPoint,
        device: str,
        data: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    ) -> DiagnosticCell:
        key = _key(arm, gamma, train_biases, seed)
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
        key = _key(arm, gamma, train_biases, seed)
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
        "| arm | gamma | train biases | seed | val acc | s | activations MB | "
        "peak MB |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for cell in report.cells:
        activations = (
            f"{cell.activations_mb:.0f}" if cell.activations_mb is not None else "—"
        )
        peak = f"{cell.peak_mb:.0f}" if cell.peak_mb is not None else "—"
        lines.append(
            f"| `{cell.arm}` | {cell.gamma:g} | {cell.train_biases} | "
            f"{cell.seed} | {cell.val_acc:.3f} | {cell.walltime_s:.1f} | "
            f"{activations} | {peak} |"
        )
    lines.extend([
        "",
        f"**Verdict: {report.verdict}** -- {report.reason}",
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
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    log_path = args.out / "hybrid_update.cells.jsonl"
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
    logger.info("verdict: %s -- %s", report.verdict, report.mechanism)


if __name__ == "__main__":
    _main()
