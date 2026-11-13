"""Surface inventory: one table joining every declared selection surface.

TODO91 S0. The selection surface is spread over six registries, a spec matrix,
a docs page, and package directories. Each was individually green while the
join was unverifiable, which is how seven algorithm packages stayed invisible
and two domain classes stayed empty. This module joins them, so a row is
`implemented` only when a smoke path exists on disk, `declared` only when a
recorded reason and trigger exist, and `unknown` otherwise.

Coverage rule (TODO91 §2): an entry is covered when (a) the code path exists,
(b) one smoke command exercises it end to end, and (c) a lock fails if the
entry disappears. A registry listing alone is not coverage.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

from computronium.experiment.schema.axis import StructuralAxis

__all__ = [
    "DeclaredClaim",
    "InventoryKind",
    "InventoryReport",
    "InventoryRow",
    "InventoryStatus",
    "build_inventory",
]

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
TESTS = "tests"
GENERATED_TESTS = "tests/property/generated"
COMPLETENESS_LOCK = "tests/property/test_registry_completeness_lock.py"
TASK_SMOKE = (
    "tests/acceptance/test_v1_exit.py::TestV1Exit::test_02_reachability_locks_pass"
)
OBJECTIVE_SMOKE = "tests/property/test_objective_breadth_lock.py"


class InventoryStatus(StrEnum):
    """Whether a surface row runs, is declared absent, or is unexplained."""

    IMPLEMENTED = "implemented"
    DECLARED = "declared"
    UNKNOWN = "unknown"


class InventoryKind(StrEnum):
    """The surface an inventory row belongs to."""

    ALGORITHM = "algorithm"
    PRIMITIVE = "primitive"
    TASK = "task"
    DOMAIN = "domain"
    OBJECTIVE = "objective"
    CAPABILITY = "capability"
    ARCHITECTURE = "architecture"


@dataclass(frozen=True, slots=True)
class InventoryRow:
    """One selectable surface entry and the evidence for its status."""

    id: str
    kind: InventoryKind
    runtime_name: str | None
    status: InventoryStatus
    smoke_path: str | None
    reason_or_trigger: str | None
    axis: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "id": self.id,
            "kind": self.kind.value,
            "axis": self.axis,
            "runtime_name": self.runtime_name,
            "status": self.status.value,
            "smoke_path": self.smoke_path,
            "reason_or_trigger": self.reason_or_trigger,
        }


@dataclass(frozen=True, slots=True)
class DeclaredClaim:
    """A docs claim or planned entry with no runtime row, and its trigger."""

    id: str
    kind: InventoryKind
    reason: str
    trigger: str


# TODO91 S3/S2: the plan-of-record entries. Every name here is prose in
# docs/readme/stability-eval.md; a name absent from the runtime registry is a
# declared row, never silence. S3 replaces a row with a loader or a retirement;
# until then the trigger is what would build it.
DECLARED_CLAIMS: Final[tuple[DeclaredClaim, ...]] = (
    DeclaredClaim(
        id="task:vision:cifar100",
        kind=InventoryKind.TASK,
        reason="network_required: torchvision downloads CIFAR-100; no cached copy",
        trigger="cached offline loader with a checksum lock",
    ),
    DeclaredClaim(
        id="task:vision:svhn",
        kind=InventoryKind.TASK,
        reason="network_required: torchvision downloads SVHN; no cached copy",
        trigger="cached offline loader with a checksum lock",
    ),
    DeclaredClaim(
        id="task:language:wikitext2",
        kind=InventoryKind.TASK,
        reason="network_required: no in-repo corpus or checksum lock",
        trigger="cached offline loader with a checksum lock",
    ),
    DeclaredClaim(
        id="task:language:penn_treebank",
        kind=InventoryKind.TASK,
        reason="network_required: no in-repo corpus or checksum lock",
        trigger="cached offline loader with a checksum lock",
    ),
    DeclaredClaim(
        id="task:rl:mountain_car",
        kind=InventoryKind.TASK,
        reason="dependency_unavailable: Gymnasium classic-control extra not installed",
        trigger="declare the gymnasium dependency and a deterministic episode cap",
    ),
    DeclaredClaim(
        id="task:rl:lunar_lander",
        kind=InventoryKind.TASK,
        reason="dependency_unavailable: Box2D not installed",
        trigger="declare the Box2D dependency and a deterministic episode cap",
    ),
    DeclaredClaim(
        id="task:tabular:diabetes",
        kind=InventoryKind.TASK,
        reason="offline loader exists (sklearn.datasets.load_diabetes); row unregistered",
        trigger="register a TabularTask regression row (S3)",
    ),
    DeclaredClaim(
        id="task:tabular:california_housing",
        kind=InventoryKind.TASK,
        reason="network_required: sklearn.datasets.fetch_california_housing downloads",
        trigger="cached offline loader with a checksum lock",
    ),
    DeclaredClaim(
        id="task:timeseries:ett_h1",
        kind=InventoryKind.TASK,
        reason="data_unavailable: no in-repo ETT CSV or checksum lock",
        trigger="cache the dataset and pin its checksum",
    ),
    *(
        DeclaredClaim(
            id=f"task:scientific:{name}",
            kind=InventoryKind.TASK,
            reason="dependency_unavailable: ScientificTask ships ODE loaders only",
            trigger=f"implement the {name} integrator with a conservation smoke",
        )
        for name in ("heat", "wave", "burgers", "navier_stokes")
    ),
    DeclaredClaim(
        id="task:scientific:pendulum",
        kind=InventoryKind.TASK,
        reason=(
            "docs name `pendulum` for the ODE loader; that name is the RL task. "
            "The scientific loader is registered as `pendulum_state`"
        ),
        trigger="rewrite the docs entry to `pendulum_state` (S3 reconciliation)",
    ),
    DeclaredClaim(
        id="task:scientific:lorenz",
        kind=InventoryKind.TASK,
        reason="ScientificTask already generates Lorenz; no task row registered",
        trigger="register `lorenz_state` in SUPPORTED_TASKS (S3)",
    ),
    DeclaredClaim(
        id="architecture:PINO",
        kind=InventoryKind.ARCHITECTURE,
        reason="docs advertise Physics-Informed Neural Operator; no geometry or preset",
        trigger="minimum faithful geometry + preset + smoke, or retire the claim",
    ),
    DeclaredClaim(
        id="architecture:DeepONet",
        kind=InventoryKind.ARCHITECTURE,
        reason="docs advertise DeepONet; no geometry or preset",
        trigger="minimum faithful geometry + preset + smoke, or retire the claim",
    ),
    DeclaredClaim(
        id="architecture:FNO",
        kind=InventoryKind.ARCHITECTURE,
        reason="docs advertise Fourier Neural Operator; no geometry or preset",
        trigger="minimum faithful geometry + preset + smoke, or retire the claim",
    ),
    DeclaredClaim(
        id="architecture:LSTM",
        kind=InventoryKind.ARCHITECTURE,
        reason=(
            "docs advertise a standalone LSTM family; the only LSTM in the tree "
            "is NTM's controller"
        ),
        trigger="recurrent-preset LSTM with a smoke, or rewrite the docs claim",
    ),
    DeclaredClaim(
        id="domain:continual",
        kind=InventoryKind.DOMAIN,
        reason="declared DomainType with no loader; forgetting cannot be measured",
        trigger="one class-incremental split (S3), or a retirement row",
    ),
    DeclaredClaim(
        id="domain:multitask",
        kind=InventoryKind.DOMAIN,
        reason="declared DomainType with no loader; backward transfer cannot be measured",
        trigger="one task-sequence row with a declared order (S3), or a retirement row",
    ),
    DeclaredClaim(
        id="domain:lm",
        kind=InventoryKind.DOMAIN,
        reason="alias of `language`; no task carries the `lm` domain value",
        trigger="keep as an alias, or retire the value",
    ),
)


@dataclass(frozen=True, slots=True)
class InventoryReport:
    """The joined surface rows."""

    rows: tuple[InventoryRow, ...]

    def by_status(self, status: InventoryStatus) -> tuple[InventoryRow, ...]:
        return tuple(row for row in self.rows if row.status is status)

    def counts(self) -> dict[str, int]:
        return {status.value: len(self.by_status(status)) for status in InventoryStatus}

    def to_dict(self) -> dict[str, object]:
        return {
            "counts": self.counts(),
            "total": len(self.rows),
            "rows": [row.to_dict() for row in self.rows],
        }

    def render(self) -> str:
        counts = self.counts()
        lines = [
            "Surface inventory",
            "=================",
            (
                f"{len(self.rows)} rows: "
                f"{counts[InventoryStatus.IMPLEMENTED.value]} implemented, "
                f"{counts[InventoryStatus.DECLARED.value]} declared, "
                f"{counts[InventoryStatus.UNKNOWN.value]} unknown"
            ),
            "",
        ]
        for row in self.rows:
            detail = row.smoke_path or row.reason_or_trigger or ""
            lines.append(
                f"{row.status.value:11} {row.kind.value:12} {row.id:44} {detail}"
            )
        unknown = self.by_status(InventoryStatus.UNKNOWN)
        if unknown:
            lines.append("")
            lines.append("UNKNOWN rows (no smoke path, no declared reason):")
            lines.extend(f"  {row.id}" for row in unknown)
        return "\n".join(lines)


def _smoke_exists(smoke_path: str | None, root: Path) -> bool:
    if smoke_path is None:
        return False
    file_part = smoke_path.split("::", 1)[0]
    return (root / file_part).is_file()


def _row(
    *,
    row_id: str,
    kind: InventoryKind,
    runtime_name: str | None,
    smoke_path: str | None,
    root: Path,
    reason: str | None = None,
    axis: str | None = None,
) -> InventoryRow:
    """Classify one row by what exists, never by what is declared implemented."""
    if smoke_path is not None:
        exists = _smoke_exists(smoke_path, root)
        return InventoryRow(
            id=row_id,
            kind=kind,
            runtime_name=runtime_name,
            status=(InventoryStatus.IMPLEMENTED if exists else InventoryStatus.UNKNOWN),
            smoke_path=smoke_path if exists else None,
            reason_or_trigger=(
                reason
                if exists
                else f"smoke path {smoke_path!r} is missing and no replacement is declared"
            ),
            axis=axis,
        )
    if reason:
        return InventoryRow(
            id=row_id,
            kind=kind,
            runtime_name=runtime_name,
            status=InventoryStatus.DECLARED,
            smoke_path=None,
            reason_or_trigger=reason,
            axis=axis,
        )
    return InventoryRow(
        id=row_id,
        kind=kind,
        runtime_name=runtime_name,
        status=InventoryStatus.UNKNOWN,
        smoke_path=None,
        reason_or_trigger="no smoke path and no declared reason",
        axis=axis,
    )


def _algorithm_rows(root: Path) -> list[InventoryRow]:
    from computronium import algorithms

    ALL_ALGORITHMS = algorithms.ALL_ALGORITHMS
    INTERNAL_ALGORITHMS = algorithms.INTERNAL_ALGORITHMS
    PUBLIC_ALGORITHMS = algorithms.PUBLIC_ALGORITHMS
    package_dir = Path(algorithms.__file__).parent
    packages = sorted(
        path.name
        for path in package_dir.iterdir()
        if path.is_dir() and not path.name.startswith(("_", "__"))
    )
    rows = []
    for name in packages:
        smoke = f"{GENERATED_TESTS}/test_algorithm_{name}_invariants.py"
        if name in PUBLIC_ALGORITHMS:
            reason = "public: selectable through computronium.algorithms"
        elif name in INTERNAL_ALGORITHMS:
            reason = f"internal: reached by {INTERNAL_ALGORITHMS[name]}"
        else:
            reason = None
        rows.append(
            _row(
                row_id=f"algorithm.{name}",
                kind=InventoryKind.ALGORITHM,
                runtime_name=name,
                smoke_path=smoke if name in ALL_ALGORITHMS else None,
                root=root,
                reason=reason,
            )
        )
    return rows


def _primitive_rows(root: Path) -> list[InventoryRow]:
    from computronium.acceleration.registry import all_specs
    from computronium.experiment.schema.axis import AXES_REGISTRIES
    from computronium.experiment.schema.spec_aliases import (
        NOT_A_PRIMITIVE,
        SPEC_AXIS,
        runtime_name_for,
    )

    rows: list[InventoryRow] = []
    targeted: dict[str, set[str]] = {axis.value: set() for axis in StructuralAxis}
    for spec in sorted(all_specs(), key=lambda item: item.id):
        if spec.kind != "primitive" or spec.axis is None:
            continue
        axis_value = SPEC_AXIS[spec.axis].value
        runtime = runtime_name_for(spec)
        generated = (
            f"{GENERATED_TESTS}/test_primitive_"
            f"{spec.id.removeprefix('primitive.').replace('.', '_')}_invariants.py"
        )
        if runtime is None:
            reason = NOT_A_PRIMITIVE.get(spec.id)
            rows.append(
                _row(
                    row_id=spec.id,
                    kind=InventoryKind.PRIMITIVE,
                    runtime_name=None,
                    smoke_path=None,
                    root=root,
                    reason=reason,
                    axis=axis_value,
                )
            )
            continue
        targeted[axis_value].add(runtime)
        rows.append(
            _row(
                row_id=spec.id,
                kind=InventoryKind.PRIMITIVE,
                runtime_name=runtime,
                smoke_path=(
                    generated if _smoke_exists(generated, root) else COMPLETENESS_LOCK
                ),
                root=root,
                axis=axis_value,
            )
        )

    for axis, registry in AXES_REGISTRIES.items():
        for runtime in sorted(registry.keys()):
            if runtime in targeted[axis]:
                continue
            rows.append(
                _row(
                    row_id=f"primitive.{axis}.{runtime}",
                    kind=InventoryKind.PRIMITIVE,
                    runtime_name=runtime,
                    smoke_path=COMPLETENESS_LOCK,
                    root=root,
                    reason=(
                        "runtime-only coordinate; no implementation spec row "
                        "names it (completeness lock pins its config mapping)"
                    ),
                    axis=axis,
                )
            )
    return rows


def _task_rows(root: Path) -> list[InventoryRow]:
    from computronium.domains.registry import SUPPORTED_TASKS
    from computronium.experiment.registry.task_registry import TaskRegistry

    domains = {task.name: task.domain.value for task in TaskRegistry()}
    rows = [
        _row(
            row_id=f"task:{name}",
            kind=InventoryKind.TASK,
            runtime_name=name,
            smoke_path=TASK_SMOKE,
            root=root,
            reason=f"domain {domains.get(name, 'unknown')}",
        )
        for name in sorted(SUPPORTED_TASKS)
    ]
    rows.extend(
        _row(
            row_id=claim.id,
            kind=claim.kind,
            runtime_name=None,
            smoke_path=None,
            root=root,
            reason=f"{claim.reason} — trigger: {claim.trigger}",
        )
        for claim in DECLARED_CLAIMS
        if claim.kind is InventoryKind.TASK
    )
    return rows


def _domain_rows(root: Path) -> list[InventoryRow]:
    from computronium.domains.base import DomainType
    from computronium.experiment.registry.task_registry import TaskRegistry

    registry = TaskRegistry()
    populated = set(registry.all_domains())
    claimed = {
        claim.id.split(":", 1)[1]: claim
        for claim in DECLARED_CLAIMS
        if claim.kind is InventoryKind.DOMAIN
    }
    rows = []
    for domain in DomainType:
        if domain in {DomainType.CUSTOM, DomainType.UNKNOWN}:
            continue
        if domain in populated:
            rows.append(
                _row(
                    row_id=f"domain:{domain.value}",
                    kind=InventoryKind.DOMAIN,
                    runtime_name=domain.value,
                    smoke_path=TASK_SMOKE,
                    root=root,
                    reason=f"{len(registry.by_domain(domain))} tasks",
                )
            )
        elif domain.value in claimed:
            claim = claimed[domain.value]
            rows.append(
                _row(
                    row_id=claim.id,
                    kind=claim.kind,
                    runtime_name=None,
                    smoke_path=None,
                    root=root,
                    reason=f"{claim.reason} — trigger: {claim.trigger}",
                )
            )
        else:
            rows.append(
                _row(
                    row_id=f"domain:{domain.value}",
                    kind=InventoryKind.DOMAIN,
                    runtime_name=domain.value,
                    smoke_path=None,
                    root=root,
                )
            )
    return rows


def _objective_rows(root: Path) -> list[InventoryRow]:
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    rows = []
    for spec in OBJECTIVES_REGISTRY:
        measured = spec.metric_key is not None
        rows.append(
            _row(
                row_id=f"objective:{spec.name}",
                kind=InventoryKind.OBJECTIVE,
                runtime_name=spec.metric_key,
                smoke_path=OBJECTIVE_SMOKE if measured else None,
                root=root,
                reason=None if measured else spec.unavailable_reason,
            )
        )
    return rows


def _capability_rows(root: Path) -> list[InventoryRow]:
    from computronium.experiment.schema.registries import (
        CAPABILITIES_REGISTRY,
        CapabilityStatus,
    )

    rows = []
    for spec in CAPABILITIES_REGISTRY:
        active = spec.status is CapabilityStatus.ACTIVE
        reason = None if active else (spec.unverified_reason or spec.retirement_record)
        rows.append(
            _row(
                row_id=f"capability:{spec.capability_id}",
                kind=InventoryKind.CAPABILITY,
                runtime_name=spec.display_name,
                smoke_path=spec.verifying_test if active else None,
                root=root,
                reason=reason,
            )
        )
    return rows


def _architecture_rows(root: Path) -> list[InventoryRow]:
    return [
        _row(
            row_id=claim.id,
            kind=claim.kind,
            runtime_name=None,
            smoke_path=None,
            root=root,
            reason=f"{claim.reason} — trigger: {claim.trigger}",
        )
        for claim in DECLARED_CLAIMS
        if claim.kind is InventoryKind.ARCHITECTURE
    ]


def build_inventory(*, root: Path | None = None) -> InventoryReport:
    """Join every declared surface into one classified table.

    Args:
        root: Repository root used to resolve smoke paths. Passing an empty
            directory makes every path-backed row classified by what is left.

    Returns:
        The report. ``unknown`` rows are defects: an entry neither runs nor
        records why it cannot.
    """
    from computronium.experiment.schema import seed_all_registries

    seed_all_registries()
    base = REPO_ROOT if root is None else Path(root)
    rows: list[InventoryRow] = []
    for builder in (
        _algorithm_rows,
        _primitive_rows,
        _task_rows,
        _domain_rows,
        _objective_rows,
        _capability_rows,
        _architecture_rows,
    ):
        rows.extend(builder(base))
    return InventoryReport(rows=tuple(rows))


def render_json(report: InventoryReport) -> str:
    """Serialize a report for the CLI's ``--format json``."""
    return json.dumps(report.to_dict(), indent=2)
