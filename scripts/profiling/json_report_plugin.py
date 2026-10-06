#!/usr/bin/env python
"""Pytest plugin for structured JSON test output.

Usage:
    uv run python -m pytest tests/ --json-report=report.json
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


@dataclass
class TestResult:
    """Structured test result."""

    nodeid: str
    outcome: str  # passed, failed, error, skipped, xfailed, xpassed
    duration_ms: float
    filepath: str
    lineno: int | None = None
    error_message: str | None = None
    traceback_str: str | None = None


@dataclass
class TestSessionReport:
    """Complete test session report."""

    start_time: float
    end_time: float
    total_duration_ms: float
    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    xfailed: int
    xpassed: int
    results: list[TestResult]


class JSONReportPlugin:
    """Pytest plugin for JSON test reporting."""

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.results: list[TestResult] = []
        self.session_start = time.perf_counter()
        self._current_test_start: float = 0.0

    def pytest_sessionstart(self, session: pytest.Session) -> None:
        """Record session start time."""
        self.session_start = time.perf_counter()

    def pytest_runtest_logstart(
        self, nodeid: str, location: tuple[str, int | None, str]
    ) -> None:
        """Record test start time."""
        self._current_test_start = time.perf_counter()

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Record test result."""
        if report.when != "call":
            # Only record the main test call, not setup/teardown
            return

        duration_ms = (time.perf_counter() - self._current_test_start) * 1000
        filepath, lineno, _ = report.location

        error_message = None
        traceback_str = None
        if report.failed or report.outcome == "error":
            if report.longrepr:
                error_message = str(report.longrepr)
            if hasattr(report, "traceback") and report.traceback:
                try:
                    traceback_str = "".join(report.traceback.format())
                except Exception:
                    traceback_str = str(report.traceback)

        result = TestResult(
            nodeid=report.nodeid,
            outcome=report.outcome,
            duration_ms=duration_ms,
            filepath=filepath,
            lineno=lineno,
            error_message=error_message,
            traceback_str=traceback_str,
        )
        self.results.append(result)

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        """Write JSON report on session finish."""
        session_end = time.perf_counter()
        total_duration_ms = (session_end - self.session_start) * 1000

        # Count outcomes
        counts = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0,
        }
        for r in self.results:
            if r.outcome in counts:
                counts[r.outcome] += 1

        report = TestSessionReport(
            start_time=self.session_start,
            end_time=session_end,
            total_duration_ms=total_duration_ms,
            total_tests=len(self.results),
            passed=counts["passed"],
            failed=counts["failed"],
            errors=counts["errors"],
            skipped=counts["skipped"],
            xfailed=counts["xfailed"],
            xpassed=counts["xpassed"],
            results=self.results,
        )

        # Write JSON
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

        print(f"\nJSON report written to {self.output_path}")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command line option for JSON report."""
    parser.addoption(
        "--json-report",
        action="store",
        metavar="PATH",
        help="Write structured JSON test report to PATH",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register plugin if --json-report is specified."""
    json_report = config.getoption("--json-report")
    if json_report:
        plugin = JSONReportPlugin(json_report)
        config.pluginmanager.register(plugin, "jsonreport")


if __name__ == "__main__":
    # Allow running as script for testing
    print("This is a pytest plugin. Use: pytest --json-report=report.json")
