"""Accessibility audit utilities (M0.5, M3.5) — axe-core + keyboard crawl.

Provides automated and manual a11y testing helpers.
"""

from __future__ import annotations

import json
import subprocess  # noqa: S404
from dataclasses import dataclass
from pathlib import Path  # noqa: TC003
from typing import Literal

# ──────────────────────────────────────────────────────────────────────────────
# Types
# ──────────────────────────────────────────────────────────────────────────────

Severity = Literal["critical", "serious", "moderate", "minor"]


@dataclass(frozen=True, slots=True)
class AxeViolation:
    """Single axe-core violation."""

    id: str
    impact: Severity
    description: str
    help: str
    help_url: str
    nodes: list[dict]
    tags: list[str]


@dataclass(frozen=True, slots=True)
class AxeResult:
    """Axe-core scan result."""

    url: str
    violations: list[AxeViolation]
    passes: list[dict]
    incomplete: list[dict]
    inapplicable: list[dict]
    timestamp: str


# ──────────────────────────────────────────────────────────────────────────────
# Automated axe-core scan
# ──────────────────────────────────────────────────────────────────────────────


def run_axe_scan(url: str, output_path: Path | None = None) -> AxeResult:
    """Run axe-core against a URL using the CLI.

    Requires: ``npm install -g @axe-core/cli``

    Args:
        url: Target URL (e.g., "http://localhost:8088")
        output_path: Optional path to write JSON results

    Returns:
        Parsed AxeResult with violations
    """
    try:
        result = subprocess.run(  # noqa: S603,S607
            ["axe", url, "--json"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )  # noqa: S607
    except FileNotFoundError:
        raise RuntimeError(
            "axe CLI not found. Install with: npm install -g @axe-core/cli"
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("axe scan timed out after 120s")

    if result.returncode not in {0, 1, 2}:  # 0=pass, 1=violations, 2=error
        raise RuntimeError(f"axe scan failed: {result.stderr}")

    data = json.loads(result.stdout)
    if output_path:
        output_path.write_text(json.dumps(data, indent=2))

    violations = [
        AxeViolation(
            id=v["id"],
            impact=v["impact"],  # type: ignore[assignment]
            description=v["description"],
            help=v["help"],
            help_url=v["helpUrl"],
            nodes=v["nodes"],
            tags=v["tags"],
        )
        for v in data.get("violations", [])
    ]

    return AxeResult(
        url=url,
        violations=violations,
        passes=data.get("passes", []),
        incomplete=data.get("incomplete", []),
        inapplicable=data.get("inapplicable", []),
        timestamp=data.get("timestamp", ""),
    )


def violations_by_severity(result: AxeResult) -> dict[Severity, list[AxeViolation]]:
    """Group violations by severity."""
    grouped: dict[Severity, list[AxeViolation]] = {
        "critical": [],
        "serious": [],
        "moderate": [],
        "minor": [],
    }
    for v in result.violations:
        grouped[v.impact].append(v)
    return grouped


def has_critical_or_serious(result: AxeResult) -> bool:
    """Check if result has any critical or serious violations."""
    return any(v.impact in {"critical", "serious"} for v in result.violations)


def format_axe_report(result: AxeResult) -> str:
    """Format a human-readable report."""
    lines = [
        "axe-core Accessibility Report",
        f"URL: {result.url}",
        f"Timestamp: {result.timestamp}",
        f"Violations: {len(result.violations)}",
        f"  Critical: {len([v for v in result.violations if v.impact == 'critical'])}",
        f"  Serious:  {len([v for v in result.violations if v.impact == 'serious'])}",
        f"  Moderate: {len([v for v in result.violations if v.impact == 'moderate'])}",
        f"  Minor:    {len([v for v in result.violations if v.impact == 'minor'])}",
        "",
    ]

    for severity in ("critical", "serious", "moderate", "minor"):
        viols = [v for v in result.violations if v.impact == severity]
        if not viols:
            continue
        lines.append(f"=== {severity.upper()} ({len(viols)}) ===")
        for v in viols:
            lines.append(f"  [{v.id}] {v.description}")
            lines.append(f"    Help: {v.help}")
            lines.append(f"    URL:  {v.help_url}")
            for node in v.nodes[:3]:  # Show first 3 nodes
                target = " > ".join(node.get("target", []))
                lines.append(f"    Element: {target}")
                if "html" in node:
                    html = node["html"][:200]
                    lines.append(f"    HTML: {html}")
            if len(v.nodes) > 3:
                lines.append(f"    ... and {len(v.nodes) - 3} more elements")
            lines.append("")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Keyboard crawl checklist (manual)
# ──────────────────────────────────────────────────────────────────────────────

KEYBOARD_CHECKLIST = [
    {
        "id": "kbd_01",
        "description": "Tab reaches all interactive elements (buttons, links, inputs, selects)",
        "wcag": "2.1.1 Keyboard",
    },
    {
        "id": "kbd_02",
        "description": "Tab order is logical (left-to-right, top-to-bottom)",
        "wcag": "2.4.3 Focus Order",
    },
    {
        "id": "kbd_03",
        "description": "Focus indicator is visible on all interactive elements",
        "wcag": "2.4.7 Focus Visible",
    },
    {
        "id": "kbd_04",
        "description": "No keyboard traps (can tab away from every component)",
        "wcag": "2.1.2 No Keyboard Trap",
    },
    {
        "id": "kbd_05",
        "description": "Skip to main content link works",
        "wcag": "2.4.1 Bypass Blocks",
    },
    {
        "id": "kbd_06",
        "description": "All dialogs/modals trap focus and restore on close",
        "wcag": "2.4.3 Focus Order, 4.1.2 Name Role Value",
    },
    {
        "id": "kbd_07",
        "description": "Dropdowns/comboboxes navigable with arrow keys",
        "wcag": "2.1.1 Keyboard",
    },
    {
        "id": "kbd_08",
        "description": "Carousels/sliders have keyboard controls",
        "wcag": "2.1.1 Keyboard",
    },
    {
        "id": "kbd_09",
        "description": "Custom components have proper ARIA roles/states",
        "wcag": "4.1.2 Name Role Value",
    },
    {
        "id": "kbd_10",
        "description": "Live regions announce dynamic updates (aria-live)",
        "wcag": "4.1.3 Status Messages",
    },
]


@dataclass(frozen=True, slots=True)
class KeyboardCheckResult:
    """Result of a single keyboard check."""

    check_id: str
    passed: bool
    notes: str = ""


def run_keyboard_crawl(url: str) -> list[KeyboardCheckResult]:
    """Interactive keyboard crawl - requires manual testing.

    This function provides the checklist; actual testing is manual.
    Returns a template for recording results.
    """
    print(f"Manual keyboard crawl for: {url}")
    print(
        "Navigate the page using ONLY the keyboard (Tab, Shift+Tab, Enter, Space, Arrows, Esc)"
    )
    print("Record results for each check below.")
    print()

    results = []
    for check in KEYBOARD_CHECKLIST:
        print(f"[{check['id']}] {check['description']} (WCAG: {check['wcag']})")
        passed = input("  Passed? (y/n/skip): ").strip().lower()
        if passed == "y":
            results.append(KeyboardCheckResult(check["id"], True))
        elif passed == "n":
            notes = input("  Notes: ").strip()
            results.append(KeyboardCheckResult(check["id"], False, notes))
        else:
            results.append(KeyboardCheckResult(check["id"], False, "Skipped"))

    passed_count = sum(1 for r in results if r.passed)
    print(f"\nKeyboard crawl complete: {passed_count}/{len(results)} passed")
    return results


# ──────────────────────────────────────────────────────────────────────────────
# CI integration
# ──────────────────────────────────────────────────────────────────────────────


def ci_axe_scan(
    url: str, fail_on: tuple[Severity, ...] = ("critical", "serious")
) -> int:
    """CI-friendly axe scan - exits with code 1 if violations at or above fail_on severity."""
    result = run_axe_scan(url)
    grouped = violations_by_severity(result)

    failed = False
    for severity in fail_on:
        if grouped[severity]:
            print(f"FAIL: {len(grouped[severity])} {severity} violation(s)")
            failed = True

    if failed:
        print(format_axe_report(result))
        return 1

    print(f"PASS: No {', '.join(fail_on)} violations")
    return 0
