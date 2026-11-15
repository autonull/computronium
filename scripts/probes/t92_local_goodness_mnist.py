"""TODO92 §3.11 follow-up: does `local_goodness` match gradient at claim grade?

The viability map (§3.11) measured `local_goodness` with its declared target
channel (`credit.readout_error=True`) at 0.9619 / 0.9623 against `gradient`
0.9562 / 0.9456 on the §3.7 MNIST anchor: one epoch, seed 57/157, lr 1e-3.
That is screening. This probe runs the pre-registered matched pair in
``configs/preregistrations/t92_local_goodness_gradient.json``: L2/20, 10k held
out, fresh seeds 57-61, decision by
``PairedComparison.passes_equivalence(0.01)``.

The control is the §3.7 gradient anchor. The treatment changes the credit and
declares its target channel (``credit.readout_error=True``); every other axis,
the schedule and the seed are shared. That channel is part of the credit, not a
second axis — the control has no equivalent flag, so the matcher allows exactly
this one declared parameter difference and prints it.

Run: uv run python scripts/probes/t92_local_goodness_mnist.py --pilot
     uv run python scripts/probes/t92_local_goodness_mnist.py
     uv run python scripts/probes/t92_local_goodness_mnist.py --report-only
Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import time
from dataclasses import asdict, replace
from pathlib import Path

from computronium.core.utils.git import git_sha
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import cell_record, evaluate_cell
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)
from computronium.validation.preregistration import (
    EquivalenceRegistration,
    paired_comparison,
)

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "experiments/t92_local_goodness_mnist.duckdb"
REGISTRATION = ROOT / "configs/preregistrations/t92_local_goodness_gradient.json"
ANCHOR_STORE = ROOT / "experiments/experiment_20261109_103319.duckdb"
ANCHOR = "bfab4794"
SEEDS = (57, 58, 59, 60, 61)
CONTROL = "gradient"
TREATMENT = "local_goodness"
CHANNEL: dict[str, object] = {"credit.readout_error": True}


def _anchor() -> tuple[Coordinate, Schedule]:
    with RecordStore(StoreConfig(path=ANCHOR_STORE, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(ANCHOR):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {ANCHOR} in {ANCHOR_STORE}"
    raise LookupError(msg)


def _coordinates(anchor: Coordinate) -> dict[str, Coordinate]:
    control = replace(anchor, credit=CONTROL)
    treatment = replace(anchor, credit=TREATMENT, params=dict(anchor.params) | CHANNEL)
    return {CONTROL: control, TREATMENT: treatment}


def _check_matched(coordinates: dict[str, Coordinate]) -> None:
    axes = {
        arm: {
            key: value for key, value in asdict(coordinate).items() if key != "credit"
        }
        for arm, coordinate in coordinates.items()
    }
    control, treatment = axes[CONTROL], axes[TREATMENT]
    difference = {
        key: (control[key], treatment[key])
        for key in control
        if control[key] != treatment[key]
    }
    if difference != {"params": ({}, CHANNEL)}:
        msg = f"arms differ beyond the declared credit channel: {difference}"
        raise ValueError(msg)
    print(f"matched: {CONTROL} vs {TREATMENT} differ only in credit + {CHANNEL}")


def _provenance(run_id: str) -> Provenance:
    env = {
        key: value
        for key, value in os.environ.items()
        if key.startswith(("CUDA", "TORCH", "OMP", "OPENBLAS"))
    }
    env.setdefault("python", platform.python_version())
    return Provenance(
        env=env,
        dataset="mnist",
        dataset_version="probe",
        code_sha=git_sha() or "local",
        policy="t92_local_goodness_mnist",
        links={"run_id": run_id},
    )


def _schedule(anchor: Schedule, device: str | None) -> Schedule:
    return replace(
        anchor,
        fidelity="L2",
        budget_id="L2_initial",
        epochs=20,
        n_seeds=len(SEEDS),
        seed=SEEDS[0],
        device=device or anchor.device,
    )


def _values(store: RecordStore, run_id: str) -> dict[str, dict[int, float]]:
    values: dict[str, dict[int, float]] = {CONTROL: {}, TREATMENT: {}}
    for record in store.query_records(run_id=run_id):
        if record.credit not in values or record.schedule.seed not in SEEDS:
            continue
        if record.status.gate_verdict.value != "PASS":
            print(
                f"{record.credit} seed={record.schedule.seed}: "
                f"gate={record.status.gate_verdict.value} "
                f"defect={record.status.defect}"
            )
            continue
        values[record.credit][record.schedule.seed] = float(record.payload["val_acc"])
    return values


def _cost(store: RecordStore, run_id: str) -> dict[str, float]:
    cost: dict[str, float] = {}
    for record in store.query_records(run_id=run_id):
        if record.credit in {CONTROL, TREATMENT}:
            cost[record.credit] = cost.get(record.credit, 0.0) + float(
                record.payload.get("walltime_s", 0.0)
            )
    return cost


def _report(values: dict[str, dict[int, float]], cost: dict[str, float]) -> int:
    registration = EquivalenceRegistration.load(REGISTRATION)
    for arm, measured in values.items():
        seeds = [measured[seed] for seed in SEEDS if seed in measured]
        if not seeds:
            print(f"{arm:16}: 0/{len(SEEDS)} seeds recorded")
            continue
        print(
            f"{arm:16}: n={len(seeds)} mean={statistics.mean(seeds):.4f} "
            f"sd={statistics.stdev(seeds) if len(seeds) > 1 else 0.0:.4f} "
            f"cost={cost.get(arm, 0.0):.0f}s"
        )
    if any(len(measured) < len(SEEDS) for measured in values.values()):
        print(
            "incomplete: "
            + ", ".join(
                f"{arm} {len(measured)}/{len(SEEDS)}"
                for arm, measured in values.items()
            )
        )
        return 2
    paired = [values[TREATMENT][seed] for seed in SEEDS]
    reference = [values[CONTROL][seed] for seed in SEEDS]
    result = paired_comparison(paired, reference, seed=0)
    equivalent = result.passes_equivalence(registration)
    print(
        f"paired {TREATMENT} - {CONTROL}: {result.mean_diff:+.4f} "
        f"95% CI [{result.ci_lower:+.4f}, {result.ci_upper:+.4f}] "
        f"p={result.p_value:.4f} dz={result.cohens_dz:.2f}"
    )
    print(
        f"verdict: {'EQUIVALENT' if equivalent else 'NOT-EQUIVALENT'} "
        f"(margin=±{registration.margin:.4f}, alpha={registration.alpha})"
    )
    return 0 if equivalent else 1


def _pilot(
    coordinates: dict[str, Coordinate],
    schedule: Schedule,
    seed: int,
    device: str | None,
) -> int:
    schedule = replace(schedule, seed=seed, epochs=1, device=device or schedule.device)
    for arm, coordinate in coordinates.items():
        started = time.perf_counter()
        result = evaluate_cell(coordinate, schedule)
        print(
            f"pilot {arm:16} seed={seed:3} device={schedule.device:4} "
            f"val_acc={result.metrics['val_acc']:.4f} "
            f"({time.perf_counter() - started:.1f}s)",
            flush=True,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default=None, help="cpu or cuda")
    args = parser.parse_args(argv)

    anchor_coordinate, anchor_schedule = _anchor()
    coordinates = _coordinates(anchor_coordinate)
    _check_matched(coordinates)
    schedule = _schedule(anchor_schedule, args.device)

    if args.pilot:
        return _pilot(coordinates, schedule, args.seed, args.device)

    with RecordStore(StoreConfig(path=STORE)) as store:
        runs = store.query_runs(limit=1)
        run_id = runs[0].run_id if runs else store.create_run()
        print(f"run {run_id[:8]} store {STORE.relative_to(ROOT)}")
        if not args.report_only:
            provenance = _provenance(run_id)
            done = {
                (record.credit, record.schedule.seed)
                for record in store.query_records(run_id=run_id)
            }
            for arm, coordinate in coordinates.items():
                for seed in SEEDS:
                    if (arm, seed) in done:
                        print(f"{arm:16} seed={seed}: already recorded")
                        continue
                    started = time.perf_counter()
                    record = cell_record(
                        coordinate, replace(schedule, seed=seed), provenance
                    )
                    store.append(record)
                    print(
                        f"{arm:16} seed={seed}: "
                        f"val_acc={record.payload.get('val_acc')} "
                        f"gate={record.status.gate_verdict.value} "
                        f"({time.perf_counter() - started:.1f}s)",
                        flush=True,
                    )
        values = _values(store, run_id)
        cost = _cost(store, run_id)
        if not args.report_only:
            complete = all(len(measured) == len(SEEDS) for measured in values.values())
            store.finish_run(
                run_id, "completed" if complete else "incomplete", sum(cost.values())
            )
    return _report(values, cost)


if __name__ == "__main__":
    raise SystemExit(main())
