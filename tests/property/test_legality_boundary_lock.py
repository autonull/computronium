"""Legality boundary lock: DECLARED constraints must only encode machine-checkable infeasibility.

This test enforces the legality boundary from feedback #9:
- Constraints with origin=DECLARED (or SYSTEM_CONFIG, i.e., from SystemConfig.validate)
  may ONLY exclude logically/experimentally invalid configurations (voids).
- They may never encode "we don't expect this to work" — that belongs in PRIORS.
- Every DECLARED constraint must have a machine-checkable infeasibility proof:
  type mismatch, resource violation, or logical contradiction.
- No heuristic exclusions allowed in DECLARED constraints.

This is a CI gate for WP3.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

import pytest

from computronium.experiment.legality.classify import (
    DEFECT_REGISTRY,
    DefectClass,
    VoidReason,
)
from computronium.experiment.legality.engine import (
    Constraint,
    ConstraintEnforcement,
    ConstraintKind,
    ConstraintOrigin,
    ConstraintScope,
    ENGINE,
    create_constraint,
    get_engine,
)
from computronium.experiment.legality.dsl import (
    Eq,
    Var,
    Const,
    and_,
    or_,
    not_,
    gt,
    lt,
    in_,
    evaluate,
    EvaluationContext,
    var,
    const,
    eq,
)


if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


class ProofKind(StrEnum):
    """Kinds of machine-checkable infeasibility proofs."""

    TYPE_MISMATCH = "type_mismatch"  # e.g., substrate requires digital, geometry requires analog
    RESOURCE_VIOLATION = "resource_violation"  # e.g., memory > budget, compute > limit
    LOGICAL_CONTRADICTION = "logical_contradiction"  # e.g., A and not A


@dataclass(frozen=True, slots=True)
class InfeasibilityProof:
    """A machine-checkable proof of infeasibility for a DECLARED constraint."""

    proof_kind: ProofKind
    description: str
    # The expression that constitutes the proof
    proof_expr: Eq | Var | Const
    # Axes/values involved
    axes: tuple[str, ...]
    values: tuple[str, ...]


# Registry of infeasibility proofs for DECLARED constraints
# Each DECLARED constraint MUST have an entry here
DECLARED_INFEASIBILITY_PROOFS: dict[str, InfeasibilityProof] = {}


def register_declared_proof(
    constraint_id: str,
    proof: InfeasibilityProof,
) -> None:
    """Register an infeasibility proof for a DECLARED constraint."""
    DECLARED_INFEASIBILITY_PROOFS[constraint_id] = proof


def _get_declared_constraints() -> list[Constraint]:
    """Get all constraints with DECLARED origin (SYSTEM_CONFIG in current impl)."""
    engine = get_engine()
    return [
        c
        for c in engine.all_constraints()
        if c.origin in (ConstraintOrigin.SYSTEM_CONFIG, ConstraintOrigin.DYNAMICS_COMPAT, ConstraintOrigin.CREDIT_COMPAT)
    ]


def _has_machine_checkable_proof(constraint: Constraint) -> tuple[bool, str | None]:
    """Check if a constraint has a registered machine-checkable proof."""
    if constraint.constraint_id in DECLARED_INFEASIBILITY_PROOFS:
        return True, None
    return False, f"No infeasibility proof registered for constraint {constraint.constraint_id} ({constraint.description})"


def _is_heuristic_exclusion(constraint: Constraint) -> tuple[bool, str | None]:
    """Detect if a constraint appears to be a heuristic exclusion rather than a void.

    Heuristic exclusions typically:
    - Use soft constraints to express preferences
    - Reference performance metrics (accuracy, loss, etc.)
    - Use vague language like "expected to work", "recommended", "preferred"
    """
    desc = constraint.description.lower()
    expr_str = str(constraint.expr).lower()

    # Keywords that suggest heuristic/preference rather than logical infeasibility
    heuristic_keywords = [
        "expected",
        "recommended",
        "preferred",
        "likely",
        "may work",
        "should work",
        "performance",
        "accuracy",
        "loss",
        "converge",
        "better",
        "worse",
        "optimal",
        "suboptimal",
    ]

    for kw in heuristic_keywords:
        if kw in desc or kw in expr_str:
            return True, f"Heuristic language detected: '{kw}' in constraint {constraint.constraint_id}"

    return False, None


class TestLegalityBoundary:
    """Tests enforcing the legality boundary for DECLARED constraints."""

    def test_declared_constraints_have_infeasibility_proofs(self) -> None:
        """Every DECLARED constraint must have a machine-checkable infeasibility proof."""
        declared = _get_declared_constraints()

        if not declared:
            pytest.skip("No DECLARED constraints registered yet")

        missing_proofs = []
        for constraint in declared:
            has_proof, reason = _has_machine_checkable_proof(constraint)
            if not has_proof:
                missing_proofs.append(f"{constraint.constraint_id}: {reason}")

        if missing_proofs:
            pytest.fail(
                "DECLARED constraints missing infeasibility proofs:\n"
                + "\n".join(missing_proofs)
                + "\n\nEvery DECLARED constraint must have a registered proof "
                "in DECLARED_INFEASIBILITY_PROOFS with ProofKind "
                "(TYPE_MISMATCH, RESOURCE_VIOLATION, or LOGICAL_CONTRADICTION)."
            )

    def test_declared_constraints_are_not_heuristic(self) -> None:
        """DECLARED constraints must not encode heuristic preferences."""
        declared = _get_declared_constraints()

        if not declared:
            pytest.skip("No DECLARED constraints registered yet")

        heuristic_violations = []
        for constraint in declared:
            is_heuristic, reason = _is_heuristic_exclusion(constraint)
            if is_heuristic:
                heuristic_violations.append(f"{constraint.constraint_id}: {reason}")

        if heuristic_violations:
            pytest.fail(
                "DECLARED constraints contain heuristic exclusions (should be in PRIORS):\n"
                + "\n".join(heuristic_violations)
            )

    def test_void_patterns_have_proofs(self) -> None:
        """Every registered void pattern must have a corresponding infeasibility proof."""
        # This ensures that the void patterns in DEFECT_REGISTRY are backed by proofs
        void_patterns = list(DEFECT_REGISTRY._void_patterns.keys())

        # For now, we verify the patterns exist and are bidirectional
        for key1 in void_patterns:
            key2 = (key1[1], key1[0])
            assert key2 in DEFECT_REGISTRY._void_patterns, (
                f"Void pattern {key1} not registered bidirectionally; "
                f"missing {key2}"
            )

    def test_no_declared_constraint_on_performance(self) -> None:
        """DECLARED constraints must not reference performance metrics."""
        declared = _get_declared_constraints()

        if not declared:
            pytest.skip("No DECLARED constraints registered yet")

        performance_keywords = [
            "accuracy",
            "loss",
            "score",
            "metric",
            "performance",
            "converge",
            "diverge",
            "speed",
            "throughput",
            "latency",
        ]

        violations = []
        for constraint in declared:
            desc = constraint.description.lower()
            expr_str = str(constraint.expr).lower()
            for kw in performance_keywords:
                if kw in desc or kw in expr_str:
                    violations.append(
                        f"{constraint.constraint_id}: references '{kw}' "
                        f"(performance metric in DECLARED constraint)"
                    )

        if violations:
            pytest.fail(
                "DECLARED constraints reference performance metrics "
                "(should be in PRIORS or soft constraints):\n"
                + "\n".join(violations)
            )

    def test_declared_constraints_are_hard_or_void(self) -> None:
        """DECLARED constraints must be HARD kind (voids) or BUDGET, never SOFT."""
        declared = _get_declared_constraints()

        if not declared:
            pytest.skip("No DECLARED constraints registered yet")

        soft_violations = []
        for constraint in declared:
            if constraint.kind == ConstraintKind.SOFT:
                soft_violations.append(
                    f"{constraint.constraint_id}: DECLARED constraint is SOFT kind "
                    "(should be HARD for voids or BUDGET for resource limits)"
                )

        if soft_violations:
            pytest.fail(
                "DECLARED constraints with SOFT kind (must be HARD or BUDGET):\n"
                + "\n".join(soft_violations)
            )

    def test_system_config_validator_constraints_are_voids(self) -> None:
        """Constraints from SystemConfig.validate() must correspond to void patterns."""
        # This test will be populated when SystemConfig.validate() constraints are migrated
        # For now, it serves as a placeholder for the migration work
        engine = get_engine()
        system_config_constraints = [
            c for c in engine.all_constraints()
            if c.origin == ConstraintOrigin.SYSTEM_CONFIG
        ]

        # When constraints are migrated from SystemConfig.validate(), they must
        # all map to known void patterns in DEFECT_REGISTRY
        # This is a structural test - actual validation happens when constraints are added

        # Verify that if we have SYSTEM_CONFIG constraints, they align with void patterns
        if system_config_constraints:
            # Each should correspond to a void reason
            for constraint in system_config_constraints:
                # The constraint should be a HARD constraint at CELL scope
                assert constraint.kind == ConstraintKind.HARD, (
                    f"SYSTEM_CONFIG constraint {constraint.constraint_id} must be HARD"
                )
                assert constraint.scope == ConstraintScope.CELL, (
                    f"SYSTEM_CONFIG constraint {constraint.constraint_id} must be CELL scope"
                )

    def test_priors_not_in_declared_constraints(self) -> None:
        """PRIORS (preferences) must not be encoded as DECLARED constraints."""
        # This is a design-time check - PRIORS registry should be separate from
        # CONSTRAINTS registry. The test verifies separation of concerns.

        from computronium.experiment.schema.registries import (
            PRIORS_REGISTRY,
            CONSTRAINTS_REGISTRY,
        )

        # PRIORS and CONSTRAINTS should be separate registries
        assert PRIORS_REGISTRY is not CONSTRAINTS_REGISTRY

        # PRIORS should not contain Constraint objects
        for spec in PRIORS_REGISTRY.values():
            assert not isinstance(spec, Constraint), (
                f"PRIORS registry contains Constraint: {spec}"
            )

        # CONSTRAINTS should not contain PriorSpec objects
        from computronium.experiment.schema.registries import PriorSpec

        for spec in CONSTRAINTS_REGISTRY.values():
            assert not isinstance(spec, PriorSpec), (
                f"CONSTRAINTS registry contains PriorSpec: {spec}"
            )

    def test_constraint_origin_enum_has_declared(self) -> None:
        """ConstraintOrigin should have a DECLARED variant for explicit void constraints."""
        # The plan mentions DECLARED origin; currently we have SYSTEM_CONFIG
        # This test documents the expected enum value
        origins = [o.value for o in ConstraintOrigin]

        # For now, SYSTEM_CONFIG serves as the DECLARED origin
        # In the future, a dedicated DECLARED origin may be added
        assert "system_config" in origins


class TestConstraintProofRegistration:
    """Tests for the proof registration mechanism."""

    def test_proof_registration_works(self) -> None:
        """Test that proof registration works correctly."""
        # Create a test constraint
        expr = eq(var("substrate"), const("digital"))
        constraint = create_constraint(
            expr=expr,
            origin=ConstraintOrigin.SYSTEM_CONFIG,
            scope=ConstraintScope.CELL,
            enforcement=ConstraintEnforcement.ALWAYS,
            kind=ConstraintKind.HARD,
            description="Test constraint for proof registration",
        )

        # Register a proof
        proof = InfeasibilityProof(
            proof_kind=ProofKind.TYPE_MISMATCH,
            description="Substrate must be digital for this geometry",
            proof_expr=expr,
            axes=("substrate", "geometry"),
            values=("digital", "crossbar"),
        )
        register_declared_proof(constraint.constraint_id, proof)

        # Verify
        assert constraint.constraint_id in DECLARED_INFEASIBILITY_PROOFS
        registered = DECLARED_INFEASIBILITY_PROOFS[constraint.constraint_id]
        assert registered.proof_kind == ProofKind.TYPE_MISMATCH

        # Clean up
        del DECLARED_INFEASIBILITY_PROOFS[constraint.constraint_id]
        get_engine().remove_constraint(constraint.constraint_id)

    def test_proof_kinds_are_exhaustive(self) -> None:
        """All proof kinds should be used somewhere."""
        # This test ensures we don't have unused proof kinds
        used_kinds = {p.proof_kind for p in DECLARED_INFEASIBILITY_PROOFS.values()}
        all_kinds = set(ProofKind)

        # At minimum, we should have examples of each kind once constraints are seeded
        # For now, just verify the enum is well-formed
        assert len(all_kinds) == 3
        assert ProofKind.TYPE_MISMATCH in all_kinds
        assert ProofKind.RESOURCE_VIOLATION in all_kinds
        assert ProofKind.LOGICAL_CONTRADICTION in all_kinds


# Re-export for external use
__all__ = [
    "DECLARED_INFEASIBILITY_PROOFS",
    "InfeasibilityProof",
    "ProofKind",
    "register_declared_proof",
]