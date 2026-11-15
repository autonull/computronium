"""TODO92 §3.10: credit × substrate 2×2 on `local_goodness` vs `gradient`.

The interaction is `(LG - grad)_analog - (LG - grad)_digital` on the §3.7
MNIST anchor at L2/20, read as a **noise response**: the analog substrate is the
digital matmul plus additive state noise (0.1), not a distinct operator.

The digital arms are already measured (§3.11 follow-up,
``experiments/t92_local_goodness_mnist.duckdb``); this probe runs the two analog
arms into ``experiments/t92_credit_substrate_lg.duckdb`` and pairs by seed. The
decision is the pre-registered ±0.01 band in
``configs/preregistrations/t92_credit_substrate_lg.json``.

- ``--pilot``: one epoch, both credits on analog, seed 57. Prices the run and
  answers rung 1 (does `local_goodness` train on the analog substrate?).
- full run: 20 epochs (L2/20), seeds 57-61, 10 cells; records PASS/FAIL.
- ``--report-only``: re-read the store and print the verdict.

Measured 2026-11-15 (L2/20, seeds 57-61, CPU, 4095 s total): analog
gradient **0.9748 ± 0.0024** vs digital 0.9759 ± 0.0017; analog
`local_goodness` **0.9657 ± 0.0024** vs digital 0.9753 ± 0.0011. Interaction
**−0.0085**, 95% CI [−0.0108, −0.0060], p=0.008, dz=−2.73 — the CI straddles
the pre-registered ±0.01 margin, so **no interaction at the declared margin**;
the direction is unfavorable and recorded as a boundary coordinate.

Walltime printed, never recorded as a claim.

Run: uv run python scripts/probes/t92_credit_substrate_lg.py --pilot
     uv run python scripts/probes/t92_credit_substrate_lg.py
     uv run python scripts/probes/t92_credit_substrate_lg.py --report-only
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
STORE = ROOT / "experiments/t92_credit_substrate_lg.duckdb"
DIGITAL_STORE = ROOT / "experiments/t92_local_goodness_mnist.duckdb"
REGISTRATION = ROOT / "configs/preregistrations/t92_credit_substrate_lg.json"
ANCHOR_STORE = ROOT / "experiments/experiment_20261109_103319.duckdb"
ANCHOR = "bfab4794"
SEEDS = (57, 58, 59, 60, 61)
DIGITAL = "digital"
ANALOG = "analog"
CREDITS = ("gradient", "local_goodness")
CHANNEL: dict[str, object] = {"credit.readout_error": True}


def _anchor() -> tuple[Coordinate, Schedule]:
    with RecordStore(StoreConfig(path=ANCHOR_STORE, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(ANCHOR):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {ANCHOR} in {ANCHOR_STORE}"
    raise LookupError(msg)


def _coordinate(anchor: Coordinate, credit: str, substrate: str) -> Coordinate:
    params = dict(anchor.params)
    if credit == "local_goodness":
        params |= CHANNEL
    return replace(anchor, credit=credit, substrate=substrate, params=params)


def _coordinates(anchor: Coordinate) -> dict[tuple[str, str], Coordinate]:
    return {
        (substrate, credit): _coordinate(anchor, credit, substrate)
        for substrate in (DIGITAL, ANALOG)
        for credit in CREDITS
    }


def _check_matched(anchor: Coordinate, analog: Coordinate) -> None:
    difference = {
        key: (getattr(anchor, key), getattr(analog, key))
        for key in asdict(anchor)
        if getattr(anchor, key) != getattr(analog, key)
    }
    if set(difference) != {"substrate"}:
        msg = f"analog arm differs beyond the substrate: {difference}"
        raise ValueError(msg)
    print("matched: analog differs from the digital anchor only in substrate")


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
        policy="t92_credit_substrate_lg",
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


def _digital_values() -> dict[str, dict[int, float]]:
    values: dict[str, dict[int, float]] = {credit: {} for credit in CREDITS}
    with RecordStore(StoreConfig(path=DIGITAL_STORE, read_only=True)) as store:
        for record in store.query_records():
            if (
                record.credit in values
                and record.substrate == DIGITAL
                and record.schedule.seed in SEEDS
                and record.status.gate_verdict.value == "PASS"
            ):
                values[record.credit][record.schedule.seed] = float(
                    record.payload["val_acc"]
                )
    missing = {
        credit: sorted(set(SEEDS) - set(measured))
        for credit, measured in values.items()
        if len(measured) != len(SEEDS)
    }
    if missing:
        msg = f"digital arms incomplete in {DIGITAL_STORE}: {missing}"
        raise LookupError(msg)
    return values


def _analog_values(store: RecordStore, run_id: str) -> dict[str, dict[int, float]]:
    values: dict[str, dict[int, float]] = {credit: {} for credit in CREDITS}
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
        if record.credit in CREDITS:
            cost[record.credit] = cost.get(record.credit, 0.0) + float(
                record.payload.get("walltime_s", 0.0)
            )
    return cost


def _report(
    digital: dict[str, dict[int, float]],
    analog: dict[str, dict[int, float]],
    cost: dict[str, float],
) -> int:
    registration = EquivalenceRegistration.load(REGISTRATION)
    for substrate, values in (
        (DIGITAL, digital),
        (ANALOG, analog),
    ):
        for credit, measured in values.items():
            seeds = [measured[seed] for seed in SEEDS if seed in measured]
            if not seeds:
                print(f"{substrate:7} {credit:16}: 0/{len(SEEDS)} seeds recorded")
                continue
            sd = statistics.stdev(seeds) if len(seeds) > 1 else 0.0
            cost_note = (
                f" cost={cost.get(credit, 0.0):.0f}s" if substrate == ANALOG else ""
            )
            print(
                f"{substrate:7} {credit:16}: n={len(seeds)} "
                f"mean={statistics.mean(seeds):.4f} sd={sd:.4f}{cost_note}"
            )
    incomplete = [credit for credit in CREDITS if len(analog[credit]) < len(SEEDS)]
    if incomplete:
        print(f"incomplete analog arms: {incomplete}")
        return 2
    interactions: list[float] = []
    for seed in SEEDS:
        d_analog = analog["local_goodness"][seed] - analog["gradient"][seed]
        d_digital = digital["local_goodness"][seed] - digital["gradient"][seed]
        interactions.append(d_analog - d_digital)
    result = paired_comparison(interactions, [0.0] * len(interactions), seed=0)
    print(
        f"interaction (LG-grad)_analog - (LG-grad)_digital: "
        f"{result.mean_diff:+.4f} 95% CI "
        f"[{result.ci_lower:+.4f}, {result.ci_upper:+.4f}] "
        f"p={result.p_value:.4f} dz={result.cohens_dz:.2f}"
    )
    margin = registration.margin
    if result.passes_equivalence(registration):
        verdict = f"NO INTERACTION (CI inside +/-{margin:.4f})"
    elif result.ci_lower > margin:
        verdict = f"POSITIVE interaction (noise-robustness advantage, > +{margin:.4f})"
    elif result.ci_upper < -margin:
        verdict = f"NEGATIVE interaction (noise-robustness loss, < -{margin:.4f})"
    else:
        verdict = "BOUNDARY (CI straddles the margin; report the measured boundary)"
    print(f"verdict: {verdict}")
    return 0


def _pilot(
    anchor: Coordinate, schedule: Schedule, seed: int, device: str | None
) -> int:
    schedule = replace(schedule, seed=seed, epochs=1, device=device or schedule.device)
    for credit in CREDITS:
        coordinate = _coordinate(anchor, credit, ANALOG)
        started = time.perf_counter()
        result = evaluate_cell(coordinate, schedule)
        print(
            f"pilot {ANALOG:7} {credit:16} seed={seed:3} device={schedule.device:4} "
            f"val_acc={result.metrics['val_acc']:.4f} "
            f"({time.perf_counter() - started:.1f}s)",
            flush=True,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--seed", type=int, default=57)
    parser.add_argument("--device", default=None, help="cpu or cuda")
    args = parser.parse_args(argv)

    anchor_coordinate, anchor_schedule = _anchor()
    coordinates = _coordinates(anchor_coordinate)
    _check_matched(anchor_coordinate, coordinates[ANALOG, "gradient"])
    schedule = _schedule(anchor_schedule, args.device)

    if args.pilot:
        return _pilot(anchor_coordinate, schedule, args.seed, args.device)

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
            for credit in CREDITS:
                coordinate = coordinates[ANALOG, credit]
                for seed in SEEDS:
                    if (credit, seed) in done:
                        print(f"{credit:16} seed={seed}: already recorded")
                        continue
                    started = time.perf_counter()
                    record = cell_record(
                        coordinate, replace(schedule, seed=seed), provenance
                    )
                    store.append(record)
                    print(
                        f"{credit:16} seed={seed}: "
                        f"val_acc={record.payload.get('val_acc')} "
                        f"gate={record.status.gate_verdict.value} "
                        f"({time.perf_counter() - started:.1f}s)",
                        flush=True,
                    )
        analog = _analog_values(store, run_id)
        cost = _cost(store, run_id)
        if not args.report_only:
            complete = all(len(analog[credit]) == len(SEEDS) for credit in CREDITS)
            store.finish_run(
                run_id, "completed" if complete else "incomplete", sum(cost.values())
            )
    return _report(_digital_values(), analog, cost)


if __name__ == "__main__":
    raise SystemExit(main())
