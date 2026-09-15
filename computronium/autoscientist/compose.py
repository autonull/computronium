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
}


class ProposalComposeError(ValueError):
    """A proposal's geometry or task could not be resolved to a runnable system."""


def _as_int(value: object, default: int) -> int:
    return int(value) if isinstance(value, int | float) else default


def _as_float(value: object, default: float) -> float:
    return float(value) if isinstance(value, int | float) else default


def _as_int_tuple(value: object, default: tuple[int, ...]) -> tuple[int, ...]:
    if isinstance(value, list | tuple) and all(
        isinstance(v, int | float) for v in value
    ):
        return tuple(int(v) for v in value)
    return default


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


def build_geometry_config(  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches]
    geometry: dict[str, object],
    *,
    input_dim: int,
    output_dim: int,
) -> GeometryConfig:
    """Build a ``GeometryConfig`` from a proposal's geometry dict.

    Args:
        geometry: Validated keys are the common set (``topology_type``,
            ``hidden_dim``, ``depth``, ``init_scheme``, ``init_scale``) plus
            the proposal topology's own extras. Unknown keys raise.
        input_dim: Task input dimension.
        output_dim: Task output dimension.
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

    hidden = _as_int(geometry.get("hidden_dim"), 64)
    depth = max(_as_int(geometry.get("depth"), 2), 1)
    init_scheme = str(geometry.get("init_scheme", "default"))
    if init_scheme not in {"default", "mupc"}:
        msg = f"init_scheme must be 'default' or 'mupc', got {init_scheme!r}"
        raise ProposalComposeError(msg)
    init_scale = _as_float(geometry.get("init_scale"), 0.1)
    hidden_dims = (hidden,) * depth

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
                neurons_per_tile=_as_int(geometry.get("neurons_per_tile"), 48),
                tiles_per_layer=_as_int(geometry.get("tiles_per_layer"), 4),
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
            return GeometryConfig.spatial_lattice(
                input_dim=input_dim,
                output_dim=output_dim,
                lattice_dims=_as_int_tuple(  # type: ignore[arg-type]
                    geometry.get("lattice_dims"), (4, 4, 4)
                ),
                hidden_dims=hidden_dims,
                connectivity_radius=_as_int(geometry.get("connectivity_radius"), 1),
                init_scale=init_scale,
            )
        case "nca":
            return GeometryConfig.nca(
                channels=hidden,
                hidden=hidden,
                grid_hw=_as_int_tuple(geometry.get("grid_hw"), (16, 16)),  # type: ignore[arg-type]
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
        geometry, input_dim=input_dim, output_dim=output_dim
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
) -> System:
    """Compose a full grid cell (dynamics × credit × update × topology).

    The G1 core-sweep path: every axis named explicitly by the coverage
    proposer, all built from the single-source config classmethods and
    registries — no preset tables, the grid re-measures (plan §0.3).
    """
    from computronium.ontology import (  # ruff: ignore[import-outside-top-level] (avoid import cycle)
        CreditAssignmentConfig,
        DigitalSubstrate,
        ParameterUpdateConfig,
        StateDynamicsConfig,
    )

    gcfg = build_geometry_config(geometry, input_dim=input_dim, output_dim=output_dim)
    try:
        dcfg = getattr(StateDynamicsConfig, dynamics)()
        ccfg = getattr(CreditAssignmentConfig, credit)()
        update_factory = getattr(ParameterUpdateConfig, update)
        kwargs = (
            {"step_size": lr}
            if "step_size" in inspect.signature(update_factory).parameters
            else {}
        )
        ucfg = update_factory(**kwargs)
    except AttributeError as exc:
        msg = f"Unknown cell axis: {exc.args[0]!r} is not a config factory"
        raise ProposalComposeError(msg) from exc
    return compose_system_from_configs(
        DigitalSubstrate().config,
        gcfg,
        dcfg,
        ccfg,
        ucfg,
    )
