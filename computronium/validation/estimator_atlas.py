"""E1: the estimator atlas (TODO93 §6a, track E).

The screen asks one question: **at matched compute on one task, what are the
bias/variance/compute coordinates of each estimator kind?** It is not a
competition. The table is the artifact: it is publishable whether or not any arm
wins, and it makes every later estimator comparison commensurable.

**The coordinate, and the declared reference.** A credit's pseudo-gradient is
compared with the exact task gradient at the same pre-update parameters and the
same probe batch. The exact arm (``BackpropCredit``) is that reference; its
finite-difference sibling on a small net is the instrument control. An arm whose
card declares ``bias_reference="none"`` (the objective-local family) has no
global gradient to be biased against: its coordinate is **update-direction
alignment** with the exact reference and its update scale, never "bias".

**The ladder.** E-lite is 4 arms x 1 claim seed: exact, gradient
approximation, objective-local, and hybrid. Each arm first gets its own 3-point
viability ladder on the primary knob (LR) at a disjoint seed, plus a
confirmation at its best point; the claim seed runs at that point. A single
shared LR is not a fair box: it collapses FA at 1e-3 and diverges the hybrid at
1e-1 (CORRECTION 16). The screen passes when its controls pass and every arm
produces a non-zero update; it does not adjudicate an estimator. The full rung
is all 6 arms x 3 disjoint claim seeds, and its per-arm variance is the seed
ruler. The exact arm must clear the learning floor, else the run is invalid
rather than the treatment being promoted (the control at chance invalidates the
run).

**Rulers.** Held-out accuracy is the full MNIST test split (1 sigma = 0.3 pp) and
chance is 0.1. The probe batch is 8 fixed batches (256 samples). The estimate
of forward-equivalents is the structural train-step FLOPs divided by one forward
FLOP; walltime is recorded beside it because a second forward pass (PEPITA) is
real compute that the structural estimate cannot see. A single seed has no
variance, and that field is ``None`` -- an honest gap, never zero.

Run it with::

    uv run python -m computronium.validation.estimator_atlas --device cuda
    uv run python -m computronium.validation.estimator_atlas --full --replay
"""

from __future__ import annotations

import argparse
import itertools
import json
import logging
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

from computronium.core.system_trainer.spec import estimator_coordinate
from computronium.ontology.credit import (
    BackpropCredit,
    CreditAssignment,
    HybridCredit,
    LocalGoodnessCredit,
    PCALMCredit,
    PepitaCredit,
    RandomProjectionsCredit,
)
from computronium.ontology.geometry import FeedforwardGeometry
from computronium.validation.gradient_check import (
    GradientEquivalenceMLP,
    finite_diff_gradient,
    loss_ce,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from computronium.core.system_trainer._resources import EpochResource
    from computronium.ontology.system import System

logger = logging.getLogger(__name__)

__all__ = [
    "ARMS",
    "BATCHES_PER_EPOCH",
    "CHANCE",
    "FLOOR",
    "FULL_SEEDS",
    "LITE_ARMS",
    "LITE_SEEDS",
    "PROBE_BATCHES",
    "REFERENCE_CONTROL_TOL",
    "EstimatorArm",
    "EstimatorCell",
    "EstimatorReport",
    "read_cells",
    "replay_estimator_atlas",
    "run_estimator_atlas",
]

#: The full atlas: every estimator kind a credit row declares (TODO93 §2).
ARMS = (
    "gradient",
    "random_projections",
    "pc_alm",
    "pepita",
    "local_goodness",
    "hybrid",
)
#: E-lite: one arm per estimator kind, the cheapest screen that can cancel
#: a broken apparatus before the six-arm table runs.
LITE_ARMS = ("gradient", "random_projections", "pepita", "hybrid")
LITE_SEEDS = (61,)
FULL_SEEDS = (61, 62, 63)
#: Each arm gets its own 3-point viability ladder on the primary knob (LR),
#: at a seed disjoint from the claim; the best point gets a confirmation seed.
LR_LADDER = (1e-3, 1e-2, 1e-1)
LADDER_SEED = 59
CONFIRM_SEED = 60
#: MNIST is 10-way; a collapsed predictor scores exactly this.
CHANCE = 0.1
#: Pre-registered viability floor (2.5x chance); the exact arm is the control.
FLOOR = 0.25
#: The fixed probe batch: 8 train batches (256 samples) for the gradient
#: coordinates, disjoint from the held-out split.
PROBE_BATCHES = 8
#: The loader cap used by the composed pilot (D2/T6), so compute is matched.
BATCHES_PER_EPOCH = 600
#: The finite-difference reference must agree with autograd on the small net.
REFERENCE_CONTROL_TOL = 0.99
#: The declared box: one cheap task, identical architecture and budget.
HIDDEN_DIMS = (32,)
INPUT_DIM = 784
NUM_CLASSES = 10
BATCH_SIZE = 32
EPOCHS = 1
MAX_STEPS = 3
BETA = 0.5
#: PC-ALM's primary knob is the settle step, not the optimiser LR; 0.02 is
#: the stable point at this shallow box. Its card validates depth 100, so a
#: chance cell here is a regime-mismatch, never a refusal.
PCALM_DYNAMICS_STEP = 0.02


@dataclass(frozen=True, slots=True)
class EstimatorArm:
    """One arm: the credit implementation, its kind, and its dynamics family."""

    name: str
    estimator_kind: str
    bias_reference: str
    credit: object
    pc_alm: bool = False


@dataclass(frozen=True, slots=True)
class EstimatorCell:
    """One measured cell: the gradient coordinates and the learning ruler."""

    arm: str
    estimator_kind: str
    bias_reference: str
    stage: str
    seed: int
    lr: float
    angle: float | None
    magnitude: float | None
    update_norm: float
    reference_norm: float
    nonzero_update: bool
    val_acc: float | None
    train_acc: float | None
    steps: int
    forward_equivalents: float | None
    time_s: float
    note: str = ""
    refused: bool = False


@dataclass(frozen=True, slots=True)
class EstimatorReport:
    """The atlas: one row per (arm, seed), plus its controls and verdict."""

    stage: str
    box: dict[str, object]
    cells: tuple[EstimatorCell, ...]
    ladder: tuple[EstimatorCell, ...]
    reference_fd_cosine: float
    reference_control: bool
    learning_control: bool
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


def _build_arm(name: str) -> EstimatorArm:
    """The credit and its declared coordinate, read from its identity card."""
    match name:
        case "gradient":
            credit = BackpropCredit()
        case "random_projections":
            credit = RandomProjectionsCredit()
        case "pc_alm":
            credit = PCALMCredit()
        case "pepita":
            credit = PepitaCredit()
        case "local_goodness":
            credit = LocalGoodnessCredit()
        case "hybrid":
            credit = HybridCredit()
        case _:
            raise ValueError(f"unknown estimator arm: {name!r}")
    kind, reference = estimator_coordinate(name)
    if kind == "unspecified" or reference == "unspecified":
        raise ValueError(f"{name}: credit identity card declares no coordinate")
    return EstimatorArm(
        name=name,
        estimator_kind=kind,
        bias_reference=reference,
        credit=credit,
        pc_alm=name == "pc_alm",
    )


def _build_system(arm: EstimatorArm, seed: int, lr: float) -> System:
    """Compose the declared box; every arm shares architecture and budget."""
    from computronium import (
        DigitalSubstrate,
        EnergyMinimizationDynamics,
        EuclideanUpdate,
        GeometryConfig,
        NullPlasticity,
        ParameterUpdateConfig,
        PCALMDynamics,
        StateDynamicsConfig,
        SubstrateConfig,
        compose_joint_system,
    )

    torch.manual_seed(seed)
    dynamics = (
        PCALMDynamics(
            StateDynamicsConfig.pc_alm(
                max_steps=MAX_STEPS,
                beta=BETA,
                step_size=PCALM_DYNAMICS_STEP,
            )
        )
        if arm.pc_alm
        else EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(max_steps=MAX_STEPS, beta=BETA)
        )
    )
    return compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=INPUT_DIM,
                output_dim=NUM_CLASSES,
                hidden_dims=HIDDEN_DIMS,
            )
        ),
        dynamics=dynamics,
        plasticity=NullPlasticity(),
        credit=cast("CreditAssignment", arm.credit),
        update=EuclideanUpdate(
            ParameterUpdateConfig.euclidean(
                step_size=lr,
                # Linear map from pseudo-gradient to delta in the probe; the
                # global clip is a step safety net, not the estimator.
                grad_clip=1e9,
            )
        ),
    )


def _parameters(system: System) -> dict[str, Tensor]:
    return {name: p.detach().clone() for name, p in system.geometry.params.items()}


def _delta(before: dict[str, Tensor], system: System) -> Tensor:
    """The parameter displacement of one step, flattened in a fixed order."""
    return torch.cat([
        (system.geometry.params[name].detach() - value).reshape(-1)
        for name, value in before.items()
    ])


def _probe_batch(loader: Iterable, seed: int) -> tuple[Tensor, Tensor]:
    """A fixed 256-sample probe batch; only the samples move, not the task."""
    sampler = loader.sampler  # type: ignore[attr-defined]
    sampler.generator = torch.Generator().manual_seed(seed)
    chunks = list(itertools.islice(loader, PROBE_BATCHES))
    return (
        torch.cat([x.view(x.size(0), -1) for x, _ in chunks]),
        torch.cat([y for _, y in chunks]),
    )


def _one_forward_flops(system: System, batch_size: int) -> int | None:
    """One forward pass's matmul FLOPs, or ``None`` when the structure is absent."""
    from computronium.ontology._settle_kernel import extract_layered_params

    layered = extract_layered_params(system.geometry)
    if layered is None:
        return None
    return sum(
        2 * batch_size * int(w.shape[0]) * int(w.shape[1]) for w in layered.weights
    )


def _accuracy(system: System, loader: Iterable) -> float:
    """Held-out accuracy over the full test split (10k samples, sigma 0.3 pp)."""
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in loader:
            logits = system.geometry(x.view(x.size(0), -1))
            correct += int((logits.argmax(dim=-1) == y).sum())
            total += int(y.numel())
    return correct / total


def _reference_control(seed: int) -> float:
    """The instrument control: autograd matches its own finite difference."""
    torch.manual_seed(seed)
    generator = torch.Generator().manual_seed(seed)
    x = torch.randn(16, 8, generator=generator)
    y = torch.randint(0, 5, (16,), generator=generator)
    model = GradientEquivalenceMLP()
    exact = torch.cat(
        torch.autograd.grad(loss_ce(model(x), y), list(model.parameters()))
    ).reshape(-1)
    finite_difference = finite_diff_gradient(model, x, y, loss_ce)
    return F.cosine_similarity(
        exact.reshape(1, -1), finite_difference.reshape(1, -1)
    ).item()


def _train(
    arm: EstimatorArm,
    seed: int,
    lr: float,
    train_loader: Iterable,
    test_loader: Iterable,
) -> tuple[float, float, EpochResource, float | None]:
    """One epoch at the declared budget; returns (val, train, cost, fwd-eq)."""
    from computronium import SystemTrainer, SystemTrainerConfig

    torch.manual_seed(seed)
    system = _build_system(arm, seed, lr)
    trainer = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(
            max_epochs=EPOCHS,
            device="cpu",
            seed=seed,
            track_flops=True,
            track_memory=True,
        ),
        train_data=_CappedLoader(train_loader, BATCHES_PER_EPOCH),
    )
    history = trainer.fit()
    resource = trainer.epoch_resources[-1]
    forward = _one_forward_flops(system, BATCH_SIZE)
    per_step = resource.forward_flops
    forward_equivalents = (
        per_step / resource.steps / forward
        if per_step and resource.steps and forward
        else None
    )
    # A fallback to parameter counting reports 1 forward-equivalent for a
    # settle-based rule; that is not a matched budget, so the cell is a gap.
    if forward_equivalents is not None and (
        abs(forward_equivalents - 2.0 * MAX_STEPS) > 1e-2
    ):
        forward_equivalents = None
    return (
        _accuracy(system, test_loader),
        float(history[-1]["train_acc"]),
        resource,
        forward_equivalents,
    )


def _note(arm: EstimatorArm, val_acc: float) -> str:
    """Why a below-floor cell is not a verdict (the plan's triage, per row)."""
    if val_acc >= FLOOR:
        return ""
    if arm.pc_alm:
        return (
            "regime-mismatch: below the floor at this shallow box; the card's "
            "validated limit is depth 100"
        )
    if arm.name == "gradient":
        return "invalid-learning control: the exact arm is at chance"
    return (
        "below the floor at this box; a ladder on its primary knob (or a "
        "regime transfer) is the trigger, not a refusal"
    )


def _write_cell(cell: EstimatorCell, progress: str | Path | None) -> None:
    """Append one cell to the kill-safe log before the next cell runs."""
    if progress is None:
        return
    path = Path(progress)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(asdict(cell)) + "\n")


def _refusal_cell(
    arm: EstimatorArm,
    *,
    seed: int,
    lr: float,
    stage: str,
    started: float,
    reference_norm: float,
    note: str,
) -> EstimatorCell:
    """A crash is a refusal with a trigger, recorded as a row — never a silent skip."""
    return EstimatorCell(
        arm=arm.name,
        estimator_kind=arm.estimator_kind,
        bias_reference=arm.bias_reference,
        stage=stage,
        seed=seed,
        lr=lr,
        angle=None,
        magnitude=None,
        update_norm=0.0,
        reference_norm=reference_norm,
        nonzero_update=False,
        val_acc=None,
        train_acc=None,
        steps=0,
        forward_equivalents=None,
        time_s=time.perf_counter() - started,
        note=note,
        refused=True,
    )


def _run_cell(  # ruff: ignore[too-many-locals]
    arm_name: str,
    *,
    seed: int,
    lr: float,
    stage: str,
    reference_delta: Tensor,
    probe: tuple[Tensor, Tensor],
    train_loader: Iterable,
    test_loader: Iterable,
    progress: str | Path | None,
) -> EstimatorCell:
    """Measure one arm at one seed: gradient coordinates, then one epoch."""
    arm = _build_arm(arm_name)
    started = time.perf_counter()
    reference_norm = float(reference_delta.norm())
    x, y = probe
    try:
        probe_system = _build_system(arm, seed, lr)
        before = _parameters(probe_system)
        probe_system.train_step(x, y)
        delta = _delta(before, probe_system)
    except (RuntimeError, ValueError) as exc:
        cell = _refusal_cell(
            arm,
            seed=seed,
            lr=lr,
            stage=stage,
            started=started,
            reference_norm=reference_norm,
            note=f"refusal at the probe step: {exc}",
        )
        _write_cell(cell, progress)
        return cell

    update_norm = float(delta.norm())
    angle = (
        float(F.cosine_similarity(delta.reshape(1, -1), reference_delta.reshape(1, -1)))
        if reference_norm > 0 and update_norm > 0
        else None
    )
    magnitude = update_norm / reference_norm if reference_norm > 0 else None

    # Reset the data order for the epoch: the probe consumed the stream.
    sampler = train_loader.sampler  # type: ignore[attr-defined]
    sampler.generator = torch.Generator().manual_seed(seed)
    try:
        val_acc, train_acc, resource, forward_equivalents = _train(
            arm, seed, lr, train_loader, test_loader
        )
    except (RuntimeError, ValueError) as exc:
        cell = _refusal_cell(
            arm,
            seed=seed,
            lr=lr,
            stage=stage,
            started=started,
            reference_norm=reference_norm,
            note=f"refusal at the epoch: {exc}",
        )
        cell = EstimatorCell(**{
            **asdict(cell),
            "angle": angle,
            "magnitude": magnitude,
            "update_norm": update_norm,
            "nonzero_update": update_norm > 0,
        })
        _write_cell(cell, progress)
        return cell

    cell = EstimatorCell(
        arm=arm_name,
        estimator_kind=arm.estimator_kind,
        bias_reference=arm.bias_reference,
        stage=stage,
        seed=seed,
        lr=lr,
        angle=angle,
        magnitude=magnitude,
        update_norm=update_norm,
        reference_norm=reference_norm,
        nonzero_update=update_norm > 0,
        val_acc=val_acc,
        train_acc=train_acc,
        steps=resource.steps,
        forward_equivalents=forward_equivalents,
        time_s=time.perf_counter() - started,
        note=_note(arm, val_acc),
    )
    _write_cell(cell, progress)
    return cell


def _verdict(  # ruff: ignore[too-many-return-statements]
    cells: tuple[EstimatorCell, ...],
    *,
    reference_fd_cosine: float,
    reference_control_tol: float = REFERENCE_CONTROL_TOL,
) -> tuple[str, str]:
    """The run's verdict: controls first, then the table as the artifact."""
    if reference_fd_cosine <= reference_control_tol:
        return (
            "invalid-instrument",
            f"autograd and its finite difference agree only at "
            f"cos={reference_fd_cosine:.3f} <= {reference_control_tol:g}; the "
            f"reference is not validated",
        )
    exact = tuple(cell for cell in cells if cell.arm == "gradient")
    if not exact:
        return ("invalid-learning", "the exact control arm did not run")
    collapsed = tuple(
        cell for cell in exact if cell.val_acc is None or cell.val_acc < FLOOR
    )
    if collapsed:
        return (
            "invalid-learning",
            f"the exact arm does not train at seed(s) "
            f"{', '.join(str(c.seed) for c in collapsed)} "
            f"(val acc {min((c.val_acc or 0.0) for c in collapsed):.3f} < floor "
            f"{FLOOR:g}); the run is invalid, not the treatment",
        )
    zero = tuple(cell for cell in cells if not cell.nonzero_update and not cell.refused)
    if zero:
        return (
            "defect",
            f"no update at {', '.join(f'{c.arm}/{c.seed}' for c in zero)}; "
            "the credit's probe step is a defect, not a coordinate",
        )
    refused = tuple(cell for cell in cells if cell.refused)
    below = tuple(
        cell for cell in cells if cell.val_acc is not None and cell.val_acc < FLOOR
    )
    if refused or below:
        parts = []
        if refused:
            parts.append(f"{', '.join(f'{c.arm}/{c.seed}' for c in refused)} refused")
        if below:
            parts.append(
                f"{', '.join(f'{c.arm}/{c.seed}' for c in below)} below the floor"
            )
        return (
            "atlas",
            f"{'; '.join(parts)} at this box; the rows carry their trigger and "
            "the table is the artifact, not a silent exclusion or a refusal of "
            "the track",
        )
    return (
        "atlas",
        "controls pass and every arm updates; the table is the artifact, not a winner",
    )


def _aggregate(cells: tuple[EstimatorCell, ...]) -> dict[str, dict[str, float | None]]:
    """Per-arm mean and sample sigma of the coordinates (None when n < 2)."""
    aggregate: dict[str, dict[str, float | None]] = {}
    for arm in dict.fromkeys(cell.arm for cell in cells):
        rows = tuple(cell for cell in cells if cell.arm == arm)
        entry: dict[str, float | None] = {}
        for field in ("angle", "magnitude", "val_acc", "time_s"):
            values = [
                float(value)
                for row in rows
                if (value := getattr(row, field)) is not None
            ]
            if not values:
                entry[field] = None
                entry[f"{field}_sigma"] = None
                continue
            mean = sum(values) / len(values)
            entry[field] = mean
            entry[f"{field}_sigma"] = (
                (sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** 0.5
                if len(values) > 1
                else None
            )
        aggregate[arm] = entry
    return aggregate


def _box(device: str, *, stage: str, seeds: tuple[int, ...]) -> dict[str, object]:
    return {
        "task": "mnist-quick",
        "geometry": "feedforward 784-32-10, Linear+ReLU",
        "batch_size": BATCH_SIZE,
        "batches_per_epoch": BATCHES_PER_EPOCH,
        "epochs": EPOCHS,
        "probe_batch": PROBE_BATCHES * BATCH_SIZE,
        "held_out": "full MNIST test split (10000 samples, 1 sigma = 0.3 pp)",
        "chance": CHANCE,
        "floor": FLOOR,
        "lr_ladder": LR_LADDER,
        "ladder_seed": LADDER_SEED,
        "confirm_seed": CONFIRM_SEED,
        "max_steps": MAX_STEPS,
        "beta": BETA,
        "pc_alm_dynamics_step": PCALM_DYNAMICS_STEP,
        "stage": stage,
        "seeds": seeds,
        "device": device,
        "cost": "CPU; forward-equivalents and walltime are the compute rulers",
    }


def _reference_delta(
    seed: int,
    probe: tuple[Tensor, Tensor],
    *,
    lr: float,
    train_loader: Iterable,
) -> Tensor:
    """The exact arm's one-step displacement at ``(seed, lr)``: the reference."""
    torch.manual_seed(seed)
    reference = _build_arm("gradient")
    reference_system = _build_system(reference, seed, lr)
    before = _parameters(reference_system)
    reference_system.train_step(*probe)
    return _delta(before, reference_system)


def _resume_cells(
    progress: str | Path | None,
) -> dict[tuple[str, int, float, str], EstimatorCell]:
    """Cells a kill left in the log, keyed by (arm, seed, lr, stage)."""
    if progress is None or not Path(progress).exists():
        return {}
    return {
        (cell.arm, cell.seed, cell.lr, cell.stage): cell
        for cell in read_cells(progress)
    }


def _cell_or_measure(  # ruff: ignore[too-many-arguments]
    done: dict[tuple[str, int, float, str], EstimatorCell],
    *,
    arm: str,
    seed: int,
    lr: float,
    stage: str,
    reference_delta: Tensor,
    probe: tuple[Tensor, Tensor],
    train_loader: Iterable,
    test_loader: Iterable,
    progress: str | Path | None,
) -> EstimatorCell:
    planned = done.get((arm, seed, lr, stage))
    if planned is not None:
        return planned
    return _run_cell(
        arm,
        seed=seed,
        lr=lr,
        stage=stage,
        reference_delta=reference_delta,
        probe=probe,
        train_loader=train_loader,
        test_loader=test_loader,
        progress=progress,
    )


def _loaders() -> tuple[Iterable, Iterable]:
    """Train and test loaders for the one cheap task."""
    from computronium import create_task
    from computronium.domains.base import TaskSplit

    task = create_task("mnist", device="cpu", quick_mode=True)
    task.setup()
    return (
        task.get_dataloader(TaskSplit.TRAIN),
        task.get_dataloader(TaskSplit.TEST),
    )


def run_estimator_atlas(  # ruff: ignore[too-many-locals]
    *,
    full: bool = False,
    device: str = "cpu",
    progress: str | Path | None = None,
) -> EstimatorReport:
    """E-lite (4 arms x 1 seed), then the full rung (6 arms x 3 seeds)."""
    stage = "full" if full else "lite"
    arms = ARMS if full else LITE_ARMS
    seeds = FULL_SEEDS if full else LITE_SEEDS
    done = _resume_cells(progress)
    if done:
        logger.info("reusing %d measured cells from %s", len(done), progress)
    train_loader, test_loader = _loaders()
    reference_fd_cosine = min(
        _reference_control(seed) for seed in (LADDER_SEED, CONFIRM_SEED, *seeds)
    )

    probes: dict[int, tuple[Tensor, Tensor]] = {}
    references: dict[tuple[int, float], Tensor] = {}
    for seed in (LADDER_SEED, CONFIRM_SEED, *seeds):
        torch.manual_seed(seed)
        probes[seed] = _probe_batch(train_loader, seed)

    def reference_for(seed: int, lr: float) -> Tensor:
        key = (seed, lr)
        if key not in references:
            references[key] = _reference_delta(
                seed, probes[seed], lr=lr, train_loader=train_loader
            )
        return references[key]

    ladder: list[EstimatorCell] = []
    cells: list[EstimatorCell] = []
    for arm in arms:
        ladder_cells = tuple(
            _cell_or_measure(
                done,
                arm=arm,
                seed=LADDER_SEED,
                lr=lr,
                stage="ladder",
                reference_delta=reference_for(LADDER_SEED, lr),
                probe=probes[LADDER_SEED],
                train_loader=train_loader,
                test_loader=test_loader,
                progress=progress,
            )
            for lr in LR_LADDER
        )
        best = max(
            ladder_cells,
            key=lambda cell: cell.val_acc if cell.val_acc is not None else -1.0,
        )
        confirmation = _cell_or_measure(
            done,
            arm=arm,
            seed=CONFIRM_SEED,
            lr=best.lr,
            stage="confirm",
            reference_delta=reference_for(CONFIRM_SEED, best.lr),
            probe=probes[CONFIRM_SEED],
            train_loader=train_loader,
            test_loader=test_loader,
            progress=progress,
        )
        ladder.extend((*ladder_cells, confirmation))
        for seed in seeds:
            cells.append(
                _cell_or_measure(
                    done,
                    arm=arm,
                    seed=seed,
                    lr=best.lr,
                    stage="atlas",
                    reference_delta=reference_for(seed, best.lr),
                    probe=probes[seed],
                    train_loader=train_loader,
                    test_loader=test_loader,
                    progress=progress,
                )
            )

    measured = tuple(cells)
    reference_control = reference_fd_cosine > REFERENCE_CONTROL_TOL
    learning_control = all(
        cell.val_acc is not None and cell.val_acc >= FLOOR
        for cell in (*ladder, *measured)
        if cell.arm == "gradient"
    )
    verdict, reason = _verdict(
        measured,
        reference_fd_cosine=reference_fd_cosine,
        reference_control_tol=REFERENCE_CONTROL_TOL,
    )
    return EstimatorReport(
        stage=stage,
        box=_box(device, stage=stage, seeds=seeds),
        cells=measured,
        ladder=tuple(ladder),
        reference_fd_cosine=reference_fd_cosine,
        reference_control=reference_control,
        learning_control=learning_control,
        verdict=verdict,
        reason=reason,
    )


def read_cells(progress: str | Path) -> tuple[EstimatorCell, ...]:
    """Read a kill-safe cell log back into cells (a replay, not a re-run)."""
    cells, seen = [], set()
    for line in Path(progress).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        cell = EstimatorCell(**json.loads(line))
        key = (cell.arm, cell.seed, cell.lr, cell.stage)
        if key in seen:
            continue
        seen.add(key)
        cells.append(cell)
    return tuple(cells)


def replay_estimator_atlas(
    *, progress: str | Path, device: str = "cpu"
) -> EstimatorReport:
    """Recompute the verdict from a cell log; no training, no new evidence."""
    cells = read_cells(progress)
    atlas = tuple(cell for cell in cells if cell.stage == "atlas")
    ladder = tuple(cell for cell in cells if cell.stage != "atlas")
    stage = "full" if len({cell.seed for cell in atlas}) > 1 else "lite"
    reference_fd_cosine = min(
        (_reference_control(seed) for seed in {cell.seed for cell in cells}),
        default=1.0,
    )
    verdict, reason = _verdict(atlas, reference_fd_cosine=reference_fd_cosine)
    return EstimatorReport(
        stage=stage,
        box=_box(device, stage=stage, seeds=tuple(sorted({c.seed for c in atlas}))),
        cells=atlas,
        ladder=ladder,
        reference_fd_cosine=reference_fd_cosine,
        reference_control=reference_fd_cosine > REFERENCE_CONTROL_TOL,
        learning_control=all(
            cell.val_acc is not None and cell.val_acc >= FLOOR
            for cell in cells
            if cell.arm == "gradient"
        ),
        verdict=verdict,
        reason=reason,
    )


def _markdown(report: EstimatorReport) -> str:
    """The table a third party can read, with its rulers and command."""
    lines = [
        "# E1 estimator atlas — bias, variance, and compute per kind",
        "",
        f"**Box.** {report.box['task']}, {report.box['geometry']}, "
        f"batch {report.box['batch_size']}, {report.box['batches_per_epoch']} "
        f"train batches, {report.box['epochs']} epoch, device "
        f"{report.box['device']}.",
        "",
        f"**Rulers.** held-out {report.box['held_out']}; chance "
        f"{CHANCE:g}; floor {FLOOR:g}; probe batch "
        f"{report.box['probe_batch']} samples; reference FD tolerance "
        f"{REFERENCE_CONTROL_TOL:g}; LR ladder {LR_LADDER} per arm.",
        "",
        "## Viability ladder (the fair chance, per arm)",
        "",
        _table(report.ladder),
        "",
        "## Atlas (the table is the artifact)",
        "",
        _table(report.cells),
        "",
        "| arm | angle mean | angle sigma | magnitude mean | magnitude sigma | "
        "val mean | val sigma |",
        "|---|---|---|---|---|---|---|",
    ]
    for arm, entry in _aggregate(report.cells).items():
        lines.append(
            f"| {arm} | {_number(entry['angle'])} | "
            f"{_number(entry['angle_sigma'])} | {_number(entry['magnitude'])} | "
            f"{_number(entry['magnitude_sigma'])} | {_number(entry['val_acc'])} | "
            f"{_number(entry['val_acc_sigma'])} |"
        )
    lines.extend([
        "",
        f"**Reference control:** FD vs autograd cos = "
        f"{report.reference_fd_cosine:.4f} -> "
        f"{'PASS' if report.reference_control else 'FAIL'}.",
        f"**Learning control (exact arm):** floor {FLOOR:g} -> "
        f"{'PASS' if report.learning_control else 'FAIL'}.",
        "",
        f"**Verdict: {report.verdict}** — {report.reason}",
        "",
        "A seed's variance is `None` when n=1: that is an honest gap, not a "
        "zero. `bias ref` is `none` for objective-local arms; their angle is "
        "update-direction alignment, never bias. The structural fwd-eq estimate "
        "cannot see PEPITA's second pass, so walltime is the compute ruler "
        "beside it. The ladder's best point is selected by held-out accuracy; "
        "claim seeds are disjoint from the ladder and confirmation seeds.",
        "",
        "Command: `uv run python -m computronium.validation.estimator_atlas "
        "--device cpu`; full rung: `... --full`; replay: `... --replay`.",
        "",
    ])
    return "\n".join(lines)


def _table(cells: tuple[EstimatorCell, ...]) -> str:
    lines = [
        "| arm | kind | bias ref | seed | lr | angle | magnitude | val acc | "
        "train acc | steps | fwd-eq | s | note |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cell in cells:
        angle = "—" if cell.angle is None else f"{cell.angle:+.3f}"
        magnitude = "—" if cell.magnitude is None else f"{cell.magnitude:.3f}"
        forward = (
            "—" if cell.forward_equivalents is None else f"{cell.forward_equivalents:g}"
        )
        val = "—" if cell.val_acc is None else f"{cell.val_acc:.3f}"
        train = "—" if cell.train_acc is None else f"{cell.train_acc:.3f}"
        lines.append(
            f"| {cell.arm} | {cell.estimator_kind} | {cell.bias_reference} | "
            f"{cell.seed} | {cell.lr:g} | {angle} | {magnitude} | "
            f"{val} | {train} | {cell.steps} | "
            f"{forward} | {cell.time_s:.1f} | {cell.note} |"
        )
    return "\n".join(lines)


def _number(value: float | None) -> str:
    return (
        "—" if value is None else f"{value:+.3f}" if abs(value) < 10 else f"{value:.3f}"
    )


def write_report(report: EstimatorReport, output_dir: str | Path) -> Path:
    """Write ``estimator.json`` and ``estimator.md``; return the JSON path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = asdict(report)
    path = output_dir / "estimator.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    (output_dir / "estimator.md").write_text(_markdown(report))
    return path


def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--device", default="cuda" if torch.cuda.is_available() else "cpu"
    )
    parser.add_argument("--full", action="store_true", help="run 6 arms x 3 seeds")
    parser.add_argument(
        "--replay", action="store_true", help="recompute the verdict from the cell log"
    )
    parser.add_argument("--out", default="results/t93_e1")
    args = parser.parse_args()
    progress = Path(args.out) / "estimator.cells.jsonl"
    report = (
        replay_estimator_atlas(progress=progress, device=args.device)
        if args.replay
        else run_estimator_atlas(full=args.full, device=args.device, progress=progress)
    )
    path = write_report(report, args.out)
    print(f"wrote {path}")
    print(f"verdict: {report.verdict} — {report.reason}")


if __name__ == "__main__":
    _main()
