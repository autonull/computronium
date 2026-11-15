"""TODO92 §3.10: does dynamics change what the credit axis buys on Cora?

The first interaction. PEPITA is refused on graph (``local_contrastive_geometry``
requires feedforward), so the graph credit pair is ``random_projections``
(error-aware layered FA) against ``gradient``. The 2x2 is dynamics
{``instantaneous``, ``energy_minimization``} x credit {``gradient``,
``random_projections``} on the Cora anchor (node classification, 500-node
public split, majority 0.316):

    interaction(seed) = (RP - gradient)_energy - (RP - gradient)_instantaneous

Anchored on record ``6328d4d4`` (digital/graph/null/adam, step_size 0.01,
L2/100, cuda). Seeds 47-51 are fresh; the pre-registration is
``configs/preregistrations/t92_dynamics_credit_cora.json``.

Measured (2026-11-14, RTX 3080, 1 epoch, seed 42): both energy cells train;
energy_minimization + random_projections 7.5 s/epoch vs instantaneous <0.05 s,
so the energy arms are ~750 s/seed. If random_projections cannot train under
instantaneous dynamics, the interaction is uninformative and the probe stops
before paying for the energy arms.

Run: uv run python scripts/probes/t92_dynamics_credit_cora.py
     uv run python scripts/probes/t92_dynamics_credit_cora.py --report-only
Walltime printed, never recorded.
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import time
from dataclasses import replace
from pathlib import Path

from computronium.core.utils.git import git_sha
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import cell_record
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)
from computronium.validation.preregistration import (
    ThresholdRegistration,
    paired_comparison,
)

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "experiments/t92_dynamics_credit_cora.duckdb"
REGISTRATION = ROOT / "configs/preregistrations/t92_dynamics_credit_cora.json"
ANCHOR_STORE = ROOT / "experiments/t88_g6_cora_claim_l1.duckdb"
ANCHOR = "6328d4d4"
SEEDS = (47, 48, 49, 50, 51)
MAJORITY = 0.316
ARMS = (
    ("instantaneous", "gradient"),
    ("instantaneous", "random_projections"),
    ("energy_minimization", "gradient"),
    ("energy_minimization", "random_projections"),
)
CHEAP_ARMS = ARMS[:2]
ENERGY_ARMS = ARMS[2:]


def _locate() -> tuple[Coordinate, Schedule]:
    with RecordStore(StoreConfig(path=ANCHOR_STORE, read_only=True)) as store:
        for record in store.query_records():
            if record.measurement_key.startswith(ANCHOR):
                return Coordinate.from_record(record), record.schedule
    msg = f"no record {ANCHOR} in {ANCHOR_STORE}"
    raise LookupError(msg)


def _provenance(run_id: str) -> Provenance:
    env = {
        key: value
        for key, value in os.environ.items()
        if key.startswith(("CUDA", "TORCH", "OMP", "OPENBLAS"))
    }
    env.setdefault("python", platform.python_version())
    return Provenance(
        env=env,
        dataset="cora",
        dataset_version="probe",
        code_sha=git_sha() or "local",
        policy="t92_dynamics_credit_cora",
        links={"run_id": run_id},
    )


def _schedule(anchor: Schedule) -> Schedule:
    return replace(
        anchor,
        fidelity="L2",
        budget_id="L2_initial",
        epochs=100,
        n_seeds=len(SEEDS),
        seed=SEEDS[0],
    )


def _values(store: RecordStore, run_id: str) -> dict[tuple[str, str], dict[int, float]]:
    values: dict[tuple[str, str], dict[int, float]] = {arm: {} for arm in ARMS}
    for record in store.query_records(run_id=run_id):
        arm = (record.dynamics, record.credit)
        if arm not in values or record.schedule.seed not in SEEDS:
            continue
        if record.status.gate_verdict.value != "PASS":
            print(
                f"{arm[0]} + {arm[1]} seed={record.schedule.seed}: "
                f"gate={record.status.gate_verdict.value} defect={record.status.defect}"
            )
            continue
        values[arm][record.schedule.seed] = float(record.payload["val_acc"])
    return values


def _cell_cost(store: RecordStore, run_id: str) -> dict[tuple[str, str], float]:
    cost: dict[tuple[str, str], float] = {}
    for record in store.query_records(run_id=run_id):
        arm = (record.dynamics, record.credit)
        if arm in ARMS:
            cost[arm] = cost.get(arm, 0.0) + float(
                record.payload.get("walltime_s", 0.0)
            )
    return cost


def _report(
    values: dict[tuple[str, str], dict[int, float]],
    cost: dict[tuple[str, str], float],
) -> int:
    registration = ThresholdRegistration.load(REGISTRATION)
    for arm in ARMS:
        measured = [values[arm][seed] for seed in SEEDS if seed in values[arm]]
        if not measured:
            print(f"{arm[0]:21} + {arm[1]:20}: no PASS seed")
            continue
        print(
            f"{arm[0]:21} + {arm[1]:20}: n={len(measured)} "
            f"mean={statistics.mean(measured):.4f} "
            f"sd={statistics.stdev(measured) if len(measured) > 1 else 0.0:.4f} "
            f"cost={cost.get(arm, 0.0):.0f}s"
        )
    if not all(len(values[arm]) == len(SEEDS) for arm in ARMS):
        print(
            "incomplete: "
            + ", ".join(f"{a[0]}+{a[1]} {len(values[a])}/{len(SEEDS)}" for a in ARMS)
        )
        return 2
    interaction = [
        (
            values["energy_minimization", "random_projections"][seed]
            - values["energy_minimization", "gradient"][seed]
        )
        - (
            values["instantaneous", "random_projections"][seed]
            - values["instantaneous", "gradient"][seed]
        )
        for seed in SEEDS
    ]
    result = paired_comparison(interaction, [0.0] * len(interaction), seed=0)
    print(
        f"interaction (RP - gradient): energy - instantaneous = "
        f"{result.mean_diff:+.4f} 95% CI [{result.ci_lower:+.4f}, "
        f"{result.ci_upper:+.4f}] p={result.p_value:.4f}"
    )
    verdict = (
        "INTERACTION"
        if result.passes(registration)
        else ("NULL" if result.ci_lower <= 0.0 <= result.ci_upper else "NEGATIVE")
    )
    print(
        f"verdict: {verdict} (threshold={registration.threshold:+.4f}, "
        f"alpha={registration.alpha})"
    )
    return 0 if verdict == "INTERACTION" else 1


def _record_arms(
    store: RecordStore,
    run_id: str,
    coordinates: dict[tuple[str, str], Coordinate],
    schedule: Schedule,
    arms: tuple[tuple[str, str], ...],
) -> None:
    provenance = _provenance(run_id)
    for dynamics, credit in arms:
        for seed in SEEDS:
            started = time.perf_counter()
            record = cell_record(
                coordinates[dynamics, credit],
                replace(schedule, seed=seed),
                provenance,
            )
            store.append(record)
            print(
                f"{dynamics:21} + {credit:20} seed={seed}: "
                f"val_acc={record.payload.get('val_acc')} "
                f"gate={record.status.gate_verdict.value} "
                f"({time.perf_counter() - started:.1f}s)",
                flush=True,
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Read recorded seeds and decide without training",
    )
    args = parser.parse_args(argv)

    anchor_coordinate, anchor_schedule = _locate()
    schedule = _schedule(anchor_schedule)
    coordinates = {
        arm: replace(anchor_coordinate, dynamics=arm[0], credit=arm[1]) for arm in ARMS
    }

    with RecordStore(StoreConfig(path=STORE)) as store:
        runs = store.query_runs(limit=1)
        run_id = runs[0].run_id if runs else store.create_run()
        print(f"run {run_id[:8]} store {STORE.relative_to(ROOT)}")
        if not args.report_only:
            _record_arms(store, run_id, coordinates, schedule, CHEAP_ARMS)
            values = _values(store, run_id)
            measured = [
                values["instantaneous", "random_projections"][seed]
                for seed in SEEDS
                if seed in values["instantaneous", "random_projections"]
            ]
            if len(measured) == len(SEEDS) and statistics.mean(measured) < MAJORITY:
                print(
                    "uninformative: random_projections instantaneous mean "
                    f"{statistics.mean(measured):.4f} < majority {MAJORITY}; "
                    "energy arms not run"
                )
            else:
                _record_arms(store, run_id, coordinates, schedule, ENERGY_ARMS)
        values = _values(store, run_id)
        cost = _cell_cost(store, run_id)
        if not args.report_only:
            store.finish_run(
                run_id,
                "completed"
                if all(len(values[arm]) == len(SEEDS) for arm in ARMS)
                else "incomplete",
                sum(cost.values()),
            )

    return _report(values, cost)


if __name__ == "__main__":
    raise SystemExit(main())
