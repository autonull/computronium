"""Proposal-side system composition and task-compatibility fencing.

The proposal schema (``ExperimentProposal.geometry``) describes a cell's
geometry independently of its training family; this module resolves that
description against a base native factory by round-tripping through
``extract_config``/``compose_system_from_configs`` — one path, so a proposal
and its executor can never disagree about how the geometry is built.

Unknown or topology-inappropriate geometry keys fail loudly (plan §1
"fail loudly, never fabricate"), and the LM/sequence lane is fenced behind
``assert_task_runnable`` until the sequence executor lands (P1.4).
"""

import inspect
from typing import TYPE_CHECKING, Final, cast

from computronium.core.logging import get_logger
from computronium.core.system_trainer import (
    compose_system_from_configs,
    extract_config,
)
from computronium.domains.registry import SUPPORTED_TASKS
from computronium.experiment.param_estimator import resolve_native_model
from computronium.ontology import GeometryConfig

if TYPE_CHECKING:
    from computronium.ontology import System

__all__ = [
    "TASK_COMPAT",
    "ProposalComposeError",
    "assert_task_runnable",
    "build_geometry_config",
    "compose_cell_system",
    "compose_proposal_system",
    "dry_run_system",
    "logger",
]

logger = get_logger(__name__)

# Dynamics step_size overrides for stable settling.
# Key: dynamics_type -> step_size value (replaces default)
_DYNAMICS_STEP_SIZE_OVERRIDES: Final[dict[str, float]] = {
    "diffusion": 0.001,  # Lower step_size for stable Langevin dynamics
    "predictive_settling": 0.01,  # 0.1 diverges on wide layers (hidden=512 -> loss 1e22)
}


#: ``task -> "run" | "fenced"`` compatibility gate (P1.4). Fenced lanes fail
#: with a reason instead of silently degrading to another task.
TASK_COMPAT: Final[dict[str, str]] = {
    "char_ngram": "fenced",
    "shakespeare": "fenced",
    "tiny_shakespeare": "fenced",
    "wikitext2": "fenced",
    "penn_treebank": "fenced",
}

#: Geometry keys shared by every topology.
_COMMON_GEOMETRY_KEYS: Final[frozenset[str]] = frozenset({
    "topology_type",
    "hidden_dim",
    "depth",
    "init_scheme",
    "init_scale",
})

#: Extra geometry keys each topology accepts; anything else in the proposal's
#: geometry dict is a hard error.
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


def _as_int_tuple(value: object, default: tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(value, list | tuple) and all(
        isinstance(v, int | float) for v in value
    ):
        result = tuple(int(v) for v in value)
        if len(result) != 3:
            return default
        return result  # type: ignore[return-value]
    return default


def _as_int_pair(value: object, default: tuple[int, int]) -> tuple[int, int]:
    if isinstance(value, list | tuple) and all(
        isinstance(v, int | float) for v in value
    ):
        result = tuple(int(v) for v in value)
        if len(result) != 2:
            return default
        return result  # type: ignore[return-value]
    return default


def _estimate_spatial_lattice_params(
    lattice_dims: tuple[int, int, int],
    hidden_dims: tuple[int, ...],
    input_dim: int,
    output_dim: int,
) -> int:
    """Estimate parameter count for spatial_lattice geometry."""
    d, h, w = lattice_dims
    num_sites = d * h * w
    first_hidden = hidden_dims[0] if hidden_dims else output_dim

    # Input projection: input_dim -> num_sites * first_hidden
    input_proj_params = input_dim * num_sites * first_hidden

    # Site weights and biases per layer
    site_weight_params = 0
    site_bias_params = 0
    prev_hidden = first_hidden
    for hidden in hidden_dims:
        site_weight_params += num_sites * hidden * prev_hidden
        site_bias_params += num_sites * hidden
        prev_hidden = hidden

    # Output projection: num_sites * last_hidden -> output_dim
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
    """Constrain lattice_dims to fit within param_budget."""
    estimated = _estimate_spatial_lattice_params(
        lattice_dims, hidden_dims, input_dim, output_dim
    )
    if estimated <= param_budget:
        return lattice_dims

    # Progressively reduce lattice dimensions until we fit
    d, h, w = lattice_dims
    # Try reducing each dimension
    for new_d in range(max(1, d), 0, -1):
        for new_h in range(max(1, h), 0, -1):
            for new_w in range(max(1, w), 0, -1):
                new_dims = (new_d, new_h, new_w)
                new_estimated = _estimate_spatial_lattice_params(
                    new_dims, hidden_dims, input_dim, output_dim
                )
                if new_estimated <= param_budget:
                    return new_dims

    # Fallback: minimal lattice
    return (1, 1, 1)


def assert_task_runnable(task_name: str | None) -> None:
    """Fail loudly when a proposal targets an unrunnable task (P1.4).

    Unknown task names are also rejected here — the domain factory's
    silent fallback to the LM lane is exactly the silent-target defect
    this fence exists to close.
    """
    name = task_name or "mnist"
    if TASK_COMPAT.get(name) == "fenced":
        msg = (
            f"Task {name!r} is fenced (P1.4): the sequence executor cannot run it; "
            "no proposal may silently target an unrunnable task"
        )
        raise ProposalComposeError(msg)
    if name not in TASK_COMPAT and name not in SUPPORTED_TASKS:
        msg = f"Unknown task {name!r}: not in the task catalog; refusing to guess"
        raise ProposalComposeError(msg)


def _allowed_keys(topology: str) -> frozenset[str]:
    return _COMMON_GEOMETRY_KEYS | _TOPOLOGY_KEYS.get(topology, frozenset())


def _auto_size_geometry(
    topology: str, param_budget: int, input_dim: int, output_dim: int, depth: int
) -> tuple[tuple[int, ...], int]:
    """Auto-size hidden_dims and depth from param_budget.

    For a simple MLP: params ≈ input_dim * hidden + (depth-1) * hidden^2 + hidden * output_dim
    Solve for hidden given budget, with depth as secondary knob.
    """
    if param_budget <= 0:
        # No budget constraint - use defaults
        return (64,) * max(depth, 1), max(depth, 1)

    # Estimate params for given hidden, depth
    def estimate_params(h: int, d: int) -> int:
        if topology in {"feedforward", "recurrent"}:
            # input * h + (d-1) * h^2 + h * output
            return input_dim * h + max(d - 1, 0) * h * h + h * output_dim
        elif topology == "attention":
            # attention: d_model^2 * n_layers (Q,K,V,O projections) + FFN ~ 4 * d_model^2 * n_layers
            return 4 * h * h * d
        elif topology == "ntm":
            # NTM: controller + memory + heads
            return h * h + 16 * 8 + h * output_dim
        elif topology == "causal_transformer":
            # Similar to attention
            return 4 * h * h * d
        elif topology == "tile_mesh":
            # tile_mesh params ≈ input_dim * npt + (d-1) * npt * tpl * npt + npt * tpl * output_dim
            # npt = neurons_per_tile, tpl = tiles_per_layer
            # For auto-sizing, use h as base and derive npt, tpl from it
            # Simplified: treat as MLP with effective hidden = npt * tpl
            # We'll estimate using npt ≈ h, tpl ≈ d
            npt = h
            tpl = max(d, 1)
            return (
                input_dim * npt
                + max(d - 1, 0) * npt * tpl * npt
                + npt * tpl * output_dim
            )
        elif topology == "spatial_lattice":
            # spatial_lattice: params ≈ input_dim * prod(lattice_dims) * hidden + hidden * output_dim
            # lattice_dims also budget-constrained - use small lattice
            lattice_volume = 4 * 4 * 4  # default 4x4x4
            return input_dim * lattice_volume * h + h * output_dim
        elif topology == "nca":
            # NCA: params ≈ channels^2 * grid_hw (need budget-aware grid sizing)
            # channels ≈ h, grid_hw ≈ 16*16 = 256
            grid_area = 16 * 16
            return h * h * grid_area
        elif topology == "conv":
            # Conv: params depend on conv_channels, kernel_size, input_hw
            # Simplified: treat as MLP with channel expansion
            # params ≈ in_channels * conv_channels * kernel^2 + conv_channels * output_dim
            kernel_size = 3
            in_channels = 3  # typical
            return in_channels * h * kernel_size * kernel_size + h * output_dim
        elif topology == "graph":
            # Graph: params ≈ hidden^2 * num_nodes + edge_params
            # Simplified: use num_nodes ≈ 32
            num_nodes = 32
            return h * h * num_nodes
        else:
            # Conservative estimate
            return input_dim * h + max(d - 1, 0) * h * h + h * output_dim

    # Find all valid (depth, hidden) combinations within budget
    valid_configs: list[tuple[int, int]] = []  # (depth, hidden)
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
        # Fallback: minimal config
        return (8,) * max(depth, 1), max(depth, 1)

    # Pick the config that maximizes hidden * depth (total capacity) rather than just depth
    # This favors balanced depth/width over extreme depth
    best_d, best_h = max(valid_configs, key=lambda x: x[0] * x[1])

    return (best_h,) * best_d, best_d


def _get_all_valid_geometry_configs(
    topology: str,
    param_budget: int,
    input_dim: int,
    output_dim: int,
    geometry_sampling: str = "full_range",
) -> list[tuple[tuple[int, ...], int]]:
    """Return all valid (hidden_dims, depth) combinations within budget for exploration diversity.

    Args:
        geometry_sampling: "full_range" (default) explores all sizes up to param_budget
            by sampling multiple hidden sizes per depth. "max_only" returns only
            the maximum hidden size for each depth (legacy behavior).
    """
    if param_budget <= 0:
        return [((64,) * d, d) for d in range(1, 7)]

    def estimate_params(h: int, d: int) -> int:
        if topology in {"feedforward", "recurrent"}:
            return input_dim * h + max(d - 1, 0) * h * h + h * output_dim
        elif topology == "attention":
            return 4 * h * h * d
        elif topology == "ntm":
            return h * h + 16 * 8 + h * output_dim
        elif topology == "causal_transformer":
            return 4 * h * h * d
        elif topology == "tile_mesh":
            npt = h
            tpl = max(d, 1)
            return (
                input_dim * npt
                + max(d - 1, 0) * npt * tpl * npt
                + npt * tpl * output_dim
            )
        elif topology == "spatial_lattice":
            lattice_volume = 4 * 4 * 4
            return input_dim * lattice_volume * h + h * output_dim
        elif topology == "nca":
            grid_area = 16 * 16
            return h * h * grid_area
        elif topology == "conv":
            kernel_size = 3
            in_channels = 3
            return in_channels * h * kernel_size * kernel_size + h * output_dim
        elif topology == "graph":
            num_nodes = 32
            return h * h * num_nodes
        else:
            return input_dim * h + max(d - 1, 0) * h * h + h * output_dim

    valid_configs = []
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
            if geometry_sampling == "max_only":
                # Legacy: only the maximum hidden size per depth
                valid_configs.append(((best_h_for_d,) * d, d))
            else:
                # Full range: log-spaced samples from 8 to max
                num_samples = min(5, best_h_for_d - 7)  # Up to 5 samples per depth
                if num_samples > 0:
                    import math

                    log_min = math.log(8)
                    log_max = math.log(best_h_for_d)
                    for i in range(num_samples):
                        log_h = log_min + (log_max - log_min) * i / max(
                            1, num_samples - 1
                        )
                        h = max(8, int(round(math.exp(log_h))))
                        valid_configs.append(((h,) * d, d))
                else:
                    valid_configs.append(((best_h_for_d,) * d, d))

    return valid_configs if valid_configs else [((8,) * 1, 1)]


def build_geometry_config(  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches]
    geometry: dict[str, object],
    *,
    input_dim: int,
    output_dim: int,
    param_budget: int = 0,
) -> GeometryConfig:
    """Build a ``GeometryConfig`` from a proposal's geometry dict.

    Args:
        geometry: Validated keys are the common set (``topology_type``,
            ``hidden_dim``, ``depth``, ``init_scheme``, ``init_scale``) plus
            the proposal topology's own extras. Unknown keys raise.
        input_dim: Task input dimension.
        output_dim: Task output dimension.
        param_budget: Optional parameter budget to constrain geometry size.
    """
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

    # Auto-size from param_budget if not explicitly provided
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

    # Auto-size topology-specific parameters from param_budget if not explicitly provided
    # Compute tile_mesh params from param_budget if not explicitly set
    npt = _as_int(geometry.get("neurons_per_tile"), 0)
    tpl = _as_int(geometry.get("tiles_per_layer"), 0)
    if topology == "tile_mesh" and param_budget > 0 and (npt == 0 or tpl == 0):
        # Use auto-sized hidden as base for npt/tpl estimation
        # tile_mesh params ≈ input_dim * npt + (depth-1) * npt * tpl * npt + npt * tpl * output_dim
        # Solve for npt, tpl to fit budget
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

    # Auto-size NCA grid_hw from param_budget
    nca_grid_hw = _as_int_pair(geometry.get("grid_hw"), (16, 16))
    if topology == "nca" and param_budget > 0 and "grid_hw" not in geometry:
        # NCA params ≈ channels^2 * grid_hw
        # grid_hw = grid_h * grid_w, channels = hidden
        # Solve for grid area to fit budget
        max_grid_area = max(1, param_budget // max(1, hidden * hidden))
        grid_side = max(4, int(max_grid_area**0.5))
        nca_grid_hw = (grid_side, grid_side)

    # Auto-size conv parameters from param_budget
    conv_channels_raw = geometry.get("conv_channels")
    kernel_size = _as_int(geometry.get("kernel_size"), 3)
    in_channels = _as_int(geometry.get("in_channels"), 3)
    input_hw = _as_int_pair(geometry.get("input_hw"), (28, 28))
    pool_hw = _as_int_pair(geometry.get("pool_hw"), (2, 2))
    if topology == "conv" and param_budget > 0 and conv_channels_raw is None:
        # Conv params ≈ in_channels * conv_channels * kernel^2 + conv_channels * output_dim
        # Solve for conv_channels (per layer), use multiple layers
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

    # Auto-size graph hidden_dims from param_budget (edge_index required)
    if topology == "graph" and param_budget > 0:
        # Graph params ≈ hidden^2 * num_nodes (approximate)
        # We already have hidden_dims from _auto_size_geometry
        pass  # hidden_dims already computed

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
            # Constrain lattice_dims and hidden_dims from param_budget to avoid blowups
            lattice_dims = _as_int_tuple(geometry.get("lattice_dims"), (4, 4, 4))
            constrained_hidden_dims = hidden_dims
            if param_budget > 0:
                # Iteratively reduce both lattice and hidden dims until under budget
                for _ in range(3):  # Max 3 iterations should converge
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
                    # Reduce hidden dimensions to fit budget
                    min_hidden = max(
                        1, param_budget // (input_dim * 4 + output_dim * 4 + 100)
                    )
                    constrained_hidden_dims = tuple(
                        min(h, min_hidden) for h in constrained_hidden_dims
                    )
                else:
                    # Final safety: force absolute minimum if still over budget
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


def compose_proposal_system(
    model: str,
    *,
    input_dim: int,
    output_dim: int,
    lr: float,
    geometry: dict[str, object] | None = None,
    dynamics: str | None = None,
    credit: str | None = None,
    update: str | None = None,
    substrate: str = "digital",
    param_budget: int = 0,
    device: str = "cpu",
) -> System:
    """Compose the training system for a proposal.

    Full-cell proposals (dynamics/credit/update all named) compose through
    :func:`compose_cell_system` — the G1 grid path. Otherwise the base
    native factory's composition is used, with an optional geometry-only
    override round-tripped through ``extract_config`` so proposal and
    trainer can never diverge on construction.
    """
    if dynamics and credit and update:
        return compose_cell_system(
            dynamics=dynamics,
            credit=credit,
            update=update,
            geometry=geometry or {"topology_type": "feedforward"},
            input_dim=input_dim,
            output_dim=output_dim,
            lr=lr,
            substrate=substrate,
            param_budget=param_budget,
        )
    base_hidden = _as_int((geometry or {}).get("hidden_dim"), 64)
    factory = resolve_native_model(model)
    system = cast(
        "System", factory(input_dim, base_hidden, output_dim, lr=lr, device=device)
    )
    if not geometry:
        return system

    configs = extract_config(system)
    configs["geometry"] = build_geometry_config(
        geometry, input_dim=input_dim, output_dim=output_dim, param_budget=0
    )
    return compose_system_from_configs(
        configs["substrate"],  # type: ignore[arg-type]
        configs["geometry"],  # type: ignore[arg-type]
        configs["dynamics"],  # type: ignore[arg-type]
        configs["credit"],  # type: ignore[arg-type]
        configs["update"],  # type: ignore[arg-type]
    )


def dry_run_system(system: System, *, batch_size: int = 2) -> None:
    """Constructor probe: one ``train_step`` on a synthetic batch.

    Catches credit × topology (and any other settle/loss-shape) crashes
    before a proposal burns governed budget — a failure here raises, the
    caller skips the proposal without pre-registering it (TODO27 rev 4,
    improvement 1).
    """
    import torch

    gcfg = system.geometry.config
    device = torch.device(cast("str", getattr(system, "device", "cpu")))
    x = torch.zeros(batch_size, int(gcfg.input_dim), device=device)
    y = torch.zeros(batch_size, dtype=torch.long, device=device)
    system.train_step(x, y)


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

    The G1 core-sweep path: every axis named explicitly by the coverage
    proposer, all built from the single-source config classmethods and
    registries — no preset tables, the grid re-measures (plan §0.3).
    """
    from computronium.ontology import (  # ruff: ignore[import-outside-top-level] (avoid import cycle)
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

    # Auto-propagate beta from dynamics to credit for EqProp and PC-ALM families.
    # EnergyMinimizationDynamics.beta must match ThermodynamicContrast.beta
    # (or PCALMCredit.beta) for correct gradient scaling.
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

    # Build substrate config - use noise for diffusion dynamics
    substrate_config = _build_substrate_config(substrate, dynamics)

    # Cross-axis hard constraints are the single source of truth (TODO28:
    # the campaign path previously skipped validate(), executing cells
    # validate() forbids — e.g. spike × thermodynamic_contrast at chance).
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

    # Diffusion, spike_integration, and PC-ALM dynamics require substrate noise > 0
    if dynamics in {"diffusion", "spike_integration", "pc_alm"}:
        return factory(noise_level=0.05)
    return factory()
