"""Experiment Catalog — auto-generated from store queries.

Provides a queryable catalog of all experiment runs and records with filtering
by axis, metrics, date range, and linking to reports and raw data.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    """Single entry in the experiment catalog."""

    run_id: str
    run_name: str | None
    timestamp: str
    git_commit: str | None
    device: str | None
    n_records: int
    axes_covered: dict[str, set[str]]
    metrics_available: set[str]
    status_summary: dict[str, int]


@dataclass(frozen=True, slots=True)
class RecordEntry:
    """Single record entry with key metrics."""

    record_id: str
    run_id: str
    substrate: str
    geometry: str
    dynamics: str
    plasticity: str
    credit: str
    update: str
    maturity: str
    gate_verdict: str
    loss: float | None
    accuracy: float | None
    runtime_seconds: float | None
    seed: int | None


def _extract_run_metadata(store: RecordStore, run_id: str) -> dict[str, Any] | None:
    """Extract run-level metadata from the store using public API."""
    run_info = store.query_run(run_id)
    if not run_info:
        return None

    spec = run_info.spec
    if spec is None:
        return {
            "run_name": run_info.run_id[:8],
            "timestamp": run_info.started_at.isoformat()
            if run_info.started_at
            else None,
            "git_commit": None,
            "device": None,
        }

    return {
        "run_name": spec.profile if spec.profile != "custom" else run_info.run_id[:8],
        "timestamp": run_info.started_at.isoformat() if run_info.started_at else None,
        "git_commit": spec.code_sha if spec.code_sha != "unknown" else None,
        "device": spec.device if spec.device != "auto" else None,
    }


def _extract_axes_covered(store: RecordStore, run_id: str) -> dict[str, set[str]]:
    """Extract unique axis values covered in a run."""
    axes = ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"]
    result: dict[str, set[str]] = {axis: set() for axis in axes}

    # Use public API to query records (assumes caller has entered store context)
    records = store.query_records(run_id=run_id)
    for record in records:
        for axis in axes:
            value = getattr(record, axis, None)
            if value:
                result[axis].add(value)

    return result


def _extract_metrics_available(store: RecordStore, run_id: str) -> set[str]:
    """Extract all metric names available in a run's records."""
    metrics = set()
    records = store.query_records(run_id=run_id)
    for record in records:
        metrics.update(record.payload.keys())

    return metrics


def _extract_status_summary(store: RecordStore, run_id: str) -> dict[str, int]:
    """Extract status summary for a run."""
    summary = {"PASS": 0, "FAIL": 0, "QUARANTINE": 0, "PENDING": 0}
    records = store.query_records(run_id=run_id)
    for record in records:
        verdict = record.status.gate_verdict.value
        if verdict in summary:
            summary[verdict] += 1
        else:
            summary["PENDING"] += 1

    return summary


def build_catalog(store_path: Path) -> list[CatalogEntry]:
    """Build the experiment catalog from a store.

    Args:
        store_path: Path to the experiment store database.

    Returns:
        List of catalog entries sorted by timestamp (newest first).
    """
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.schema import _ensure_registries_seeded

    _ensure_registries_seeded()

    store = RecordStore(StoreConfig(path=store_path))
    entries = []

    with store:
        runs = store.query_runs()

        for run in runs:
            meta = _extract_run_metadata(store, run.run_id)
            if not meta:
                continue

            axes = _extract_axes_covered(store, run.run_id)
            metrics = _extract_metrics_available(store, run.run_id)
            status = _extract_status_summary(store, run.run_id)

            n_records = sum(status.values())

            entries.append(
                CatalogEntry(
                    run_id=run.run_id,
                    run_name=meta["run_name"],
                    timestamp=meta["timestamp"],
                    git_commit=meta["git_commit"],
                    device=meta["device"],
                    n_records=n_records,
                    axes_covered=axes,
                    metrics_available=metrics,
                    status_summary=status,
                )
            )

    # Sort by timestamp descending (newest first)
    entries.sort(key=lambda e: e.timestamp or "", reverse=True)
    return entries


@dataclass(frozen=True, slots=True)
class RecordQuery:
    """Query parameters for record search."""

    store_path: Path
    substrate: str | None = None
    geometry: str | None = None
    dynamics: str | None = None
    plasticity: str | None = None
    credit: str | None = None
    update: str | None = None
    maturity: str | None = None
    gate_verdict: str | None = None
    run_id: str | None = None
    min_loss: float | None = None
    max_loss: float | None = None
    limit: int = 100


def query_records(query: RecordQuery) -> list[RecordEntry]:
    """Query records with axis filters.

    Args:
        query: RecordQuery object containing all filter parameters.

    Returns:
        List of matching record entries.
    """
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.schema import _ensure_registries_seeded
    from computronium.experiment.schema.record import GateVerdict, Maturity

    _ensure_registries_seeded()

    store = RecordStore(StoreConfig(path=query.store_path))
    entries = []

    # Use public API with available filters
    gv = GateVerdict(query.gate_verdict) if query.gate_verdict else None
    mat = Maturity(query.maturity) if query.maturity else None

    with store:
        records = store.query_records(
            run_id=query.run_id, gate_verdict=gv, limit=query.limit * 2
        )

        for record in records:
            # Apply axis filters in Python
            if query.substrate and record.substrate != query.substrate:
                continue
            if query.geometry and record.geometry != query.geometry:
                continue
            if query.dynamics and record.dynamics != query.dynamics:
                continue
            if query.plasticity and record.plasticity != query.plasticity:
                continue
            if query.credit and record.credit != query.credit:
                continue
            if query.update and record.update != query.update:
                continue
            if mat and record.status.maturity != mat:
                continue

            # Apply payload filters
            loss = record.payload.get("loss")
            accuracy = record.payload.get("accuracy")
            runtime = record.payload.get("runtime_seconds")
            seed = record.payload.get("seed")

            if loss is not None:
                if query.min_loss is not None and loss < query.min_loss:
                    continue
                if query.max_loss is not None and loss > query.max_loss:
                    continue

            entries.append(
                RecordEntry(
                    record_id=record.record_id,
                    run_id=record.run_id,
                    substrate=record.substrate,
                    geometry=record.geometry,
                    dynamics=record.dynamics,
                    plasticity=record.plasticity,
                    credit=record.credit,
                    update=record.update,
                    maturity=record.status.maturity.value,
                    gate_verdict=record.status.gate_verdict.value,
                    loss=loss,
                    accuracy=accuracy,
                    runtime_seconds=runtime,
                    seed=seed,
                )
            )

            if len(entries) >= query.limit:
                break

    return entries


def export_catalog(
    catalog: list[CatalogEntry], output_path: Path, format: str = "json"
) -> None:
    """Export catalog to file.

    Args:
        catalog: List of catalog entries.
        output_path: Output file path.
        format: Export format (json, csv).
    """
    if format == "json":
        data = [
            {
                "run_id": e.run_id,
                "run_name": e.run_name,
                "timestamp": e.timestamp,
                "git_commit": e.git_commit,
                "device": e.device,
                "n_records": e.n_records,
                "axes_covered": {k: list(v) for k, v in e.axes_covered.items()},
                "metrics_available": list(e.metrics_available),
                "status_summary": e.status_summary,
            }
            for e in catalog
        ]
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif format == "csv":
        import csv

        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "run_id",
                "run_name",
                "timestamp",
                "git_commit",
                "device",
                "n_records",
                "axes_covered",
                "metrics_available",
                "status_summary",
            ])
            for e in catalog:
                writer.writerow([
                    e.run_id,
                    e.run_name or "",
                    e.timestamp or "",
                    e.git_commit or "",
                    e.device or "",
                    e.n_records,
                    json.dumps({k: list(v) for k, v in e.axes_covered.items()}),
                    json.dumps(list(e.metrics_available)),
                    json.dumps(e.status_summary),
                ])
    else:
        raise ValueError(f"Unknown format: {format}")


def export_records(
    records: list[RecordEntry], output_path: Path, format: str = "json"
) -> None:
    """Export records to file.

    Args:
        records: List of record entries.
        output_path: Output file path.
        format: Export format (json, csv).
    """
    if format == "json":
        data = [
            {
                "record_id": e.record_id,
                "run_id": e.run_id,
                "substrate": e.substrate,
                "geometry": e.geometry,
                "dynamics": e.dynamics,
                "plasticity": e.plasticity,
                "credit": e.credit,
                "update": e.update,
                "maturity": e.maturity,
                "gate_verdict": e.gate_verdict,
                "loss": e.loss,
                "accuracy": e.accuracy,
                "runtime_seconds": e.runtime_seconds,
                "seed": e.seed,
            }
            for e in records
        ]
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif format == "csv":
        import csv

        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "record_id",
                "run_id",
                "substrate",
                "geometry",
                "dynamics",
                "plasticity",
                "credit",
                "update",
                "maturity",
                "gate_verdict",
                "loss",
                "accuracy",
                "runtime_seconds",
                "seed",
            ])
            for e in records:
                writer.writerow([
                    e.record_id,
                    e.run_id,
                    e.substrate,
                    e.geometry,
                    e.dynamics,
                    e.plasticity,
                    e.credit,
                    e.update,
                    e.maturity,
                    e.gate_verdict,
                    e.loss if e.loss is not None else "",
                    e.accuracy if e.accuracy is not None else "",
                    e.runtime_seconds if e.runtime_seconds is not None else "",
                    e.seed if e.seed is not None else "",
                ])
    else:
        raise ValueError(f"Unknown format: {format}")


def _build_catalog_parser() -> argparse.ArgumentParser:
    """Build the catalog CLI parser."""
    parser = argparse.ArgumentParser(
        prog="comp catalog",
        description="Experiment Catalog — query and export experiment runs/records",
    )
    sub = parser.add_subparsers(
        dest="catalog_command", metavar="<command>", required=True
    )

    # list command
    list_parser = sub.add_parser("list", help="List all runs in catalog")
    list_parser.add_argument("--store", required=True, help="Path to experiment store")
    list_parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format",
    )
    list_parser.add_argument("--output", help="Output file (default: stdout)")

    # search command
    search_parser = sub.add_parser("search", help="Search records with filters")
    search_parser.add_argument(
        "--store", required=True, help="Path to experiment store"
    )
    search_parser.add_argument("--substrate", help="Filter by substrate")
    search_parser.add_argument("--geometry", help="Filter by geometry")
    search_parser.add_argument("--dynamics", help="Filter by dynamics")
    search_parser.add_argument("--plasticity", help="Filter by plasticity")
    search_parser.add_argument("--credit", help="Filter by credit assignment")
    search_parser.add_argument("--update", help="Filter by update rule")
    search_parser.add_argument(
        "--maturity", choices=["l0", "l1", "l2"], help="Filter by maturity"
    )
    search_parser.add_argument(
        "--gate-verdict",
        choices=["PASS", "FAIL", "QUARANTINE"],
        help="Filter by gate verdict",
    )
    search_parser.add_argument("--run-id", help="Filter by run ID")
    search_parser.add_argument("--min-loss", type=float, help="Minimum loss value")
    search_parser.add_argument("--max-loss", type=float, help="Maximum loss value")
    search_parser.add_argument("--limit", type=int, default=100, help="Max results")
    search_parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format",
    )
    search_parser.add_argument("--output", help="Output file (default: stdout)")

    # export command
    export_parser = sub.add_parser("export", help="Export full catalog")
    export_parser.add_argument(
        "--store", required=True, help="Path to experiment store"
    )
    export_parser.add_argument("--output", required=True, help="Output file")
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Output format"
    )

    return parser


def _print_catalog_text(entries: list[CatalogEntry]) -> None:
    """Print catalog in text format."""
    if not entries:
        print("No runs found in catalog.")
        return

    for e in entries:
        print(f"Run: {e.run_id}")
        if e.run_name:
            print(f"  Name: {e.run_name}")
        if e.timestamp:
            print(f"  Time: {e.timestamp}")
        if e.git_commit:
            print(f"  Commit: {e.git_commit[:8]}")
        if e.device:
            print(f"  Device: {e.device}")
        print(f"  Records: {e.n_records}")
        print(f"  Status: {e.status_summary}")
        axes_str = ", ".join(f"{k}={sorted(v)}" for k, v in e.axes_covered.items() if v)
        if axes_str:
            print(f"  Axes: {axes_str}")
        if e.metrics_available:
            print(f"  Metrics: {', '.join(sorted(e.metrics_available))}")
        print()


def _print_records_text(entries: list[RecordEntry]) -> None:
    """Print records in text format."""
    if not entries:
        print("No records found matching criteria.")
        return

    for e in entries:
        print(f"Record: {e.record_id[:16]}...")
        print(f"  Run: {e.run_id}")
        print(
            f"  Axes: substrate={e.substrate} geometry={e.geometry} dynamics={e.dynamics} "
            f"plasticity={e.plasticity} credit={e.credit} update={e.update}"
        )
        print(f"  Maturity: {e.maturity} | Verdict: {e.gate_verdict}")
        metrics = []
        if e.loss is not None:
            metrics.append(f"loss={e.loss:.4f}")
        if e.accuracy is not None:
            metrics.append(f"acc={e.accuracy:.4f}")
        if e.runtime_seconds is not None:
            metrics.append(f"runtime={e.runtime_seconds:.1f}s")
        if e.seed is not None:
            metrics.append(f"seed={e.seed}")
        if metrics:
            print(f"  Metrics: {', '.join(metrics)}")
        print()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for catalog commands."""
    parser = _build_catalog_parser()
    args = parser.parse_args(argv)

    store_path = Path(args.store)

    if args.catalog_command == "list":
        catalog = build_catalog(store_path)

        if args.format == "text":
            if args.output:
                import sys

                old_stdout = sys.stdout
                try:
                    with Path(args.output).open("w", encoding="utf-8") as f:
                        sys.stdout = f
                        _print_catalog_text(catalog)
                finally:
                    sys.stdout = old_stdout
            else:
                _print_catalog_text(catalog)
        elif args.format == "json":
            output_path = Path(args.output) if args.output else None
            if output_path:
                export_catalog(catalog, output_path, "json")
            else:
                data = [
                    {
                        "run_id": e.run_id,
                        "run_name": e.run_name,
                        "timestamp": e.timestamp,
                        "git_commit": e.git_commit,
                        "device": e.device,
                        "n_records": e.n_records,
                        "axes_covered": {k: list(v) for k, v in e.axes_covered.items()},
                        "metrics_available": list(e.metrics_available),
                        "status_summary": e.status_summary,
                    }
                    for e in catalog
                ]
                print(json.dumps(data, indent=2))
        elif args.format == "csv":
            output_path = Path(args.output) if args.output else None
            if output_path:
                export_catalog(catalog, output_path, "csv")
            else:
                import csv
                import sys

                writer = csv.writer(sys.stdout)
                writer.writerow([
                    "run_id",
                    "run_name",
                    "timestamp",
                    "git_commit",
                    "device",
                    "n_records",
                    "axes_covered",
                    "metrics_available",
                    "status_summary",
                ])
                for e in catalog:
                    writer.writerow([
                        e.run_id,
                        e.run_name or "",
                        e.timestamp or "",
                        e.git_commit or "",
                        e.device or "",
                        e.n_records,
                        json.dumps({k: list(v) for k, v in e.axes_covered.items()}),
                        json.dumps(list(e.metrics_available)),
                        json.dumps(e.status_summary),
                    ])

    elif args.catalog_command == "search":
        query = RecordQuery(
            store_path=store_path,
            substrate=args.substrate,
            geometry=args.geometry,
            dynamics=args.dynamics,
            plasticity=args.plasticity,
            credit=args.credit,
            update=args.update,
            maturity=args.maturity,
            gate_verdict=args.gate_verdict,
            run_id=args.run_id,
            min_loss=args.min_loss,
            max_loss=args.max_loss,
            limit=args.limit,
        )
        records = query_records(query)

        if args.format == "text":
            if args.output:
                import sys

                old_stdout = sys.stdout
                try:
                    with Path(args.output).open("w", encoding="utf-8") as f:
                        sys.stdout = f
                        _print_records_text(records)
                finally:
                    sys.stdout = old_stdout
            else:
                _print_records_text(records)
        elif args.format == "json":
            output_path = Path(args.output) if args.output else None
            if output_path:
                export_records(records, output_path, "json")
            else:
                data = [
                    {
                        "record_id": e.record_id,
                        "run_id": e.run_id,
                        "substrate": e.substrate,
                        "geometry": e.geometry,
                        "dynamics": e.dynamics,
                        "plasticity": e.plasticity,
                        "credit": e.credit,
                        "update": e.update,
                        "maturity": e.maturity,
                        "gate_verdict": e.gate_verdict,
                        "loss": e.loss,
                        "accuracy": e.accuracy,
                        "runtime_seconds": e.runtime_seconds,
                        "seed": e.seed,
                    }
                    for e in records
                ]
                print(json.dumps(data, indent=2))
        elif args.format == "csv":
            output_path = Path(args.output) if args.output else None
            if output_path:
                export_records(records, output_path, "csv")
            else:
                import csv
                import sys

                writer = csv.writer(sys.stdout)
                writer.writerow([
                    "record_id",
                    "run_id",
                    "substrate",
                    "geometry",
                    "dynamics",
                    "plasticity",
                    "credit",
                    "update",
                    "maturity",
                    "gate_verdict",
                    "loss",
                    "accuracy",
                    "runtime_seconds",
                    "seed",
                ])
                for e in records:
                    writer.writerow([
                        e.record_id,
                        e.run_id,
                        e.substrate,
                        e.geometry,
                        e.dynamics,
                        e.plasticity,
                        e.credit,
                        e.update,
                        e.maturity,
                        e.gate_verdict,
                        e.loss if e.loss is not None else "",
                        e.accuracy if e.accuracy is not None else "",
                        e.runtime_seconds if e.runtime_seconds is not None else "",
                        e.seed if e.seed is not None else "",
                    ])

    elif args.catalog_command == "export":
        catalog = build_catalog(store_path)
        export_catalog(catalog, Path(args.output), args.format)
        print(f"Exported {len(catalog)} runs to {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
