"""Wiring lockstep locks for experiment registries (WP2).

Ensures registry ↔ config classmethods ↔ __all__ ↔ TYPE_CHECKING imports
stay in sync per pillar; never bypassed.

After WP8/WP9 completion, registries are seeded with domain data:
- OBJECTIVES: ~39 objectives (task, cost, substrate, ruler, stability, plasticity)
- CONSTRAINTS: 17 constraints (void, hard, fairness, operating_point)
- PRIORS: 28 priors (ruler LR, step-size overrides, dynamics step-sizes)
- POLICIES: 9 policies (8 catalog + 1 TPE/GP variant)
- STAGES: 11 stages (S1_FRAME...S11_REPORT)
- CAPABILITIES: 88 capabilities (C1-C88)
"""

from pathlib import Path

from computronium.experiment.schema.registries import (
    ALL_REGISTRIES,
    CAPABILITIES_REGISTRY,
    CONSTRAINTS_REGISTRY,
    OBJECTIVES_REGISTRY,
    POLICIES_REGISTRY,
    PRIORS_REGISTRY,
    STAGES_REGISTRY,
)
from computronium.experiment.schema.seed_registries import seed_all_registries

ROOT_INIT = Path("computronium") / "__init__.py"
EXPERIMENT_INIT = Path("computronium/experiment") / "__init__.py"


def _seed_registries() -> None:
    """Seed registries for testing."""
    seed_all_registries()


def test_objectives_registry_seeded() -> None:
    """Objectives registry exists and is seeded with the full B.7 union.

    TODO51 added the four objectives the new measurements back
    (stability_margin, nonnormality, energy_per_mac, macs_per_step), so the
    count is a floor on the union, not a frozen tally.
    """
    _seed_registries()
    assert OBJECTIVES_REGISTRY is not None
    assert len(OBJECTIVES_REGISTRY) >= 36  # Full B.7 union + TODO51 additions


def test_constraints_registry_seeded() -> None:
    """Constraints registry exists and is seeded with 17 constraints."""
    _seed_registries()
    assert CONSTRAINTS_REGISTRY is not None
    assert len(CONSTRAINTS_REGISTRY) >= 17  # Void, hard, fairness, operating_point


def test_priors_registry_seeded() -> None:
    """Priors registry exists and is seeded with 28 priors."""
    _seed_registries()
    assert PRIORS_REGISTRY is not None
    assert len(PRIORS_REGISTRY) >= 28  # Ruler LR + step-size + dynamics


def test_policies_registry_seeded() -> None:
    """Policies registry exists and is seeded with 9 policies."""
    _seed_registries()
    assert POLICIES_REGISTRY is not None
    assert len(POLICIES_REGISTRY) >= 9  # Eight catalog + variants


def test_stages_registry_seeded() -> None:
    """Stages registry exists and is seeded with 11 canonical stages."""
    _seed_registries()
    assert STAGES_REGISTRY is not None
    assert len(STAGES_REGISTRY) == 11  # S1_FRAME...S11_REPORT


def test_capabilities_registry_seeded() -> None:
    """Capabilities registry exists and is seeded with 88 capabilities."""
    _seed_registries()
    assert CAPABILITIES_REGISTRY is not None
    assert len(CAPABILITIES_REGISTRY) == 88  # C1-C88


def test_all_registries_dict_completeness() -> None:
    """ALL_REGISTRIES contains all six registries."""
    expected_keys = {
        "objectives",
        "constraints",
        "priors",
        "policies",
        "stages",
        "capabilities",
    }
    assert set(ALL_REGISTRIES.keys()) == expected_keys
    for key, registry in ALL_REGISTRIES.items():
        assert registry is not None


def test_registries_are_experiment_exports() -> None:
    """All registries are exported from experiment.schema.registries."""
    from computronium.experiment.schema import registries as reg_module

    for name in [
        "OBJECTIVES_REGISTRY",
        "CONSTRAINTS_REGISTRY",
        "PRIORS_REGISTRY",
        "POLICIES_REGISTRY",
        "STAGES_REGISTRY",
        "CAPABILITIES_REGISTRY",
        "ALL_REGISTRIES",
    ]:
        assert hasattr(reg_module, name), f"{name} not exported from registries module"


def test_registry_spec_classes_are_exported() -> None:
    """Registry spec classes are exported."""
    from computronium.experiment.schema import registries as reg_module

    for name in [
        "ObjectiveSpec",
        "ConstraintSpec",
        "PriorSpec",
        "PolicySpec",
        "StageSpec",
        "CapabilitySpec",
        "PolicyKind",
        "StageId",
        "CapabilityKind",
    ]:
        assert hasattr(reg_module, name), f"{name} not exported from registries module"


def test_register_functions_are_exported() -> None:
    """Register functions are exported."""
    from computronium.experiment.schema import registries as reg_module

    for name in [
        "register_objective",
        "register_constraint",
        "register_prior",
        "register_policy",
        "register_stage",
        "register_capability",
    ]:
        assert hasattr(reg_module, name), f"{name} not exported from registries module"


def test_experiment_init_exports_registries_module() -> None:
    """experiment/__init__.py exports the registries module."""
    from computronium.experiment import schema

    assert hasattr(schema, "registries"), (
        "registries not exported from experiment.schema"
    )


def test_registry_integrity_checks_pass() -> None:
    """All registries pass integrity checks (no name mismatches, all dataclasses)."""
    for name, registry in ALL_REGISTRIES.items():
        issues = registry.integrity_check()
        assert not issues, f"{name} registry integrity issues: {issues}"


__all__ = [
    "test_all_registries_dict_completeness",
    "test_capabilities_registry_seeded",
    "test_constraints_registry_seeded",
    "test_experiment_init_exports_registries_module",
    "test_objectives_registry_seeded",
    "test_policies_registry_seeded",
    "test_priors_registry_seeded",
    "test_register_functions_are_exported",
    "test_registries_are_experiment_exports",
    "test_registry_integrity_checks_pass",
    "test_registry_spec_classes_are_exported",
    "test_stages_registry_seeded",
]
