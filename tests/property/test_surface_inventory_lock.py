"""Lock: the surface inventory is a join, not a list (TODO91 S0/S1).

The defect this guards is the one TODO91 opened with: every registry was
individually green while nothing proved the spec vocabulary, the runtime
coordinates, the algorithm packages, the tasks, and the docs claims described
one surface. These tests fail when a row loses its smoke path, when a package
is in neither algorithm table, when a spec ID resolves to nothing, when a
runtime coordinate is unaccounted for, and when the docs name a task the
inventory does not know.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from computronium.acceleration.registry import all_specs
from computronium.algorithms import (
    ALL_ALGORITHMS,
    INTERNAL_ALGORITHMS,
    PUBLIC_ALGORITHMS,
)
from computronium.domains.base import DomainType
from computronium.domains.registry import SUPPORTED_TASKS
from computronium.experiment.registry.task_registry import TaskRegistry
from computronium.experiment.schema import seed_all_registries
from computronium.experiment.schema.axis import AXES_REGISTRIES
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    OBJECTIVES_REGISTRY,
)
from computronium.experiment.schema.spec_aliases import (
    NOT_A_PRIMITIVE,
    SPEC_AXIS,
    runtime_name_for,
)
from computronium.experiment.surface.inventory import (
    DECLARED_CLAIMS,
    InventoryKind,
    InventoryStatus,
    build_inventory,
)

pytestmark = pytest.mark.timeout(120)

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module", autouse=True)
def _seeded() -> None:
    seed_all_registries()


@pytest.fixture(scope="module")
def report():
    return build_inventory()


def _ids(report, kind: InventoryKind) -> set[str]:
    return {row.id for row in report.rows if row.kind is kind}


def test_inventory_has_no_unknown_rows(report) -> None:
    unknown = report.by_status(InventoryStatus.UNKNOWN)
    assert not unknown, [row.id for row in unknown]


def test_every_algorithm_package_is_declared_public_or_internal(report) -> None:
    package_dir = REPO / "computronium" / "algorithms"
    packages = {
        path.name
        for path in package_dir.iterdir()
        if path.is_dir() and not path.name.startswith("__")
    }
    assert packages <= set(ALL_ALGORITHMS)
    assert set(ALL_ALGORITHMS) == set(PUBLIC_ALGORITHMS) | set(INTERNAL_ALGORITHMS)
    assert not set(PUBLIC_ALGORITHMS) & set(INTERNAL_ALGORITHMS)
    algorithm_rows = _ids(report, InventoryKind.ALGORITHM)
    assert {f"algorithm.{name}" for name in packages} == algorithm_rows
    for row in report.rows:
        if row.kind is InventoryKind.ALGORITHM:
            assert row.status is InventoryStatus.IMPLEMENTED, row.id
            assert row.smoke_path, row.id


def test_every_spec_id_resolves_or_is_not_a_primitive(report) -> None:
    rows = _ids(report, InventoryKind.PRIMITIVE)
    for spec in all_specs():
        if spec.kind != "primitive":
            continue
        assert spec.id in rows, spec.id
        runtime = runtime_name_for(spec)
        if runtime is None:
            assert spec.id in NOT_A_PRIMITIVE, spec.id
            row = next(row for row in report.rows if row.id == spec.id)
            assert row.status is InventoryStatus.DECLARED, spec.id
        else:
            assert spec.axis is not None
            assert runtime in AXES_REGISTRIES[SPEC_AXIS[spec.axis]], spec.id


def test_every_runtime_axis_coordinate_has_a_row(report) -> None:
    runtimes = {
        (row.axis, row.runtime_name)
        for row in report.rows
        if row.kind is InventoryKind.PRIMITIVE and row.runtime_name
    }
    missing = {
        (axis, name)
        for axis, registry in AXES_REGISTRIES.items()
        for name in (spec.name for spec in registry)
        if (axis, name) not in runtimes
    }
    assert not missing, sorted(missing)


def test_every_task_domain_objective_and_capability_has_a_row(report) -> None:
    task_rows = _ids(report, InventoryKind.TASK)
    assert {f"task:{name}" for name in SUPPORTED_TASKS} <= task_rows

    registry = TaskRegistry()
    for domain in registry.all_domains():
        assert f"domain:{domain.value}" in _ids(report, InventoryKind.DOMAIN), domain

    assert {f"objective:{spec.name}" for spec in OBJECTIVES_REGISTRY} == _ids(
        report, InventoryKind.OBJECTIVE
    )
    assert {f"capability:{spec.capability_id}" for spec in CAPABILITIES_REGISTRY} == (
        _ids(report, InventoryKind.CAPABILITY)
    )


def test_declared_claims_cover_every_empty_domain(report) -> None:
    populated = TaskRegistry().all_domains()
    claimed = {
        claim.id.split(":", 1)[1]
        for claim in DECLARED_CLAIMS
        if claim.kind is InventoryKind.DOMAIN
    }
    empty = {
        domain.value
        for domain in DomainType
        if domain not in {DomainType.CUSTOM, DomainType.UNKNOWN}
        and domain not in populated
    }
    assert empty <= claimed, empty


def test_missing_smoke_path_makes_a_row_unknown(tmp_path: Path) -> None:
    empty = build_inventory(root=tmp_path)
    backprop = next(row for row in empty.rows if row.id == "algorithm.backprop")
    assert backprop.status is InventoryStatus.UNKNOWN
    assert backprop.smoke_path is None
    assert empty.by_status(InventoryStatus.UNKNOWN)


def test_unknown_spec_runtime_fails_the_join(monkeypatch, tmp_path: Path) -> None:
    fake = SimpleNamespace(
        id="primitive.geometry.does_not_exist",
        kind="primitive",
        axis="geometry",
    )
    monkeypatch.setattr("computronium.acceleration.registry.all_specs", lambda: (fake,))
    report = build_inventory(root=REPO)
    row = next(
        row for row in report.rows if row.id == "primitive.geometry.does_not_exist"
    )
    assert row.status is InventoryStatus.UNKNOWN


def _docs_task_names() -> set[str]:
    text = (REPO / "docs" / "readme" / "stability-eval.md").read_text(encoding="utf-8")
    names: set[str] = set()
    for line in text.splitlines():
        if not line.startswith("**Tasks**"):
            continue
        names.update(re.findall(r"`([^`]+)`", line))
    return names


def test_docs_task_names_resolve_to_a_row(report) -> None:
    known = {
        row.id.removeprefix("task:").rsplit(":", 1)[-1]
        for row in report.rows
        if row.kind is InventoryKind.TASK
    }
    assert _docs_task_names() <= known, _docs_task_names() - known


def test_spec_matrix_ids_are_inventory_rows(report) -> None:
    matrix = (REPO / "docs" / "generated" / "IMPLEMENTATION_MATRIX.md").read_text(
        encoding="utf-8"
    )
    matrix_ids = {
        line.split("|")[1].strip()
        for line in matrix.splitlines()
        if line.startswith("| ") and "---" not in line and not line.startswith("| ID ")
    }
    known = {row.id for row in report.rows}
    assert matrix_ids <= known, sorted(matrix_ids - known)
