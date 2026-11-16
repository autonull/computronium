"""B1: the routing ladder (TODO93 §5, track B).

The screen asks one question: **does the straight-through (STE) gradient's
bias grow with the number of stacked hard selections?** The question is what
decides the track. A gap that compounds with depth means a matched pair of
credits is worth running (B2); a gap that stays flat means depth is not the
axis the surrogate is wrong on, and the track is refused with a trigger.

**What is measured, and against what.** The hard top-k router's true gradient
is zero almost everywhere, so "bias" has no meaning without a declared
reference. The reference here is the temperature-smoothed routing gradient
(the same router weights, the same probe batch, the same temperature, with the
selection replaced by the soft mixture over all experts). A finite-difference
probe on that smoothed objective validates the reference itself, so the
instrument control is "the reference tracks its own objective", not "STE is
right". Both numbers are recorded per cell; the reference's agreement is a
gate, the STE gap is the mechanism claim.

**The ladder.** A 3-point temperature ladder at :data:`TEMP_LADDER_DEPTH`
chooses the best temperature by end-task accuracy. The 4-point depth ladder
(1/2/4/8 stacked selections) then runs at that temperature, and a disjoint
confirmation seed repeats the two endpoints. The gate is pre-registered: the
gap must clear :data:`GROWTH_DELTA` from the first depth to the last **on both
seeds**; flat is a refusal with a trigger, not a failure.

**Rulers.** End-task accuracy is read on a 2000-sample held-out split of a
4-class synthetic task, so its binomial 1-sigma is ~1.0 pp. Router accuracy
is the last block's top-k agreement with the head's per-expert argmin loss;
its chance level is ``k / n_experts`` (:data:`ROUTER_CHANCE`). The gradient
gap is a relative norm, dimensionless, on a fixed probe batch.

Run it with::

    uv run python -m computronium.validation.routing_ladder --device cuda
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
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

__all__ = [
    "DEPTHS",
    "FLOOR",
    "GROWTH_DELTA",
    "HELD_OUT",
    "LADDER_SEEDS",
    "REFERENCE_TOL",
    "ROUTER_CHANCE",
    "TEMPERATURES",
    "RoutingCell",
    "RoutingNet",
    "RoutingReport",
    "read_cells",
    "replay_routing",
    "run_routing_ladder",
]

#: The held-out split: 2000 samples over 4 classes (1 sigma = 1.0 pp).
HELD_OUT = 2000
NUM_CLASSES = 4
INPUT_DIM = 8
TRAIN_SAMPLES = 4096
BATCH_SIZE = 64
EPOCHS = 4
LR = 1e-3
DIM = 32
EXPERTS = 8
TOP_K = 2
#: Router accuracy's chance level: k of n experts are selected per sample.
ROUTER_CHANCE = TOP_K / EXPERTS
#: Pre-registered viability floor for the arm's learning control.
FLOOR = 0.40
#: Pre-registered growth margin on the relative STE gap, depth 1 -> depth 8.
GROWTH_DELTA = 0.05
#: The reference is validated by finite differences within this relative error.
REFERENCE_TOL = 0.10
#: Finite-difference step along the reference direction (declared scale).
FD_EPS = 1e-2
TEMPERATURES = (0.25, 0.5, 1.0)
DEPTHS = (1, 2, 4, 8)
TEMP_LADDER_DEPTH = 2
LADDER_SEEDS = (51,)
CONFIRM_SEEDS = (52,)
#: Probe batch for the gradient measurements: fixed, seeded, no augmentation.
PROBE_BATCH = 512
#: Where on the training path the gap is probed, in optimiser steps.
PROBE_STEPS = (8, 16, 32)


def _blobs(
    task_seed: int, n: int, seed: int, device: torch.device
) -> tuple[Tensor, Tensor]:
    """Samples from one task's fixed blob centers, drawn with ``seed``.

    The centers belong to the task (``task_seed``), so the held-out split is
    drawn from the same distribution the arm trains on; only the samples move.
    """
    centers = (
        torch.randn(
            NUM_CLASSES,
            INPUT_DIM,
            generator=torch.Generator(device="cpu").manual_seed(task_seed),
        )
        * 2.0
    )
    generator = torch.Generator(device="cpu").manual_seed(seed)
    labels = torch.randint(0, NUM_CLASSES, (n,), generator=generator)
    noise = torch.randn(n, INPUT_DIM, generator=generator) * 0.5
    return (centers[labels] + noise).to(device), labels.to(device)


class GatedBlock(torch.nn.Module):
    """One hard top-k selection over ``EXPERTS`` expert banks.

    Forward is always the hard selection (eval semantics). Backward is the
    surrogate under test: ``ste`` routes credit through the selected experts'
    masked softmax; ``soft`` is the temperature-smoothed mixture over all
    experts, the reference objective.
    """

    def __init__(self, temperature: float, mode: str = "ste") -> None:
        super().__init__()
        self.router: torch.nn.Linear = torch.nn.Linear(DIM, EXPERTS)
        self.experts = torch.nn.ModuleList(
            torch.nn.Sequential(
                torch.nn.Linear(DIM, DIM), torch.nn.ReLU(), torch.nn.Linear(DIM, DIM)
            )
            for _ in range(EXPERTS)
        )
        object.__setattr__(self, "temperature", temperature)
        object.__setattr__(self, "mode", mode)

    def expert_list(self) -> list[torch.nn.Module]:
        """The expert banks as a typed list (``ModuleList`` is not generic)."""
        return cast("list[torch.nn.Module]", list(self.experts))

    def selection(self, h: Tensor) -> tuple[Tensor, Tensor]:
        """Weights and hard mask for ``h``: STE (masked softmax) or soft."""
        scores = self.router(h) / self.temperature
        index = scores.topk(TOP_K, dim=-1).indices
        mask = torch.zeros_like(scores).scatter_(-1, index, 1.0)
        if self.mode == "soft":
            return torch.softmax(scores, dim=-1), mask
        masked = scores.masked_fill(mask == 0, float("-inf"))
        selected = torch.softmax(masked, dim=-1)
        return mask + selected - selected.detach(), mask

    def forward(self, h: Tensor) -> tuple[Tensor, Tensor]:
        weights, mask = self.selection(h)
        stacked = torch.stack([expert(h) for expert in self.expert_list()], dim=1)
        return (weights.unsqueeze(-1) * stacked).sum(dim=1), mask


class RoutingNet(torch.nn.Module):
    """A trunk feeding ``depth`` parallel selections, averaged, into one head.

    The selections are stacked in parallel and averaged, not chained: a chained
    stack's joint gradient vanishes with depth (each mixture's softmax
    saturates), so a chained ladder would measure the depth of the stack
    instead of the surrogate's bias on one selection. Averaging also keeps the
    forward scale depth-invariant, which is what "matched" means here.
    """

    def __init__(self, *, depth: int, temperature: float, mode: str = "ste") -> None:
        super().__init__()
        self.inp: torch.nn.Linear = torch.nn.Linear(INPUT_DIM, DIM)
        self.blocks = torch.nn.ModuleList(
            GatedBlock(temperature, mode) for _ in range(depth)
        )
        self.head: torch.nn.Linear = torch.nn.Linear(DIM, NUM_CLASSES)

    def block_list(self) -> list[GatedBlock]:
        """The blocks as a typed list (``ModuleList`` is not generic)."""
        return cast("list[GatedBlock]", list(self.blocks))

    def _trunk(self, x: Tensor) -> Tensor:
        return F.relu(self.inp(x))

    def forward(self, x: Tensor) -> Tensor:
        h = self._trunk(x)
        out = sum(block(h)[0] for block in self.block_list()) / len(self.blocks)
        return self.head(out)

    def set_mode(self, mode: str) -> None:
        for block in self.block_list():
            object.__setattr__(block, "mode", mode)

    def router_parameters(self) -> list[Tensor]:
        return [block.router.weight for block in self.block_list()]

    def last_selection(self, x: Tensor) -> Tensor:
        """The last block's hard mask, i.e. which experts each sample routes to."""
        return self.block_list()[-1].selection(self._trunk(x))[1]

    def expert_losses(self, x: Tensor, y: Tensor) -> Tensor:
        """Per-sample loss if the last block routed to one expert, [n, E]."""
        h = self._trunk(x)
        blocks = self.block_list()
        depth = len(blocks)
        base = sum((block(h)[0] for block in blocks[:-1]), torch.zeros_like(h)) / depth
        last = blocks[-1]
        stacked = (
            torch.stack([expert(h) for expert in last.expert_list()], dim=1) / depth
        )
        logits = self.head((base.unsqueeze(1) + stacked).reshape(-1, DIM))
        target = y.repeat_interleave(EXPERTS)
        return F.cross_entropy(
            logits.view(-1, NUM_CLASSES), target, reduction="none"
        ).view(len(y), EXPERTS)


@dataclass(frozen=True, slots=True)
class RoutingCell:
    """One measured cell: a depth and a temperature, one seed."""

    stage: str
    depth: int
    temperature: float
    seed: int
    end_task_acc: float
    router_acc: float
    ste_gap: float
    reference_gap: float
    ste_norm: float
    reference_norm: float
    time_s: float


@dataclass(frozen=True, slots=True)
class RoutingReport:
    """The ladder's measured table and its pre-registered verdict."""

    stage: str
    box: dict[str, object]
    cells: tuple[RoutingCell, ...]
    best: RoutingCell | None
    depth_ladder: tuple[RoutingCell, ...]
    confirmation: tuple[RoutingCell, ...]
    verdict: str
    reason: str


def _accuracy(net: RoutingNet, x: Tensor, y: Tensor) -> tuple[float, float]:
    """Held-out end-task accuracy and the router's own accuracy."""
    net.set_mode("ste")
    with torch.no_grad():
        acc = (net(x).argmax(dim=-1) == y).float().mean().item()
    mask = net.last_selection(x)
    best = net.expert_losses(x, y).argmin(dim=-1)
    routed = mask.gather(1, best.unsqueeze(-1)).mean().item()
    return acc, routed


def _objective(net: RoutingNet, x: Tensor, y: Tensor) -> Tensor:
    """The mean cross-entropy the arm trains on, under its current mode."""
    return F.cross_entropy(net(x), y)


def _finite_difference(
    net: RoutingNet, x: Tensor, y: Tensor, block: GatedBlock, direction: Tensor
) -> float:
    """Central difference of the smoothed objective along one router's gradient."""
    net.set_mode("soft")
    param = block.router.weight
    unit = direction / direction.norm().clamp_min(1e-12)
    with torch.no_grad():
        param.add_(unit, alpha=FD_EPS)
        plus = _objective(net, x, y).item()
        param.add_(unit, alpha=-2 * FD_EPS)
        minus = _objective(net, x, y).item()
        param.add_(unit, alpha=FD_EPS)
    return (plus - minus) / (2 * FD_EPS)


def _gradient_gap(
    net: RoutingNet, x: Tensor, y: Tensor
) -> tuple[float, float, float, float]:
    """Mean per-selection STE gap, worst reference mismatch, and mean norms.

    The gap is read per selection rather than on the stacked vector: a deep
    stack's joint gradient shrinks with depth, so a joint ratio would measure
    the depth of the stack instead of the surrogate's bias on one selection.

    The finite-difference probe reads the same smoothed objective the
    reference differentiates, so its agreement validates the reference, not
    the STE arm.
    """
    net.set_mode("ste")
    ste = torch.autograd.grad(_objective(net, x, y), net.router_parameters())
    net.set_mode("soft")
    reference = torch.autograd.grad(_objective(net, x, y), net.router_parameters())
    gaps: list[float] = []
    mismatches: list[float] = []
    ste_norms: list[float] = []
    reference_norms: list[float] = []
    for block, g_ste, g_ref in zip(net.block_list(), ste, reference, strict=True):
        reference_norm = g_ref.norm().clamp_min(1e-12).item()
        ste_norm = g_ste.norm().item()
        gaps.append((g_ste - g_ref).norm().item() / reference_norm)
        ste_norms.append(ste_norm)
        reference_norms.append(reference_norm)
        directional = _finite_difference(net, x, y, block, g_ref)
        mismatches.append(
            abs(directional - reference_norm) / max(directional, reference_norm)
        )
    count = len(gaps)
    return (
        sum(gaps) / count,
        max(mismatches),
        sum(ste_norms) / count,
        sum(reference_norms) / count,
    )


def _train(
    net: RoutingNet,
    x: Tensor,
    y: Tensor,
    *,
    seed: int,
    device: torch.device,
    probe: Callable[[], tuple[float, float, float, float]],
) -> list[tuple[float, float, float, float]]:
    """Four epochs of seeded minibatch Adam, probing the gap on the way.

    The gap is probed at :data:`PROBE_STEPS`, not at the end: once the router
    saturates, both the STE gradient and its reference vanish, and their ratio
    measures the one-hot limit rather than the surrogate's bias. The probe
    points are declared in the box, so they are part of the measurement, not a
    search.
    """
    generator = torch.Generator(device="cpu").manual_seed(seed)
    optimizer = torch.optim.Adam(net.parameters(), lr=LR)
    net.set_mode("ste")
    marks = set(PROBE_STEPS)
    probes: list[tuple[float, float, float, float]] = []
    step = 0
    for _epoch in range(EPOCHS):
        order = torch.randperm(len(y), generator=generator).to(device)
        for start in range(0, len(y), BATCH_SIZE):
            index = order[start : start + BATCH_SIZE]
            optimizer.zero_grad()
            _objective(net, x[index], y[index]).backward()
            optimizer.step()
            step += 1
            if step in marks:
                probes.append(probe())
    return probes


@dataclass(frozen=True, slots=True)
class _Measurement:
    """What one trained arm measures: its rulers and its gradient gap."""

    end_task_acc: float
    router_acc: float
    ste_gap: float
    reference_gap: float
    ste_norm: float
    reference_norm: float


def _measure(*, depth: int, temperature: float, seed: int, device: str) -> _Measurement:
    """Train one arm, read its rulers, and average its training-path gap."""
    target = torch.device(device)
    torch.manual_seed(seed)
    x_train, y_train = _blobs(seed, TRAIN_SAMPLES, seed, target)
    x_probe, y_probe = _blobs(seed, HELD_OUT, seed + 1000, target)
    probe_x, probe_y = x_probe[:PROBE_BATCH], y_probe[:PROBE_BATCH]
    net = RoutingNet(depth=depth, temperature=temperature).to(target)
    probes = _train(
        net,
        x_train,
        y_train,
        seed=seed,
        device=target,
        probe=lambda: _gradient_gap(net, probe_x, probe_y),
    )
    end_task_acc, router_acc = _accuracy(net, x_probe, y_probe)
    count = len(probes)
    return _Measurement(
        end_task_acc=end_task_acc,
        router_acc=router_acc,
        ste_gap=sum(p[0] for p in probes) / count,
        reference_gap=max(p[1] for p in probes),
        ste_norm=sum(p[2] for p in probes) / count,
        reference_norm=sum(p[3] for p in probes) / count,
    )


def _run_cell(
    *,
    stage: str,
    depth: int,
    temperature: float,
    seed: int,
    device: str,
    progress: str | Path | None = None,
) -> RoutingCell:
    """Time one measurement and log its cell."""
    start = time.perf_counter()
    measured = _measure(depth=depth, temperature=temperature, seed=seed, device=device)
    cell = RoutingCell(
        stage=stage,
        depth=depth,
        temperature=temperature,
        seed=seed,
        **asdict(measured),
        time_s=time.perf_counter() - start,
    )
    return _emit(cell, progress)


def _emit(cell: RoutingCell, progress: str | Path | None) -> RoutingCell:
    """Append one finished cell to the progress log, so a kill keeps evidence."""
    if progress is not None:
        path = Path(progress)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(cell)) + "\n")
    return cell


def _best_temperature(cells: tuple[RoutingCell, ...]) -> RoutingCell | None:
    """The ladder's best point: end-task accuracy, then the graded reference.

    Ties at 3 decimals go to the cell with the larger mean reference norm: the
    gradient measurement with more signal, not the sharper one.
    """
    return max(
        cells,
        key=lambda cell: (round(cell.end_task_acc, 3), cell.reference_norm),
        default=None,
    )


def _growth(cells: tuple[RoutingCell, ...]) -> float:
    """The gap's rise from the shallowest admissible depth to the deepest."""
    ordered = sorted(cells, key=lambda c: c.depth)
    if len(ordered) < 2:
        return 0.0
    return ordered[-1].ste_gap - ordered[0].ste_gap


def _instrument_failure(cells: tuple[RoutingCell, ...]) -> str | None:
    """The reference must track its own smoothed objective, or bias is undefined."""
    for cell in cells:
        if cell.reference_gap > REFERENCE_TOL:
            return (
                f"reference misses its finite difference by "
                f"{cell.reference_gap:.3f} at depth {cell.depth} "
                f"(tol {REFERENCE_TOL:g}): the bias is undefined"
            )
    return None


def _learning_failure(best: RoutingCell | None, deep: RoutingCell | None) -> str | None:
    """Both ends of the ladder must be trained arms, not chance-level cells."""
    if best is None:
        return "no temperature cell measured"
    if best.end_task_acc < FLOOR:
        return (
            f"the arm reads {best.end_task_acc:.3f} below the floor {FLOOR} "
            f"at tau={best.temperature:g}: it does not train"
        )
    if deep is not None and deep.end_task_acc < FLOOR:
        return (
            f"the deepest arm reads {deep.end_task_acc:.3f} below the floor "
            f"{FLOOR} at depth {deep.depth}: the growth cell is not a trained arm"
        )
    return None


def _verdict(
    *,
    temperature_cells: tuple[RoutingCell, ...],
    depth_ladder: tuple[RoutingCell, ...],
    confirmation: tuple[RoutingCell, ...],
) -> tuple[str, str]:
    """Apply the pre-registered B1 gate: controls, then growth on two seeds."""
    failure = _instrument_failure((*temperature_cells, *depth_ladder, *confirmation))
    if failure is not None:
        return "invalid-instrument", failure
    shallow = min(depth_ladder, key=lambda c: c.depth)
    deep = max(depth_ladder, key=lambda c: c.depth)
    best = _best_temperature(temperature_cells)
    failure = _learning_failure(best, deep)
    if failure is not None:
        return "invalid-learning", failure
    growth = _growth(depth_ladder)
    conf_growth = _growth(confirmation)
    summary = (
        f"gap {shallow.ste_gap:.3f} -> {deep.ste_gap:.3f} "
        f"({growth:+.3f}) at tau={deep.temperature:g}, depth "
        f"{shallow.depth}->{deep.depth}, end-task acc "
        f"{shallow.end_task_acc:.3f}/{deep.end_task_acc:.3f}"
    )
    if len(confirmation) < 2:
        return (
            "promote-provisional",
            f"{summary}; the confirmation seed has no depth pair",
        )
    if growth >= GROWTH_DELTA and conf_growth >= GROWTH_DELTA:
        return (
            "promote",
            f"{summary}; the confirmation seed repeats it ({conf_growth:+.3f}): "
            f"the bias compounds with stacked hard selections",
        )
    return (
        "refuse",
        f"{summary}; the confirmation seed reads {conf_growth:+.3f} against "
        f"the pre-registered growth margin {GROWTH_DELTA:g}: the depth axis "
        f"is not where the surrogate is wrong",
    )


def _box(device: str) -> dict[str, object]:
    """The identity card of the B1 ladder, shared by the run and its replay."""
    return {
        "task": "gaussian-blobs",
        "classes": NUM_CLASSES,
        "train_samples": TRAIN_SAMPLES,
        "held_out": HELD_OUT,
        "probe_batch": PROBE_BATCH,
        "probe_steps": PROBE_STEPS,
        "dim": DIM,
        "experts": EXPERTS,
        "top_k": TOP_K,
        "batch_size": BATCH_SIZE,
        "epochs": EPOCHS,
        "lr": LR,
        "temperature_ladder": TEMPERATURES,
        "depth_ladder": DEPTHS,
        "temp_ladder_depth": TEMP_LADDER_DEPTH,
        "growth_delta": GROWTH_DELTA,
        "reference_tol": REFERENCE_TOL,
        "fd_eps": FD_EPS,
        "seeds": LADDER_SEEDS + CONFIRM_SEEDS,
        "device": device,
    }


def read_cells(progress: str | Path) -> tuple[RoutingCell, ...]:
    """Read a kill-safe cell log back into cells (a replay, not a re-run).

    A kill can land between a cell's write and the report's, so the same
    ``(stage, depth, temperature, seed)`` row can appear twice; the first
    measurement wins.
    """
    cells, seen = [], set()
    for line in Path(progress).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        cell = RoutingCell(**json.loads(line))
        key = (cell.stage, cell.depth, cell.temperature, cell.seed)
        if key in seen:
            continue
        seen.add(key)
        cells.append(cell)
    return tuple(cells)


def replay_routing(*, progress: str | Path, device: str = "cuda") -> RoutingReport:
    """Recompute the B1 gate from a cell log; no training, no new evidence."""
    cells = read_cells(progress)
    temperatures = tuple(c for c in cells if c.stage == "temperature")
    ladder = tuple(c for c in cells if c.stage == "depth")
    confirmation = tuple(c for c in cells if c.stage == "confirmation")
    verdict, reason = _verdict(
        temperature_cells=temperatures,
        depth_ladder=ladder,
        confirmation=confirmation,
    )
    return RoutingReport(
        stage="routing",
        box=_box(device),
        cells=temperatures + ladder,
        best=_best_temperature(temperatures),
        depth_ladder=ladder,
        confirmation=confirmation,
        verdict=verdict,
        reason=reason,
    )


def _resume_cells(
    progress: str | Path | None,
) -> dict[tuple[str, int, float, int], RoutingCell]:
    """Cells a kill left in the log, keyed by stage, depth, temperature, seed."""
    if progress is None or not Path(progress).exists():
        return {}
    return {(c.stage, c.depth, c.temperature, c.seed): c for c in read_cells(progress)}


def _cell_or_measure(
    done: dict[tuple[str, int, float, int], RoutingCell],
    *,
    stage: str,
    depth: int,
    temperature: float,
    seed: int,
    device: str,
    progress: str | Path | None,
) -> RoutingCell:
    """Reuse a measured cell; otherwise run it and log it."""
    planned = done.get((stage, depth, temperature, seed))
    if planned is not None:
        return planned
    return _run_cell(
        stage=stage,
        depth=depth,
        temperature=temperature,
        seed=seed,
        device=device,
        progress=progress,
    )


def run_routing_ladder(
    *, device: str = "cuda", progress: str | Path | None = None
) -> RoutingReport:
    """The temperature ladder, then the depth ladder at its best point.

    A cell already present in ``progress`` is reused, not re-run, so a kill
    costs only the cell in flight.
    """
    done = _resume_cells(progress)
    if done:
        logger.info("reusing %d measured cells from %s", len(done), progress)
    temperatures = tuple(
        _cell_or_measure(
            done,
            stage="temperature",
            depth=TEMP_LADDER_DEPTH,
            temperature=temperature,
            seed=LADDER_SEEDS[0],
            device=device,
            progress=progress,
        )
        for temperature in TEMPERATURES
    )
    best = _best_temperature(temperatures)
    if best is None:
        raise RuntimeError("the temperature ladder produced no cell")
    ladder = tuple(
        _cell_or_measure(
            done,
            stage="depth",
            depth=depth,
            temperature=best.temperature,
            seed=LADDER_SEEDS[0],
            device=device,
            progress=progress,
        )
        for depth in DEPTHS
    )
    confirmation = tuple(
        _cell_or_measure(
            done,
            stage="confirmation",
            depth=depth,
            temperature=best.temperature,
            seed=CONFIRM_SEEDS[0],
            device=device,
            progress=progress,
        )
        for depth in (DEPTHS[0], DEPTHS[-1])
    )
    verdict, reason = _verdict(
        temperature_cells=temperatures,
        depth_ladder=ladder,
        confirmation=confirmation,
    )
    return RoutingReport(
        stage="routing",
        box=_box(device),
        cells=temperatures + ladder,
        best=best,
        depth_ladder=ladder,
        confirmation=confirmation,
        verdict=verdict,
        reason=reason,
    )


def _markdown(report: RoutingReport) -> str:
    """The table a third party can read, with its rulers and command."""
    box = report.box
    lines = [
        "# B1 routing ladder — stacked hard selections",
        "",
        f"**Box.** {box}",
        "",
        "**Rulers.** held-out 2000 samples (1 sigma = 0.010); chance "
        f"{1 / NUM_CLASSES:.2f}; floor {FLOOR}; router chance "
        f"{ROUTER_CHANCE:.3f}; growth margin {GROWTH_DELTA:g}; reference "
        f"tolerance {REFERENCE_TOL:g}.",
        "",
        "| stage | depth | tau | seed | end-task acc | router acc | STE gap | "
        "reference gap | s |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for cell in report.cells + report.confirmation:
        lines.append(
            f"| {cell.stage} | {cell.depth} | {cell.temperature:g} | "
            f"{cell.seed} | {cell.end_task_acc:.3f} | {cell.router_acc:.3f} | "
            f"{cell.ste_gap:.3f} | {cell.reference_gap:.3f} | {cell.time_s:.1f} |"
        )
    lines.extend([
        "",
        f"**Verdict: {report.verdict}** — {report.reason}",
        "",
        "Command: `uv run python -m computronium.validation.routing_ladder "
        f"--device {box['device']}`; replay from the cell log: "
        "`... --replay`.",
        "",
    ])
    return "\n".join(lines)


def write_report(report: RoutingReport, output_dir: str | Path) -> Path:
    """Write ``routing.json`` and ``routing.md``; return the JSON path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = asdict(report)
    payload["best"] = asdict(report.best) if report.best else None
    path = output_dir / "routing.json"
    path.write_text(json.dumps(payload, indent=2) + "\n")
    (output_dir / "routing.md").write_text(_markdown(report))
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
    parser.add_argument("--out", default="results/t93_b1")
    args = parser.parse_args()
    progress = Path(args.out) / "routing.cells.jsonl"
    report = (
        replay_routing(progress=progress, device=args.device)
        if args.replay
        else run_routing_ladder(device=args.device, progress=progress)
    )
    path = write_report(report, args.out)
    print(f"wrote {path}")
    print(f"verdict: {report.verdict} — {report.reason}")


if __name__ == "__main__":
    _main()
