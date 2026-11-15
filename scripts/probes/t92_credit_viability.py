"""TODO92 §3.11: the credit viability map, before any credit comparison.

TODO92 §5 and AGENTS.md's breadth exit ask the same question about every
error-aware credit before one is ranked: does this implementation compose on a
legal cell, produce a non-zero update, and clear the task's chance ruler at
some point of its own primary knob? A credit with no above-chance point is a
defect or a refusal probe, not a coordinate to compare.

This probe runs the AGENTS viability ladder per credit — 3 values of the
credit's primary knob, one seed each, plus one confirmation seed at the best
point — on the §3.7 MNIST anchor (feedforward, instantaneous where the credit
allows it, adam). Ruler: val_acc on 10k held out, chance 0.10, 1 epoch.

Primary knob, per credit:

- ``credit.feedback_scale`` (γ for PEPITA, the FA/DFA feedback scale) where the
  credit's own sensitive knob is the feedback matrix;
- ``update.step_size`` (lr) otherwise.

``local_goodness`` declares its target channel with ``credit.readout_error``;
without it the credit is error-blind by construction, so the ladder sets it.

``homeostatic`` and ``temporal_trace`` declare ``error_blind=True``: chance is
their contract, so accuracy is not their ruler and they are not in this map.
§3.9's one-step parameter fingerprint already classifies both live.

Prints the map; records nothing. Screening, not a claim.

Run: uv run python scripts/probes/t92_credit_viability.py
     uv run python scripts/probes/t92_credit_viability.py --only pepita pc_alm
"""

from __future__ import annotations

import argparse
import time
from dataclasses import dataclass, replace
from pathlib import Path

from computronium.experiment.kernel.evaluate import evaluate_cell

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
ANCHOR = ("experiments/experiment_20261109_103319.duckdb", "bfab4794")
CHANCE = 0.10
LR = "update.step_size"
GAMMA = "credit.feedback_scale"
LR_VALUES: tuple[float, ...] = (3e-4, 1e-3, 3e-3)
GAMMA_VALUES: tuple[float, ...] = (0.01, 0.05, 0.25)


@dataclass(frozen=True, slots=True)
class Ladder:
    """One credit's legal cheap cell and its primary knob."""

    dynamics: str
    knob: str
    values: tuple[float, ...]
    fixed: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True, slots=True)
class LadderResult:
    """One credit's ladder: its points, its best point, its confirmation."""

    knob: str
    points: tuple[tuple[float, float], ...]
    best_value: float
    best_acc: float
    confirmation: float
    viable: bool
    error: str | None = None


LADDERS: dict[str, Ladder] = {
    "gradient": Ladder("instantaneous", LR, LR_VALUES),
    "pepita": Ladder("instantaneous", GAMMA, GAMMA_VALUES),
    "local_goodness": Ladder(
        "instantaneous", LR, LR_VALUES, (("credit.readout_error", True),)
    ),
    "local_contrastive": Ladder("instantaneous", LR, LR_VALUES),
    "target_inversion": Ladder("instantaneous", LR, LR_VALUES),
    "random_projections": Ladder("instantaneous", GAMMA, GAMMA_VALUES),
    "thermodynamic_contrast": Ladder("energy_minimization", LR, LR_VALUES),
    "pc_alm": Ladder("pc_alm", LR, LR_VALUES),
}


def _anchor():
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.schema.coordinate import Coordinate

    store_name, anchor = ANCHOR
    with RecordStore(StoreConfig(path=ROOT / store_name, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(anchor):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {anchor} in {store_name}"
    raise LookupError(msg)


def _cell(
    credit: str,
    ladder: Ladder,
    knob_value: float,
    seed: int,
    epochs: int,
    device: str,
) -> tuple[float, float]:
    coordinate, schedule = _anchor()
    params = dict(coordinate.params)
    params.update(dict(ladder.fixed))
    params[ladder.knob] = knob_value
    run = replace(
        coordinate,
        credit=credit,
        dynamics=ladder.dynamics,
        params=params,
    )
    started = time.perf_counter()
    result = evaluate_cell(
        run, replace(schedule, seed=seed, epochs=epochs, device=device)
    )
    return result.metrics["val_acc"], time.perf_counter() - started


def _print(
    credit: str,
    ladder: Ladder,
    knob_value: float,
    seed: int,
    epochs: int,
    device: str,
) -> float:
    value, wall = _cell(credit, ladder, knob_value, seed, epochs, device)
    print(
        f"{credit:23} {ladder.dynamics:18} {ladder.knob.split('.')[-1]}="
        f"{knob_value:<8g} seed={seed:3} val_acc={value:.4f} ({wall:.1f}s)",
        flush=True,
    )
    return value


def _ladder(
    credit: str, ladder: Ladder, seed: int, epochs: int, device: str
) -> LadderResult:
    points = tuple(
        (value, _print(credit, ladder, value, seed, epochs, device))
        for value in ladder.values
    )
    best_value, best_acc = max(points, key=lambda point: point[1])
    confirmation = _print(credit, ladder, best_value, seed + 100, epochs, device)
    return LadderResult(
        knob=ladder.knob,
        points=points,
        best_value=best_value,
        best_acc=best_acc,
        confirmation=confirmation,
        viable=max(best_acc, confirmation) > CHANCE,
    )


def _report(map_: dict[str, LadderResult]) -> int:
    print("\ncredit viability map (val_acc, 1 epoch, MNIST, chance 0.10)")
    print(f"{'credit':23} {'points':34} {'best':>8} {'conf':>8} verdict")
    for credit, row in map_.items():
        plotted = ",".join(f"{value:g}:{acc:.3f}" for value, acc in row.points) or "-"
        print(
            f"{credit:23} {plotted:34} {row.best_acc:8.4f} {row.confirmation:8.4f} "
            f"{'VIABLE' if row.viable else 'AT CHANCE -> triage'}"
        )
    viable = [credit for credit, row in map_.items() if row.viable]
    print(f"\n{len(viable)}/{len(map_)} error-aware credits above chance: {viable}")
    return 0 if len(viable) == len(map_) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=57)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--only", nargs="*", default=None)
    args = parser.parse_args(argv)

    selected = {
        credit: ladder
        for credit, ladder in LADDERS.items()
        if args.only is None or credit in args.only
    }
    started = time.perf_counter()
    map_: dict[str, LadderResult] = {}
    for credit, ladder in selected.items():
        try:
            map_[credit] = _ladder(credit, ladder, args.seed, args.epochs, args.device)
        except Exception as exc:  # ruff: ignore[blind-except] — a refused cell is a map row
            print(f"{credit:23} ladder failed: {type(exc).__name__}: {exc}", flush=True)
            map_[credit] = LadderResult(
                knob=ladder.knob,
                points=(),
                best_value=0.0,
                best_acc=0.0,
                confirmation=0.0,
                viable=False,
                error=f"{type(exc).__name__}: {exc}",
            )
    verdict = _report(map_)
    print(f"walltime {time.perf_counter() - started:.0f}s")
    return verdict


if __name__ == "__main__":
    raise SystemExit(main())
