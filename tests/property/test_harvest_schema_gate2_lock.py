"""Lockstep test: harvest_schema() ⊇ Gate-2 union (WP2).

This test verifies that the harvested tunable schema includes all parameters
from the Gate 2 frozen union table (Appendix IV + §13.2 additions).

NOTE: Currently harvest_schema() does not yet harvest from ontology primitives
(the _get_primitive_class() returns None). This test documents the expected
union and verifies the harvest mechanism works without conflicts. Once the
ontology primitive connection is implemented (WP2 completion), this test
will assert full coverage.
"""

from __future__ import annotations

from computronium.experiment.schema.harvest import harvest_schema
from computronium.experiment.schema.seed_registries import seed_all_registries

# Gate 2 frozen union table (from Appendix IV + §13.2 additions)
# 37 unique parameters from six implementations' hyperparameter spaces
GATE_2_UNION = frozenset({
    # Learning rate variants
    "learning_rate",
    "layer_lr",
    "classifier_lr",
    "target_lr",
    # Regularization
    "weight_decay",
    # Architecture
    "hidden_dim",
    "num_layers",
    "cube_size",
    # Energy-based / settling
    "beta",
    "step_size",
    "max_steps",
    "convergence_threshold",
    "convergence_start",
    "damping",
    "tol",
    "momentum",
    "update_scale",
    "update_scale_by_depth",
    "w_rec_init",
    "w_rec_gain",
    # Feedback alignment
    "feedback_gain",
    "feedback_init_gain",
    "feedback_mode",
    "use_spectral_norm",
    # Sparse / routing
    "sparse_ratio",
    "alpha",
    # Spiking
    "num_steps",
    "tau_mem",
    "tau_syn",
    "spike_threshold",
    "refractory_period",
    "dt",
    "spike_grad",
    # Threshold / activation
    "threshold",
    # PC-ALM
    "rho",
    "prospective_leak",
    # Hebbian
    "use_oja",
    # Gate 2 additions (§13.2)
    "batch_size",
    "adam_beta1",
    "adam_beta2",
    "muon_momentum",
    "apply_constraints_max_hidden",
    "apply_constraints_max_layers",
    "apply_constraints_max_steps",
})


def test_gate_2_union_count() -> None:
    """Verify Gate 2 union has expected size (37 + 7 = 44)."""
    # 37 from Appendix IV + 7 from §13.2 additions
    assert len(GATE_2_UNION) == 44


def test_harvest_schema_has_no_conflicts() -> None:
    """Verify harvest_schema() produces no ConflictingTunableError."""
    seed_all_registries()
    # This should not raise ConflictingTunableError
    schema = harvest_schema()
    assert schema.version == 1


def test_harvest_schema_structure() -> None:
    """Verify harvest_schema() returns valid structure."""
    seed_all_registries()
    schema = harvest_schema()

    # Should have axis kind order
    assert len(schema.axis_kind_order) == 6
    assert schema.axis_kind_order[0].value == "substrate"
    assert schema.axis_kind_order[5].value == "update"

    # Should have tunables list (currently empty until ontology connection)
    assert isinstance(schema.tunables, tuple)


def test_harvest_schema_to_dict_roundtrip() -> None:
    """Verify harvest_schema() can serialize and deserialize."""
    seed_all_registries()
    schema = harvest_schema()

    data = schema.to_dict()
    assert data["version"] == 1
    assert "axis_kind_order" in data
    assert "tunables" in data

    # Round-trip
    restored = schema.from_dict(data)
    assert restored.version == schema.version
    assert restored.axis_kind_order == schema.axis_kind_order
    assert len(restored.tunables) == len(schema.tunables)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
