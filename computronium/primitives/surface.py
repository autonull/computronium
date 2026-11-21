"""The declared test surface: 75 laws, 6 protocol seams, and the rule tables.

TODO98's unit is the law, not the ``(primitive, family, box)`` row. A law is a
registry row: its ID, its axis, its family, and the knobs composition may pass
it. A seam is two laws exchanging what they declare. A rule is a compiled void
constraint or an axis availability predicate.

The surface is derived on call from the registry, the axis specs, and the
compiled constraints — there is no second list. A new primitive adds one
registry row and inherits its tests; a new constraint adds one predicate and
inherits its accept/refuse pair. ``comp test --surface`` prints this surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from computronium.primitives.protocol import PrimitiveSpec

__all__ = [
    "SEAMS",
    "Law",
    "Rule",
    "Seam",
    "Surface",
    "laws",
    "rules",
    "seams",
    "surface",
    "validate",
]


@dataclass(frozen=True, slots=True)
class Law:
    """One registered primitive: its law, its declared knobs, its state."""

    id: str
    axis: str
    family: str
    knobs: tuple[str, ...]
    refusal: str | None = None
    gap: str | None = None


@dataclass(frozen=True, slots=True)
class Seam:
    """One protocol seam: two laws exchanging what they declare.

    Attributes:
        name: The seam's name, and the key its check is filed under.
        axis: The axis of the exemplar primitive.
        primitive_id: The registry row that anchors the seam.
        task_id: The declared task the exemplar runs on.
        exchange: What the seam proves reaches the other side.
    """

    name: str
    axis: str
    primitive_id: str
    task_id: str
    exchange: str


#: The six protocol seams, each with its exemplar and the exchange it proves.
#: A seam is a declaration: the test surface maps each name to the check that
#: exercises it, and a seam without a check fails the lock.
SEAMS: tuple[Seam, ...] = (
    Seam(
        name="label channel",
        axis="credit",
        primitive_id="primitive.credit_assignment.local_contrastive",
        task_id="mnist",
        exchange="the target reaches the credit through the widened input",
    ),
    Seam(
        name="token lane",
        axis="geometry",
        primitive_id="primitive.geometry.causal_transformer",
        task_id="tiny_shakespeare",
        exchange="token ids and their targets broadcast through the token task",
    ),
    Seam(
        name="time axis",
        axis="geometry",
        primitive_id="primitive.geometry.recurrent",
        task_id="delayed_cue",
        exchange="(time, batch, features) unrolls through the recurrent geometry",
    ),
    Seam(
        name="graph topology",
        axis="geometry",
        primitive_id="primitive.geometry.graph",
        task_id="cora",
        exchange="edge_index reaches the topology",
    ),
    Seam(
        name="settle",
        axis="dynamics",
        primitive_id="primitive.state_dynamics.energy_minimization",
        task_id="mnist",
        exchange="the settle converges on one geometry",
    ),
    Seam(
        name="joint plasticity",
        axis="plasticity",
        primitive_id="primitive.plasticity.routing",
        task_id="copy_task",
        exchange="both the plastic and the parameter update path run",
    ),
)


@dataclass(frozen=True, slots=True)
class Rule:
    """One declared rule, with the declaration that decides it."""

    name: str
    table: Literal["task-independent", "task-dependent", "availability"]
    predicate: object


@dataclass(frozen=True, slots=True)
class Surface:
    """The whole declared test surface."""

    laws: tuple[Law, ...]
    seams: tuple[Seam, ...]
    rules: tuple[Rule, ...]

    @property
    def tables(self) -> tuple[int, int, int]:
        """Rule counts per table: task-independent, task-dependent, availability."""
        counts = {"task-independent": 0, "task-dependent": 0, "availability": 0}
        for rule in self.rules:
            counts[rule.table] += 1
        return (
            counts["task-independent"],
            counts["task-dependent"],
            counts["availability"],
        )


def _seeds() -> None:
    """Seed the axis registries once, before the surface reads them."""
    from computronium.experiment.schema.axis import AXES_REGISTRIES, StructuralAxis

    if not AXES_REGISTRIES[StructuralAxis.GEOMETRY]:
        from computronium.experiment.schema.seed_registries import seed_all_registries

        seed_all_registries()


def _axes() -> Any:
    from computronium.experiment.schema import AXES_REGISTRIES

    return AXES_REGISTRIES


def _family(spec: PrimitiveSpec) -> str:
    """The cheapest declared family that owns a base box."""
    from computronium.experiment.sec_pilot import BASE_BOXES

    return next((family for family in spec.task_families if family in BASE_BOXES), "")


def _axis_spec(spec: PrimitiveSpec) -> Any:
    from computronium.experiment.schema.axis import StructuralAxis

    return _axes()[StructuralAxis(spec.axis)].get(spec.id.rsplit(".", 1)[-1])


def laws() -> tuple[Law, ...]:
    """One row per registered law, joined with its axis declaration."""
    from computronium.primitives.cases import IMPOSSIBLE
    from computronium.primitives.registry import list_primitives

    _seeds()
    rows: list[Law] = []
    for spec in sorted(list_primitives(), key=lambda row: row.id):
        axis_spec = _axis_spec(spec)
        refusal = IMPOSSIBLE.get(spec.id)
        rows.append(
            Law(
                id=spec.id,
                axis=spec.axis,
                family=_family(spec),
                knobs=tuple(sorted(axis_spec.accepted_params)) if axis_spec else (),
                refusal=refusal,
                gap=None if axis_spec is None else axis_spec.unavailable_reason,
            )
        )
    return tuple(rows)


def rules() -> tuple[Rule, ...]:
    """The compiled void constraints, plus every availability predicate."""
    from computronium.experiment.kernel.search_space import _compiled_void_constraints
    from computronium.experiment.schema.harvest import harvest_schema

    _seeds()
    independent, dependent = _compiled_void_constraints()
    declared = [
        Rule(name=name, table="task-independent", predicate=predicate)
        for name, predicate in independent
    ]
    declared += [
        Rule(name=name, table="task-dependent", predicate=predicate)
        for name, predicate in dependent
    ]
    declared += [
        Rule(
            name=f"{spec.axis_name}.{spec.name}",
            table="availability",
            predicate=spec.availability,
        )
        for spec in harvest_schema().hyperparameters
        if spec.availability is not None
    ]
    return tuple(declared)


def seams() -> tuple[Seam, ...]:
    """The six protocol seams, in declaration order."""
    return SEAMS


def surface() -> Surface:
    """The whole surface, derived from the repository's declarations."""
    return Surface(laws=laws(), seams=seams(), rules=rules())


def validate(declared: Surface) -> list[str]:
    """What disagrees with the registry, as problems the caller reports.

    An empty list is the surface's acceptance: one law per registered
    primitive, six seams whose exemplars exist on the declared axis, and the
    rule tables the registry compiles.
    """
    from computronium.domains.registry import SUPPORTED_TASKS
    from computronium.primitives.registry import get_primitive_spec

    problems: list[str] = []
    if len(declared.laws) != 75:
        problems.append(f"{len(declared.laws)} laws, expected 75")
    if len({law.id for law in declared.laws}) != len(declared.laws):
        problems.append("a law ID repeats")
    if len(declared.seams) != 6:
        problems.append(f"{len(declared.seams)} seams, expected 6")
    if len({seam.name for seam in declared.seams}) != len(declared.seams):
        problems.append("a seam name repeats")
    for seam in declared.seams:
        spec = get_primitive_spec(seam.primitive_id)
        if spec is None:
            problems.append(
                f"seam {seam.name!r}: {seam.primitive_id} is not registered"
            )
            continue
        if spec.axis != seam.axis:
            problems.append(
                f"seam {seam.name!r}: {seam.primitive_id} is on {spec.axis!r}, "
                f"declared {seam.axis!r}"
            )
        if seam.task_id not in SUPPORTED_TASKS:
            problems.append(f"seam {seam.name!r}: {seam.task_id!r} is not a task")
    if not declared.rules:
        problems.append("the rule tables are empty")
    return problems
