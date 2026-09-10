"""CEEC CLI (Phase F.5 / H.2-H.3 / §12).

Usage:
    uv run python -m computronium.ceec.cli <command> [options]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER_DIR = REPO_ROOT / "ceec"


def _open_store(ledger_dir: Path):
    from computronium.ceec import CEECStore

    return CEECStore(ledger_dir / "ceec.sqlite3", ledger_dir / "artifacts")


def _init(args: argparse.Namespace) -> int:
    ledger_dir = Path(args.ledger_dir)
    with _open_store(ledger_dir) as store:
        print(f"initialized ledger at {store.db_path}")
    return 0


def _bootstrap(args: argparse.Namespace) -> int:
    from computronium.ceec import bootstrap

    with _open_store(Path(args.ledger_dir)) as store:
        result = bootstrap.bootstrap(store, Path(args.config))
        for kind, ids in result.items():
            print(f"{kind}: {len(ids)}")
            for id_ in ids:
                print(f"  {id_}")
    return 0


def _migrate(args: argparse.Namespace) -> int:
    from computronium.ceec.migrate import todo18_records

    with _open_store(Path(args.ledger_dir)) as store:
        result = todo18_records.migrate_all(store)
        print(json.dumps(result, indent=2, default=str))
    return 0


def _propose(args: argparse.Namespace) -> int:
    from computronium.ceec import selection

    with _open_store(Path(args.ledger_dir)) as store:
        candidates = selection.generate_candidates(store)
        for experiment in candidates[: args.limit]:
            print(
                f"{experiment.id}  budget={experiment.budget}  {experiment.question[:72]}"
            )
    return 0


def _decide(args: argparse.Namespace) -> int:
    from computronium.ceec import selection
    from computronium.ceec.store import _SCHEMA  # ruff: ignore[unused-import]

    profile = selection.load_profile(Path(args.profile))
    with _open_store(Path(args.ledger_dir)) as store:
        decision = selection.decide(store, profile, rationale=args.rationale)
        print(
            json.dumps(
                {
                    "id": decision.id,
                    "state_hash": decision.state_hash,
                    "selected": decision.selected_experiment,
                    "scores": decision.scores,
                },
                indent=2,
            )
        )
    return 0


def _audit(args: argparse.Namespace) -> int:
    from computronium.ceec import audit

    with _open_store(Path(args.ledger_dir)) as store:
        findings = audit.run_audit(store)
        if not findings:
            print("audit clean: no violations or warnings")
        for f in findings:
            print(f"[{f.severity}] {f.check}: {f.detail}")
        return 1 if any(f.severity == "violation" for f in findings) else 0


def _calibration_report(args: argparse.Namespace) -> int:
    from computronium.ceec import calibration

    with _open_store(Path(args.ledger_dir)) as store:
        report = calibration.calibration_report(store)
        flags = calibration.review_flags(report)
        print(json.dumps(report, indent=2))
        if flags:
            print("review flags:", ", ".join(flags))
    return 0


def _status_history(args: argparse.Namespace) -> int:
    with _open_store(Path(args.ledger_dir)) as store:
        for revision in store.revisions(args.belief):
            print(
                f"{revision.created_at}  {revision.status:12s}  "
                f"[{revision.probability.low:.2f}, {revision.probability.high:.2f}]  "
                f"{revision.rationale[:60]}"
            )
    return 0


def _emit_schema(args: argparse.Namespace) -> int:
    from computronium.ceec import schemas

    with _open_store(Path(args.ledger_dir)) as store:
        derived = schemas.emit_mechanism_schema(
            store,
            args.belief,
            statement=args.statement,
            supporting_evidence=args.evidence.split(",") if args.evidence else None,
            failure_boundaries=args.boundaries.split(",") if args.boundaries else [],
            verification_levels=dict(
                pair.split(":") for pair in args.levels.split(",") if pair
            ),
        )
        print(f"emitted {derived.id} for {args.belief}")
    return 0


def _quarantine_report(args: argparse.Namespace) -> int:
    with _open_store(Path(args.ledger_dir)) as store:
        quarantined = store.beliefs_by_status("quarantined")
        if not quarantined:
            print("no quarantined beliefs")
        for belief_id in quarantined:
            print(f"quarantined: {belief_id}")
            for dependent in store.dependents_of(belief_id):
                print(f"  blocks: {dependent}")
    return 0


def _export(args: argparse.Namespace) -> int:
    from computronium.ceec import audit, calibration

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    with _open_store(Path(args.ledger_dir)) as store:
        (out_dir / "calibration_report.json").write_text(
            json.dumps(calibration.calibration_report(store), indent=2)
        )
        findings = [
            {"check": f.check, "severity": f.severity, "detail": f.detail}
            for f in audit.run_audit(store)
        ]
        (out_dir / "audit.json").write_text(json.dumps(findings, indent=2))
        beliefs = [
            {
                "id": b,
                "status": store.current_status(b),
                "revision": (r.id if (r := store.latest_revision(b)) else None),
                "probability": (
                    [r.probability.low, r.probability.high]
                    if (r := store.latest_revision(b))
                    else None
                ),
            }
            for b in _all_belief_ids(store)
        ]
        (out_dir / "beliefs.json").write_text(json.dumps(beliefs, indent=2))
    print(f"exported to {out_dir}")
    return 0


def _all_belief_ids(store):
    return [r["id"] for r in store._conn.execute("SELECT id FROM beliefs").fetchall()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="computronium.ceec.cli")
    parser.add_argument("--ledger-dir", default=str(DEFAULT_LEDGER_DIR))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init").set_defaults(func=_init)

    p = sub.add_parser("bootstrap")
    p.add_argument("--config", default=str(REPO_ROOT / "configs" / "ceec"))
    p.set_defaults(func=_bootstrap)

    sub.add_parser("migrate").set_defaults(func=_migrate)

    p = sub.add_parser("propose")
    p.add_argument("--limit", type=int, default=16)
    p.set_defaults(func=_propose)

    p = sub.add_parser("decide")
    p.add_argument(
        "--profile", default=str(REPO_ROOT / "configs" / "ceec" / "profile.yaml")
    )
    p.add_argument("--rationale", required=True)
    p.set_defaults(func=_decide)

    sub.add_parser("audit").set_defaults(func=_audit)
    sub.add_parser("calibration-report").set_defaults(func=_calibration_report)

    p = sub.add_parser("status-history")
    p.add_argument("--belief", required=True)
    p.set_defaults(func=_status_history)

    sub.add_parser("quarantine-report").set_defaults(func=_quarantine_report)

    p = sub.add_parser("emit-schema")
    p.add_argument("--belief", required=True)
    p.add_argument("--statement", required=True)
    p.add_argument(
        "--evidence",
        default=None,
        help="comma-separated evidence IDs (default: all linked)",
    )
    p.add_argument(
        "--boundaries", default="", help="comma-separated failure boundaries"
    )
    p.add_argument(
        "--levels",
        default="",
        help="verification levels as evidence_id:level pairs, comma-separated",
    )
    p.set_defaults(func=_emit_schema)

    p = sub.add_parser("export")
    p.add_argument("--output", default=str(DEFAULT_LEDGER_DIR / "exports"))
    p.set_defaults(func=_export)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # CEECError + argument errors surface cleanly
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
