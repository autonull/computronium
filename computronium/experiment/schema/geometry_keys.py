"""The composer's geometry key vocabulary — the exact names geometry reads.

Geometry is the one axis whose config is built by a normalizer rather than a
factory. The normalizer reads a fixed key vocabulary; a geometry hyperparameter
is a key in that vocabulary, declared by ``GeometryConfig.hyperparameters()``
under the same name, so a swept value is one the builder reads with no
translation (TODO61 §11.1).

The vocabulary lives here — one module — so the schema that declares geometry
hyperparameters and the composer that reads them agree by construction. The
search space reads it as ``AxisSpec.accepted_params``; composition reads the
same predicate as ``for_axis``. A geometry knob that names no key here is
consumed by nobody, and the wiring lock says so instead of dropping it silently.
"""

from __future__ import annotations

from typing import Final

COMMON_GEOMETRY_KEYS: Final[frozenset[str]] = frozenset({
    "hidden_dim",
    "num_layers",
    "init_scheme",
    "init_scale",
})

TOPOLOGY_KEYS: Final[dict[str, frozenset[str]]] = {
    "feedforward": frozenset({"residual"}),
    "recurrent": frozenset(),
    "tile": frozenset({"neurons_per_tile", "tiles_per_layer"}),
    "tile_mesh": frozenset({"neurons_per_tile", "tiles_per_layer"}),
    "attention": frozenset({"num_heads", "head_dim"}),
    "spatial_lattice": frozenset({"lattice_dims", "connectivity_radius"}),
    "nca": frozenset({"grid_hw", "delta_scale", "mask_prob"}),
    "ntm": frozenset({"mem_slots", "mem_width"}),
    "conv": frozenset({
        "conv_channels",
        "kernel_size",
        "in_channels",
        "input_hw",
        "pool_hw",
    }),
    "graph": frozenset({"edge_index"}),
    "causal_transformer": frozenset({"num_heads", "seq_len"}),
}

# Geometry values the task determines; never taken from a swept hyperparameter.
TASK_SHAPED_GEOMETRY_KEYS: Final[frozenset[str]] = frozenset({
    "input_dim",
    "output_dim",
})


def allowed_geometry_keys(topology: str) -> frozenset[str]:
    """The composer keys a topology's normalizer reads."""
    return COMMON_GEOMETRY_KEYS | TOPOLOGY_KEYS.get(topology, frozenset())


def geometry_consumes_name(name: str, topology: str) -> bool:
    """Whether the composer reads geometry hyperparameter ``name``."""
    return name not in TASK_SHAPED_GEOMETRY_KEYS and name in allowed_geometry_keys(
        topology
    )


def geometry_accepted_params(topology: str) -> frozenset[str]:
    """The names a topology's normalizer reads, for ``accepted_params``.

    The set is a superset of the declared geometry hyperparameters — the
    composer also reads keys the task supplies (``edge_index``) — which is
    harmless: the caller intersects it with the declared specs.
    """
    return allowed_geometry_keys(topology)


__all__ = [
    "COMMON_GEOMETRY_KEYS",
    "TASK_SHAPED_GEOMETRY_KEYS",
    "TOPOLOGY_KEYS",
    "allowed_geometry_keys",
    "geometry_accepted_params",
    "geometry_consumes_name",
]
