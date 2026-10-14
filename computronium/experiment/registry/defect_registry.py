"""Defect registry: turns failures into constraints on the LegalityEngine.

Phase 3 of TODO63: wires the existing failure taxonomy and LegalityEngine
into the loop so that observed defects prune the search space.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path  # ruff: ignore[typing-only-standard-library-import] - used in runtime type hints
from typing import TYPE_CHECKING, Any

from computronium.experiment.legality.classify import (
    classify_record,
    get_defect_registry,
)
from computronium.experiment.legality.engine import (
    Constraint,
    ConstraintEnforcement,
    ConstraintKind,
    ConstraintOrigin,
    ConstraintScope,
    LegalityEngine,
)
from computronium.experiment.schema.record import (
    FailureCause,
    GateVerdict,
    Record,
)

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DefectConstraint:
    """A constraint derived from an observed defect.

    Wraps a LegalityEngine Constraint with metadata for versioning and revocation.
    """

    constraint_id: str
    defect_cause: FailureCause
    defect_class: str
    cell_key: str
    measurement_key: str
    constraint: Constraint
    author: str = "system"
    created_at: float = field(default_factory=time.time)
    revoked: bool = False
    revoked_at: float | None = None
    revoked_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        data = {
            "constraint_id": self.constraint_id,
            "defect_cause": self.defect_cause.value,
            "defect_class": self.defect_class,
            "cell_key": self.cell_key,
            "measurement_key": self.measurement_key,
            "constraint": self.constraint.to_json(),
            "author": self.author,
            "created_at": self.created_at,
            "revoked": self.revoked,
            "revoked_at": self.revoked_at,
            "revoked_by": self.revoked_by,
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DefectConstraint:
        """Deserialize from JSON."""
        constraint = Constraint.from_json(data["constraint"])
        return cls(
            constraint_id=data["constraint_id"],
            defect_cause=FailureCause(data["defect_cause"]),
            defect_class=data["defect_class"],
            cell_key=data["cell_key"],
            measurement_key=data["measurement_key"],
            constraint=constraint,
            author=data.get("author", "system"),
            created_at=data.get("created_at", time.time()),
            revoked=data.get("revoked", False),
            revoked_at=data.get("revoked_at"),
            revoked_by=data.get("revoked_by"),
        )


class DefectRegistry:
    """Registry of defect-derived constraints.

    Turns FAIL/QUARANTINE records into LegalityEngine constraints that
    prune the search space at the S4 gate.
    """

    def __init__(
        self,
        engine: LegalityEngine | None = None,
        state_dir: Path | None = None,
    ) -> None:
        self._engine = engine or LegalityEngine()
        self._state_dir = state_dir
        self._constraints: dict[str, DefectConstraint] = {}
        self._legality_registry = get_defect_registry()

        if state_dir:
            self._constraints_path = state_dir / "defect_constraints.json"
            self._load()

    @property
    def engine(self) -> LegalityEngine:
        return self._engine

    def _load(self) -> None:
        """Load persisted constraints from disk."""
        if not self._constraints_path.exists():
            return
        try:
            self._load_constraints_from_file()
        except Exception as exc:
            logger.warning("Failed to load defect constraints: %s", exc)

    def _load_constraints_from_file(self) -> None:
        """Load constraints from the JSON file."""
        with self._constraints_path.open("r") as f:
            data = json.load(f)
        for item in data:
            dc = DefectConstraint.from_dict(item)
            if not dc.revoked:
                self._constraints[dc.constraint_id] = dc
                self._engine.add_constraint(dc.constraint)
        logger.info("Loaded %d active defect constraints", len(self._constraints))

    def _persist(self) -> None:
        """Persist all constraints to disk."""
        if not self._state_dir:
            return
        self._state_dir.mkdir(parents=True, exist_ok=True)
        data = [dc.to_dict() for dc in self._constraints.values()]
        with self._constraints_path.open("w") as f:
            json.dump(data, f, indent=2)

    def record_defect(self, record: Record) -> list[DefectConstraint]:
        """Process a FAIL/QUARANTINE record into constraints.

        Args:
            record: A record with gate_verdict != PASS or quarantine=True

        Returns:
            List of newly created DefectConstraint objects
        """
        # Only process failed or quarantined records
        if (
            record.status.gate_verdict == GateVerdict.PASS_
            and not record.status.quarantine
        ):
            return []

        # Classify the record's defects using the legality engine
        hard_violations, soft_violations = self._engine.evaluate_record(
            record, ConstraintEnforcement.S4_EXPANSION
        )

        result = classify_record(record, hard_violations, soft_violations)
        new_constraints: list[DefectConstraint] = []

        # Convert void defects to constraints
        for void_defect in result.void_defects:
            constraint = self._void_to_constraint(void_defect, record)
            dc = DefectConstraint(
                constraint_id=constraint.constraint_id,
                defect_cause=FailureCause.INVALID_CONFIG,
                defect_class=void_defect.defect_class.value,
                cell_key=void_defect.cell_key,
                measurement_key=void_defect.conflicting_axes[0],
                constraint=constraint,
            )
            self._add(dc)
            new_constraints.append(dc)

        # Convert hard defects to constraints
        for hard_defect in result.hard_defects:
            constraint = self._violation_to_constraint(hard_defect, record)
            dc = DefectConstraint(
                constraint_id=constraint.constraint_id,
                defect_cause=record.status.cause,
                defect_class=hard_defect.defect_class.value,
                cell_key=hard_defect.cell_key,
                measurement_key=hard_defect.measurement_key,
                constraint=constraint,
            )
            self._add(dc)
            new_constraints.append(dc)

        # Convert soft defects to advisory constraints
        for soft_defect in result.soft_defects:
            constraint = self._violation_to_constraint(
                soft_defect, record, kind=ConstraintKind.SOFT
            )
            dc = DefectConstraint(
                constraint_id=constraint.constraint_id,
                defect_cause=record.status.cause,
                defect_class=soft_defect.defect_class.value
                if soft_defect.defect_class
                else "soft",
                cell_key=soft_defect.cell_key,
                measurement_key=soft_defect.measurement_key,
                constraint=constraint,
            )
            self._add(dc)
            new_constraints.append(dc)

        # Unclassified defects get a generic constraint
        for unclassified in result.unclassified_defects:
            constraint = self._unclassified_to_constraint(unclassified, record)
            dc = DefectConstraint(
                constraint_id=constraint.constraint_id,
                defect_cause=FailureCause.UNKNOWN,
                defect_class="unclassified",
                cell_key=unclassified.cell_key,
                measurement_key=unclassified.measurement_key,
                constraint=constraint,
            )
            self._add(dc)
            new_constraints.append(dc)

        if new_constraints:
            self._persist()
            logger.info(
                "Recorded %d defect constraints from cell %s (cause=%s)",
                len(new_constraints),
                record.cell_key[:12],
                record.status.cause.value,
            )

        return new_constraints

    def _void_to_constraint(self, void_defect, record: Record) -> Constraint:
        """Create a hard constraint from a void defect."""
        from computronium.experiment.legality.dsl import And, Eq, Var

        # Build expression: (axis_a == value_a) AND (axis_b == value_b) -> this combination is forbidden
        axis_a, axis_b = void_defect.conflicting_axes
        value_a, value_b = void_defect.conflicting_values
        expr = And(
            Eq(Var(f"coordinate.{axis_a}"), value_a),
            Eq(Var(f"coordinate.{axis_b}"), value_b),
        )

        return Constraint.create(
            expr=expr,
            origin=ConstraintOrigin.OBSERVED_DEFECT,
            scope=ConstraintScope.CELL,
            enforcement=ConstraintEnforcement.S4_EXPANSION,
            kind=ConstraintKind.HARD,
            description=f"Void: {axis_a}={value_a} incompatible with {axis_b}={value_b}",
            tags=frozenset(["void", void_defect.void_reason.value]),
        )

    def _violation_to_constraint(
        self, defect, record: Record, kind: ConstraintKind = ConstraintKind.HARD
    ) -> Constraint:
        """Create a constraint from a hard/soft defect violation."""
        from computronium.experiment.legality.dsl import Var

        # Use the violation's constraint expression if available
        if defect.constraint_violation:
            try:
                import json

                from computronium.experiment.legality.dsl import expr_from_json

                expr = expr_from_json(
                    json.loads(defect.constraint_violation.constraint_expr)
                )
                return Constraint.create(
                    expr=expr,
                    origin=ConstraintOrigin.OBSERVED_DEFECT,
                    scope=ConstraintScope.MEASUREMENT,
                    enforcement=ConstraintEnforcement.S4_EXPANSION,
                    kind=kind,
                    description=defect.description,
                    tags=frozenset(["defect", defect.defect_class.value]),
                )
            except Exception as exc:
                logger.debug(
                    "Failed to parse violation constraint expr: %s", exc
                )

        # Fallback: constrain the failing coordinate axis
        expr = Var(f"coordinate.{record.credit}")  # generic fallback
        return Constraint.create(
            expr=expr,
            origin=ConstraintOrigin.OBSERVED_DEFECT,
            scope=ConstraintScope.CELL,
            enforcement=ConstraintEnforcement.S4_EXPANSION,
            kind=kind,
            description=defect.description,
            tags=frozenset(["defect", "fallback"]),
        )

    def _unclassified_to_constraint(self, unclassified, record: Record) -> Constraint:
        """Create a soft advisory constraint from an unclassified defect."""
        from computronium.experiment.legality.dsl import Var

        expr = Var(f"coordinate.{record.credit}")
        return Constraint.create(
            expr=expr,
            origin=ConstraintOrigin.OBSERVED_DEFECT,
            scope=ConstraintScope.CELL,
            enforcement=ConstraintEnforcement.S4_EXPANSION,
            kind=ConstraintKind.SOFT,
            description=f"Unclassified: {unclassified.raw_message}",
            tags=frozenset(["unclassified"]),
        )

    def _add(self, dc: DefectConstraint) -> None:
        """Add a defect constraint to the registry and engine."""
        if dc.constraint_id in self._constraints:
            existing = self._constraints[dc.constraint_id]
            if not existing.revoked:
                return  # Already active
        self._constraints[dc.constraint_id] = dc
        self._engine.add_constraint(dc.constraint)

    def revoke(self, constraint_id: str, revoked_by: str = "user") -> bool:
        """Revoke a constraint by ID.

        Removes it from the engine and marks it revoked in the registry.
        """
        if constraint_id not in self._constraints:
            return False

        dc = self._constraints[constraint_id]
        if dc.revoked:
            return True  # Idempotent

        # Remove from engine
        self._engine.remove_constraint(dc.constraint_id)

        # Mark as revoked
        revoked_dc = DefectConstraint(
            constraint_id=dc.constraint_id,
            defect_cause=dc.defect_cause,
            defect_class=dc.defect_class,
            cell_key=dc.cell_key,
            measurement_key=dc.measurement_key,
            constraint=dc.constraint,
            author=dc.author,
            created_at=dc.created_at,
            revoked=True,
            revoked_at=time.time(),
            revoked_by=revoked_by,
        )
        self._constraints[constraint_id] = revoked_dc
        self._persist()
        logger.info("Revoked defect constraint %s", constraint_id)
        return True

    def list_constraints(self, include_revoked: bool = False) -> list[DefectConstraint]:
        """List all defect constraints."""
        constraints = list(self._constraints.values())
        if not include_revoked:
            constraints = [c for c in constraints if not c.revoked]
        return sorted(constraints, key=lambda c: c.created_at, reverse=True)

    def get_digest(self, store: RecordStore) -> dict[str, Any]:
        """Generate a human-readable digest of failure patterns.

        Uses evidence/failure.analyze_store_failures under the hood.
        """
        from computronium.experiment.evidence.failure import analyze_store_failures

        return analyze_store_failures(store)

    def get_constraints_for_task(self, task: str) -> list[DefectConstraint]:
        """Get constraints relevant to a specific task.

        Note: constraints are cell-scoped; this is a best-effort filter.
        """
        # Would need to query store for task-specific cells
        # For now, return all active constraints
        return [c for c in self._constraints.values() if not c.revoked]


def create_defect_registry(
    engine: LegalityEngine | None = None,
    state_dir: Path | None = None,
) -> DefectRegistry:
    """Factory for DefectRegistry."""
    return DefectRegistry(engine=engine, state_dir=state_dir)


__all__ = [
    "DefectConstraint",
    "DefectRegistry",
    "create_defect_registry",
]
