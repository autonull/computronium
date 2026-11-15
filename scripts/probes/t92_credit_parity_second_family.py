"""TODO92 §0 standing stop-loss: second-family parity for `local_goodness`.

The breadth exit is green. The stop-loss then asks whether any non-standard
composition matches the standard stack at matched cost on >=2 task families
with a declared domain bar. `local_goodness` is the only non-standard credit
with claim-grade parity, and it holds vision only (§3.11 follow-up). This
probe adds the tabular family: `wine` is at ceiling for both arms and cannot
discriminate, so the cell is `breast_cancer` (declared bar 0.6316, 114 held
out, resolution 0.88 pp).

Control = `gradient`; treatment = `local_goodness` with its declared target
channel (`credit.readout_error=True`). Both arms share the breadth probe's
reference stack (digital / feedforward / instantaneous / null / adam,
`geometry.hidden_dim=256`), L2/20, seeds 57-61, CPU; only the credit, its
channel and the seed differ. The decision is the pre-registered ±0.01 margin
in ``configs/preregistrations/t92_local_goodness_breast_cancer.json``.

Walltime printed, never recorded as a claim.

Measured 2026-11-15 (L2/20, seeds 57-61, CPU, 10 cells, 15 s): gradient
**0.9509 ± 0.0048** vs `local_goodness` **0.9667 ± 0.0073**; paired
**+0.0158**, 95% CI [+0.0105, +0.0211], p=0.0076, dz=2.15 — the ±0.01
equivalence margin is rejected, so the credit that holds vision parity holds a
tabular advantage at ~1.15× total cell cost. Coordinate, not a claim (the file
pre-registers equivalence only).

Run: uv run python scripts/probes/t92_credit_parity_second_family.py --pilot
     uv run python scripts/probes/t92_credit_parity_second_family.py
     uv run python scripts/probes/t92_credit_parity_second_family.py --report-only
"""

from __future__ import annotations

import argparse
import os
import platform
import statistics
import time
from pathlib import Path

from computronium.core.utils.git import git_sha
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.kernel.evaluate import cell_record, evaluate_cell
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.validation.preregistration import (
    EquivalenceRegistration,
    paired_comparison,
)

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "experiments/t92_credit_parity_breast_cancer.duckdb"
REGISTRATION = ROOT / "configs/preregistrations/t92_local_goodness_breast_cancer.json"
TASK = "breast_cancer"
SEEDS = (57, 58, 59, 60, 61)
CONTROL = "gradient"
TREATMENT = "local_goodness"
CHANNEL: dict[str, object] = {"credit.readout_error": True}
PARAMS: dict[str, object] = {"geometry.hidden_dim": 256}


def _coordinate(credit: str) -> Coordinate:
    params = PARAMS | (CHANNEL if credit == TREATMENT else {})
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit=credit,
        update="adam",
        params=params,
    )


def _schedule(seed: int, epochs: int, device: str) -> Schedule:
    return Schedule(
        fidelity="L2",
        seed=seed,
        n_seeds=len(SEEDS),
        epochs=epochs,
        batch_limit=0,
        budget_id="L2_initial",
        task_id=TASK,
        device=device,
    )


def _provenance(run_id: str) -> Provenance:
    env = {
        key: value
        for key, value in os.environ.items()
        if key.startswith(("CUDA", "TORCH", "OMP", "OPENBLAS"))
    }
    env.setdefault("python", platform.python_version())
    return Provenance(
        env=env,
        dataset=TASK,
        dataset_version="probe",
        code_sha=git_sha() or "local",
        policy="t92_credit_parity_second_family",
        links={"run_id": run_id},
    )


def _pilot(device: str) -> int:
    for credit in (CONTROL, TREATMENT):
        started = time.perf_counter()
        result = evaluate_cell(_coordinate(credit), _schedule(57, 1, device))
        print(
            f"pilot {credit:16} seed=57 val_acc={result.metrics['val_acc']:.4f} "
            f"({time.perf_counter() - started:.1f}s)",
            flush=True,
        )
    return 0


def _values(store: RecordStore, run_id: str) -> dict[str, dict[int, float]]:
    values: dict[str, dict[int, float]] = {CONTROL: {}, TREATMENT: {}}
    for record in store.query_records(run_id=run_id):
        if record.credit not in values or record.schedule.seed not in SEEDS:
            continue
        if record.status.gate_verdict.value != "PASS":
            print(
                f"{record.credit} seed={record.schedule.seed}: "
                f"gate={record.status.gate_verdict.value} defect={record.status.defect}"
            )
            continue
        values[record.credit][record.schedule.seed] = float(record.payload["val_acc"])
    return values


def _report(values: dict[str, dict[int, float]]) -> int:
    registration = EquivalenceRegistration.load(REGISTRATION)
    for arm, measured in values.items():
        seeds = [measured[seed] for seed in SEEDS if seed in measured]
        print(
            f"{arm:16}: n={len(seeds)} "
            f"mean={statistics.mean(seeds) if seeds else float('nan'):.4f} "
            f"sd={statistics.stdev(seeds) if len(seeds) > 1 else 0.0:.4f}"
        )
    if any(len(measured) < len(SEEDS) for measured in values.values()):
        print("incomplete")
        return 2
    result = paired_comparison(
        [values[TREATMENT][seed] for seed in SEEDS],
        [values[CONTROL][seed] for seed in SEEDS],
        seed=0,
    )
    equivalent = result.passes_equivalence(registration)
    print(
        f"paired {TREATMENT} - {CONTROL}: {result.mean_diff:+.4f} "
        f"95% CI [{result.ci_lower:+.4f}, {result.ci_upper:+.4f}] "
        f"p={result.p_value:.4f} dz={result.cohens_dz:.2f}"
    )
    print(
        f"verdict: {'EQUIVALENT' if equivalent else 'NOT-EQUIVALENT'} "
        f"(margin=±{registration.margin:.4f})"
    )
    return 0 if equivalent else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)

    if args.pilot:
        return _pilot(args.device)

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
            cost = 0.0
            for credit in (CONTROL, TREATMENT):
                for seed in SEEDS:
                    if (credit, seed) in done:
                        print(f"{credit:16} seed={seed}: recorded")
                        continue
                    started = time.perf_counter()
                    record = cell_record(
                        _coordinate(credit),
                        _schedule(seed, 20, args.device),
                        provenance,
                    )
                    store.append(record)
                    cost += time.perf_counter() - started
                    print(
                        f"{credit:16} seed={seed}: "
                        f"val_acc={record.payload.get('val_acc')} "
                        f"gate={record.status.gate_verdict.value} "
                        f"({time.perf_counter() - started:.1f}s)",
                        flush=True,
                    )
            store.finish_run(run_id, "completed", cost)
        values = _values(store, run_id)
    return _report(values)


if __name__ == "__main__":
    raise SystemExit(main())
