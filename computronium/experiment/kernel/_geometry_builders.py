"""Per-topology geometry builders extracted from compose.py.

Each topology has its own builder function to avoid the massive match statement
in build_geometry_config. This module is the single place where topology-specific
sizing and parameter logic lives.
"""

from __future__ import annotations

import math
from typing import Any, Literal

import torch

from computronium.experiment.schema.geometry_keys import (
    TOPOLOGY_KEYS,
    allowed_geometry_keys,
)
from computronium.ontology.geometry import GeometryConfig

_TOPOLOGY_REQUIRED_INPUT: dict[str, str] = {
    "feedforward": "image",
    "recurrent": "image",
    "tile": "image",
    "tile_mesh": "image",
    "attention": "image",
    "spatial_lattice": "image",
    "nca": "image",
    "ntm": "image",
    "conv": "image",
    "graph": "image",
    "causal_transformer": "token",
}

_TILE_TOPOLOGIES: frozenset[str] = frozenset({"tile", "tile_mesh"})
_HEAD_SPLIT_TOPOLOGIES: frozenset[str] = frozenset({"attention", "causal_transformer"})
_DEFAULT_NUM_HEADS: int = 8


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
        return result
    return default


def _as_int_tuple(value: object, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(value, list | tuple) and all(
        isinstance(v, int | float) for v in value
    ):
        result = tuple(int(v) for v in value)
        if len(result) != 3:
            return default
        return result
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


def _auto_size_geometry(
    topology: str, param_budget: int, input_dim: int, output_dim: int, depth: int
) -> tuple[tuple[int, ...], int]:
    if param_budget <= 0:
        return (64,) * max(depth, 1), max(depth, 1)

    def _estimate_ff_recurrent(h: int, d: int) -> int:
        return input_dim * h + max(d - 1, 0) * h * h + h * output_dim

    def _estimate_attention(h: int, d: int) -> int:
        return 4 * h * h * d

    def _estimate_ntm(h: int, d: int) -> int:
        return h * h + 16 * 8 + h * output_dim

    def _estimate_tile_mesh(h: int, d: int) -> int:
        npt = h
        tpl = max(d, 1)
        return (
            input_dim * npt + max(d - 1, 0) * npt * tpl * npt + npt * tpl * output_dim
        )

    def _estimate_spatial_lattice(h: int, d: int) -> int:
        lattice_volume = 4 * 4 * 4
        return input_dim * lattice_volume * h + h * output_dim

    def _estimate_nca(h: int, d: int) -> int:
        grid_area = 16 * 16
        return h * h * grid_area

    def _estimate_conv(h: int, d: int) -> int:
        kernel_size = 3
        in_channels = 3
        return in_channels * h * kernel_size * kernel_size + h * output_dim

    def _estimate_graph(h: int, d: int) -> int:
        num_nodes = 32
        return h * h * num_nodes

    estimator_map = {
        "feedforward": _estimate_ff_recurrent,
        "recurrent": _estimate_ff_recurrent,
        "attention": _estimate_attention,
        "causal_transformer": _estimate_attention,
        "ntm": _estimate_ntm,
        "tile_mesh": _estimate_tile_mesh,
        "spatial_lattice": _estimate_spatial_lattice,
        "nca": _estimate_nca,
        "conv": _estimate_conv,
        "graph": _estimate_graph,
    }
    estimate_params = estimator_map.get(topology, _estimate_ff_recurrent)

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


def _validate_topology(topology: str) -> None:
    if topology not in TOPOLOGY_KEYS:
        raise ValueError(
            f"Unknown topology {topology!r}; allowed: {sorted(TOPOLOGY_KEYS)}"
        )


def _check_geometry_input_compat(
    topology: str,
    input_shape: tuple[int, ...],
    required_input: str,
    geometry: dict[str, object] | None = None,
) -> None:
    # For causal_transformer with patch embedding, allow image input
    if (
        topology == "causal_transformer"
        and geometry
        and _as_int(geometry.get("patch_size"), 0) > 0
    ):
        return  # Vision mode with patch embedding - allow image input

    if required_input == "token" and len(input_shape) != 1:
        # Token-only geometries require 1D sequence input (seq_len)
        raise ValueError(
            f"Geometry '{topology}' requires token input (integer token IDs), "
            f"but task provides input with shape {input_shape} (expected 1D sequence)"
        )


def _validate_geometry_keys(topology: str, geometry: dict[str, object]) -> None:
    allowed = allowed_geometry_keys(topology)
    unknown = frozenset(geometry) - allowed
    if unknown:
        raise ValueError(
            f"Unknown geometry keys {sorted(unknown)} for topology {topology!r}; "
            f"allowed: {sorted(allowed)}"
        )


def _derive_init_params(
    geometry: dict[str, object],
) -> tuple[Literal["default", "mupc", "innocenti"], float]:
    init_scheme = str(geometry.get("init_scheme", "default"))
    if init_scheme not in {"default", "mupc", "innocenti"}:
        raise ValueError(
            f"init_scheme must be 'default', 'mupc', or 'innocenti', got {init_scheme!r}"
        )
    init_scale = _as_float(geometry.get("init_scale"), 0.1)
    return init_scheme, init_scale  # type: ignore[return-value]


def _derive_head_params(
    topology: str,
    geometry: dict[str, object],
    hidden: int,
) -> tuple[int, int]:
    if topology in _HEAD_SPLIT_TOPOLOGIES:
        heads = _as_int(geometry.get("num_heads"), _DEFAULT_NUM_HEADS)
        hidden = max(heads, hidden - hidden % heads)
    else:
        heads = _DEFAULT_NUM_HEADS
    return heads, hidden


def _derive_tile_params(
    topology: str,
    geometry: dict[str, object],
    param_budget: int,
    hidden: int,
    depth: int,
) -> tuple[int, int]:
    if topology not in _TILE_TOPOLOGIES:
        return 0, 0

    npt = _as_int(geometry.get("neurons_per_tile"), 0)
    tpl = _as_int(geometry.get("tiles_per_layer"), 0)
    if param_budget > 0 and (npt == 0 or tpl == 0):
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
    return npt, tpl


def _derive_nca_params(
    topology: str,
    geometry: dict[str, object],
    param_budget: int,
    hidden: int,
    input_shape: tuple[int, ...],
) -> tuple[tuple[int, int], int]:
    if topology != "nca":
        return (16, 16), hidden

    nca_grid_hw = _as_int_pair(geometry.get("grid_hw"), _spatial_extent(input_shape))
    if param_budget > 0 and "grid_hw" not in geometry:
        max_grid_area = max(1, param_budget // max(1, hidden * hidden))
        task_side = min(_spatial_extent(input_shape))
        grid_side = max(1, min(int(max_grid_area**0.5), task_side))
        nca_grid_hw = (grid_side, grid_side)

    user_channels = geometry.get("channels")
    if user_channels is not None:
        channels = _as_int(user_channels, hidden)
    else:
        h, w = nca_grid_hw
        grid_area = max(1, h * w)
        input_dim = math.prod(input_shape)
        channels = max(1, input_dim // grid_area)

    return nca_grid_hw, channels


def _derive_conv_params(
    topology: str,
    geometry: dict[str, object],
    param_budget: int,
    input_shape: tuple[int, ...],
    depth: int,
    output_dim: int,
) -> tuple[int, int, tuple[int, int], tuple[int, int], tuple[int, ...]]:
    if topology != "conv":
        return 0, 0, (0, 0), (0, 0), ()

    conv_channels_raw = geometry.get("conv_channels")
    kernel_size = _as_int(geometry.get("kernel_size"), 3)
    in_channels = _as_int(geometry.get("in_channels"), _channel_count(input_shape))
    input_hw = _as_int_pair(geometry.get("input_hw"), _spatial_extent(input_shape))
    pool_hw = _as_int_pair(geometry.get("pool_hw"), (2, 2))

    if param_budget > 0 and conv_channels_raw is None:
        base_channels = max(
            8,
            param_budget // (in_channels * kernel_size * kernel_size + output_dim * 2),
        )
        num_conv_layers = max(2, min(4, depth))
        conv_channels = tuple(
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

    return kernel_size, in_channels, input_hw, pool_hw, conv_channels


def build_feedforward_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    explicit_hidden: bool,
    explicit_depth: bool,
    depth: int,
    hidden: int,
    init_scheme: str,
    init_scale: float,
    residual: bool,
    geometry: dict[str, object],
) -> GeometryConfig:
    derived_dims, derived_depth = _auto_size_geometry(
        "feedforward", param_budget, input_dim, output_dim, depth
    )
    if not explicit_depth:
        depth = derived_depth
    hidden_dims = (
        (hidden,) * depth
        if explicit_hidden
        else _fit_depth(derived_dims, depth, hidden)
    )
    return GeometryConfig.feedforward(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dims=hidden_dims,
        init_scale=init_scale,
        init_scheme=init_scheme,  # type: ignore[arg-type]
        residual=residual,
    )


def build_recurrent_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    explicit_hidden: bool,
    explicit_depth: bool,
    depth: int,
    hidden: int,
    init_scheme: str,
    init_scale: float,
    geometry: dict[str, object],
) -> GeometryConfig:
    derived_dims, derived_depth = _auto_size_geometry(
        "recurrent", param_budget, input_dim, output_dim, depth
    )
    if not explicit_depth:
        depth = derived_depth
    hidden_dims = (
        (hidden,) * depth
        if explicit_hidden
        else _fit_depth(derived_dims, depth, hidden)
    )
    return GeometryConfig.recurrent(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dims=hidden_dims,
        init_scale=init_scale,
        init_scheme=init_scheme,  # type: ignore[arg-type]
    )


def build_tile_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    depth: int,
    hidden: int,
    init_scale: float,
    npt: int,
    tpl: int,
) -> GeometryConfig:
    return GeometryConfig.tile(
        input_dim=input_dim,
        output_dim=output_dim,
        num_layers=depth,
        neurons_per_tile=npt,
        tiles_per_layer=tpl,
        init_scale=init_scale,
    )


def build_tile_mesh_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    depth: int,
    hidden: int,
    init_scale: float,
    npt: int,
    tpl: int,
) -> GeometryConfig:
    return GeometryConfig.tile_mesh(
        input_dim=input_dim,
        output_dim=output_dim,
        num_layers=depth,
        neurons_per_tile=npt,
        tiles_per_layer=tpl,
        init_scale=init_scale,
    )


def build_attention_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    explicit_hidden: bool,
    explicit_depth: bool,
    depth: int,
    hidden: int,
    init_scheme: str,
    init_scale: float,
    geometry: dict[str, object],
) -> GeometryConfig:
    derived_dims, derived_depth = _auto_size_geometry(
        "attention", param_budget, input_dim, output_dim, depth
    )
    if not explicit_depth:
        depth = derived_depth
    hidden_dims = (
        (hidden,) * depth
        if explicit_hidden
        else _fit_depth(derived_dims, depth, hidden)
    )
    heads, hidden = _derive_head_params("attention", geometry, hidden_dims[0])
    return GeometryConfig.attention(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dim=hidden,
        num_layers=depth,
        num_heads=heads,
        init_scale=init_scale,
    )


def build_spatial_lattice_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    hidden: int,
    depth: int,
    init_scale: float,
    geometry: dict[str, object],
) -> GeometryConfig:
    lattice_dims = _as_int_tuple(geometry.get("lattice_dims"), (4, 4, 4))
    constrained_hidden_dims = (hidden,) * depth
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
            min_hidden = max(1, param_budget // (input_dim * 4 + output_dim * 4 + 100))
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


def build_nca_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    hidden: int,
    init_scale: float,
    geometry: dict[str, object],
    input_shape: tuple[int, ...],
) -> GeometryConfig:
    nca_grid_hw, channels = _derive_nca_params(
        "nca", geometry, param_budget, hidden, input_shape
    )
    return GeometryConfig.nca(
        channels=channels,
        hidden=hidden,
        grid_hw=nca_grid_hw,
        init_scale=init_scale,
        output_dim=output_dim,
    )


def build_ntm_config(
    *,
    input_dim: int,
    output_dim: int,
    hidden: int,
    geometry: dict[str, object],
) -> GeometryConfig:
    return GeometryConfig.ntm(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden=hidden,
        mem_slots=_as_int(geometry.get("mem_slots"), 16),
        mem_width=_as_int(geometry.get("mem_width"), 8),
    )


def build_conv_config(
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int,
    depth: int,
    init_scale: float,
    kernel_size: int,
    in_channels: int,
    input_hw: tuple[int, int],
    pool_hw: tuple[int, int],
    conv_channels: tuple[int, ...],
) -> GeometryConfig:
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


def build_graph_config(
    *,
    input_dim: int,
    output_dim: int,
    hidden: int,
    depth: int,
    init_scale: float,
    init_scheme: str,
    geometry: dict[str, object],
) -> GeometryConfig:
    edge_index = _as_edge_index(geometry.get("edge_index"))
    hidden_dims = (hidden,) * depth
    return GeometryConfig.graph(
        input_dim=input_dim,
        output_dim=output_dim,
        edge_index=edge_index,
        hidden_dims=hidden_dims,
        init_scale=init_scale,
    )


def _as_edge_index(value: object) -> list[list[int]]:
    """Normalize edge_index to ``[2, num_edges]`` nested lists.

    Accepts the serialized ``list[list[int]]`` form and the PyG LongTensor
    the graph loaders supply directly.
    """
    if isinstance(value, torch.Tensor):
        value = value.detach().cpu().tolist()
    if not (
        isinstance(value, list)
        and all(
            isinstance(e, list) and all(isinstance(v, int) for v in e) for e in value
        )
    ):
        raise ValueError("graph topology requires edge_index: list[list[int]]")
    return value


def build_causal_transformer_config(
    *,
    input_dim: int,
    output_dim: int,
    hidden: int,
    depth: int,
    geometry: dict[str, object],
) -> GeometryConfig:
    heads, hidden = _derive_head_params("causal_transformer", geometry, hidden)
    patch_size = _as_int(geometry.get("patch_size"), 0)
    if patch_size > 0:
        # Vision mode: input_dim is the product of input_shape (C*H*W)
        # We need to derive image_hw and in_channels from input_shape
        # This is handled by the caller - we need to pass them through
        # For now, use defaults
        image_hw_raw = geometry.get("image_hw", (28, 28))
        image_hw = (
            tuple(image_hw_raw) if isinstance(image_hw_raw, (list, tuple)) else (28, 28)
        )
        return GeometryConfig.causal_transformer(
            vocab_size=output_dim,
            d_model=hidden,
            n_layers=depth,
            n_heads=heads,
            seq_len=_as_int(geometry.get("seq_len"), 32),
            patch_size=patch_size,
            patch_embed_dim=_as_int(geometry.get("patch_embed_dim"), 0),
            image_hw=image_hw,
            in_channels=_as_int(geometry.get("in_channels"), 1),
        )
    else:
        # Standard LM mode
        return GeometryConfig.causal_transformer(
            vocab_size=input_dim,
            d_model=hidden,
            n_layers=depth,
            n_heads=heads,
            seq_len=_as_int(geometry.get("seq_len"), 32),
        )


# Registry of topology builders
_GEOMETRY_BUILDERS: dict[str, Any] = {
    "feedforward": build_feedforward_config,
    "recurrent": build_recurrent_config,
    "tile": build_tile_config,
    "tile_mesh": build_tile_mesh_config,
    "attention": build_attention_config,
    "spatial_lattice": build_spatial_lattice_config,
    "nca": build_nca_config,
    "ntm": build_ntm_config,
    "conv": build_conv_config,
    "graph": build_graph_config,
    "causal_transformer": build_causal_transformer_config,
}


def build_geometry_config_dispatch(
    topology: str,
    *,
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int,
    geometry: dict[str, object],
) -> GeometryConfig:
    """Dispatch to topology-specific builder.

    This replaces the massive match statement in the original compose.py.
    """
    input_dim = math.prod(input_shape)

    # Common validation
    _validate_topology(topology)
    required_input = _TOPOLOGY_REQUIRED_INPUT.get(topology, "image")

    # Auto-derive patch embedding params for causal_transformer vision mode
    if (
        topology == "causal_transformer"
        and len(input_shape) > 1
        and "patch_size" not in geometry
    ):
        # Derive from input_shape: (C, H, W) or (H, W)
        if len(input_shape) == 3:
            in_channels = input_shape[0]
            image_hw = input_shape[1:]
        elif len(input_shape) == 2:
            in_channels = 1
            image_hw = input_shape
        else:
            in_channels = 1
            image_hw = input_shape[-2:]

        # Default patch_size: 4 for 28x28, 8 for 32x32, etc.
        patch_size = 4
        if image_hw[0] >= 32:
            patch_size = 8
        elif image_hw[0] >= 64:
            patch_size = 16

        geometry["patch_size"] = patch_size
        geometry["image_hw"] = image_hw
        geometry["in_channels"] = in_channels
        # patch_embed_dim defaults to hidden (d_model) if not specified
        if "patch_embed_dim" not in geometry:
            geometry["patch_embed_dim"] = 0  # Will use d_model in builder

    _check_geometry_input_compat(topology, input_shape, required_input, geometry)
    _validate_geometry_keys(topology, geometry)

    # Common parameter derivation
    explicit_hidden = "hidden_dim" in geometry
    explicit_depth = "num_layers" in geometry
    depth = max(_as_int(geometry.get("num_layers"), 2), 1)
    hidden = _as_int(geometry.get("hidden_dim"), 64)

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

    init_scheme, init_scale = _derive_init_params(geometry)
    npt, tpl = _derive_tile_params(topology, geometry, param_budget, hidden, depth)
    nca_grid_hw, channels = _derive_nca_params(
        topology, geometry, param_budget, hidden, input_shape
    )
    kernel_size, in_channels, input_hw, pool_hw, conv_channels = _derive_conv_params(
        topology, geometry, param_budget, input_shape, depth, output_dim
    )

    # Dispatch to builder with topology-specific arguments
    match topology:
        case "feedforward":
            return build_feedforward_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                explicit_hidden=explicit_hidden,
                explicit_depth=explicit_depth,
                depth=depth,
                hidden=hidden,
                init_scheme=init_scheme,
                init_scale=init_scale,
                residual=bool(geometry.get("residual")),
                geometry=geometry,
            )
        case "recurrent":
            return build_recurrent_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                explicit_hidden=explicit_hidden,
                explicit_depth=explicit_depth,
                depth=depth,
                hidden=hidden,
                init_scheme=init_scheme,
                init_scale=init_scale,
                geometry=geometry,
            )
        case "tile":
            return build_tile_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                depth=depth,
                hidden=hidden,
                init_scale=init_scale,
                npt=npt,
                tpl=tpl,
            )
        case "tile_mesh":
            return build_tile_mesh_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                depth=depth,
                hidden=hidden,
                init_scale=init_scale,
                npt=npt,
                tpl=tpl,
            )
        case "attention":
            return build_attention_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                explicit_hidden=explicit_hidden,
                explicit_depth=explicit_depth,
                depth=depth,
                hidden=hidden,
                init_scheme=init_scheme,
                init_scale=init_scale,
                geometry=geometry,
            )
        case "spatial_lattice":
            return build_spatial_lattice_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                hidden=hidden,
                depth=depth,
                init_scale=init_scale,
                geometry=geometry,
            )
        case "nca":
            return build_nca_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                hidden=hidden,
                init_scale=init_scale,
                geometry=geometry,
                input_shape=input_shape,
            )
        case "ntm":
            return build_ntm_config(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden=hidden,
                geometry=geometry,
            )
        case "conv":
            return build_conv_config(
                input_dim=input_dim,
                output_dim=output_dim,
                param_budget=param_budget,
                depth=depth,
                init_scale=init_scale,
                kernel_size=kernel_size,
                in_channels=in_channels,
                input_hw=input_hw,
                pool_hw=pool_hw,
                conv_channels=conv_channels,
            )
        case "graph":
            return build_graph_config(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden=hidden,
                depth=depth,
                init_scale=init_scale,
                init_scheme=init_scheme,
                geometry=geometry,
            )
        case "causal_transformer":
            return build_causal_transformer_config(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden=hidden,
                depth=depth,
                geometry=geometry,
            )
        case _:
            raise ValueError(f"Unknown topology {topology!r}")
