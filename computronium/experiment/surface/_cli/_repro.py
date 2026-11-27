"""The surface CLI's reproducibility and power-analysis commands."""

from __future__ import annotations

import json
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- controlled docker call
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.surface.report import (
    ReportGenerator,
    export_to_json,
)

from ._commands import _generate_dockerfile
from ._execution import _open_store

if TYPE_CHECKING:
    import argparse

    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.run_spec import (
        RunSpec,
    )

logger = get_logger()

# Host and device measurements are outcomes, not identities (TODO107 D8): a
# replay on another host, or on CPU for a CUDA run, cannot reproduce RSS,
# walltime, latency, or a device-derived energy. They stay out of the default
# diff; naming one in --metrics opts back in.
_HOST_METRICS = frozenset({
    "cpu_rss_mb",
    "memory_usage",
    "memory_mb",
    "latency_ms",
    "walltime_s",
    "training_time",
    "energy_per_step",
    "energy_per_mac",
    "energy_efficiency",
    "energy_per_batch",
    "energy_per_sample",
})


def _comparable_metrics(payload: dict) -> list[str]:
    """The payload's numeric metrics a replay can reproduce."""
    return [
        k
        for k, v in payload.items()
        if isinstance(v, int | float) and k not in _HOST_METRICS
    ]


def _measurement_identity(record: Record) -> tuple[str, str, int]:
    """The replay's comparison key: the same cell, task, and seed.

    A ``cell_key`` collapses seeds *and* tasks, and one run's schedule may
    span several tasks. The replay's changed device/determinism stay out: they
    change the ``measurement_key``, not the measurement.
    """
    return (record.cell_key, record.schedule.task_id, record.schedule.seed)


def _replay_spec(spec: RunSpec, *, seeds: int | None, device: str) -> RunSpec:
    """The declaration a replay runs: the original's, with determinism forced.

    ``cell_workers`` is not an argument: it is the environment the record
    declares, and a replay at another ceiling compares two environments
    (TODO107 W33).
    """
    return spec.model_copy(
        update={
            "deterministic": True,
            **({"n_seeds": seeds} if seeds is not None else {}),
            **({"device": device} if device != "auto" else {}),
        }
    )


def _cmd_repro_docker(  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-statements]
    store: RecordStore,
    run_id: str,
    repro_spec: RunSpec,
    args: argparse.Namespace,
) -> int:
    """Run reproduction in a Docker container for full environment isolation."""
    import subprocess  # ruff: ignore[suspicious-subprocess-import] -- controlled docker call
    import tempfile
    from pathlib import Path

    logger.info(f"Building Docker image for reproduction of run {run_id}")

    # Create temporary directory for Docker build context
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # Export run data
        export_path = tmpdir_path / "export.json"
        export_to_json(store, export_path, run_id)

        # Write repro spec
        repro_spec_file = tmpdir_path / "repro_spec.json"
        repro_spec_file.write_text(json.dumps(repro_spec.to_dict(), indent=2))

        # Generate Dockerfile
        dockerfile_path = tmpdir_path / "Dockerfile"
        _generate_dockerfile(store, run_id, str(tmpdir_path / "export"))

        # Copy the generated Dockerfile to the right location
        generated_dockerfile = Path("export.Dockerfile")
        if generated_dockerfile.exists():
            import shutil

            shutil.copy(generated_dockerfile, dockerfile_path)
            generated_dockerfile.unlink()
        else:
            # Fallback: generate inline
            _generate_dockerfile(store, run_id, str(tmpdir_path / "export"))
            if Path("export.Dockerfile").exists():
                import shutil

                shutil.copy("export.Dockerfile", dockerfile_path)
                Path("export.Dockerfile").unlink()

        # Build Docker image
        image_name = f"computronium-repro-{run_id[:8]}"
        build_result = subprocess.run(  # ruff: ignore[subprocess-run-without-check, subprocess-without-shell-equals-true]
            ["docker", "build", "-t", image_name, str(tmpdir_path)],  # ruff: ignore[start-process-with-partial-path]
            capture_output=True,
            text=True,
            timeout=600,
        )
        if build_result.returncode != 0:
            logger.error(f"Docker build failed: {build_result.stderr}")
            return 1

        logger.info(f"Docker image built: {image_name}")

        # Run reproduction in Docker container
        repro_store_path = "/workspace/repro.duckdb"
        repro_spec_path = "/workspace/repro_spec.json"

        run_result = subprocess.run(  # ruff: ignore[subprocess-run-without-check, subprocess-without-shell-equals-true]
            [  # ruff: ignore[start-process-with-partial-path]
                "docker",
                "run",
                "--rm",
                "--gpus",
                "all" if repro_spec.device == "cuda" else "none",
                "-v",
                f"{tmpdir_path}:/workspace",
                image_name,
                "python",
                "-m",
                "computronium.experiment.surface.cli",
                "run",
                "--spec",
                repro_spec_path,
                "--store",
                repro_store_path,
            ],
            capture_output=True,
            text=True,
            timeout=3600,
        )

        if run_result.returncode != 0:
            logger.error(f"Docker reproduction failed: {run_result.stderr}")
            return 1

        # Copy results back
        repro_store_local = tmpdir_path / "repro.duckdb"
        # The store is already in the mounted volume

        # Compare metrics
        repro_store_obj = RecordStore(
            StoreConfig(path=repro_store_local, read_only=True)
        )
        with repro_store_obj:
            repro_run_id = repro_store_obj.latest_run_id()
            if repro_run_id is None:
                logger.error("Repro run produced no run ID")
                return 1

            generator = ReportGenerator(store)
            repro_generator = ReportGenerator(repro_store_obj)

            orig_records = generator.claim_eligible_records(run_id)
            repro_records = repro_generator.claim_eligible_records(repro_run_id)

            if not orig_records or not repro_records:
                logger.warning("No claim-eligible records for comparison")
                orig_records = generator._store.query_records(run_id=run_id)
                repro_records = repro_generator._store.query_records(
                    run_id=repro_run_id
                )

            # A cell_key collapses seeds and tasks; a measurement_key carries
            # the replay's changed device/determinism. Compare the same cell,
            # task, and seed, not the schedule's environment flags.
            orig_by_measurement = {_measurement_identity(r): r for r in orig_records}
            repro_by_measurement = {_measurement_identity(r): r for r in repro_records}

            common_measurements = set(orig_by_measurement) & set(repro_by_measurement)
            if not common_measurements:
                logger.error("No matching cells between original and reproduction")
                return 1

            metrics_to_check = (
                [m.strip() for m in args.metrics.split(",")] if args.metrics else None
            )

            mismatches = []
            for measurement_key in sorted(common_measurements):
                orig_r = orig_by_measurement[measurement_key]
                repro_r = repro_by_measurement[measurement_key]
                orig_payload = orig_r.payload
                repro_payload = repro_r.payload

                check_metrics = metrics_to_check or _comparable_metrics(orig_payload)

                for metric in check_metrics:
                    if metric not in orig_payload or metric not in repro_payload:
                        continue
                    orig_val = orig_payload[metric]
                    repro_val = repro_payload[metric]
                    if isinstance(orig_val, int | float) and isinstance(
                        repro_val, int | float
                    ):
                        diff = abs(float(orig_val) - float(repro_val))
                        if diff > args.tolerance:
                            mismatches.append({
                                "measurement_key": orig_r.measurement_key,
                                "task": orig_r.schedule.task_id,
                                "metric": metric,
                                "original": orig_val,
                                "reproduction": repro_val,
                                "diff": diff,
                            })

            output_data = {
                "original_run_id": run_id,
                "reproduction_run_id": repro_run_id,
                "tolerance": args.tolerance,
                "cells_compared": len(common_measurements),
                "metrics_checked": metrics_to_check or "all",
                "mismatches": mismatches,
                "passed": len(mismatches) == 0,
                "docker": True,
            }

            if args.format == "json":
                output = json.dumps(output_data, indent=2, default=str)
            elif mismatches:
                lines = [
                    f"REPRO FAILED: {len(mismatches)} mismatches > {args.tolerance}"
                ]
                for m in mismatches[:10]:
                    lines.append(
                        f"  {m['measurement_key'][:16]} {m['metric']}: {m['original']} vs {m['reproduction']} (diff={m['diff']})"
                    )
                output = "\n".join(lines)
            else:
                output = f"REPRO PASSED: {len(common_measurements)} cells match within {args.tolerance}"

            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Repro result written to {args.output}")
            else:
                print(output)

            return 0 if output_data["passed"] else 1


def _cmd_repro(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-return-statements, too-many-statements]
    """Replay a run and verify bitwise reproducibility."""
    import tempfile

    store = _open_store(args.store)
    if store is None:
        return 1
    with store:
        generator = ReportGenerator(store)
        run_info = generator.run_summary(args.run_id)
        if run_info is None:
            logger.error(f"Run {args.run_id} not found")
            return 1

        spec = run_info.spec
        if spec is None:
            logger.error(f"Run {args.run_id} has no spec")
            return 1

        # The replay's environment is the record's, not this host's: the cell
        # ceiling is part of it (TODO107 W33).
        if spec.cell_workers is None:
            logger.warning(
                "Run %s declares no cell ceiling; the replay uses this host's "
                "default and may not reproduce",
                args.run_id,
            )
        repro_spec = _replay_spec(spec, seeds=args.seeds, device=args.device)

        if args.docker:
            return _cmd_repro_docker(store, args.run_id, repro_spec, args)

        # Run reproduction in a temp store
        with tempfile.TemporaryDirectory() as tmpdir:
            repro_store = Path(tmpdir) / "repro.duckdb"
            repro_spec_file = Path(tmpdir) / "repro_spec.json"
            repro_spec_file.write_text(json.dumps(repro_spec.to_dict(), indent=2))
            # Concurrency is part of the environment, and the spec file
            # declares it: the replay runs the record's ceiling (TODO107 W33).

            # Execute the spec
            result = subprocess.run(  # ruff: ignore[subprocess-run-without-check, subprocess-without-shell-equals-true]
                [
                    sys.executable,
                    "-m",
                    "computronium.experiment.surface.cli",
                    "run",
                    "--spec",
                    str(repro_spec_file),
                    "--store",
                    str(repro_store),
                    "--dry-run",  # Just validate the spec first
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                logger.error(f"Repro dry-run failed: {result.stderr}")
                return 1

            # Now run for real
            result = subprocess.run(  # ruff: ignore[subprocess-run-without-check, subprocess-without-shell-equals-true]
                [
                    sys.executable,
                    "-m",
                    "computronium.experiment.surface.cli",
                    "run",
                    "--spec",
                    str(repro_spec_file),
                    "--store",
                    str(repro_store),
                ],
                capture_output=True,
                text=True,
                timeout=3600,
            )
            if result.returncode != 0:
                logger.error(f"Repro run failed: {result.stderr}")
                return 1

            # Compare metrics
            repro_store_obj = RecordStore(StoreConfig(path=repro_store, read_only=True))
            with repro_store_obj:
                repro_run_id = repro_store_obj.latest_run_id()
                if repro_run_id is None:
                    logger.error("Repro run produced no run ID")
                    return 1

                repro_generator = ReportGenerator(repro_store_obj)
                orig_records = generator.claim_eligible_records(args.run_id)
                repro_records = repro_generator.claim_eligible_records(repro_run_id)

                if not orig_records or not repro_records:
                    logger.warning("No claim-eligible records for comparison")
                    # Fall back to all records
                    orig_records = generator._store.query_records(run_id=args.run_id)
                    repro_records = repro_generator._store.query_records(
                        run_id=repro_run_id
                    )

                # A cell_key collapses seeds and tasks; a measurement_key carries
                # the replay's changed device/determinism. Compare the same cell,
                # task, and seed, not the schedule's environment flags.
                orig_by_measurement = {
                    _measurement_identity(r): r for r in orig_records
                }
                repro_by_measurement = {
                    _measurement_identity(r): r for r in repro_records
                }

                common_measurements = set(orig_by_measurement) & set(
                    repro_by_measurement
                )
                if not common_measurements:
                    logger.error("No matching cells between original and reproduction")
                    return 1

                metrics_to_check = (
                    [m.strip() for m in args.metrics.split(",")]
                    if args.metrics
                    else None
                )

                mismatches = []
                for measurement_key in sorted(common_measurements):
                    orig_r = orig_by_measurement[measurement_key]
                    repro_r = repro_by_measurement[measurement_key]
                    orig_payload = orig_r.payload
                    repro_payload = repro_r.payload

                    check_metrics = metrics_to_check or _comparable_metrics(
                        orig_payload
                    )

                    for metric in check_metrics:
                        if metric not in orig_payload or metric not in repro_payload:
                            continue
                        orig_val = orig_payload[metric]
                        repro_val = repro_payload[metric]
                        if isinstance(orig_val, int | float) and isinstance(
                            repro_val, int | float
                        ):
                            diff = abs(float(orig_val) - float(repro_val))
                            if diff > args.tolerance:
                                mismatches.append({
                                    "measurement_key": orig_r.measurement_key,
                                    "task": orig_r.schedule.task_id,
                                    "metric": metric,
                                    "original": orig_val,
                                    "reproduction": repro_val,
                                    "diff": diff,
                                })

                output_data = {
                    "original_run_id": args.run_id,
                    "reproduction_run_id": repro_run_id,
                    "tolerance": args.tolerance,
                    "cells_compared": len(common_measurements),
                    "metrics_checked": metrics_to_check or "all",
                    "mismatches": mismatches,
                    "passed": len(mismatches) == 0,
                }

                if args.format == "json":
                    output = json.dumps(output_data, indent=2, default=str)
                elif mismatches:
                    lines = [
                        f"REPRO FAILED: {len(mismatches)} mismatches > {args.tolerance}"
                    ]
                    for m in mismatches[:10]:
                        lines.append(
                            f"  {m['measurement_key'][:16]} {m['metric']}: {m['original']} vs {m['reproduction']} (diff={m['diff']})"
                        )
                    output = "\n".join(lines)
                else:
                    output = f"REPRO PASSED: {len(common_measurements)} cells match within {args.tolerance}"

                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                    logger.info(f"Repro result written to {args.output}")
                else:
                    print(output)

                return 0 if output_data["passed"] else 1


def _cmd_power_analysis(args: argparse.Namespace) -> int:
    """Compute statistical power for experiment design."""
    from computronium.core.statistics import power_for_two_sample

    if args.solve_for == "power":
        if args.n_per_group is None:
            logger.error("--n-per-group is required when --solve-for power")
            return 1
        power = power_for_two_sample(args.effect_size, args.n_per_group, args.alpha)
        result = {
            "effect_size": args.effect_size,
            "n_per_group": args.n_per_group,
            "alpha": args.alpha,
            "power": power,
            "solved_for": "power",
        }
        if args.format == "text":
            output = (
                f"Power Analysis\n"
                f"  Effect size (Cohen's d): {args.effect_size}\n"
                f"  Sample size per group: {args.n_per_group}\n"
                f"  Alpha: {args.alpha}\n"
                f"  Power: {power:.4f}\n"
            )
        else:
            output = json.dumps(result, indent=2)
    else:  # solve for n
        # Binary search for required n
        target = args.target_power
        lo, hi = 2, 10000
        best_n = hi
        while lo <= hi:
            mid = (lo + hi) // 2
            p = power_for_two_sample(args.effect_size, mid, args.alpha)
            if p >= target:
                best_n = mid
                hi = mid - 1
            else:
                lo = mid + 1
        result = {
            "effect_size": args.effect_size,
            "alpha": args.alpha,
            "target_power": args.target_power,
            "required_n_per_group": best_n,
            "achieved_power": power_for_two_sample(
                args.effect_size, best_n, args.alpha
            ),
            "solved_for": "n",
        }
        if args.format == "text":
            output = (
                f"Power Analysis (solve for n)\n"
                f"  Effect size (Cohen's d): {args.effect_size}\n"
                f"  Alpha: {args.alpha}\n"
                f"  Target power: {args.target_power}\n"
                f"  Required n per group: {best_n}\n"
                f"  Achieved power: {result['achieved_power']:.4f}\n"
            )
        else:
            output = json.dumps(result, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        logger.info(f"Power analysis written to {args.output}")
    else:
        print(output)
    return 0
