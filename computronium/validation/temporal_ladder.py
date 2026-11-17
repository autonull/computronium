"""T1 — the temporal axis's rung ladder (TODO93 §19, order 1).

The three temporal credits were locked on the sequence contract but no
pipeline ran it: every loader yielded 2-D batches, so a temporal credit was
reachable only from its own fixture. This ticket closes that gap — the
geometry's time axis, a time-major loader, and the trainer's per-step loss —
and asks the cheapest question that decides the build is **wired**:

- **rung 0**: the forward returns ``(time, batch, classes)`` for the batch
  the loader yields, the credit's update is non-zero, and the credit reads
  the target (``error_blind=False``);
- **rung 1**: one cell with ``eligibility_prop`` trains above chance;
- **rung 2**: the 3-point LR ladder at 1e-3/1e-2/1e-1 with the upper
  extension at 3e-1 (the measured best was the edge, C1's precedent), then
  one confirmation seed at the best point.

The box is the synthetic delayed cue (``delayed_cue``): a one-hot class at
step 2 of 12, noise elsewhere, and the class as the label at *every* step,
so the hidden state must carry the cue forward. Chance is 1/10. The
``rtrl_reference`` arm is the exact rule on the same box: when it reaches
the floor and the treatment does not, the box is sound and the treatment's
mechanism is the finding; when the reference itself misses the floor, the
run is invalid rather than the treatment being refused.

Run it with::

    uv run python -m computronium.validation.temporal_ladder
    uv run python -m computronium.validation.temporal_ladder --replay
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

import torch

if TYPE_CHECKING:
    from computronium.ontology.credit import CreditAssignment
    from computronium.ontology.system import System

logger = logging.getLogger(__name__)

__all__ = [
    "BOX",
    "CHANCE",
    "CONFIRM_SEED",
    "DATE",
    "FLOOR",
    "LADDER_SEED",
    "LR_LADDER",
    "REFERENCE_ARM",
    "TREATMENT_ARM",
    "TemporalCell",
    "TemporalReport",
    "read_cells",
    "replay_temporal_ladder",
    "run_temporal_ladder",
    "write_temporal_report",
]

DATE = "2026-11-17"


@dataclass(frozen=True, slots=True)
class TemporalBox:
    """The declared box: one task, one geometry, one budget."""

    task: str = "delayed_cue"
    time: int = 12
    cue_step: int = 2
    classes: int = 10
    hidden: int = 32
    batch: int = 64
    epochs: int = 3
    n_train: int = 1024
    n_val: int = 512

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


BOX = TemporalBox()
CHANCE = 1.0 / BOX.classes
#: Viability floor: 2.5x chance (the atlas's declared bar).
FLOOR = 0.25
LR_LADDER = (1e-3, 1e-2, 1e-1, 3e-1)
LADDER_SEED = 71
CONFIRM_SEED = 72
TREATMENT_ARM = "eligibility_prop"
REFERENCE_ARM = "rtrl_reference"
DEFAULT_OUT = Path("results/t93_temporal")


@dataclass(frozen=True, slots=True)
class TemporalCell:
    """One measured cell: the rung-0 gates and the learning ruler."""

    arm: str
    stage: str
    seed: int
    lr: float
    epochs: int
    val_acc: float
    train_acc: float
    update_norm: float
    shapes_ok: bool
    time_s: float

    @property
    def wired(self) -> bool:
        """Rung 0: shapes, a non-zero update, and a target-reading credit."""
        return self.shapes_ok and self.update_norm > 0.0


@dataclass(frozen=True, slots=True)
class TemporalReport:
    """The ladder: every cell, the gate, and the mechanism it names."""

    stage: str
    box: dict[str, object]
    cells: tuple[TemporalCell, ...]
    best_lr: float
    best_val: float
    confirm_val: float | None
    reference_val: float | None
    verdict: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "date": DATE,
            "box": self.box,
            "chance": CHANCE,
            "floor": FLOOR,
            "best_lr": self.best_lr,
            "best_val": self.best_val,
            "confirm_val": self.confirm_val,
            "reference_val": self.reference_val,
            "verdict": self.verdict,
            "reason": self.reason,
            "cells": [asdict(cell) for cell in self.cells],
        }


def _credit(arm: str):
    """The arm's credit; both arms read the time-major state."""
    from computronium.ontology.credit import (
        CreditAssignmentConfig,
        EligibilityPropCredit,
        RTRLReference,
    )

    match arm:
        case "eligibility_prop":
            return EligibilityPropCredit(CreditAssignmentConfig.eligibility_prop())
        case "rtrl_reference":
            return RTRLReference(CreditAssignmentConfig.rtrl_reference())
        case _:
            raise ValueError(f"unknown temporal arm: {arm!r}")


def _build(arm: str, seed: int, lr: float) -> System:
    """The declared box: one geometry, one credit, one update."""
    from computronium import (
        DigitalSubstrate,
        EuclideanUpdate,
        InstantaneousDynamics,
        NullPlasticity,
        ParameterUpdateConfig,
        StateDynamicsConfig,
        SubstrateConfig,
        compose_joint_system,
    )
    from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry

    torch.manual_seed(seed)
    return compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=RecurrentGeometry(
            GeometryConfig.recurrent(
                input_dim=BOX.classes,
                output_dim=BOX.classes,
                hidden_dims=(BOX.hidden,),
                sequence=True,
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        plasticity=NullPlasticity(),
        credit=cast("CreditAssignment", _credit(arm)),
        update=EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=lr, grad_clip=1e9)
        ),
    )


def _displacement(before: dict[str, torch.Tensor], system: System) -> float:
    """The total parameter displacement of the epoch (rung 0's non-zero update)."""
    total = torch.zeros(())
    for name, value in before.items():
        # A live accumulator, not an autograd leaf: the update is measured.
        total += ((system.geometry.params[name].detach() - value) ** 2).sum()
    return float(total.sqrt())


def _measure(arm: str, stage: str, seed: int, lr: float, task) -> TemporalCell:
    """One cell: rung-0 gates, then one epoch loop at the declared box."""
    from computronium import SystemTrainer, SystemTrainerConfig

    system = _build(arm, seed, lr)
    batch_x, _ = next(iter(task.train_dataloader))
    logits = system.forward(batch_x)
    shapes_ok = tuple(logits.shape) == (
        BOX.time,
        batch_x.shape[1],
        BOX.classes,
    )
    before = {
        name: param.detach().clone() for name, param in system.geometry.params.items()
    }
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=BOX.epochs,
            device="cpu",
            seed=seed,
        ),
        train_data=task.train_dataloader,
        val_data=task.val_dataloader,
    )
    start = time.perf_counter()
    history = trainer.fit()
    walltime_s = time.perf_counter() - start
    last = history[-1]
    return TemporalCell(
        arm=arm,
        stage=stage,
        seed=seed,
        lr=lr,
        epochs=BOX.epochs,
        val_acc=float(last.get("val_acc", 0.0)),
        train_acc=float(last.get("train_acc", 0.0)),
        update_norm=_displacement(before, system),
        shapes_ok=shapes_ok,
        time_s=walltime_s,
    )


def _gate(
    cells: tuple[TemporalCell, ...],
) -> tuple[float, float, float | None, float | None, str, str]:
    """The pre-registered gate: reference control, floor, then confirmation."""
    ladder = [cell for cell in cells if cell.stage == "ladder"]
    confirm = next((cell for cell in cells if cell.stage == "confirm"), None)
    reference = next((cell for cell in cells if cell.arm == REFERENCE_ARM), None)
    if not ladder:
        raise ValueError("the ladder has no cells; nothing to gate")
    best = max(ladder, key=lambda cell: cell.val_acc)
    reference_val = None if reference is None else reference.val_acc
    confirm_val = None if confirm is None else confirm.val_acc
    if any(not cell.wired for cell in cells):
        return (
            best.lr,
            best.val_acc,
            confirm_val,
            reference_val,
            "invalid-box",
            "a cell failed rung 0 (shapes or a zero update); the build is not wired",
        )
    if reference_val is not None and reference_val < FLOOR:
        return (
            best.lr,
            best.val_acc,
            confirm_val,
            reference_val,
            "invalid-box",
            "the exact reference misses the viability floor: the box, not the "
            "treatment, is the finding",
        )
    if best.val_acc < FLOOR:
        return (
            best.lr,
            best.val_acc,
            confirm_val,
            reference_val,
            "refuse",
            "the treatment misses the floor at every declared LR; the next edge "
            "is the trace's decay or the fixture's depth, not a new verdict",
        )
    if confirm_val is not None and confirm_val >= FLOOR:
        return (
            best.lr,
            best.val_acc,
            confirm_val,
            reference_val,
            "promote",
            "the treatment clears the floor at its best LR on both seeds",
        )
    return (
        best.lr,
        best.val_acc,
        confirm_val,
        reference_val,
        "coordinate",
        "the best point clears the floor but its confirmation seed does not: "
        "the gain is a coordinate at this box, not a claim",
    )


def read_cells(log_path: Path) -> list[TemporalCell]:
    """Read the kill-safe cell log (one JSON object per line)."""
    cells: list[TemporalCell] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        cells.append(TemporalCell(**payload))
    return cells


def _write_cell(log_path: Path, cell: TemporalCell) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(cell)) + "\n")


def _report(stage: str, cells: tuple[TemporalCell, ...]) -> TemporalReport:
    best_lr, best_val, confirm_val, reference_val, verdict, reason = _gate(cells)
    return TemporalReport(
        stage=stage,
        box=BOX.to_dict(),
        cells=cells,
        best_lr=best_lr,
        best_val=best_val,
        confirm_val=confirm_val,
        reference_val=reference_val,
        verdict=verdict,
        reason=reason,
    )


def run_temporal_ladder(*, log_path: Path | None = None) -> TemporalReport:
    """Measure the ladder, the confirmation, and the exact reference."""
    from computronium.domains.factory import create_task

    log_path = log_path or DEFAULT_OUT / "temporal_ladder.cells.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.unlink(missing_ok=True)
    task = create_task(
        BOX.task,
        device="cpu",
        quick_mode=False,
        time=BOX.time,
        cue_step=BOX.cue_step,
        classes=BOX.classes,
        n_train=BOX.n_train,
        n_val=BOX.n_val,
        batch_size=BOX.batch,
    )
    task.setup()
    cells: list[TemporalCell] = []
    ladder: list[TemporalCell] = []
    for lr in LR_LADDER:
        cell = _measure(TREATMENT_ARM, "ladder", LADDER_SEED, lr, task)
        _write_cell(log_path, cell)
        ladder.append(cell)
        cells.append(cell)
        logger.info(
            "%s lr=%g seed=%d val=%.3f train=%.3f update=%.2f %.2fs",
            cell.arm,
            cell.lr,
            cell.seed,
            cell.val_acc,
            cell.train_acc,
            cell.update_norm,
            cell.time_s,
        )
    best_lr = max(ladder, key=lambda cell: cell.val_acc).lr
    for stage, arm, seed, lr in (
        ("confirm", TREATMENT_ARM, CONFIRM_SEED, best_lr),
        ("reference", REFERENCE_ARM, LADDER_SEED, best_lr),
    ):
        cell = _measure(arm, stage, seed, lr, task)
        _write_cell(log_path, cell)
        cells.append(cell)
        logger.info(
            "%s %s lr=%g seed=%d val=%.3f %.2fs",
            stage,
            cell.arm,
            cell.lr,
            cell.seed,
            cell.val_acc,
            cell.time_s,
        )
    return _report("run", tuple(cells))


def replay_temporal_ladder(*, log_path: Path | None = None) -> TemporalReport:
    """Rebuild the gate from the cell log without training."""
    log_path = log_path or DEFAULT_OUT / "temporal_ladder.cells.jsonl"
    cells = read_cells(log_path)
    if not cells:
        raise ValueError(f"{log_path}: no cells to replay")
    return _report("replay", tuple(cells))


def _markdown(report: TemporalReport) -> str:
    lines = [
        "# T1 — the temporal axis's rung ladder (TODO93 §19)",
        "",
        f"Measured {DATE}. Box: {json.dumps(report.box)}; chance "
        f"{CHANCE:.2f}; floor {FLOOR:.2f}.",
        "",
        "| stage | arm | lr | seed | epochs | val acc | train acc | "
        "update | shapes | s |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cell in report.cells:
        lines.append(
            f"| {cell.stage} | `{cell.arm}` | {cell.lr:g} | {cell.seed} | "
            f"{cell.epochs} | {cell.val_acc:.3f} | {cell.train_acc:.3f} | "
            f"{cell.update_norm:.2f} | {'yes' if cell.shapes_ok else 'no'} | "
            f"{cell.time_s:.2f} |"
        )
    confirm = "—" if report.confirm_val is None else f"{report.confirm_val:.3f}"
    reference = "—" if report.reference_val is None else f"{report.reference_val:.3f}"
    lines.extend([
        "",
        f"**Gate outcome: {report.verdict}.** Best LR {report.best_lr:g} at "
        f"{report.best_val:.3f}; confirmation {confirm}; exact reference "
        f"{reference}; floor {FLOOR:.2f}.",
        "",
        f"**Reason.** {report.reason}",
        "",
        "**Rulers.** Held-out accuracy over the task's 512-cue validation set "
        "(the 1 sigma resolution is ~2.1 pp); chance 0.10; the floor is 2.5x "
        "chance; walltime per cell on CPU; the update norm is the epoch's total "
        "parameter displacement (rung 0's non-zero update).",
        "",
        "Command: `uv run python -m computronium.validation.temporal_ladder`; "
        "replay the gate from the cell log with `... --replay`.",
        "",
    ])
    return "\n".join(lines)


def write_temporal_report(
    report: TemporalReport, output_dir: str | Path = DEFAULT_OUT
) -> Path:
    """Write ``temporal_ladder.json`` and ``temporal_ladder.md``."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "temporal_ladder.json"
    path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    (output_dir / "temporal_ladder.md").write_text(_markdown(report), encoding="utf-8")
    return path


def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replay", action="store_true", help="rebuild the gate from the cell log"
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    log_path = args.out / "temporal_ladder.cells.jsonl"
    report = (
        replay_temporal_ladder(log_path=log_path)
        if args.replay
        else run_temporal_ladder(log_path=log_path)
    )
    logger.info(
        "T1: chance=%.2f floor=%.2f best lr=%g val=%.3f confirm=%s "
        "reference=%s verdict=%s",
        CHANCE,
        FLOOR,
        report.best_lr,
        report.best_val,
        "—" if report.confirm_val is None else f"{report.confirm_val:.3f}",
        "—" if report.reference_val is None else f"{report.reference_val:.3f}",
        report.verdict,
    )
    logger.info("reason: %s", report.reason)
    path = write_temporal_report(report, args.out)
    logger.info("wrote %s", path)


if __name__ == "__main__":
    _main()
