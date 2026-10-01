"""Constraint classification and void/defect taxonomy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.legality.engine import ConstraintViolation
    from computronium.experiment.schema.record import Record


class DefectClass(StrEnum):
    """Defect classification taxonomy (void/defect taxonomy as registry data)."""

    # Void defects - fundamental incompatibilities
    VOID_DYNAMICS_CREDIT = "void_dynamics_credit"
    VOID_PLASTICITY_CREDIT = "void_plasticity_credit"
    VOID_SUBSTRATE_GEOMETRY = "void_substrate_geometry"
    VOID_SUBSTRATE_DYNAMICS = "void_substrate_dynamics"
    VOID_GEOMETRY_DYNAMICS = "void_geometry_dynamics"

    # Hard defects - constraint violations
    HARD_NUMERICAL = "hard_numerical"
    HARD_TIMEOUT = "hard_timeout"
    HARD_OOM = "hard_oom"
    HARD_INVALID_CONFIG = "hard_invalid_config"
    HARD_RUNTIME_ERROR = "hard_runtime_error"
    HARD_CONSTRAINT_VIOLATION = "hard_constraint_violation"
    HARD_DIVERGENCE = "hard_divergence"

    # Soft defects - warnings
    SOFT_DEGRADATION = "soft_degradation"
    SOFT_INSTABILITY = "soft_instability"
    SOFT_RESOURCE_WARNING = "soft_resource_warning"

    # Unclassified bucket (always counted)
    UNCLASSIFIED = "unclassified"


class VoidReason(StrEnum):
    """Reason for void classification."""

    INCOMPATIBLE_DYNAMICS_CREDIT = "incompatible_dynamics_credit"
    INCOMPATIBLE_PLASTICITY_CREDIT = "incompatible_plasticity_credit"
    INCOMPATIBLE_SUBSTRATE_GEOMETRY = "incompatible_substrate_geometry"
    INCOMPATIBLE_SUBSTRATE_DYNAMICS = "incompatible_substrate_dynamics"
    INCOMPATIBLE_GEOMETRY_DYNAMICS = "incompatible_geometry_dynamics"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class VoidDefect:
    """A void defect - fundamental incompatibility that makes a cell invalid."""

    defect_class: DefectClass
    void_reason: VoidReason
    cell_key: str
    conflicting_axes: tuple[str, str]  # e.g., ("dynamics", "credit")
    conflicting_values: tuple[str, str]  # e.g., ("ep", "hebbian")
    description: str = ""


@dataclass(frozen=True, slots=True)
class HardDefect:
    """A hard defect - constraint violation that blocks execution."""

    defect_class: DefectClass
    constraint_violation: ConstraintViolation
    record_id: str
    cell_key: str
    measurement_key: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class SoftDefect:
    """A soft defect - warning that doesn't block execution."""

    defect_class: DefectClass
    constraint_violation: ConstraintViolation | None
    record_id: str
    cell_key: str
    measurement_key: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class UnclassifiedDefect:
    """An unclassified defect - counted but not categorized."""

    record_id: str
    cell_key: str
    measurement_key: str
    raw_message: str
    description: str = ""


Defect = VoidDefect | HardDefect | SoftDefect | UnclassifiedDefect


class DefectRegistry:
    """Registry of known defect patterns for classification.

    Void/defect taxonomy as registry data; unclassified bucket counted.
    """

    def __init__(self) -> None:
        self._void_patterns: dict[tuple[str, str], tuple[DefectClass, VoidReason]] = {}
        self._unclassified_count = 0

    def register_void_pattern(
        self,
        axis_a: str,
        value_a: str,
        axis_b: str,
        value_b: str,
        defect_class: DefectClass,
        void_reason: VoidReason,
    ) -> None:
        """Register a known void pattern (bidirectional)."""
        key1 = (f"{axis_a}.{value_a}", f"{axis_b}.{value_b}")
        key2 = (f"{axis_b}.{value_b}", f"{axis_a}.{value_a}")
        self._void_patterns[key1] = (defect_class, void_reason)
        self._void_patterns[key2] = (defect_class, void_reason)

    def classify_void(
        self, axis_a: str, value_a: str, axis_b: str, value_b: str
    ) -> tuple[DefectClass, VoidReason] | None:
        """Check if a combination is a known void."""
        key = (f"{axis_a}.{value_a}", f"{axis_b}.{value_b}")
        return self._void_patterns.get(key)

    def increment_unclassified(self) -> None:
        """Increment the unclassified counter."""
        self._unclassified_count += 1

    def get_unclassified_count(self) -> int:
        """Get the count of unclassified defects."""
        return self._unclassified_count


# Global defect registry
DEFECT_REGISTRY = DefectRegistry()

# Register known void patterns (from SystemConfig.validate migrations)
# Dynamics-Credit voids
DEFECT_REGISTRY.register_void_pattern(
    "dynamics",
    "ep",
    "credit",
    "hebbian",
    DefectClass.VOID_DYNAMICS_CREDIT,
    VoidReason.INCOMPATIBLE_DYNAMICS_CREDIT,
)
DEFECT_REGISTRY.register_void_pattern(
    "dynamics",
    "ep",
    "credit",
    "fa",
    DefectClass.VOID_DYNAMICS_CREDIT,
    VoidReason.INCOMPATIBLE_DYNAMICS_CREDIT,
)
DEFECT_REGISTRY.register_void_pattern(
    "dynamics",
    "sparse_ep",
    "credit",
    "hebbian",
    DefectClass.VOID_DYNAMICS_CREDIT,
    VoidReason.INCOMPATIBLE_DYNAMICS_CREDIT,
)

# Plasticity-Credit voids
DEFECT_REGISTRY.register_void_pattern(
    "plasticity",
    "hebbian",
    "credit",
    "fa",
    DefectClass.VOID_PLASTICITY_CREDIT,
    VoidReason.INCOMPATIBLE_PLASTICITY_CREDIT,
)

# Substrate-Geometry voids
DEFECT_REGISTRY.register_void_pattern(
    "substrate",
    "analog",
    "geometry",
    "mlp",
    DefectClass.VOID_SUBSTRATE_GEOMETRY,
    VoidReason.INCOMPATIBLE_SUBSTRATE_GEOMETRY,
)
DEFECT_REGISTRY.register_void_pattern(
    "substrate",
    "digital",
    "geometry",
    "crossbar",
    DefectClass.VOID_SUBSTRATE_GEOMETRY,
    VoidReason.INCOMPATIBLE_SUBSTRATE_GEOMETRY,
)

# Substrate-Dynamics voids
DEFECT_REGISTRY.register_void_pattern(
    "substrate",
    "analog",
    "dynamics",
    "ep",
    DefectClass.VOID_SUBSTRATE_DYNAMICS,
    VoidReason.INCOMPATIBLE_SUBSTRATE_DYNAMICS,
)
DEFECT_REGISTRY.register_void_pattern(
    "substrate",
    "digital",
    "dynamics",
    "sparse_ep",
    DefectClass.VOID_SUBSTRATE_DYNAMICS,
    VoidReason.INCOMPATIBLE_SUBSTRATE_DYNAMICS,
)

# Geometry-Dynamics voids
DEFECT_REGISTRY.register_void_pattern(
    "geometry",
    "mlp",
    "dynamics",
    "sparse_ep",
    DefectClass.VOID_GEOMETRY_DYNAMICS,
    VoidReason.INCOMPATIBLE_GEOMETRY_DYNAMICS,
)
DEFECT_REGISTRY.register_void_pattern(
    "geometry",
    "crossbar",
    "dynamics",
    "ep",
    DefectClass.VOID_GEOMETRY_DYNAMICS,
    VoidReason.INCOMPATIBLE_GEOMETRY_DYNAMICS,
)


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    """Result of classifying a record's defects."""

    void_defects: tuple[VoidDefect, ...]
    hard_defects: tuple[HardDefect, ...]
    soft_defects: tuple[SoftDefect, ...]
    unclassified_defects: tuple[UnclassifiedDefect, ...]

    @property
    def all_defects(self) -> tuple[Defect, ...]:
        return (
            self.void_defects
            + self.hard_defects
            + self.soft_defects
            + self.unclassified_defects
        )

    @property
    def has_void(self) -> bool:
        return bool(self.void_defects)

    @property
    def has_hard(self) -> bool:
        return bool(self.hard_defects)

    @property
    def total_count(self) -> int:
        return len(self.all_defects)

    @property
    def unclassified_count(self) -> int:
        return len(self.unclassified_defects)


def classify_record(
    record: Record,
    hard_violations: list[ConstraintViolation],
    soft_violations: list[ConstraintViolation],
) -> ClassificationResult:
    """Classify all defects for a record.

    Args:
        record: The record to classify
        hard_violations: Hard constraint violations from engine
        soft_violations: Soft constraint violations from engine

    Returns:
        ClassificationResult with categorized defects
    """
    void_defects: list[VoidDefect] = []
    hard_defects: list[HardDefect] = []
    soft_defects: list[SoftDefect] = []
    unclassified_defects: list[UnclassifiedDefect] = []

    # Check for void defects (axis incompatibilities)
    axes = [
        ("substrate", record.substrate),
        ("geometry", record.geometry),
        ("dynamics", record.dynamics),
        ("plasticity", record.plasticity),
        ("credit", record.credit),
        ("update", record.update),
    ]

    for i, (axis_a, value_a) in enumerate(axes):
        for axis_b, value_b in axes[i + 1 :]:
            result = DEFECT_REGISTRY.classify_void(axis_a, value_a, axis_b, value_b)
            if result:
                defect_class, void_reason = result
                void_defects.append(
                    VoidDefect(
                        defect_class=defect_class,
                        void_reason=void_reason,
                        cell_key=record.cell_key,
                        conflicting_axes=(axis_a, axis_b),
                        conflicting_values=(value_a, value_b),
                        description=f"Void: {axis_a}={value_a} incompatible with {axis_b}={value_b}",
                    )
                )

    # Classify hard violations
    for violation in hard_violations:
        # Try to map to known defect class
        defect_class = _map_violation_to_defect_class(violation)
        if defect_class and defect_class != DefectClass.UNCLASSIFIED:
            hard_defects.append(
                HardDefect(
                    defect_class=defect_class,
                    constraint_violation=violation,
                    record_id=record.record_id,
                    cell_key=record.cell_key,
                    measurement_key=record.measurement_key,
                    description=violation.message,
                )
            )
        else:
            # Unclassified
            DEFECT_REGISTRY.increment_unclassified()
            unclassified_defects.append(
                UnclassifiedDefect(
                    record_id=record.record_id,
                    cell_key=record.cell_key,
                    measurement_key=record.measurement_key,
                    raw_message=violation.message,
                    description="Unclassified hard violation",
                )
            )

    # Classify soft violations
    for violation in soft_violations:
        defect_class = _map_violation_to_defect_class(violation)
        if defect_class and defect_class != DefectClass.UNCLASSIFIED:
            soft_defects.append(
                SoftDefect(
                    defect_class=defect_class,
                    constraint_violation=violation,
                    record_id=record.record_id,
                    cell_key=record.cell_key,
                    measurement_key=record.measurement_key,
                    description=violation.message,
                )
            )
        else:
            DEFECT_REGISTRY.increment_unclassified()
            unclassified_defects.append(
                UnclassifiedDefect(
                    record_id=record.record_id,
                    cell_key=record.cell_key,
                    measurement_key=record.measurement_key,
                    raw_message=violation.message,
                    description="Unclassified soft violation",
                )
            )

    return ClassificationResult(
        void_defects=tuple(void_defects),
        hard_defects=tuple(hard_defects),
        soft_defects=tuple(soft_defects),
        unclassified_defects=tuple(unclassified_defects),
    )


def _map_violation_to_defect_class(  # ruff: ignore[complex-structure, too-many-return-statements] - classifier with many patterns
    violation: ConstraintViolation,
) -> DefectClass | None:
    """Map a constraint violation to a defect class."""
    msg = violation.message.lower()
    expr_str = violation.constraint_expr.lower()

    # Numerical issues
    if any(kw in msg for kw in ("nan", "inf", "overflow", "underflow", "numerical")):
        return DefectClass.HARD_NUMERICAL

    # Timeout
    if "timeout" in msg or "time out" in msg:
        return DefectClass.HARD_TIMEOUT

    # OOM
    if "oom" in msg or "out of memory" in msg or "memory" in msg:
        return DefectClass.HARD_OOM

    # Invalid config
    if any(kw in msg for kw in ("invalid config", "invalid parameter", "bad config")):
        return DefectClass.HARD_INVALID_CONFIG

    # Runtime error
    if any(kw in msg for kw in ("runtime error", "exception", "error:", "traceback")):
        return DefectClass.HARD_RUNTIME_ERROR

    # Constraint violation
    if "constraint" in msg or "violation" in expr_str:
        return DefectClass.HARD_CONSTRAINT_VIOLATION

    # Divergence
    if "diverg" in msg or "explod" in msg:
        return DefectClass.HARD_DIVERGENCE

    # Soft warnings
    if "degrad" in msg:
        return DefectClass.SOFT_DEGRADATION
    if "instab" in msg:
        return DefectClass.SOFT_INSTABILITY
    if "resource" in msg or "budget" in msg:
        return DefectClass.SOFT_RESOURCE_WARNING

    return None


def get_defect_registry() -> DefectRegistry:
    """Get the global defect registry."""
    return DEFECT_REGISTRY


__all__ = [
    "DEFECT_REGISTRY",
    "ClassificationResult",
    "Defect",
    "DefectClass",
    "DefectRegistry",
    "HardDefect",
    "SoftDefect",
    "UnclassifiedDefect",
    "VoidDefect",
    "VoidReason",
    "classify_record",
    "get_defect_registry",
]
