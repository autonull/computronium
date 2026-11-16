"""D1: the substrate ladder (TODO93 §6a, track D).

The screen asks one question: **on a constrained substrate model, does an
energy-minimisation learner reach digital parity at lower state per step?** The
substrate models and the settling kernel already exist; what is missing is one
matched row.

**Arms and controls.** Three substrate arms share one rule, one architecture,
and one budget: ``digital`` (the control), ``ternary`` (TWN quantisation with
STE), and ``memristive`` (differential int8 conductance pairs). A fourth arm,
the digital backprop baseline, is the **learning control**: it establishes
that the task is learnable at this box and records the strongest baseline's
accuracy at the same epochs. It is not the parity reference -- parity is
against the same rule on a digital substrate, which isolates the substrate's
effect from the rule's own weakness.

**The knob box.** The primary knob is the settle length (``max_steps`` =
5/10/20). A shared LR would confound the ladder: at this box ternary peaks at
3e-3 while digital and memristive peak at 1e-2 (pilot, CORRECTION 17 rows).
Each arm therefore gets its own 3-point LR viability ladder at the middle
settle length, at a seed disjoint from the ladder and confirmation, and the
best point is frozen before the settle ladder runs.

**The state ruler.** A step's state is reported in two parts, and only one is
a hardware claim:

- ``device_state_bytes`` -- what a device must hold to represent the weights
  at a step: 32 bits/weight for digital fp32, 2 bits/weight for a 3-level
  ternary device (plus one fp32 scale per layer), and 16 bits/weight for a
  differential int8 memristive pair. This is the ruler the "less state"
  claim rests on.
- ``train_state_bytes`` -- what the simulator keeps across steps: the fp32
  latent weights and the optimizer buffer. It is equal for every arm, and it
  is recorded as a **declared** cost, never claimed as a saving: an in-situ
  device would hold the weights, not a second fp32 copy.

**Gate (pre-registered).** Controls first: the backprop arm must clear
:data:`FLOOR` (else the run is invalid, not the substrate) and the digital
control is the parity reference. A constrained arm **promotes to D2** only
when, at its best ``max_steps`` point, both the ladder and the confirmation
seed are within :data:`PARITY_DELTA` of the digital control at the **same**
``max_steps``, and its ``device_state_bytes`` is strictly smaller. A
constrained arm that cannot train at any point **parks** with a trigger; a box
where no arm reaches parity **refuses** the track at this box, with the knob
box, the reversal trigger, and the re-open command.

Run it with::

    uv run python -m computronium.validation.substrate_ladder --device cpu
    uv run python -m computronium.validation.substrate_ladder --replay
"""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import torch

from computronium.domains.base import TaskSplit

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from computronium.core.system_trainer._resources import EpochResource
    from computronium.ontology.system import System

logger = logging.getLogger(__name__)

__all__ = [
    "BATCHES_PER_EPOCH",
    "CHANCE",
    "CONFIRM_SEED",
    "DEVICE_BITS",
    "FLOOR",
    "LADDER_SEED",
    "LEARNING_CONTROL",
    "LR_LADDER",
    "MAX_STEPS_LADDER",
    "PARITY_DELTA",
    "SUBSTRATE_ARMS",
    "SubstrateCell",
    "SubstrateReport",
    "device_state",
    "read_cells",
    "replay_substrate_ladder",
    "run_substrate_ladder",
]

#: The constrained substrates and their digital control (one shared rule).
SUBSTRATE_ARMS = ("digital", "ternary", "memristive")
#: The strongest baseline at the same budget; a learning control, not a reference.
LEARNING_CONTROL = "backprop"
#: The primary knob: the settle length, three points + confirmation.
MAX_STEPS_LADDER = (5, 10, 20)
#: Per-arm LR viability ladder (the pilot found 1e-3..1e-2 live, 3e-2 diverged).
LR_LADDER = (1e-3, 3e-3, 1e-2)
LADDER_SEED = 59
CONFIRM_SEED = 60
#: MNIST is 10-way; a collapsed predictor scores exactly this.
CHANCE = 0.1
#: Pre-registered viability floor for the learning control (C1's floor).
FLOOR = 0.55
#: Parity is a 1 pp margin against the same rule on the digital substrate.
PARITY_DELTA = 0.01
#: The declared box: one cheap task, identical architecture and budget.
INPUT_DIM = 784
NUM_CLASSES = 10
HIDDEN_DIMS = (32,)
BATCH_SIZE = 32
BATCHES_PER_EPOCH = 600
EPOCHS = 1
BETA = 0.5
#: Bits per weight a device needs for each substrate (scales priced separately).
DEVICE_BITS = {"digital": 32, "ternary": 2, "memristive": 16}
#: A ternary device keeps one fp32 scale per layer beside its weights.
TERNARY_SCALE_BYTES = 4


@dataclass(frozen=True, slots=True)
class SubstrateCell:
    """One measured cell: a substrate arm at one knob point, one seed."""

    arm: str
    stage: str
    seed: int
    lr: float
    max_steps: int
    device: str
    val_acc: float | None
    train_acc: float | None
    device_state_bytes: int
    device_state_per_weight: float
    train_state_bytes: int | None
    params_mb: float | None
    optimizer_mb: float | None
    activations_mb: float | None
    steps: int
    time_s: float
    forward_equivalents: float | None
    note: str = ""
    refused: bool = False


@dataclass(frozen=True, slots=True)
class SubstrateReport:
    """The ladder's measured table and its pre-registered verdict."""

    stage: str
    box: dict[str, object]
    cells: tuple[SubstrateCell, ...]
    control: SubstrateCell
    verdict: str
    reason: str


class _CappedLoader:
    """A loader view with a batch cap and a length the trainer can price."""

    __slots__ = ("_cap", "_loader")

    def __init__(self, loader: Iterable, cap: int) -> None:
        self._loader = loader
        self._cap = cap

    def __iter__(self):
        return itertools.islice(self._loader, self._cap)  # type: ignore[arg-type]

    def __len__(self) -> int:
        return min(len(self._loader), self._cap)  # type: ignore[arg-type]


def _substrate(arm: str, device: str):
    """The substrate instance for an arm (the ontology models, not adapters)."""
    from computronium import DigitalSubstrate, MemristiveSubstrate, SubstrateConfig
    from computronium.ontology import TernarySubstrate

    match arm:
        case "digital":
            return DigitalSubstrate(SubstrateConfig.digital(device=device))
        case "ternary":
            return TernarySubstrate(SubstrateConfig.ternary(device=device))
        case "memristive":
            return MemristiveSubstrate(SubstrateConfig.memristive(device=device))
        case _:
            raise ValueError(f"unknown substrate arm: {arm!r}")


def _build_system(
    arm: str, seed: int, lr: float, max_steps: int, device: str = "cpu"
) -> System:
    """Compose the declared box; every arm shares architecture and budget."""
    from computronium import (
        BackpropCredit,
        CreditAssignmentConfig,
        EnergyMinimizationDynamics,
        EuclideanUpdate,
        FeedforwardGeometry,
        GeometryConfig,
        InstantaneousDynamics,
        NullPlasticity,
        ParameterUpdateConfig,
        StateDynamicsConfig,
        ThermodynamicContrast,
        compose_joint_system,
    )

    torch.manual_seed(seed)
    if arm == LEARNING_CONTROL:
        dynamics = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
        credit = BackpropCredit(CreditAssignmentConfig.gradient())
    else:
        dynamics = EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(
                max_steps=max_steps, beta=BETA, compiled=False
            )
        )
        credit = ThermodynamicContrast(
            CreditAssignmentConfig.thermodynamic_contrast(beta=BETA)
        )
    return compose_joint_system(
        substrate=_substrate("digital" if arm == LEARNING_CONTROL else arm, device),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=INPUT_DIM,
                output_dim=NUM_CLASSES,
                hidden_dims=HIDDEN_DIMS,
            )
        ),
        dynamics=dynamics,
        plasticity=NullPlasticity(),
        credit=credit,
        update=EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=lr, grad_clip=1e9)
        ),
    )


def device_state(system: System, arm: str) -> tuple[int, float]:
    """Device state per step (bytes, bytes/weight) from the substrate's width.

    Only weight matrices are counted; biases and the ternary per-layer scale
    are declared beside the ruler. ``digital`` is the reference width.
    """
    weights = [p for p in system.geometry.params.values() if p.ndim >= 2]
    weights_numel = sum(int(p.numel()) for p in weights)
    bits = DEVICE_BITS["digital" if arm == LEARNING_CONTROL else arm]
    scale_bytes = TERNARY_SCALE_BYTES * len(weights) if arm == "ternary" else 0
    total = math.ceil(weights_numel * bits / 8) + scale_bytes
    return total, total / weights_numel


def _accuracy(system: System, loader: Iterable, device: str = "cpu") -> float:
    """Held-out accuracy over the full test split (10k samples, sigma 0.3 pp)."""
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in loader:
            logits = system.geometry(x.view(x.size(0), -1).to(device))
            correct += int((logits.argmax(dim=-1) == y).sum())
            total += int(y.numel())
    return correct / total


def _train(
    arm: str,
    *,
    seed: int,
    lr: float,
    max_steps: int,
    device: str,
    train_loader: Iterable,
    test_loader: Iterable,
) -> tuple[float, float, EpochResource, int, float, float, float | None]:
    """One epoch at the declared budget: (val, train, cost, bytes, B/w, s, fwd-eq)."""
    from computronium import SystemTrainer, SystemTrainerConfig

    system = _build_system(arm, seed, lr, max_steps, device)
    device_bytes, per_weight = device_state(system, arm)
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=EPOCHS,
            device=device,
            seed=seed,
            track_flops=True,
            track_memory=True,
        ),
        train_data=_CappedLoader(train_loader, BATCHES_PER_EPOCH),
    )
    started = time.perf_counter()
    history = trainer.fit()
    elapsed = time.perf_counter() - started
    resource = trainer.epoch_resources[-1]
    one_forward = _one_forward_flops(system)
    forward_equivalents = (
        resource.forward_flops / resource.steps / one_forward
        if resource.forward_flops and resource.steps and one_forward
        else None
    )
    return (
        _accuracy(system, test_loader, device),
        float(history[-1]["train_acc"]),
        resource,
        device_bytes,
        per_weight,
        elapsed,
        forward_equivalents,
    )


def _one_forward_flops(system: System) -> int | None:
    """One forward pass's matmul FLOPs, or ``None`` when the stack is absent."""
    from computronium.ontology._settle_kernel import extract_layered_params

    layered = extract_layered_params(system.geometry)
    if layered is None:
        return None
    return sum(
        2 * BATCH_SIZE * int(w.shape[0]) * int(w.shape[1]) for w in layered.weights
    )


def _train_state_bytes(resource: EpochResource) -> int | None:
    """fp32 latent weights + optimizer buffer, in bytes (the declared cost)."""
    if resource.params_mb is None or resource.optimizer_mb is None:
        return None
    return int((resource.params_mb + resource.optimizer_mb) * 1024**2)


def _refusal_cell(  # ruff: ignore[too-many-arguments]
    *,
    arm: str,
    stage: str,
    seed: int,
    lr: float,
    max_steps: int,
    device: str,
    started: float,
    note: str,
) -> SubstrateCell:
    """A crash is a refusal with a trigger, recorded as a row -- never skipped."""
    system = _build_system(arm, seed, lr, max_steps, device)
    device_bytes, per_weight = device_state(system, arm)
    return SubstrateCell(
        arm=arm,
        stage=stage,
        seed=seed,
        lr=lr,
        max_steps=max_steps,
        device=device,
        val_acc=None,
        train_acc=None,
        device_state_bytes=device_bytes,
        device_state_per_weight=per_weight,
        train_state_bytes=None,
        params_mb=None,
        optimizer_mb=None,
        activations_mb=None,
        steps=0,
        time_s=time.perf_counter() - started,
        forward_equivalents=None,
        note=note,
        refused=True,
    )


def _run_cell(
    arm: str,
    *,
    stage: str,
    seed: int,
    lr: float,
    max_steps: int,
    device: str,
    train_loader: Iterable,
    test_loader: Iterable,
    progress: str | Path | None,
) -> SubstrateCell:
    """Measure one cell, then log it before the next cell runs."""
    started = time.perf_counter()
    try:
        (
            val_acc,
            train_acc,
            resource,
            device_bytes,
            per_weight,
            elapsed,
            forward_equivalents,
        ) = _train(
            arm,
            seed=seed,
            lr=lr,
            max_steps=max_steps,
            device=device,
            train_loader=train_loader,
            test_loader=test_loader,
        )
    except (RuntimeError, ValueError) as exc:
        cell = _refusal_cell(
            arm=arm,
            stage=stage,
            seed=seed,
            lr=lr,
            max_steps=max_steps,
            device=device,
            started=started,
            note=f"refusal at the cell: {exc}",
        )
        _write_cell(cell, progress)
        return cell

    cell = SubstrateCell(
        arm=arm,
        stage=stage,
        seed=seed,
        lr=lr,
        max_steps=max_steps,
        device=device,
        val_acc=val_acc,
        train_acc=train_acc,
        device_state_bytes=device_bytes,
        device_state_per_weight=per_weight,
        train_state_bytes=_train_state_bytes(resource),
        params_mb=resource.params_mb,
        optimizer_mb=resource.optimizer_mb,
        activations_mb=resource.activations_mb,
        steps=resource.steps,
        time_s=elapsed,
        forward_equivalents=forward_equivalents,
        note=_note(arm, val_acc),
    )
    _write_cell(cell, progress)
    return cell


def _note(arm: str, val_acc: float) -> str:
    """Why a below-floor cell is not a verdict (the plan's triage, per row)."""
    if val_acc >= FLOOR:
        return ""
    if arm == LEARNING_CONTROL:
        return "invalid-learning control: the digital backprop arm is below the floor"
    return (
        "below the floor at this point; a quantisation-width or LR extension "
        "is the trigger, not a refusal"
    )


def _write_cell(cell: SubstrateCell, progress: str | Path | None) -> None:
    """Append one cell to the kill-safe log before the next cell runs."""
    if progress is None:
        return
    path = Path(progress)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(asdict(cell)) + "\n")


def read_cells(progress: str | Path) -> tuple[SubstrateCell, ...]:
    """Read the kill-safe cell log (one JSON object per line)."""
    path = Path(progress)
    if not path.exists():
        return ()
    return tuple(
        SubstrateCell(**json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def _resume_cells(
    progress: str | Path | None,
) -> dict[tuple[str, str, int, float, int], SubstrateCell]:
    """Cells a kill left in the log, keyed by arm, stage, seed, LR, settle."""
    if progress is None or not Path(progress).exists():
        return {}
    return {
        (c.arm, c.stage, c.seed, c.lr, c.max_steps): c for c in read_cells(progress)
    }


def _cell_or_measure(  # ruff: ignore[too-many-arguments]
    done: dict[tuple[str, str, int, float, int], SubstrateCell],
    *,
    arm: str,
    stage: str,
    seed: int,
    lr: float,
    max_steps: int,
    device: str,
    train_loader: Iterable,
    test_loader: Iterable,
    progress: str | Path | None,
) -> SubstrateCell:
    """Reuse a measured cell; otherwise run it and log it."""
    planned = done.get((arm, stage, seed, lr, max_steps))
    if planned is not None:
        return planned
    return _run_cell(
        arm,
        stage=stage,
        seed=seed,
        lr=lr,
        max_steps=max_steps,
        device=device,
        train_loader=train_loader,
        test_loader=test_loader,
        progress=progress,
    )


def _best(cells: tuple[SubstrateCell, ...]) -> SubstrateCell | None:
    """The best trained cell (a refused cell never wins a ladder point)."""
    trained = [c for c in cells if c.val_acc is not None and not c.refused]
    return max(trained, key=lambda c: c.val_acc or 0.0) if trained else None


def _edge_note(cells: tuple[SubstrateCell, ...], best: SubstrateCell | None) -> str:
    """Name a best point that sits on the ladder's edge (an extension trigger)."""
    if best is None or len(cells) < 3:
        return ""
    if best is cells[0] or best is cells[-1]:
        return "best point at the ladder edge; an extension is the next rung"
    return ""


def _arm_parity(
    arm: str,
    *,
    ladder: tuple[SubstrateCell, ...],
    confirmation: tuple[SubstrateCell, ...],
    digital_by_steps: dict[int, SubstrateCell],
    parity_delta: float = PARITY_DELTA,
) -> bool:
    """Both seeds within the margin at the arm's best settle, with less state."""
    arm_ladder = [c for c in ladder if c.arm == arm and not c.refused]
    best = _best(tuple(arm_ladder))
    if best is None:
        return False
    reference = digital_by_steps.get(best.max_steps)
    if reference is None or reference.val_acc is None or best.val_acc is None:
        return False
    arm_confirm = [
        c
        for c in confirmation
        if c.arm == arm and c.max_steps == best.max_steps and not c.refused
    ]
    ref_confirm = [
        c
        for c in confirmation
        if c.arm == "digital" and c.max_steps == best.max_steps and not c.refused
    ]
    if (
        not arm_confirm
        or not ref_confirm
        or arm_confirm[0].val_acc is None
        or ref_confirm[0].val_acc is None
    ):
        return False
    seed_parity = best.val_acc >= reference.val_acc - parity_delta
    confirm_parity = arm_confirm[0].val_acc >= ref_confirm[0].val_acc - parity_delta
    state_saving = best.device_state_bytes < reference.device_state_bytes
    return seed_parity and confirm_parity and state_saving


def _verdict(
    *,
    control: SubstrateCell,
    ladder: tuple[SubstrateCell, ...],
    confirmation: tuple[SubstrateCell, ...],
    parity_delta: float = PARITY_DELTA,
    floor: float = FLOOR,
) -> tuple[str, str]:
    """Controls first, then parity at a matched settle length, then state."""
    if control.val_acc is None or control.val_acc < floor:
        return (
            "invalid-learning-control",
            f"the digital backprop control reads {control.val_acc}; a control "
            "below the floor invalidates the run, not the substrate",
        )
    digital_by_steps = {
        c.max_steps: c for c in ladder if c.arm == "digital" and not c.refused
    }
    if not digital_by_steps:
        return (
            "invalid-learning-control",
            "the digital control produced no trained ladder cell",
        )
    if not any(c.arm in {"ternary", "memristive"} for c in (*ladder, *confirmation)):
        return "park", "no constrained substrate produced a cell to compare"
    promoted = [
        arm
        for arm in ("ternary", "memristive")
        if _arm_parity(
            arm,
            ladder=ladder,
            confirmation=confirmation,
            digital_by_steps=digital_by_steps,
            parity_delta=parity_delta,
        )
    ]
    if promoted:
        return (
            "promote",
            f"{', '.join(promoted)} reaches parity within {parity_delta:.2f} of "
            "the digital control at the same settle length on two seeds, with "
            "device state below the digital width; D2 is the matched comparison",
        )
    if not any(c.arm in {"ternary", "memristive"} and not c.refused for c in ladder):
        return (
            "park",
            "no constrained substrate trained at any ladder point; a wider "
            "quantisation box or a quantisation-aware init is the trigger",
        )
    return (
        "refuse",
        "no constrained substrate reaches parity within "
        f"{parity_delta:.2f} of the digital control on two seeds at this box; "
        "the ladder box and its re-open command are recorded",
    )


def _box(device: str, *, stage: str) -> dict[str, object]:
    """The declared box every cell runs inside."""
    return {
        "task": "MNIST quick mode; full 10k test split (1 sigma = 0.3 pp)",
        "architecture": f"feedforward {INPUT_DIM}-{HIDDEN_DIMS[0]}-{NUM_CLASSES}",
        "batch": BATCH_SIZE,
        "batches_per_epoch": BATCHES_PER_EPOCH,
        "epochs": EPOCHS,
        "chance": CHANCE,
        "floor": FLOOR,
        "parity_delta": PARITY_DELTA,
        "max_steps_ladder": MAX_STEPS_LADDER,
        "lr_ladder": LR_LADDER,
        "ladder_seed": LADDER_SEED,
        "confirm_seed": CONFIRM_SEED,
        "beta": BETA,
        "device_bits": DEVICE_BITS,
        "rule": "energy_minimization + thermodynamic_contrast for the three "
        "substrate arms; instantaneous + gradient for the learning control",
        "stage": stage,
        "device": device,
        "cost": "CPU; walltime is the compute ruler, forward-equivalents recorded",
    }


def _run_ladders(
    measure: Callable[..., SubstrateCell],
) -> tuple[
    tuple[SubstrateCell, ...],
    tuple[SubstrateCell, ...],
    tuple[SubstrateCell, ...],
    SubstrateCell,
]:
    """Per-arm LR ladder, then the settle ladder at each arm's best LR."""
    control = measure(
        LEARNING_CONTROL, "control", seed=LADDER_SEED, lr=LR_LADDER[-1], steps=10
    )
    lr_cells: list[SubstrateCell] = []
    step_cells: list[SubstrateCell] = []
    confirmation: list[SubstrateCell] = []
    best_lr: dict[str, float] = {}
    middle = MAX_STEPS_LADDER[len(MAX_STEPS_LADDER) // 2]
    for arm in SUBSTRATE_ARMS:
        arm_lr = tuple(
            measure(arm, "lr", seed=LADDER_SEED, lr=lr, steps=middle)
            for lr in LR_LADDER
        )
        lr_cells.extend(arm_lr)
        best = _best(arm_lr)
        best_lr[arm] = best.lr if best is not None else LR_LADDER[0]
        for note in (_edge_note(arm_lr, best),):
            if note:
                logger.info("%s: %s", arm, note)
        arm_steps = tuple(
            measure(
                arm,
                "steps",
                seed=LADDER_SEED,
                lr=best_lr[arm],
                steps=steps,
            )
            for steps in MAX_STEPS_LADDER
        )
        step_cells.extend(arm_steps)
        step_best = _best(arm_steps)
        for note in (_edge_note(arm_steps, step_best),):
            if note:
                logger.info("%s: %s", arm, note)
        if best is not None and step_best is not None:
            confirmation.append(
                measure(
                    arm,
                    "confirm",
                    seed=CONFIRM_SEED,
                    lr=best.lr,
                    steps=step_best.max_steps,
                )
            )
    # The parity reference needs a digital confirmation at every settle length
    # a constrained arm can choose, or a matched confirmation is missing.
    confirmation.extend(
        measure(
            "digital", "confirm", seed=CONFIRM_SEED, lr=best_lr["digital"], steps=steps
        )
        for steps in MAX_STEPS_LADDER
    )
    return (
        tuple(lr_cells),
        tuple(step_cells),
        tuple(confirmation),
        control,
    )


def run_substrate_ladder(
    *,
    device: str = "cpu",
    progress: str | Path | None = None,
) -> SubstrateReport:
    """The per-arm LR ladder, then the settle ladder at each arm's best LR."""
    from computronium import create_task

    done = _resume_cells(progress)
    if done:
        logger.info("reusing %d measured cells from %s", len(done), progress)
    task = create_task("mnist", device="cpu", quick_mode=True)
    task.setup()
    train_loader = task.get_dataloader(TaskSplit.TRAIN)
    test_loader = task.get_dataloader(TaskSplit.TEST)

    def measure(
        arm: str, stage: str, *, seed: int, lr: float, steps: int
    ) -> SubstrateCell:
        key = (arm, stage, seed, lr, steps)
        if key in done:
            return done[key]
        done[key] = _cell_or_measure(
            done,
            arm=arm,
            stage=stage,
            seed=seed,
            lr=lr,
            max_steps=steps,
            device=device,
            train_loader=train_loader,
            test_loader=test_loader,
            progress=progress,
        )
        return done[key]

    lr_cells, step_cells, confirmation, control = _run_ladders(measure)
    verdict, reason = _verdict(
        control=control, ladder=step_cells, confirmation=confirmation
    )
    return SubstrateReport(
        stage="substrate",
        box=_box(device, stage="substrate"),
        cells=(*lr_cells, *step_cells, *confirmation),
        control=control,
        verdict=verdict,
        reason=reason,
    )


def replay_substrate_ladder(
    *, progress: str | Path, device: str = "cpu"
) -> SubstrateReport:
    """Recompute the gate from the cell log, without training."""
    cells = read_cells(progress)
    if not cells:
        raise RuntimeError(f"no cells in {progress}; run the ladder first")
    control = next((c for c in cells if c.arm == LEARNING_CONTROL), None)
    if control is None:
        raise RuntimeError("the cell log holds no learning control")
    ladder = tuple(c for c in cells if c.stage == "steps")
    confirmation = tuple(c for c in cells if c.stage == "confirm")
    verdict, reason = _verdict(
        control=control, ladder=ladder, confirmation=confirmation
    )
    return SubstrateReport(
        stage="substrate",
        box=_box(cells[0].device if cells else device, stage="substrate"),
        cells=cells,
        control=control,
        verdict=verdict,
        reason=reason,
    )


def _markdown(report: SubstrateReport) -> str:
    """The table a third party can read, with its rulers and command."""
    box = report.box
    lines = [
        "# D1 substrate ladder — ternary/memristive + energy_min",
        "",
        f"**Box.** {box}",
        "",
        "**State ruler.** device state per step = weight bits / 8 (+ one fp32 "
        "scale per layer for ternary); train state = fp32 latent weights + "
        "optimizer buffer (declared, equal for every arm).",
        "",
        "| stage | arm | seed | lr | settle | val acc | dev B/weight | "
        "train MB | steps | s | note |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cell in report.cells:
        acc = f"{cell.val_acc:.3f}" if cell.val_acc is not None else "refused"
        train_mb = (
            f"{cell.train_state_bytes / 1024**2:.1f}"
            if cell.train_state_bytes is not None
            else "—"
        )
        lines.append(
            f"| {cell.stage} | {cell.arm} | {cell.seed} | {cell.lr:g} | "
            f"{cell.max_steps} | {acc} | {cell.device_state_per_weight:.2f} | "
            f"{train_mb} | {cell.steps} | {cell.time_s:.1f} | {cell.note} |"
        )
    lines.extend([
        "",
        f"**Verdict: {report.verdict}** — {report.reason}",
        "",
        "**Learning control:** digital backprop reads "
        f"{report.control.val_acc if report.control.val_acc is not None else 'refused'}"
        f" (floor {FLOOR}).",
        "",
        "**Ladder edges:** "
        + ("; ".join(_edges(report.cells)) or "none (every best point is interior)"),
        "",
        "Command: `uv run python -m computronium.validation.substrate_ladder "
        f"--device {box['device']}`; replay from the cell log: `... --replay`.",
        "",
    ])
    return "\n".join(lines)


def _edges(cells: tuple[SubstrateCell, ...]) -> tuple[str, ...]:
    """Name every ladder point that sits on an edge (an extension trigger)."""
    edges: list[str] = []
    for arm in SUBSTRATE_ARMS:
        for stage, ladder in (("lr", LR_LADDER), ("steps", MAX_STEPS_LADDER)):
            points = [
                c for c in cells if c.arm == arm and c.stage == stage and not c.refused
            ]
            best = _best(tuple(points))
            if best is None:
                continue
            value = best.lr if stage == "lr" else best.max_steps
            if value in {ladder[0], ladder[-1]}:
                edges.append(f"{arm}/{stage} best at the ladder edge ({value:g})")
    return tuple(edges)


def write_report(report: SubstrateReport, output_dir: str | Path) -> Path:
    """Write ``substrate.json`` and ``substrate.md``; return the JSON path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = asdict(report)
    payload["control"] = asdict(report.control)
    payload["ladder_edges"] = _edges(report.cells)
    path = output_dir / "substrate.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    (output_dir / "substrate.md").write_text(_markdown(report))
    return path


def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--device", default="cuda" if torch.cuda.is_available() else "cpu"
    )
    parser.add_argument(
        "--replay", action="store_true", help="recompute the gate from the cell log"
    )
    parser.add_argument("--out", default="results/t93_d1")
    args = parser.parse_args()
    progress = Path(args.out) / "substrate.cells.jsonl"
    report = (
        replay_substrate_ladder(progress=progress, device=args.device)
        if args.replay
        else run_substrate_ladder(device=args.device, progress=progress)
    )
    path = write_report(report, args.out)
    print(f"wrote {path}")
    print(f"verdict: {report.verdict} — {report.reason}")


if __name__ == "__main__":
    _main()
