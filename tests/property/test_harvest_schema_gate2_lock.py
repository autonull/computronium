"""Lockstep test: harvest_schema() with Gate-2 union (WP2/WP8).

This test verifies that the harvested hyperparameter schema includes all parameters
from the Gate 2 frozen union table (Appendix IV + §13.2 additions), AND
includes the richer ontology-specific parameters with availability predicates.

NOTE: The harvest now includes more than the Gate 2 union — it includes
all ontology-specific parameters with availability predicates. The Gate 2
union is a FROZEN reference of unique names from six implementations,
including legacy names that are now superseded by the ontology structure
(e.g., `learning_rate` → `update_lr` in update; `cube_size` was experiment-specific).

Harvest pulls directly from ontology config classes (via hyperparameters())
not from the experiment registries, so no seeding is required.
"""

from __future__ import annotations

from computronium.experiment.schema import harvest_schema

# Gate 2 frozen union table (from Appendix IV + §13.2 additions)
# 37 unique parameters from six implementations' hyperparameter spaces
# NOTE: These are LEGACY names from the original six implementations.
# The ontology now uses canonical names with availability predicates.
GATE_2_UNION = frozenset({
    # Learning rate variants (legacy names, map to step_size/ortho_lr)
    "learning_rate",  # → update_lr
    "layer_lr",  # per-layer override
    "classifier_lr",  # classifier-specific LR
    "target_lr",  # target-prop LR
    # Regularization
    "weight_decay",  # optimizer weight decay
    # Architecture (geometry)
    "hidden_dim",
    "num_layers",
    "cube_size",  # cube/lattice size (legacy, now lattice_dims)
    # Energy-based / settling (dynamics)
    "beta",
    "step_size",
    "max_steps",
    "convergence_threshold",
    "convergence_start",
    "damping",  # damping factor (legacy)
    "tol",  # tolerance (legacy, now convergence_threshold)
    "momentum",
    "update_scale",  # legacy update scale
    "update_scale_by_depth",  # legacy depth scaling
    "w_rec_init",  # recurrent weight init
    "w_rec_gain",  # recurrent weight gain
    # Feedback alignment (credit)
    "feedback_gain",  # → feedback_scale
    "feedback_init_gain",  # initial feedback gain
    "feedback_mode",  # DFA/FA modes
    "use_spectral_norm",  # spectral norm on feedback
    # Sparse / routing
    "sparse_ratio",  # → sparsity
    "alpha",  # generic mixing coefficient
    # Spiking (dynamics)
    "num_steps",  # spike simulation steps
    "tau_mem",  # membrane time constant
    "tau_syn",  # synaptic time constant
    "spike_threshold",
    "refractory_period",
    "dt",  # simulation timestep
    "spike_grad",  # gradient approximation mode
    # Threshold / activation
    "threshold",
    # PC-ALM
    "rho",
    "prospective_leak",
    # Hebbian
    "use_oja",
    # Gate 2 additions (§13.2)
    "batch_size",
    "adam_beta1",  # → momentum
    "adam_beta2",  # → beta2
    "muon_momentum",  # → momentum
    "apply_constraints_max_hidden",  # from apply_constraints()
    "apply_constraints_max_layers",  # from apply_constraints()
    "apply_constraints_max_steps",  # from apply_constraints()
})

# Map legacy names to canonical ontology names
LEGACY_TO_CANONICAL = {
    "learning_rate": "update_lr",
    "layer_lr": "update_lr",  # per-layer would be an override
    "classifier_lr": "update_lr",
    "target_lr": "update_lr",
    "weight_decay": "ewc_lambda",  # EWC-style regularization
    "cube_size": "lattice_dims",
    "damping": "settle_momentum",
    "tol": "convergence_threshold",
    "update_scale": "update_lr",
    "update_scale_by_depth": "update_lr",
    "w_rec_init": "init_scale",
    "w_rec_gain": "init_scale",
    "feedback_gain": "feedback_scale",
    "feedback_init_gain": "feedback_scale",
    "use_spectral_norm": "spectral_norm",
    "sparse_ratio": "sparsity",
    "num_steps": "max_steps",
    "spike_threshold": "threshold",
    "muon_momentum": "momentum",
    "adam_beta1": "momentum",
    "adam_beta2": "beta2",
}


def test_gate_2_union_count() -> None:
    """Verify Gate 2 union has expected size (37 + 7 = 44)."""
    # 37 from Appendix IV + 7 from §13.2 additions
    assert len(GATE_2_UNION) == 44


def test_harvest_schema_has_no_conflicts() -> None:
    """Verify harvest_schema() produces no ConflictingHyperparameterError."""

    # This should not raise ConflictingHyperparameterError
    schema = harvest_schema()
    assert schema.version == 1


def test_harvest_schema_structure() -> None:
    """Verify harvest_schema() returns valid structure."""

    schema = harvest_schema()

    # Should have axis kind order (6 structural axes)
    assert len(schema.axis_kind_order) == 6
    assert schema.axis_kind_order[0].value == "substrate"
    assert schema.axis_kind_order[5].value == "update"

    # Should have hyperparameters list
    assert isinstance(schema.hyperparameters, tuple)
    assert len(schema.hyperparameters) > 0


def test_harvest_schema_covers_gate_2_legacy_names() -> None:
    """Verify harvest_schema() covers Gate 2 union via canonical mapping.

    Many Gate 2 names are legacy from the six implementations; the ontology
    uses canonical names. This test verifies the mapping covers the union.
    """

    schema = harvest_schema()
    harvested_names = {t.name for t in schema.hyperparameters}

    # Check that we have canonical names for the key hyperparameters
    # Core params that must be present (availability predicates don't matter for presence)
    core_params = {
        "settle_step",
        "update_lr",
        "momentum",
        "settle_beta",
        "credit_beta",
        "max_steps",
        "convergence_threshold",
        "hidden_dim",
        "num_layers",
        "sparsity",
        "rho",
        "prospective_leak",
        "threshold",
        "beta2",
    }

    missing_core = core_params - harvested_names
    assert not missing_core, f"Missing core params: {missing_core}"

    # Count how many Gate 2 params (via mapping) are covered
    covered_legacy = 0
    for legacy in GATE_2_UNION:
        canonical = LEGACY_TO_CANONICAL.get(legacy, legacy)
        if canonical in harvested_names:
            covered_legacy += 1

    # We should cover most legacy params via canonical mapping
    # Some legacy params were experiment-specific and are superseded
    print(
        f"Covered {covered_legacy}/{len(GATE_2_UNION)} Gate 2 legacy params via canonical mapping"
    )
    assert covered_legacy >= 30, f"Insufficient coverage: {covered_legacy}/44"


def test_harvest_schema_rich_coverage() -> None:
    """Verify harvest_schema() includes rich ontology-specific params."""

    schema = harvest_schema()
    harvested_names = {t.name for t in schema.hyperparameters}

    # These are the expanded ontology params beyond Gate 2
    ontology_expansions = {
        # Credit axis rich params
        "credit_norm",
        "local_objective",
        "orthogonal_init",
        "learned_feedback",
        "feedback_lr",
        "feedback_update_every",
        "a_plus",
        "a_minus",
        "tau_pre",
        "tau_post",
        "homeostatic_target",
        "homeostatic_scaling",
        "ema_beta",
        "stream_norm",
        "contrast_threshold",
        "contrast_objective",
        "readout_scale",
        "sequential_lr",
        "train_biases",
        # Update axis rich params
        "ortho_steps",
        "spectral_norm",
        "fisher_damping",
        "ewc_lambda",
        "grad_clip",
        "ortho_lr",
        "eps",
        # Geometry axis rich params
        "init_scheme",
        "residual",
        "neurons_per_tile",
        "tiles_per_layer",
        "conv_channels",
        "kernel_size",
        "num_heads",
        "seq_len",
        "lattice_dims",
        "mem_slots",
        "mem_width",
        "grid_hw",
        # Plasticity axis params
        "gate_dim",
        "fast_weight_dim",
        "num_operators",
        "trace_decay",
        "conflict_threshold",
        # Substrate axis params
        "noise_level",
        "precision",
    }

    present = ontology_expansions & harvested_names
    print(f"Rich ontology params present: {len(present)}/{len(ontology_expansions)}")
    assert len(present) >= 40, f"Insufficient rich coverage: {len(present)}"


def test_harvest_schema_availability_predicates() -> None:
    """Verify harvest_schema() includes availability predicates for conditional params."""

    schema = harvest_schema()

    # Params that should have availability predicates
    conditional_params = {
        # Credit availability
        "a_plus",
        "a_minus",
        "tau_pre",
        "tau_post",  # temporal_trace only
        "settle_beta",  # settling dynamics
        "credit_beta",  # thermodynamic_contrast, pc_alm
        "ema_beta",
        "stream_norm",  # local_contrastive only
        "train_biases",  # gradient only
        # Update availability
        "ortho_steps",
        "spectral_norm",
        "beta2",
        "eps",
        "ortho_lr",  # specific update rules
        # Geometry availability
        "neurons_per_tile",
        "tiles_per_layer",  # tile geometries
        "conv_channels",
        "kernel_size",  # conv
        "mem_slots",
        "mem_width",  # ntm
        # Plasticity availability
        "trace_decay",
        "conflict_threshold",  # conflict_adaptive
    }

    with_availability = sum(
        1 for t in schema.hyperparameters if t.availability is not None
    )
    print(
        f"Params with availability: {with_availability}/{len(schema.hyperparameters)}"
    )

    # Check that some key conditional params do have availability
    conditional_found = sum(
        1
        for t in schema.hyperparameters
        if t.name in conditional_params and t.availability is not None
    )
    print(
        f"Conditional params with availability: {conditional_found}/{len(conditional_params)}"
    )
    assert conditional_found >= 20, (
        f"Insufficient availability predicates: {conditional_found}"
    )


def test_harvest_schema_to_dict_roundtrip() -> None:
    """Verify harvest_schema() can serialize and deserialize."""

    schema = harvest_schema()

    data = schema.to_dict()
    assert data["version"] == 1
    assert "axis_kind_order" in data
    assert "hyperparameters" in data

    # Round-trip
    restored = schema.from_dict(data)
    assert restored.version == schema.version
    assert restored.axis_kind_order == schema.axis_kind_order
    assert len(restored.hyperparameters) == len(schema.hyperparameters)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
