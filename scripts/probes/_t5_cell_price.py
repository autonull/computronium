"""Probe: price one campaign cell. TODO47 T5 cost discipline: measure, do not guess.

One cell = one (coordinate, schedule) evaluated through the executor the
pipeline's backend calls (``cell_record``). Measures per-cell seconds for the
primary task (digits) and the transfer task (mnist) across two batch limits, so
the campaign's cell count is derived from a number rather than a hope.
"""

from __future__ import annotations

import time

from computronium.experiment.execution.evaluate import cell_record
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule
from computronium.experiment.schema.run_spec import MEASURED_PARAM_BUDGET
from computronium.experiment.schema.seed_registries import seed_all_registries

seed_all_registries()

CREDITS = ("thermodynamic_contrast", "local_contrastive", "gradient")


def coordinate(credit: str) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="energy_minimization",
        plasticity="fast_weights",
        credit=credit,
        update="euclidean",
        params={},
    )


def provenance() -> Provenance:
    return Provenance(
        env={},
        dataset="probe",
        dataset_version="1.0",
        code_sha="probe",
        policy="probe",
        links={},
    )


for task in ("digits", "mnist"):
    for batches in (2, 8):
        timings = []
        for index, credit in enumerate(CREDITS):
            start = time.perf_counter()
            cell_record(
                coordinate(credit),
                Schedule(
                    fidelity="L0",
                    seed=index,
                    n_seeds=1,
                    epochs=1,
                    batch_limit=batches,
                    budget_id="probe",
                    task_id=task,
                    param_budget=MEASURED_PARAM_BUDGET,
                ),
                provenance(),
            )
            timings.append(time.perf_counter() - start)
        per_cell = sum(timings) / len(timings)
        print(
            f"{task:7s} batch_limit={batches:<3d} per_cell={per_cell:6.2f}s "
            f"(min {min(timings):.2f} max {max(timings):.2f})"
        )
