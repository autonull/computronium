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

# A spec ID *is* its runtime coordinate, so the expected primitive name is
# derived rather than translated (TODO91 S1b).
_AXIS_SLUG = {
    "geometry": "geometry",
    "state_dynamics": "state_dynamics",
    "credit_assignment": "credit_assignment",
    "parameter_update": "parameter_update",
    "plasticity": "plasticity",
}


def _primitive_for(axis: str, coordinate: str) -> str:
    """The same-named primitive spec a dispatch coordinate names."""
    return f"primitive.{_AXIS_SLUG[axis]}.{coordinate}"


def _axis_of_primitive(spec_id: str) -> str | None:
    """The dispatch axis a primitive spec ID names, or None if it names none.

    A spec ID's middle segment is the spec's own axis label, which is the
    dispatch axis name for the five composed axes.
    """
    parts = spec_id.split(".")
    if len(parts) != 3 or parts[0] != "primitive":
        return None
    return parts[1] if parts[1] in DISPATCH_AXES else None


def _map_coordinate_to_primitives(
    coordinate: tuple[str, str, str, str, str],
) -> dict[str, str]:
    """Map a dispatch coordinate to the primitive spec each axis names."""
    topology, dynamics, credit, update, plasticity = coordinate
    return {
        "geometry": _primitive_for("geometry", topology),
        "state_dynamics": _primitive_for("state_dynamics", dynamics),
        "credit_assignment": _primitive_for("credit_assignment", credit),
        "parameter_update": _primitive_for("parameter_update", update),
        "plasticity": _primitive_for("plasticity", plasticity),
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
            axis = _axis_of_primitive(declared_primitive)
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
            axis = _axis_of_primitive(declared_primitive)
            assert axis is not None, declared_primitive
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

    def test_fast_weight_uses_fast_weights_plasticity(self) -> None:
        """Fast weight must declare the fast_weights plasticity coordinate."""
        system = _build_algorithm_system("fast_weight")
        coordinate = key_of(system)
        # plasticity is at index 4
        assert coordinate[4] == "fast_weights", (
            f"fast_weight plasticity axis is {coordinate[4]!r}, expected 'fast_weights'"
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
