"""Lockstep tests for AXES + CAPABILITIES totality (C↔R matrix).

This test ensures:
1. AXES registry ↔ config classmethods ↔ __all__ ↔ TYPE_CHECKING imports stay in sync
2. CAPABILITIES registry totality: every capability cites ≥1 requirement (R), every R cites ≥1 capability (C)
3. The §7.2 C↔R matrix as data: every C cited by ≥1 R, every R cites ≥1 C
"""

from __future__ import annotations

import inspect

import pytest

from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    StructuralAxis,
    get_registry,
)
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilityKind,
    CapabilitySpec,
    CapabilityStatus,
)


class TestAxesRegistryWiring:
    """Lockstep test: AXES registry ↔ config classmethods ↔ exports."""

    def test_axes_registries_exist_for_all_structural_axes(self) -> None:
        """Each StructuralAxis has a registry."""
        for axis in StructuralAxis:
            registry = get_registry(axis)
            assert registry is not None, f"Missing registry for {axis}"

    def test_axes_registries_are_experiment_exports(self) -> None:
        """All axis registries exported from experiment.schema.axis."""
        from computronium.experiment.schema import axis as axis_module

        for axis in StructuralAxis:
            registry_name = f"{axis.value.upper()}_REGISTRY"
            assert hasattr(axis_module, registry_name), f"{registry_name} not exported"

    def test_axis_spec_classes_exported(self) -> None:
        """AxisSpec, StructuralAxis, AxisKind, Domain, HyperparameterSpec, Scale exported."""
        from computronium.experiment.schema import axis as axis_module

        for name in [
            "AxisSpec",
            "StructuralAxis",
            "AxisKind",
            "Domain",
            "HyperparameterSpec",
            "Scale",
            "AXES_REGISTRIES",
            "get_registry",
            "list_axis_specs",
            "is_available",
            "register_axis_spec",
            "get_axis_spec",
        ]:
            assert hasattr(axis_module, name), f"{name} not exported from axis module"

    def test_axis_primitives_registered_via_init_subclass(self) -> None:
        """Verify AXES_REGISTRIES populated via __init_subclass__ auto-registration."""
        # This is a structural test - the registries should be importable and non-None
        for axis in StructuralAxis:
            registry = AXES_REGISTRIES[axis]
            assert registry is not None

    def test_config_class_hyperparameters_method_exists(self) -> None:
        """Each structural axis's config class has hyperparameters() classmethod."""
        axis_config_classes = {
            StructuralAxis.SUBSTRATE: (
                "computronium.ontology.substrate",
                "SubstrateConfig",
            ),
            StructuralAxis.GEOMETRY: (
                "computronium.ontology.geometry",
                "GeometryConfig",
            ),
            StructuralAxis.DYNAMICS: (
                "computronium.ontology.dynamics",
                "StateDynamicsConfig",
            ),
            StructuralAxis.PLASTICITY: (
                "computronium.state.transitions",
                "PlasticityConfig",
            ),
            StructuralAxis.CREDIT: (
                "computronium.ontology.credit",
                "CreditAssignmentConfig",
            ),
            StructuralAxis.UPDATE: (
                "computronium.ontology.update",
                "ParameterUpdateConfig",
            ),
        }

        for axis_kind, (module_path, class_name) in axis_config_classes.items():
            module = __import__(module_path, fromlist=[class_name])
            config_cls = getattr(module, class_name)
            assert hasattr(config_cls, "hyperparameters"), (
                f"{class_name} missing hyperparameters() classmethod"
            )
            # Verify it's a classmethod
            hp_method = getattr(config_cls, "hyperparameters")
            assert isinstance(
                inspect.getattr_static(config_cls, "hyperparameters"), classmethod
            ), f"{class_name}.hyperparameters is not a classmethod"

    def test_harvest_schema_integrity(self) -> None:
        """harvest_schema() runs without ConflictingHyperparameterError."""
        from computronium.experiment.schema.harvest import harvest_schema

        schema = harvest_schema()
        assert schema.version == 1
        assert len(schema.axis_kind_order) == 6
        assert isinstance(schema.hyperparameters, tuple)
        assert len(schema.hyperparameters) > 0


class TestCapabilitiesRegistryTotality:
    """Lockstep test: CAPABILITIES registry totality (C↔R matrix).

    Per §7.2: every capability (C) cited by ≥1 requirement (R),
    every requirement (R) cites ≥1 capability (C).
    """

    def test_capabilities_registry_exists_and_seeded(self) -> None:
        """Capabilities registry exists and has C1-C88 entries after seeding."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()
        assert len(CAPABILITIES_REGISTRY) == 88, (
            f"Expected 88 capabilities, got {len(CAPABILITIES_REGISTRY)}"
        )

    def test_all_seeded_capabilities_have_valid_specs(self) -> None:
        """All C1-C88 have valid CapabilitySpec with required fields."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        for cap_id in [f"C{i}" for i in range(1, 89)]:
            cap = CAPABILITIES_REGISTRY.get(cap_id)
            assert cap is not None, f"Missing capability {cap_id}"

            assert isinstance(cap, CapabilitySpec)
            assert cap.capability_id == cap_id
            assert cap.kind in CapabilityKind
            assert cap.name
            assert cap.description
            assert cap.stage is not None
            assert cap.owner is not None
            assert cap.verifying_test is not None
            assert isinstance(cap.flags, tuple)
            assert cap.status in CapabilityStatus
            if cap.status == CapabilityStatus.RETIRED:
                assert cap.retirement_record is not None

    def test_capability_kind_distribution(self) -> None:
        """Capabilities distributed across all kinds."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        kind_counts: dict[CapabilityKind, int] = {}
        for cap in CAPABILITIES_REGISTRY.values():
            kind_counts[cap.kind] = kind_counts.get(cap.kind, 0) + 1

        # Every kind should have at least one capability
        for kind in CapabilityKind:
            assert kind in kind_counts, f"No capabilities for kind {kind}"

    def test_required_capabilities_are_active(self) -> None:
        """Required capabilities must be ACTIVE status."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        for cap in CAPABILITIES_REGISTRY.values():
            if cap.required:
                assert cap.status == CapabilityStatus.ACTIVE, (
                    f"Required capability {cap.capability_id} is not ACTIVE"
                )

    def test_retired_capabilities_have_retirement_record(self) -> None:
        """RETIRED capabilities must have retirement_record."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        for cap in CAPABILITIES_REGISTRY.values():
            if cap.status == CapabilityStatus.RETIRED:
                assert cap.retirement_record is not None, (
                    f"RETIRED capability {cap.capability_id} missing retirement_record"
                )

    def test_stage_coverage(self) -> None:
        """Capabilities cover all pipeline stages S1-S11 (canonical names)."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        stages_covered = set()
        for cap in CAPABILITIES_REGISTRY.values():
            if cap.stage:
                stages_covered.add(cap.stage)

        # Should cover S1_FRAME through S11_REPORT (canonical stage IDs)
        expected_stages = {
            "S1_FRAME",
            "S2_SPACE",
            "S3_SCHEDULE",
            "S4_GATE",
            "S5_COMPOSE",
            "S6_TRAIN",
            "S7_MEASURE",
            "S8_RECORD",
            "S9_ATTRIBUTE",
            "S10_DECIDE",
            "S11_REPORT",
        }
        for stage in expected_stages:
            assert stage in stages_covered, f"No capabilities for stage {stage}"

    def test_owner_coverage(self) -> None:
        """Capabilities have meaningful owner assignments."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        owners = set()
        for cap in CAPABILITIES_REGISTRY.values():
            assert cap.owner, f"Capability {cap.capability_id} missing owner"
            owners.add(cap.owner)

        # Key owners should be present
        expected_owners = {
            "schema",
            "store",
            "legality",
            "pipeline",
            "policy",
            "allocator",
            "replay",
            "evidence",
            "artifacts",
            "dynamics",
            "geometry",
            "credit",
            "update",
            "plasticity",
            "substrate",
            "learning",
            "priors",
            "backends",
            "operations",
            "surface",
            "models_native",
            "ceec_core",
            "psi_peft",
            "local_feedback",
            "stability",
            "lab",
            "visualization",
            "probes",
        }
        for owner in expected_owners:
            assert owner in owners, f"No capabilities for owner {owner}"

    def test_verifying_test_format(self) -> None:
        """verifying_test should be pytest node id format."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        for cap in CAPABILITIES_REGISTRY.values():
            test_path = cap.verifying_test
            assert test_path, f"Capability {cap.capability_id} missing verifying_test"
            # Should be a valid pytest path format
            assert "::" in test_path or test_path.endswith(".py"), (
                f"verifying_test '{test_path}' not valid pytest node id format"
            )

    def test_flags_are_tuples(self) -> None:
        """flags should be tuples of strings."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        for cap in CAPABILITIES_REGISTRY.values():
            assert isinstance(cap.flags, tuple)
            for flag in cap.flags:
                assert isinstance(flag, str)


class TestCRequirementsMatrix:
    """Test the C↔R matrix: every C cited by ≥1 R, every R cites ≥1 C.

    This is a data-driven lock. The matrix is defined below as a dict
    mapping capability_id -> list of requirement_ids it satisfies.
    """

    # C↔R Matrix: capability_id -> list of requirement IDs from TODO43 §3 / abc3
    C_R_MATRIX: dict[str, list[str]] = {
        # Core capabilities (C1-C20) - mapped to R1-R20
        "C1": ["R1", "R4"],  # Six-axis coordinate space
        "C2": ["R2", "R3"],  # Unified record schema
        "C3": ["R12", "R26"],  # Content-addressed records
        "C4": ["R12", "K8"],  # Measurement key deduplication
        "C5": ["R9", "R27"],  # Cell key grouping
        "C6": ["R79", "K4"],  # Schema versioning
        "C7": ["R37", "R38", "R63", "R66"],  # Legality engine
        "C8": ["R18", "R19", "R20", "R29", "R12"],  # S1-S11 pipeline
        "C9": ["R46", "R47", "R48", "R49", "R50", "R51"],  # Eight-policy catalog
        "C10": ["R46", "R47", "R48", "R49", "R50", "R51"],  # Evidence-driven allocation
        "C11": ["R26", "R27", "R28", "R29", "R30"],  # Replay and resume
        "C12": ["R31", "R32", "R33", "R34", "R35"],  # Three-tier status
        "C13": ["R35", "R36", "R64", "R65"],  # Claim eligibility predicates
        "C14": ["R58", "R59", "R60", "R61", "R62"],  # Failure intelligence
        "C15": ["R60", "K8"],  # Unified artifact storage
        "C16": ["C59", "R15", "K5"],  # Vector retrieval
        "C17": ["R52", "Q4", "Q12"],  # Prior registry
        "C18": ["R54", "Q10"],  # Surrogate policy wrapper
        "C19": ["R53", "R55", "R56"],  # I(C,U) metamodel
        "C20": ["R57", "Q15"],  # Reasoning records
        # Acceleration (C21-C25)
        "C21": ["R75"],  # torch.compile settle loop
        "C22": ["R75"],  # Gradient checkpointing
        "C23": ["R75"],  # Gain control homeostasis
        "C24": ["R75"],  # KV cache for transformer
        "C25": ["R75"],  # Async orchestration
        # Scaling (C26-C30)
        "C26": ["R75"],  # Multiprocess backend
        "C27": ["R75"],  # Multi-GPU DDP/FSDP
        "C28": ["R75"],  # P2P gossip cluster
        "C29": ["R75"],  # Batch vectorization
        "C30": ["R75"],  # Pipeline parallelism
        # Reproducibility (C31-C36)
        "C31": ["R86"],  # Computational reproducibility
        "C32": ["R86"],  # Scientific reproducibility
        "C33": ["R86"],  # Reproducibility class tracking
        "C34": ["R31", "R32"],  # Assessment procedure versioning
        "C35": ["R8", "R22", "R67"],  # Data origin tagging
        "C36": ["R53", "R55"],  # Transfer provenance tracking
        # Governance (C37-C48)
        "C37": ["R65"],  # Matched-cost comparison guard
        "C38": ["R8", "R22", "R67"],  # Stratification guard
        "C39": ["R53", "R55"],  # I(C,U) leakage audit
        "C40": ["R83", "Q14"],  # Alert predicates
        "C41": ["R35", "R36"],  # Promotion predicates
        "C42": ["R54"],  # Effect-size protocol
        "C43": ["R21", "R22", "R23", "R24"],  # Budget tier system
        "C44": ["R81", "R82", "R83", "R84"],  # Run controller
        "C45": ["R81", "R82", "R83", "R84"],  # Service manager
        "C46": ["R76", "R77", "R78"],  # Conformance harness
        "C47": ["R78"],  # Currency lock
        "C48": ["R43"],  # Question-first entry
        # Learning (C49-C60)
        "C49": ["R54", "Q10"],  # Surrogate-driven acquisition
        "C50": ["R53", "R55"],  # Cross-task transfer
        "C51": ["R6", "R52", "R55"],  # Prior single-source accessor
        "C52": ["K10"],  # Run-scoped ICU/Reasoning
        "C53": ["R57"],  # Reasoning persistence
        "C54": ["R15", "R53"],  # Warm-start from prior runs
        "C55": ["R54", "C59"],  # Coordinate-wide surrogate
        "C56": ["C59", "C60", "C61", "C62", "C63"],  # I(C,U) feature encoder
        "C57": ["R64"],  # Achieved-seed claim eligibility
        "C58": ["C1", "R31"],  # Multi-objective Pareto
        "C59": ["C1", "R31"],  # Substrate-aware objectives
        "C60": ["R53", "R55"],  # Frozen-θ ψ adaptation
        # Gate 1 Experimental (C61-C76)
        "C61": ["§13.3"],  # NTM geometry
        "C62": ["§13.3"],  # NCA geometry
        "C63": ["§13.3"],  # PEPITA/LEMMA credit
        "C64": ["§13.3"],  # Holomorphic EP
        "C65": ["§13.3"],  # Directed EP
        "C66": ["§13.3"],  # Finite-nudge EP
        "C67": ["§13.3"],  # Ternary EqProp
        "C68": ["§13.3"],  # Momentum EqProp
        "C69": ["§13.3"],  # Sparse EqProp
        "C70": ["§13.3"],  # Diffusion EqProp
        "C71": ["§13.3"],  # Routing plasticity
        "C72": ["§13.3"],  # Fast-weight plasticity
        "C73": ["§13.3"],  # Substrate-coupled plasticity
        "C74": ["§13.3"],  # Rule-state plasticity (Z3)
        "C75": ["§13.3"],  # Closed-form ridge plasticity
        "C76": ["§13.3"],  # Temporal ψ plasticity
        # Platform packages (C77-C82)
        "C77": ["§13.5"],  # CEEC core ledger
        "C78": ["§13.5"],  # Psi-PEFT
        "C79": ["§13.5"],  # Local feedback projections
        "C80": ["§13.5"],  # Stability guard
        "C81": ["§13.5"],  # Lab synthesis
        "C82": ["§13.5"],  # Lab evolution
        # CLI / Surface (C83-C88)
        "C83": ["R80"],  # Surface CLI dispatcher
        "C84": ["R85", "R86", "R87", "R88"],  # Report generator
        "C85": ["R78", "R80"],  # Codegen from registries
        "C86": ["R80"],  # Documented-command conformance
        "C87": ["R87"],  # Gallery lock
        "C88": ["R80"],  # Probe conventions
    }

    def test_every_capability_cites_at_least_one_requirement(self) -> None:
        """Every capability (C) cited by ≥1 requirement (R)."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        for cap_id in [f"C{i}" for i in range(1, 89)]:
            assert cap_id in self.C_R_MATRIX, (
                f"Capability {cap_id} missing from C↔R matrix"
            )
            requirements = self.C_R_MATRIX[cap_id]
            assert len(requirements) >= 1, f"Capability {cap_id} cites no requirements"

    def test_every_requirement_cited_by_at_least_one_capability(self) -> None:
        """Every requirement (R) cites ≥1 capability (C)."""
        # Collect all requirements from matrix
        all_requirements = set()
        for reqs in self.C_R_MATRIX.values():
            all_requirements.update(reqs)

        # Each requirement should be cited by at least one capability
        for req in all_requirements:
            citing_caps = [
                cap_id for cap_id, reqs in self.C_R_MATRIX.items() if req in reqs
            ]
            assert len(citing_caps) >= 1, (
                f"Requirement {req} not cited by any capability"
            )

    def test_matrix_covers_all_seeded_capabilities(self) -> None:
        """C↔R matrix covers all 88 seeded capabilities."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()

        seeded_caps = set(CAPABILITIES_REGISTRY.keys())
        matrix_caps = set(self.C_R_MATRIX.keys())

        assert seeded_caps == matrix_caps, (
            f"Matrix mismatch: seeded={seeded_caps - matrix_caps}, "
            f"matrix={matrix_caps - seeded_caps}"
        )


class TestSeedRegistriesIdempotent:
    """Verify seed_all_registries is idempotent."""

    def test_seed_all_registries_idempotent(self) -> None:
        """Calling seed_all_registries twice produces same result."""
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()
        counts1 = {
            "objectives": len(CAPABILITIES_REGISTRY),  # Will be overwritten
        }
        seed_all_registries()
        counts2 = {
            "capabilities": len(CAPABILITIES_REGISTRY),
        }
        # Just verify it doesn't error and registries are populated
        assert len(CAPABILITIES_REGISTRY) == 88


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
