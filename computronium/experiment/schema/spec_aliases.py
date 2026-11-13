"""Spec-ID to runtime-coordinate aliases (TODO91 S1).

The implementation matrix names primitives by their historical *spec* ID;
``AXES_REGISTRIES`` names the coordinate a run selects. The two vocabularies
drifted because nothing joined them: ``feedforward_dag`` shipped as
``feedforward``, ``photonic`` as ``optical``, ``reverse_mode`` as ``gradient``.
This module is the one table that says which spec ID selects which runtime
coordinate, so the inventory, the docs lock, and any future selector read the
same answer.

An entry is one of three kinds:

* identity — the spec's last segment is the runtime name (most rows);
* alias — :data:`SPEC_RUNTIME_ALIASES` names the runtime coordinate;
* not a primitive — :data:`NOT_A_PRIMITIVE` records why a shipped mechanism has
  no composable coordinate. A spec ID absent from the runtime registry and
  without a row here is a defect, not a fallback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from computronium.experiment.schema.axis import StructuralAxis

if TYPE_CHECKING:
    from computronium.acceleration.spec import ImplementationSpec

__all__ = [
    "NOT_A_PRIMITIVE",
    "SPEC_AXIS",
    "SPEC_RUNTIME_ALIASES",
    "runtime_name_for",
]

# ImplementationSpec.axis (the spec vocabulary) -> StructuralAxis (the runtime
# vocabulary). Kept explicit because the two spellings differ for three axes.
SPEC_AXIS: Final[dict[str, StructuralAxis]] = {
    "substrate": StructuralAxis.SUBSTRATE,
    "geometry": StructuralAxis.GEOMETRY,
    "state_dynamics": StructuralAxis.DYNAMICS,
    "plasticity": StructuralAxis.PLASTICITY,
    "credit_assignment": StructuralAxis.CREDIT,
    "parameter_update": StructuralAxis.UPDATE,
}

# Spec IDs whose runtime coordinate is not their own last segment.
SPEC_RUNTIME_ALIASES: Final[dict[str, str]] = {
    # A noisy substrate is the digital substrate configured with noise; there
    # is no separate runtime coordinate.
    "primitive.substrate.noisy": "digital",
    "primitive.substrate.photonic": "optical",
    "primitive.geometry.feedforward_dag": "feedforward",
    "primitive.geometry.recurrent_attractor": "recurrent",
    "primitive.geometry.spatial_lattice_3d": "spatial_lattice",
    # fabric_pc is the spec name for the graph topology; GraphGeometry is the
    # runtime implementation. One implementation, one coordinate.
    "primitive.geometry.fabric_pc": "graph",
    "primitive.state_dynamics.instantaneous_pass": "instantaneous",
    "primitive.state_dynamics.lazy_state_dynamics": "lazy",
    "primitive.state_dynamics.pc_alm_settling": "pc_alm",
    "primitive.plasticity.fast_weight": "fast_weights",
    "primitive.credit_assignment.reverse_mode": "gradient",
}

# Spec rows whose mechanism ships but has no composable axis coordinate.
NOT_A_PRIMITIVE: Final[dict[str, str]] = {
    "primitive.plasticity.closed_form_ridge": (
        "no axis coordinate: reachable only as "
        "core.plasticity.closed_form_ridge.create_closed_form_ridge_plasticity, "
        "which method cards call; the axis composes plasticity through "
        "core.joint.transition.PlasticityConfig"
    ),
}


def runtime_name_for(spec: ImplementationSpec) -> str | None:
    """Return the runtime coordinate a primitive spec selects, if any."""
    from computronium.experiment.schema.axis import AXES_REGISTRIES

    if spec.id in NOT_A_PRIMITIVE:
        return None
    axis = SPEC_AXIS.get(spec.axis or "")
    if axis is None:
        msg = (
            f"spec {spec.id!r} names axis {spec.axis!r}, which is absent from "
            f"SPEC_AXIS; add the axis or a not-a-primitive row"
        )
        raise ValueError(msg)
    name = SPEC_RUNTIME_ALIASES.get(spec.id, spec.id.rsplit(".", 1)[-1])
    return name if name in AXES_REGISTRIES[axis] else None
