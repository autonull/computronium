#!/usr/bin/env python
"""Defect-to-Fix Traceability Tracker (TODO99 #7).

Scans the codebase for @pytest.mark.fixes("GAP-XXX") and @pytest.mark.verifies("GAP-XXX")
markers, and generates a traceability report.

Usage:
    uv run python scripts/defect_tracker.py --scan
    uv run python scripts/defect_tracker.py --report
    uv run python scripts/defect_tracker.py --check-gaps
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True, slots=True)
class DefectMarker:
    """A @pytest.mark.fixes or @pytest.mark.verifies marker found in code."""
    gap_id: str
    marker_type: str  # "fixes" or "verifies"
    file_path: str
    line_number: int
    test_name: str
    commit_hash: str | None = None


@dataclass(frozen=True, slots=True)
class DefectInfo:
    """Aggregated information about a GAP defect."""
    gap_id: str
    fixes: list[DefectMarker]
    verifies: list[DefectMarker]
    status: str  # "open", "fixed", "verified", "regression"

    @property
    def is_fixed(self) -> bool:
        return len(self.fixes) > 0

    @property
    def is_verified(self) -> bool:
        return len(self.verifies) > 0

    @property
    def has_regression(self) -> bool:
        return self.status == "regression"


def _extract_gap_id_from_call(call: ast.Call) -> str | None:
    """Extract GAP-XXX string from a pytest.mark.fixes/verifies call."""
    if call.args:
        arg = call.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
    return None


def _is_pytest_mark_fixes_or_verifies(node: ast.Call) -> tuple[str, str] | None:
    """Check if a Call node is @pytest.mark.fixes("GAP-XXX") or @pytest.mark.verifies("GAP-XXX")."""
    # Check for @pytest.mark.fixes("...") or @pytest.mark.verifies("...")
    if (
        isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Attribute)
        and isinstance(node.func.value.value, ast.Name)
        and node.func.value.value.id == "pytest"
        and node.func.value.attr == "mark"
        and node.func.attr in ("fixes", "verifies")
    ):
        gap_id = _extract_gap_id_from_call(node)
        if gap_id:
            return node.func.attr, gap_id
    return None


def find_pytest_markers(root: Path) -> Iterator[DefectMarker]:
    """Scan Python files for @pytest.mark.fixes and @pytest.mark.verifies markers using AST."""
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        try:
            tree = ast.parse(content, filename=str(py_file))
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                test_name = node.name
                # Check decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        result = _is_pytest_mark_fixes_or_verifies(decorator)
                        if result:
                            marker_type, gap_id = result
                            yield DefectMarker(
                                gap_id=gap_id,
                                marker_type=marker_type,
                                file_path=str(py_file.relative_to(root)),
                                line_number=decorator.lineno,
                                test_name=test_name,
                            )


def scan_codebase(root: Path) -> dict[str, DefectInfo]:
    """Scan the entire codebase and aggregate by GAP ID."""
    markers = list(find_pytest_markers(root))

    by_gap: dict[str, list[DefectMarker]] = {}
    for marker in markers:
        if marker.gap_id not in by_gap:
            by_gap[marker.gap_id] = []
        by_gap[marker.gap_id].append(marker)

    result: dict[str, DefectInfo] = {}
    for gap_id, markers_list in by_gap.items():
        fixes = [m for m in markers_list if m.marker_type == "fixes"]
        verifies = [m for m in markers_list if m.marker_type == "verifies"]

        if verifies:
            status = "verified"
        elif fixes:
            status = "fixed"
        else:
            status = "open"

        result[gap_id] = DefectInfo(
            gap_id=gap_id,
            fixes=fixes,
            verifies=verifies,
            status=status,
        )

    return result


def generate_report(defects: dict[str, DefectInfo], output: Path | None = None) -> str:
    """Generate a markdown traceability report."""
    lines = [
        "# Defect-to-Fix Traceability Report",
        f"\nGenerated: {__import__('datetime').datetime.now().isoformat()}",
        f"Total GAPs tracked: {len(defects)}",
        "",
        "## Summary",
        "",
        "| GAP ID | Status | Fixes | Verifies |",
        "|--------|--------|-------|----------|",
    ]

    for gap_id in sorted(defects.keys()):
        info = defects[gap_id]
        lines.append(
            f"| {gap_id} | {info.status} | {len(info.fixes)} | {len(info.verifies)} |"
        )

    lines.extend(["", "## Details", ""])

    for gap_id in sorted(defects.keys()):
        info = defects[gap_id]
        lines.append(f"### {gap_id} ({info.status})")
        lines.append("")

        if info.fixes:
            lines.append("**Fixes:**")
            for fix in info.fixes:
                lines.append(
                    f"- `{fix.file_path}:{fix.line_number}` - `{fix.test_name}`"
                )
            lines.append("")

        if info.verifies:
            lines.append("**Verifies:**")
            for verify in info.verifies:
                lines.append(
                    f"- `{verify.file_path}:{verify.line_number}` - `{verify.test_name}`"
                )
            lines.append("")

        if not info.fixes and not info.verifies:
            lines.append("*No markers found (orphaned GAP)*")
            lines.append("")

    report = "\n".join(lines)

    if output:
        output.write_text(report, encoding="utf-8")
        print(f"Report written to {output}")

    return report


def check_gaps(defects: dict[str, DefectInfo]) -> int:
    """Check for GAPs that are fixed but not verified, or open."""
    issues = 0
    for gap_id, info in defects.items():
        if info.status == "fixed" and not info.verifies:
            print(f"WARNING: {gap_id} has fixes but no verifying test")
            issues += 1
        elif info.status == "open":
            print(f"INFO: {gap_id} is open (no fixes or verifies)")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan codebase for markers and print JSON",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate markdown traceability report",
    )
    parser.add_argument(
        "--check-gaps",
        action="store_true",
        help="Check for GAPs with fixes but no verifies",
    )
    parser.add_argument(
        "--output", "-o", type=Path, help="Output file for report"
    )
    parser.add_argument(
        "--root", type=Path, default=Path("."), help="Root directory to scan"
    )
    args = parser.parse_args(argv)

    defects = scan_codebase(args.root)

    if args.scan:
        # Output as JSON for programmatic use
        json_output = {
            gap_id: {
                "gap_id": info.gap_id,
                "status": info.status,
                "fixes": [asdict(f) for f in info.fixes],
                "verifies": [asdict(v) for v in info.verifies],
            }
            for gap_id, info in defects.items()
        }
        print(json.dumps(json_output, indent=2))

    if args.report:
        generate_report(defects, args.output)

    if args.check_gaps:
        return check_gaps(defects)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())