"""S6 geometry x task truth table: which task shapes each geometry can train.

TODO91 S6 found cells the declared constraints admit but training refuses
(graph on a tabular task: "requires edge_index"; conv on a 4-feature input:
shape mismatch; causal_transformer on a classifier: LM target shift makes
labels negative). Each of those is a task-shape rule the declared table does
not state. This probe measures the truth per geometry so the rule is written
from evidence.

One tuple per geometry (the axis pair that composes), 1 epoch per task, the
task's own loader. A cell that neither composes nor trains prints its cause.
"""

from __future__ import annotations

from computronium.experiment.schema.seed_registries import seed_all_registries

seed_all_registries()

from computronium.experiment.kernel.evaluate import cell_record  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.schema.coordinate import (  # ruff: ignore[module-import-not-at-top-of-file]
    Coordinate,
    Provenance,
    Schedule,
)

TASKS = ("iris", "mnist", "char_ngram", "cora", "pendulum_state")
# Candidates per geometry: (dynamics, credit, update). The first that composes
# is trained; if none composes the last cause is printed.
CANDIDATES = (
    ("instantaneous", "gradient", "adam"),
    ("instantaneous", "local_goodness", "adam"),
    ("energy_minimization", "gradient", "euclidean"),
)

GEOMETRIES = list(AXES_REGISTRIES[StructuralAxis.GEOMETRY].keys())


def smoke(task_id: str, geometry: str, candidate: tuple[str, str, str]) -> str:
    dynamics, credit, update = candidate
    coordinate = Coordinate(
        substrate="digital",
        geometry=geometry,
        dynamics=dynamics,
        plasticity="null",
        credit=credit,
        update=update,
        params={},
    )
    schedule = Schedule(
        fidelity="L0",
        seed=0,
        n_seeds=1,
        epochs=1,
        batch_limit=1,
        budget_id="s6-probe",
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
        policy="s6 probe",
        links={},
    )
    try:
        record = cell_record(coordinate, schedule, provenance)
    except Exception as exc:  # the exception text is the measurement
        return f"FAIL {type(exc).__name__}: {exc}"
    if record.status.gate_verdict.value == "PASS":
        return "PASS"
    return f"FAIL {record.status.cause}: {record.status.defect}"


def main() -> None:
    for geometry in GEOMETRIES:
        print(f"\n### {geometry}")
        for task_id in TASKS:
            outcome = ""
            for candidate in CANDIDATES:
                outcome = smoke(task_id, geometry, candidate)
                if (
                    outcome == "PASS"
                    or "not found" in outcome
                    or "unavailable" in outcome
                ):
                    break
            print(f"  {task_id:16} {outcome[:150]}")


if __name__ == "__main__":
    main()
