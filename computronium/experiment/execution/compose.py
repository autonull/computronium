"""Kernel-native system composition for grid cells.

Composes a full grid cell (dynamics × credit × update × topology) from the
single-source config classmethods and registries — no preset tables.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Any, Final

from computronium.core.logging import get_logger
from computronium.core.system_trainer import (
    compose_joint_system_from_configs,
    compose_system_from_configs,
)
from computronium.core.system_trainer.factory import param_count
from computronium.experiment.learning.prior import apply_dynamics_step_size
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.harvest import (
    ActiveSpace,
    config_field_name,
    harvest_schema,
)
from computronium.ontology import GeometryConfig
from computronium.ontology.dynamics import StateDynamicsConfig

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.schema.coordinate import Coordinate
    from computronium.ontology import System

__all__ = [
    "GRID_CREDITS",
    "GRID_DYNAMICS",
    "GRID_UPDATES",
    "ComposedCell",
    "ProposalComposeError",
    "_fit_geometry",
    "build_geometry_config",
    "compose_cell_system",
    "compose_configs",
    "geometry_param_count",
]

logger = get_logger(__name__)

GRID_DYNAMICS: tuple[str, ...] = (
    "energy_minimization",
    "predictive_settelling",
    "error_predictive_coding",
    "spike_integration",
    "instantaneous",
    "lazy",
    "diffusion",
)

GRID_CREDITS: tuple[str, ...] = (
    "thermodynamic_contrast",
    "local_contrastive",
    "random_projections",
    "local_goodness",
    "temporal_trace",
    "target_inversion",
    "homeostatic",
    "pepita",
    "gradient",
)

GRID_UPDATES: tuple[str, ...] = (
    "euclidean",
    "adam",
    "local_adam",
    "ortho_adam",
    "lion",
    "elastic_consolidation",
    "riemannian_orthogonal",
    "muon",
    "spectral_constrained",
)

_COMMON_GEOMETRY_KEYS: Final[frozenset[str]] = frozenset({
    "hidden_dim",
    "depth",
    "init_scheme",
    "init_scale",
})

_DEFAULT_NUM_HEADS: Final[int] = 8

_TOPOLOGY_KEYS: Final[dict[str, frozenset[str]]] = {
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


class ProposalComposeError(ValueError):
    """A proposal's geometry or task could not be resolved to a runnable system."""


def _as_int(value: object, default: int) -> int:
    return int(value) if isinstance(value, int | float) else default


def _as_float(value: object, default: float) -> float:
    return float(value) if isinstance(value, int | float) else default


def _as_int_pair(value: object, default: tuple[int, int]) -> tuple[int, int]:
    if isinstance(value, list | tuple) and all(
        isinstance(v, int | float) for v in value
    ):
        result = tuple(int(v) for v in value)
        if len(result) != 2:
            return default
        return result  # type: ignore[return-value]
    return default


def _as_int_tuple(value: object, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(value, list | tuple) and all(
        isinstance(v, int | float) for v in value
    ):
        result = tuple(int(v) for v in value)
        if len(result) != 3:
            return default
        return result  # type: ignore[return-value]
    return default


def _channel_count(input_shape: tuple[int, ...]) -> int:
    """A per-example channel count: ``(3, 28, 28)`` is 3, ``(784,)`` is 1."""
    return input_shape[0] if len(input_shape) > 1 else 1


def _spatial_extent(input_shape: tuple[int, ...]) -> tuple[int, int]:
    """The height and width a spatial topology should cover."""
    return (
        (int(input_shape[-2]), int(input_shape[-1])) if len(input_shape) > 2 else (1, 1)
    )


def _estimate_spatial_lattice_params(
    lattice_dims: tuple[int, int, int],
    hidden_dims: tuple[int, ...],
    input_dim: int,
    output_dim: int,
) -> int:
    d, h, w = lattice_dims
    num_sites = d * h * w
    first_hidden = hidden_dims[0] if hidden_dims else output_dim
    input_proj_params = input_dim * num_sites * first_hidden
    site_weight_params = 0
    site_bias_params = 0
    prev_hidden = first_hidden
    for hidden in hidden_dims:
        site_weight_params += num_sites * hidden * prev_hidden
        site_bias_params += num_sites * hidden
        prev_hidden = hidden
    output_proj_params = num_sites * prev_hidden * output_dim
    return (
        input_proj_params + site_weight_params + site_bias_params + output_proj_params
    )


def _constrain_spatial_lattice_dims(
    lattice_dims: tuple[int, int, int],
    hidden_dims: tuple[int, ...],
    input_dim: int,
    output_dim: int,
    param_budget: int,
) -> tuple[int, int, int]:
    estimated = _estimate_spatial_lattice_params(
        lattice_dims, hidden_dims, input_dim, output_dim
    )
    if estimated <= param_budget:
        return lattice_dims
    d, h, w = lattice_dims
    for new_d in range(max(1, d), 0, -1):
        for new_h in range(max(1, h), 0, -1):
            for new_w in range(max(1, w), 0, -1):
                new_dims = (new_d, new_h, new_w)
                new_estimated = _estimate_spatial_lattice_params(
                    new_dims, hidden_dims, input_dim, output_dim
                )
                if new_estimated <= param_budget:
                    return new_dims
    return (1, 1, 1)


def _fit_depth(dims: tuple[int, ...], depth: int, fallback: int) -> tuple[int, ...]:
    """Widen or narrow a derived width tuple to exactly ``depth`` entries."""
    if not dims:
        return (fallback,) * depth
    if len(dims) == depth:
        return dims
    if len(dims) > depth:
        return dims[:depth]
    return dims + (dims[-1],) * (depth - len(dims))


def geometry_param_count(config: GeometryConfig) -> int:
    """Learnable parameters a geometry config actually builds.

    The ground truth, not an estimate: a ceiling enforced against an estimator
    is only as trustworthy as the estimator, and the estimator is the thing that
    has already been wrong (a conv cell sized from its channel counts alone
    ignores the spatial extent of its input).
    """
    from computronium.ontology.geometry import geometry_from_config

    return sum(p.numel() for p in geometry_from_config(config).params.values())


def _fit_geometry(
    mapping: Mapping[str, object],
    *,
    topology: str,
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int,
) -> GeometryConfig:
    """The largest derived sizing whose built geometry fits ``param_budget``.

    Derived sizing is a search over the ceiling itself, and the acceptance test
    is the built module's parameter count. With no ceiling in force this is a
    plain build, so an unconstrained run keeps the measured regime.
    """

    def build(budget: int) -> GeometryConfig:
        return build_geometry_config(
            dict(mapping),
            topology=topology,
            input_shape=input_shape,
            output_dim=output_dim,
            param_budget=budget,
        )

    if param_budget <= 0:
        return build(0)
    lo, hi, best = 1, param_budget, None
    smallest = build(lo)
    while lo <= hi:
        mid = (lo + hi) // 2
        candidate = build(mid)
        if geometry_param_count(candidate) <= param_budget:
            best = candidate
            lo = mid + 1
        else:
            hi = mid - 1
    # A cell that cannot fit even at minimum sizing is not silently enlarged:
    # the tightest cell is returned and the evaluator's gate reports it.
    return best or smallest


def _allowed_keys(topology: str) -> frozenset[str]:
    return _COMMON_GEOMETRY_KEYS | _TOPOLOGY_KEYS.get(topology, frozenset())


_TILE_TOPOLOGIES: Final[frozenset[str]] = frozenset({"tile", "tile_mesh"})

# Topologies whose width must divide evenly by the head count.
_HEAD_SPLIT_TOPOLOGIES: Final[frozenset[str]] = frozenset({
    "attention",
    "causal_transformer",
})


def _auto_size_geometry(  # ruff: ignore[complex-structure] - one branch per topology
    topology: str, param_budget: int, input_dim: int, output_dim: int, depth: int
) -> tuple[tuple[int, ...], int]:
    if param_budget <= 0:
        return (64,) * max(depth, 1), max(depth, 1)

    def estimate_params(h: int, d: int) -> int:  # ruff: ignore[too-many-return-statements]
        if topology in {"feedforward", "recurrent"}:
            return input_dim * h + max(d - 1, 0) * h * h + h * output_dim
        if topology in {"attention", "causal_transformer"}:
            return 4 * h * h * d
        if topology == "ntm":
            return h * h + 16 * 8 + h * output_dim
        if topology == "tile_mesh":
            npt = h
            tpl = max(d, 1)
            return (
                input_dim * npt
                + max(d - 1, 0) * npt * tpl * npt
                + npt * tpl * output_dim
            )
        if topology == "spatial_lattice":
            lattice_volume = 4 * 4 * 4
            return input_dim * lattice_volume * h + h * output_dim
        if topology == "nca":
            grid_area = 16 * 16
            return h * h * grid_area
        if topology == "conv":
            kernel_size = 3
            in_channels = 3
            return in_channels * h * kernel_size * kernel_size + h * output_dim
        if topology == "graph":
            num_nodes = 32
            return h * h * num_nodes
        return input_dim * h + max(d - 1, 0) * h * h + h * output_dim

    valid_configs: list[tuple[int, int]] = []
    for d in range(1, 7):
        lo, hi = 8, 512
        best_h_for_d = 0
        while lo <= hi:
            mid = (lo + hi) // 2
            if estimate_params(mid, d) <= param_budget:
                best_h_for_d = mid
                lo = mid + 1
            else:
                hi = mid - 1
        if best_h_for_d >= 8:
            valid_configs.append((d, best_h_for_d))

    if not valid_configs:
        return (8,) * max(depth, 1), max(depth, 1)

    best_d, best_h = max(valid_configs, key=lambda x: x[0] * x[1])
    return (best_h,) * best_d, best_d


def build_geometry_config(  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches, too-many-locals, too-many-statements]
    geometry: dict[str, object],
    *,
    topology: str,
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int = 0,
) -> GeometryConfig:
    """Build a ``GeometryConfig`` for one topology from a geometry mapping.

    Args:
        geometry: Topology parameters for ``topology``.
        topology: The structural geometry axis' primitive. It is an argument,
            not a key: reading it out of the mapping defaulted every topology
            to ``feedforward``, so every non-feedforward cell was compiled as
            an MLP and then rejected for carrying keys an MLP has no use for.
        input_shape: The task's own input shape, channels first.
        output_dim: Class count, from the task.
        param_budget: Parameter ceiling for derived sizing; 0 disables it.
    """
    input_dim = math.prod(input_shape)
    if topology not in _TOPOLOGY_KEYS:
        msg = f"Unknown topology {topology!r}; allowed: {sorted(_TOPOLOGY_KEYS)}"
        raise ProposalComposeError(msg)

    allowed = _allowed_keys(topology)
    unknown = frozenset(geometry) - allowed
    if unknown:
        msg = (
            f"Unknown geometry keys {sorted(unknown)} for topology {topology!r}; "
            f"allowed: {sorted(allowed)}"
        )
        raise ProposalComposeError(msg)

    explicit_hidden = "hidden_dim" in geometry
    explicit_depth = "depth" in geometry
    depth = max(_as_int(geometry.get("depth"), 2), 1)
    hidden = _as_int(geometry.get("hidden_dim"), 64)

    # Sizing is derived per component: a swept width is honoured while the
    # depth it stacks into is still derived from the ceiling, so honouring one
    # knob never silently discards the other. With no ceiling the derivation is
    # the measured regime (64 wide, 2 deep).
    derived_dims, derived_depth = _auto_size_geometry(
        topology, param_budget, input_dim, output_dim, depth
    )
    if not explicit_depth:
        depth = derived_depth
    hidden_dims = (
        (hidden,) * depth
        if explicit_hidden
        else _fit_depth(derived_dims, depth, hidden)
    )
    hidden = hidden_dims[0] if hidden_dims else hidden
    if topology in _HEAD_SPLIT_TOPOLOGIES and not explicit_hidden:
        heads = _as_int(geometry.get("num_heads"), _DEFAULT_NUM_HEADS)
        hidden = max(heads, hidden - hidden % heads)
        hidden_dims = (hidden,) * depth

    init_scheme = str(geometry.get("init_scheme", "default"))
    if init_scheme not in {"default", "mupc", "innocenti"}:
        msg = f"init_scheme must be 'default', 'mupc', or 'innocenti', got {init_scheme!r}"
        raise ProposalComposeError(msg)
    init_scale = _as_float(geometry.get("init_scale"), 0.1)

    npt = _as_int(geometry.get("neurons_per_tile"), 0)
    tpl = _as_int(geometry.get("tiles_per_layer"), 0)
    if topology in _TILE_TOPOLOGIES and param_budget > 0 and (npt == 0 or tpl == 0):
        if param_budget < 50000:
            npt = max(8, hidden // 4)
            tpl = max(2, depth // 2)
        elif param_budget < 100000:
            npt = max(16, hidden // 2)
            tpl = max(3, depth)
        else:
            npt = hidden
            tpl = depth
    if npt == 0:
        npt = _as_int(geometry.get("neurons_per_tile"), 48)
    if tpl == 0:
        tpl = _as_int(geometry.get("tiles_per_layer"), 4)

    nca_grid_hw = _as_int_pair(geometry.get("grid_hw"), _spatial_extent(input_shape))
    if topology == "nca" and param_budget > 0 and "grid_hw" not in geometry:
        # A CA grid may not exceed the task's own extent: its state contract is
        # a grid the size of the input.
        max_grid_area = max(1, param_budget // max(1, hidden * hidden))
        task_side = min(_spatial_extent(input_shape))
        grid_side = max(1, min(int(max_grid_area**0.5), task_side))
        nca_grid_hw = (grid_side, grid_side)

    conv_channels_raw = geometry.get("conv_channels")
    kernel_size = _as_int(geometry.get("kernel_size"), 3)
    # Channels and extent are the task's, not literals: a conv stack built for
    # 3x28x28 dies on a 1x8x8 task, and no gate said why.
    in_channels = _as_int(geometry.get("in_channels"), _channel_count(input_shape))
    input_hw = _as_int_pair(geometry.get("input_hw"), _spatial_extent(input_shape))
    pool_hw = _as_int_pair(geometry.get("pool_hw"), (2, 2))
    if topology == "conv" and param_budget > 0 and conv_channels_raw is None:
        base_channels = max(
            8,
            param_budget // (in_channels * kernel_size * kernel_size + output_dim * 2),
        )
        num_conv_layers = max(2, min(4, depth))
        conv_channels: tuple[int, ...] = tuple(
            max(8, base_channels // (i + 1)) for i in range(num_conv_layers)
        )
    elif conv_channels_raw is not None:
        if isinstance(conv_channels_raw, list):
            conv_channels = tuple(conv_channels_raw)
        elif isinstance(conv_channels_raw, tuple):
            conv_channels = conv_channels_raw
        else:
            conv_channels = (int(str(conv_channels_raw)),)
    else:
        conv_channels = (8, 16)

    match topology:
        case "feedforward":
            return GeometryConfig.feedforward(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden_dims=hidden_dims,
                init_scale=init_scale,
                init_scheme=init_scheme,  # type: ignore[arg-type]
                residual=bool(geometry.get("residual")),
            )
        case "recurrent":
            return GeometryConfig.recurrent(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden_dims=hidden_dims,
                init_scale=init_scale,
                init_scheme=init_scheme,  # type: ignore[arg-type]
            )
        case "tile" | "tile_mesh":
            factory = getattr(GeometryConfig, topology)
            return factory(
                input_dim=input_dim,
                output_dim=output_dim,
                num_layers=depth,
                neurons_per_tile=npt,
                tiles_per_layer=tpl,
                init_scale=init_scale,
            )
        case "attention":
            return GeometryConfig.attention(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden_dim=hidden,
                num_layers=depth,
                num_heads=_as_int(geometry.get("num_heads"), _DEFAULT_NUM_HEADS),
                init_scale=init_scale,
            )
        case "spatial_lattice":
            lattice_dims = _as_int_tuple(geometry.get("lattice_dims"), (4, 4, 4))
            constrained_hidden_dims = hidden_dims
            if param_budget > 0:
                for _ in range(3):
                    lattice_dims = _constrain_spatial_lattice_dims(
                        lattice_dims,
                        constrained_hidden_dims,
                        input_dim,
                        output_dim,
                        param_budget,
                    )
                    estimated = _estimate_spatial_lattice_params(
                        lattice_dims, constrained_hidden_dims, input_dim, output_dim
                    )
                    if estimated <= param_budget:
                        break
                    min_hidden = max(
                        1, param_budget // (input_dim * 4 + output_dim * 4 + 100)
                    )
                    constrained_hidden_dims = tuple(
                        min(h, min_hidden) for h in constrained_hidden_dims
                    )
                else:
                    constrained_hidden_dims = (1,) * len(constrained_hidden_dims)
                    lattice_dims = (1, 1, 1)
            return GeometryConfig.spatial_lattice(
                input_dim=input_dim,
                output_dim=output_dim,
                lattice_dims=lattice_dims,
                hidden_dims=constrained_hidden_dims,
                connectivity_radius=_as_int(geometry.get("connectivity_radius"), 1),
                init_scale=init_scale,
            )
        case "nca":
            # Compute channels to match input size: channels * H * W = input_dim
            # If user specifies channels in geometry, use that; otherwise derive it.
            user_channels = geometry.get("channels")
            if user_channels is not None:
                channels = _as_int(user_channels, hidden)
            else:
                h, w = nca_grid_hw
                grid_area = max(1, h * w)
                channels = max(1, input_dim // grid_area)
            return GeometryConfig.nca(
                channels=channels,
                hidden=hidden,
                grid_hw=nca_grid_hw,  # type: ignore[arg-type]
                init_scale=init_scale,
                output_dim=output_dim,
            )
        case "ntm":
            return GeometryConfig.ntm(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden=hidden,
                mem_slots=_as_int(geometry.get("mem_slots"), 16),
                mem_width=_as_int(geometry.get("mem_width"), 8),
            )
        case "conv":
            return GeometryConfig.conv(
                input_dim=input_dim,
                output_dim=output_dim,
                conv_channels=conv_channels,
                kernel_size=kernel_size,
                in_channels=in_channels,
                input_hw=input_hw,
                pool_hw=pool_hw,
                init_scale=init_scale,
            )
        case "graph":
            edge_index = geometry.get("edge_index")
            if not (
                isinstance(edge_index, list)
                and all(
                    isinstance(e, list) and all(isinstance(v, int) for v in e)
                    for e in edge_index
                )
            ):
                msg = "graph topology requires edge_index: list[list[int]]"
                raise ProposalComposeError(msg)
            return GeometryConfig.graph(
                input_dim=input_dim,
                output_dim=output_dim,
                edge_index=edge_index,
                hidden_dims=hidden_dims,
                init_scale=init_scale,
            )
        case "causal_transformer":
            return GeometryConfig.causal_transformer(
                vocab_size=input_dim,
                d_model=hidden,
                n_layers=depth,
                n_heads=_as_int(geometry.get("num_heads"), _DEFAULT_NUM_HEADS),
                seq_len=_as_int(geometry.get("seq_len"), 32),
            )
        case _:
            msg = f"Unknown topology {topology!r}"
            raise ProposalComposeError(msg)  # pragma: no cover - guarded above


def _build_substrate_config(substrate_name: str, dynamics: str):
    """Build substrate config, adding noise for diffusion dynamics."""
    from computronium.ontology.substrate._substrate import SubstrateConfig

    name_lower = substrate_name.lower()
    factory_map = {
        "digital": SubstrateConfig.digital,
        "analog": SubstrateConfig.analog,
        "memristive": SubstrateConfig.memristive,
        "neuromorphic": SubstrateConfig.neuromorphic,
        "optical": SubstrateConfig.optical,
        "quantum": SubstrateConfig.quantum,
        "sparse": SubstrateConfig.sparse,
        "ternary": SubstrateConfig.ternary,
        "complex": SubstrateConfig.complex,
    }
    factory = factory_map.get(name_lower, SubstrateConfig.digital)

    if dynamics in {"diffusion", "spike_integration", "pc_alm"}:
        return factory(noise_level=0.05)
    return factory()


@dataclass(frozen=True, slots=True)
class ComposedCell:
    """A composed cell: the system, the declaration it was built from, and the
    hyperparameters it was actually given (R6).

    The declaration is kept because the runtime module does not name its own
    topology, so "which cell was this?" is otherwise unanswerable from a
    composed system.  ``param_count`` is the measured size of the composed
    system, so a declared parameter ceiling can be checked against the thing it
    was declared for.
    """

    system: System
    config: Any
    params: Mapping[str, Any]
    param_count: int


# Harvested geometry names that mean the same thing as the composer's key.
_GEOMETRY_ALIASES: Final[Mapping[str, str]] = {"num_layers": "depth"}

# Geometry values the task determines; never taken from a hyperparameter.
_TASK_SHAPED: Final[frozenset[str]] = frozenset({"input_dim", "output_dim"})


def _geometry_mapping(
    active: ActiveSpace,
    geometry: Mapping[str, object],
    topology: str,
    swept: Mapping[str, Any],
) -> dict[str, object]:
    """Merge the cell's *swept* geometry values under the composer's key names.

    Only swept values are injected.  A resolved-but-unswept value is a prior or
    a config default, and injecting it would be a hidden default answering a
    sizing question the parameter ceiling owns: ``build_geometry_config``
    treats an explicit ``hidden_dim``/``depth`` as a request to skip derived
    sizing, so a prior of 64 would silently defeat a 10 000-parameter ceiling.
    """
    allowed = _allowed_keys(topology)
    harvested = {
        _GEOMETRY_ALIASES.get(name, name): value
        for name, value in active.by_axis(StructuralAxis.GEOMETRY).items()
        if name in swept
        and name not in _TASK_SHAPED
        and (_GEOMETRY_ALIASES.get(name, name) in allowed)
    }
    return {**harvested, **geometry}


def _axis_factory(config_cls: Any, primitive: str) -> Any:
    """Resolve an axis name to its config factory through the ontology surface."""
    factory = getattr(config_cls, primitive, None)
    if not callable(factory):
        msg = f"Unknown cell axis: {primitive!r} is not a config factory"
        raise ProposalComposeError(msg)
    return factory


def compose_configs(  # ruff: ignore[too-many-locals]
    *,
    coordinate: Coordinate,
    geometry: Mapping[str, object],
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int = 0,
) -> Any:
    """Compose and validate the configs of one cell, building no ``System``.

    What each primitive can accept is decided by availability predicates in
    ``AXES``, evaluated against ``coordinate`` — not by inspecting factories and
    not by branching on pairs of axis names. Adding a coupling between two axes
    is a spec row. Cross-axis legality is ``SystemConfig.validate``, so this is
    also the cheap way to ask *whether a cell can exist* before spending a
    training run on it.

    Args:
        coordinate: The six-axis selection and its hyperparameter overrides.
        geometry: Topology parameters; harvested geometry values fill the gaps.
        input_shape: The task's own input shape, channels first.
        output_dim: Class count, derived from the task.
        param_budget: Parameter ceiling for derived sizing; 0 disables it.

    Returns:
        The validated ``SystemConfig`` for the cell.

    Raises:
        ProposalComposeError: A primitive, or one of its parameters, has no
            place in this cell.
        ValueError: ``SystemConfig.validate`` rejected the combination.
    """
    from computronium.ontology import (
        CreditAssignmentConfig,
        ParameterUpdateConfig,
        StateDynamicsConfig,
    )
    from computronium.ontology.system import SystemConfig
    from computronium.state.transitions import PlasticityConfig

    active = harvest_schema().active(coordinate)
    substrate_name = coordinate.substrate
    dynamics_name = coordinate.dynamics

    gcfg = _fit_geometry(
        _geometry_mapping(active, geometry, coordinate.geometry, coordinate.params),
        topology=coordinate.geometry,
        input_shape=input_shape,
        output_dim=output_dim,
        param_budget=param_budget,
    )

    d_factory = _axis_factory(StateDynamicsConfig, dynamics_name)
    dcfg = d_factory(**{
        **active.for_axis(StructuralAxis.DYNAMICS, dynamics_name),
        "step_size": apply_dynamics_step_size(
            active.values.get("settle_step", _config_default_step_size(d_factory)),
            dynamics_name,
        ),
    })

    c_factory = _axis_factory(CreditAssignmentConfig, coordinate.credit)
    ccfg = c_factory(**active.for_axis(StructuralAxis.CREDIT, coordinate.credit))

    u_factory = _axis_factory(ParameterUpdateConfig, coordinate.update)
    ucfg = u_factory(
        **active.for_axis(StructuralAxis.UPDATE, coordinate.update),
        dynamics=dynamics_name,
        credit=coordinate.credit,
    )

    substrate_config = _build_substrate_config(substrate_name, dynamics_name)
    m_factory = _axis_factory(PlasticityConfig, coordinate.plasticity)
    mcfg = m_factory(
        **active.for_axis(StructuralAxis.PLASTICITY, coordinate.plasticity)
    )

    config = SystemConfig(
        substrate=substrate_config,
        geometry=gcfg,
        dynamics=dcfg,
        credit=ccfg,
        update=ucfg,
        plasticity=mcfg,
    )
    config.validate()
    return config


def compose_cell_system(
    *,
    coordinate: Coordinate,
    geometry: Mapping[str, object],
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int = 0,
) -> ComposedCell:
    """Compose a full grid cell and build its ``System``.

    Args:
        coordinate: The six-axis selection and its hyperparameter overrides.
        geometry: Topology parameters; harvested geometry values fill the gaps.
        input_shape: The task's own input shape, channels first.
        output_dim: Class count, derived from the task.
        param_budget: Parameter ceiling for derived sizing; 0 disables it.

    Returns:
        ComposedCell carrying the system, its validated declaration, and the
        effective hyperparameter values.
    """
    config = compose_configs(
        coordinate=coordinate,
        geometry=geometry,
        input_shape=input_shape,
        output_dim=output_dim,
        param_budget=param_budget,
    )
    active = harvest_schema().active(coordinate)
    # Use joint system (6-D) when plasticity is not null, otherwise 5-D system
    if coordinate.plasticity != "null":
        system = compose_joint_system_from_configs(
            config.substrate,
            config.geometry,
            config.dynamics,
            config.plasticity,
            config.credit,
            config.update,
            validate=True,
        )
    else:
        system = compose_system_from_configs(
            config.substrate,
            config.geometry,
            config.dynamics,
            config.credit,
            config.update,
        )
    return ComposedCell(
        system=system,
        config=config,
        param_count=param_count(system),
        params=_effective_params(
            active,
            config.geometry,
            config.dynamics,
            config.credit,
            config.update,
        ),
    )


def _effective_params(
    active: ActiveSpace, gcfg: GeometryConfig, *configs: Any
) -> dict[str, Any]:
    """Record what each composed config actually holds, keyed ``axis.name``.

    Names are per-axis (``dynamics.settle_step`` vs ``update.update_lr``), so
    each axis records the value its own config actually holds.
    """
    by_axis = {
        StructuralAxis.GEOMETRY: gcfg,
        StructuralAxis.DYNAMICS: configs[0],
        StructuralAxis.CREDIT: configs[1],
        StructuralAxis.UPDATE: configs[2],
    }
    effective: dict[str, Any] = {}
    for axis, config in by_axis.items():
        for spec in active.by_axis_specs_for(axis):
            effective[f"{axis.value}.{spec.name}"] = getattr(
                config, config_field_name(spec.name), active.values[spec.name]
            )
    return effective


def _config_default_step_size(factory: Any) -> float:
    """The step size a dynamics factory would take from its dataclass default."""
    for field in fields(StateDynamicsConfig):
        if field.name == "step_size" and isinstance(field.default, float):
            return field.default
    return 0.1
