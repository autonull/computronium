"""Kernel-native system composition for grid cells.

Composes a full grid cell (dynamics × credit × update × topology) from the
single-source config classmethods and registries — no preset tables.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Final

from computronium.core.logging import get_logger
from computronium.core.pipeline import _task_loss_tensor, forward_pass
from computronium.core.system_trainer import (
    compose_joint_system_from_configs,
    compose_system_from_configs,
)
from computronium.core.system_trainer.factory import param_count
from computronium.experiment.learning.prior import apply_dynamics_step_size
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.geometry_keys import (
    TOPOLOGY_KEYS,
    allowed_geometry_keys,
)
from computronium.experiment.schema.harvest import (
    ActiveSpace,
    harvest_schema,
)
from computronium.ontology import GeometryConfig
from computronium.ontology.credit import Phase
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.dynamics._state import set_state_field
from computronium.ontology.system import SystemState
from computronium.ontology.utils import _learnable_weight_names

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

class ProposalComposeError(ValueError):
    """A proposal's geometry or task could not be resolved to a runnable system."""


def _dry_run_trainable(  # ruff: ignore[too-many-statements, too-many-branches, too-many-return-statements, too-many-locals, complex-structure]
    coordinate: Coordinate,
    geometry: Mapping[str, object],
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int,
) -> tuple[bool, str]:
    """Run a minimal dry-run to verify the cell can train.

    This catches:
    - RandomProjectionsCredit: detached settle graph or feedback/act width mismatch
    - GradientCredit: no gradient reaching learnable weights (detached graph)
    - Other credits: any failure in compute_pseudo_gradient

    Args:
        coordinate: The six-axis coordinate.
        geometry: Topology parameters.
        input_shape: The task's input shape.
        output_dim: Number of output classes.
        param_budget: Parameter budget.

    Returns:
        (ok, reason): True if dry-run passes, False with reason if it fails.
    """
    import torch

    # Only run dry-run for credits that have known failure modes
    credit_name = coordinate.credit
    DRY_RUN_CREDITS: set[str] = {"random_projections", "gradient"}
    if credit_name not in DRY_RUN_CREDITS:
        return True, "credit not checked"

    try:  # ruff: ignore[too-many-statements-in-try-clause]
        # Compose the full cell system
        cell = compose_cell_system(
            coordinate=coordinate,
            geometry=geometry,
            input_shape=input_shape,
            output_dim=output_dim,
            param_budget=param_budget,
        )
        system = cell.system

        # Create a dummy input batch (batch_size=2 for batch norm etc.)
        batch_size = 2
        if len(input_shape) == 1:
            # Sequence or flat: (seq_len,) or (dim,)
            x = torch.randint(
                0, output_dim, (batch_size, input_shape[0]), dtype=torch.long
            )
        elif len(input_shape) == 2:
            # (H, W) grayscale
            x = torch.randn(batch_size, 1, *input_shape)
        elif len(input_shape) == 3:
            x = torch.randn(batch_size, *input_shape)
        else:
            x = torch.randn(batch_size, *input_shape)

        # Target: random labels
        y = torch.randint(0, output_dim, (batch_size,))

        # Move to CPU (dry-run runs on CPU)
        system = system.to("cpu")  # type: ignore[attr-defined]
        x = x.to("cpu")
        y = y.to("cpu")

        credit = system.credit
        requires_autograd = getattr(credit, "requires_autograd", False)

        # Run forward pass and settle with/without autograd
        grad_ctx = torch.enable_grad() if requires_autograd else torch.no_grad()
        with grad_ctx:
            initial_activations = forward_pass(system.substrate, system.geometry, x)

            states = {}
            for phase in credit.phases:
                state = SystemState(x=x, y=y)
                state.activations = initial_activations
                target = y if phase is Phase.NUDGED else None
                settled = system.dynamics.settle(
                    state, system.geometry, system.substrate, target=target
                )

                # Compute loss for nudged phase
                if phase is Phase.NUDGED:
                    loss_tensor, _ = _task_loss_tensor(settled, y)
                    set_state_field(settled, "loss", loss_tensor)

                states[phase] = settled

            # Try to compute pseudo-gradients - this is where failures occur
            output_state = states.get(Phase.NUDGED) or states.get(Phase.FREE)
            if output_state is None:
                return False, "no settled states available"
            loss = output_state.loss
            if loss is None:
                loss, _ = _task_loss_tensor(output_state, y)

            pseudo_grads = credit.compute_pseudo_gradient(states, loss, system.geometry)

            weight_names = _learnable_weight_names(system.geometry.params)
            if len(pseudo_grads) != len(weight_names):
                return (
                    False,
                    f"pseudo_gradient count mismatch: got {len(pseudo_grads)}, expected {len(weight_names)}",
                )

            # Check for all-zero gradients (no-op)
            if all(g.abs().max() == 0 for g in pseudo_grads):
                return False, "all-zero pseudo-gradients (no-op)"

        return True, "ok"  # ruff: ignore[try-consider-else]

    except RuntimeError as e:
        msg = str(e)
        if "all-zero pseudo-gradient" in msg or "layered FA contract" in msg:
            return False, f"RandomProjectionsCredit: {msg}"
        if "no gradient reached" in msg:
            return False, f"GradientCredit: {msg}"
        return False, f"RuntimeError: {msg}"
    except Exception as e:
        return False, f"Exception: {type(e).__name__}: {e}"


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
    return allowed_geometry_keys(topology)


def build_geometry_config(
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
    from computronium.experiment.kernel._geometry_builders import build_geometry_config_dispatch

    return build_geometry_config_dispatch(
        topology=topology,
        input_shape=input_shape,
        output_dim=output_dim,
        param_budget=param_budget,
        geometry=geometry,
    )


def _build_substrate_config(
    substrate_name: str, dynamics: str, params: Mapping[str, object] | None = None
):
    """Build substrate config from the cell's swept substrate values."""
    from computronium.experiment.schema.axis import get_axis_spec
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

    axis_spec = get_axis_spec(StructuralAxis.SUBSTRATE, substrate_name)
    accepted = set(axis_spec.accepted_params) if axis_spec is not None else set()
    kwargs = {key: value for key, value in (params or {}).items() if key in accepted}
    if dynamics in {"diffusion", "spike_integration", "pc_alm"}:
        kwargs.setdefault("noise_level", 0.05)
    return factory(**kwargs)


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

    The values come from ``ActiveSpace.for_axis`` — the same predicate that
    decides, in the search space, which swept values a cell may carry — so a
    value the space carries is exactly one composition reads. Geometry
    hyperparameters are named for the keys the normalizer reads, so no
    translation is applied.
    """
    harvested = {
        name: value
        for name, value in active.for_axis(StructuralAxis.GEOMETRY, topology).items()
        if f"geometry.{name}" in swept
    }
    return {**harvested, **geometry}


def _axis_factory(config_cls: Any, primitive: str) -> Any:
    """Resolve an axis name to its config factory through the ontology surface."""
    factory = getattr(config_cls, primitive, None)
    if not callable(factory):
        msg = f"Unknown cell axis: {primitive!r} is not a config factory"
        raise ProposalComposeError(msg)
    return factory


def _extract_graph_edge_index(task: Any) -> list[list[int]] | None:
    """Extract edge_index from a graph task if available."""
    # GraphTask (node classification) has _data.edge_index
    if hasattr(task, "_data") and hasattr(task._data, "edge_index"):
        return task._data.edge_index.tolist()
    # GraphClassificationTask uses TUDataset - use first graph's edge_index as representative
    if hasattr(task, "_train_loader") and task._train_loader is not None:
        try:
            batch = next(iter(task._train_loader))
            if hasattr(batch, "edge_index"):
                return batch.edge_index.tolist()
        except StopIteration, AttributeError:
            pass
    return None


def _make_hashable(value: Any) -> Any:
    """Recursively convert lists and dicts to hashable tuples."""
    if isinstance(value, list):
        return tuple(_make_hashable(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in value.items()))
    return value


def _restore_mutable(value: Any) -> Any:
    """Recursively convert tuples back to lists for validation."""
    if isinstance(value, tuple):
        return [_restore_mutable(v) for v in value]
    return value


@dataclass(frozen=True, slots=True)
class ComposeCacheKey:
    """Cache key for compose_configs: all structural parameters affecting composition.

    Fully hashable - contains no mutable objects or external references.
    """

    substrate: str
    geometry: str
    dynamics: str
    plasticity: str
    credit: str
    update: str
    params: tuple[tuple[str, Any], ...]  # sorted coordinate.params items
    geometry_explicit: tuple[tuple[str, Any], ...]  # sorted explicit geometry items
    input_shape: tuple[int, ...]
    output_dim: int
    param_budget: int

    @classmethod
    def from_compose_args(
        cls,
        coordinate: Coordinate,
        geometry: Mapping[str, object],
        input_shape: tuple[int, ...],
        output_dim: int,
        param_budget: int,
    ) -> ComposeCacheKey:
        """Create cache key from compose_configs arguments."""
        # Convert coordinate params to sorted tuple
        coord_params = tuple(
            sorted((k, _make_hashable(v)) for k, v in coordinate.params.items())
        )

        # Convert geometry to sorted tuple with hashable values
        geometry_items = []
        for k, v in sorted(geometry.items()):
            geometry_items.append((k, _make_hashable(v)))
        geometry_explicit = tuple(geometry_items)

        return cls(
            substrate=coordinate.substrate,
            geometry=coordinate.geometry,
            dynamics=coordinate.dynamics,
            plasticity=coordinate.plasticity,
            credit=coordinate.credit,
            update=coordinate.update,
            params=coord_params,
            geometry_explicit=geometry_explicit,
            input_shape=input_shape,
            output_dim=output_dim,
            param_budget=param_budget,
        )

    def to_coordinate(self) -> Coordinate:
        """Reconstruct a minimal coordinate for the cached function."""
        from computronium.experiment.schema.coordinate import Coordinate

        params = dict(self.params)
        return Coordinate(
            substrate=self.substrate,
            geometry=self.geometry,
            dynamics=self.dynamics,
            plasticity=self.plasticity,
            credit=self.credit,
            update=self.update,
            params=params,
        )

    def to_geometry_dict(self) -> dict[str, object]:
        """Reconstruct geometry dict with mutable values for validation."""
        return {k: _restore_mutable(v) for k, v in self.geometry_explicit}


@lru_cache(maxsize=10000)
def _compose_configs_cached(cache_key: ComposeCacheKey) -> Any:  # ruff: ignore[too-many-locals]
    """Cached inner implementation of compose_configs.

    Uses the ComposeCacheKey dataclass directly for the LRU cache.
    """
    from computronium.ontology import (
        CreditAssignmentConfig,
        ParameterUpdateConfig,
        StateDynamicsConfig,
    )
    from computronium.ontology.system import SystemConfig
    from computronium.state.transitions import PlasticityConfig

    coordinate = cache_key.to_coordinate()
    geometry_dict = cache_key.to_geometry_dict()
    input_shape = cache_key.input_shape
    output_dim = cache_key.output_dim
    param_budget = cache_key.param_budget

    active = harvest_schema().active(coordinate)
    substrate_name = coordinate.substrate
    dynamics_name = coordinate.dynamics

    gcfg = _fit_geometry(
        _geometry_mapping(
            active, geometry_dict, coordinate.geometry, coordinate.params
        ),
        topology=coordinate.geometry,
        input_shape=input_shape,
        output_dim=output_dim,
        param_budget=param_budget,
    )

    d_factory = _axis_factory(StateDynamicsConfig, dynamics_name)
    dynamics_step_size = active.values.get(
        "dynamics.step_size", _config_default_step_size(d_factory)
    )
    if "dynamics.step_size" not in coordinate.params:
        dynamics_step_size = apply_dynamics_step_size(dynamics_step_size, dynamics_name)
    dcfg = d_factory(**{
        **active.for_axis(StructuralAxis.DYNAMICS, dynamics_name),
        "step_size": dynamics_step_size,
    })

    c_factory = _axis_factory(CreditAssignmentConfig, coordinate.credit)
    ccfg = c_factory(**active.for_axis(StructuralAxis.CREDIT, coordinate.credit))

    u_factory = _axis_factory(ParameterUpdateConfig, coordinate.update)
    ucfg = u_factory(**active.for_axis(StructuralAxis.UPDATE, coordinate.update))

    substrate_config = _build_substrate_config(
        substrate_name,
        dynamics_name,
        active.for_axis(StructuralAxis.SUBSTRATE, substrate_name),
    )
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


def compose_configs(  # ruff: ignore[too-many-locals]
    *,
    coordinate: Coordinate,
    geometry: Mapping[str, object],
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int = 0,
    task: Any | None = None,
) -> Any:
    """Compose and validate the configs of one cell, building no ``System``.

    What each primitive can accept is decided by availability predicates in
    ``AXES``, evaluated against ``coordinate`` — not by inspecting factories and
    not by branching on pairs of axis names. Adding a coupling between two axes
    is a spec row. Cross-axis legality is ``SystemConfig.validate``, so this is
    also the cheap way to ask *whether a cell can exist* before spending a
    training run on it.

    Uses an LRU cache (maxsize=10000) keyed by (coordinate, geometry, input_shape,
    output_dim, param_budget) to avoid re-composing the same cell across seeds/rounds.

    Args:
        coordinate: The six-axis selection and its hyperparameter overrides.
        geometry: Topology parameters; harvested geometry values fill the gaps.
        input_shape: The task's own input shape, channels first.
        output_dim: Class count, derived from the task.
        param_budget: Parameter ceiling for derived sizing; 0 disables it.
        task: Optional task instance for extracting task-specific geometry data
            (e.g., edge_index for graph tasks).

    Returns:
        The validated ``SystemConfig`` for the cell.

    Raises:
        ProposalComposeError: A primitive, or one of its parameters, has no
            place in this cell.
        ValueError: ``SystemConfig.validate`` rejected the combination.
    """
    # Auto-extract graph edge_index from task if not provided in geometry
    geometry_dict = dict(geometry)
    if (
        coordinate.geometry == "graph"
        and "edge_index" not in geometry_dict
        and task is not None
    ):
        edge_index = _extract_graph_edge_index(task)
        if edge_index is not None:
            geometry_dict["edge_index"] = edge_index

    # Build cache key using the ComposeCacheKey dataclass
    cache_key = ComposeCacheKey.from_compose_args(
        coordinate, geometry_dict, input_shape, output_dim, param_budget
    )
    return _compose_configs_cached(cache_key)


def compose_cell_system(
    *,
    coordinate: Coordinate,
    geometry: Mapping[str, object],
    input_shape: tuple[int, ...],
    output_dim: int,
    param_budget: int = 0,
    task: Any | None = None,
) -> ComposedCell:
    """Compose a full grid cell and build its ``System``.

    Args:
        coordinate: The six-axis selection and its hyperparameter overrides.
        geometry: Topology parameters; harvested geometry values fill the gaps.
        input_shape: The task's own input shape, channels first.
        output_dim: Class count, derived from the task.
        param_budget: Parameter ceiling for derived sizing; 0 disables it.
        task: Optional task instance for extracting task-specific geometry data
            (e.g., edge_index for graph tasks).

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
        task=task,
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

    Names are per-axis (``dynamics.step_size`` vs ``update.step_size``), so each
    axis records the value its own config actually holds under its own name.
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
                config, spec.name, active.values[f"{axis.value}.{spec.name}"]
            )
    return effective


def _config_default_step_size(factory: Any) -> float:
    """The step size a dynamics factory would take from its dataclass default."""
    for field in fields(StateDynamicsConfig):
        if field.name == "step_size" and isinstance(field.default, float):
            return field.default
    return 0.1
