"""C1: the batch-1 plasticity ladder (TODO93 §6, track C).

The first falsifier for streaming without replay is *plasticity*, not
retention: if a local credit cannot learn a task stream at batch 1, a
consolidation protocol has nothing to retain. This module runs that ladder.

**Stage 1 (plasticity).** A 3-point learning-rate ladder over the local
(PEPITA) arm and its exact-gradient control on SplitMNIST at batch 1, one
epoch per task, tasks presented once in the fixed order. The best point per
arm gets one disjoint confirmation seed. The gate is pre-registered: the
local arm's mean final accuracy must clear :data:`FLOOR` on **both** seeds,
and the backprop control must clear it too -- a control at chance invalidates
the run rather than promoting the treatment.

**Stage 2 (consolidation).** Only after stage 1 promotes. The best stage-1
learning rate is frozen; local x EWC and backprop x EWC then get a 3-point
consolidation-strength ladder. That is the C2 retention protocol, priced here
so the next session does not rebuild it.

**Rulers.** Each task's held-out split is 2000 samples (two classes), so the
binomial 1-sigma resolution of a per-task accuracy is ~1.1 pp. The floor is
0.55, pre-registered before the ladder, and is 4.5 sigma above chance.
Walltime and consolidation state are recorded per cell beside the metric.

Run it with::

    uv run python -m computronium.validation.plasticity_ladder \
        --stage plasticity --device cuda --out results/t93_c1
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import torch

from computronium.core.continual import CLConfig, run_continual_learning

logger = logging.getLogger(__name__)

__all__ = [
    "CHANCE",
    "EWC_LAMBDA_LADDER",
    "FLOOR",
    "LADDER_SEEDS",
    "LR_LADDER",
    "LadderCell",
    "LadderReport",
    "run_consolidation_ladder",
    "run_plasticity_ladder",
]

#: SplitMNIST tasks are binary; a collapsed predictor scores exactly this.
CHANCE = 0.5
#: Pre-registered viability floor (4.5 sigma above chance at 2000 samples/task).
FLOOR = 0.55
#: One ladder seed, one disjoint confirmation seed: the gate needs two.
LADDER_SEEDS = (41,)
CONFIRM_SEEDS = (42,)
LR_LADDER = (0.001, 0.01, 0.1)
EWC_LAMBDA_LADDER = (1.0, 10.0, 100.0)
PLASTICITY_ARMS = ("local", "backprop")
CONSOLIDATION_ARMS = ("local_ewc", "backprop_ewc")
TASKS = 5
HELD_OUT_PER_TASK = 2000
RESOLUTION = (0.25 / HELD_OUT_PER_TASK) ** 0.5


@dataclass(frozen=True, slots=True)
class LadderCell:
    """One measured cell: an arm at one knob point, one seed."""

    stage: str
    arm: str
    knob: float
    seed: int
    mean_final_acc: float
    last_task_acc: float
    backward_transfer: float
    avg_forgetting: float
    state_mb: float
    time_s: float
    accuracy_matrix: tuple[tuple[float, ...], ...]


@dataclass(frozen=True, slots=True)
class LadderReport:
    """The ladder's measured table and its pre-registered verdict."""

    stage: str
    box: dict[str, object]
    cells: tuple[LadderCell, ...]
    best: dict[str, LadderCell]
    confirmation: tuple[LadderCell, ...]
    verdict: str
    reason: str


def _run_cell(
    *,
    stage: str,
    arm: str,
    knob: float,
    seed: int,
    device: str,
    lr: float,
    ewc_lambda: float,
    progress: str | Path | None = None,
) -> LadderCell:
    """Run one continual-learning cell and read its metric and resource rulers."""
    config = CLConfig(
        batch_size=1,
        epochs_per_task=1,
        lr=lr,
        ewc_lambda=ewc_lambda,
        hidden_dim=256,
        seed=seed,
        device=device,
        num_workers=0,
    )
    start = time.perf_counter()
    metrics = run_continual_learning(arm, config, "task_incremental")
    elapsed = time.perf_counter() - start
    cell = LadderCell(
        stage=stage,
        arm=arm,
        knob=knob,
        seed=seed,
        mean_final_acc=sum(metrics.final_accuracies) / len(metrics.final_accuracies),
        last_task_acc=metrics.final_accuracies[-1],
        backward_transfer=metrics.backward_transfer,
        avg_forgetting=metrics.avg_forgetting,
        state_mb=metrics.plastic_state_bytes / 1024**2,
        time_s=elapsed,
        accuracy_matrix=tuple(tuple(row) for row in metrics.accuracy_matrix),
    )
    return _emit(cell, progress)


def _emit(cell: LadderCell, progress: str | Path | None) -> LadderCell:
    """Append one finished cell to the progress log, so a kill keeps evidence."""
    if progress is not None:
        path = Path(progress)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(cell)) + "\n")
    return cell


def _summarise(cells: tuple[LadderCell, ...]) -> dict[str, LadderCell]:
    """Best ladder point per arm, ranked by mean final accuracy."""
    best: dict[str, LadderCell] = {}
    for cell in cells:
        incumbent = best.get(cell.arm)
        if incumbent is None or cell.mean_final_acc > incumbent.mean_final_acc:
            best[cell.arm] = cell
    return best


def _verdict(
    best: dict[str, LadderCell],
    confirmation: tuple[LadderCell, ...],
) -> tuple[str, str]:
    """Apply the pre-registered gate: floor on both seeds, control valid."""
    control = best.get("backprop")
    if control is None or control.mean_final_acc < FLOOR:
        acc = "missing" if control is None else f"{control.mean_final_acc:.3f}"
        return "invalid-control", f"backprop control below floor {FLOOR} ({acc})"
    local = best.get("local")
    if local is None:
        return "invalid-control", "no local cell measured"
    confirmed = [c for c in confirmation if c.arm == "local"]
    if not confirmed:
        return "promote-provisional", "local above floor, confirmation seed absent"
    second = confirmed[0]
    if local.mean_final_acc >= FLOOR and second.mean_final_acc >= FLOOR:
        return (
            "promote",
            f"local {local.mean_final_acc:.3f} / {second.mean_final_acc:.3f} "
            f">= floor {FLOOR} on two seeds",
        )
    return (
        "refuse",
        f"local {local.mean_final_acc:.3f} / {second.mean_final_acc:.3f} "
        f"below floor {FLOOR} at the ladder's best point",
    )


def run_plasticity_ladder(
    *, device: str = "cuda", progress: str | Path | None = None
) -> LadderReport:
    """Stage 1: the 3-point LR ladder plus one confirmation seed at the best."""
    cells = tuple(
        _run_cell(
            stage="plasticity",
            progress=progress,
            arm=arm,
            knob=lr,
            seed=LADDER_SEEDS[0],
            device=device,
            lr=lr,
            ewc_lambda=1000.0,
        )
        for lr in LR_LADDER
        for arm in PLASTICITY_ARMS
    )
    best = _summarise(cells)
    confirmation = tuple(
        _run_cell(
            stage="plasticity",
            progress=progress,
            arm=arm,
            knob=best[arm].knob,
            seed=CONFIRM_SEEDS[0],
            device=device,
            lr=best[arm].knob,
            ewc_lambda=1000.0,
        )
        for arm in PLASTICITY_ARMS
        if arm in best
    )
    verdict, reason = _verdict(best, confirmation)
    return LadderReport(
        stage="plasticity",
        box={
            "task": "SplitMNIST",
            "tasks": TASKS,
            "epochs_per_task": 1,
            "batch_size": 1,
            "hidden_dim": 256,
            "lr_ladder": LR_LADDER,
            "ewc_lambda_fixed": 1000.0,
            "seeds": LADDER_SEEDS + CONFIRM_SEEDS,
            "device": device,
        },
        cells=cells,
        best=best,
        confirmation=confirmation,
        verdict=verdict,
        reason=reason,
    )


def run_consolidation_ladder(
    *,
    lr: float,
    device: str = "cuda",
    progress: str | Path | None = None,
) -> LadderReport:
    """Stage 2: the 3-point EWC-strength ladder at the frozen learning rate."""
    cells = tuple(
        _run_cell(
            stage="consolidation",
            progress=progress,
            arm=arm,
            knob=ewc_lambda,
            seed=LADDER_SEEDS[0],
            device=device,
            lr=lr,
            ewc_lambda=ewc_lambda,
        )
        for ewc_lambda in EWC_LAMBDA_LADDER
        for arm in CONSOLIDATION_ARMS
    )
    best = _summarise(cells)
    confirmation = tuple(
        _run_cell(
            stage="consolidation",
            progress=progress,
            arm=arm,
            knob=best[arm].knob,
            seed=CONFIRM_SEEDS[0],
            device=device,
            lr=lr,
            ewc_lambda=best[arm].knob,
        )
        for arm in CONSOLIDATION_ARMS
        if arm in best
    )
    control = best.get("backprop_ewc")
    local = best.get("local_ewc")
    if control is None or control.mean_final_acc < FLOOR:
        verdict, reason = "invalid-control", "backprop x EWC control below floor"
    elif local is None:
        verdict, reason = "invalid-control", "no local x EWC cell measured"
    else:
        confirmed = [c for c in confirmation if c.arm == "local_ewc"]
        ok = local.mean_final_acc >= FLOOR and (
            not confirmed or confirmed[0].mean_final_acc >= FLOOR
        )
        verdict = "promote" if ok else "refuse"
        reason = (
            f"local x EWC {local.mean_final_acc:.3f} at lambda={local.knob:g}, "
            f"frozen lr={lr:g}"
        )
    return LadderReport(
        stage="consolidation",
        box={
            "task": "SplitMNIST",
            "tasks": TASKS,
            "epochs_per_task": 1,
            "batch_size": 1,
            "hidden_dim": 256,
            "frozen_lr": lr,
            "ewc_lambda_ladder": EWC_LAMBDA_LADDER,
            "seeds": LADDER_SEEDS + CONFIRM_SEEDS,
            "device": device,
        },
        cells=cells,
        best=best,
        confirmation=confirmation,
        verdict=verdict,
        reason=reason,
    )


def _markdown(report: LadderReport) -> str:
    """The table a third party can read, with its rulers and command."""
    box = report.box
    lines = [
        f"# C1 {report.stage} ladder — {box['task']} at batch 1",
        "",
        f"**Box.** {box}",
        "",
        "**Rulers.** held-out 2000 samples/task (1 sigma = "
        f"{RESOLUTION:.3f}); chance {CHANCE}; floor {FLOOR}.",
        "",
        "| arm | knob | seed | mean final acc | last task acc | BWT | forgetting "
        "| state MiB | s |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for cell in report.cells + report.confirmation:
        lines.append(
            f"| {cell.arm} | {cell.knob:g} | {cell.seed} | "
            f"{cell.mean_final_acc:.3f} | {cell.last_task_acc:.3f} | "
            f"{cell.backward_transfer:+.3f} | {cell.avg_forgetting:.3f} | "
            f"{cell.state_mb:.1f} | {cell.time_s:.1f} |"
        )
    lines.extend([
        "",
        f"**Verdict: {report.verdict}** — {report.reason}",
        "",
        f"Command: `uv run python -m computronium.validation.plasticity_ladder "
        f"--stage {report.stage} --device {box['device']}`",
        "",
    ])
    return "\n".join(lines)


def write_report(report: LadderReport, output_dir: str | Path) -> Path:
    """Write ``report.json`` and ``report.md``; return the JSON path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = asdict(report)
    payload["best"] = {k: asdict(v) for k, v in report.best.items()}
    path = output_dir / f"{report.stage}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    (output_dir / f"{report.stage}.md").write_text(_markdown(report))
    return path


def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", choices=("plasticity", "consolidation"), default="plasticity"
    )
    parser.add_argument(
        "--device", default="cuda" if torch.cuda.is_available() else "cpu"
    )
    parser.add_argument("--lr", type=float, default=None, help="frozen LR for stage 2")
    parser.add_argument("--out", default="results/t93_c1")
    args = parser.parse_args()
    if args.stage == "plasticity":
        progress = Path(args.out) / "plasticity.cells.jsonl"
        report = run_plasticity_ladder(device=args.device, progress=progress)
        path = write_report(report, args.out)
        lr = report.best["local"].knob if "local" in report.best else LR_LADDER[1]
        (Path(args.out) / "frozen_lr.txt").write_text(f"{lr:g}\n")
    else:
        frozen = Path(args.out) / "frozen_lr.txt"
        lr = args.lr or (
            float(frozen.read_text(encoding="utf-8"))
            if frozen.exists()
            else LR_LADDER[1]
        )
        progress = Path(args.out) / "consolidation.cells.jsonl"
        report = run_consolidation_ladder(lr=lr, device=args.device, progress=progress)
        path = write_report(report, args.out)
    print(f"wrote {path}")
    print(f"verdict: {report.verdict} — {report.reason}")


if __name__ == "__main__":
    _main()
