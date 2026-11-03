"""Lock: SystemConfig.validate() rejects known incompatible primitive pairs.

WS1.3 acceptance: Zero EvaluationError for known-incompatible combos (caught at admission gate).
"""

from __future__ import annotations

import pytest

from computronium.ontology.system import (
    SystemConfig,
    check_compatibility_matrix,
    COMPATIBILITY_MATRIX,
)
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium.state import PlasticityConfig


def _base_config(
    substrate: str = "digital",
    geometry: str = "feedforward",
    dynamics: str = "energy_minimization",
    plasticity: str = "null",
    credit: str = "thermodynamic_contrast",
    update: str = "euclidean",
) -> SystemConfig:
    """Create a valid base SystemConfig for testing."""
    return SystemConfig(
        substrate=SubstrateConfig.digital() if substrate == "digital" else SubstrateConfig.analog(),
        geometry=GeometryConfig.feedforward(input_dim=64, output_dim=10, hidden_dims=[128, 64])
        if geometry == "feedforward"
        else GeometryConfig.recurrent(input_dim=64, output_dim=10, hidden_dim=128),
        dynamics=StateDynamicsConfig.energy_minimization()
        if dynamics == "energy_minimization"
        else StateDynamicsConfig.instantaneous(),
        plasticity=PlasticityConfig.null()
        if plasticity == "null"
        else PlasticityConfig.fast_weights(fast_weight_dim=64, decay=0.9, learning_rate=0.1),
        credit=CreditAssignmentConfig.thermodynamic_contrast()
        if credit == "thermodynamic_contrast"
        else CreditAssignmentConfig.gradient(),
        update=ParameterUpdateConfig.euclidean()
        if update == "euclidean"
        else ParameterUpdateConfig.adam(),
    )


class TestPrimitiveCompatibilityLock:
    """Tests enforcing primitive compatibility matrix at admission gate."""

    # Substrate-Dynamics incompatibilities from TODO78 Appendix
    @pytest.mark.parametrize(
        "substrate,dynamics",
        [
            ("quantum", "pc_alm"),
            ("quantum", "spike_integration"),
            ("neuromorphic", "error_predictive_coding"),
            ("ternary", "spike_integration"),
            ("ternary", "pc_alm"),
            ("complex", "spike_integration"),
        ],
    )
    def test_substrate_dynamics_incompatibilities_rejected(self, substrate: str, dynamics: str) -> None:
        """Known substrate-dynamics incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate=substrate,
            geometry="feedforward",
            dynamics=dynamics,
            plasticity="null",
            credit="thermodynamic_contrast",
            update="euclidean",
        )
        assert len(violations) > 0, f"Expected violation for {substrate}/{dynamics}"
        assert any("incompatible" in v.lower() for v in violations)

    # Substrate-Geometry incompatibilities
    @pytest.mark.parametrize(
        "substrate,geometry",
        [
            ("quantum", "attention"),
            ("quantum", "ntm"),
            ("neuromorphic", "attention"),
            ("ternary", "ntm"),
            ("sparse", "attention"),
            ("analog", "ntm"),
        ],
    )
    def test_substrate_geometry_incompatibilities_rejected(self, substrate: str, geometry: str) -> None:
        """Known substrate-geometry incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate=substrate,
            geometry=geometry,
            dynamics="energy_minimization",
            plasticity="null",
            credit="thermodynamic_contrast",
            update="euclidean",
        )
        assert len(violations) > 0, f"Expected violation for {substrate}/{geometry}"
        assert any("incompatible" in v.lower() for v in violations)

    # Substrate-Plasticity incompatibilities
    @pytest.mark.parametrize(
        "substrate,plasticity",
        [
            ("quantum", "fast_weights"),
            ("neuromorphic", "substrate_coupled"),
            ("ternary", "temporal_psi"),
        ],
    )
    def test_substrate_plasticity_incompatibilities_rejected(self, substrate: str, plasticity: str) -> None:
        """Known substrate-plasticity incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate=substrate,
            geometry="feedforward",
            dynamics="energy_minimization",
            plasticity=plasticity,
            credit="thermodynamic_contrast",
            update="euclidean",
        )
        assert len(violations) > 0, f"Expected violation for {substrate}/{plasticity}"
        assert any("incompatible" in v.lower() for v in violations)

    # Dynamics-Geometry incompatibilities
    @pytest.mark.parametrize(
        "dynamics,geometry",
        [
            ("pc_alm", "attention"),
            ("pc_alm", "ntm"),
            ("spike_integration", "attention"),
            ("spike_integration", "ntm"),
            ("spike_integration", "spatial_lattice"),
            ("spike_integration", "graph"),
            ("spike_integration", "conv"),
            ("spike_integration", "nca"),
            ("diffusion", "attention"),
            ("diffusion", "ntm"),
            ("diffusion", "spatial_lattice"),
            ("diffusion", "graph"),
            ("diffusion", "conv"),
            ("diffusion", "nca"),
            ("diffusion", "tile"),
            ("diffusion", "tile_mesh"),
            ("diffusion", "causal_transformer"),
            ("error_predictive_coding", "attention"),
            ("error_predictive_coding", "ntm"),
            ("error_predictive_coding", "nca"),
            ("error_predictive_coding", "causal_transformer"),
            ("predictive_settling", "attention"),
            ("predictive_settling", "ntm"),
            ("predictive_settling", "nca"),
            ("predictive_settling", "causal_transformer"),
        ],
    )
    def test_dynamics_geometry_incompatibilities_rejected(self, dynamics: str, geometry: str) -> None:
        """Known dynamics-geometry incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate="digital",
            geometry=geometry,
            dynamics=dynamics,
            plasticity="null",
            credit="thermodynamic_contrast",
            update="euclidean",
        )
        assert len(violations) > 0, f"Expected violation for {dynamics}/{geometry}"
        assert any("incompatible" in v.lower() for v in violations)

    # Dynamics-Plasticity incompatibilities
    @pytest.mark.parametrize(
        "dynamics,plasticity",
        [
            ("pc_alm", "fast_weights"),
            ("pc_alm", "substrate_coupled"),
            ("spike_integration", "fast_weights"),
            ("spike_integration", "substrate_coupled"),
            ("spike_integration", "temporal_psi"),
            ("diffusion", "fast_weights"),
            ("error_predictive_coding", "fast_weights"),
        ],
    )
    def test_dynamics_plasticity_incompatibilities_rejected(self, dynamics: str, plasticity: str) -> None:
        """Known dynamics-plasticity incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate="digital",
            geometry="feedforward",
            dynamics=dynamics,
            plasticity=plasticity,
            credit="thermodynamic_contrast",
            update="euclidean",
        )
        assert len(violations) > 0, f"Expected violation for {dynamics}/{plasticity}"
        assert any("incompatible" in v.lower() for v in violations)

    # Credit-Dynamics incompatibilities
    @pytest.mark.parametrize(
        "credit,dynamics",
        [
            ("gradient", "diffusion"),
            ("gradient", "spike_integration"),
            ("backprop", "diffusion"),
            ("backprop", "spike_integration"),
            ("thermodynamic_contrast", "spike_integration"),
            ("thermodynamic_contrast", "instantaneous"),
            ("thermodynamic_contrast", "lazy"),
            ("equilibrium", "spike_integration"),
            ("equilibrium", "instantaneous"),
            ("equilibrium", "lazy"),
            ("local_goodness", "spike_integration"),
            ("forward_only", "spike_integration"),
            ("temporal_trace", "instantaneous"),
            ("temporal_trace", "energy_minimization"),
            ("temporal_trace", "lazy"),
            ("temporal_trace", "diffusion"),
            ("temporal_trace", "error_predictive_coding"),
            ("temporal_trace", "pc_alm"),
            ("target_inversion", "energy_minimization"),
            ("target_inversion", "lazy"),
            ("target_inversion", "diffusion"),
            ("target_inversion", "error_predictive_coding"),
            ("target_inversion", "pc_alm"),
            ("target_prop", "energy_minimization"),
            ("target_prop", "lazy"),
            ("target_prop", "diffusion"),
            ("target_prop", "error_predictive_coding"),
            ("target_prop", "pc_alm"),
            ("pepita", "spike_integration"),
            ("pepita", "diffusion"),
            ("local_contrastive", "spike_integration"),
            ("local_contrastive", "diffusion"),
            ("random_projections", "spike_integration"),
            ("random_projections", "diffusion"),
            ("homeostatic", "spike_integration"),
            ("homeostatic", "diffusion"),
        ],
    )
    def test_credit_dynamics_incompatibilities_rejected(self, credit: str, dynamics: str) -> None:
        """Known credit-dynamics incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate="digital",
            geometry="feedforward",
            dynamics=dynamics,
            plasticity="null",
            credit=credit,
            update="euclidean",
        )
        assert len(violations) > 0, f"Expected violation for {credit}/{dynamics}"
        assert any("incompatible" in v.lower() for v in violations)

    # Credit-Geometry incompatibilities
    @pytest.mark.parametrize(
        "credit,geometry",
        [
            ("local_contrastive", "attention"),
            ("local_contrastive", "causal_transformer"),
        ],
    )
    def test_credit_geometry_incompatibilities_rejected(self, credit: str, geometry: str) -> None:
        """Known credit-geometry incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate="digital",
            geometry=geometry,
            dynamics="energy_minimization",
            plasticity="null",
            credit=credit,
            update="euclidean",
        )
        assert len(violations) > 0, f"Expected violation for {credit}/{geometry}"
        assert any("incompatible" in v.lower() for v in violations)

    # Update-Substrate incompatibilities
    @pytest.mark.parametrize(
        "update,substrate",
        [
            ("riemannian_orthogonal", "sparse"),
            ("spectral_constrained", "sparse"),
        ],
    )
    def test_update_substrate_incompatibilities_rejected(self, update: str, substrate: str) -> None:
        """Known update-substrate incompatibilities are rejected by compatibility matrix."""
        violations = check_compatibility_matrix(
            substrate=substrate,
            geometry="feedforward",
            dynamics="energy_minimization",
            plasticity="null",
            credit="thermodynamic_contrast",
            update=update,
        )
        assert len(violations) > 0, f"Expected violation for {update}/{substrate}"
        assert any("incompatible" in v.lower() for v in violations)

    def test_compatible_combinations_pass(self) -> None:
        """Known compatible combinations pass the compatibility matrix."""
        # Digital + feedforward + energy_minimization + null + thermodynamic_contrast + euclidean
        violations = check_compatibility_matrix(
            substrate="digital",
            geometry="feedforward",
            dynamics="energy_minimization",
            plasticity="null",
            credit="thermodynamic_contrast",
            update="euclidean",
        )
        assert len(violations) == 0, f"Compatible combo rejected: {violations}"

        # Digital + feedforward + instantaneous + null + gradient + adam
        violations = check_compatibility_matrix(
            substrate="digital",
            geometry="feedforward",
            dynamics="instantaneous",
            plasticity="null",
            credit="gradient",
            update="adam",
        )
        assert len(violations) == 0, f"Compatible combo rejected: {violations}"

    def test_system_config_validate_catches_incompatibilities(self) -> None:
        """SystemConfig.validate() rejects known incompatible combinations."""
        # Create a config with known incompatibility: quantum + spike_integration
        # Use temporal_trace credit which is compatible with spike_integration
        config = SystemConfig(
            substrate=SubstrateConfig.quantum(),
            geometry=GeometryConfig.feedforward(input_dim=64, output_dim=10, hidden_dims=[128, 64]),
            dynamics=StateDynamicsConfig.spike_integration(),
            plasticity=PlasticityConfig.null(),
            credit=CreditAssignmentConfig.temporal_trace(),
            update=ParameterUpdateConfig.euclidean(),
        )

        with pytest.raises(ValueError, match="requires"):
            config.validate()

    def test_system_config_validate_allows_compatible(self) -> None:
        """SystemConfig.validate() allows compatible combinations."""
        config = _base_config()
        config.validate()  # Should not raise

    def test_compatibility_matrix_completeness(self) -> None:
        """COMPATIBILITY_MATRIX contains all expected categories."""
        expected_categories = {
            "substrate_dynamics",
            "substrate_geometry",
            "substrate_plasticity",
            "dynamics_geometry",
            "dynamics_plasticity",
            "geometry_dynamics",
            "geometry_plasticity",
            "credit_dynamics",
            "credit_geometry",
            "update_substrate",
        }
        assert set(COMPATIBILITY_MATRIX.keys()) == expected_categories

    def test_admission_gate_uses_compatibility_matrix(self) -> None:
        """Admission gate (pipeline) uses check_compatibility_matrix for fast rejection."""
        # This test verifies the integration point exists
        from computronium.experiment.execution.pipeline._stages import _StageMixin

        # The _fresh_batch_items method calls check_compatibility_matrix
        # We can't easily test the full pipeline here, but we can verify
        # the function is imported and used in the pipeline module
        import computronium.experiment.execution.pipeline._stages as stages_module

        # Check that check_compatibility_matrix is imported in the pipeline module
        import inspect
        source = inspect.getsource(stages_module)
        assert "check_compatibility_matrix" in source
        assert "ADMISSION_REJECTED" in source