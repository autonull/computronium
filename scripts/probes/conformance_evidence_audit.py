"""C1–C88 conformance-evidence audit probe (WP13 DoD hardening).

Executes every capability's ``verifying_test`` pytest node id via the
ConformanceHarness and records the pass/fail result for each. Produces a
complete conformance evidence audit showing every capability has a passing
test (or an explicit retirement record).

Pass criterion: all 88 capabilities have status PASS_ (or RETIRED/SKIPPED
with a record). The audit fails if any required capability lacks evidence.

Measured regime (filled on run): total, passed, failed, retired, skipped,
walltime.
Informs: WP13 Definition of Done — every C1–C88 + gated row has conformance
evidence or a retirement record.

Usage:
    uv run python scripts/probes/conformance_evidence_audit.py \
        [--out logs/conformance_audit.json] [--timeout 60]
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.seed_registries import seed_all_registries
from computronium.experiment.surface.conformance import (
    ConformanceStatus,
    check_conformance,
)

logger = logging.getLogger(__name__)


def run_conformance_audit(
    execute_tests: bool = True,
) -> dict:
    """Run the full C1–C88 conformance-evidence audit.

    Args:
        execute_tests: If True, execute verifying tests; otherwise check
            evidence from the store only.

    Returns:
        Dict with per-capability results and summary counts.
    """
    seed_all_registries()

    store_path = Path("logs/conformance_audit_store.duckdb")
    store_path.parent.mkdir(parents=True, exist_ok=True)

    start = time.monotonic()
    with RecordStore(StoreConfig(path=store_path)) as store:
        results = check_conformance(
            store=store,
            execute_verifying_tests=execute_tests,
        )
    walltime = time.monotonic() - start

    passed = sum(1 for r in results if r.status == ConformanceStatus.PASS_)
    failed = sum(1 for r in results if r.status == ConformanceStatus.FAIL)
    retired = sum(1 for r in results if r.status == ConformanceStatus.RETIRED)
    skipped = sum(1 for r in results if r.status == ConformanceStatus.SKIPPED)
    no_evidence = sum(1 for r in results if r.status == ConformanceStatus.NO_EVIDENCE)

    per_capability = [
        {
            "capability_id": r.capability_id,
            "capability_name": r.capability_name,
            "kind": r.kind.value,
            "status": r.status.value,
            "evidence_count": r.evidence_count,
            "message": r.message,
            "test_duration_seconds": round(r.test_duration_seconds, 3),
        }
        for r in results
    ]

    return {
        "total": len(results),
        "passed": passed,
        "failed": failed,
        "retired": retired,
        "skipped": skipped,
        "no_evidence": no_evidence,
        "walltime_s": round(walltime, 1),
        "all_green": failed == 0 and no_evidence == 0,
        "per_capability": per_capability,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="logs/conformance_audit.json")
    ap.add_argument(
        "--no-execute",
        action="store_true",
        help="Check evidence from store only (skip test execution)",
    )
    args = ap.parse_args()

    logging.basicConfig(level=logging.WARNING)

    result = run_conformance_audit(
        execute_tests=not args.no_execute,
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    summary = {k: v for k, v in result.items() if k != "per_capability"}
    print(json.dumps(summary, indent=2))

    if not result["all_green"]:
        failed_caps = [
            r["capability_id"]
            for r in result["per_capability"]
            if r["status"] in {"fail", "no_evidence"}
        ]
        msg = f"Conformance audit FAILED: {failed_caps}"
        raise SystemExit(msg)


if __name__ == "__main__":
    main()
