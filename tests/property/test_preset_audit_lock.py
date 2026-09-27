"""Preset Audit Lock: spec axes ≡ factory composed axes (TODO38 §4 commit 1).

This lock builds each preset and reads back the composed axes, asserting they
match the spec's `uses_primitives`. It catches the defect class where a spec
and its factory agree with each other but both contradict the algorithm
(e.g. hebbian using local_goodness instead of temporal_trace).
"""

import importlib
from typing import TYPE_CHECKING

import pytest

from computronium.acceleration.coordinate import DISPATCH_AXES, key_of
from computronium.acceleration.registry import get as get_spec
from computronium.algorithms import _ALGORITHMS

if TYPE_CHECKING:
    from computronium.ontology import System

# Mapping from config values to primitive names (from test_registry_completeness_lock.py)
_TOPOLOGY_TO_PRIMITIVE = {
    "feedforward": "primitive.geometry.feedforward_dag",
    "causal_transformer": "primitive.geometry.feedforward_dag",
    "recurrent": "primitive.geometry.recurrent_attractor",
    "tile_mesh": "primitive.geometry.tile_mesh",
    "conv": "primitive.geometry.feedforward_dag",
    "graph": "primitive.geometry.fabric_pc",
    "attention": "primitive.geometry.feedforward_dag",
    "spatial_lattice": "primitive.geometry.spatial_lattice_3d",
    "nca": "primitive.geometry.nca",
    "ntm": "primitive.geometry.ntm",
}

_DYNAMICS_TO_PRIMITIVE = {
    "instantaneous": "primitive.state_dynamics.instantaneous_pass",
    "energy_minimization": "primitive.state_dynamics.energy_minimization",
    "predictive_settling": "primitive.state_dynamics.predictive_settling",
    "spike_integration": "primitive.state_dynamics.spike_integration",
    "diffusion": "primitive.state_dynamics.diffusion",
    "pc_alm": "primitive.state_dynamics.pc_alm_settling",
    "lazy": "primitive.state_dynamics.lazy_state_dynamics",
    "error_predictive_coding": "primitive.state_dynamics.error_predictive_coding",
}

_CREDIT_TO_PRIMITIVE = {
    "gradient": "primitive.credit_assignment.reverse_mode",
    "thermodynamic_contrast": "primitive.credit_assignment.thermodynamic_contrast",
    "random_projections": "primitive.credit_assignment.random_projections",
    "local_goodness": "primitive.credit_assignment.local_goodness",
    "temporal_trace": "primitive.credit_assignment.temporal_trace",
    "target_inversion": "primitive.credit_assignment.target_inversion",
    "homeostatic": "primitive.credit_assignment.homeostatic",
    "pepita": "primitive.credit_assignment.pepita",
    "pc_alm": "primitive.credit_assignment.pc_alm",
    "local_contrastive": "primitive.credit_assignment.local_goodness",
}

_UPDATE_TO_PRIMITIVE = {
    "euclidean": "primitive.parameter_update.euclidean",
    "riemannian_orthogonal": "primitive.parameter_update.muon",
    "muon": "primitive.parameter_update.muon",
    "spectral_constrained": "primitive.parameter_update.spectral_constrained",
    "mean_norm": "primitive.parameter_update.euclidean",
    "elastic_consolidation": "primitive.parameter_update.elastic_consolidation",
    "natural_gradient": "primitive.parameter_update.natural_gradient",
    "adam": "primitive.parameter_update.euclidean",
    "ortho_adam": "primitive.parameter_update.muon",
    "unit_rms": "primitive.parameter_update.euclidean",
    "local_adam": "primitive.parameter_update.euclidean",
    "lion": "primitive.parameter_update.euclidean",
    "role_split": "primitive.parameter_update.role_split",
}

_PLASTICITY_TO_PRIMITIVE = {
    "null": "primitive.plasticity.null",
    "routing": "primitive.plasticity.routing",
    "fast_weight": "primitive.plasticity.fast_weight",
    "substrate_coupled": "primitive.plasticity.substrate_coupled",
    "rule_state": "primitive.plasticity.rule_state",
    "temporal_psi": "primitive.plasticity.temporal_psi",
    "conflict_adaptive": "primitive.plasticity.temporal_psi",
}

_AXIS_TO_PRIMITIVE_MAP = {
    "geometry": _TOPOLOGY_TO_PRIMITIVE,
    "state_dynamics": _DYNAMICS_TO_PRIMITIVE,
    "credit_assignment": _CREDIT_TO_PRIMITIVE,
    "parameter_update": _UPDATE_TO_PRIMITIVE,
    "plasticity": _PLASTICITY_TO_PRIMITIVE,
}

_PRIMITIVE_TO_AXIS = {
    **dict.fromkeys(_TOPOLOGY_TO_PRIMITIVE.values(), "geometry"),
    **dict.fromkeys(_DYNAMICS_TO_PRIMITIVE.values(), "state_dynamics"),
    **dict.fromkeys(_CREDIT_TO_PRIMITIVE.values(), "credit_assignment"),
    **dict.fromkeys(_UPDATE_TO_PRIMITIVE.values(), "parameter_update"),
    **dict.fromkeys(_PLASTICITY_TO_PRIMITIVE.values(), "plasticity"),
}


def _map_coordinate_to_primitives(
    coordinate: tuple[str, str, str, str, str],
) -> dict[str, str]:
    """Map a dispatch coordinate to the expected primitive names by axis."""
    topology, dynamics, credit, update, plasticity = coordinate
    return {
        "geometry": _TOPOLOGY_TO_PRIMITIVE[topology],
        "state_dynamics": _DYNAMICS_TO_PRIMITIVE[dynamics],
        "credit_assignment": _CREDIT_TO_PRIMITIVE[credit],
        "parameter_update": _UPDATE_TO_PRIMITIVE[update],
        "plasticity": _PLASTICITY_TO_PRIMITIVE[plasticity],
    }


def _build_algorithm_system(name: str) -> System:
    """Build a system for the given algorithm using its public factory."""
    module = importlib.import_module(f"computronium.algorithms.{name}.factory")
    factory = next(
        v
        for k, v in vars(module).items()
        if k.startswith("create_") and k.endswith("_mlp")
    )
    return factory(input_dim=8, hidden_dims=(16,), output_dim=4)


class TestPresetAuditLock:
    """Verify every algorithm spec's uses_primitives matches its factory's composition."""

    @pytest.mark.parametrize("name", sorted(_ALGORITHMS))
    def test_spec_matches_factory(self, name: str) -> None:
        """The spec's uses_primitives must match the axes the factory composes."""
        # Build the system and get its coordinate
        system = _build_algorithm_system(name)
        coordinate = key_of(system)

        # Map coordinate to expected primitives by axis
        expected_by_axis = _map_coordinate_to_primitives(coordinate)

        # Get the spec's declared primitives
        spec = get_spec(f"algorithm.{name}")
        declared = spec.uses_primitives

        # Check each declared primitive matches the factory's composition for its axis
        for declared_primitive in declared:
            axis = _PRIMITIVE_TO_AXIS.get(declared_primitive)
            if axis is None:
                pytest.fail(
                    f"{name}: unknown primitive {declared_primitive!r} in uses_primitives"
                )
            expected = expected_by_axis[axis]
            assert declared_primitive == expected, (
                f"{name}: spec declares {declared_primitive!r} for axis {axis} "
                f"but factory composes {expected!r} "
                f"(coordinate: {dict(zip(DISPATCH_AXES, coordinate, strict=True))})"
            )

        # The spec should not declare more than one primitive per axis
        seen_axes = set()
        for declared_primitive in declared:
            axis = _PRIMITIVE_TO_AXIS[declared_primitive]
            assert axis not in seen_axes, (
                f"{name}: duplicate axis {axis} in uses_primitives"
            )
            seen_axes.add(axis)

    def test_hebbian_uses_temporal_trace_not_local_goodness(self) -> None:
        """Regression test for the hebbian collision (TODO38 §4 commit 1).

        Hebbian must use temporal_trace (STDP), not local_goodness (FF).
        """
        system = _build_algorithm_system("hebbian")
        coordinate = key_of(system)
        # credit is at index 2
        assert coordinate[2] == "temporal_trace", (
            f"hebbian credit axis is {coordinate[2]!r}, expected 'temporal_trace'"
        )

    def test_pepita_uses_pepita_not_local_goodness(self) -> None:
        """Regression test for the pepita spec mismatch (TODO38 §4 commit 1).

        PEPITA spec must declare pepita credit, not local_goodness.
        """
        system = _build_algorithm_system("pepita")
        coordinate = key_of(system)
        # credit is at index 2
        assert coordinate[2] == "pepita", (
            f"pepita credit axis is {coordinate[2]!r}, expected 'pepita'"
        )

    def test_fast_weight_uses_fast_weight_plasticity(self) -> None:
        """Fast weight must declare fast_weight plasticity."""
        system = _build_algorithm_system("fast_weight")
        coordinate = key_of(system)
        # plasticity is at index 4
        assert coordinate[4] == "fast_weight", (
            f"fast_weight plasticity axis is {coordinate[4]!r}, expected 'fast_weight'"
        )

    def test_tile_uses_tile_mesh_geometry(self) -> None:
        """Tile must declare tile_mesh geometry."""
        system = _build_algorithm_system("tile")
        coordinate = key_of(system)
        # geometry is at index 0
        assert coordinate[0] == "tile_mesh", (
            f"tile geometry axis is {coordinate[0]!r}, expected 'tile_mesh'"
        )

    def test_backprop_uses_gradient_credit(self) -> None:
        """Backprop must declare gradient (reverse_mode) credit."""
        system = _build_algorithm_system("backprop")
        coordinate = key_of(system)
        assert coordinate[2] == "gradient", (
            f"backprop credit axis is {coordinate[2]!r}, expected 'gradient'"
        )

    def test_eqprop_uses_thermodynamic_contrast(self) -> None:
        """EqProp must declare thermodynamic_contrast credit."""
        system = _build_algorithm_system("eqprop")
        coordinate = key_of(system)
        assert coordinate[2] == "thermodynamic_contrast", (
            f"eqprop credit axis is {coordinate[2]!r}, expected 'thermodynamic_contrast'"
        )

    def test_pc_uses_predictive_settling_and_local_goodness(self) -> None:
        """PC must declare predictive_settling dynamics and local_goodness credit."""
        system = _build_algorithm_system("pc")
        coordinate = key_of(system)
        assert coordinate[1] == "predictive_settling", (
            f"pc dynamics axis is {coordinate[1]!r}, expected 'predictive_settling'"
        )
        assert coordinate[2] == "local_goodness", (
            f"pc credit axis is {coordinate[2]!r}, expected 'local_goodness'"
        )

    def test_routing_uses_routing_plasticity(self) -> None:
        """Routing (MEP) must declare routing plasticity."""
        system = _build_algorithm_system("routing")
        coordinate = key_of(system)
        assert coordinate[4] == "routing", (
            f"routing plasticity axis is {coordinate[4]!r}, expected 'routing'"
        )
