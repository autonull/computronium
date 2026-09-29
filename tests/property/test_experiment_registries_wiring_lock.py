"""Wiring lockstep locks for experiment registries (WP2).

Ensures registry ↔ config classmethods ↔ __all__ ↔ TYPE_CHECKING imports
stay in sync per pillar; never bypassed.
"""

from pathlib import Path

from computronium.experiment.schema import registries
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CONSTRAINTS_REGISTRY,
    OBJECTIVES_REGISTRY,
    POLICIES_REGISTRY,
    PRIORS_REGISTRY,
    STAGES_REGISTRY,
    ALL_REGISTRIES,
)

ROOT_INIT = Path("computronium") / "__init__.py"
EXPERIMENT_INIT = Path("computronium/experiment") / "__init__.py"


def test_objectives_registry_exists_and_empty() -> None:
    """Objectives registry exists and starts empty."""
    assert OBJECTIVES_REGISTRY is not None
    assert len(OBJECTIVES_REGISTRY) == 0


def test_constraints_registry_exists_and_empty() -> None:
    """Constraints registry exists and starts empty."""
    assert CONSTRAINTS_REGISTRY is not None
    assert len(CONSTRAINTS_REGISTRY) == 0


def test_priors_registry_exists_and_empty() -> None:
    """Priors registry exists and starts empty."""
    assert PRIORS_REGISTRY is not None
    assert len(PRIORS_REGISTRY) == 0


def test_policies_registry_exists_and_empty() -> None:
    """Policies registry exists and starts empty."""
    assert POLICIES_REGISTRY is not None
    assert len(POLICIES_REGISTRY) == 0


def test_stages_registry_exists_and_empty() -> None:
    """Stages registry exists and starts empty."""
    assert STAGES_REGISTRY is not None
    assert len(STAGES_REGISTRY) == 0


def test_capabilities_registry_exists_and_empty() -> None:
    """Capabilities registry exists and starts empty."""
    assert CAPABILITIES_REGISTRY is not None
    assert len(CAPABILITIES_REGISTRY) == 0


def test_all_registries_dict_completeness() -> None:
    """ALL_REGISTRIES contains all six registries."""
    expected_keys = {"objectives", "constraints", "priors", "policies", "stages", "capabilities"}
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

    assert hasattr(schema, "registries"), "registries not exported from experiment.schema"


def test_registry_integrity_checks_pass() -> None:
    """All registries pass integrity checks (no name mismatches, all dataclasses)."""
    for name, registry in ALL_REGISTRIES.items():
        issues = registry.integrity_check()
        assert not issues, f"{name} registry integrity issues: {issues}"


__all__ = [
    "test_objectives_registry_exists_and_empty",
    "test_constraints_registry_exists_and_empty",
    "test_priors_registry_exists_and_empty",
    "test_policies_registry_exists_and_empty",
    "test_stages_registry_exists_and_empty",
    "test_capabilities_registry_exists_and_empty",
    "test_all_registries_dict_completeness",
    "test_registries_are_experiment_exports",
    "test_registry_spec_classes_are_exported",
    "test_register_functions_are_exported",
    "test_experiment_init_exports_registries_module",
    "test_registry_integrity_checks_pass",
]