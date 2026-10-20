"""The store a dashboard test reads: one run, five seeds, one cell.

The dashboard's tests all need the same thing — a store that holds a run, its
declaration and a few measurements — and each of them building its own would
be a second version of the demo's contract. This is that one version.
"""

from __future__ import annotations

from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Maturity,
    Record,
    ReproducibilityClass,
    Severity,
    Status,
)
from computronium.experiment.schema.run_spec import AxisSelection, RunSpec

# The demo's cell: four credit arms, everything else fixed.
COORDINATE = {
    "substrate": "digital",
    "geometry": "feedforward",
    "dynamics": "instantaneous",
    "plasticity": "null",
    "credit": "gradient",
    "update": "adam",
}

# A cell the system refuses: predictive settling needs a contrastive credit.
VOID_COORDINATE = {**COORDINATE, "dynamics": "predictive_settling"}


def demo_spec() -> RunSpec:
    """The demo's declaration: four credit arms, everything else fixed."""
    return RunSpec(
        profile="demo",
        task="digits",
        objectives=("validation_accuracy",),
        fidelity="L1",
        n_seeds=5,
        epochs=1,
        budget_seconds=120.0,
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=("instantaneous",)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=(
                    "gradient",
                    "random_projections",
                    "pepita",
                    "local_goodness",
                ),
            ),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("adam",)),
        ),
    )


def demo_record(run_id: str, val_acc: float, seed: int) -> Record:
    """One measurement of the demo's cell."""
    return Record.create(
        run_id=run_id,
        coordinate=Coordinate(**COORDINATE, params={}),
        schedule=Schedule(
            fidelity="L1",
            seed=seed,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="dashboard-space-test",
            task_id="digits",
            param_budget=0,
        ),
        provenance=Provenance(
            env={"python": "3.14", "platform": "linux"},
            dataset="digits",
            dataset_version="1.0",
            code_sha="dashboard-space-test",
            policy="dashboard-space-test",
            links={"run_id": run_id},
        ),
        status=Status(
            gate_verdict=GateVerdict.PASS_,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L1,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload={"val_acc": val_acc, "walltime_s": 3.0, "param_count": 1024},
    )
