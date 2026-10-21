"""The surface CLI's dataset, environment, dashboard, and quality commands."""

from __future__ import annotations

import asyncio
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig

if TYPE_CHECKING:
    import argparse

logger = get_logger()


def _cmd_dashboard(args: argparse.Namespace) -> int:
    """Launch live monitoring web dashboard (Phase E5) or console dashboard."""

    if args.console:
        from computronium.experiment.execution.dashboard.console import (
            run_console_dashboard,
        )

        logger.info("Starting console dashboard")
        logger.info(f"Store: {args.store}")
        logger.info(f"Update interval: {args.update_interval}s")

        # Get campaign queue if available (for queue monitoring)
        campaign_queue = None
        try:
            from computronium.experiment.execution.campaign_queue import (
                get_campaign_queue,
            )

            campaign_queue = get_campaign_queue()
        except Exception as exc:
            logger.debug("campaign queue unavailable: %s", exc)

        try:
            asyncio.run(
                run_console_dashboard(
                    store_path=args.store,
                    campaign_queue=campaign_queue,
                    update_interval=args.update_interval,
                )
            )
        except KeyboardInterrupt:
            logger.info("Console dashboard stopped by user")
        except Exception as e:
            logger.exception("Console dashboard failed")
            print(f"Console dashboard error: {e}", file=sys.stderr)
            return 1
        return 0

    # Web dashboard (default)
    from computronium.experiment.execution.dashboard.web import run_dashboard

    logger.info(f"Starting dashboard on {args.host}:{args.port}")
    logger.info(f"Store: {args.store}")

    # Get campaign queue if available (for queue monitoring)
    campaign_queue = None
    try:
        from computronium.experiment.execution.campaign_queue import get_campaign_queue

        campaign_queue = get_campaign_queue()
    except Exception as exc:
        logger.debug("campaign queue unavailable: %s", exc)

    try:
        asyncio.run(
            run_dashboard(
                host=args.host,
                port=args.port,
                store_path=args.store,
                campaign_queue=campaign_queue,
            )
        )
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.exception("Dashboard failed")
        print(f"Dashboard error: {e}", file=sys.stderr)
        return 1

    return 0


def _cmd_dataset(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-return-statements, too-many-statements]
    """Dataset registry commands (Phase E6)."""
    from pathlib import Path

    from computronium.experiment.data.dataset_registry import (
        DatasetRegistration,
        DatasetRegistry,
    )

    store = RecordStore(StoreConfig(path=Path(args.store)))
    if store is None:
        return 1

    # Initialize dataset registry
    with store:
        conn = store._conn
        write_lock = store._write_lock
        data_root = Path(args.data_root)
        registry = DatasetRegistry(conn, write_lock, data_root)

        cmd = args.dataset_command

        if cmd == "register":
            tags = {}
            if args.tags:
                for tag in args.tags.split(","):
                    if "=" in tag:
                        k, v = tag.split("=", 1)
                        tags[k] = v

            registration = DatasetRegistration(
                dataset_id=args.dataset_id,
                version=args.version,
                path=args.path,
                description=args.description,
                tags=tags,
                source_url=args.source_url,
                source_hash=args.source_hash,
            )

            version = registry.register(registration)
            print(f"Registered dataset {version.dataset_id} version {version.version}")
            print(f"  Digest: {version.digest}")
            print(f"  Splits: {list(version.splits.keys())}")
            return 0

        elif cmd == "get":
            version_str = args.version or "latest"
            if version_str == "latest":
                version = registry.get_latest(args.dataset_id)
            else:
                version = registry.get(args.dataset_id, version_str)

            if not version:
                print(f"Dataset {args.dataset_id} version {version_str} not found")
                return 1

            if args.format == "json":
                import json

                print(
                    json.dumps(
                        {
                            "dataset_id": version.dataset_id,
                            "version": version.version,
                            "digest": version.digest,
                            "created_at": version.created_at,
                            "description": version.description,
                            "splits": {
                                k: {
                                    "name": v.name,
                                    "path": v.path,
                                    "hash": v.hash,
                                    "size_bytes": v.size_bytes,
                                    "num_samples": v.num_samples,
                                    "metadata": v.metadata,
                                }
                                for k, v in version.splits.items()
                            },
                            "tags": version.tags,
                            "metadata": version.metadata,
                            "source_url": version.source_url,
                            "source_hash": version.source_hash,
                        },
                        indent=2,
                    )
                )
            else:
                print(f"Dataset: {version.dataset_id}")
                print(f"  Version: {version.version}")
                print(f"  Digest: {version.digest}")
                print(f"  Created: {version.created_at}")
                print(f"  Description: {version.description}")
                print("  Splits:")
                for k, v in version.splits.items():
                    print(
                        f"    {k}: {v.num_samples} samples, {v.size_bytes} bytes, hash={v.hash[:12]}..."
                    )
                if version.tags:
                    print(f"  Tags: {version.tags}")
            return 0

        elif cmd == "list":
            if args.dataset_id:
                versions = registry.list_versions(args.dataset_id)
            else:
                tag_filter = {}
                if args.tag:
                    k, v = args.tag.split("=", 1)
                    tag_filter[k] = v
                versions = registry.list_datasets(tag_filter=tag_filter)

            if args.format == "json":
                import json

                print(
                    json.dumps(
                        [
                            {
                                "dataset_id": v.dataset_id,
                                "version": v.version,
                                "digest": v.digest,
                                "created_at": v.created_at,
                                "splits": list(v.splits.keys()),
                            }
                            for v in versions
                        ],
                        indent=2,
                    )
                )
            else:
                for v in versions:
                    print(
                        f"{v.dataset_id}@{v.version} (digest: {v.digest[:12]}..., splits: {list(v.splits.keys())})"
                    )
            return 0

        elif cmd == "verify":
            result = registry.verify_integrity(args.dataset_id, args.version)

            if args.format == "json":
                import json

                print(json.dumps(result, indent=2))
            else:
                print(f"Dataset: {args.dataset_id}@{args.version}")
                print(f"  Overall valid: {result['valid']}")
                if "overall_digest" in result:
                    od = result["overall_digest"]
                    print(
                        f"  Overall digest: expected={od['expected'][:12]}... actual={od['actual'][:12]}... valid={od['valid']}"
                    )
                if "splits" in result:
                    print("  Splits:")
                    for split_name, split_result in result["splits"].items():
                        if split_result.get("valid"):
                            print(
                                f"    {split_name}: VALID (hash={split_result['actual_hash'][:12]}...)"
                            )
                        else:
                            print(
                                f"    {split_name}: INVALID - {split_result.get('error', 'hash mismatch')}"
                            )
            return 0 if result.get("valid") else 1

        elif cmd == "export":
            output_path = Path(args.output)
            registry.export_metadata(args.dataset_id, args.version, output_path)
            print(f"Exported metadata to {output_path}")
            return 0

    return 2


def _cmd_environment(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-return-statements, too-many-statements]
    """Environment snapshot commands (Phase E7)."""
    from pathlib import Path

    from computronium.experiment.environment.snapshots import (
        ContainerManager,
        create_environment_snapshot,
        verify_environment,
    )

    cmd = args.env_command

    if cmd == "capture":
        snapshot = create_environment_snapshot(
            output_path=Path(args.output),
            include_env_vars=not args.no_env_vars,
            include_git=not args.no_git,
            include_container=bool(args.container_image),
            container_image=args.container_image,
        )
        print(f"Environment snapshot saved to {args.output}")
        print(f"  Snapshot ID: {snapshot.snapshot_id}")
        print(f"  Python: {snapshot.python.python_version}")
        print(f"  Packages: {len(snapshot.python.pip_packages)}")
        print(f"  Git: {snapshot.git.commit_sha[:12] if snapshot.git else 'N/A'}")
        return 0

    elif cmd == "verify":
        result = verify_environment(Path(args.snapshot))

        if args.format == "json":
            import json

            print(json.dumps(result, indent=2))
        else:
            print(
                f"Environment verification: {'MATCH' if result['matches'] else 'MISMATCH'}"
            )
            print(f"  Expected snapshot: {result['expected_snapshot_id']}")
            print(f"  Actual snapshot: {result['actual_snapshot_id']}")
            if result["mismatches"]:
                print("  Mismatches:")
                for m in result["mismatches"]:
                    if m["type"] == "package":
                        print(
                            f"    Package {m['package']}: expected {m['expected']}, got {m['actual']}"
                        )
                    elif m["type"] == "extra_package":
                        print(f"    Extra package: {m['package']}=={m['version']}")
                    elif m["type"] == "python_version":
                        print(
                            f"    Python version: expected {m['expected']}, got {m['actual']}"
                        )
                    elif m["type"] == "uv_lock":
                        print("    uv.lock hash mismatch")
                    elif m["type"] == "git_commit":
                        print(
                            f"    Git commit: expected {m['expected'][:12]}, got {m['actual'][:12]}"
                        )
            return 0 if result["matches"] else 1

    elif cmd == "docker-build":
        if not shutil.which("docker"):
            print("Docker not found in PATH", file=sys.stderr)
            return 1

        manager = ContainerManager()
        if not manager.is_available():
            print("Docker daemon not available", file=sys.stderr)
            return 1

        build_args = {}
        if args.build_arg:
            for arg in args.build_arg:
                if "=" in arg:
                    k, v = arg.split("=", 1)
                    build_args[k] = v

        container_env = manager.build_image(
            dockerfile_path=args.dockerfile,
            image_name=args.image_name,
            build_args=build_args,
            tag=args.tag,
        )

        if container_env:
            print(f"Built Docker image: {container_env.image_name}")
            print(f"  Image ID: {container_env.image_id}")
            print(f"  Base image: {container_env.base_image}")
            return 0
        else:
            print("Failed to build Docker image", file=sys.stderr)
            return 1

    elif cmd == "docker-save":
        manager = ContainerManager()
        if not manager.is_available():
            print("Docker daemon not available", file=sys.stderr)
            return 1

        try:
            output_path = manager.save_image(args.image_name, Path(args.output))
        except Exception as e:
            print(f"Failed to save Docker image: {e}", file=sys.stderr)
            return 1
        else:
            print(f"Saved Docker image to {output_path}")
            return 0

    elif cmd == "docker-load":
        manager = ContainerManager()
        if not manager.is_available():
            print("Docker daemon not available", file=sys.stderr)
            return 1

        image_id = manager.load_image(Path(args.input))
        if image_id:
            print(f"Loaded Docker image: {image_id}")
            return 0
        else:
            print("Failed to load Docker image", file=sys.stderr)
            return 1

    return 2


def _cmd_quality(args: argparse.Namespace) -> int:
    """Quality gates commands (Phase F1)."""
    from pathlib import Path

    from computronium.experiment.quality.gates import (
        DataIntegrityGate,
        ReportQualityGate,
        run_all_quality_gates,
    )

    cmd = args.quality_command

    if cmd == "check-report":
        store = RecordStore(StoreConfig(path=Path(args.store)))
        if store is None:
            return 1

        with store:
            # Build report context from store
            generator = __import__(
                "computronium.experiment.templates.report.generator",
                fromlist=["JinjaReportGenerator"],
            ).JinjaReportGenerator()
            context = generator.build_context_from_store(store, args.run_id)

            gate = ReportQualityGate()
            result = gate.validate(context)

        _output_result(result, args)
        return 0 if result.passed else 1

    elif cmd == "check-store":
        gate = DataIntegrityGate(Path(args.store))
        result = gate.validate()

        _output_result(result, args)
        return 0 if result.passed else 1

    elif cmd == "check-all":
        store = RecordStore(StoreConfig(path=Path(args.store)))
        if store is None:
            return 1

        with store:
            generator = __import__(
                "computronium.experiment.templates.report.generator",
                fromlist=["JinjaReportGenerator"],
            ).JinjaReportGenerator()
            context = generator.build_context_from_store(store, args.run_id)

            result = run_all_quality_gates(context, Path(args.store))

        _output_result(result, args)
        return 0 if result.passed else 1

    return 2


def _output_result(result, args):
    """Output quality gate result."""
    if args.format == "json":
        output = result.to_json()
    else:
        output = f"Quality Gate: {'PASSED' if result.passed else 'FAILED'}\n"
        output += f"Timestamp: {result.timestamp}\n"
        output += f"Summary: {result.summary['errors']} errors, {result.summary['warnings']} warnings, {result.summary['info']} info\n\n"
        for issue in result.issues:
            output += f"[{issue.severity.upper()}] {issue.category}: {issue.message}\n"
            if issue.location:
                output += f"  Location: {issue.location}\n"
            if issue.suggestion:
                output += f"  Suggestion: {issue.suggestion}\n"
            output += "\n"

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Results written to {args.output}")
    else:
        print(output)
