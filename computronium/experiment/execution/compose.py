"""Kernel-native system composition for grid cells.

Composes a full grid cell (dynamics × credit × update × topology) from the
single-source config classmethods and registries — no preset tables.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Final

from computronium.core.logging import get_logger
from computronium.core.system_trainer import compose_system_from_configs
from computronium.experiment.learning.prior import get_dynamics_step_size
from computronium.ontology import GeometryConfig

if TYPE_CHECKING:
    from computronium.ontology import System

__all__ = [
    "GRID_CREDITS",
    "GRID_DYNAMICS",
    "GRID_UPDATES",
    "ProposalComposeError",
    "build_geometry_config",
    "compose_cell_system",
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
    "topology_type",
    "hidden_dim",
    "depth",
    "init_scheme",
    "init_scale",
})

_TOPOLOGY_KEYS: Final[dict[str, frozenset[str]]] = {
    "feedforward": frozenset({"residual"}),
    "recurrent": frozenset(),
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


def _allowed_keys(topology: str) -> frozenset[str]:
    return _COMMON_GEOMETRY_KEYS | _TOPOLOGY_KEYS.get(topology, frozenset())


def _auto_size_geometry(  # noqa: C901, PLR0911
    topology: str, param_budget: int, input_dim: int, output_dim: int, depth: int
) -> tuple[tuple[int, ...], int]:
    if param_budget <= 0:
        return (64,) * max(depth, 1), max(depth, 1)

    def estimate_params(h: int, d: int) -> int:  # noqa: PLR0911
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


def build_geometry_config(  # noqa: C901, PLR0911, PLR0912, PLR0914, PLR0915
    geometry: dict[str, object],
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int = 0,
) -> GeometryConfig:
    """Build a ``GeometryConfig`` from a proposal's geometry dict."""
    topology = str(geometry.get("topology_type", "feedforward"))
    if topology not in _TOPOLOGY_KEYS:
        msg = f"Unknown topology_type {topology!r}; allowed: {sorted(_TOPOLOGY_KEYS)}"
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

    if not explicit_hidden or not explicit_depth:
        hidden_dims, depth = _auto_size_geometry(
            topology, param_budget, input_dim, output_dim, depth
        )
        hidden = hidden_dims[0] if hidden_dims else 64
    else:
        hidden_dims = (hidden,) * depth

    init_scheme = str(geometry.get("init_scheme", "default"))
    if init_scheme not in {"default", "mupc"}:
        msg = f"init_scheme must be 'default' or 'mupc', got {init_scheme!r}"
        raise ProposalComposeError(msg)
    init_scale = _as_float(geometry.get("init_scale"), 0.1)

    npt = _as_int(geometry.get("neurons_per_tile"), 0)
    tpl = _as_int(geometry.get("tiles_per_layer"), 0)
    if topology == "tile_mesh" and param_budget > 0 and (npt == 0 or tpl == 0):
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

    nca_grid_hw = _as_int_pair(geometry.get("grid_hw"), (16, 16))
    if topology == "nca" and param_budget > 0 and "grid_hw" not in geometry:
        max_grid_area = max(1, param_budget // max(1, hidden * hidden))
        grid_side = max(4, int(max_grid_area**0.5))
        nca_grid_hw = (grid_side, grid_side)

    conv_channels_raw = geometry.get("conv_channels")
    kernel_size = _as_int(geometry.get("kernel_size"), 3)
    in_channels = _as_int(geometry.get("in_channels"), 3)
    input_hw = _as_int_pair(geometry.get("input_hw"), (28, 28))
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
        case "tile_mesh":
            return GeometryConfig.tile_mesh(
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
                num_heads=_as_int(geometry.get("num_heads"), 8),
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
            return GeometryConfig.nca(
                channels=hidden,
                hidden=hidden,
                grid_hw=nca_grid_hw,  # type: ignore[arg-type]
                init_scale=init_scale,
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
                n_heads=_as_int(geometry.get("num_heads"), 4),
                seq_len=_as_int(geometry.get("seq_len"), 32),
            )
        case _:
            msg = f"Unknown topology_type {topology!r}"
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


def compose_cell_system(
    *,
    dynamics: str,
    credit: str,
    update: str,
    geometry: dict[str, object],
    input_dim: int,
    output_dim: int,
    lr: float = 1e-3,
    substrate: str = "digital",
    param_budget: int = 0,
) -> System:
    """Compose a full grid cell (dynamics × credit × update × topology).

    Every axis named explicitly by the coverage proposer, all built from the
    single-source config classmethods and registries — no preset tables.
    """
    from computronium.ontology import (
        CreditAssignmentConfig,
        ParameterUpdateConfig,
        StateDynamicsConfig,
    )
    from computronium.ontology.system import SystemConfig

    gcfg = build_geometry_config(
        geometry, input_dim=input_dim, output_dim=output_dim, param_budget=param_budget
    )
    try:
        dynamics_step_size = _DYNAMICS_STEP_SIZE_OVERRIDES.get(dynamics, 0.1)
        dcfg = getattr(StateDynamicsConfig, dynamics)(step_size=dynamics_step_size)
        ccfg = getattr(CreditAssignmentConfig, credit)()
        update_factory = getattr(ParameterUpdateConfig, update)
        kwargs = (
            {"step_size": lr, "dynamics": dynamics, "credit": credit}
            if "step_size" in inspect.signature(update_factory).parameters
            else {}
        )
        ucfg = update_factory(**kwargs)
    except AttributeError as exc:
        msg = f"Unknown cell axis: {exc.args[0]!r} is not a config factory"
        raise ProposalComposeError(msg) from exc

    if (
        dcfg.dynamics_type == "energy_minimization"
        and ccfg.credit_type == "thermodynamic_contrast"
    ):
        ccfg = CreditAssignmentConfig.thermodynamic_contrast(beta=dcfg.beta)
    elif dcfg.dynamics_type == "pc_alm" and ccfg.credit_type in {
        "pc_alm",
        "thermodynamic_contrast",
    }:
        ccfg = CreditAssignmentConfig(
            credit_type=ccfg.credit_type,
            beta=dcfg.beta,
            feedback_matrix=ccfg.feedback_matrix,
            local_objective=ccfg.local_objective,
            orthogonal_init=ccfg.orthogonal_init,
            feedback_scale=ccfg.feedback_scale,
            credit_norm=ccfg.credit_norm,
        )

    substrate_config = _build_substrate_config(substrate, dynamics)

    SystemConfig(
        substrate=substrate_config,
        geometry=gcfg,
        dynamics=dcfg,
        credit=ccfg,
        update=ucfg,
    ).validate()
    return compose_system_from_configs(
        substrate_config,
        gcfg,
        dcfg,
        ccfg,
        ucfg,
    )
