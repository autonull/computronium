"""Lock: every declared void rule is decidable on the axis tuple (TODO94 R1b).

The planner compiles a VOID row's predicate once per scan. A node the
compiler does not know is not a planner error the caller can read — it was a
bare ``ValueError: Unknown expr type`` from inside a scan. The compiler now
knows every axis-tuple node, and a node it cannot decide fails with the
constraint's name.

Each test fails if a declared row stops compiling, or if a comparison node
decides the opposite of its DSL evaluation.
"""

from __future__ import annotations

import pytest

from computronium.experiment.legality.dsl import (
    add,
    call,
    const,
    eq,
    ge,
    implies,
    lt,
    ne,
    references_params,
    var,
)
from computronium.experiment.schema.registries import (
    CONSTRAINTS_REGISTRY,
    ConstraintKind,
    ConstraintSpec,
    ProofKind,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

_AXIS_VALUES = (
    "digital",
    "feedforward",
    "instantaneous",
    "null",
    "gradient",
    "euclidean",
)


def _values(dynamics: str) -> tuple[str, ...]:
    values: list[str] = list(_AXIS_VALUES)
    values[2] = dynamics
    return (*values, "")


def test_every_params_free_void_row_compiles() -> None:
    """The registry is the contract: a new row cannot crash the planner."""
    from computronium.experiment.kernel.search_space import _compile_expr

    seed_all_registries()
    checked = 0
    for constraint in CONSTRAINTS_REGISTRY.values():
        if constraint.kind != ConstraintKind.VOID:
            continue
        if constraint.predicate is None or references_params(constraint.predicate):
            continue
        _compile_expr(constraint.predicate)
        checked += 1
    assert checked > 0


@pytest.mark.parametrize(
    ("expr", "values", "expected"),
    [
        (ne(var("dynamics"), const("instantaneous")), _values("instantaneous"), False),
        (ne(var("dynamics"), const("instantaneous")), _values("diffusion"), True),
        (lt(const(1), const(2)), _values("diffusion"), True),
        (ge(const(2), const(2)), _values("diffusion"), True),
        (
            implies(
                eq(var("geometry"), const("nca")), eq(var("credit"), const("pc_alm"))
            ),
            _values("diffusion"),
            True,
        ),
        (
            implies(
                eq(var("geometry"), const("feedforward")),
                eq(var("credit"), const("pc_alm")),
            ),
            _values("diffusion"),
            False,
        ),
    ],
)
def test_comparison_nodes_decide_like_the_dsl(expr, values, expected) -> None:
    from computronium.experiment.kernel.search_space import _compile_expr

    assert _compile_expr(expr)(values) is expected


def test_no_declared_row_is_a_constant() -> None:
    """A row that answers the same for every axis value is not a rule.

    Two rows answered ``True`` for all 2,068,416 axis combinations: one
    compared ``substrate`` with itself, one tested a credit name the vocabulary
    does not contain (TODO94 S12). Neither could ever fire, so neither was the
    refusal its name promised.
    """
    from itertools import product

    from computronium.experiment.kernel.search_space import _compile_expr
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    seed_all_registries()
    fields = ("substrate", "geometry", "dynamics", "plasticity", "credit", "update")
    values = [
        [spec.name for spec in AXES_REGISTRIES[StructuralAxis(field)].values()]
        for field in fields
    ]
    for constraint in CONSTRAINTS_REGISTRY.values():
        if constraint.kind != ConstraintKind.VOID or constraint.predicate is None:
            continue
        if references_params(constraint.predicate):
            continue
        if "task" in str(constraint.predicate):
            continue
        rule = _compile_expr(constraint.predicate)
        answers = {bool(rule((*vals, ""))) for vals in product(*values)}
        assert answers != {True}, f"{constraint.name} refuses no coordinate"
        assert answers != {False}, f"{constraint.name} refuses every coordinate"


def test_a_decision_node_names_its_constraint() -> None:
    """A row the axis tuple cannot decide fails with its own name."""
    from computronium.experiment.kernel.search_space import _compiled_void_constraints

    seed_all_registries()
    spec = ConstraintSpec(
        name="synthetic_undecidable_rule",
        kind=ConstraintKind.VOID,
        description="a capability call is decided by the trainer, not the planner",
        predicate=call("has_capability", var("credit")),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    )
    CONSTRAINTS_REGISTRY.register(spec)
    try:
        with pytest.raises(ValueError, match="synthetic_undecidable_rule"):
            _compiled_void_constraints()
    finally:
        CONSTRAINTS_REGISTRY.unregister(spec.name)


def test_call_is_not_decidable_on_the_axis_tuple() -> None:
    from computronium.experiment.kernel.search_space import _compile_expr

    with pytest.raises(ValueError, match="Call"):
        _compile_expr(call("has_capability", var("credit")))


def test_the_arithmetic_nodes_are_not_decidable_either() -> None:
    from computronium.experiment.kernel.search_space import _compile_expr

    with pytest.raises(ValueError, match="Add"):
        _compile_expr(add(var("credit"), const(1)))
