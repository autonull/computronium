"""Contrast Design for Design of Experiments (DOE).

Implements OFAT (One Factor At a Time) and fractional-factorial designs
with contrast_id, factor_assignments, matched_group for identifiability.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from computronium.experiment.schema.coordinate import DataOrigin


class ContrastDesignKind(StrEnum):
    """Contrast design types."""

    OFAT = "ofat"  # One Factor At a Time
    FRACTIONAL_FACTORIAL = "fractional_factorial"  # 2^(k-p) fractional factorial
    FULL_FACTORIAL = "full_factorial"  # Full 2^k factorial
    PLAKETT_BURMAN = "plackett_burman"  # Plackett-Burman design


@dataclass(frozen=True, slots=True)
class Factor:
    """Experimental factor definition."""

    name: str
    levels: tuple[Any, ...]  # Typically (low, high) for 2-level factors
    unit: str = ""

    def __post_init__(self) -> None:
        if len(self.levels) < 2:
            raise ValueError(f"Factor {self.name} must have at least 2 levels")


@dataclass(frozen=True, slots=True)
class ContrastAssignment:
    """A single contrast assignment mapping factors to levels.

    ``data_origin`` is the schema's own field for what the assignment *is*: the
    base condition is a control, a varied factor is a contrast. It rides on the
    assignment rather than being inferred from ``matched_group`` so that a
    record stamped from a design states its origin instead of having it
    reconstructed by a reader that happens to know the convention.
    """

    contrast_id: str
    factor_assignments: dict[str, Any]
    matched_group: str  # Group identifier for matched pairs/blocks
    data_origin: DataOrigin = DataOrigin.CONTRAST

    def to_dict(self) -> dict[str, Any]:
        return {
            "contrast_id": self.contrast_id,
            "factor_assignments": self.factor_assignments,
            "matched_group": self.matched_group,
            "data_origin": self.data_origin.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContrastAssignment:
        return cls(
            contrast_id=data["contrast_id"],
            factor_assignments=data["factor_assignments"],
            matched_group=data["matched_group"],
            data_origin=DataOrigin(data.get("data_origin", DataOrigin.CONTRAST)),
        )


@dataclass(frozen=True, slots=True)
class ContrastDesign:
    """A contrast design specifying DOE structure.

    Attributes:
        design_kind: Type of design (OFAT, fractional_factorial, etc.)
        factors: List of factors with their levels
        assignments: Generated contrast assignments
        resolution: Design resolution (III, IV, V, etc.)
        generators: Generator relations for fractional factorial
        metadata: Additional design metadata
    """

    design_kind: ContrastDesignKind
    factors: tuple[Factor, ...]
    assignments: tuple[ContrastAssignment, ...]
    resolution: str = ""
    generators: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.factors:
            raise ValueError("ContrastDesign must have at least one factor")
        if not self.assignments:
            raise ValueError("ContrastDesign must have at least one assignment")

    @property
    def n_factors(self) -> int:
        return len(self.factors)

    @property
    def n_runs(self) -> int:
        return len(self.assignments)

    def get_factor_names(self) -> tuple[str, ...]:
        return tuple(f.name for f in self.factors)

    def get_levels(self, factor_name: str) -> tuple[Any, ...]:
        for f in self.factors:
            if f.name == factor_name:
                return f.levels
        raise KeyError(f"Factor {factor_name} not found")

    def to_dict(self) -> dict[str, Any]:
        return {
            "design_kind": self.design_kind.value,
            "factors": [
                {"name": f.name, "levels": list(f.levels), "unit": f.unit}
                for f in self.factors
            ],
            "assignments": [a.to_dict() for a in self.assignments],
            "resolution": self.resolution,
            "generators": list(self.generators),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContrastDesign:
        factors = tuple(
            Factor(name=f["name"], levels=tuple(f["levels"]), unit=f.get("unit", ""))
            for f in data["factors"]
        )
        assignments = tuple(
            ContrastAssignment.from_dict(a) for a in data["assignments"]
        )
        return cls(
            design_kind=ContrastDesignKind(data["design_kind"]),
            factors=factors,
            assignments=assignments,
            resolution=data.get("resolution", ""),
            generators=tuple(data.get("generators", ())),
            metadata=data.get("metadata", {}),
        )


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _make_contrast_id(design_kind: ContrastDesignKind, index: int, seed: int) -> str:
    """Generate deterministic contrast_id."""
    payload = f"{design_kind.value}:{index}:{seed}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def create_ofat_design(
    factors: list[Factor],
    base_levels: dict[str, Any] | None = None,
    *,
    seed: int = 42,
) -> ContrastDesign:
    """Create a One-Factor-At-A-Time (OFAT) design.

    Varies one factor at a time from a base condition.
    Includes the base condition as a control.

    Args:
        factors: List of factors to vary
        base_levels: Base level for each factor (defaults to first level)
        seed: Random seed for deterministic contrast_id

    Returns:
        ContrastDesign with OFAT assignments
    """
    if not factors:
        raise ValueError("At least one factor required")

    base = base_levels or {f.name: f.levels[0] for f in factors}
    assignments = []

    # Base condition (control)
    assignments.append(
        ContrastAssignment(
            contrast_id=_make_contrast_id(ContrastDesignKind.OFAT, 0, seed),
            factor_assignments=base.copy(),
            matched_group="control",
        )
    )

    # OFAT: vary each factor. The varied assignments carry the group their
    # design names — ``ofat_<factor>`` — and the base condition above carries
    # ``control``, so a record stamped from one assignment is distinguishable
    # from a record stamped from the other. Before this, every assignment
    # reported ``matched_group == "contrast"`` and the control existed only as
    # an attribute of the assignment that no measurement ever received.
    idx = 1
    for factor in factors:
        for level in factor.levels[1:]:  # Skip base level
            assignment = base.copy()
            assignment[factor.name] = level
            assignments.append(
                ContrastAssignment(
                    contrast_id=_make_contrast_id(ContrastDesignKind.OFAT, idx, seed),
                    factor_assignments=assignment,
                    matched_group=f"ofat_{factor.name}",
                    data_origin=DataOrigin.CONTRAST,
                )
            )
            idx += 1

    control = assignments[0]
    assignments[0] = ContrastAssignment(
        contrast_id=control.contrast_id,
        factor_assignments=control.factor_assignments,
        matched_group=control.matched_group,
        data_origin=DataOrigin.CONTROL,
    )

    return ContrastDesign(
        design_kind=ContrastDesignKind.OFAT,
        factors=tuple(factors),
        assignments=tuple(assignments),
        resolution="II",
        metadata={"base_levels": base, "seed": seed},
    )


def create_fractional_factorial_design(
    factors: list[Factor],
    *,
    resolution: str = "IV",
    seed: int = 42,
) -> ContrastDesign:
    """Create a 2^(k-p) fractional factorial design.

    Args:
        factors: List of 2-level factors
        resolution: Target resolution (III, IV, V)
        seed: Random seed for deterministic generation

    Returns:
        ContrastDesign with fractional factorial assignments
    """
    if not factors:
        raise ValueError("At least one factor required")

    # Verify all factors are 2-level
    for f in factors:
        if len(f.levels) != 2:
            raise ValueError(
                f"Fractional factorial requires 2-level factors, "
                f"got {len(f.levels)} levels for {f.name}"
            )

    k = len(factors)

    # Standard generator tables for 2^(k-p) designs
    # Resolution IV designs for k=4..7
    generators_map = {
        4: {"IV": ("ABCD",)},  # 2^(4-1), I=ABCD
        5: {"IV": ("ABD", "ACE")},  # 2^(5-2), I=ABD=ACE=BCDE
        6: {"IV": ("ABCE", "ABDF")},  # 2^(6-2), I=ABCE=ABDF=CDEF
        7: {"IV": ("ABCD", "ABEF", "ACFG")},  # 2^(7-3)
    }

    if k <= 3:
        # Full factorial for k <= 3
        return create_full_factorial_design(factors, seed=seed)

    if k not in generators_map or resolution not in generators_map[k]:
        raise ValueError(f"No standard {resolution} design for k={k}")

    generators = generators_map[k][resolution]
    p = len(generators)
    n_runs = 2 ** (k - p)

    # Generate base design for first (k-p) factors
    base_factors = factors[: k - p]
    extra_factors = factors[k - p :]

    # Full factorial on base factors
    base_assignments = []
    for bits in itertools.product([0, 1], repeat=k - p):
        assignment = {
            f.name: f.levels[b] for f, b in zip(base_factors, bits, strict=True)
        }
        base_assignments.append(assignment)

    # Compute extra factor levels from generators
    assignments = _build_fractional_assignments(
        base_assignments, base_factors, extra_factors, generators, seed
    )

    return ContrastDesign(
        design_kind=ContrastDesignKind.FRACTIONAL_FACTORIAL,
        factors=tuple(factors),
        assignments=tuple(assignments),
        resolution=resolution,
        generators=generators,
        metadata={"k": k, "p": p, "n_runs": n_runs, "seed": seed},
    )


def _build_fractional_assignments(
    base_assignments: list[dict[str, Any]],
    base_factors: list[Factor],
    extra_factors: list[Factor],
    generators: tuple[str, ...],
    seed: int,
) -> tuple[ContrastAssignment, ...]:
    """Build assignments for fractional factorial design from base + generators."""
    assignments = []
    for i, base_assignment in enumerate(base_assignments):
        assignment = base_assignment.copy()
        for j, gen in enumerate(generators):
            extra_factor = extra_factors[j]
            level = 1
            for letter in gen:
                if letter.isalpha():
                    idx = ord(letter.upper()) - ord("A")
                    if idx < len(base_factors):
                        factor_name = base_factors[idx].name
                        val = base_assignment[factor_name]
                        level *= 1 if val == base_factors[idx].levels[1] else -1
            assignment[extra_factor.name] = (
                extra_factor.levels[1] if level > 0 else extra_factor.levels[0]
            )
        assignments.append(
            ContrastAssignment(
                contrast_id=_make_contrast_id(
                    ContrastDesignKind.FRACTIONAL_FACTORIAL, i, seed
                ),
                factor_assignments=assignment,
                matched_group=f"run_{i}",
            )
        )
    return tuple(assignments)


def create_full_factorial_design(
    factors: list[Factor],
    *,
    seed: int = 42,
) -> ContrastDesign:
    """Create a full factorial design (2^k for 2-level factors).

    Args:
        factors: List of factors
        seed: Random seed for deterministic contrast_id

    Returns:
        ContrastDesign with full factorial assignments
    """
    if not factors:
        raise ValueError("At least one factor required")

    assignments = []

    # Generate all combinations
    factor_names = [f.name for f in factors]
    factor_levels = [f.levels for f in factors]

    for i, combo in enumerate(itertools.product(*factor_levels)):
        assignment = dict(zip(factor_names, combo, strict=True))
        assignments.append(
            ContrastAssignment(
                contrast_id=_make_contrast_id(
                    ContrastDesignKind.FULL_FACTORIAL, i, seed
                ),
                factor_assignments=assignment,
                matched_group=f"run_{i}",
            )
        )

    return ContrastDesign(
        design_kind=ContrastDesignKind.FULL_FACTORIAL,
        factors=tuple(factors),
        assignments=tuple(assignments),
        resolution="full",
        metadata={"n_runs": len(assignments), "seed": seed},
    )


def create_plackett_burman_design(
    factors: list[Factor],
    *,
    seed: int = 42,
) -> ContrastDesign:
    """Create a Plackett-Burman design for screening.

    Args:
        factors: List of 2-level factors (n <= 11 for standard 12-run design)
        seed: Random seed

    Returns:
        ContrastDesign with Plackett-Burman assignments
    """
    if not factors:
        raise ValueError("At least one factor required")

    k = len(factors)
    if k > 11:
        raise ValueError("Standard Plackett-Burman supports up to 11 factors")

    # Standard 12-run Plackett-Burman first row
    # For 11 factors in 12 runs
    pb_first_row = (
        1,
        1,
        1,
        -1,
        1,
        -1,
        -1,
        -1,
        1,
        -1,
        1,
        -1,
    )

    # Generate cyclic shifts
    assignments = []

    for run in range(12):
        row = pb_first_row[run:] + pb_first_row[:run]
        assignment = {}
        for i, factor in enumerate(factors):
            if i < len(row):
                level = factor.levels[1] if row[i] > 0 else factor.levels[0]
            else:
                level = factor.levels[0]
            assignment[factor.name] = level
        assignments.append(
            ContrastAssignment(
                contrast_id=_make_contrast_id(
                    ContrastDesignKind.PLAKETT_BURMAN, run, seed
                ),
                factor_assignments=assignment,
                matched_group=f"pb_run_{run}",
            )
        )

    return ContrastDesign(
        design_kind=ContrastDesignKind.PLAKETT_BURMAN,
        factors=tuple(factors),
        assignments=tuple(assignments),
        resolution="III",
        metadata={"n_runs": 12, "seed": seed},
    )


def create_contrast_design(
    kind: ContrastDesignKind,
    factors: list[Factor],
    **kwargs: Any,
) -> ContrastDesign:
    """Factory function to create contrast designs.

    Args:
        kind: Design type
        factors: Experimental factors
        **kwargs: Additional arguments passed to specific design function

    Returns:
        ContrastDesign instance
    """
    match kind:
        case ContrastDesignKind.OFAT:
            return create_ofat_design(factors, **kwargs)
        case ContrastDesignKind.FRACTIONAL_FACTORIAL:
            return create_fractional_factorial_design(factors, **kwargs)
        case ContrastDesignKind.FULL_FACTORIAL:
            return create_full_factorial_design(factors, **kwargs)
        case ContrastDesignKind.PLAKETT_BURMAN:
            return create_plackett_burman_design(factors, **kwargs)
        case _:
            raise ValueError(f"Unknown contrast design kind: {kind}")


__all__ = [
    "ContrastAssignment",
    "ContrastDesign",
    "ContrastDesignKind",
    "Factor",
    "create_contrast_design",
    "create_fractional_factorial_design",
    "create_full_factorial_design",
    "create_ofat_design",
    "create_plackett_burman_design",
]
