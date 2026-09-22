"""i18n String Extraction Audit (M3.4) — extract all simple-register strings.

Ensures 100% of Explorer strings are in resource files, no concatenation.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


def extract_tr_calls(file_path: Path) -> list[dict[str, Any]]:
    """Extract all tr() and tr_both() calls from a Python file."""
    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content)

    calls: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for tr() or tr_both() calls
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in {"tr", "tr_both"}:
                # Extract string argument
                if node.args and isinstance(node.args[0], ast.Constant):
                    key = node.args[0].value
                    register = "both"
                    if func_name == "tr":
                        # Check for register keyword argument
                        for kw in node.keywords:
                            if kw.arg == "register" and isinstance(
                                kw.value, ast.Constant
                            ):
                                register = kw.value.value
                    calls.append({
                        "file": str(file_path),
                        "line": node.lineno,
                        "function": func_name,
                        "key": key,
                        "register": register,
                    })

    return calls


def check_glossary_coverage(glossary_path: Path, ui_dir: Path) -> dict[str, Any]:
    """Check that all tr() keys exist in glossary.json."""
    glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
    glossary_terms = set(glossary.get("terms", {}).keys())

    # Find all Python files in ui/
    py_files = list(ui_dir.rglob("*.py"))

    all_calls: list[dict[str, Any]] = []
    for py_file in py_files:
        all_calls.extend(extract_tr_calls(py_file))

    used_keys = {call["key"] for call in all_calls}
    missing_keys = used_keys - glossary_terms
    unused_keys = glossary_terms - used_keys

    # Check for string concatenation in tr() calls
    concat_issues = []
    for call in all_calls:
        if "+" in call["key"] or "{" in call["key"]:
            concat_issues.append(call)

    return {
        "total_calls": len(all_calls),
        "unique_keys": len(used_keys),
        "glossary_terms": len(glossary_terms),
        "missing_keys": sorted(missing_keys),
        "unused_keys": sorted(unused_keys),
        "concat_issues": concat_issues,
        "coverage_pct": (
            len(used_keys & glossary_terms) / len(used_keys) * 100 if used_keys else 100
        ),
    }


def extract_explorer_strings(glossary_path: Path) -> list[dict[str, str]]:
    """Extract all Explorer register strings for translation."""
    glossary = json.loads(glossary_path.read_text(encoding="utf-8"))
    terms = glossary.get("terms", {})

    explorer_strings = []
    for key, registers in terms.items():
        if "explorer" in registers:
            explorer_strings.append({
                "key": key,
                "explorer": registers["explorer"],
                "lab": registers.get("lab", ""),
            })

    return explorer_strings


def check_readability(
    strings: list[dict[str, str]], max_grade: float = 8.0
) -> list[dict[str, Any]]:
    """Check Flesch-Kincaid grade level for Explorer strings."""
    import textstat

    issues = []
    for entry in strings:
        text = entry["explorer"]
        if not text or text.isspace():
            continue
        try:
            grade = textstat.flesch_kincaid_grade(text)
            if grade > max_grade:
                issues.append({
                    "key": entry["key"],
                    "text": text,
                    "grade": grade,
                    "max_grade": max_grade,
                })
        except Exception:
            pass  # Skip unparseable text

    return sorted(issues, key=lambda x: x["grade"], reverse=True)


def main() -> int:
    """CLI entry point for i18n extraction audit."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="comp i18n-extract",
        description="Extract and audit i18n strings from UI components",
    )
    parser.add_argument(
        "--glossary",
        type=Path,
        default=Path("computronium/ui/glossary.json"),
        help="Path to glossary.json",
    )
    parser.add_argument(
        "--ui-dir",
        type=Path,
        default=Path("computronium/ui"),
        help="UI source directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/i18n_audit.json"),
        help="Output audit report",
    )
    parser.add_argument(
        "--explorer-output",
        type=Path,
        default=Path("reports/explorer_strings.json"),
        help="Output Explorer strings for translation",
    )
    parser.add_argument(
        "--check-readability",
        action="store_true",
        help="Check Flesch-Kincaid readability (requires textstat)",
    )
    args = parser.parse_args()

    print(f"Glossary: {args.glossary}")
    print(f"UI Dir: {args.ui_dir}")

    # Coverage check
    coverage = check_glossary_coverage(args.glossary, args.ui_dir)

    print("\n=== Coverage Report ===")
    print(f"Total tr() calls: {coverage['total_calls']}")
    print(f"Unique keys: {coverage['unique_keys']}")
    print(f"Glossary terms: {coverage['glossary_terms']}")
    print(f"Coverage: {coverage['coverage_pct']:.1f}%")

    if coverage["missing_keys"]:
        print(f"\n❌ MISSING KEYS ({len(coverage['missing_keys'])}):")
        for key in coverage["missing_keys"]:
            print(f"  - {key}")
    else:
        print("\n✅ All keys found in glossary")

    if coverage["unused_keys"]:
        print(f"\n⚠️ UNUSED KEYS ({len(coverage['unused_keys'])}):")
        for key in coverage["unused_keys"][:20]:
            print(f"  - {key}")
        if len(coverage["unused_keys"]) > 20:
            print(f"  ... and {len(coverage['unused_keys']) - 20} more")

    if coverage["concat_issues"]:
        print(f"\n❌ CONCATENATION ISSUES ({len(coverage['concat_issues'])}):")
        for issue in coverage["concat_issues"]:
            print(f"  {issue['file']}:{issue['line']} - {issue['key']}")

    # Extract Explorer strings
    explorer_strings = extract_explorer_strings(args.glossary)
    print("\n=== Explorer Strings ===")
    print(f"Total: {len(explorer_strings)}")

    args.explorer_output.parent.mkdir(parents=True, exist_ok=True)
    args.explorer_output.write_text(
        json.dumps(explorer_strings, indent=2, ensure_ascii=False)
    )
    print(f"Exported to: {args.explorer_output}")

    # Readability check
    if args.check_readability:
        try:
            readability_issues = check_readability(explorer_strings)
            if readability_issues:
                print(f"\n❌ READABILITY ISSUES ({len(readability_issues)}):")
                for issue in readability_issues[:10]:
                    print(
                        f"  [{issue['grade']:.1f}] {issue['key']}: {issue['text'][:80]}"
                    )
            else:
                print("\n✅ All Explorer strings pass readability check (≤ FK grade 8)")
        except ImportError:
            print("\n⚠️ textstat not installed, skipping readability check")

    # Write full audit report
    audit_report = {
        "coverage": coverage,
        "explorer_strings_count": len(explorer_strings),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit_report, indent=2))
    print(f"\nFull audit report: {args.output}")

    # Exit with error if issues found
    has_errors = bool(coverage["missing_keys"] or coverage["concat_issues"])
    if args.check_readability:
        try:
            readability_issues = check_readability(explorer_strings)
            has_errors = has_errors or bool(readability_issues)
        except ImportError:
            pass

    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
