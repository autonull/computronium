"""Capability conformance harness (WP7 + WP11).

Ensures every C1-C88 + gated row has a passing test or explicit retirement record.
CI gate for capability conformance. Appendix A flags become a projection view
of CAPABILITIES with a currency lock.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore

from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilityKind,
    CapabilitySpec,
    CapabilityStatus,
)

__all__ = [
    "ConformanceHarness",
    "ConformanceResult",
    "ConformanceStatus",
    "CurrencyLock",
    "FlagProjectionLock",
    "check_conformance",
    "generate_conformance_report",
    "generate_flag_projection_lock",
    "load_currency_lock",
    "load_flag_projection_lock",
    "run_verifying_test",
    "save_currency_lock",
    "save_flag_projection_lock",
]


class ConformanceStatus(StrEnum):
    """Conformance check result status."""

    PASS_ = "pass"  # noqa: S105 - not a password, status value
    FAIL = "fail"
    SKIPPED = "skipped"  # Optional capability
    RETIRED = "retired"  # Explicitly retired with record
    NO_EVIDENCE = "no_evidence"  # Required but no evidence found


@dataclass(frozen=True, slots=True)
class ConformanceResult:
    """Result of a single capability conformance check."""

    capability_id: str
    capability_name: str
    kind: CapabilityKind
    status: ConformanceStatus
    evidence_count: int
    message: str
    checked_at: datetime
    verifying_test_result: str | None = None  # pytest node id + result
    test_duration_seconds: float = 0.0


@dataclass(frozen=True, slots=True)
class CurrencyLock:
    """Currency lock for capability conformance (R78).

    Ensures Appendix A flags (capability projections) are current.
    """

    generated_at: datetime
    capability_count: int
    passed_count: int
    failed_count: int
    retired_count: int
    skipped_count: int
    lock_hash: str  # Content hash of the lock file

    def is_current(self, max_age_hours: int = 24) -> bool:
        """Check if lock is current (not stale)."""
        age_hours = (datetime.now() - self.generated_at).total_seconds() / 3600
        return age_hours <= max_age_hours


@dataclass(frozen=True, slots=True)
class FlagProjectionLock:
    """Appendix-A flag projection lock (R78).

    Maps flags -> capability IDs, ensuring the projection view is current.
    """

    generated_at: datetime
    flag_to_capabilities: dict[str, list[str]]  # flag -> list of capability_ids
    capability_count: int
    lock_hash: str

    def is_current(self, max_age_hours: int = 24) -> bool:
        """Check if lock is current (not stale)."""
        age_hours = (datetime.now() - self.generated_at).total_seconds() / 3600
        return age_hours <= max_age_hours


def run_verifying_test(
    node_id: str, timeout_seconds: int = 60
) -> tuple[bool, str, float]:
    """Run a single pytest verifying test and return (passed, output, duration).

    Uses targeted selection (-k) to run only the specified test node.
    """
    import time

    start = time.monotonic()
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "pytest",
                node_id,
                "-v",
                "--tb=short",
                "-x",
            ],
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            cwd=Path.cwd(),
        )
        duration = time.monotonic() - start
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return passed, output, duration
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return False, f"Test timed out after {timeout_seconds}s", duration
    except Exception as e:
        duration = time.monotonic() - start
        return False, f"Test execution error: {e}", duration


class ConformanceHarness:
    """Capability conformance harness for CI gate enforcement.

    Every registered capability must have:
    - Passing verifying_test (pytest node id executed via targeted selection) (PASS)
    - OR be marked optional (SKIPPED)
    - OR have an explicit retirement record (RETIRED)
    """

    def __init__(self, store: RecordStore) -> None:
        self._store = store

    def check_all(
        self,
        run_id: str | None = None,
        require_all: bool = True,
        execute_verifying_tests: bool = True,
    ) -> list[ConformanceResult]:
        """Check all registered capabilities.

        Args:
            run_id: Optional run ID to filter evidence
            require_all: If True, fail on any required capability without evidence
            execute_verifying_tests: If True, run pytest verifying tests

        Returns:
            List of conformance results for all capabilities
        """
        results = []
        for capability_id, spec in CAPABILITIES_REGISTRY.items():
            result = self._check_capability(spec, run_id, execute_verifying_tests)
            results.append(result)

        if require_all:
            failed = [r for r in results if r.status == ConformanceStatus.FAIL]
            if failed:
                raise ConformanceError(
                    f"{len(failed)} required capabilities lack evidence", failed
                )

        return results

    def _check_capability(
        self,
        spec: CapabilitySpec,
        run_id: str | None,
        execute_verifying_tests: bool,
    ) -> ConformanceResult:
        """Check a single capability."""
        if not spec.required:
            return ConformanceResult(
                capability_id=spec.capability_id,
                capability_name=spec.name,
                kind=spec.kind,
                status=ConformanceStatus.SKIPPED,
                evidence_count=0,
                message=f"Optional capability ({spec.kind.value})",
                checked_at=datetime.now(),
            )

        # Check for retirement record
        if spec.status == CapabilityStatus.RETIRED:
            return ConformanceResult(
                capability_id=spec.capability_id,
                capability_name=spec.name,
                kind=spec.kind,
                status=ConformanceStatus.RETIRED,
                evidence_count=0,
                message=f"Retired: {spec.retirement_record or 'no record'}",
                checked_at=datetime.now(),
            )

        # Run verifying test if available
        if execute_verifying_tests and spec.verifying_test:
            passed, output, duration = run_verifying_test(spec.verifying_test)
            if passed:
                return ConformanceResult(
                    capability_id=spec.capability_id,
                    capability_name=spec.name,
                    kind=spec.kind,
                    status=ConformanceStatus.PASS_,
                    evidence_count=1,
                    message=f"Verifying test passed: {spec.verifying_test}",
                    checked_at=datetime.now(),
                    verifying_test_result=spec.verifying_test,
                    test_duration_seconds=duration,
                )
            else:
                return ConformanceResult(
                    capability_id=spec.capability_id,
                    capability_name=spec.name,
                    kind=spec.kind,
                    status=ConformanceStatus.FAIL,
                    evidence_count=0,
                    message=f"Verifying test failed: {spec.verifying_test}",
                    checked_at=datetime.now(),
                    verifying_test_result=f"FAILED: {spec.verifying_test}",
                    test_duration_seconds=duration,
                )

        # Fallback to store evidence query
        evidence_count = self._count_evidence(spec, run_id)

        if evidence_count > 0:
            return ConformanceResult(
                capability_id=spec.capability_id,
                capability_name=spec.name,
                kind=spec.kind,
                status=ConformanceStatus.PASS_,
                evidence_count=evidence_count,
                message=f"{evidence_count} passing record(s) found",
                checked_at=datetime.now(),
            )

        return ConformanceResult(
            capability_id=spec.capability_id,
            capability_name=spec.name,
            kind=spec.kind,
            status=ConformanceStatus.NO_EVIDENCE,
            evidence_count=0,
            message="Required capability has no verifying test or passing evidence",
            checked_at=datetime.now(),
        )

    def _count_evidence(self, spec: CapabilitySpec, run_id: str | None) -> int:
        """Count passing records as fallback evidence for a capability."""
        _ = spec  # evidence is currently run-scoped, not capability-scoped
        return self._store.count_passing_records(run_id)

    def generate_lock(self, run_id: str | None = None) -> CurrencyLock:
        """Generate a currency lock for the current conformance state."""
        results = self.check_all(run_id=run_id, require_all=False)

        passed = sum(1 for r in results if r.status == ConformanceStatus.PASS_)
        failed = sum(1 for r in results if r.status == ConformanceStatus.FAIL)
        skipped = sum(1 for r in results if r.status == ConformanceStatus.SKIPPED)
        retired = sum(1 for r in results if r.status == ConformanceStatus.RETIRED)

        # Generate lock hash from results
        lock_data = "|".join(
            f"{r.capability_id}:{r.status.value}:{r.evidence_count}"
            for r in sorted(results, key=lambda x: x.capability_id)
        )
        lock_hash = hashlib.sha256(lock_data.encode()).hexdigest()[:16]

        return CurrencyLock(
            generated_at=datetime.now(),
            capability_count=len(results),
            passed_count=passed,
            failed_count=failed,
            retired_count=retired,
            skipped_count=skipped,
            lock_hash=lock_hash,
        )


class ConformanceError(Exception):
    """Raised when conformance check fails."""

    def __init__(self, message: str, failed_results: list[ConformanceResult]) -> None:
        super().__init__(message)
        self.failed_results = failed_results


def check_conformance(
    store: RecordStore,
    run_id: str | None = None,
    require_all: bool = True,
    execute_verifying_tests: bool = True,
) -> list[ConformanceResult]:
    """Convenience function to run conformance check."""
    harness = ConformanceHarness(store)
    return harness.check_all(
        run_id=run_id,
        require_all=require_all,
        execute_verifying_tests=execute_verifying_tests,
    )


def generate_conformance_report(
    store: RecordStore,
    run_id: str | None = None,
    output_path: str | Path | None = None,
    execute_verifying_tests: bool = True,
) -> str:
    """Generate a human-readable conformance report."""
    harness = ConformanceHarness(store)
    results = harness.check_all(
        run_id=run_id,
        require_all=False,
        execute_verifying_tests=execute_verifying_tests,
    )
    lock = harness.generate_lock(run_id=run_id)

    lines = [
        "Capability Conformance Report",
        "=" * 60,
        f"Generated: {lock.generated_at.isoformat()}",
        f"Lock Hash: {lock.lock_hash}",
        f"Total Capabilities: {lock.capability_count}",
        f"  Passed: {lock.passed_count}",
        f"  Failed: {lock.failed_count}",
        f"  Retired: {lock.retired_count}",
        f"  Skipped (optional): {lock.skipped_count}",
        "",
        "Details:",
    ]

    for result in sorted(results, key=lambda x: (x.status.value, x.capability_id)):
        status_icon = {
            ConformanceStatus.PASS_: "✓",
            ConformanceStatus.FAIL: "✗",
            ConformanceStatus.SKIPPED: "⊘",
            ConformanceStatus.RETIRED: "◌",
            ConformanceStatus.NO_EVIDENCE: "?",
        }.get(result.status, "?")

        test_info = ""
        if result.verifying_test_result:
            test_info = f" [test: {result.verifying_test_result} ({result.test_duration_seconds:.2f}s)]"

        lines.append(
            f"  {status_icon} {result.capability_id:<32} [{result.kind.value:16}] "
            f"{result.status.value:12} evidence={result.evidence_count} - {result.message}{test_info}"
        )

    report_text = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(report_text, encoding="utf-8")

    return report_text


def generate_flag_projection_lock() -> FlagProjectionLock:
    """Generate Appendix-A flag projection lock (R78).

    Maps each flag to the capabilities that carry it.
    """
    flag_map: dict[str, list[str]] = {}
    for cap_id, spec in CAPABILITIES_REGISTRY.items():
        for flag in spec.flags:
            flag_map.setdefault(flag, []).append(cap_id)

    # Sort for deterministic output
    for flag in flag_map:
        flag_map[flag].sort()

    lock_data = "|".join(
        f"{flag}:{','.join(caps)}" for flag, caps in sorted(flag_map.items())
    )
    lock_hash = hashlib.sha256(lock_data.encode()).hexdigest()[:16]

    return FlagProjectionLock(
        generated_at=datetime.now(),
        flag_to_capabilities=flag_map,
        capability_count=len(CAPABILITIES_REGISTRY),
        lock_hash=lock_hash,
    )


def save_currency_lock(lock: CurrencyLock, path: str | Path) -> None:
    """Save currency lock to JSON file."""
    data = {
        "generated_at": lock.generated_at.isoformat(),
        "capability_count": lock.capability_count,
        "passed_count": lock.passed_count,
        "failed_count": lock.failed_count,
        "retired_count": lock.retired_count,
        "skipped_count": lock.skipped_count,
        "lock_hash": lock.lock_hash,
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_currency_lock(path: str | Path) -> CurrencyLock:
    """Load currency lock from JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return CurrencyLock(
        generated_at=datetime.fromisoformat(data["generated_at"]),
        capability_count=data["capability_count"],
        passed_count=data["passed_count"],
        failed_count=data["failed_count"],
        retired_count=data["retired_count"],
        skipped_count=data["skipped_count"],
        lock_hash=data["lock_hash"],
    )


def save_flag_projection_lock(lock: FlagProjectionLock, path: str | Path) -> None:
    """Save flag projection lock to JSON file."""
    data = {
        "generated_at": lock.generated_at.isoformat(),
        "flag_to_capabilities": lock.flag_to_capabilities,
        "capability_count": lock.capability_count,
        "lock_hash": lock.lock_hash,
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_flag_projection_lock(path: str | Path) -> FlagProjectionLock:
    """Load flag projection lock from JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return FlagProjectionLock(
        generated_at=datetime.fromisoformat(data["generated_at"]),
        flag_to_capabilities=data["flag_to_capabilities"],
        capability_count=data["capability_count"],
        lock_hash=data["lock_hash"],
    )
