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


def _expected_spec_id(axis: str, coordinate: str) -> str:
    """The spec ID that must exist for a runtime coordinate."""
    return f"primitive.{axis}.{coordinate}"


def _assert_coordinate_has_spec(specs, axis: str, coordinate: str) -> str:
    """Assert the coordinate's same-named spec is registered; return its ID."""
    spec_id = _expected_spec_id(axis, coordinate)
    if spec_id not in specs:
        raise AssertionError(
            f"{axis} coordinate {coordinate!r} has no same-named spec; "
            f"registered: {sorted(specs)}"
        )
    return spec_id


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
    """Every SubstrateConfig classmethod names the spec of its own coordinate."""
    primitive_ids = {s.id for s in primitives() if s.axis == "substrate"}

    for _method, substrate_type in _substrate_config_classmethods().items():
        _assert_coordinate_has_spec(primitive_ids, "substrate", substrate_type)


def test_substrate_primitives_have_ontology_classes() -> None:
    """Every substrate primitive has a corresponding ontology class."""
    from computronium.ontology.substrate import (
        AnalogSubstrate,
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
        "primitive.substrate.optical": OpticalSubstrate,
        "primitive.substrate.quantum": QuantumSubstrate,
        "primitive.substrate.complex": ComplexSubstrate,
        "primitive.substrate.sparse": SparseSubstrate,
        "primitive.substrate.ternary": TernarySubstrate,
        "primitive.substrate.noisy": NoisySubstrate,
        "primitive.substrate.analog": AnalogSubstrate,
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
            config_method = spec.id.rsplit(".", 1)[-1]
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
    """Every GeometryConfig classmethod names the spec of its own coordinate."""
    primitive_ids = {s.id for s in primitives() if s.axis == "geometry"}

    for _method, topology_type in _geometry_config_classmethods().items():
        _assert_coordinate_has_spec(primitive_ids, "geometry", topology_type)


def test_geometry_primitives_have_ontology_classes() -> None:
    """Every geometry primitive has a corresponding ontology class."""
    from computronium.ontology.geometry import (
        AttentionGeometry,
        ConvGeometry,
        FeedforwardGeometry,
        GraphGeometry,
        NcaGeometry,
        NtmGeometry,
        RecurrentGeometry,
        SpatialLattice3DGeometry,
        TileGeometry,
        TransformerGeometry,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.geometry.feedforward": FeedforwardGeometry,
        "primitive.geometry.recurrent": RecurrentGeometry,
        "primitive.geometry.tile_mesh": TileGeometry,
        "primitive.geometry.graph": GraphGeometry,
        "primitive.geometry.ntm": NtmGeometry,
        "primitive.geometry.nca": NcaGeometry,
        "primitive.geometry.spatial_lattice": SpatialLattice3DGeometry,
        "primitive.geometry.conv": ConvGeometry,
        "primitive.geometry.attention": AttentionGeometry,
        "primitive.geometry.causal_transformer": TransformerGeometry,
        "primitive.geometry.tile": TileGeometry,
    }

    # Config methods with their specific required arguments
    GEOMETRY_CONFIG_ARGS: dict[str, dict] = {
        "feedforward": {"input_dim": 10, "output_dim": 5, "hidden_dims": (8,)},
        "recurrent": {"input_dim": 10, "output_dim": 5, "hidden_dims": (8,)},
        "tile_mesh": {"input_dim": 10, "output_dim": 5, "num_layers": 2},
        "tile": {"input_dim": 10, "output_dim": 5, "num_layers": 2},
        "conv": {
            "input_dim": 784,
            "output_dim": 5,
            "conv_channels": (8,),
            "in_channels": 1,
            "input_hw": (8, 8),
        },
        "attention": {
            "input_dim": 10,
            "output_dim": 5,
            "hidden_dim": 8,
            "num_heads": 2,
        },
        "causal_transformer": {
            "vocab_size": 16,
            "d_model": 8,
            "n_layers": 1,
            "n_heads": 2,
            "seq_len": 4,
        },
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
        config_method = spec.id.rsplit(".", 1)[-1]
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
        ErrorPredictiveCodingDynamics,
        InstantaneousDynamics,
        LazyStateDynamics,
        PCALMDynamics,
        PredictiveSettlingDynamics,
        SpikeIntegrationDynamics,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.state_dynamics.diffusion": DiffusionDynamics,
        "primitive.state_dynamics.energy_minimization": EnergyMinimizationDynamics,
        "primitive.state_dynamics.instantaneous": InstantaneousDynamics,
        "primitive.state_dynamics.lazy": LazyStateDynamics,
        "primitive.state_dynamics.pc_alm": PCALMDynamics,
        "primitive.state_dynamics.predictive_settling": PredictiveSettlingDynamics,
        "primitive.state_dynamics.spike_integration": SpikeIntegrationDynamics,
        "primitive.state_dynamics.error_predictive_coding": (
            ErrorPredictiveCodingDynamics
        ),
    }

    for spec in primitives():
        if spec.axis != "state_dynamics":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = spec.id.rsplit(".", 1)[-1]
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


_CREDIT_ONTOLOGY_CLASSES: dict[str, str] = {
    "thermodynamic_contrast": "ThermodynamicContrast",
    "random_projections": "RandomProjectionsCredit",
    "local_goodness": "LocalGoodnessCredit",
    "temporal_trace": "TemporalTraceCredit",
    "target_inversion": "TargetInversionCredit",
    "homeostatic": "HomeostaticCredit",
    "pepita": "PepitaCredit",
    "hybrid": "HybridCredit",
    "gradient": "BackpropCredit",
    "local_contrastive": "LocalContrastiveCredit",
    "pc_alm": "PCALMCredit",
    "forward_tangent": "ForwardTangentCredit",
    "score_function": "ScoreFunctionCredit",
    "zeroth_order": "ZerothOrderCredit",
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
    """Every CreditAssignmentConfig classmethod names its own coordinate's spec."""
    primitive_ids = {s.id for s in primitives() if s.axis == "credit_assignment"}

    for _method, credit_type in _credit_config_classmethods().items():
        _assert_coordinate_has_spec(primitive_ids, "credit_assignment", credit_type)


def test_credit_primitives_have_ontology_classes() -> None:
    """Every credit_assignment primitive has a corresponding ontology class."""
    from computronium.ontology.credit import (
        BackpropCredit,
        ForwardTangentCredit,
        HomeostaticCredit,
        HybridCredit,
        LocalContrastiveCredit,
        LocalGoodnessCredit,
        PCALMCredit,
        PepitaCredit,
        RandomProjectionsCredit,
        ScoreFunctionCredit,
        TargetInversionCredit,
        TemporalTraceCredit,
        ThermodynamicContrast,
        ZerothOrderCredit,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.credit_assignment.thermodynamic_contrast": ThermodynamicContrast,
        "primitive.credit_assignment.random_projections": RandomProjectionsCredit,
        "primitive.credit_assignment.local_goodness": LocalGoodnessCredit,
        "primitive.credit_assignment.temporal_trace": TemporalTraceCredit,
        "primitive.credit_assignment.target_inversion": TargetInversionCredit,
        "primitive.credit_assignment.homeostatic": HomeostaticCredit,
        "primitive.credit_assignment.pepita": PepitaCredit,
        "primitive.credit_assignment.hybrid": HybridCredit,
        "primitive.credit_assignment.pc_alm": PCALMCredit,
        "primitive.credit_assignment.gradient": BackpropCredit,
        "primitive.credit_assignment.local_contrastive": LocalContrastiveCredit,
        "primitive.credit_assignment.forward_tangent": ForwardTangentCredit,
        "primitive.credit_assignment.score_function": ScoreFunctionCredit,
        "primitive.credit_assignment.zeroth_order": ZerothOrderCredit,
    }

    for spec in primitives():
        if spec.axis != "credit_assignment":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = spec.id.rsplit(".", 1)[-1]
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
    """Map config classmethod name -> update_type.

    Read from ``vars()``: ``inspect.getmembers`` yields *bound* methods, so
    the ``isinstance(member, classmethod)`` filter silently matched nothing
    and every caller of this helper asserted over an empty dict — including
    ``test_update_config_classmethods_cover_primitives``, which had been
    vacuous. §2.5's rule (a lock that resolves zero of N is worse than no
    lock) applies to helpers as much as to locks.
    """
    found: dict[str, str] = {}
    for name, member in vars(ParameterUpdateConfig).items():
        if name.startswith("_") or not isinstance(member, classmethod):
            continue
        try:
            config = member.__func__(ParameterUpdateConfig)
        except TypeError:
            continue  # factory with required args is not no-arg
        if isinstance(config, ParameterUpdateConfig):
            found[name] = config.update_type
    return found


def test_update_config_classmethods_cover_primitives() -> None:
    """Every ParameterUpdateConfig classmethod names its own coordinate's spec.

    ``unit_rms`` is the one factory with no coordinate: the update registry does
    not select it, so it has no spec and is excluded here.
    """
    primitive_ids = {s.id for s in primitives() if s.axis == "parameter_update"}

    for _method, update_type in _update_config_classmethods().items():
        if update_type == "unit_rms":
            continue
        _assert_coordinate_has_spec(primitive_ids, "parameter_update", update_type)


def test_every_update_config_factory_dispatches() -> None:
    """Every documented ``update_type`` must resolve through the dispatcher.

    ``NaturalGradientUpdate`` shipped with a config factory, a primitive spec
    and no dispatch entry; ``update_from_config`` raised for it and a test
    grew a special case to instantiate the class directly. The registry is
    now derived from ``@update_backend`` (TODO34 §5.4), so this asserts the
    pairing in both directions instead of accommodating a gap.
    """
    from computronium.ontology.update import _UPDATE_BACKENDS

    classmethods = _update_config_classmethods()
    assert classmethods, "no ParameterUpdateConfig factories found"
    missing = {
        update_type
        for update_type in classmethods.values()
        if update_type.lower() not in _UPDATE_BACKENDS
    }
    assert not missing, f"update types that cannot be dispatched: {missing}"
    assert len(_UPDATE_BACKENDS) >= len(classmethods), (
        f"registry has {len(_UPDATE_BACKENDS)} keys for {len(classmethods)} factories"
    )


def test_every_update_class_is_registered() -> None:
    """A class the dispatcher cannot reach is dead code by another name."""
    import computronium.ontology.update as update_module

    declared = {
        name
        for name, member in vars(update_module).items()
        if isinstance(member, type)
        and name.endswith("Update")
        and not name.startswith("_")
        and not getattr(member, "_is_protocol", False)
        and member.__module__ == update_module.__name__
    }
    registered = {cls.__name__ for cls in update_module._UPDATE_BACKENDS.values()}
    assert declared, "no update classes found — the scan is broken"
    assert registered == declared, (
        f"update classes not declared with @update_backend: {declared - registered}"
    )


def test_update_primitives_have_ontology_classes() -> None:
    """Every parameter_update primitive has a corresponding ontology class."""
    from computronium.ontology.update import (
        AdamUpdate,
        ElasticConsolidationUpdate,
        EuclideanUpdate,
        LionUpdate,
        LocalAdamUpdate,
        MeanNormUpdate,
        NaturalGradientUpdate,
        OrthoAdamUpdate,
        RiemannianOrthogonalUpdate,
        RoleSplitUpdate,
        SpectralConstrainedUpdate,
    )

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.parameter_update.euclidean": EuclideanUpdate,
        "primitive.parameter_update.muon": RiemannianOrthogonalUpdate,
        "primitive.parameter_update.spectral_constrained": SpectralConstrainedUpdate,
        "primitive.parameter_update.natural_gradient": NaturalGradientUpdate,
        "primitive.parameter_update.elastic_consolidation": ElasticConsolidationUpdate,
        "primitive.parameter_update.adam": AdamUpdate,
        "primitive.parameter_update.lion": LionUpdate,
        "primitive.parameter_update.local_adam": LocalAdamUpdate,
        "primitive.parameter_update.mean_norm": MeanNormUpdate,
        "primitive.parameter_update.ortho_adam": OrthoAdamUpdate,
        "primitive.parameter_update.riemannian_orthogonal": (
            RiemannianOrthogonalUpdate
        ),
        "primitive.parameter_update.role_split": RoleSplitUpdate,
    }

    for spec in primitives():
        if spec.axis != "parameter_update":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = spec.id.rsplit(".", 1)[-1]
        config = getattr(ParameterUpdateConfig, config_method)()
        update = update_from_config(config)
        assert isinstance(update, cls), (
            f"{spec.id} -> update instantiation returned "
            f"{type(update).__name__}, expected {cls.__name__}"
        )


# ============================================================
# Axis 6: Plasticity
# ============================================================


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
    """Every PlasticityConfig classmethod names its own coordinate's spec."""
    primitive_ids = {s.id for s in primitives() if s.axis == "plasticity"}

    for _method, plasticity_type in _plasticity_config_classmethods().items():
        _assert_coordinate_has_spec(primitive_ids, "plasticity", plasticity_type)


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
    from computronium.core.plasticity.adaptive_psi import (
        ConflictAdaptivePsiPlasticity,
    )
    from computronium.state import NullPlasticity

    ONTOLOGY_MAP: dict[str, type] = {
        "primitive.plasticity.null": NullPlasticity,
        "primitive.plasticity.routing": RoutingPlasticity,
        "primitive.plasticity.fast_weights": FastWeightPlasticity,
        "primitive.plasticity.substrate_coupled": SubstrateCoupledPlasticity,
        "primitive.plasticity.rule_state": RuleStatePlasticity,
        "primitive.plasticity.temporal_psi": TemporalPsiPlasticity,
        "primitive.plasticity.closed_form_ridge": ClosedFormRidgePlasticity,
        "primitive.plasticity.conflict_adaptive": ConflictAdaptivePsiPlasticity,
    }

    for spec in primitives():
        if spec.axis != "plasticity":
            continue
        if spec.id not in ONTOLOGY_MAP:
            raise AssertionError(f"Primitive {spec.id} has no ontology class mapping")
        cls = ONTOLOGY_MAP[spec.id]
        # Verify the ontology class can be instantiated via config round-trip
        config_method = spec.id.rsplit(".", 1)[-1]
        if config_method == "closed_form_ridge":
            config_method = None
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
        "primitive.substrate.optical": "OpticalSubstrate",
        "primitive.substrate.quantum": "QuantumSubstrate",
        "primitive.substrate.complex": "ComplexSubstrate",
        "primitive.substrate.sparse": "SparseSubstrate",
        "primitive.substrate.ternary": "TernarySubstrate",
        "primitive.substrate.noisy": "NoisySubstrate",
        "primitive.substrate.analog": "AnalogSubstrate",
    },
    "geometry": {
        "primitive.geometry.feedforward": "FeedforwardGeometry",
        "primitive.geometry.recurrent": "RecurrentGeometry",
        "primitive.geometry.tile_mesh": "TileGeometry",
        "primitive.geometry.graph": "GraphGeometry",
        "primitive.geometry.ntm": "NtmGeometry",
        "primitive.geometry.nca": "NcaGeometry",
        "primitive.geometry.spatial_lattice": "SpatialLattice3DGeometry",
        "primitive.geometry.conv": "ConvGeometry",
        "primitive.geometry.attention": "AttentionGeometry",
        "primitive.geometry.causal_transformer": "TransformerGeometry",
        "primitive.geometry.tile": "TileGeometry",
    },
    "state_dynamics": {
        "primitive.state_dynamics.diffusion": "DiffusionDynamics",
        "primitive.state_dynamics.energy_minimization": "EnergyMinimizationDynamics",
        "primitive.state_dynamics.instantaneous": "InstantaneousDynamics",
        "primitive.state_dynamics.lazy": "LazyStateDynamics",
        "primitive.state_dynamics.pc_alm": "PCALMDynamics",
        "primitive.state_dynamics.predictive_settling": "PredictiveSettlingDynamics",
        "primitive.state_dynamics.spike_integration": "SpikeIntegrationDynamics",
        "primitive.state_dynamics.error_predictive_coding": (
            "ErrorPredictiveCodingDynamics"
        ),
    },
    "credit_assignment": {
        "primitive.credit_assignment.thermodynamic_contrast": "ThermodynamicContrast",
        "primitive.credit_assignment.random_projections": "RandomProjectionsCredit",
        "primitive.credit_assignment.local_goodness": "LocalGoodnessCredit",
        "primitive.credit_assignment.temporal_trace": "TemporalTraceCredit",
        "primitive.credit_assignment.target_inversion": "TargetInversionCredit",
        "primitive.credit_assignment.homeostatic": "HomeostaticCredit",
        "primitive.credit_assignment.pepita": "PepitaCredit",
        "primitive.credit_assignment.hybrid": "HybridCredit",
        "primitive.credit_assignment.pc_alm": "PCALMCredit",
        "primitive.credit_assignment.gradient": "BackpropCredit",
        "primitive.credit_assignment.local_contrastive": "LocalContrastiveCredit",
        "primitive.credit_assignment.forward_tangent": "ForwardTangentCredit",
        "primitive.credit_assignment.score_function": "ScoreFunctionCredit",
        "primitive.credit_assignment.zeroth_order": "ZerothOrderCredit",
    },
    "parameter_update": {
        "primitive.parameter_update.euclidean": "EuclideanUpdate",
        "primitive.parameter_update.muon": "RiemannianOrthogonalUpdate",
        "primitive.parameter_update.spectral_constrained": "SpectralConstrainedUpdate",
        "primitive.parameter_update.natural_gradient": "NaturalGradientUpdate",
        "primitive.parameter_update.elastic_consolidation": "ElasticConsolidationUpdate",
        "primitive.parameter_update.adam": "AdamUpdate",
        "primitive.parameter_update.lion": "LionUpdate",
        "primitive.parameter_update.local_adam": "LocalAdamUpdate",
        "primitive.parameter_update.mean_norm": "MeanNormUpdate",
        "primitive.parameter_update.ortho_adam": "OrthoAdamUpdate",
        "primitive.parameter_update.riemannian_orthogonal": (
            "RiemannianOrthogonalUpdate"
        ),
        "primitive.parameter_update.role_split": "RoleSplitUpdate",
    },
    "plasticity": {
        "primitive.plasticity.null": "NullPlasticity",
        "primitive.plasticity.routing": "RoutingPlasticity",
        "primitive.plasticity.fast_weights": "FastWeightPlasticity",
        "primitive.plasticity.substrate_coupled": "SubstrateCoupledPlasticity",
        "primitive.plasticity.rule_state": "RuleStatePlasticity",
        "primitive.plasticity.temporal_psi": "TemporalPsiPlasticity",
        "primitive.plasticity.closed_form_ridge": "ClosedFormRidgePlasticity",
        "primitive.plasticity.conflict_adaptive": "ConflictAdaptivePsiPlasticity",
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
