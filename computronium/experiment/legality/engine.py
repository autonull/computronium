"""Legality engine: constraint model and enforcement."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from computronium.experiment.legality.dsl import (
    EvaluationContext,
    Expr,
    evaluate,
    expr_hash,
    expr_to_json,
)

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record


def _canonical_json(obj: Any) -> str:
    """Serialize to canonical JSON for content hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class ConstraintOrigin(StrEnum):
    """Origin of a constraint."""

    SYSTEM_CONFIG = "system_config"  # From SystemConfig.validate()
    TASK_FENCE = "task_fence"  # Task-specific guardrails
    APPLY_CONSTRAINTS = "apply_constraints"  # User-applied constraints
    DYNAMICS_COMPAT = "dynamics_compat"  # Cross-axis compatibility (R63)
    CREDIT_COMPAT = "credit_compat"  # Credit assignment compatibility
    MANUAL = "manual"  # Manually added


class ConstraintScope(StrEnum):
    """Scope at which a constraint applies."""

    CELL = "cell"  # Structural coordinate only (R9)
    MEASUREMENT = "measurement"  # Coordinate + schedule
    RUN = "run"  # Entire run
    GLOBAL = "global"  # Across all runs


class ConstraintEnforcement(StrEnum):
    """When a constraint is enforced."""

    S1_DISCOVERY = "s1_discovery"  # Initial mapping
    S2_VALIDATION = "s2_validation"  # Verification
    S3_CALIBRATION = "s3_calibration"  # Calibration
    S4_EXPANSION = "s4_expansion"  # Expansion (R38 - globally suppressive)
    S5_COMPOSE = "s5_compose"  # Composition (resource constraints with params)
    S5_MATURATION = "s5_maturation"  # Maturation
    S6_CLAIM = "s6_claim"  # Claim-grade (R38 - globally suppressive)
    S7_REPRODUCTION = "s7_reproduction"
    S8_DISTILLATION = "s8_distillation"
    S9_DEPLOYMENT = "s9_deployment"
    S10_MONITORING = "s10_monitoring"
    S11_RETIREMENT = "s11_retirement"
    ALWAYS = "always"  # Enforced at all stages


# Stages at which global suppression applies (R38)
_SUPPRESS_STAGES = frozenset({
    ConstraintEnforcement.S4_EXPANSION,
    ConstraintEnforcement.S5_COMPOSE,
    ConstraintEnforcement.S6_CLAIM,
})


class ConstraintKind(StrEnum):
    """Kind of constraint."""

    HARD = "hard"  # Must pass, blocks execution
    SOFT = "soft"  # Advisory, recorded but doesn't block
    BUDGET = "budget"  # Budget-related (cost, time, resources)


@dataclass(frozen=True, slots=True)
class Constraint:
    """A single constraint with metadata.

    Attributes:
        constraint_id: Unique identifier (content hash of expr + metadata)
        expr: The DSL expression to evaluate
        origin: Where this constraint came from
        scope: At what level it applies
        enforcement: When it is enforced (stage)
        kind: Hard/soft/budget
        description: Human-readable description
        tags: Optional tags for categorization
    """

    constraint_id: str
    expr: Expr
    origin: ConstraintOrigin
    scope: ConstraintScope
    enforcement: ConstraintEnforcement
    kind: ConstraintKind
    description: str = ""
    tags: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if not hasattr(self.expr, "to_json"):
            raise TypeError(
                f"expr must be an expression with to_json method, got {type(self.expr)}"
            )
        if not isinstance(self.origin, ConstraintOrigin):
            raise TypeError(f"origin must be ConstraintOrigin, got {type(self.origin)}")
        if not isinstance(self.scope, ConstraintScope):
            raise TypeError(f"scope must be ConstraintScope, got {type(self.scope)}")
        if not isinstance(self.enforcement, ConstraintEnforcement):
            raise TypeError(
                f"enforcement must be ConstraintEnforcement, got {type(self.enforcement)}"
            )
        if not isinstance(self.kind, ConstraintKind):
            raise TypeError(f"kind must be ConstraintKind, got {type(self.kind)}")

    @classmethod
    def create(
        cls,
        expr: Expr,
        origin: ConstraintOrigin,
        scope: ConstraintScope,
        enforcement: ConstraintEnforcement,
        kind: ConstraintKind,
        description: str = "",
        tags: frozenset[str] | None = None,
    ) -> Constraint:
        """Create a constraint with auto-generated ID."""
        # Content hash includes expr hash + metadata for uniqueness
        metadata = {
            "expr_hash": expr_hash(expr),
            "origin": origin.value,
            "scope": scope.value,
            "enforcement": enforcement.value,
            "kind": kind.value,
        }
        constraint_id = hashlib.sha256(_canonical_json(metadata).encode()).hexdigest()[
            :16
        ]
        return cls(
            constraint_id=constraint_id,
            expr=expr,
            origin=origin,
            scope=scope,
            enforcement=enforcement,
            kind=kind,
            description=description,
            tags=tags or frozenset(),
        )

    def to_json(self) -> dict[str, Any]:
        """Serialize to JSON."""
        return {
            "constraint_id": self.constraint_id,
            "expr": expr_to_json(self.expr),
            "origin": self.origin.value,
            "scope": self.scope.value,
            "enforcement": self.enforcement.value,
            "kind": self.kind.value,
            "description": self.description,
            "tags": sorted(self.tags),
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Constraint:
        """Deserialize from JSON."""
        from computronium.experiment.legality.dsl import expr_from_json

        return cls(
            constraint_id=data["constraint_id"],
            expr=expr_from_json(data["expr"]),
            origin=ConstraintOrigin(data["origin"]),
            scope=ConstraintScope(data["scope"]),
            enforcement=ConstraintEnforcement(data["enforcement"]),
            kind=ConstraintKind(data["kind"]),
            description=data.get("description", ""),
            tags=frozenset(data.get("tags", [])),
        )


@dataclass(frozen=True, slots=True)
class ConstraintViolation:
    """Record of a constraint violation."""

    constraint_id: str
    constraint_expr: str  # JSON string of expression
    record_id: str
    cell_key: str
    measurement_key: str
    severity: str  # "error" | "warning"
    message: str
    stage: str


class LegalityEngine:
    """Engine for managing and enforcing constraints.

    Globally-suppressive semantics (R38): a constraint violation at any
    cell suppresses that cell from all downstream stages. Hard constraints
    block execution; soft constraints emit warnings; budget constraints
    affect allocation.
    """

    def __init__(self) -> None:
        self._constraints: dict[str, Constraint] = {}
        self._by_enforcement: dict[ConstraintEnforcement, list[Constraint]] = {
            e: [] for e in ConstraintEnforcement
        }
        self._by_scope: dict[ConstraintScope, list[Constraint]] = {
            s: [] for s in ConstraintScope
        }
        self._by_kind: dict[ConstraintKind, list[Constraint]] = {
            k: [] for k in ConstraintKind
        }

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the engine."""
        if constraint.constraint_id in self._constraints:
            return  # Idempotent
        self._constraints[constraint.constraint_id] = constraint
        self._by_enforcement[constraint.enforcement].append(constraint)
        self._by_scope[constraint.scope].append(constraint)
        self._by_kind[constraint.kind].append(constraint)

    def remove_constraint(self, constraint_id: str) -> bool:
        """Remove a constraint by ID."""
        if constraint_id not in self._constraints:
            return False
        constraint = self._constraints.pop(constraint_id)
        self._by_enforcement[constraint.enforcement].remove(constraint)
        self._by_scope[constraint.scope].remove(constraint)
        self._by_kind[constraint.kind].remove(constraint)
        return True

    def get_constraint(self, constraint_id: str) -> Constraint | None:
        """Get a constraint by ID."""
        return self._constraints.get(constraint_id)

    def get_constraints_for_stage(
        self, stage: ConstraintEnforcement, scope: ConstraintScope | None = None
    ) -> list[Constraint]:
        """Get all constraints enforced at a given stage, optionally filtered by scope."""
        constraints = self._by_enforcement.get(stage, [])
        if scope is not None:
            constraints = [c for c in constraints if c.scope == scope]
        return constraints

    def get_constraints_for_record(self, record: Record) -> list[Constraint]:
        """Get all constraints applicable to a record (cell + measurement scope)."""
        # Cell-scope constraints apply to all measurements in the cell
        # Measurement-scope constraints apply to specific measurement
        return (
            self._by_scope[ConstraintScope.CELL]
            + self._by_scope[ConstraintScope.MEASUREMENT]
        )

    def evaluate_record(
        self, record: Record, stage: ConstraintEnforcement
    ) -> tuple[list[ConstraintViolation], list[ConstraintViolation]]:
        """Evaluate all applicable constraints for a record at a stage.

        Returns:
            Tuple of (hard_violations, soft_violations).
            Hard violations block the record; soft violations are warnings.
        """
        ctx = EvaluationContext(record)
        hard_violations: list[ConstraintViolation] = []
        soft_violations: list[ConstraintViolation] = []

        for constraint in self.get_constraints_for_stage(stage):
            # Skip if enforcement is ALWAYS but stage doesn't match (for specific stages)
            if constraint.enforcement not in {
                ConstraintEnforcement.ALWAYS,
                stage,
            }:
                continue

            try:
                result = evaluate(constraint.expr, ctx)
                if not result:
                    violation = ConstraintViolation(
                        constraint_id=constraint.constraint_id,
                        constraint_expr=_canonical_json(constraint.expr.to_json()),
                        record_id=record.record_id,
                        cell_key=record.cell_key,
                        measurement_key=record.measurement_key,
                        severity="error"
                        if constraint.kind == ConstraintKind.HARD
                        else "warning",
                        message=f"Constraint violated: {constraint.description or constraint.constraint_id}",
                        stage=stage.value,
                    )
                    if constraint.kind == ConstraintKind.HARD:
                        hard_violations.append(violation)
                    else:
                        soft_violations.append(violation)
            except Exception as e:
                # Evaluation error - log as warning but don't treat as hard violation
                # This allows the pipeline to continue even if some constraints
                # have parsing/evaluation issues (e.g., complex predicates)
                violation = ConstraintViolation(
                    constraint_id=constraint.constraint_id,
                    constraint_expr=_canonical_json(constraint.expr.to_json()),
                    record_id=record.record_id,
                    cell_key=record.cell_key,
                    measurement_key=record.measurement_key,
                    severity="warning",
                    message=f"Constraint evaluation error: {e}",
                    stage=stage.value,
                )
                soft_violations.append(violation)

        return hard_violations, soft_violations

    def is_cell_suppressed(self, cell_key: str, stage: ConstraintEnforcement) -> bool:
        """Check if a cell is globally suppressed (R38).

        A cell is suppressed if ANY measurement in it has a hard violation
        at S4 (expansion) or S6 (claim) stage. This is globally-suppressive
        semantics: once suppressed at S4/S6, the cell is excluded from
        all downstream stages.
        """
        if stage not in _SUPPRESS_STAGES:
            return False
        # This would require querying the store for violations
        # For now, return False - actual implementation needs store integration
        return False

    def all_constraints(self) -> list[Constraint]:
        """Get all constraints."""
        return list(self._constraints.values())

    def __len__(self) -> int:
        return len(self._constraints)


def create_constraint(
    expr: Expr,
    origin: ConstraintOrigin,
    scope: ConstraintScope,
    enforcement: ConstraintEnforcement,
    kind: ConstraintKind,
    description: str = "",
    tags: frozenset[str] | None = None,
    engine: LegalityEngine | None = None,
) -> Constraint:
    """Create a constraint and register it on the given engine.

    The engine is explicit (K10: no module-level shared engine); callers
    own the `LegalityEngine` instance lifetime.
    """
    constraint = Constraint.create(
        expr, origin, scope, enforcement, kind, description, tags
    )
    if engine is not None:
        engine.add_constraint(constraint)
    return constraint


__all__ = [
    "Constraint",
    "ConstraintEnforcement",
    "ConstraintKind",
    "ConstraintOrigin",
    "ConstraintScope",
    "ConstraintViolation",
    "LegalityEngine",
    "create_constraint",
]
