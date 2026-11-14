"""Regression-lane attribution probe (TODO91 §8, measured 2026-11-14).

The breadth baseline's store keeps a failure *message*, not a traceback, and
the same message ("one_hot ... LongTensor") can come from a credit or from a
plasticity. This probe re-executes each of the recorded FAIL cells and prints
the innermost ``computronium`` frame that raised, so the fix is aimed at the
law that actually assumed class labels.

Regime: L0, 3 epochs, batch_limit=1, seed 42, CPU — the recorded schedule.
Recorded cells came from ``experiments/experiment_20261114_080534.duckdb``.
"""

from __future__ import annotations

import traceback

from computronium.experiment.kernel.evaluate import EvaluationError, evaluate_cell
from computronium.experiment.schema import seed_all_registries
from computronium.experiment.schema.coordinate import Coordinate, Provenance, Schedule

# (task, substrate, geometry, dynamics, plasticity, credit, update)
FAILING_CELLS: tuple[tuple[str, str, str, str, str, str, str], ...] = (
    (
        "lorenz_state",
        "digital",
        "feedforward",
        "energy_minimization",
        "fast_weights",
        "pepita",
        "adam",
    ),
    (
        "lorenz_state",
        "ternary",
        "feedforward",
        "instantaneous",
        "substrate_coupled",
        "local_contrastive",
        "muon",
    ),
    (
        "lorenz_state",
        "optical",
        "attention",
        "instantaneous",
        "substrate_coupled",
        "target_inversion",
        "spectral_constrained",
    ),
    (
        "diabetes",
        "ternary",
        "feedforward",
        "spike_integration",
        "null",
        "target_inversion",
        "adam",
    ),
    (
        "diabetes",
        "optical",
        "feedforward",
        "lazy",
        "conflict_adaptive",
        "random_projections",
        "lion",
    ),
    (
        "lorenz_state",
        "analog",
        "feedforward",
        "energy_minimization",
        "routing",
        "local_contrastive",
        "riemannian_orthogonal",
    ),
    (
        "diabetes",
        "neuromorphic",
        "feedforward",
        "energy_minimization",
        "conflict_adaptive",
        "thermodynamic_contrast",
        "elastic_consolidation",
    ),
    (
        "lorenz_state",
        "sparse",
        "recurrent",
        "pc_alm",
        "conflict_adaptive",
        "thermodynamic_contrast",
        "spectral_constrained",
    ),
)


def _innermost_cause(exc: BaseException) -> str:
    seen: list[str] = []
    current: BaseException | None = exc
    while current is not None:
        for frame in traceback.extract_tb(current.__traceback__):
            if "computronium/" in frame.filename:
                seen.append(
                    f"{frame.filename.split('computronium/', 1)[1]}:{frame.lineno}"
                )
        current = current.__cause__ or current.__context__
    return " <- ".join(reversed(seen[-3:]))


def main() -> None:
    seed_all_registries()
    from computronium.experiment.surface.combinations import declared_space

    refused = {
        task_id: dict(declared_space(task_id).refused)
        for task_id in {cell[0] for cell in FAILING_CELLS}
    }
    for (
        task,
        substrate,
        geometry,
        dynamics,
        plasticity,
        credit,
        update,
    ) in FAILING_CELLS:
        keys = (
            f"substrate={substrate}",
            f"geometry={geometry}",
            f"dynamics={dynamics}",
            f"plasticity={plasticity}",
            f"credit={credit}",
            f"update={update}",
        )
        blocked = next((refused[task][k] for k in keys if k in refused[task]), None)
        if blocked is not None:
            print(f"{task:13s} {credit:22s} {plasticity:17s} REFUSED {blocked}")
            continue
        schedule = Schedule(
            fidelity="L0",
            seed=42,
            n_seeds=1,
            epochs=3,
            batch_limit=1,
            budget_id="todo91-regression-attribution",
            task_id=task,
            param_budget=10_000_000,
            device="cpu",
            num_workers=0,
        )
        provenance = Provenance(
            env={},
            dataset=task,
            dataset_version="attribution",
            code_sha="",
            policy="regression-lane attribution",
            links={},
        )
        coordinate = Coordinate(
            substrate=substrate,
            geometry=geometry,
            dynamics=dynamics,
            plasticity=plasticity,
            credit=credit,
            update=update,
            params={},
        )
        try:
            evaluate_cell(coordinate, schedule)
        except EvaluationError as exc:
            print(
                f"{task:13s} {credit:22s} {plasticity:17s} RAISED {_innermost_cause(exc)}"
            )
            continue
        print(f"{task:13s} {credit:22s} {plasticity:17s} PASS")


if __name__ == "__main__":
    main()
