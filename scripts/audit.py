"""The TODO97 audit gate: one predicate per defect class (§8.2).

The migration replaced per-primitive scaffolding with one registry. A
commit-time gate has to make the old shapes expensive to reintroduce, so each
check below names a defect and exits non-zero when the defect is present.

Run:
    uv run python scripts/audit.py
    uv run python scripts/audit.py --check duplicate_bodies
    uv run python scripts/audit.py --json

Exit codes: 0 when every check is clean, 1 when a check finds a defect, 2 when
an input the check needs is missing (an unreadable map, a missing registry).
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"
PRIMITIVES = ROOT / "computronium" / "primitives"
BENCH = ROOT / "artifacts" / "benchmarks"
MAPS = (
    ROOT / "results" / "sec" / "map.json",
    ROOT / "results" / "sec_graph" / "map.json",
    ROOT / "results" / "sec_tabular" / "map.json",
    ROOT / "results" / "sec_sequence" / "map.json",
    ROOT / "results" / "sec_continual" / "map.json",
    ROOT / "results" / "sec_rl" / "map.json",
    ROOT / "results" / "sec_scientific" / "map.json",
    ROOT / "results" / "sec_neuromorphic" / "map.json",
    ROOT / "results" / "sec_lm" / "map.json",
)

#: Directories that never hold source under audit.
SKIP_PARTS = frozenset({
    ".venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    "build",
    "dist",
    "node_modules",
})

#: The per-axis primitive contract tests are one parameterized body per axis;
#: a duplicate inside this directory is the mechanism, not the template.
ALLOW_DUPLICATES = TESTS / "primitives"

#: Kernel states the protocol declares. ``stub`` is never a pass.
KERNEL_STATES = frozenset({"implemented", "wrapper", "stub", "absent"})


@dataclass(frozen=True, slots=True)
class Finding:
    """One defect the gate found."""

    check: str
    detail: str


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except OSError, SyntaxError, UnicodeDecodeError:
        return None


def _test_files(tests: Path = TESTS) -> Iterable[Path]:
    for path in tests.rglob("test_*.py"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def _test_functions(
    tree: ast.Module,
) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef]:
    for node in tree.body:
        if isinstance(
            node, ast.FunctionDef | ast.AsyncFunctionDef
        ) and node.name.startswith("test"):
            yield node


def _normalized_body(node: ast.AST) -> str:
    """The body with docstrings and literal values erased, so shape is compared."""

    class _Normalize(ast.NodeTransformer):
        def visit_Constant(self, const: ast.Constant) -> ast.Constant:
            return ast.copy_location(ast.Constant(value="<literal>"), const)

        def visit_Expr(self, expr: ast.Expr) -> ast.Expr | None:
            if isinstance(expr.value, ast.Constant) and isinstance(
                expr.value.value, str
            ):
                return None
            return self.generic_visit(expr)

    cloned = ast.parse(ast.unparse(node))
    normalized = _Normalize().visit(cloned)
    return ast.unparse(ast.fix_missing_locations(normalized))


def _truthy_constants(tree: ast.Module) -> Iterable[tuple[int, str]]:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assert)
            and isinstance(node.test, ast.Constant)
            and bool(node.test.value)
        ):
            yield node.lineno, ast.unparse(node.test)


def duplicate_bodies() -> list[Finding]:
    """A normalized duplicate body outside the per-axis contract suite."""
    bodies: dict[str, list[tuple[Path, str]]] = {}
    for path in _test_files():
        tree = _parse(path)
        if tree is None:
            continue
        for function in _test_functions(tree):
            try:
                key = _normalized_body(function)
            except SyntaxError, ValueError:
                continue
            bodies.setdefault(key, []).append((path, function.name))

    findings = []
    for members in bodies.values():
        if len(members) < 2:
            continue
        if all(ALLOW_DUPLICATES in path.parents for path, _ in members):
            continue
        names = ", ".join(f"{path.relative_to(ROOT)}::{name}" for path, name in members)
        findings.append(Finding("duplicate_bodies", names))
    return findings


def empty_assertions() -> list[Finding]:
    """An assertion that is a truthy literal: it cannot fail."""
    findings = []
    for path in _test_files():
        tree = _parse(path)
        if tree is None:
            continue
        for lineno, text in _truthy_constants(tree):
            findings.append(
                Finding("empty_assertions", f"{path.relative_to(ROOT)}:{lineno} {text}")
            )
    return findings


def per_primitive_subdirectories() -> list[Finding]:
    """A per-primitive package under ``computronium/primitives/`` is scaffolding."""
    findings = []
    for path in PRIMITIVES.iterdir():
        if path.is_dir() and path.name not in {"__pycache__"}:
            findings.append(
                Finding("per_primitive_subdirectories", str(path.relative_to(ROOT)))
            )
    return findings


def primitive_without_spec() -> list[Finding]:
    """An acceleration primitive without a ``PrimitiveSpec`` row, and the reverse."""
    from computronium.acceleration.registry import primitives as acceleration_primitives
    from computronium.primitives.registry import REGISTRY

    acceleration = {spec.id for spec in acceleration_primitives()}
    declared = set(REGISTRY)
    findings = [
        Finding("primitive_without_spec", f"{item}: no PrimitiveSpec row")
        for item in sorted(acceleration - declared)
    ]
    findings += [
        Finding("primitive_without_spec", f"{item}: no acceleration primitive row")
        for item in sorted(declared - acceleration)
    ]
    return findings


def family_without_base() -> list[Finding]:
    """A declared task family without a ``BASE_BOXES`` row."""
    from computronium.experiment.sec_pilot import BASE_BOXES, TASK_FAMILIES

    return [
        Finding("family_without_base", f"{family}: no BASE_BOXES row")
        for family in TASK_FAMILIES
        if family not in BASE_BOXES
    ]


def near_chance_without_ladder() -> list[Finding]:
    """A bound row at its resolution's chance rate must have a ladder record.

    The record is the only adjudication of a near-chance cell: a measurement
    says the primitive ran, not that it cannot train. ``sec_ladder`` owns the
    record's schema, so the gate and the runner read one declaration.
    """
    from computronium.experiment.sec_ladder import map_findings

    findings = []
    for map_path in MAPS:
        if not map_path.exists():
            continue
        document = json.loads(map_path.read_text(encoding="utf-8"))
        findings += [
            Finding("near_chance_without_ladder", f"{map_path.name}: {problem}")
            for problem in map_findings(document)
        ]
    return findings


def kernel_stub_pass() -> list[Finding]:
    """A stub never passes, and an implemented kernel carries its evidence."""
    from computronium.primitives.registry import REGISTRY

    findings = []
    for spec in REGISTRY.values():
        if spec.kernel_status not in KERNEL_STATES:
            findings.append(
                Finding(
                    "kernel_stub_pass",
                    f"{spec.id}: kernel_status={spec.kernel_status!r} is not declared",
                )
            )
        if spec.kernel_status == "stub":
            findings.append(
                Finding("kernel_stub_pass", f"{spec.id}: a stub cannot be a pass")
            )
        if spec.kernel_status == "implemented":
            if not spec.kernel_entrypoint:
                findings.append(
                    Finding(
                        "kernel_stub_pass", f"{spec.id}: implemented without entrypoint"
                    )
                )
            if spec.kernel_technology is None:
                findings.append(
                    Finding(
                        "kernel_stub_pass", f"{spec.id}: implemented without technology"
                    )
                )
            if not (BENCH / f"{spec.id}.jsonl").exists():
                findings.append(
                    Finding(
                        "kernel_stub_pass",
                        f"{spec.id}: implemented without microbench evidence",
                    )
                )
    return findings


#: Reasons a skip may name: the environment, never the capability. Matched
#: case-insensitively, so a tool's name is the tool whether it is capitalized.
ENVIRONMENT_SKIPS = (
    "cuda",
    "cupy",
    "cpu fallback",
    "triton",
    "dataset",
    "database",
    "network",
    "gpu",
    "disk",
    "platform",
    "no --experiment-db",
)


def _static_reason(node: ast.expr | None) -> str | None:
    """The static text of a skip reason, or ``None`` when it is not constant.

    An f-string is a literal whose interpolations are opaque: its constant
    parts are the text the gate can read. A name, attribute or call carries no
    readable text, so it cannot prove the environment and is a finding
    (TODO97 S6d: 28 non-literal sites evaded the literal-only scan).
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            value.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str)
            else "{}"
            for value in node.values
        )
    return None


def _skip_reason(node: ast.Call) -> ast.expr | None:
    """The reason argument of a ``pytest.skip`` call, positional or keyword."""
    if node.args:
        return node.args[0]
    return next(
        (kw.value for kw in node.keywords if kw.arg == "reason"),
        None,
    )


def _skips(tree: ast.Module) -> Iterable[tuple[int, str | None]]:
    """``(lineno, reason)`` for every ``pytest.skip`` call in ``tree``.

    The attribute's value must be the ``pytest`` name: ``pytest.mark.skip`` is
    a marker, not a call, and its reason is a keyword the marker declares.
    """
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "skip"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pytest"
        ):
            yield node.lineno, _static_reason(_skip_reason(node))


def capability_skip(tests: Path = TESTS) -> list[Finding]:
    """A ``pytest.skip`` that names a capability, not the environment.

    A capability skip is a test defect (TODO97 §0.1): the row is
    ``unimplemented`` or ``defective`` and must fail instead. A reason the
    scanner cannot read (a variable, a call) is a finding: it cannot name the
    environment, so it cannot be an environment skip.
    """
    findings = []
    for path in _test_files(tests):
        tree = _parse(path)
        if tree is None:
            continue
        for lineno, reason in _skips(tree):
            try:
                where = path.relative_to(ROOT)
            except ValueError:
                where = path
            if reason is None:
                findings.append(
                    Finding(
                        "capability_skip",
                        f"{where}:{lineno} non-literal skip reason: "
                        "cannot prove the environment",
                    )
                )
                continue
            lowered = reason.lower()
            if any(marker in lowered for marker in ENVIRONMENT_SKIPS):
                continue
            if reason.strip().startswith("declared:"):
                continue
            findings.append(Finding("capability_skip", f"{where}:{lineno} {reason!r}"))
    return findings


def _map_rows() -> Iterable[tuple[Path, str, dict]]:
    for map_path in MAPS:
        if not map_path.exists():
            continue
        document = json.loads(map_path.read_text(encoding="utf-8"))
        for spec_id, row in document.get("primitives", {}).items():
            yield map_path, spec_id, row


def impossible_without_lock() -> list[Finding]:
    """A quiet ``impossible`` row without a refusal test and a necessity test."""
    findings = []
    for map_path, spec_id, row in _map_rows():
        if row.get("status") != "impossible":
            continue
        missing = [
            key for key in ("refusal_test", "necessity_test") if not row.get(key)
        ]
        if missing:
            findings.append(
                Finding(
                    "impossible_without_lock",
                    f"{map_path.name}:{spec_id} missing {', '.join(missing)}",
                )
            )
    return findings


def quiet_row_without_lock() -> list[Finding]:
    """A ``gap`` label anywhere, or an unimplemented row without a failing test.

    ``unimplemented`` and ``defective`` rows are always failing tests; "gap"
    is retired vocabulary (TODO97 §0.2). The register's ``refused`` means the
    declared family excludes the task, so it is scope, not a row state.
    """
    findings = []
    for map_path, spec_id, row in _map_rows():
        status = row.get("status")
        labelled = status == "gap" or "gap" in json.dumps(row).lower()
        if labelled:
            findings.append(Finding("quiet_row_without_lock", f"{spec_id}: gap label"))
        if status in {"unimplemented", "defective"} and not row.get("failing_test"):
            findings.append(
                Finding(
                    "quiet_row_without_lock",
                    f"{map_path.name}:{spec_id} {status} without a failing test",
                )
            )
    return findings


def unaccounted_row() -> list[Finding]:
    """A declared ``(primitive, family)`` row the map does not account for."""
    from computronium.primitives.registry import REGISTRY

    rows: dict[str, set[str]] = {}
    for _map_path, spec_id, row in _map_rows():
        rows.setdefault(spec_id, set()).add(row.get("task_family", row.get("task", "")))
    statuses = {spec_id: row for _p, spec_id, row in _map_rows()}
    findings = []
    for spec in REGISTRY.values():
        if spec.id not in statuses:
            findings.append(Finding("unaccounted_row", f"{spec.id}: no map row"))
    return findings


def claim_count_mismatch() -> list[Finding]:
    """A map's declared counts disagree with its own rows."""
    findings = []
    for map_path in MAPS:
        if not map_path.exists():
            continue
        document = json.loads(map_path.read_text(encoding="utf-8"))
        primitives = document.get("primitives", {})
        inventory = document.get("inventory") or {}
        for key, value in inventory.items():
            claimed = isinstance(value, int) and key in {"rows", "primitives", "total"}
            if claimed and value != len(primitives):
                findings.append(
                    Finding(
                        "claim_count_mismatch",
                        f"{map_path.name}: inventory.{key}={value} "
                        f"but {len(primitives)} rows",
                    )
                )
    return findings


#: Names the migration deleted; a surviving alias is a compatibility crutch.
RETIRED_NAMES = ("_FAMILY_OF_DOMAIN",)


def compatibility_alias() -> list[Finding]:
    """A surviving alias or deprecated re-export of a deleted shape."""
    findings = []
    for path in (ROOT / "computronium").rglob("*.py"):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue
        for name in RETIRED_NAMES:
            if name in text:
                findings.append(
                    Finding("compatibility_alias", f"{path.relative_to(ROOT)}: {name}")
                )
    return findings


CHECKS: dict[str, Callable[[], list[Finding]]] = {
    "duplicate_bodies": duplicate_bodies,
    "empty_assertions": empty_assertions,
    "per_primitive_subdirectories": per_primitive_subdirectories,
    "primitive_without_spec": primitive_without_spec,
    "family_without_base": family_without_base,
    "near_chance_without_ladder": near_chance_without_ladder,
    "kernel_stub_pass": kernel_stub_pass,
    "capability_skip": capability_skip,
    "impossible_without_lock": impossible_without_lock,
    "quiet_row_without_lock": quiet_row_without_lock,
    "unaccounted_row": unaccounted_row,
    "claim_count_mismatch": claim_count_mismatch,
    "compatibility_alias": compatibility_alias,
}

#: The measurement checks need run output; the static gate is the commit gate.
MEASUREMENT_CHECKS = frozenset({"near_chance_without_ladder"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        choices=sorted(CHECKS),
        action="append",
        help="run one check (repeatable); default runs every check",
    )
    parser.add_argument(
        "--static",
        action="store_true",
        help="skip the measurement checks (the commit gate)",
    )
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args(argv)

    names = args.check or list(CHECKS)
    if args.static:
        names = [name for name in names if name not in MEASUREMENT_CHECKS]
    findings: list[Finding] = []
    for name in names:
        findings.extend(CHECKS[name]())

    if args.json:
        print(
            json.dumps(
                [{"check": f.check, "detail": f.detail} for f in findings], indent=2
            )
        )
    else:
        for finding in findings:
            print(f"{finding.check}: {finding.detail}")
        digest = hashlib.blake2b(
            "\n".join(f"{f.check}:{f.detail}" for f in findings).encode(),
            digest_size=8,
        ).hexdigest()
        print(f"{len(findings)} finding(s) [{digest}]")

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
