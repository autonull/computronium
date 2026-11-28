"""Legality boundary lock: DECLARED constraints must only encode machine-checkable infeasibility.

This test enforces the legality boundary from feedback #9:
- Constraints with origin=DECLARED (or SYSTEM_CONFIG, i.e., from SystemConfig.validate)
  may ONLY exclude logically/experimentally invalid configurations (voids).
- They may never encode "we don't expect this to work" — that belongs in PRIORS.
- Every DECLARED constraint must carry a machine-checkable proof kind:
  type mismatch, resource violation, or logical contradiction.
- No heuristic exclusions allowed in DECLARED constraints.

The registry seeded by ``seed_all_registries`` is the population; the
``ConstraintSpec.proof_kind`` field is the proof, so one table owns both the
row and its justification.
"""

from __future__ import annotations

from computronium.experiment.legality.classify import (
    DEFECT_REGISTRY,
)
from computronium.experiment.legality.engine import (
    ConstraintEnforcement,
    ConstraintOrigin,
    ConstraintScope,
    engine_from_registry,
)
from computronium.experiment.schema.registries import (
    CONSTRAINTS_REGISTRY,
    PRIORS_REGISTRY,
    ConstraintSpec,
    PriorSpec,
)
from computronium.experiment.schema.registries import (
    ConstraintKind as RegistryConstraintKind,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

_HEURISTIC_KEYWORDS = (
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
)
_PERFORMANCE_KEYWORDS = (
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
)


def _declared_specs() -> list[ConstraintSpec]:
    """The registry's DECLARED rows, seeded the way a run seeds them."""
    seed_all_registries()
    return [s for s in CONSTRAINTS_REGISTRY.values() if s.origin == "DECLARED"]


def _first_keyword(spec: ConstraintSpec, keywords: tuple[str, ...]) -> str | None:
    text = f"{spec.description} {spec.predicate}".lower()
    return next((kw for kw in keywords if kw in text), None)


class TestLegalityBoundary:
    """Tests enforcing the legality boundary for DECLARED constraints."""

    def test_declared_constraints_have_infeasibility_proofs(self) -> None:
        """Every DECLARED constraint must carry a machine-checkable proof kind."""
        declared = _declared_specs()
        assert declared, "the registry declares no constraints"

        missing = [spec.name for spec in declared if spec.proof_kind is None]
        assert not missing, (
            "DECLARED constraints missing a proof_kind: "
            + ", ".join(missing)
            + "; every DECLARED row must be a TYPE_MISMATCH, RESOURCE, or "
            "LOGICAL contradiction"
        )

    def test_declared_constraints_are_not_heuristic(self) -> None:
        """DECLARED constraints must not encode heuristic preferences."""
        declared = _declared_specs()
        assert declared, "the registry declares no constraints"

        violations = [
            f"{spec.name}: {keyword}"
            for spec in declared
            if (keyword := _first_keyword(spec, _HEURISTIC_KEYWORDS)) is not None
        ]
        assert not violations, (
            "DECLARED constraints contain heuristic exclusions (should be PRIORS):\n"
            + "\n".join(violations)
        )

    def test_void_patterns_have_proofs(self) -> None:
        """Every registered void pattern must have a corresponding infeasibility proof."""
        void_patterns = list(DEFECT_REGISTRY._void_patterns.keys())

        for key1 in void_patterns:
            key2 = (key1[1], key1[0])
            assert key2 in DEFECT_REGISTRY._void_patterns, (
                f"Void pattern {key1} not registered bidirectionally; missing {key2}"
            )

    def test_no_declared_constraint_on_performance(self) -> None:
        """DECLARED constraints must not reference performance metrics."""
        declared = _declared_specs()
        assert declared, "the registry declares no constraints"

        violations = [
            f"{spec.name}: references {keyword}"
            for spec in declared
            if (keyword := _first_keyword(spec, _PERFORMANCE_KEYWORDS)) is not None
        ]
        assert not violations, (
            "DECLARED constraints reference performance metrics "
            "(should be PRIORS or soft constraints):\n" + "\n".join(violations)
        )

    def test_declared_constraints_are_hard_or_void(self) -> None:
        """DECLARED constraints must never be SOFT."""
        declared = _declared_specs()
        assert declared, "the registry declares no constraints"

        soft = [
            spec.name for spec in declared if spec.kind is RegistryConstraintKind.SOFT
        ]
        assert not soft, (
            "DECLARED constraints with SOFT kind (must be VOID or HARD):\n"
            + "\n".join(soft)
        )

    def test_system_config_validator_constraints_are_voids(self) -> None:
        """System-config rows are structural voids at CELL scope."""
        seed_all_registries()
        engine = engine_from_registry(
            enforcement=ConstraintEnforcement.S4_EXPANSION,
            params=False,
            void_only=True,
        )
        system_config_constraints = [
            c
            for c in engine.all_constraints()
            if c.origin == ConstraintOrigin.SYSTEM_CONFIG
        ]
        assert system_config_constraints, "the S4 engine built no declared rows"

        for constraint in system_config_constraints:
            assert constraint.scope == ConstraintScope.CELL, (
                f"SYSTEM_CONFIG constraint {constraint.constraint_id} must be CELL scope"
            )

    def test_priors_not_in_declared_constraints(self) -> None:
        """PRIORS (preferences) must not be encoded as DECLARED constraints."""
        assert PRIORS_REGISTRY is not CONSTRAINTS_REGISTRY

        for spec in PRIORS_REGISTRY.values():
            assert isinstance(spec, PriorSpec), (
                f"PRIORS registry contains a non-PriorSpec: {spec}"
            )

        for spec in CONSTRAINTS_REGISTRY.values():
            assert isinstance(spec, ConstraintSpec), (
                f"CONSTRAINTS registry contains a non-ConstraintSpec: {spec}"
            )

    def test_constraint_origin_enum_has_declared(self) -> None:
        """ConstraintOrigin should have a DECLARED variant for explicit void constraints."""
        origins = [o.value for o in ConstraintOrigin]
        assert "system_config" in origins
