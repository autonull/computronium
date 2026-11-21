"""TODO98 P0 locks: the surface is the registry's own list.

The surface has no second list: laws, their knobs, the six seams and the rule
tables are derived from the registry and the harvested schema. These locks fail
when a table is hand-maintained instead of derived, when a per-family screen
returns as a test, or when a declared refusal loses the test that proves it.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from computronium.primitives.cases import (
    IMPOSSIBLE,
    PrimitiveImpossibleError,
    cell_config,
)
from computronium.primitives.registry import REGISTRY, list_primitives
from computronium.primitives.surface import laws, rules, seams, surface, validate

ROOT = Path(__file__).resolve().parents[2]
#: The one per-family test TODO98 keeps: the AGENTS rung-1 capability gate.
RUNG_ONE = Path("tests/primitives/test_primitive_capability.py")
#: Names that only a family screen reads. A test that names one re-screens a
#: box, which is the loop's instrument, not the test surface's gate. This file
#: names them to forbid them, so it is not its own offender.
FAMILY_SCREEN_NAMES = ("map_rows", "screen_coordinate", "BASE_BOXES", "results/sec")

pytestmark = pytest.mark.timeout(300)


def test_the_surface_agrees_with_the_registry() -> None:
    """75 laws, 6 seams, and the rule tables: no disagreement with the registry."""
    assert validate(surface()) == []


def test_laws_are_one_row_per_registered_primitive() -> None:
    """The law list is exactly the registry's 75 rows."""
    declared = {law.id: law for law in laws()}
    registered = {spec.id: spec for spec in list_primitives()}
    assert set(declared) == set(registered)
    for primitive_id, spec in registered.items():
        assert declared[primitive_id].axis == spec.axis, primitive_id


def test_knobs_are_the_axis_declaration() -> None:
    """The knobs a law carries are its axis row's ``accepted_params``."""
    from computronium.experiment.schema import AXES_REGISTRIES
    from computronium.experiment.schema.axis import StructuralAxis

    for law in laws():
        axis_spec = AXES_REGISTRIES[StructuralAxis(law.axis)][law.id.rsplit(".", 1)[-1]]
        assert law.knobs == tuple(sorted(axis_spec.accepted_params)), law.id


def test_seams_are_six_declared_exemplars() -> None:
    """Exactly six seams, each anchored on a registered primitive."""
    from computronium.primitives.registry import get_primitive_spec

    declared = seams()
    assert len(declared) == 6
    assert len({seam.name for seam in declared}) == 6
    for seam in declared:
        spec = get_primitive_spec(seam.primitive_id)
        assert spec is not None, seam.name
        assert spec.axis == seam.axis, seam.name


def test_the_void_tables_are_the_compiled_constraints() -> None:
    """The two void tables are each compiled constraint, by name and table."""
    from computronium.experiment.kernel.search_space import _compiled_void_constraints

    declared = {
        (rule.table, rule.name) for rule in rules() if rule.table != "availability"
    }
    independent, dependent = _compiled_void_constraints()
    expected = {("task-independent", name) for name, _ in independent}
    expected |= {("task-dependent", name) for name, _ in dependent}
    assert declared == expected


def test_availability_rules_are_the_harvested_predicates() -> None:
    """Every availability rule is a harvested hyperparameter predicate."""
    from computronium.experiment.schema.harvest import harvest_schema

    expected = {
        f"{spec.axis_name}.{spec.name}"
        for spec in harvest_schema().hyperparameters
        if spec.availability is not None
    }
    declared = {rule.name for rule in rules() if rule.table == "availability"}
    assert declared == expected


def test_a_surface_row_is_registry_derived(monkeypatch: pytest.MonkeyPatch) -> None:
    """A row added to the registry appears in the surface without a second list."""
    source = REGISTRY["primitive.credit_assignment.gradient"]
    fake = dataclasses.replace(source, id="primitive.credit_assignment.fake")
    monkeypatch.setitem(REGISTRY, fake.id, fake)
    ids = {law.id for law in laws()}
    assert fake.id in ids


def test_no_test_names_a_family_box() -> None:
    """No per-family test re-screens a box; the rung-1 gate is the exception."""
    current = Path(__file__).resolve()
    offenders = [
        path.relative_to(ROOT)
        for path in (ROOT / "tests" / "primitives").rglob("test_*.py")
        if path.resolve() != current
        and path.relative_to(ROOT) != RUNG_ONE
        and any(
            name in path.read_text(encoding="utf-8") for name in FAMILY_SCREEN_NAMES
        )
    ]
    assert not offenders, offenders


@pytest.mark.parametrize("primitive_id", sorted(IMPOSSIBLE))
def test_a_refusal_has_a_failing_test(primitive_id: str) -> None:
    """A declared refusal is the constraint that refuses the cell, or it is prose."""
    declared = next(law for law in laws() if law.id == primitive_id)
    assert declared.refusal == IMPOSSIBLE[primitive_id]
    spec = next(spec for spec in list_primitives() if spec.id == primitive_id)
    with pytest.raises(PrimitiveImpossibleError) as refused:
        cell_config(spec)
    assert refused.value.constraint == declared.refusal
