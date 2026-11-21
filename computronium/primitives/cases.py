"""The deterministic micro-case each primitive's reference step runs on.

A primitive's reference step is one execution of its law on a cell small
enough to run in milliseconds and structured enough to exercise the law's
contract: a typed config, a fixed geometry, a seeded payload, and whatever
companion state the law reads. The case's shape differs only per axis, so there
is one builder per axis and the per-primitive difference is data — its config
factory and its ontology class.

The companions are chosen by ``compose_configs``, the system's own legality
oracle: a case exists exactly when a cell can exist. That keeps the declared
legality table the one source of truth, so a law that only runs beside a
particular companion gets that companion, not a second hand-kept skip list.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import cache, lru_cache
from typing import TYPE_CHECKING, Any

import torch

from computronium.primitives.protocol import PrimitiveCase, PrimitiveSpec, StepResult

if TYPE_CHECKING:
    from computronium.ontology.system import SystemConfig

__all__ = [
    "AXES",
    "IMPOSSIBLE",
    "MICRO_BATCH",
    "MICRO_INPUT_SHAPE",
    "MICRO_OUTPUT_DIM",
    "build_case",
    "cell_config",
    "invariant",
    "step",
]

#: The micro-task every case presents: a four-wide vector batch with four
#: classes. Small enough that a law runs in milliseconds; wide enough that a
#: hidden layer and a readout are both non-degenerate.
MICRO_INPUT_SHAPE: tuple[int, ...] = (4,)
MICRO_OUTPUT_DIM = 4
MICRO_BATCH = 4
MICRO_TIME = 3

#: Rows the declared space refuses at every companion combination, with the
#: void constraint that refuses them (TODO97 §0: impossible is proved, counted).
IMPOSSIBLE: dict[str, str] = {
    "primitive.substrate.complex": "complex_substrate_real_compute",
}

AXES: tuple[str, ...] = (
    "substrate",
    "geometry",
    "dynamics",
    "plasticity",
    "credit",
    "update",
)


def _name(spec: PrimitiveSpec) -> str:
    """The registry name of ``spec`` (the last id segment)."""
    return spec.id.rsplit(".", 1)[-1]


def _generator(seed: int, device: str, offset: int = 0) -> torch.Generator:
    """A seeded generator; ``offset`` separates independent draws on one case."""
    return torch.Generator(device=device).manual_seed(seed + offset)


def _randn(
    shape: tuple[int, ...], seed: int, device: str, offset: int = 0
) -> torch.Tensor:
    """A standard-normal tensor drawn from ``seed``."""
    return torch.randn(shape, device=device, generator=_generator(seed, device, offset))


def _classes(shape: tuple[int, ...], seed: int, device: str) -> torch.Tensor:
    """Class indices in ``[0, MICRO_OUTPUT_DIM)`` drawn from ``seed``."""
    return torch.randint(
        0,
        MICRO_OUTPUT_DIM,
        shape,
        device=device,
        generator=_generator(seed, device, 1),
    )


@cache
def cell_config(spec: PrimitiveSpec, task_id: str = "mnist") -> SystemConfig:
    """The composed config of a cell the primitive's law can run in.

    The primitive's own axis is pinned to the spec; the five companions start
    at their declared defaults and are repaired until the declared space and
    the system's own validator both accept the cell. Two things decide
    legality, and both are the repository's declarations rather than a table
    here: the void constraints (``CONSTRAINTS_REGISTRY``, compiled by the
    search space) and ``compose_configs`` (``SystemConfig.validate`` and the
    axis availability predicates).

    A credit that declares ``requires_sequence`` reads a time-major batch, so
    the composer gives the geometry the single hidden layer its unroll contract
    states (``compose_configs``).

    Raises:
        PrimitiveImpossibleError: The declared space refuses the primitive's own axis
            value, so no cell can run it.
        RuntimeError: No companion combination composes for this primitive.
    """
    from computronium.experiment.kernel.compose import compose_configs
    from computronium.experiment.sec_loop import (
        _AXIS_DEFAULTS,
        _axis_values,
        _coordinate,
    )

    def compose(axes: dict[str, str]) -> SystemConfig | None:
        if _declared_legal(axes, _family_task(spec, task_id)) is not None:
            return None
        try:
            return compose_configs(
                coordinate=_coordinate(axes),
                geometry={},
                input_shape=MICRO_INPUT_SHAPE,
                output_dim=MICRO_OUTPUT_DIM,
            )
        except ValueError:
            return None

    task = _family_task(spec, task_id)
    axes = dict(_AXIS_DEFAULTS)
    axes[spec.axis] = _name(spec)
    refusal = _declared_legal(axes, task)
    config = compose(axes)
    if config is not None:
        return config

    companions = [axis for axis in AXES if axis != spec.axis]
    values = {axis: _axis_values(axis) for axis in companions}
    for size in (1, 2):
        config = _repair(axes, companions, values, size, compose)
        if config is not None:
            return config
    if refusal is not None:
        raise PrimitiveImpossibleError(spec.id, refusal)
    msg = f"{spec.id}: no companion combination composes a micro-cell"
    raise RuntimeError(msg)


def _repair(
    axes: dict[str, str],
    companions: list[str],
    values: dict[str, list[str]],
    size: int,
    compose: Any,
) -> SystemConfig | None:
    """Move at most ``size`` companion axes off the default until a cell composes."""
    from itertools import combinations, product

    for moved in combinations(companions, size):
        for chosen in product(*(values[axis] for axis in moved)):
            trial = {**axes, **dict(zip(moved, chosen, strict=True))}
            config = compose(trial)
            if config is not None:
                return config
    return None


@lru_cache(maxsize=1)
def _void_predicates() -> Any:
    """The compiled declared-void constraints of the search space.

    Seeds the registries first: they are declared at import but populated by
    ``seed_all_registries``, and an unseeded registry admits every combination
    (TODO46 D11).
    """
    from computronium.experiment.kernel.search_space import _compiled_void_constraints
    from computronium.experiment.schema.seed_registries import seed_all_registries

    seed_all_registries()
    return _compiled_void_constraints()


def _declared_legal(axes: dict[str, str], task: str) -> str | None:
    """The first declared void constraint this combination violates, else ``None``."""
    from computronium.experiment.schema.axis import StructuralAxis

    task_independent, task_dependent = _void_predicates()
    values = tuple(axes[axis.value] for axis in StructuralAxis)
    for name, check in task_independent:
        if not check((*values, "")):
            return name
    for name, check in task_dependent:
        if not check((*values, task)):
            return name
    return None


class PrimitiveImpossibleError(ValueError):
    """The declared space refuses every cell the primitive's axis can run in.

    Only ``impossible`` rows raise this, and only with the constraint that
    refuses them: the row is then quiet only if a refusal test and a necessity
    test both exist (TODO97 §0).

    Attributes:
        constraint: The declared void constraint that refuses the cell.
    """

    def __init__(self, primitive_id: str, constraint: str) -> None:
        super().__init__(
            f"{primitive_id}: refused by declared constraint {constraint!r}"
        )
        self.constraint = constraint


def _family_task(spec: PrimitiveSpec, task_id: str) -> str:
    """The task the declared space is asked about for this primitive's case.

    The requested task when the primitive declares a family that owns it;
    otherwise the base task of the primitive's first declared family. A base box
    is the declaration that a family has a task, so no second table is needed.
    """
    from computronium.experiment.sec_pilot import BASE_BOXES

    bases = [
        BASE_BOXES[family] for family in spec.task_families if family in BASE_BOXES
    ]
    if any(box.task_id == task_id for box in bases):
        return task_id
    return bases[0].task_id if bases else task_id


@dataclass(frozen=True, slots=True)
class _CaseContext:
    """The context a plasticity law reads: its device and its parameter set.

    A plasticity step reads ``context.device`` and, for training detection,
    ``context.theta``. The micro-case has no trained parameters, so the set is
    empty; the device is the case's.
    """

    device: torch.device

    @property
    def theta(self) -> dict[str, torch.Tensor]:
        """The persistent parameters; the micro-case has none."""
        return {}


def _geometry(geometry_config: Any, seed: int) -> Any:
    """The geometry a case runs against, built under the case's seed."""
    from computronium.harness import seeded_rng
    from computronium.ontology.geometry import geometry_from_config

    with seeded_rng(seed):
        return geometry_from_config(geometry_config)


def _input_shape(geometry_config: Any) -> tuple[int, ...]:
    """The batch a geometry accepts, read from its own declaration.

    Args:
        geometry_config: The composed ``GeometryConfig``.

    Returns:
        The input shape, batch first.
    """
    match geometry_config.topology_type:
        case "conv":
            return (MICRO_BATCH, geometry_config.in_channels, *geometry_config.input_hw)
        case "nca":
            return (MICRO_BATCH, geometry_config.input_dim, *geometry_config.grid_hw)
        case "causal_transformer":
            return (MICRO_BATCH, geometry_config.seq_len)
        case "graph":
            nodes = max(max(row) for row in geometry_config.connectivity["edge_index"])
            return (nodes + 1, geometry_config.input_dim)
        case _ if geometry_config.sequence:
            return (MICRO_TIME, MICRO_BATCH, geometry_config.input_dim)
        case _:
            return (MICRO_BATCH, geometry_config.input_dim)


def _geometry_input(geometry_config: Any, seed: int) -> torch.Tensor:
    """The tensor a geometry case forwards: class indices for a token geometry."""
    shape = _input_shape(geometry_config)
    if geometry_config.topology_type == "causal_transformer":
        return torch.randint(
            0,
            geometry_config.input_dim,
            shape,
            generator=_generator(seed, "cpu"),
        )
    return _randn(shape, seed, "cpu")


def _forward(geometry: Any, x: torch.Tensor, substrate: Any) -> torch.Tensor:
    """Forward ``x`` through ``geometry``, passing a graph batch when it has one."""
    return geometry(x, substrate)


def build_case(
    spec: PrimitiveSpec,
    task_id: str = "mnist",
    box: dict[str, Any] | None = None,
    seed: int = 0,
    device: str = "cpu",
    cell: SystemConfig | None = None,
) -> PrimitiveCase:
    """Build the deterministic case the primitive's reference step consumes.

    Args:
        spec: The primitive to build a case for.
        task_id: The task the case is filed under (provenance; the micro-case is
            task-independent by design).
        box: The hyperparameter box the case is filed under.
        seed: The seed for every draw, the geometry, and the config.
        device: The device the case's tensors live on.
        cell: The composed cell the case runs in; ``None`` reads the law's own
            registry cell. A companion cell is the removal's case, and it must
            carry the whole composed config, not the law's axis config alone.

    Returns:
        The case, with its typed config, its seeded payload, and its companions.
    """
    cell = cell_config(spec, task_id) if cell is None else cell
    axis_config = getattr(cell, spec.axis)
    config = {**asdict(axis_config), "seed": seed}
    extra = {**_payload(spec, cell, seed, device), "cell": cell}
    batch = extra.get("batch")
    return PrimitiveCase(
        config=config,
        box=dict(box or {}),
        seed=seed,
        task_id=task_id,
        batch=batch,
        extra=extra,
    )


def _payload(  # ruff: ignore[too-many-locals]
    spec: PrimitiveSpec, cell: SystemConfig, seed: int, device: str
) -> dict[str, Any]:
    """The axis-specific companions and payload a case carries."""
    match spec.axis:
        case "geometry":
            geometry = _geometry(cell.geometry, seed)
            x = _geometry_input(cell.geometry, seed).to(device)
            return {"geometry": geometry, "state": x, "batch": (x, None)}
        case "credit":
            geometry = _geometry(cell.geometry, seed)
            x, y = _classification(cell, seed, device)
            return {
                "geometry": geometry,
                "state": x,
                "nudged": x + 0.1 * _randn(tuple(x.shape), seed, device, 7),
                "targets": y,
                "batch": (x, y),
            }
        case "dynamics":
            from computronium.state import CompositeState

            x = _randn(_input_shape(cell.geometry), seed, device)
            classes = x.shape[:2] if x.dim() == 3 else (MICRO_BATCH,)
            state = CompositeState(
                activity={"x": x, "y": _classes(classes, seed, device)},
                plastic={},
                substrate={},
            )
            return {
                "geometry": _geometry(cell.geometry, seed),
                "state": state,
                "batch": (x, state.activity["y"]),
            }
        case "update":
            x = _randn((MICRO_BATCH, MICRO_INPUT_SHAPE[0]), seed, device)
            prediction = _randn(x.shape, seed, device, 2)
            multiplier = torch.ones_like(prediction)
            return {
                "state": x,
                "prediction": prediction,
                "multiplier": multiplier,
                "batch": (x, prediction),
            }
        case "plasticity":
            from computronium.state import CompositeState

            plasticity = _plasticity(cell.plasticity)
            psi = plasticity.initial_psi(None, MICRO_BATCH)
            width = MICRO_INPUT_SHAPE[0]
            state, hidden = (
                _randn((MICRO_BATCH, width), seed, device),
                _randn((MICRO_BATCH, width), seed, device, 2),
            )
            logits = _randn((MICRO_BATCH, MICRO_OUTPUT_DIM), seed, device, 3)
            targets = _classes((MICRO_BATCH,), seed, device)
            joint = CompositeState(
                activity={
                    "x": state,
                    "h": hidden,
                    "y": logits,
                    "target": targets,
                },
                plastic=psi,
                substrate={},
            )
            return {
                "psi": psi,
                "state": joint,
                "batch": (state, targets),
            }
        case "substrate":
            from computronium.ontology.substrate import substrate_from_config

            x = _randn((MICRO_BATCH, MICRO_INPUT_SHAPE[0]), seed, device)
            return {
                "substrate": substrate_from_config(cell.substrate),
                "state": x,
                "batch": (x, None),
            }
        case other:
            msg = f"{spec.id}: no case builder for axis {other!r}"
            raise ValueError(msg)


def _classification(
    cell: SystemConfig, seed: int, device: str
) -> tuple[torch.Tensor, torch.Tensor]:
    """The classification batch a credit case reads.

    A credit that declares ``requires_sequence`` reads ``x (time, batch, input)``
    and ``y (time, batch)``; every other credit reads one batch.
    """
    shape = _input_shape(cell.geometry)
    x = _randn(shape, seed, device)
    if cell.credit.requires_sequence:
        return x, _classes((MICRO_TIME, MICRO_BATCH), seed, device)
    return x, _classes((MICRO_BATCH,), seed, device)


def _plasticity(plasticity_config: Any) -> Any:
    """The plasticity law a config names, built through the one dispatcher."""
    from computronium.core.plasticity import plasticity_from_config

    return plasticity_from_config(plasticity_config)


def _logits(activations: list[torch.Tensor]) -> torch.Tensor:
    """The readout of an activation stack."""
    return activations[-1]


def _cell(spec: PrimitiveSpec, case: PrimitiveCase) -> SystemConfig:
    """The composed cell the case runs in, or the law's own registry cell."""
    return case.extra.get("cell") or cell_config(spec, case.task_id)


def step(spec: PrimitiveSpec, case: PrimitiveCase) -> StepResult:  # ruff: ignore[too-many-return-statements]
    """Run one reference step of the primitive's law on ``case``.

    Args:
        spec: The primitive the step runs.
        case: The case built by :func:`build_case`.

    Returns:
        The step's weights, activations, metrics, and named state.
    """
    match spec.axis:
        case "geometry":
            return _geometry_step(case)
        case "credit":
            return _credit_step(_cell(spec, case), case)
        case "dynamics":
            return _dynamics_step(_cell(spec, case), case)
        case "update":
            return _update_step(_cell(spec, case), case)
        case "plasticity":
            return _plasticity_step(_cell(spec, case), case)
        case "substrate":
            return _substrate_step(case)
        case other:
            msg = f"{spec.id}: no reference step for axis {other!r}"
            raise ValueError(msg)


def _geometry_step(case: PrimitiveCase) -> StepResult:
    """Forward the case's input through its geometry."""
    from computronium.ontology.substrate import DigitalSubstrate

    geometry = case.extra["geometry"]
    x = case.extra["state"]
    substrate = DigitalSubstrate()
    logits = _forward(geometry, x, substrate)
    acts = geometry.forward_with_intermediates(x, substrate)
    return StepResult(
        weights=list(geometry.parameters()),
        activations=list(acts),
        metrics={"output_norm": float(logits.detach().float().norm())},
        state={"logits": logits},
    )


def _credit_step(cell: SystemConfig, case: PrimitiveCase) -> StepResult:
    """One pseudo-gradient of the case's credit, from the pipeline's own phases."""
    from computronium.core.losses import cross_entropy
    from computronium.core.pipeline import _PhaseContext, _run_phases
    from computronium.core.system_trainer.spec import _credit_from_config
    from computronium.harness import seeded_rng
    from computronium.ontology.credit import Phase
    from computronium.ontology.dynamics import dynamics_from_config
    from computronium.ontology.substrate import DigitalSubstrate

    geometry = case.extra["geometry"]
    substrate = DigitalSubstrate()
    dynamics = dynamics_from_config(cell.dynamics)
    target = case.extra["targets"]
    x = case.extra["state"]
    with seeded_rng(case.seed):
        credit = _credit_from_config(cell.credit)
        context = _PhaseContext(
            credit=credit,
            dynamics=dynamics,
            geometry=geometry,
            substrate=substrate,
            initial_activations=geometry.forward_with_intermediates(x, substrate),
            x=x,
            y=target,
            plasticity=None,
            psi=None,
            context=None,
            loss_fn=cross_entropy,
            graph_kwargs={},
            owned_free=None,
        )
        phases = _run_phases(context)
        states = {
            phase: state
            for phase, state in phases.items()
            if phase in {Phase.FREE, Phase.NUDGED}
        }
        readout = states[credit.phases[-1]].activations[-1]
        loss = cross_entropy(readout.reshape(-1, readout.shape[-1]), target.reshape(-1))
        grads = credit.compute_pseudo_gradient(states, loss, geometry)
    return StepResult(
        weights=list(grads),
        activations=[],
        metrics={"pseudo_gradient_norm": float(sum(g.norm() for g in grads))},
        state={"loss": float(loss.detach())},
    )


def _dynamics_step(cell: SystemConfig, case: PrimitiveCase) -> StepResult:
    """One settle of the case's dynamics on its geometry."""
    from computronium.harness import seeded_rng
    from computronium.ontology.dynamics import dynamics_from_config
    from computronium.ontology.substrate import DigitalSubstrate

    with seeded_rng(case.seed):
        dynamics = dynamics_from_config(cell.dynamics)
        settled = dynamics.settle(
            case.extra["state"], case.extra["geometry"], DigitalSubstrate()
        )
    return StepResult(
        weights=list(case.extra["geometry"].parameters()),
        activations=list(settled.activations or []),
        metrics={},
        state={"settled": settled},
    )


def _update_step(cell: SystemConfig, case: PrimitiveCase) -> StepResult:
    """One parameter update on the case's geometry and pseudo-gradients."""
    from computronium.harness import update_geometry, update_pseudo_grads
    from computronium.ontology.update import update_from_config

    geometry = update_geometry(case)
    params = dict(geometry.params)
    grads = update_pseudo_grads(case, geometry)
    with torch.no_grad():
        updated = update_from_config(cell.update).step(params, grads, geometry)
    return StepResult(
        weights=list(updated.values()),
        activations=[],
        metrics={},
        state={"updated": updated},
    )


def _plasticity_step(cell: SystemConfig, case: PrimitiveCase) -> StepResult:
    """One plastic-state transition of the case's law, then its modulation.

    The primitive runs the same P-axis protocol the trainer runs
    (``pipeline._run_phases``): ψ steps once, then the law's ``modulate``
    hook applies the new plastic state to the activity. A digest that read
    only ψ would miss every law whose declared channel is the modulation.
    """
    from computronium.harness import seeded_rng

    plasticity = _plasticity(cell.plasticity)
    state = case.extra["state"]
    context = _CaseContext(device=state.activity["x"].device)
    activations: list[torch.Tensor] = []
    with seeded_rng(case.seed):
        psi = plasticity.step(case.extra["psi"], state, context)
        modulate = getattr(plasticity, "modulate", None)
        if modulate is not None:
            acts = [
                value
                for key in ("h", "y")
                if isinstance(value := state.activity.get(key), torch.Tensor)
            ]
            modulated = modulate(acts, psi)
            activations = modulated if isinstance(modulated, list) else [modulated]
    return StepResult(
        weights=list(psi.values()),
        activations=activations,
        metrics={},
        state={"psi": psi},
    )


def _substrate_step(case: PrimitiveCase) -> StepResult:
    """One forward operation through the case's substrate.

    The probe weight is dense and seeded, not the identity: a quantizer maps
    the identity to itself (every 1 is above any magnitude threshold), so an
    identity probe makes ``ternary``, ``sparse`` and ``noisy`` digest equal
    to ``digital`` and the removal unobservable. The output then passes the
    substrate's own state noise, so a law whose mechanism is that noise is
    measured rather than silently equal to its companion.
    """
    from computronium.harness import seeded_rng

    substrate = case.extra["substrate"]
    x = case.extra["state"]
    width = x.shape[-1]
    weight = torch.randn(
        (width, width),
        generator=_generator(case.seed, str(x.device), 11),
        device=x.device,
    )
    weight = substrate.quantize_weights(weight)
    with seeded_rng(case.seed):
        output = substrate.get_forward_operator()(x, weight)
        output = substrate.inject_state_noise(output)
    return StepResult(
        weights=[weight],
        activations=[output],
        metrics={"output_norm": float(output.detach().float().norm())},
        state={},
    )


def invariant(  # ruff: ignore[too-many-return-statements]
    spec: PrimitiveSpec,
    case: PrimitiveCase,
) -> bool:
    """The axis-level invariant for ``spec`` on ``case``.

    One predicate per axis, on the same case and step the contracts use, so a
    new primitive inherits its invariant by registering.

    Args:
        spec: The primitive to check.
        case: The case built by :func:`build_case`.

    Returns:
        Whether the step satisfies the axis's analytic invariant.
    """
    result = step(spec, case)
    tensors = [
        *result.weights,
        *result.activations,
        *(
            value
            for value in (
                result.state.get("settled"),
                result.state.get("psi"),
            )
            if isinstance(value, torch.Tensor)
        ),
    ]
    if not tensors:
        # A plasticity law whose case declares no plastic state has nothing to
        # move: the empty step is its declared state, not a failed invariant.
        return spec.axis == "plasticity" and not case.extra.get("psi")
    if not all(tensor.isfinite().all() for tensor in tensors):
        return False
    match spec.axis:
        case "geometry":
            return bool(result.activations) and result.activations[-1].shape[-1] > 0
        case "credit":
            return bool(result.weights) and all(
                weight.shape == grad.shape
                for weight, grad in zip(
                    [p for p in case.extra["geometry"].params.values() if p.dim() == 2],
                    result.weights,
                    strict=False,
                )
            )
        case "dynamics":
            settled = result.state["settled"]
            return bool(settled.activations) and settled.activity.get("x") is not None
        case "update":
            return bool(result.state["updated"])
        case "plasticity":
            return set(result.state["psi"]) >= set(case.extra["psi"])
        case "substrate":
            return bool(result.activations)
        case _:
            return False
