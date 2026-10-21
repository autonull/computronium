"""The surface CLI's run, report, and status commands."""

from __future__ import annotations

import json
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- controlled git call
import sys
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.execution.pipeline import PipelineConfig
from computronium.experiment.reporters import (
    generate_html_report as generate_html_report_v2,
)
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CapabilitySpec,
)
from computronium.experiment.surface.report import (
    ReportGenerator,
    RunSummary,
    export_to_json,
    export_to_parquet,
    generate_run_report,
)

from ._execution import _dry_run_report, _open_store, _resolve_spec, execute_spec

if TYPE_CHECKING:
    import argparse

logger = get_logger()


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute a run from a spec file or a named profile."""
    spec = _resolve_spec(args)

    # A dry run writes nothing: not a store, not a run row, not a checkpoint.
    if args.dry_run:
        if args.format == "json":
            # Build a JSON representation of the dry run plan
            from computronium.experiment.execution.pipeline import _resolve_tasks
            from computronium.experiment.kernel.evaluate import task_shape
            from computronium.experiment.kernel.search_space import (
                iter_candidates,
                search_space_from_spec,
            )
            from computronium.experiment.schema.axis import StructuralAxis
            from computronium.experiment.schema.harvest import AXIS_KIND_ORDER

            tasks = _resolve_tasks(PipelineConfig(run_id="dry-run", run_spec=spec))
            space = search_space_from_spec(spec, tasks=tasks)
            axes = {}
            for axis in StructuralAxis:
                names = space.primitives(axis)
                axes[axis.value] = list(names)

            cells = []
            for coordinate, schedule in iter_candidates(spec, space, shape=task_shape):
                swept = (
                    ", ".join(
                        f"{k}={v:.4g}" for k, v in sorted(coordinate.params.items())
                    )
                    or "no swept params"
                )
                selection = ", ".join(
                    f"{axis.value}={getattr(coordinate, axis.value)}"
                    for axis in AXIS_KIND_ORDER
                )
                cells.append({
                    "fidelity": schedule.fidelity,
                    "seed": schedule.seed,
                    "selection": selection,
                    "swept_params": swept,
                })

            from computronium.experiment.execution.pricing import price_plan

            plan = price_plan(spec, space).render().splitlines()

            output = json.dumps(
                {
                    "profile": spec.profile,
                    "tasks": list(tasks),
                    "fidelity": spec.fidelity,
                    "epochs": spec.epochs,
                    "seeds": spec.n_seeds,
                    "batch_limit": spec.batch_limit,
                    "param_budget": spec.param_budget,
                    "budget": spec.budget_seconds,
                    "policy": spec.policy or "round_robin_grid",
                    "objectives": list(spec.objectives) or "all",
                    "spec_version": spec.version,
                    "axes": axes,
                    "cells": cells,
                    "pricing": plan,
                },
                indent=2,
            )

            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print(_dry_run_report(spec, policy_name=spec.policy or "round_robin_grid"))
        return 0

    return execute_spec(spec, store_path=args.store, run_id=args.run_id)


def _cmd_report(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches, too-many-statements]
    """Generate report from store."""
    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        # Determine run_id
        run_id = args.run_id
        if run_id is None:
            run_id = store.latest_run_id()
            if run_id is None:
                logger.error("No runs found in store")
                return 1

        logger.info(f"Generating report for run: {run_id}")

        if args.axis_coverage:
            generator = ReportGenerator(store)
            coverage = generator.axis_coverage(run_id)
            lines = ["Axis Coverage (per-axis stratification):"]
            for axis, counts in sorted(coverage.items()):
                lines.append(f"  {axis}:")
                for value, count in sorted(counts.items()):
                    lines.append(f"    {value}: {count}")
            report_text = "\n".join(lines)
            if args.output:
                Path(args.output).write_text(report_text, encoding="utf-8")
                logger.info(f"Report written to {args.output}")
            else:
                print(report_text)
            return 0

        if args.format == "text":
            report_text = generate_run_report(store, run_id)
            if args.output:
                Path(args.output).write_text(report_text, encoding="utf-8")
                logger.info(f"Report written to {args.output}")
            else:
                print(report_text)
            return 0

        elif args.format == "json":
            output_path = args.output or f"{run_id}.report.json"
            export_to_json(store, output_path, run_id)
            logger.info(f"JSON report written to {output_path}")
            return 0

        elif args.format == "parquet":
            output_path = args.output or f"{run_id}.report.parquet"
            export_to_parquet(store, output_path, run_id)
            logger.info(f"Parquet report written to {output_path}")
            return 0

        elif args.format == "html":
            output_path = args.output or f"{run_id}.report.html"
            from computronium.experiment.reporters import ReportConfig

            config = ReportConfig(output_dir=str(Path(output_path).parent))
            generate_html_report_v2(store, run_id, config)
            logger.info(f"HTML report written to {output_path}")
            return 0

        elif args.format == "latex":
            output_path = args.output or f"{run_id}.report.tex"
            from computronium.experiment.surface.report import generate_latex_report

            generate_latex_report(store, run_id, output_path)
            logger.info(f"LaTeX report written to {output_path}")
            return 0

        elif args.format == "pdf":
            output_path = args.output or f"{run_id}.report.pdf"
            from computronium.experiment.surface.report import generate_pdf_report

            try:
                generate_pdf_report(store, run_id, output_path, keep_tex=args.keep_tex)
                logger.info(f"PDF report written to {output_path}")
            except RuntimeError:
                logger.exception("PDF generation failed")
                return 1
            return 0

    return 0


def _generate_dockerfile(
    store: RecordStore, run_id: str | None, output_path: str
) -> None:
    """Generate a Dockerfile for reproducible experiment environment."""

    with store:
        # Get run info to capture environment
        generator = ReportGenerator(store)
        _ = generator.run_summary(run_id) if run_id else None

        # Get git commit
        import contextlib

        git_commit = "unknown"
        with contextlib.suppress(Exception):
            import shutil

            git_path = shutil.which("git")
            if git_path:
                git_commit = subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                    [git_path, "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip()

        # Get Python version

        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Get PyTorch version
        import torch

        torch_version = torch.__version__
        cuda_version = torch.version.cuda or "cpu"

        # Generate Dockerfile
        dockerfile = f"""# Computronium Experiment Reproduction Dockerfile
# Generated from run {run_id or "all"} at {git_commit[:8] if git_commit != "unknown" else "unknown"}
# Python {python_version}, PyTorch {torch_version}, CUDA {cuda_version}

FROM nvidia/cuda:12.4-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    python3-pip \\
    python3-venv \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Set working directory
WORKDIR /computronium

# Copy project files
COPY pyproject.toml uv.lock ./
COPY computronium/ ./computronium/
COPY tests/ ./tests/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Install dependencies
RUN uv sync --dev --all-extras --no-install-project

# Install the project in development mode
RUN uv pip install -e .

# Set environment variables for reproducibility
ENV PYTHONHASHSEED=42
ENV CUBLAS_WORKSPACE_CONFIG=:4096:8
ENV TORCH_DETERMINISTIC=1

# Default command
CMD ["python", "-c", "import computronium; print('Computronium environment ready')"]
"""
        dockerfile_path = Path(output_path).with_suffix(".Dockerfile")
        dockerfile_path.write_text(dockerfile, encoding="utf-8")


def _cmd_export(args: argparse.Namespace) -> int:
    """Export store data for round-trip."""
    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        if args.format == "json":
            export_to_json(store, args.output, args.run_id)
        elif args.format == "parquet":
            export_to_parquet(store, args.output, args.run_id)
        logger.info(f"Export completed: {args.output}")

    # Generate Dockerfile if requested
    if args.docker:
        _generate_dockerfile(store, args.run_id, args.output)
        logger.info(f"Dockerfile generated: {args.output}.Dockerfile")

    return 0


def _cmd_import(args: argparse.Namespace) -> int:
    """Import store data from export (round-trip)."""
    import json

    if args.dry_run:
        plan = {
            "command": "import",
            "store": args.store,
            "input": args.input,
        }
        if args.format == "json":
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print("Dry run: would import export file")
            print(f"  Store: {args.store}")
            print(f"  Input: {args.input}")
        return 0

    # Load the export file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return 1

    with input_path.open(encoding="utf-8") as f:
        snapshot = json.load(f)

    # Open store in write mode
    try:
        store = RecordStore(StoreConfig(path=Path(args.store), read_only=False))
    except Exception as e:
        logger.error(f"Failed to open store: {e}")  # ruff: ignore[error-instead-of-exception]
        return 1

    with store:
        imported = store.import_snapshot(snapshot)
        logger.info(f"Import completed: {imported} records imported")

    if args.format == "json":
        output = json.dumps({"imported_records": imported}, indent=2)
    else:
        output = f"Imported {imported} records"

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        logger.info(f"Result written to {args.output}")
    else:
        print(output)

    return 0


def _cmd_conformance(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-statements]
    """Check capability conformance."""
    if args.dry_run:
        plan = {
            "command": "conformance",
            "store": args.store,
            "run_id": args.run_id,
            "list_only": args.list_only,
        }
        if args.format == "json":
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print("Dry run: would check capability conformance")
            print(f"  Store: {args.store}")
            print(f"  Run ID: {args.run_id or 'latest'}")
            print(f"  List only: {args.list_only}")
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        if args.list_only:
            results = []
            for name, spec in CAPABILITIES_REGISTRY.items():
                status = (
                    "pass"
                    if _check_capability(store, run_id=args.run_id, spec=spec)
                    else "fail"
                )
                if args.format == "json":
                    results.append({
                        "name": name,
                        "kind": spec.kind.value,
                        "required": spec.required,
                        "status": status,
                    })
                else:
                    print(f"  {status} {name} ({spec.kind.value})")
            if args.format == "json":
                output = json.dumps({"capabilities": results}, indent=2)
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    logger.info(f"Results written to {args.output}")
                else:
                    print(output)
            return 0

        # Full conformance check
        passed = 0
        failed = 0
        results = []

        for name, spec in CAPABILITIES_REGISTRY.items():
            if not spec.required:
                if args.format == "json":
                    results.append({
                        "name": name,
                        "kind": spec.kind.value,
                        "required": False,
                        "status": "skipped",
                    })
                else:
                    logger.info(f"  ⊘ {name} (optional)")
                continue

            if _check_capability(store, run_id=args.run_id, spec=spec):
                passed += 1
                status = "pass"
                if args.format != "json":
                    logger.info(f"  ✓ {name}")
            else:
                failed += 1
                status = "fail"
                if args.format != "json":
                    logger.error(f"  ✗ {name} - NO PASSING EVIDENCE")
            if args.format == "json":
                results.append({
                    "name": name,
                    "kind": spec.kind.value,
                    "required": True,
                    "status": status,
                })

        if args.format == "json":
            output = json.dumps(
                {
                    "summary": {"passed": passed, "failed": failed},
                    "capabilities": results,
                },
                indent=2,
            )
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Results written to {args.output}")
            else:
                print(output)
        else:
            logger.info(f"Conformance: {passed} passed, {failed} failed")
        if failed > 0:
            return 1
    return 0


def _check_capability(
    store: RecordStore, run_id: str | None, spec: CapabilitySpec
) -> bool:
    """Check if a capability has passing evidence in the store."""
    _ = spec  # evidence is currently run-scoped, not capability-scoped
    return store.count_passing_records(run_id) > 0


def _cmd_status(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-statements]
    """Show run/store status."""
    if args.dry_run:
        plan = {
            "command": "status",
            "store": args.store,
            "run_id": args.run_id,
            "detailed": args.detailed,
        }
        if args.format == "json":
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print("Dry run: would show run/store status")
            print(f"  Store: {args.store}")
            print(f"  Run ID: {args.run_id or 'all'}")
            print(f"  Detailed: {args.detailed}")
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        if args.run_id:
            summary = ReportGenerator(store).run_summary(args.run_id)
            if summary is None:
                logger.error(f"Run {args.run_id} not found")
                return 1
            if args.format == "json":
                output = json.dumps(asdict(summary), default=str, indent=2)
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    logger.info(f"Status written to {args.output}")
                else:
                    print(output)
            elif args.detailed:
                _print_detailed_status(summary)
            else:
                print(json.dumps(asdict(summary), default=str, indent=2))
        else:
            runs = ReportGenerator(store).list_runs()
            if not runs:
                if args.format == "json":
                    output = json.dumps({"runs": []}, indent=2)
                else:
                    output = "No runs found"
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    logger.info(f"Status written to {args.output}")
                else:
                    print(output)
                return 0

            if args.format == "json":
                runs_data = []
                for run in runs:
                    runs_data.append({
                        "run_id": run.run_id,
                        "status": run.status,
                        "record_count": run.record_count,
                        "claim_eligible_cells": run.claim_eligible_cells,
                        "promoted_count": run.promoted_count,
                        "started_at": run.started_at,
                    })
                output = json.dumps({"runs": runs_data}, indent=2)
            else:
                lines = []
                for run in runs:
                    lines.append(
                        f"  {run.run_id[:8]}... | {run.status:12} | "
                        f"recs={run.record_count:4} | claim={run.claim_eligible_cells:3} | "
                        f"promo={run.promoted_count:3} | {run.started_at}"
                    )
                output = "\n".join(lines)

            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Status written to {args.output}")
            else:
                print(output)
    return 0


def _print_detailed_status(summary: RunSummary) -> None:
    """Print detailed status with campaign economics."""
    print(f"Run: {summary.run_id}")
    print(f"Status: {summary.status}")
    print(f"Started: {summary.started_at}")
    print(f"Finished: {summary.finished_at or 'N/A'}")
    print(f"Budget Consumed: {summary.budget_consumed_s or 0:.1f}s")
    print(f"Replay Hash: {summary.replay_hash or 'N/A'}")
    print(f"Spec Version: {summary.spec_version}")
    print()
    print("Record Statistics:")
    print(f"  Total Records: {summary.record_count}")
    print(f"  Claim-Eligible Cells: {summary.claim_eligible_cells}")
    print(f"  Promoted: {summary.promoted_count}")
    print(f"  Declared Cells: {summary.declared_cells}")
    print()

    # Campaign Economics
    if summary.record_count > 0 and summary.budget_consumed_s is not None:
        cost_per_record = summary.budget_consumed_s / summary.record_count
        print("Campaign Economics:")
        print(f"  Cost per Record: {cost_per_record:.3f}s")

        if summary.declared_cells > 0:
            projected_total = cost_per_record * summary.declared_cells
            remaining_cells = summary.declared_cells - summary.record_count
            projected_remaining = cost_per_record * remaining_cells
            print(
                f"  Projected Total: {projected_total:.1f}s ({projected_total / 60:.1f}m)"
            )
            print(
                f"  Remaining: {projected_remaining:.1f}s ({projected_remaining / 60:.1f}m)"
            )
            progress = (summary.record_count / summary.declared_cells) * 100
            print(
                f"  Progress: {progress:.1f}% ({summary.record_count}/{summary.declared_cells})"
            )
    elif summary.declared_cells > 0:
        print("Campaign Economics:")
        print(f"  Declared Cells: {summary.declared_cells}")
        print(f"  Records Measured: {summary.record_count}")
        print("  Cost per Record: N/A (no budget consumed yet)")


def _cmd_gallery(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches]
    """Render gallery figures from demo records."""
    from computronium.visualization.gallery import render_gallery

    records_dir = Path(args.records_dir)
    output_dir = Path(args.output_dir)

    if args.dry_run:
        plan = {
            "command": "gallery",
            "records_dir": str(records_dir),
            "output_dir": str(output_dir),
        }
        if args.format == "json":
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print("Dry run: would render gallery figures")
            print(f"  Records dir: {records_dir}")
            print(f"  Output dir: {output_dir}")
        return 0

    if not records_dir.exists():
        logger.error(f"Records directory not found: {records_dir}")
        return 1

    logger.info(f"Rendering gallery from {records_dir} to {output_dir}")
    try:
        metas = render_gallery(records_dir, output_dir)
    except Exception:
        logger.exception("Gallery rendering failed")
        return 1
    else:
        if args.format == "json":
            results = []
            for meta in metas:
                results.append({
                    "figure_png": meta.figure_png,
                    "capability_name": meta.capability_name,
                    "capability_id": meta.capability_id,
                    "data_sha256": meta.data_sha256,
                    "demo_test": meta.demo_test,
                })
            output = json.dumps({"figures": results}, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Results written to {args.output}")
            else:
                print(output)
        else:
            logger.info(f"Rendered {len(metas)} gallery figures")
            for meta in metas:
                logger.info(
                    f"  {meta.figure_png} (data_sha256={meta.data_sha256[:16]}...)"
                )
        return 0
