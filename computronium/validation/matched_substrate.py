"""D2: the matched substrate comparison (TODO93 §8.1, track D).

D1 promoted the memristive arm at one cheap box: parity with the digital
rule at 2 B/weight against 4 B/weight. D2 asks the next question: **does
that saving survive a matched-budget comparison?** The memory arm runs the
same rule and architecture against three references:

- the same rule on a digital substrate at **matched settle compute** (the
  same settle length, so the substrate is isolated from the rule);
- digital backprop at the same budget (the **learning control**: it
  establishes that the box is learnable, not that parity holds);
- the int8 quantise-dequantise digital control (the same width, no device
  model), so a parity claim can name the constraint that binds.

The walltime, the forward-equivalents, and the device state are rulers
beside the accuracy, and the verdict must name which constraint binds:
the int8 width, the host-side conductance programming budget, or nothing
measurable (then D3's drift row is the only untested constraint).

**The box.** MNIST quick mode at *2x* D1's width (784-64-10), batch 32, 600
batches, one epoch, beta 0.5, full 10k test split (1 sigma = 0.3 pp), CPU.
The LR is frozen from D1 at 1e-2: the pilot's 3e-2 read the same accuracy,
so the upward LR check needs no new ladder at this box.

**The settle extension.** D1's best settle sat on the ladder's upper edge,
so D2 screens settle 40 against 20 on two disjoint seeds (57/58) before the
matched comparison. The extension is adopted for both arms only when the
memristive arm at 40 beats its own 20 by at least 0.5 pp on both screen
seeds; a screen cell that cannot train refuses the extension, not the
track.

**Paired seeds.** Five claim seeds (71-75), one paired row per seed. The
verdict is a paired 95% interval on the accuracy gap, so the margin is
not read off one seed.

Run it with::

    uv run python -m computronium.validation.matched_substrate --device cpu
    uv run python -m computronium.validation.matched_substrate --replay
"""

from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import torch

from computronium.experiment.execution.statistical_promotion import (
    compute_confidence_interval,
)
from computronium.validation.substrate_ladder import (
    FLOOR,
    HIDDEN_DIMS,
    LEARNING_CONTROL,
    PARITY_DELTA,
    SubstrateCell,
    _box,
    _cell_or_measure,
    _resume_cells,
    read_cells,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

logger = logging.getLogger(__name__)

__all__ = [
    "CONTROL_STEPS",
    "D2_LR",
    "EXTENSION_MARGIN",
    "EXTENSION_SEEDS",
    "PAIRED_SEEDS",
    "QDQ_ARM",
    "SETTLE_LADDER",
    "WALLTIME_RATIO",
    "MatchedGate",
    "MatchedPair",
    "MatchedReport",
    "replay_matched_comparison",
    "run_matched_comparison",
    "write_report",
]

#: The same rule on a digital substrate: the parity reference.
RULE_ARM = "digital"
#: The promoted substrate arm: energy minimisation on a differential int8 pair.
MEM_ARM = "memristive"
#: The int8 quantise-dequantise digital control: same width, no device model.
QDQ_ARM = "qdq"
#: D1's frozen LR for the rule and the memristive arm (the pilot read 3e-2).
D2_LR = 1e-2
#: D1's promoted settle and its upward extension.
SETTLE_LADDER = (20, 40)
#: The extension screen's seeds, disjoint from the claim seeds and D1's seeds.
EXTENSION_SEEDS = (57, 58)
#: Five paired claim seeds: the paired interval, not one seed, carries a claim.
PAIRED_SEEDS = (71, 72, 73, 74, 75)
#: The learning control's budget (settle is not part of backprop's path).
CONTROL_STEPS = 10
#: Adopt settle 40 only when the memory arm gains this on both screen seeds.
EXTENSION_MARGIN = 0.005
#: The cost ruler: the memory arm may not exceed this share of the rule's time.
WALLTIME_RATIO = 1.2
#: The box's width is D1's width doubled (the plan's declared box).
D2_HIDDEN_DIMS = (2 * HIDDEN_DIMS[0],)


@dataclass(frozen=True, slots=True)
class MatchedPair:
    """One paired row: four arms at one seed and one settle length."""

    seed: int
    settle: int
    rule: SubstrateCell
    memristive: SubstrateCell
    qdq: SubstrateCell
    control: SubstrateCell
    accuracy_gap: float | None
    qdq_gap: float | None
    walltime_ratio: float | None
    forward_ratio: float | None
    matched: bool


@dataclass(frozen=True, slots=True)
class MatchedGate:
    """The paired verdict with its rulers."""

    verdict: str
    reason: str
    mean_gap: float | None
    gap_ci95: tuple[float, float] | None
    mean_walltime_ratio: float | None
    mean_qdq_gap: float | None


@dataclass(frozen=True, slots=True)
class MatchedReport:
    """D2's measured table, its screen, and its pre-registered verdict."""

    stage: str
    box: dict[str, object]
    pairs: tuple[MatchedPair, ...]
    screen: tuple[SubstrateCell, ...]
    cells: tuple[SubstrateCell, ...]
    settle: int
    verdict: str
    reason: str
    mean_gap: float | None
    gap_ci95: tuple[float, float] | None
    mean_walltime_ratio: float | None
    mean_qdq_gap: float | None


def _diff(numerator: SubstrateCell, reference: SubstrateCell) -> float | None:
    """A cell's accuracy gap to the digital rule, or ``None`` if either failed."""
    if (
        numerator.val_acc is None
        or reference.val_acc is None
        or numerator.refused
        or reference.refused
    ):
        return None
    return numerator.val_acc - reference.val_acc


def _ratio(
    numerator: SubstrateCell,
    reference: SubstrateCell,
    field: str = "time_s",
) -> float | None:
    """A cell's cost ratio to the digital rule, or ``None`` when unpriced."""
    value = getattr(numerator, field)
    base = getattr(reference, field)
    if (
        value is None
        or base is None
        or base <= 0
        or numerator.refused
        or reference.refused
    ):
        return None
    return float(value) / float(base)


def _pair(
    seed: int,
    settle: int,
    *,
    rule: SubstrateCell,
    memristive: SubstrateCell,
    qdq: SubstrateCell,
    control: SubstrateCell,
) -> MatchedPair:
    """Join four measured cells into one paired row."""
    walltime_ratio = _ratio(memristive, rule)
    return MatchedPair(
        seed=seed,
        settle=settle,
        rule=rule,
        memristive=memristive,
        qdq=qdq,
        control=control,
        accuracy_gap=_diff(memristive, rule),
        qdq_gap=_diff(qdq, rule),
        walltime_ratio=walltime_ratio,
        forward_ratio=_ratio(memristive, rule, "forward_equivalents"),
        matched=walltime_ratio is not None and walltime_ratio <= WALLTIME_RATIO,
    )


def _screen_adopts(screen: tuple[SubstrateCell, ...]) -> bool:
    """Adopt the settle extension only when the memory arm gains on both seeds.

    A screen cell that refused refuses the extension (not the track): the
    matched comparison then stays at the ladder's lower point.
    """
    by_key = {(c.seed, c.arm, c.max_steps): c for c in screen}
    for seed in EXTENSION_SEEDS:
        low = by_key.get((seed, MEM_ARM, SETTLE_LADDER[0]))
        high = by_key.get((seed, MEM_ARM, SETTLE_LADDER[-1]))
        if low is None or high is None:
            return False
        if low.refused or high.refused:
            return False
        if low.val_acc is None or high.val_acc is None:
            return False
        if high.val_acc < low.val_acc + EXTENSION_MARGIN:
            return False
    return True


def _empty_gate(verdict: str, reason: str) -> MatchedGate:
    """A gate with no paired row: an invalid run, a park, or a crash refusal."""
    return MatchedGate(verdict, reason, None, None, None, None)


def _control_gate(
    pairs: tuple[MatchedPair, ...], *, floor: float
) -> MatchedGate | None:
    """A control or a reference below the floor invalidates the run."""
    if not pairs:
        return _empty_gate("park", "no paired rows to compare at this box")
    if any(p.control.refused or p.control.val_acc is None for p in pairs):
        return _empty_gate(
            "invalid-learning-control",
            "the digital backprop control refused a paired cell; an apparatus "
            "failure invalidates the run, not the substrate",
        )
    control_acc = min(p.control.val_acc or 0.0 for p in pairs)
    if control_acc < floor:
        return _empty_gate(
            "invalid-learning-control",
            f"the digital backprop control reads {control_acc:.3f}; a control "
            "below the floor invalidates the run, not the substrate",
        )
    if any(
        p.rule.refused or p.rule.val_acc is None or p.rule.val_acc < floor
        for p in pairs
    ):
        return _empty_gate(
            "invalid-reference",
            "the digital rule fell below the floor on a paired cell; a "
            "reference below the floor cannot decide parity",
        )
    return None


def _refusal_gate(pairs: tuple[MatchedPair, ...]) -> MatchedGate | None:
    """A crashed constrained cell is a refusal with a trigger, never skipped."""
    refused = [p.seed for p in pairs if p.memristive.refused or p.qdq.refused]
    if refused:
        return _empty_gate(
            "refuse",
            f"the constrained cells refused on seeds {refused}; a crash is a "
            "refusal with a trigger -- a wider device width or a learnable "
            "scale per layer is the re-open command",
        )
    return None


def _mechanism(mean_qdq: float, mean_ratio: float, *, parity_gap: float) -> str:
    """Name the constraint that binds: the width, the budget, or neither."""
    if mean_qdq < -parity_gap:
        return (
            "the int8 width binds (the QDQ control reads "
            f"{mean_qdq * 100:+.1f} pp against the digital rule), so the "
            "differential pair's conductance levels are the measured constraint"
        )
    if mean_ratio > WALLTIME_RATIO:
        return (
            "the int8 width is harmless at this box (the QDQ control reads "
            f"{mean_qdq * 100:+.1f} pp), so the programming budget binds: "
            f"the device path costs {mean_ratio:.2f}x the digital rule's "
            "walltime at matched settle compute, and a device-level "
            "quantisation path is the trigger"
        )
    return (
        "the int8 width is harmless at this box (the QDQ control reads "
        f"{mean_qdq * 100:+.1f} pp) and the device path costs "
        f"{mean_ratio:.2f}x the rule's walltime at matched settle compute, "
        "so the device model adds no measurable error; D3's drift row is the "
        "only untested constraint"
    )


def _paired_gate(
    pairs: tuple[MatchedPair, ...],
    *,
    settle: int,
    parity_gap: float,
    walltime_ratio: float,
) -> MatchedGate:
    """The paired interval, the cost ruler, and the constraint that binds."""
    gaps = [p.accuracy_gap for p in pairs if p.accuracy_gap is not None]
    qdq_gaps = [p.qdq_gap for p in pairs if p.qdq_gap is not None]
    ratios = [p.walltime_ratio for p in pairs if p.walltime_ratio is not None]
    mean_gap = math.fsum(gaps) / len(gaps)
    mean_qdq = math.fsum(qdq_gaps) / len(qdq_gaps)
    mean_ratio = math.fsum(ratios) / len(ratios)
    gap_ci95 = compute_confidence_interval(gaps)
    lower, upper = gap_ci95
    interval = f"[{lower * 100:+.1f}, {upper * 100:+.1f}] pp"
    mechanism = _mechanism(mean_qdq, mean_ratio, parity_gap=parity_gap)
    measured = (mean_gap, gap_ci95, mean_ratio, mean_qdq)
    if mean_ratio > walltime_ratio:
        return MatchedGate(
            "refuse",
            f"the memristive arm costs {mean_ratio:.2f}x the digital rule's "
            f"walltime at matched settle compute (limit {walltime_ratio:.1f}x) "
            f"with a mean accuracy gap of {mean_gap * 100:+.1f} pp "
            f"(paired 95% interval {interval}); the measured mechanism: "
            f"{mechanism}",
            *measured,
        )
    if mean_gap < -parity_gap:
        return MatchedGate(
            "refuse",
            f"the memristive arm trails the digital rule by "
            f"{-mean_gap * 100:.1f} pp at {mean_ratio:.2f}x walltime "
            f"(paired 95% interval {interval} on {len(gaps)} seeds); "
            f"the measured mechanism: {mechanism}",
            *measured,
        )
    if lower < -parity_gap:
        return MatchedGate(
            "coordinate",
            f"the mean gap is {mean_gap * 100:+.1f} pp but its paired 95% "
            f"interval {interval} crosses the {parity_gap * 100:.0f} pp margin "
            f"at n_max={len(gaps)}; a wider seed plan is the trigger, not a "
            f"verdict. The measured mechanism: {mechanism}",
            *measured,
        )
    return MatchedGate(
        "promote",
        f"the memristive arm is within {parity_gap * 100:.0f} pp of the "
        f"digital rule at settle {settle} on {len(gaps)} paired seeds "
        f"(mean gap {mean_gap * 100:+.1f} pp, paired 95% interval {interval}) "
        f"at {mean_ratio:.2f}x walltime and 2 vs 4 B/weight; {mechanism}; "
        "D3 is the retention/drift rung",
        *measured,
    )


def _gate(
    *,
    pairs: tuple[MatchedPair, ...],
    settle: int,
    parity_gap: float = PARITY_DELTA,
    walltime_ratio: float = WALLTIME_RATIO,
    floor: float = FLOOR,
) -> MatchedGate:
    """Controls first, then the paired interval, the cost, and the mechanism."""
    return (
        _control_gate(pairs, floor=floor)
        or _refusal_gate(pairs)
        or _paired_gate(
            pairs,
            settle=settle,
            parity_gap=parity_gap,
            walltime_ratio=walltime_ratio,
        )
    )


def _measure(
    done: dict[tuple[str, str, int, float, int], SubstrateCell],
    *,
    arm: str,
    stage: str,
    seed: int,
    steps: int,
    device: str,
    train_loader: Iterable,
    test_loader: Iterable,
    progress: str | Path | None,
) -> SubstrateCell:
    """Reuse a measured cell; otherwise run it at the D2 box."""
    key = (arm, stage, seed, D2_LR, steps)
    if key not in done:
        done[key] = _cell_or_measure(
            done,
            arm=arm,
            stage=stage,
            seed=seed,
            lr=D2_LR,
            max_steps=steps,
            device=device,
            train_loader=train_loader,
            test_loader=test_loader,
            progress=progress,
            hidden_dims=D2_HIDDEN_DIMS,
        )
    return done[key]


def _measure_pair(
    measure: Callable[..., SubstrateCell], *, seed: int, settle: int
) -> MatchedPair:
    """Measure one seed's four arms and join them."""
    return _pair(
        seed,
        settle,
        rule=measure(RULE_ARM, "matched", seed=seed, steps=settle),
        memristive=measure(MEM_ARM, "matched", seed=seed, steps=settle),
        qdq=measure(QDQ_ARM, "matched", seed=seed, steps=settle),
        control=measure(LEARNING_CONTROL, "control", seed=seed, steps=CONTROL_STEPS),
    )


def _report(
    *,
    pairs: tuple[MatchedPair, ...],
    screen: tuple[SubstrateCell, ...],
    settle: int,
    device: str,
) -> MatchedReport:
    """Build the report from its paired rows and screen."""
    gate = _gate(pairs=pairs, settle=settle)
    cells = (
        *screen,
        *(
            cell
            for pair in pairs
            for cell in (pair.rule, pair.memristive, pair.qdq, pair.control)
        ),
    )
    box = _box(device, stage="matched", hidden_dims=D2_HIDDEN_DIMS)
    for key in ("max_steps_ladder", "lr_ladder", "ladder_seed", "confirm_seed"):
        box.pop(key, None)
    box.update({
        "settle_ladder": SETTLE_LADDER,
        "paired_seeds": PAIRED_SEEDS,
        "extension_seeds": EXTENSION_SEEDS,
        "extension_margin": EXTENSION_MARGIN,
        "lr": D2_LR,
        "walltime_ratio": WALLTIME_RATIO,
        "rule": "energy_minimization + thermodynamic_contrast on the digital "
        "rule, the memristive pair, and the int8 QDQ control; instantaneous "
        "+ gradient for the backprop learning control",
    })
    return MatchedReport(
        stage="matched",
        box=box,
        pairs=pairs,
        screen=screen,
        cells=cells,
        settle=settle,
        verdict=gate.verdict,
        reason=gate.reason,
        mean_gap=gate.mean_gap,
        gap_ci95=gate.gap_ci95,
        mean_walltime_ratio=gate.mean_walltime_ratio,
        mean_qdq_gap=gate.mean_qdq_gap,
    )


def run_matched_comparison(
    *, device: str = "cpu", progress: str | Path | None = None
) -> MatchedReport:
    """Screen the settle extension, then run five paired seeds at the adopted box."""
    from computronium import create_task
    from computronium.domains.base import TaskSplit

    done = _resume_cells(progress)
    if done:
        logger.info("reusing %d measured cells from %s", len(done), progress)
    task = create_task("mnist", device="cpu", quick_mode=True)
    task.setup()
    train_loader = task.get_dataloader(TaskSplit.TRAIN)
    test_loader = task.get_dataloader(TaskSplit.TEST)

    def measure(arm: str, stage: str, *, seed: int, steps: int) -> SubstrateCell:
        return _measure(
            done,
            arm=arm,
            stage=stage,
            seed=seed,
            steps=steps,
            device=device,
            train_loader=train_loader,
            test_loader=test_loader,
            progress=progress,
        )

    screen = tuple(
        measure(MEM_ARM, "screen", seed=seed, steps=steps)
        for seed in EXTENSION_SEEDS
        for steps in SETTLE_LADDER
    )
    settle = SETTLE_LADDER[-1] if _screen_adopts(screen) else SETTLE_LADDER[0]
    logger.info("extension screen: settle %d adopted", settle)
    pairs = tuple(
        _measure_pair(measure, seed=seed, settle=settle) for seed in PAIRED_SEEDS
    )
    return _report(pairs=pairs, screen=screen, settle=settle, device=device)


def replay_matched_comparison(
    *, progress: str | Path, device: str = "cpu"
) -> MatchedReport:
    """Recompute the screen and the gate from the cell log, without training."""
    cells = read_cells(progress)
    if not cells:
        raise RuntimeError(f"no cells in {progress}; run the comparison first")
    screen = tuple(c for c in cells if c.stage == "screen")
    settle = (
        SETTLE_LADDER[-1] if screen and _screen_adopts(screen) else SETTLE_LADDER[0]
    )
    by_key = {(c.arm, c.seed): c for c in cells if c.stage == "matched"}
    pairs = tuple(
        _pair(
            seed,
            settle,
            rule=by_key["digital", seed],
            memristive=by_key["memristive", seed],
            qdq=by_key["qdq", seed],
            control=next(
                c for c in cells if c.arm == LEARNING_CONTROL and c.seed == seed
            ),
        )
        for seed in PAIRED_SEEDS
        if ("digital", seed) in by_key
        and ("memristive", seed) in by_key
        and ("qdq", seed) in by_key
        and any(c.arm == LEARNING_CONTROL and c.seed == seed for c in cells)
    )
    return _report(pairs=pairs, screen=screen, settle=settle, device=device)


def _markdown(report: MatchedReport) -> str:
    """The table a third party can read, with its rulers and command."""
    box = report.box
    lines = [
        "# D2 matched substrate comparison -- memristive + energy_min",
        "",
        f"**Box.** {box}",
        "",
        "**State ruler.** device state per step = weight bits / 8 (+ one fp32 "
        "scale per layer for a quantised substrate); the QDQ control is 8 "
        "bits/weight with no device model, the memristive pair 16, the digital "
        "rule 32. Train state is declared, equal for every arm.",
        "",
        "| seed | settle | digital rule | memristive | gap | QDQ control | "
        "QDQ gap | backprop | walltime | fwd | matched |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for pair in report.pairs:
        rule = pair.rule.val_acc
        mem = pair.memristive.val_acc
        qdq = pair.qdq.val_acc
        control = pair.control.val_acc
        lines.append(
            f"| {pair.seed} | {pair.settle} | "
            f"{f'{rule:.3f}' if rule is not None else 'refused'} | "
            f"{f'{mem:.3f}' if mem is not None else 'refused'} | "
            f"{f'{pair.accuracy_gap * 100:+.1f} pp' if pair.accuracy_gap is not None else '—'} | "
            f"{f'{qdq:.3f}' if qdq is not None else 'refused'} | "
            f"{f'{pair.qdq_gap * 100:+.1f} pp' if pair.qdq_gap is not None else '—'} | "
            f"{f'{control:.3f}' if control is not None else 'refused'} | "
            f"{f'{pair.walltime_ratio:.2f}x' if pair.walltime_ratio is not None else '—'} | "
            f"{f'{pair.forward_ratio:.2f}x' if pair.forward_ratio is not None else '—'} | "
            f"{'yes' if pair.matched else 'no'} |"
        )
    lines.extend([
        "",
        "**Extension screen** (seeds 57/58; adopt 40 only when the "
        "memristive arm gains 0.5 pp on both):",
        "",
        "| seed | arm | settle | val acc | s |",
        "|---|---|---|---|---|",
    ])
    for cell in report.screen:
        shown = f"{cell.val_acc:.3f}" if cell.val_acc is not None else "refused"
        lines.append(
            f"| {cell.seed} | {cell.arm} | {cell.max_steps} | {shown} | "
            f"{cell.time_s:.1f} |"
        )
    lines.extend([
        "",
        f"**Verdict: {report.verdict}** -- {report.reason}",
        "",
        "**Rulers.** paired accuracy gap (memristive - digital rule) with its "
        "95% interval; walltime ratio at matched settle compute; "
        "forward-equivalents ratio; device state per step (2 vs 4 vs 1 "
        "B/weight).",
        "",
        "Command: `uv run python -m computronium.validation."
        "matched_substrate --device "
        f"{box.get('device')}`; replay from the cell log: `... --replay`.",
        "",
    ])
    return "\n".join(lines)


def write_report(report: MatchedReport, output_dir: str | Path) -> Path:
    """Write ``matched.json`` and ``matched.md``; return the JSON path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "matched.json"
    path.write_text(json.dumps(asdict(report), indent=2) + "\n")
    (output_dir / "matched.md").write_text(_markdown(report))
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
    parser.add_argument("--out", default="results/t93_d2")
    args = parser.parse_args()
    progress = Path(args.out) / "matched.cells.jsonl"
    report = (
        replay_matched_comparison(progress=progress, device=args.device)
        if args.replay
        else run_matched_comparison(device=args.device, progress=progress)
    )
    path = write_report(report, args.out)
    print(f"wrote {path}")
    print(f"verdict: {report.verdict} -- {report.reason}")


if __name__ == "__main__":
    _main()
