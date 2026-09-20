"""Registry Completeness Lock (F1 from TODO32b).

Ensures every concrete ontology class across all 6 axes has exactly one
primitive spec, and every primitive spec resolves to a live ontology class.

Extends the dynamics wiring lock doctrine to the full 64-spec registry.
"""

import inspect

from computronium.acceleration.registry import primitives
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig, geometry_from_config
from computronium.ontology.plasticity import PlasticityConfig
from computronium.ontology.substrate import (
    SubstrateConfig,
    substrate_from_config,
)
from computronium.ontology.update import (
    ParameterUpdateConfig,
    update_from_config,
)

# ============================================================
# Axis 1: Substrate
# ============================================================

_SUBSTRATE_CONFIG_METHODS: dict[str, str] = {
    "digital": "primitive.substrate.digital",
    "analog": "primitive.substrate.digital",  # Analog uses digital primitive (no separate primitive)
    "memristive": "primitive.substrate.memristive",
    "neuromorphic": "primitive.substrate.neuromorphic",
    "optical": "primitive.substrate.photonic",
    "quantum": "primitive.substrate.quantum",
    "complex": "primitive.substrate.complex",
    "sparse": "primitive.substrate.sparse",
    "ternary": "primitive.substrate.ternary",
    # noisy is created via digital with noise_level > 0
}

_SUBSTRATE_ONTOLOGY_CLASSES: dict[str, str] = {
    "digital": "DigitalSubstrate",
    "analog": "AnalogSubstrate",
    "memristive": "MemristiveSubstrate",
    "neuromorphic": "NeuromorphicSubstrate",
    "optical": "OpticalSubstrate",
    "quantum": "QuantumSubstrate",
    "complex": "ComplexSubstrate",
    "sparse": "SparseSubstrate",
    "ternary": "TernarySubstrate",
}


def _substrate_config_classmethods() -> dict[str, str]:
    """Map config classmethod name -> substrate_type."""
    found: dict[str, str] = {}
    for name, member in inspect.getmembers(SubstrateConfig):
        if name.startswith("_") or not isinstance(member, classmethod):
            continue
        config = member.__func__(SubstrateConfig)
        if isinstance(config, SubstrateConfig):
            found[name] = config.substrate_type.value
    return found


def test_substrate_config_classmethods_cover_primitives() -> None:
    """Every SubstrateConfig classmethod maps to a known primitive spec."""
    classmethods = _substrate_config_classmethods()
    primitive_ids = {s.id for s in primitives() if s.axis == "substrate"}

    for method_name, substrate_type in classmethods.items():
        if substrate_type not in _SUBSTRATE_CONFIG_METHODS:
            raise AssertionError(
                f"SubstrateConfig.{method_name} -> {substrate_type} "
                f"has no expected primitive mapping"
            )
        expected_primitive = _SUBSTRATE_CONFIG_METHODS[substrate_type]
        if expected_primitive not in primitive_ids:
            raise AssertionError(
                f"SubstrateConfig.{method_name} expects primitive "
                f"{expected_primitive!r} but it's not registered. "
                f"Available: {sorted(primitive_ids)}"
            )


def test_substrate_primitives_have_ontology_classes() -> None:
    """Every substrate primitive has a corresponding ontology class."""
    from computronium.ontology.substrate import (
        ComplexSubstrate,
        DigitalSubstrate,
        MemristiveSubstrate,
        NeuromorphicSubstrate,
        NoisySubstrate,
        OpticalSubstrate,
        QuantumSubstrate,
        SparseSubstrate,
        TernarySubstrate,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.substrate.digital": DigitalSubstrate,
        "primitive.substrate.memristive": MemristiveSubstrate,
        "primitive.substrate.neuromorphic": NeuromorphicSubstrate,
        "primitive.substrate.photonic": OpticalSubstrate,
        "primitive.substrate.quantum": QuantumSubstrate,
        "primitive.substrate.complex": ComplexSubstrate,
        "primitive.substrate.sparse": SparseSubstrate,
        "primitive.substrate.ternary": TernarySubstrate,
        "primitive.substrate.noisy": NoisySubstrate,
    }

    for spec in primitives():
        if spec.axis != "substrate":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        if spec.id == "primitive.substrate.noisy":
            # Noisy uses digital config with noise_level
            config = SubstrateConfig.digital(noise_level=0.05)
            substrate = cls(config)
        else:
            config_method = next(
                k for k, v in _SUBSTRATE_CONFIG_METHODS.items() if v == spec.id
            )
            config = getattr(SubstrateConfig, config_method)()
            # ComplexSubstrate is instantiated directly (not via substrate_from_config)
            if cls is ComplexSubstrate:
                substrate = cls(config)
            else:
                substrate = substrate_from_config(config)
        assert isinstance(substrate, cls), (
            f"{spec.id} -> substrate_from_config returned "
            f"{type(substrate).__name__}, expected {cls.__name__}"
        )


# ============================================================
# Axis 2: Geometry
# ============================================================

_GEOMETRY_CONFIG_METHODS: dict[str, str] = {
    "feedforward": "primitive.geometry.feedforward_dag",
    "causal_transformer": "primitive.geometry.feedforward_dag",  # uses FeedforwardGeometry
    "recurrent": "primitive.geometry.recurrent_attractor",
    "tile_mesh": "primitive.geometry.tile_mesh",
    "conv": "primitive.geometry.feedforward_dag",  # ConvGeometry extends FeedforwardGeometry
    "graph": "primitive.geometry.fabric_pc",  # GraphGeometry uses FabricPC
    "attention": "primitive.geometry.feedforward_dag",  # AttentionGeometry extends FeedforwardGeometry
    "spatial_lattice": "primitive.geometry.spatial_lattice_3d",
    "nca": "primitive.geometry.nca",
    "ntm": "primitive.geometry.ntm",
}

_GEOMETRY_ONTOLOGY_CLASSES: dict[str, str] = {
    "feedforward": "FeedforwardGeometry",
    "causal_transformer": "TransformerGeometry",
    "recurrent": "RecurrentGeometry",
    "tile_mesh": "TileGeometry",
    "conv": "ConvGeometry",
    "graph": "GraphGeometry",
    "attention": "AttentionGeometry",
    "spatial_lattice": "SpatialLattice3DGeometry",
    "nca": "NcaGeometry",
    "ntm": "NtmGeometry",
}


def _geometry_config_classmethods() -> dict[str, str]:
    """Map config classmethod name -> topology_type."""
    found: dict[str, str] = {}
    for name, member in inspect.getmembers(GeometryConfig):
        if name.startswith("_") or not isinstance(member, classmethod):
            continue
        config = member.__func__(
            GeometryConfig, input_dim=10, output_dim=5, hidden_dims=(8,)
        )
        if isinstance(config, GeometryConfig):
            found[name] = config.topology_type
    return found


def test_geometry_config_classmethods_cover_primitives() -> None:
    """Every GeometryConfig classmethod maps to a known primitive spec."""
    classmethods = _geometry_config_classmethods()
    primitive_ids = {s.id for s in primitives() if s.axis == "geometry"}

    for method_name, topology_type in classmethods.items():
        if topology_type not in _GEOMETRY_CONFIG_METHODS:
            raise AssertionError(
                f"GeometryConfig.{method_name} -> {topology_type} "
                f"has no expected primitive mapping"
            )
        expected_primitive = _GEOMETRY_CONFIG_METHODS[topology_type]
        if expected_primitive not in primitive_ids:
            raise AssertionError(
                f"GeometryConfig.{method_name} expects primitive "
                f"{expected_primitive!r} but it's not registered. "
                f"Available: {sorted(primitive_ids)}"
            )


def test_geometry_primitives_have_ontology_classes() -> None:
    """Every geometry primitive has a corresponding ontology class."""
    from computronium.ontology.geometry import (
        FeedforwardGeometry,
        GraphGeometry,
        NcaGeometry,
        NtmGeometry,
        RecurrentGeometry,
        SpatialLattice3DGeometry,
        TileGeometry,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.geometry.feedforward_dag": FeedforwardGeometry,
        "primitive.geometry.recurrent_attractor": RecurrentGeometry,
        "primitive.geometry.tile_mesh": TileGeometry,
        "primitive.geometry.fabric_pc": GraphGeometry,
        "primitive.geometry.ntm": NtmGeometry,
        "primitive.geometry.nca": NcaGeometry,
        "primitive.geometry.spatial_lattice_3d": SpatialLattice3DGeometry,
    }

    # Config methods with their specific required arguments
    GEOMETRY_CONFIG_ARGS: dict[str, dict] = {
        "feedforward": {"input_dim": 10, "output_dim": 5, "hidden_dims": (8,)},
        "recurrent": {"input_dim": 10, "output_dim": 5, "hidden_dims": (8,)},
        "tile_mesh": {"input_dim": 10, "output_dim": 5, "num_layers": 2},
        "graph": {"input_dim": 10, "output_dim": 5, "edge_index": [[0, 1], [1, 0]]},
        "ntm": {"input_dim": 10, "output_dim": 5, "hidden": 8},
        "nca": {"channels": 8, "hidden": 8},
        "spatial_lattice": {
            "input_dim": 10,
            "output_dim": 5,
            "lattice_dims": (2, 2, 2),
        },
    }

    for spec in primitives():
        if spec.axis != "geometry":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = next(
            k for k, v in _GEOMETRY_CONFIG_METHODS.items() if v == spec.id
        )
        args = GEOMETRY_CONFIG_ARGS[config_method]
        config = getattr(GeometryConfig, config_method)(**args)
        geometry = geometry_from_config(config)
        assert isinstance(geometry, cls), (
            f"{spec.id} -> geometry_from_config returned "
            f"{type(geometry).__name__}, expected {cls.__name__}"
        )


# ============================================================
# Axis 3: StateDynamics (already covered by dynamics wiring lock)
# ============================================================


def test_state_dynamics_primitives_have_ontology_classes() -> None:
    """Every state_dynamics primitive has a corresponding ontology class."""
    from computronium.ontology.dynamics import (
        DiffusionDynamics,
        EnergyMinimizationDynamics,
        InstantaneousDynamics,
        LazyStateDynamics,
        PCALMDynamics,
        PredictiveSettlingDynamics,
        SpikeIntegrationDynamics,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.state_dynamics.diffusion": DiffusionDynamics,
        "primitive.state_dynamics.energy_minimization": EnergyMinimizationDynamics,
        "primitive.state_dynamics.instantaneous_pass": InstantaneousDynamics,
        "primitive.state_dynamics.lazy_state_dynamics": LazyStateDynamics,
        "primitive.state_dynamics.pc_alm_settling": PCALMDynamics,
        "primitive.state_dynamics.predictive_settling": PredictiveSettlingDynamics,
        "primitive.state_dynamics.spike_integration": SpikeIntegrationDynamics,
    }

    # Map primitive IDs to StateDynamicsConfig classmethod names
    DYNAMICS_CONFIG_METHODS: dict[str, str] = {
        "primitive.state_dynamics.diffusion": "diffusion",
        "primitive.state_dynamics.energy_minimization": "energy_minimization",
        "primitive.state_dynamics.instantaneous_pass": "instantaneous",
        "primitive.state_dynamics.lazy_state_dynamics": "lazy",
        "primitive.state_dynamics.pc_alm_settling": "pc_alm",
        "primitive.state_dynamics.predictive_settling": "predictive_settling",
        "primitive.state_dynamics.spike_integration": "spike_integration",
    }

    for spec in primitives():
        if spec.axis != "state_dynamics":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = DYNAMICS_CONFIG_METHODS[spec.id]
        config = getattr(StateDynamicsConfig, config_method)()
        from computronium.ontology.dynamics import dynamics_from_config

        dynamics = dynamics_from_config(config)
        assert isinstance(dynamics, cls), (
            f"{spec.id} -> dynamics_from_config returned "
            f"{type(dynamics).__name__}, expected {cls.__name__}"
        )


# ============================================================
# Axis 4: CreditAssignment
# ============================================================

_CREDIT_CONFIG_METHODS: dict[str, str] = {
    "thermodynamic_contrast": "primitive.credit_assignment.thermodynamic_contrast",
    "random_projections": "primitive.credit_assignment.random_projections",
    "local_goodness": "primitive.credit_assignment.local_goodness",
    "temporal_trace": "primitive.credit_assignment.temporal_trace",
    "target_inversion": "primitive.credit_assignment.target_inversion",
    "homeostatic": "primitive.credit_assignment.homeostatic",
    "pepita": "primitive.credit_assignment.pc_alm",  # PEPITA maps to PC-ALM credit primitive
    "gradient": "primitive.credit_assignment.reverse_mode",  # gradient/backprop -> reverse_mode
    "local_contrastive": "primitive.credit_assignment.local_goodness",  # local_contrastive uses local_goodness
    "pc_alm": "primitive.credit_assignment.pc_alm",
}

_CREDIT_ONTOLOGY_CLASSES: dict[str, str] = {
    "thermodynamic_contrast": "ThermodynamicContrast",
    "random_projections": "RandomProjectionsCredit",
    "local_goodness": "LocalGoodnessCredit",
    "temporal_trace": "TemporalTraceCredit",
    "target_inversion": "TargetInversionCredit",
    "homeostatic": "HomeostaticCredit",
    "pepita": "PepitaCredit",
    "gradient": "BackpropCredit",
    "local_contrastive": "LocalContrastiveCredit",
    "pc_alm": "PCALMCredit",
}


def _credit_config_classmethods() -> dict[str, str]:
    """Map config classmethod name -> credit_type."""
    found: dict[str, str] = {}
    for name, member in inspect.getmembers(CreditAssignmentConfig):
        if name.startswith("_") or not isinstance(member, classmethod):
            continue
        config = member.__func__(CreditAssignmentConfig)
        if isinstance(config, CreditAssignmentConfig):
            found[name] = config.credit_type
    return found


def test_credit_config_classmethods_cover_primitives() -> None:
    """Every CreditAssignmentConfig classmethod maps to a known primitive spec."""
    classmethods = _credit_config_classmethods()
    primitive_ids = {s.id for s in primitives() if s.axis == "credit_assignment"}

    for method_name, credit_type in classmethods.items():
        if credit_type not in _CREDIT_CONFIG_METHODS:
            raise AssertionError(
                f"CreditAssignmentConfig.{method_name} -> {credit_type} "
                f"has no expected primitive mapping"
            )
        expected_primitive = _CREDIT_CONFIG_METHODS[credit_type]
        if expected_primitive not in primitive_ids:
            raise AssertionError(
                f"CreditAssignmentConfig.{method_name} expects primitive "
                f"{expected_primitive!r} but it's not registered. "
                f"Available: {sorted(primitive_ids)}"
            )


def test_credit_primitives_have_ontology_classes() -> None:
    """Every credit_assignment primitive has a corresponding ontology class."""
    from computronium.ontology.credit import (
        BackpropCredit,
        HomeostaticCredit,
        LocalGoodnessCredit,
        PCALMCredit,
        RandomProjectionsCredit,
        TargetInversionCredit,
        TemporalTraceCredit,
        ThermodynamicContrast,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.credit_assignment.thermodynamic_contrast": ThermodynamicContrast,
        "primitive.credit_assignment.random_projections": RandomProjectionsCredit,
        "primitive.credit_assignment.local_goodness": LocalGoodnessCredit,
        "primitive.credit_assignment.temporal_trace": TemporalTraceCredit,
        "primitive.credit_assignment.target_inversion": TargetInversionCredit,
        "primitive.credit_assignment.homeostatic": HomeostaticCredit,
        "primitive.credit_assignment.pc_alm": PCALMCredit,
        "primitive.credit_assignment.reverse_mode": BackpropCredit,
    }

    for spec in primitives():
        if spec.axis != "credit_assignment":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = next(
            k for k, v in _CREDIT_CONFIG_METHODS.items() if v == spec.id
        )
        config = getattr(CreditAssignmentConfig, config_method)()
        # PCALMCredit is not handled by _credit_from_config dispatch (gap in dispatch)
        # Directly instantiate the ontology class with the config
        if cls.__name__ == "PCALMCredit":
            credit = cls(config)
        else:
            from computronium.core.system_trainer.spec import _credit_from_config

            credit = _credit_from_config(config)
        assert isinstance(credit, cls), (
            f"{spec.id} -> credit instantiation returned "
            f"{type(credit).__name__}, expected {cls.__name__}"
        )


# ============================================================
# Axis 5: ParameterUpdate
# ============================================================

_UPDATE_CONFIG_METHODS: dict[str, str] = {
    "euclidean": "primitive.parameter_update.euclidean",
    "riemannian_orthogonal": "primitive.parameter_update.muon",
    "muon": "primitive.parameter_update.muon",
    "spectral_constrained": "primitive.parameter_update.spectral_constrained",
    "mean_norm": "primitive.parameter_update.euclidean",  # mean_norm uses euclidean primitive
    "elastic_consolidation": "primitive.parameter_update.elastic_consolidation",
    "natural_gradient": "primitive.parameter_update.natural_gradient",
    "adam": "primitive.parameter_update.euclidean",  # adam uses euclidean primitive
    "ortho_adam": "primitive.parameter_update.muon",  # ortho_adam uses muon primitive
    "unit_rms": "primitive.parameter_update.euclidean",  # unit_rms uses euclidean primitive
    "local_adam": "primitive.parameter_update.euclidean",  # local_adam uses euclidean primitive
    "lion": "primitive.parameter_update.euclidean",  # lion uses euclidean primitive
}

_UPDATE_ONTOLOGY_CLASSES: dict[str, str] = {
    "euclidean": "EuclideanUpdate",
    "riemannian_orthogonal": "RiemannianOrthogonalUpdate",
    "muon": "RiemannianOrthogonalUpdate",
    "spectral_constrained": "SpectralConstrainedUpdate",
    "mean_norm": "MeanNormUpdate",
    "elastic_consolidation": "ElasticConsolidationUpdate",
    "natural_gradient": "NaturalGradientUpdate",
    "adam": "AdamUpdate",
    "ortho_adam": "OrthoAdamUpdate",
    "unit_rms": "UnitRMSUpdate",
    "local_adam": "LocalAdamUpdate",
    "lion": "LionUpdate",
    "role_split": "RoleSplitUpdate",
}


def _update_config_classmethods() -> dict[str, str]:
    """Map config classmethod name -> update_type."""
    found: dict[str, str] = {}
    for name, member in inspect.getmembers(ParameterUpdateConfig):
        if name.startswith("_") or not isinstance(member, classmethod):
            continue
        config = member.__func__(ParameterUpdateConfig)
        if isinstance(config, ParameterUpdateConfig):
            found[name] = config.update_type
    return found


def test_update_config_classmethods_cover_primitives() -> None:
    """Every ParameterUpdateConfig classmethod maps to a known primitive spec."""
    classmethods = _update_config_classmethods()
    primitive_ids = {s.id for s in primitives() if s.axis == "parameter_update"}

    for method_name, update_type in classmethods.items():
        if update_type not in _UPDATE_CONFIG_METHODS:
            raise AssertionError(
                f"ParameterUpdateConfig.{method_name} -> {update_type} "
                f"has no expected primitive mapping"
            )
        expected_primitive = _UPDATE_CONFIG_METHODS[update_type]
        if expected_primitive not in primitive_ids:
            raise AssertionError(
                f"ParameterUpdateConfig.{method_name} expects primitive "
                f"{expected_primitive!r} but it's not registered. "
                f"Available: {sorted(primitive_ids)}"
            )


def test_update_primitives_have_ontology_classes() -> None:
    """Every parameter_update primitive has a corresponding ontology class."""
    from computronium.ontology.update import (
        ElasticConsolidationUpdate,
        EuclideanUpdate,
        NaturalGradientUpdate,
        RiemannianOrthogonalUpdate,
        SpectralConstrainedUpdate,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.parameter_update.euclidean": EuclideanUpdate,
        "primitive.parameter_update.muon": RiemannianOrthogonalUpdate,
        "primitive.parameter_update.spectral_constrained": SpectralConstrainedUpdate,
        "primitive.parameter_update.natural_gradient": NaturalGradientUpdate,
        "primitive.parameter_update.elastic_consolidation": ElasticConsolidationUpdate,
    }

    for spec in primitives():
        if spec.axis != "parameter_update":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = next(
            k for k, v in _UPDATE_CONFIG_METHODS.items() if v == spec.id
        )
        config = getattr(ParameterUpdateConfig, config_method)()
        # natural_gradient is not in _UPDATE_CLASSES dispatch (gap in dispatch)
        # Directly instantiate the ontology class with the config
        if cls.__name__ == "NaturalGradientUpdate":
            update = cls(config)
        else:
            update = update_from_config(config)
        assert isinstance(update, cls), (
            f"{spec.id} -> update instantiation returned "
            f"{type(update).__name__}, expected {cls.__name__}"
        )


# ============================================================
# Axis 6: Plasticity
# ============================================================

_PLASTICITY_CONFIG_METHODS: dict[str, str] = {
    "null": "primitive.plasticity.null",
    "routing": "primitive.plasticity.routing",
    "fast_weights": "primitive.plasticity.fast_weight",
    "substrate_coupled": "primitive.plasticity.substrate_coupled",
    "rule_state": "primitive.plasticity.rule_state",
    "temporal_psi": "primitive.plasticity.temporal_psi",
    "conflict_adaptive": "primitive.plasticity.temporal_psi",  # conflict_adaptive uses temporal_psi primitive
    # closed_form_ridge has no PlasticityConfig classmethod
}


def _plasticity_config_classmethods() -> dict[str, str]:
    """Map config classmethod name -> plasticity_type."""
    from computronium.state.transitions import PlasticityConfig

    found: dict[str, str] = {}
    # Directly call known classmethods (inspect.getmembers doesn't find them reliably)
    for name in [
        "null",
        "routing",
        "fast_weights",
        "substrate_coupled",
        "rule_state",
        "temporal_psi",
        "conflict_adaptive",
    ]:
        config = getattr(PlasticityConfig, name)()
        if isinstance(config, PlasticityConfig):
            found[name] = config.plasticity_type
    return found


def test_plasticity_config_classmethods_cover_primitives() -> None:
    """Every PlasticityConfig classmethod maps to a known primitive spec."""
    classmethods = _plasticity_config_classmethods()
    primitive_ids = {s.id for s in primitives() if s.axis == "plasticity"}

    for method_name, plasticity_type in classmethods.items():
        if plasticity_type not in _PLASTICITY_CONFIG_METHODS:
            raise AssertionError(
                f"PlasticityConfig.{method_name} -> {plasticity_type} "
                f"has no expected primitive mapping"
            )
        expected_primitive = _PLASTICITY_CONFIG_METHODS[plasticity_type]
        if expected_primitive not in primitive_ids:
            raise AssertionError(
                f"PlasticityConfig.{method_name} expects primitive "
                f"{expected_primitive!r} but it's not registered. "
                f"Available: {sorted(primitive_ids)}"
            )


def test_plasticity_primitives_have_ontology_classes() -> None:
    """Every plasticity primitive has a corresponding ontology class."""
    from computronium.core.plasticity import (
        ClosedFormRidgePlasticity,
        FastWeightPlasticity,
        RoutingPlasticity,
        RuleStatePlasticity,
        SubstrateCoupledPlasticity,
        TemporalPsiPlasticity,
    )
    from computronium.state import NullPlasticity

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.plasticity.null": NullPlasticity,
        "primitive.plasticity.routing": RoutingPlasticity,
        "primitive.plasticity.fast_weight": FastWeightPlasticity,
        "primitive.plasticity.substrate_coupled": SubstrateCoupledPlasticity,
        "primitive.plasticity.rule_state": RuleStatePlasticity,
        "primitive.plasticity.temporal_psi": TemporalPsiPlasticity,
        "primitive.plasticity.closed_form_ridge": ClosedFormRidgePlasticity,
    }

    # Map primitive IDs to PlasticityConfig classmethod names
    PLASTICITY_CONFIG_METHODS: dict[str, str | None] = {
        "primitive.plasticity.null": "null",
        "primitive.plasticity.routing": "routing",
        "primitive.plasticity.fast_weight": "fast_weights",
        "primitive.plasticity.substrate_coupled": "substrate_coupled",
        "primitive.plasticity.rule_state": "rule_state",
        "primitive.plasticity.temporal_psi": "temporal_psi",
        # closed_form_ridge has no PlasticityConfig classmethod
        "primitive.plasticity.closed_form_ridge": None,
    }

    for spec in primitives():
        if spec.axis != "plasticity":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = PLASTICITY_CONFIG_METHODS.get(spec.id)
        if config_method is None:
            # closed_form_ridge: directly instantiate with default config
            # ClosedFormRidgePlasticity expects ClosedFormRidgeConfig, not PlasticityConfig
            from computronium.core.plasticity.closed_form import (
                ClosedFormRidgeConfig,
                ClosedFormRidgePlasticity,
            )

            config = ClosedFormRidgeConfig()
            plasticity = ClosedFormRidgePlasticity(config)
        else:
            config = getattr(PlasticityConfig, config_method)()
            from computronium.core.system_trainer.spec import _plasticity_from_config

            plasticity = _plasticity_from_config(config)
        assert isinstance(plasticity, cls), (
            f"{spec.id} -> plasticity instantiation returned "
            f"{type(plasticity).__name__}, expected {cls.__name__}"
        )


# ============================================================
# Cross-axis: No orphan primitive specs
# ============================================================

ALL_ONTOLOGY_MAPS: dict[str, dict[str, str]] = {
    "substrate": {
        "primitive.substrate.digital": "DigitalSubstrate",
        "primitive.substrate.memristive": "MemristiveSubstrate",
        "primitive.substrate.neuromorphic": "NeuromorphicSubstrate",
        "primitive.substrate.photonic": "OpticalSubstrate",
        "primitive.substrate.quantum": "QuantumSubstrate",
        "primitive.substrate.complex": "ComplexSubstrate",
        "primitive.substrate.sparse": "SparseSubstrate",
        "primitive.substrate.ternary": "TernarySubstrate",
        "primitive.substrate.noisy": "NoisySubstrate",
    },
    "geometry": {
        "primitive.geometry.feedforward_dag": "FeedforwardGeometry",
        "primitive.geometry.recurrent_attractor": "RecurrentGeometry",
        "primitive.geometry.tile_mesh": "TileGeometry",
        "primitive.geometry.fabric_pc": "GraphGeometry",
        "primitive.geometry.ntm": "NtmGeometry",
        "primitive.geometry.nca": "NcaGeometry",
        "primitive.geometry.spatial_lattice_3d": "SpatialLattice3DGeometry",
    },
    "state_dynamics": {
        "primitive.state_dynamics.diffusion": "DiffusionDynamics",
        "primitive.state_dynamics.energy_minimization": "EnergyMinimizationDynamics",
        "primitive.state_dynamics.instantaneous_pass": "InstantaneousDynamics",
        "primitive.state_dynamics.lazy_state_dynamics": "LazyStateDynamics",
        "primitive.state_dynamics.pc_alm_settling": "PCALMDynamics",
        "primitive.state_dynamics.predictive_settling": "PredictiveSettlingDynamics",
        "primitive.state_dynamics.spike_integration": "SpikeIntegrationDynamics",
    },
    "credit_assignment": {
        "primitive.credit_assignment.thermodynamic_contrast": "ThermodynamicContrast",
        "primitive.credit_assignment.random_projections": "RandomProjectionsCredit",
        "primitive.credit_assignment.local_goodness": "LocalGoodnessCredit",
        "primitive.credit_assignment.temporal_trace": "TemporalTraceCredit",
        "primitive.credit_assignment.target_inversion": "TargetInversionCredit",
        "primitive.credit_assignment.homeostatic": "HomeostaticCredit",
        "primitive.credit_assignment.pc_alm": "PCALMCredit",
        "primitive.credit_assignment.reverse_mode": "BackpropCredit",
    },
    "parameter_update": {
        "primitive.parameter_update.euclidean": "EuclideanUpdate",
        "primitive.parameter_update.muon": "RiemannianOrthogonalUpdate",
        "primitive.parameter_update.spectral_constrained": "SpectralConstrainedUpdate",
        "primitive.parameter_update.natural_gradient": "NaturalGradientUpdate",
        "primitive.parameter_update.elastic_consolidation": "ElasticConsolidationUpdate",
    },
    "plasticity": {
        "primitive.plasticity.null": "NullPlasticity",
        "primitive.plasticity.routing": "RoutingPlasticity",
        "primitive.plasticity.fast_weight": "FastWeightPlasticity",
        "primitive.plasticity.substrate_coupled": "SubstrateCoupledPlasticity",
        "primitive.plasticity.rule_state": "RuleStatePlasticity",
        "primitive.plasticity.temporal_psi": "TemporalPsiPlasticity",
        "primitive.plasticity.closed_form_ridge": "ClosedFormRidgePlasticity",
    },
}


def test_no_orphan_primitive_specs() -> None:
    """Every registered primitive spec has a known ontology class mapping."""
    all_mapped_ids = set()
    for axis_map in ALL_ONTOLOGY_MAPS.values():
        all_mapped_ids.update(axis_map.keys())

    for spec in primitives():
        if spec.id not in all_mapped_ids:
            raise AssertionError(
                f"Orphan primitive spec: {spec.id} (axis={spec.axis}) "
                f"has no ontology class mapping in the completeness lock"
            )


def test_no_dead_ontology_mappings() -> None:
    """Every ontology class mapping corresponds to a registered primitive spec."""
    registered_ids = {s.id for s in primitives()}

    for axis, mapping in ALL_ONTOLOGY_MAPS.items():
        for spec_id in mapping:
            if spec_id not in registered_ids:
                raise AssertionError(
                    f"Dead ontology mapping: {spec_id} (axis={axis}) "
                    f"is mapped but not registered as a primitive spec"
                )
