"""Reproduce the update-lr ladder that retired the step-size multiplier column.

The column (``step_size_override_<dynamics>_<credit>``, 29 rows) multiplied the
parameter-update step *after* config construction and was deleted in TODO66 §15;
the measurement that retired it is ``docs/CORRECTIONS.md`` Correction 3. Every
original row attenuated, one as far as ``5e-5`` — a composed lr of 5e-7 against
a rule that measurably learns at 1e-3.

This probe keeps the control, not the audit: one rule at a ladder of update lrs,
with the composed lr now written directly into ``update_lr``. On `digits` at gate
2b's reference regime, 10 epochs, ``energy_minimization x
thermodynamic_contrast``:

========================  ==========  ==========  ==========  ==========
update lr                 5e-7        1e-4        1e-3        5e-3
========================  ==========  ==========  ==========  ==========
``train_acc``             0.105       0.080       0.411       0.878
========================  ==========  ==========  ==========  ==========

Usage::

    uv run python scripts/probes/step_size_multipliers.py --ladder energy_minimization_thermodynamic_contrast
"""

from __future__ import annotations

import time

from computronium.experiment.execution.evaluate import cell_record

from computronium.experiment.schema.coordinate import (
    Coordinate,
    Provenance,
    Schedule,
)
from computronium.experiment.schema.record import Record
from computronium.experiment.schema.run_spec import MEASURED_PARAM_BUDGET
from computronium.experiment.schema.seed_registries import seed_all_registries

CHANCE = 0.1
BEATS_CHANCE_FACTOR = 1.5
SETTLE_STEP = 0.03162
LADDER = (5e-7, 1e-4, 1e-3, 5e-3, 1.6e-2, 5e-2)

PROVENANCE = Provenance(
    env={},
    dataset="digits",
    dataset_version="1.0",
    code_sha="q1b_multiplier_audit",
    policy="q1b_multiplier_audit",
    links={},
)


def _decompose(suffix: str) -> tuple[str, str]:
    """Split ``<dynamics>_<credit>`` using the axis registries as the grammar.

    Both axis names contain underscores (``energy_minimization``), so the
    separator is not the first underscore — only the registries know where the
    dynamics name ends.
    """
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    credits = {spec.name for spec in AXES_REGISTRIES[StructuralAxis.CREDIT]}
    for spec in AXES_REGISTRIES[StructuralAxis.DYNAMICS]:
        tail = suffix[len(spec.name) + 1 :]
        if suffix.startswith(f"{spec.name}_") and tail in credits:
            return spec.name, tail
    raise SystemExit(f"not a dynamics x credit pair: {suffix}")


def _coordinate(dynamics: str, credit: str, params: dict[str, object]) -> Coordinate:
    return Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics=dynamics,
        plasticity="fast_weights",
        credit=credit,
        update="euclidean",
        params=params,
    )


def _cell(dynamics: str, credit: str, update_lr: float) -> Record:
    """One reference-regime cell at the given composed update lr."""
    from computronium.experiment.schema.harvest import InactiveHyperparameterError

    base: dict[str, object] = {
        "depth": 2,
        "hidden_dim": 64,
        "settle_step": SETTLE_STEP,
        "update_lr": update_lr,
    }
    try:
        return cell_record(
            _coordinate(dynamics, credit, base),
            Schedule(
                fidelity="L0",
                seed=0,
                n_seeds=1,
                epochs=10,
                batch_limit=0,
                budget_id="q1b",
                task_id="digits",
                param_budget=MEASURED_PARAM_BUDGET,
            ),
            provenance=PROVENANCE,
        )
    except InactiveHyperparameterError:
        base.pop("settle_step")
        return cell_record(
            _coordinate(dynamics, credit, base),
            Schedule(
                fidelity="L0",
                seed=0,
                n_seeds=1,
                epochs=10,
                batch_limit=0,
                budget_id="q1b",
                task_id="digits",
                param_budget=MEASURED_PARAM_BUDGET,
            ),
            provenance=PROVENANCE,
        )


def _ladder(row: str) -> None:
    """The control: one rule at a ladder of update lrs."""
    seed_all_registries()
    dynamics, credit = _decompose(row)
    print(f"{row}: ladder over update lr", flush=True)
    print(
        f"{'update_lr':>12s} {'train_loss':>11s} {'train_acc':>10s} {'s':>5s}  verdict",
        flush=True,
    )
    for composed in LADDER:
        started = time.perf_counter()
        record = _cell(dynamics, credit, composed)
        elapsed = time.perf_counter() - started
        payload = record.payload
        if not payload:
            print(
                f"{composed:12.2e} {'-':>11s} {'-':>10s} "
                f"{elapsed:5.1f}  {record.status.cause.value}",
                flush=True,
            )
            continue
        accuracy = float(payload["train_acc"])  # type: ignore[index]
        print(
            f"{composed:12.2e} {float(payload['train_loss']):11.4f} "  # type: ignore[index]
            f"{accuracy:10.4f} {elapsed:5.1f}  "
            f"{'learns' if accuracy > BEATS_CHANCE_FACTOR * CHANCE else 'flat'}",
            flush=True,
        )


def main() -> None:
    import sys

    if "--ladder" in sys.argv:
        _ladder(sys.argv[sys.argv.index("--ladder") + 1])
        return
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
