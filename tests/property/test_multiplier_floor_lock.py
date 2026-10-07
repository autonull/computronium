"""No registered multiplier may compose an update lr below the learning floor.

TODO48b R4 (Q1b). The ``step_size_override_<dynamics>_<credit>`` priors scale the
*parameter update* step — the one reader is
``ontology/update.py::_apply_step_size_overrides`` — and the campaign compares
learning rules through them. Twenty-nine of them were registered as
multipliers, every one of them below 1.0, none carrying a measurement, so the
column could only ever attenuate the swept ``update_lr``. One row was
``energy_minimization x thermodynamic_contrast = 5e-5``: a composed lr of
5e-7 against a rule that measurably learns at 1e-3.

The measurement (``scripts/probes/step_size_multipliers.py --ladder``), on
`digits` at gate 2b's reference regime, 10 epochs, ``energy_minimization x
thermodynamic_contrast``:

======================  ==========  ==========  ==========
composed update lr      5e-7        1e-4        1e-3        5e-3
======================  ==========  ==========  ==========
``train_acc``          0.105       0.080       0.411       0.878
======================  ==========  ==========  ==========

So the rule was never broken; its multiplier deleted it. R4 retired the
attenuation (every row re-registered at 1.0 with the measurement in its
description) and this lock is what stops the column regrowing by hand:

**no row may compose an update lr below :data:`LEARNING_FLOOR`.**

Falsifiable in both directions — registering a multiplier of ``1e-4`` turns
``test_no_registered_multiplier_strangles_its_rule`` red, and the assertion
reads the *composed* config rather than the table, so a row whose base also
moved cannot hide behind a nominal 1.0.
"""

from __future__ import annotations

from computronium.experiment.execution import compose_configs, task_shape
from computronium.experiment.schema import (
    AXES_REGISTRIES,
    StructuralAxis,
    Coordinate,
    harvest_schema,
    prior_value,
    MEASURED_PARAM_BUDGET,
    PRIORS,
    seed_all_registries,
)

PREFIX = "step_size_override_"

#: The composed update lr at which the audited rule demonstrably learns
#: (``train_acc`` 0.411 at 1e-3, 0.878 at 5e-3). Measured, not chosen.
LEARNING_FLOOR = 1e-3


type Row = tuple[str, str, str, float, str]


def _rows() -> list[Row]:
    """``(name, dynamics, credit, multiplier, description)`` per registered row.

    The axis registries are the grammar: both axis names contain underscores,
    so only they know where the dynamics name ends. A row whose name is not a
    registered pair is *not* returned — it is not a rule the table can handicap.
    """
    credits = {spec.name for spec in AXES_REGISTRIES[StructuralAxis.CREDIT]}
    rows: list[Row] = []
    for spec in PRIORS:
        if not spec.name.startswith(PREFIX):
            continue
        suffix = spec.name.removeprefix(PREFIX)
        for axis in AXES_REGISTRIES[StructuralAxis.DYNAMICS]:
            tail = suffix[len(axis.name) + 1 :]
            if suffix.startswith(f"{axis.name}_") and tail in credits:
                measured = prior_value(spec.name)
                assert measured is not None
                multiplier, _, _ = measured
                rows.append((spec.name, axis.name, tail, multiplier, spec.description))
                break
    return rows


def _composed_update_lr(dynamics: str, credit: str) -> float | None:
    """The update lr a cell of this pair holds, or ``None`` if it cannot exist."""
    shape = task_shape("digits")
    try:
        config = compose_configs(
            coordinate=Coordinate(
                substrate="digital",
                geometry="feedforward",
                dynamics=dynamics,
                plasticity="fast_weights",
                credit=credit,
                update="euclidean",
                params={"depth": 2, "hidden_dim": 64},
            ),
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=MEASURED_PARAM_BUDGET,
        )
    except ValueError, RuntimeError:
        return None
    return float(config.update.step_size)


def test_the_table_has_rows_to_audit() -> None:
    assert _rows(), "no multiplier rows registered; the lock has nothing to hold"


def test_no_registered_multiplier_strangles_its_rule() -> None:
    """The claim: every row composes an lr at or above the learning floor."""
    seed_all_registries()
    swept_floor = harvest_schema().by_name()["update_lr"].domain.lo
    assert swept_floor is not None and swept_floor <= LEARNING_FLOOR, (
        "the floor sits below the swept domain; the lock would be vacuous"
    )
    starved = [
        (dynamics, credit, lr)
        for _name, dynamics, credit, _mult, _desc in _rows()
        if (lr := _composed_update_lr(dynamics, credit)) is not None
        and lr < LEARNING_FLOOR
    ]
    assert not starved, (
        f"rows composing an update lr below the measured learning floor "
        f"{LEARNING_FLOOR:g}: {starved}"
    )


def test_multipliers_cannot_attenuate_below_one() -> None:
    """A multiplier is a prior, and this column's priors were never measured.

    Every registered row is ``<= 1.0`` in the original table, which is what made
    the column a handicap rather than a prior. A row may scale a step *up*; one
    that scales it down needs the ladder measurement in its description.
    """
    seed_all_registries()
    unrecorded = [
        name
        for name, _d, _c, mult, desc in _rows()
        if mult < 1.0 and "Retired" not in desc
    ]
    assert not unrecorded, (
        f"attenuating rows without a recorded retirement: {unrecorded}"
    )
