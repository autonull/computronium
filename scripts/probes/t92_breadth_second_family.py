"""TODO92 §0: the missing second task family for the breadth exit.

The breadth gate (§0, ``uv run comp gate breadth``) needs every error-aware
credit to hold a legal, bar-cleared L2/n>=5 cell on >=2 registered task
domains. Six credits hold one family (vision, except ``random_projections`` on
graph) and two hold none. This probe measures only what the gate is missing:

- ``local_goodness``, ``target_inversion``, ``thermodynamic_contrast``: one
  tabular cell (``wine``) to pair with their vision cells;
- ``random_projections``: one tabular cell (``wine``) to pair with Cora;
- ``local_contrastive``, ``pc_alm``: one vision cell (``digits``) and one
  tabular cell (``wine``), because they hold no family at all.

Each cell is the reference stack (digital / feedforward / null plasticity /
adam, ``geometry.hidden_dim=256``) with only the credit axis changed, plus the
credit's required dynamics (``thermodynamic_contrast`` ->
``energy_minimization``, ``pc_alm`` -> ``pc_alm``) and its declared target
channel (``local_goodness`` -> ``credit.readout_error=True``). Schedule: L2,
20 epochs, seeds 57-61. The task's own ``pass_bar`` decides bar clearance, so a
cell below the majority rate does not count.

This is a breadth measurement, not a claim: it answers "is the credit legal and
above bar on a second domain", not "is the credit better than gradient". The
gradient reference cells on the same two tasks are measured alongside, so every
credit cell has its ruler in the same store.

Walltime printed, never recorded as a claim.

Measured 2026-11-15 (L2/20, seeds 57-61, CPU, 50 cells, 582 s):
`wine` (tabular, 36 held out, majority 0.3889) - gradient 1.0000,
`local_goodness` 1.0000, `random_projections` 0.9944 ± 0.0124,
`target_inversion` 0.9389 ± 0.0362, `thermodynamic_contrast` 1.0000,
`local_contrastive` 0.9722, `pc_alm` 1.0000; `digits` (vision, 359 held out,
bar 0.10) - gradient 0.9750 ± 0.0052, `local_contrastive` 0.8256 ± 0.0162,
`pc_alm` 0.2917 ± 0.0715. Gate result: `comp gate breadth` exits 0, 8/8.

Run: uv run python scripts/probes/t92_breadth_second_family.py --pilot
     uv run python scripts/probes/t92_breadth_second_family.py
     uv run python scripts/probes/t92_breadth_second_family.py --report-only
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

__all__ = ["main"]

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / "experiments/t92_breadth_second_family.duckdb"
SEEDS = (57, 58, 59, 60, 61)

REFERENCE_STACK = {
    "substrate": "digital",
    "geometry": "feedforward",
    "plasticity": "null",
    "update": "adam",
}
BASE_PARAMS: dict[str, object] = {"geometry.hidden_dim": 256}

# credit -> (dynamics, required params)
CREDITS: dict[str, tuple[str, dict[str, object]]] = {
    "gradient": ("instantaneous", {}),
    "local_goodness": ("instantaneous", {"credit.readout_error": True}),
    "random_projections": ("instantaneous", {}),
    "target_inversion": ("instantaneous", {}),
    "thermodynamic_contrast": ("energy_minimization", {}),
    "local_contrastive": ("instantaneous", {}),
    "pc_alm": ("pc_alm", {}),
}

# (task, credits) — only the cells each credit still needs
TASKS: dict[str, tuple[str, ...]] = {
    "wine": (
        "gradient",
        "local_goodness",
        "random_projections",
        "target_inversion",
        "thermodynamic_contrast",
        "local_contrastive",
        "pc_alm",
    ),
    "digits": ("gradient", "local_contrastive", "pc_alm"),
}


def _coordinate(task: str, credit: str) -> Coordinate:
    dynamics, params = CREDITS[credit]
    return Coordinate(
        **REFERENCE_STACK,
        dynamics=dynamics,
        credit=credit,
        params=BASE_PARAMS | params,
    )


def _schedule(task: str, seed: int, epochs: int, device: str) -> Schedule:
    return Schedule(
        fidelity="L2",
        seed=seed,
        n_seeds=len(SEEDS),
        epochs=epochs,
        batch_limit=0,
        budget_id="L2_initial",
        task_id=task,
        device=device,
    )


def _provenance(run_id: str, task: str) -> Provenance:
    env = {
        key: value
        for key, value in os.environ.items()
        if key.startswith(("CUDA", "TORCH", "OMP", "OPENBLAS"))
    }
    env.setdefault("python", platform.python_version())
    return Provenance(
        env=env,
        dataset=task,
        dataset_version="probe",
        code_sha=git_sha() or "local",
        policy="t92_breadth_second_family",
        links={"run_id": run_id},
    )


def _pilot(device: str) -> int:
    for task, credits in TASKS.items():
        for credit in credits:
            started = time.perf_counter()
            try:
                result = evaluate_cell(
                    _coordinate(task, credit), _schedule(task, 57, 1, device)
                )
            except Exception as exc:  # ruff: ignore[blind-except] - a refusal is a row
                print(f"{task:8} {credit:23} refused: {type(exc).__name__}: {exc}")
                continue
            print(
                f"{task:8} {credit:23} seed=57 val_acc={result.metrics['val_acc']:.4f} "
                f"({time.perf_counter() - started:.1f}s)",
                flush=True,
            )
    return 0


def _values(store: RecordStore, run_id: str) -> dict[tuple[str, str], dict[int, float]]:
    values: dict[tuple[str, str], dict[int, float]] = {}
    for record in store.query_records(run_id=run_id):
        key = (record.schedule.task_id, record.credit)
        if key[1] not in CREDITS or record.schedule.seed not in SEEDS:
            continue
        if record.status.gate_verdict.value != "PASS":
            print(
                f"{key[0]:8} {key[1]:23} seed={record.schedule.seed}: "
                f"gate={record.status.gate_verdict.value} defect={record.status.defect}"
            )
            continue
        values.setdefault(key, {})[record.schedule.seed] = float(
            record.payload["val_acc"]
        )
    return values


def _report(values: dict[tuple[str, str], dict[int, float]]) -> int:
    print(f"\n{'task':8} {'credit':23} {'n':>2} {'mean':>7} {'sd':>7} verdict")
    missing = 0
    for task, credits in TASKS.items():
        for credit in credits:
            measured = values.get((task, credit), {})
            seeds = [measured[seed] for seed in SEEDS if seed in measured]
            if len(seeds) < len(SEEDS):
                missing += 1
            mean = statistics.mean(seeds) if seeds else 0.0
            sd = statistics.stdev(seeds) if len(seeds) > 1 else 0.0
            verdict = "complete" if len(seeds) == len(SEEDS) else "incomplete"
            print(
                f"{task:8} {credit:23} {len(seeds):2} {mean:7.4f} {sd:7.4f} {verdict}"
            )
    return 0 if missing == 0 else 2


def _run_credit(
    store: RecordStore,
    task: str,
    credit: str,
    provenance: Provenance,
    done: set[tuple[str, str, int]],
    device: str,
) -> float:
    cost = 0.0
    for seed in SEEDS:
        if (task, credit, seed) in done:
            print(f"{task:8} {credit:23} seed={seed}: recorded")
            continue
        started = time.perf_counter()
        record = cell_record(
            _coordinate(task, credit),
            _schedule(task, seed, 20, device),
            provenance,
        )
        store.append(record)
        cost += time.perf_counter() - started
        print(
            f"{task:8} {credit:23} seed={seed}: "
            f"val_acc={record.payload.get('val_acc')} "
            f"gate={record.status.gate_verdict.value} "
            f"({time.perf_counter() - started:.1f}s)",
            flush=True,
        )
    return cost


def _run_cells(store: RecordStore, run_id: str, device: str) -> float:
    done = {
        (record.schedule.task_id, record.credit, record.schedule.seed)
        for record in store.query_records(run_id=run_id)
    }
    cost = 0.0
    for task, credits in TASKS.items():
        provenance = _provenance(run_id, task)
        for credit in credits:
            cost += _run_credit(store, task, credit, provenance, done, device)
    return cost


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
            store.finish_run(
                run_id, "completed", _run_cells(store, run_id, args.device)
            )
        values = _values(store, run_id)
    return _report(values)


if __name__ == "__main__":
    raise SystemExit(main())
