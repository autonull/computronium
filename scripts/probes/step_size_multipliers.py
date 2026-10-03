"""Audit the update-step multiplier table: a prior, not a verdict (TODO48 Q1b).

Every ``step_size_override_<dynamics>_<credit>`` prior multiplies the *parameter
update* step (``ParameterUpdateConfig.step_size``, swept as ``update_lr``) —
**not** the settle step; ``ontology/update.py`` is the only reader. The campaign
compares learning rules *through* that table, so a row that scales the update
lr by ``5e-5`` does not handicap a rule, it deletes it.

Two modes, because the audit and the control answer different questions:

``--audit`` (default, milliseconds, no training)
    Compose each row and print the update lr the cell *actually* holds, and its
    attenuation against the best-composed row in the table. Attenuation is a
    measurement, not a verdict; the verdict needs the lr at which the rule
    learns, which is what the ladder measures.

``--ladder <dynamics>_<credit>`` (one training cell per rung, ~45 s each)
    The control that separates "the rule is broken" from "the rule is
    strangled": the same rule at a ladder of composed update lrs. If the rule
    learns at a fair lr and is flat only at its registered one, the table is the
    defect and the registry edit is the fix.

Informed the shipped campaign (``examples/learning-rules-and-geometry-digits.yaml``)
and ``tests/acceptance/test_campaign_lock.py`` gate 2b's reference regime.

Usage::

    uv run python scripts/probes/step_size_multipliers.py
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

PREFIX = "step_size_override_"
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


def _decompose(suffix: str) -> tuple[str, str] | None:
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
    return None


def _rows() -> list[tuple[str, str, str, float]]:
    """``(prior name, dynamics, credit, multiplier)`` for every override row."""
    from computronium.experiment.schema.registries import prior_value
    from computronium.experiment.schema.seed_registries import PRIORS

    rows: list[tuple[str, str, str, float]] = []
    for spec in PRIORS:
        if not spec.name.startswith(PREFIX):
            continue
        pair = _decompose(spec.name.removeprefix(PREFIX))
        measured = prior_value(spec.name)
        if pair is None or measured is None:
            # Never drop a row quietly: an unregistered pair is a question this
            # table cannot answer, and silence would read as "audited".
            print(f"SKIPPED (not a dynamics x credit pair): {spec.name}", flush=True)
            continue
        dynamics, credit = pair
        multiplier, _, _ = measured
        rows.append((spec.name, dynamics, credit, multiplier))
    return rows


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


def _composed_update_lr(dynamics: str, credit: str) -> tuple[float | None, str]:
    """The update lr a cell of this row *actually* holds, composed not assumed."""
    from computronium.experiment.execution.compose import compose_configs
    from computronium.experiment.execution.evaluate import task_shape

    shape = task_shape("digits")
    try:
        config = compose_configs(
            coordinate=_coordinate(dynamics, credit, {"depth": 2, "hidden_dim": 64}),
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=MEASURED_PARAM_BUDGET,
        )
    except Exception as exc:  # ruff: ignore[blind-except] - an illegal pair is an audit result
        return None, f"{type(exc).__name__}: {str(exc)[:48]}"
    return float(config.update.step_size), "-"


def _cell(dynamics: str, credit: str, update_lr: float | None) -> Record:
    """One reference-regime cell; ``update_lr=None`` uses the swept default."""
    from computronium.experiment.schema.harvest import InactiveHyperparameterError

    base: dict[str, object] = {"depth": 2, "hidden_dim": 64, "settle_step": SETTLE_STEP}
    if update_lr is not None:
        base["update_lr"] = update_lr
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
        return cell_record(
            _coordinate(dynamics, credit, {"depth": 2, "hidden_dim": 64}),
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


def _audit() -> None:
    """Compose every row; no training. Prints the lr the cell actually holds."""
    seed_all_registries()
    rows = _rows()
    composed = {
        (dynamics, credit): lr
        for _n, dynamics, credit, _m in rows
        if (lr := _composed_update_lr(dynamics, credit)[0]) is not None
    }
    best = max(composed.values(), default=0.0)
    print(
        f"{len(rows)} rows; composed update lr = base(default 0.01) x "
        f"multiplier; best composed lr in the table = {best:.2e}",
        flush=True,
    )
    print(
        f"{'dynamics':22s} {'credit':22s} {'mult':>9s} {'composed_lr':>12s} "
        f"{'attenuation':>11s}  note",
        flush=True,
    )
    for _name, dynamics, credit, multiplier in rows:
        lr, error = _composed_update_lr(dynamics, credit)
        if lr is None:
            print(
                f"{dynamics:22s} {credit:22s} {multiplier:9.1e} {'-':>12s} "
                f"{'-':>11s}  ILLEGAL HERE ({error})",
                flush=True,
            )
            continue
        attenuation = best / lr if lr else float("inf")
        print(
            f"{dynamics:22s} {credit:22s} {multiplier:9.1e} {lr:12.2e} "
            f"{attenuation:10.0f}x  vs the table's best composed lr",
            flush=True,
        )


def _ladder(row: str) -> None:
    """The control: one rule at a ladder of composed update lrs."""
    from computronium.experiment.schema.registries import prior_value

    seed_all_registries()
    name = f"{PREFIX}{row}"
    registered = prior_value(name)
    pair = _decompose(row)
    if registered is None or pair is None:
        raise SystemExit(f"not an audited multiplier row: {name}")
    base, _, _ = registered
    dynamics, credit = pair
    print(
        f"{name}: registered multiplier={base:g}; ladder over composed lr",
        flush=True,
    )
    print(
        f"{'composed_lr':>12s} {'declared_lr':>12s} {'train_loss':>11s} "
        f"{'train_acc':>10s} {'s':>5s}  verdict",
        flush=True,
    )
    for composed in LADDER:
        started = time.perf_counter()
        record = _cell(dynamics, credit, composed / base)
        elapsed = time.perf_counter() - started
        payload = record.payload
        if not payload:
            print(
                f"{composed:12.2e} {composed / base:12.2e} {'-':>11s} {'-':>10s} "
                f"{elapsed:5.1f}  {record.status.cause.value}",
                flush=True,
            )
            continue
        accuracy = float(payload["train_acc"])  # type: ignore[index]
        print(
            f"{composed:12.2e} {composed / base:12.2e} "
            f"{float(payload['train_loss']):11.4f} "  # type: ignore[index]
            f"{accuracy:10.4f} {elapsed:5.1f}  "
            f"{'learns' if accuracy > BEATS_CHANCE_FACTOR * CHANCE else 'flat'}",
            flush=True,
        )


def main() -> None:
    import sys

    if "--ladder" in sys.argv:
        _ladder(sys.argv[sys.argv.index("--ladder") + 1])
        return
    _audit()


if __name__ == "__main__":
    main()
