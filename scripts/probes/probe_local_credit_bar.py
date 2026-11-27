"""W39: which credit clears a cheap task's bar at L0 on the loop's own arms.

The from-scratch acceptance test expects a local credit at L1/L2 (eligible =
PASS at the spec's seed count). It has only ever seen `gradient` promote, so
this measures every local credit the test accepts beside the backprop ruler:
1 epoch, two seeds, the loop's feedforward/digital/instantaneous geometry.

Informs TODO107 W39.
"""

from __future__ import annotations

from computronium.experiment.schema.seed_registries import seed_all_registries

seed_all_registries()

from computronium.experiment.kernel.evaluate import (  # ruff: ignore[module-import-not-at-top-of-file]
    cell_record,
    clears_task_bar,
    task_pass_bar,
)
from computronium.experiment.schema.coordinate import (  # ruff: ignore[module-import-not-at-top-of-file]
    Coordinate,
    Provenance,
    Schedule,
)

TASKS = ("xor", "iris", "spiral")
CREDITS = (
    "gradient",
    "thermodynamic_contrast",
    "random_projections",
    "pepita",
    "local_goodness",
)


def measure(task_id: str, credit: str, seed: int) -> str:
    coordinate = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="null",
        credit=credit,
        update="euclidean",
        params={},
    )
    schedule = Schedule(
        fidelity="L0",
        seed=seed,
        n_seeds=1,
        epochs=1,
        batch_limit=1,
        budget_id="w39-probe",
        task_id=task_id,
        param_budget=50_000,
        device="cpu",
        num_workers=0,
    )
    provenance = Provenance(
        env={},
        dataset=task_id,
        dataset_version="probe",
        code_sha="",
        policy="w39 probe",
        links={},
    )
    record = cell_record(coordinate, schedule, provenance)
    bar = task_pass_bar(task_id)
    accuracy = record.payload.get("val_acc")
    verdict = record.status.gate_verdict.value
    if bar is None or accuracy is None:
        return f"{verdict:6s} val_acc={accuracy} bar={bar}"
    cleared = clears_task_bar(bar, {"val_acc": accuracy})
    return f"{verdict:6s} val_acc={accuracy:.4f} bar={bar.value:.4f} cleared={cleared}"


def main() -> None:
    for task_id in TASKS:
        print(f"\n### {task_id}")
        for credit in CREDITS:
            for seed in (0, 1):
                try:
                    outcome = measure(task_id, credit, seed)
                except Exception as exc:  # the exception text is the measurement
                    outcome = f"RAISE  {type(exc).__name__}: {exc}"
                print(f"{credit:22s} seed={seed} {outcome}")


if __name__ == "__main__":
    main()
