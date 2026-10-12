"""Width contract lock (TODO57 D3).

The search space must reject geometry↔plasticity pairs with activation layout
mismatches. The ActivationLayout schema must be the single source of truth for
activation shapes consumed by plasticity, credit, and readout. Removing the
void constraints or layout awareness must make the fixture fail (TODO46 D25).
"""

from __future__ import annotations

import pytest
import torch
from computronium.core.plasticity.fast_weights import FastWeightPlasticity
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.kernel.search_space import _composable
from computronium.experiment.schema import Coordinate
from computronium.experiment.kernel.evaluate import task_shape
from computronium.ontology.geometry import (
    GeometryConfig,
    ActivationLayout,
    LayerLayout,
    geometry_from_config,
)


def test_activation_layout_all_geometries() -> None:
    """Every geometry backend must implement activation_layout."""
    from computronium.ontology.geometry import _GEOMETRY_BACKENDS

    for topology_type, backend in _GEOMETRY_BACKENDS.items():
        # Skip abstract/base entries
        if topology_type in ("tile_block",):
            continue
        # Create a minimal config for this topology
        config = _minimal_config_for_topology(topology_type)
        if config is None:
            continue
        geom = backend.build(config)
        layout = geom.activation_layout(batch_size=4)
        assert isinstance(layout, ActivationLayout), (
            f"{topology_type}: activation_layout must return ActivationLayout"
        )
        assert layout.batch_size == 4
        assert len(layout.layers) > 0, f"{topology_type}: must have at least one layer"
        # Every layer must have a valid batch_mode
        for layer in layout.layers:
            assert layer.batch_mode in ("sample", "cell", "sequence")
            assert isinstance(layer.feature_shape, tuple)
            assert all(d >= 0 for d in layer.feature_shape)
        # Must have a readout layer
        readout = layout.readout_layer()
        assert readout is not None, f"{topology_type}: must have a readout layer"
        assert readout.is_readout


def _minimal_config_for_topology(topology_type: str) -> GeometryConfig | None:
    """Create a minimal valid config for a topology type."""
    match topology_type:
        case "feedforward":
            return GeometryConfig.feedforward(input_dim=10, output_dim=5, hidden_dims=(16,))
        case "causal_transformer":
            return GeometryConfig.causal_transformer(vocab_size=32, d_model=64, n_layers=2, n_heads=4, seq_len=16)
        case "recurrent" | "recurrent_attractor":
            return GeometryConfig.recurrent(input_dim=10, output_dim=5, hidden_dims=(16,))
        case "tile" | "tile_mesh":
            return GeometryConfig.tile_mesh(input_dim=10, output_dim=5, num_layers=3, neurons_per_tile=8, tiles_per_layer=2)
        case "conv":
            return GeometryConfig.conv(input_dim=784, output_dim=10, conv_channels=(8, 16), kernel_size=3, in_channels=1, input_hw=(28, 28), pool_hw=(4, 4))
        case "graph":
            return GeometryConfig.graph(input_dim=16, output_dim=5, edge_index=[[0, 1], [1, 0]], hidden_dims=(32,))
        case "attention":
            return GeometryConfig.attention(input_dim=64, output_dim=10, hidden_dim=64, num_layers=2, num_heads=4)
        case "spatial_lattice":
            return GeometryConfig.spatial_lattice(input_dim=64, output_dim=10, lattice_dims=(4, 4, 4), hidden_dims=(32, 32))
        case "nca":
            return GeometryConfig.nca(channels=8, hidden=16, grid_hw=(8, 8), output_dim=10)
        case "ntm":
            return GeometryConfig.ntm(input_dim=16, output_dim=10, hidden=32, mem_slots=16, mem_width=8)
        case _:
            return None


def test_nca_activation_layout_cell_mode() -> None:
    """NCA geometry must use cell-mode batch for its internal layers."""
    config = GeometryConfig.nca(channels=8, hidden=16, grid_hw=(8, 8), output_dim=10)
    geom = geometry_from_config(config)
    layout = geom.activation_layout(batch_size=4)

    # First three layers (perceived, hidden, delta) should be cell-mode
    perceived = layout.get_layer("perceived")
    hidden = layout.get_layer("hidden")
    delta = layout.get_layer("delta")
    assert perceived is not None and perceived.batch_mode == "cell"
    assert hidden is not None and hidden.batch_mode == "cell"
    assert delta is not None and delta.batch_mode == "cell"

    # Readout should be sample-mode
    readout = layout.readout_layer()
    assert readout is not None and readout.batch_mode == "sample"

    # Spatial dims must be set
    assert layout.spatial_dims == (8, 8)


def test_ntm_activation_layout_sample_mode() -> None:
    """NTM geometry must use sample-mode batch for all layers."""
    config = GeometryConfig.ntm(input_dim=16, output_dim=10, hidden=32, mem_slots=16, mem_width=8)
    geom = geometry_from_config(config)
    layout = geom.activation_layout(batch_size=4)

    for layer in layout.layers:
        assert layer.batch_mode == "sample", f"NTM layer {layer.name} must be sample-mode"

    # No spatial dims for NTM
    assert layout.spatial_dims is None


def test_tile_activation_layout_sample_mode() -> None:
    """Tile geometry must use sample-mode batch for all layers."""
    config = GeometryConfig.tile_mesh(input_dim=10, output_dim=5, num_layers=3, neurons_per_tile=8, tiles_per_layer=2)
    geom = geometry_from_config(config)
    layout = geom.activation_layout(batch_size=4)

    for layer in layout.layers:
        assert layer.batch_mode == "sample", f"Tile layer {layer.name} must be sample-mode"


def test_void_constraint_nca_ntm_fast_weights() -> None:
    """NCA/NTM geometries with fast_weights plasticity must be rejected by void constraint."""
    # NCA + fast_weights
    coord = Coordinate(
        substrate="digital",
        geometry="nca",
        dynamics="instantaneous",
        plasticity="fast_weights",
        credit="gradient",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is False, "NCA + fast_weights must be rejected by void constraint"

    # NTM + fast_weights
    coord = Coordinate(
        substrate="digital",
        geometry="ntm",
        dynamics="instantaneous",
        plasticity="fast_weights",
        credit="gradient",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is False, "NTM + fast_weights must be rejected by void constraint"


def test_void_constraint_tile_fast_weights() -> None:
    """Tile/tile_mesh geometries with fast_weights plasticity must be rejected by void constraint."""
    # tile + fast_weights
    coord = Coordinate(
        substrate="digital",
        geometry="tile",
        dynamics="instantaneous",
        plasticity="fast_weights",
        credit="gradient",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is False, "Tile + fast_weights must be rejected by void constraint"

    # tile_mesh + fast_weights
    coord = Coordinate(
        substrate="digital",
        geometry="tile_mesh",
        dynamics="instantaneous",
        plasticity="fast_weights",
        credit="gradient",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is False, "Tile_mesh + fast_weights must be rejected by void constraint"


def test_fast_weights_modulate_with_layout() -> None:
    """FastWeightPlasticity.modulate must use layout for feature matching and batch tiling."""
    # Create a geometry with sample-mode layers
    config = GeometryConfig.feedforward(input_dim=64, output_dim=10, hidden_dims=(32, 32))
    geom = geometry_from_config(config)
    layout = geom.activation_layout(batch_size=4)

    # Create fast weights plasticity
    fw = FastWeightPlasticity(fast_weight_dim=512, decay=0.9, learning_rate=0.1)
    psi = fw.initial_psi(None, batch_size=4)

    # Create dummy activations matching the layout
    activations = []
    for layer in layout.layers:
        if layer.batch_mode == "sample":
            act = torch.randn(4, *layer.feature_shape)
        else:
            act = torch.randn(4 * 8 * 8, *layer.feature_shape)  # cell-mode
        activations.append(act)

    # Modulate with layout
    modulated = fw.modulate(activations, psi, layout=layout)

    # Check output shapes match input shapes
    assert isinstance(modulated, list)
    assert len(modulated) == len(activations)
    for i, (orig, mod) in enumerate(zip(activations, modulated)):
        assert orig.shape == mod.shape, f"Layer {i}: shape mismatch {orig.shape} vs {mod.shape}"


def test_fast_weights_modulate_cell_mode_tiling() -> None:
    """FastWeightPlasticity.modulate must tile fast_weights for cell-mode layers."""
    # Create NCA geometry (cell-mode)
    config = GeometryConfig.nca(channels=8, hidden=16, grid_hw=(8, 8), output_dim=10)
    geom = geometry_from_config(config)
    layout = geom.activation_layout(batch_size=4)

    # Create fast weights plasticity
    fw = FastWeightPlasticity(fast_weight_dim=128, decay=0.9, learning_rate=0.1)
    psi = fw.initial_psi(None, batch_size=4)

    # Create dummy activations - cell-mode layers have B*H*W batch
    h, w = layout.spatial_dims
    activations = []
    for layer in layout.layers:
        if layer.batch_mode == "cell":
            act = torch.randn(4 * h * w, *layer.feature_shape)
        else:
            act = torch.randn(4, *layer.feature_shape)
        activations.append(act)

    # Modulate with layout
    modulated = fw.modulate(activations, psi, layout=layout)

    # Check output shapes match input shapes
    assert isinstance(modulated, list)
    assert len(modulated) == len(activations)
    for i, (orig, mod) in enumerate(zip(activations, modulated)):
        assert orig.shape == mod.shape, f"Layer {i}: shape mismatch {orig.shape} vs {mod.shape}"


def test_fast_weights_modulate_feature_truncate_pad() -> None:
    """FastWeightPlasticity.modulate must truncate/pad fast_weights to match feature dim."""
    config = GeometryConfig.feedforward(input_dim=64, output_dim=10, hidden_dims=(32, 32))
    geom = geometry_from_config(config)
    layout = geom.activation_layout(batch_size=4)

    # Fast weight dim smaller than feature dim -> pad
    fw = FastWeightPlasticity(fast_weight_dim=16, decay=0.9, learning_rate=0.1)
    psi = fw.initial_psi(None, batch_size=4)
    activations = [torch.randn(4, 64), torch.randn(4, 32), torch.randn(4, 32), torch.randn(4, 10)]
    modulated = fw.modulate(activations, psi, layout=layout)
    assert all(m.shape == a.shape for m, a in zip(modulated, activations))

    # Fast weight dim larger than feature dim -> truncate
    fw = FastWeightPlasticity(fast_weight_dim=256, decay=0.9, learning_rate=0.1)
    psi = fw.initial_psi(None, batch_size=4)
    modulated = fw.modulate(activations, psi, layout=layout)
    assert all(m.shape == a.shape for m, a in zip(modulated, activations))


def test_void_constraint_removal_regression_nca_ntm() -> None:
    """If the nca_ntm_fast_weight_plasticity validation is removed from SystemConfig.validate, the fixture must fail.

    This test verifies the lock is not a comment (TODO46 D25).
    It uses temporal_trace credit (not checked by dry-run gate, compatible with NCA+instantaneous)
    and temporarily patches the validation method to always pass
    AND removes the void constraint, then asserts the search space
    then includes NCA+fast_weights for digits.
    """
    from computronium.ontology.system import SystemConfig
    from computronium.experiment.schema.seed_registries import CONSTRAINTS_REGISTRY

    # Save originals
    original_validate = SystemConfig._validate_nca_ntm_fast_weight_plasticity
    original_constraint = None
    for c in CONSTRAINTS_REGISTRY:
        if c.name == "nca_ntm_fast_weight_plasticity":
            original_constraint = c
            break

    def no_op_validate(self) -> None:
        return None  # Always pass

    try:
        # Remove void constraint
        if original_constraint is not None:
            CONSTRAINTS_REGISTRY.unregister(original_constraint.name)
        # Patch validation
        SystemConfig._validate_nca_ntm_fast_weight_plasticity = no_op_validate

        from computronium.experiment.execution import search_space as search_space_module
        search_space_module._composable_cache.clear()
        search_space_module._filter_axes_cache.clear()

        # Use temporal_trace credit with instantaneous dynamics
        # to bypass the dry-run gate (which only runs for random_projections/gradient)
        # and satisfy NCA's instantaneous dynamics requirement
        coord = Coordinate(
            substrate="digital",
            geometry="nca",
            dynamics="instantaneous",
            plasticity="fast_weights",
            credit="temporal_trace",
            update="adam",
            params={},
        )
        result = _composable(coord, "digits", task_shape, 50000)
        assert result is True, (
            "Lock broken: removing _validate_nca_ntm_fast_weight_plasticity "
            "must make NCA+fast_weights pass for digits"
        )
    finally:
        SystemConfig._validate_nca_ntm_fast_weight_plasticity = original_validate
        if original_constraint is not None:
            CONSTRAINTS_REGISTRY.register(original_constraint)
        from computronium.experiment.execution import search_space as search_space_module
        search_space_module._composable_cache.clear()
        search_space_module._filter_axes_cache.clear()


def test_void_constraint_removal_regression_tile() -> None:
    """If the tile_fast_weight_plasticity validation is removed from SystemConfig.validate, the fixture must fail.

    This test verifies the lock is not a comment (TODO46 D25).
    It uses thermodynamic_contrast credit (not checked by dry-run gate)
    and temporarily patches the validation method to always pass
    AND removes the void constraint, then asserts the search space
    then includes Tile+fast_weights for digits.
    """
    from computronium.ontology.system import SystemConfig
    from computronium.experiment.schema.seed_registries import CONSTRAINTS_REGISTRY

    # Save originals
    original_validate = SystemConfig._validate_tile_fast_weight_plasticity
    original_constraint = None
    for c in CONSTRAINTS_REGISTRY:
        if c.name == "tile_fast_weight_plasticity":
            original_constraint = c
            break

    def no_op_validate(self) -> None:
        return None  # Always pass

    try:
        # Remove void constraint
        if original_constraint is not None:
            CONSTRAINTS_REGISTRY.unregister(original_constraint.name)
        # Patch validation
        SystemConfig._validate_tile_fast_weight_plasticity = no_op_validate

        from computronium.experiment.execution import search_space as search_space_module
        search_space_module._composable_cache.clear()
        search_space_module._filter_axes_cache.clear()

        # Use thermodynamic_contrast credit with energy_minimization dynamics
        # to bypass the dry-run gate (which only runs for random_projections/gradient)
        coord = Coordinate(
            substrate="digital",
            geometry="tile",
            dynamics="energy_minimization",
            plasticity="fast_weights",
            credit="thermodynamic_contrast",
            update="euclidean",
            params={},
        )
        result = _composable(coord, "digits", task_shape, 50000)
        assert result is True, (
            "Lock broken: removing _validate_tile_fast_weight_plasticity "
            "must make Tile+fast_weights pass for digits"
        )
    finally:
        SystemConfig._validate_tile_fast_weight_plasticity = original_validate
        if original_constraint is not None:
            CONSTRAINTS_REGISTRY.register(original_constraint)
        from computronium.experiment.execution import search_space as search_space_module
        search_space_module._composable_cache.clear()
        search_space_module._filter_axes_cache.clear()


def test_fast_weights_with_compatible_geometry_accepted() -> None:
    """Fast weights with feedforward geometry must be accepted."""
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="fast_weights",
        credit="gradient",
        update="adam",
        params={},
    )
    result = _composable(coord, "digits", task_shape, 50000)
    assert result is True, "Feedforward + fast_weights must be accepted"


def test_compose_fast_weights_feedforward_works() -> None:
    """Direct compose with feedforward + fast_weights must work."""
    shape = task_shape("digits")
    coord = Coordinate(
        substrate="digital",
        geometry="feedforward",
        dynamics="instantaneous",
        plasticity="fast_weights",
        credit="gradient",
        update="adam",
        params={},
    )
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=shape.input_shape,
        output_dim=shape.output_dim,
        param_budget=50000,
    )
    assert cell is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])