"""The surface CLI's defect, frontier, and hypothesis-campaign commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from computronium.core.logging import get_logger
from computronium.experiment.evidence.store import RecordStore, StoreConfig
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.run_spec import (
    AxisSelection,
    RunSpec,
)

from ._execution import _open_store, execute_spec

if TYPE_CHECKING:
    import argparse

logger = get_logger()


def _cmd_defect(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-return-statements, too-many-statements]
    """Defect constraint registry commands (TODO63 Phase 3)."""
    import json
    from datetime import datetime
    from pathlib import Path

    from computronium.experiment.legality.engine import LegalityEngine
    from computronium.experiment.registry.defect_registry import create_defect_registry

    # Ensure registries are seeded
    from computronium.experiment.schema import _ensure_registries_seeded

    _ensure_registries_seeded()

    if args.defect_command == "list":
        engine = LegalityEngine()
        defect_registry = create_defect_registry(engine, Path(args.state_dir))
        constraints = defect_registry.list_constraints(
            include_revoked=args.include_revoked
        )

        if args.format == "json":
            output = json.dumps(
                [c.to_dict() for c in constraints], indent=2, default=str
            )
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
            else:
                print(output)
        else:
            print("Active Defect Constraints")
            print("=" * 70)
            if not constraints:
                print("  (none)")
            else:
                for c in constraints:
                    status = "REVOKED" if c.revoked else "ACTIVE"
                    print(
                        f"\n{c.constraint_id} [{status}]"
                        f"\n  Defect: {c.defect_cause} ({c.defect_class})"
                        f"\n  Cell: {c.cell_key[:16]}"
                        f"\n  Measurement: {c.measurement_key}"
                        f"\n  Origin: {c.constraint.origin.value}"
                        f"\n  Scope: {c.constraint.scope.value}"
                        f"\n  Enforcement: {c.constraint.enforcement.value}"
                        f"\n  Kind: {c.constraint.kind.value}"
                        f"\n  Description: {c.constraint.description}"
                        f"\n  Tags: {', '.join(c.constraint.tags)}"
                        f"\n  Author: {c.author}"
                        f"\n  Created: {datetime.fromtimestamp(c.created_at).isoformat()}"
                    )
                    if c.revoked and c.revoked_at is not None:
                        print(
                            f"  Revoked by: {c.revoked_by} at {datetime.fromtimestamp(c.revoked_at).isoformat()}"
                        )
        return 0

    elif args.defect_command == "cluster":
        store_path = Path(args.store)
        if not store_path.exists():
            print(f"Store not found: {store_path}")
            return 1

        with RecordStore(StoreConfig(path=store_path)) as store:
            from computronium.experiment.evidence.failure import (
                cluster_failures,
                detect_failure_patterns,
            )

            # Determine run_id
            run_id = args.run_id
            if run_id is None:
                run_id = store.latest_run_id()
                if run_id is None:
                    print("No runs found in store")
                    return 0

            all_records = list(store.query_records(run_id=run_id))
            failed_records = [
                r
                for r in all_records
                if r.status.gate_verdict.value == "FAIL"
                or r.status.cause.value != "unknown"
            ]

            if not failed_records:
                print(f"No failed records found for run {run_id[:12]}")
                return 0

            clusters = cluster_failures(
                failed_records, min_cluster_size=args.min_cluster_size
            )
            patterns = detect_failure_patterns(failed_records)

            if args.format == "json":
                output = json.dumps(
                    {
                        "run_id": run_id,
                        "total_failures": len(failed_records),
                        "clusters": [c.__dict__ for c in clusters],
                        "patterns": [p.__dict__ for p in patterns],
                    },
                    indent=2,
                    default=str,
                )
                if args.output:
                    Path(args.output).write_text(output, encoding="utf-8")
                else:
                    print(output)
            else:
                print(f"Failure Analysis for run {run_id[:12]}")
                print("=" * 70)
                print(f"Total failures: {len(failed_records)}")
                print(f"Clusters: {len(clusters)}")
                print(f"Patterns: {len(patterns)}")
                print()
                for cluster in clusters:
                    print(
                        f"Cluster {cluster.cluster_id}: {cluster.failure_cause.value}"
                        f" ({cluster.count} occurrences, severity={cluster.severity})"
                    )
                    print(
                        f"  Cells: {', '.join(c[:12] for c in cluster.cell_keys[:5])}"
                    )
                    if cluster.common_params:
                        print(f"  Common params: {cluster.common_params}")
                    print(f"  {cluster.description}")
                    print()
                for pattern in patterns:
                    print(
                        f"Pattern {pattern.pattern_id}: {pattern.name}"
                        f" (confidence={pattern.confidence:.2f}, freq={pattern.frequency})"
                    )
                    if pattern.suggested_fix:
                        print(f"  Suggested fix: {pattern.suggested_fix}")
                    print()
        return 0

    elif args.defect_command == "revoke":
        engine = LegalityEngine()
        defect_registry = create_defect_registry(engine, Path(args.state_dir))
        success = defect_registry.revoke(args.constraint_id)

        if args.format == "json":
            output = json.dumps(
                {"constraint_id": args.constraint_id, "revoked": success}, indent=2
            )
            print(output)
        elif success:
            print(f"Revoked constraint {args.constraint_id}")
        else:
            print(f"Constraint {args.constraint_id} not found")
            return 1
        return 0

    return 0


def _cmd_stability_plasticity(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-statements]
    """Generate and optionally run a stability-plasticity frontier campaign."""
    from computronium.experiment.schema.run_spec import (
        Domain,
        Scale,
    )

    # Parse sweep parameters (using valid hyperparameter names)
    rho_vals = tuple(float(x) for x in args.rho.split(","))
    feedback_scale_vals = tuple(float(x) for x in args.feedback_scale.split(","))
    precision_vals = tuple(args.precision.split(","))
    noise_level_vals = tuple(float(x) for x in args.noise_level.split(","))
    # Replace 0.0 with a small positive value for log scale
    noise_level_vals = tuple(max(v, 1e-6) for v in noise_level_vals)
    convergence_start_vals = tuple(int(x) for x in args.convergence_start.split(","))

    # Create axis selections - use CLI overrides or defaults
    def _parse_axis(arg_value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
        if arg_value is None:
            return default
        return tuple(x.strip() for x in arg_value.split(","))

    substrate_prims = _parse_axis(args.axis_substrate, ("digital",))
    geometry_prims = _parse_axis(args.axis_geometry, ("recurrent",))
    dynamics_prims = _parse_axis(args.axis_dynamics, ("energy_minimization",))
    plasticity_prims = _parse_axis(args.axis_plasticity, ("null",))
    credit_prims = _parse_axis(args.axis_credit, ("thermodynamic_contrast",))
    update_prims = _parse_axis(args.axis_update, ("euclidean",))

    # Calculate total cells (axis primitive combinations × hyperparameter sweep)
    axis_combinations = (
        len(substrate_prims)
        * len(geometry_prims)
        * len(dynamics_prims)
        * len(plasticity_prims)
        * len(credit_prims)
        * len(update_prims)
    )
    hyperparameter_combinations = (
        len(rho_vals)
        * len(feedback_scale_vals)
        * len(precision_vals)
        * len(noise_level_vals)
        * len(convergence_start_vals)
    )
    total_cells = axis_combinations * hyperparameter_combinations

    axes = (
        AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=substrate_prims),
        AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=geometry_prims),
        AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=dynamics_prims),
        AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=plasticity_prims),
        AxisSelection(axis=StructuralAxis.CREDIT, primitives=credit_prims),
        AxisSelection(axis=StructuralAxis.UPDATE, primitives=update_prims),
    )

    # Hyperparameters for the stability-plasticity sweep
    # Map to valid hyperparameter names from harvest
    def _make_domain(vals, scale=Scale.LINEAR, is_int=False):
        """Create Domain from values - categorical if single value, range otherwise."""
        if len(vals) == 1:
            # Keep native type for categorical domains
            return Domain(members=(vals[0],))
        if is_int:
            return Domain(lo=min(vals), hi=max(vals), scale=scale)
        return Domain(lo=min(vals), hi=max(vals), scale=scale)

    hyperparameters = {
        "rho": _make_domain(rho_vals, Scale.LOG),
        "feedback_scale": _make_domain(feedback_scale_vals, Scale.LOG),
        "precision": Domain(members=precision_vals),
        "noise_level": _make_domain(noise_level_vals, Scale.LOG),
        "convergence_start": _make_domain(
            convergence_start_vals, Scale.LINEAR, is_int=True
        ),
        # Constrain hidden_dim to respect param_budget for recurrent geometry
        # With param_budget=200000 and 25% tolerance, max params = 250000
        # For recurrent: 64*H + H + (L-1)*(H*H + H) + H*10 + 10
        # Max at L=4: 3*H^2 + 85*H + 10 <= 250000 => H <= ~270
        "hidden_dim": Domain(lo=32.0, hi=256.0, scale=Scale.LOG),
    }

    # Gate is a categorical sweep - we'll handle it via the grid
    # For now, we include it in operating_points for reference
    operating_points = {
        "rho_sweep": list(rho_vals),
        "feedback_scale_sweep": list(feedback_scale_vals),
        "precision_sweep": list(precision_vals),
        "noise_level_sweep": list(noise_level_vals),
        "convergence_start_sweep": list(convergence_start_vals),
    }

    # Axis-aligned objectives. The stability set is the campaign's subject:
    # rho, sigma_max and their ratio are the frontier's three axes, and
    # settle_steps is the horizon the step was measured against.
    axis_objectives = {
        "task": ("validation_accuracy",),
        "stability": (
            "spectral_radius",
            "max_singular_value",
            "nonnormality",
            "stability_margin",
            "lyapunov_exponent",
            "settle_steps",
        ),
        "cost": ("walltime_total", "param_count", "energy_per_step"),
    }

    # Create RunSpec. `objectives` is the union of the axis sets: the combined
    # study needs a direction per name, and the per-axis studies read the sets.
    objectives = tuple(
        dict.fromkeys(o for objs in axis_objectives.values() for o in objs)
    )

    spec = RunSpec(
        version=2,
        profile="stability-plasticity",
        task="digits",
        objectives=objectives,
        fidelity="L1",
        n_seeds=args.seeds,
        epochs=args.epochs,
        budget_seconds=args.budget_seconds,
        param_budget=500000,
        policy="model_based",
        axes=axes,
        hyperparameters=hyperparameters,
        operating_points=operating_points,
        axis_objectives=axis_objectives,
        deterministic=True,
        num_workers=0,
        sweep_steps=243,
    )

    # Dry run or run
    if args.dry_run:
        if args.format == "json":
            plan = {
                "command": "stability-plasticity",
                "store": args.store,
                "run_id": args.run_id,
                "rho": list(rho_vals),
                "feedback_scale": list(feedback_scale_vals),
                "precision": list(precision_vals),
                "noise_level": list(noise_level_vals),
                "convergence_start": list(convergence_start_vals),
                "seeds": args.seeds,
                "epochs": args.epochs,
                "budget_seconds": args.budget_seconds,
                "axes": {
                    "substrate": list(substrate_prims),
                    "geometry": list(geometry_prims),
                    "dynamics": list(dynamics_prims),
                    "plasticity": list(plasticity_prims),
                    "credit": list(credit_prims),
                    "update": list(update_prims),
                },
                "total_cells": total_cells,
                "objectives": list(objectives),
                "axis_objectives": axis_objectives,
            }
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print("Stability-Plasticity Campaign")
            print(f"  Rho (contraction): {rho_vals}")
            print(f"  Feedback scale (coupling): {feedback_scale_vals}")
            print(f"  Precision: {precision_vals}")
            print(f"  Noise level: {noise_level_vals}")
            print(f"  Convergence start (delay proxy): {convergence_start_vals}")
            print(
                f"  Axis primitives: substrate={substrate_prims}, geometry={geometry_prims}, "
                f"dynamics={dynamics_prims}, plasticity={plasticity_prims}, "
                f"credit={credit_prims}, update={update_prims}"
            )
            print(f"  Axis combinations: {axis_combinations}")
            print(f"  Hyperparameter combinations: {hyperparameter_combinations}")
            print(f"  Total coordinates: {total_cells}")
            print(f"  Seeds per coordinate: {args.seeds}")
            print(f"  Epochs: {args.epochs}")
            print(f"  Budget: {args.budget_seconds}s")
            from computronium.experiment.kernel.search_space import (
                iter_candidates,
                search_space_from_spec,
            )

            print("\nDry run - first 5 candidates:")
            search_space = search_space_from_spec(spec)
            for count, (coord, sched) in enumerate(iter_candidates(spec, search_space)):
                print(f"  {coord}")
                if count >= 4:
                    break
            print(f"... (total {total_cells} coordinates)")
        return 0

    if not args.run:
        if args.format == "json":
            plan = {
                "command": "stability-plasticity",
                "store": args.store,
                "run_id": args.run_id,
                "spec": spec.to_dict(),
            }
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Plan written to {args.output}")
            else:
                print(output)
        else:
            print("Stability-Plasticity Campaign")
            print(f"  Rho (contraction): {rho_vals}")
            print(f"  Feedback scale (coupling): {feedback_scale_vals}")
            print(f"  Precision: {precision_vals}")
            print(f"  Noise level: {noise_level_vals}")
            print(f"  Convergence start (delay proxy): {convergence_start_vals}")
            print(
                f"  Axis primitives: substrate={substrate_prims}, geometry={geometry_prims}, "
                f"dynamics={dynamics_prims}, plasticity={plasticity_prims}, "
                f"credit={credit_prims}, update={update_prims}"
            )
            print(f"  Axis combinations: {axis_combinations}")
            print(f"  Hyperparameter combinations: {hyperparameter_combinations}")
            print(f"  Total coordinates: {total_cells}")
            print(f"  Seeds per coordinate: {args.seeds}")
            print(f"  Epochs: {args.epochs}")
            print(f"  Budget: {args.budget_seconds}s")
            print("Spec generated. Use --run to execute or --dry-run to preview.")
            if args.output_spec:
                print(f"Spec written to {args.output_spec}")
        return 0

    # Run the campaign. Same executor every run uses, so the run row is closed,
    # maturity is settled, and --run-id resumes an interrupted campaign.
    print("Running campaign...")
    return execute_spec(spec, store_path=args.store, run_id=args.run_id)


def _cmd_frozen_theta_psi(args: argparse.Namespace) -> int:  # ruff: ignore[too-many-statements, too-many-locals, complex-structure, too-many-branches]
    """Run frozen-θ ψ benchmarks at scale (multi-substrate, multi-plasticity)."""
    import json
    from pathlib import Path

    from computronium.benchmarks.joint.structural_robustness import (
        run_structural_robustness_suite,
    )

    substrates = (
        tuple(args.substrates.split(","))
        if args.substrates
        else (
            "digital",
            "memristive",
            "neuromorphic",
            "photonic",
            "complex",
            "analog",
            "quantum",
        )
    )
    plasticity_types = (
        tuple(args.plasticity_types.split(","))
        if args.plasticity_types
        else ("null", "routing", "fast_weights", "substrate_coupled")
    )

    # Generate coordinates for all combinations
    coordinates = []
    neuromorphic_plasticity = {"null", "routing"}
    no_substrate_coupled = {"photonic", "quantum"}
    for substrate in substrates:
        for plasticity in plasticity_types:
            # Skip invalid combinations
            if (
                substrate == "neuromorphic"
                and plasticity not in neuromorphic_plasticity
            ):
                continue  # Neuromorphic only supports null and routing
            if substrate in no_substrate_coupled and plasticity == "substrate_coupled":
                continue  # Substrate coupled not implemented for these yet

            coord = f"{substrate}/{args.geometry}/{args.dynamics}/{plasticity}/{args.credit}/{args.update}"
            coordinates.append(coord)

    plan = {
        "command": "frozen-theta-psi",
        "store": args.store,
        "substrates": list(substrates),
        "plasticity_types": list(plasticity_types),
        "geometry": args.geometry,
        "dynamics": args.dynamics,
        "credit": args.credit,
        "update": args.update,
        "total_coordinates": len(coordinates),
        "seeds": args.seeds,
        "epochs": args.epochs,
        "recovery_steps": args.recovery_steps,
        "damage_severity": args.damage_severity,
        "device": args.device,
    }

    if args.dry_run:
        if args.format == "json":
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print("Frozen-θ ψ Benchmark Campaign")
            print(f"  Substrates: {substrates}")
            print(f"  Plasticity types: {plasticity_types}")
            print(f"  Geometry: {args.geometry}")
            print(f"  Dynamics: {args.dynamics}")
            print(f"  Credit: {args.credit}")
            print(f"  Update: {args.update}")
            print(f"  Total coordinates: {len(coordinates)}")
            print(f"  Seeds per coordinate: {args.seeds}")
            print(f"  Epochs: {args.epochs}")
            print(f"  Recovery steps: {args.recovery_steps}")
            print(f"  Damage severity: {args.damage_severity}")
            print("\nDry run - coordinates:")
            for coord in coordinates:
                print(f"  {coord}")
        return 0

    if not args.run:
        if args.format == "json":
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Plan written to {args.output}")
            else:
                print(output)
        else:
            print("Frozen-θ ψ Benchmark Campaign")
            print(f"  Substrates: {substrates}")
            print(f"  Plasticity types: {plasticity_types}")
            print(f"  Geometry: {args.geometry}")
            print(f"  Dynamics: {args.dynamics}")
            print(f"  Credit: {args.credit}")
            print(f"  Update: {args.update}")
            print(f"  Total coordinates: {len(coordinates)}")
            print(f"  Seeds per coordinate: {args.seeds}")
            print(f"  Epochs: {args.epochs}")
            print(f"  Recovery steps: {args.recovery_steps}")
            print(f"  Damage severity: {args.damage_severity}")
            print("Plan generated. Use --run to execute or --dry-run to preview.")
        return 0

    if args.format == "json":
        output = json.dumps({"status": "running", **plan}, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Running status written to {args.output}")
        else:
            print(output)

    print("Running benchmark...")
    output_dir = Path(args.output_dir)

    run_structural_robustness_suite(
        coordinates=coordinates,
        output_dir=output_dir,
        epochs=args.epochs,
        recovery_steps=args.recovery_steps,
        damage_severity=args.damage_severity,
        seeds=args.seeds,
        device=args.device,
    )

    print("Benchmark complete.")
    if args.format == "json" and args.output:
        # Update output with completion status
        output_data = {"status": "completed", **plan, "output_dir": str(output_dir)}
        Path(args.output).write_text(
            json.dumps(output_data, indent=2), encoding="utf-8"
        )
        logger.info(f"Completion status written to {args.output}")
    return 0


def _cmd_hypothesis_campaign(args: argparse.Namespace) -> int:  # ruff: ignore[complex-structure, too-many-return-statements, too-many-branches, too-many-statements, too-many-locals]
    """Run hypothesis templates over campaign records."""
    import json
    from pathlib import Path

    if args.dry_run:
        plan = {
            "command": "hypothesis-campaign",
            "store": args.store,
            "run_id": args.run_id,
            "templates": args.templates,
            "bindings": args.bind,
        }
        if args.format == "json":
            output = json.dumps(plan, indent=2)
            if args.output:
                Path(args.output).write_text(output, encoding="utf-8")
                logger.info(f"Dry run plan written to {args.output}")
            else:
                print(output)
        else:
            print("Dry run: would evaluate hypothesis templates")
            print(f"  Store: {args.store}")
            print(f"  Run ID: {args.run_id or 'latest'}")
            print(f"  Templates: {args.templates}")
            print(f"  Bindings: {args.bind}")
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        # Determine run_id
        run_id = args.run_id
        if run_id is None:
            # Query all records to find the latest run_id
            all_records = list(store.query_records())
            if not all_records:
                logger.error("No records found in store")
                return 1
            run_ids: set[str] = set()
            for r in all_records:
                rid = r.provenance.links.get("run_id")
                if rid is not None:
                    run_ids.add(rid)
            if not run_ids:
                logger.error("No valid run_id found in records")
                return 1
            run_id = max(run_ids)  # Use latest by string comparison
            logger.info(f"Auto-selected run_id: {run_id}")
        else:
            # Verify run exists by querying records
            all_records = list(store.query_records(run_id=run_id))
            if not all_records:
                logger.error(f"No records found for run_id: {run_id}")
                return 1

        logger.info(f"Evaluating hypothesis templates for run: {run_id}")

        # Load templates
        import contextlib
        import json

        templates_path = Path(args.templates)
        if not templates_path.exists():
            logger.error(f"Templates file not found: {templates_path}")
            return 1

        with templates_path.open(encoding="utf-8") as f:
            templates_data = json.load(f)

        # Parse bindings
        bindings: dict[str, dict[str, Any]] = {}
        for bind_str in args.bind:
            if ":" not in bind_str or "=" not in bind_str:
                logger.error(
                    f"Invalid binding format: {bind_str} (expected template:param=value)"
                )
                return 1
            template_name, param_value = bind_str.split(":", 1)
            param, value = param_value.split("=", 1)
            # Try to parse value as JSON
            with contextlib.suppress(json.JSONDecodeError):
                value = json.loads(value)
            bindings.setdefault(template_name, {})[param] = value

        # Query all records for the run
        records = list(store.query_records(run_id=run_id))
        if not records:
            logger.warning(f"No records found for run {run_id}")
            return 0

        # Create campaign context
        from computronium.experiment.legality.dsl import (
            CampaignContext,
            Diff,
            Exists,
            ForAll,
            Max,
            Mean,
            Min,
            Ratio,
            Std,
            expr_from_json,
        )

        campaign_ctx = CampaignContext(records)

        # Evaluate each template
        results = {}
        for template_data in templates_data:
            template_name = template_data.get("name")
            if not template_name:
                logger.warning("Template missing name, skipping")
                continue

            template_expr = expr_from_json(template_data["expr"])

            # Apply bindings if any
            if template_name in bindings:
                # For now, we just note the bindings - full template binding
                # would require substituting variables in the expression
                logger.info(
                    f"Template {template_name} has bindings: {bindings[template_name]}"
                )

            # Evaluate based on expression type
            result = None
            if isinstance(template_expr, ForAll):
                result = campaign_ctx.eval_forall(
                    template_expr.filter, template_expr.body
                )
            elif isinstance(template_expr, Exists):
                result = campaign_ctx.eval_exists(
                    template_expr.filter, template_expr.body
                )
            elif isinstance(template_expr, Mean):
                result = campaign_ctx.eval_aggregation(
                    "Mean", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Max):
                result = campaign_ctx.eval_aggregation(
                    "Max", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Min):
                result = campaign_ctx.eval_aggregation(
                    "Min", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Std):
                result = campaign_ctx.eval_aggregation(
                    "Std", template_expr.expr, template_expr.group_by
                )
            elif isinstance(template_expr, Diff):
                result = campaign_ctx.eval_diff(template_expr.left, template_expr.right)
            elif isinstance(template_expr, Ratio):
                result = campaign_ctx.eval_ratio(
                    template_expr.left, template_expr.right
                )
            else:
                logger.warning(
                    f"Template {template_name}: unsupported expression type {type(template_expr).__name__}"
                )
                continue

            # Convert result to JSON-serializable format
            def to_serializable(obj):
                if isinstance(obj, dict):
                    return {str(k): to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [to_serializable(v) for v in obj]
                elif isinstance(obj, (int, float, str, bool)) or obj is None:
                    return obj
                else:
                    return str(obj)

            results[template_name] = {
                "result": to_serializable(result),
                "template_type": type(template_expr).__name__,
            }

        # Output results
        output_data = {
            "run_id": run_id,
            "record_count": len(records),
            "results": results,
        }

        if args.format == "json":
            output = json.dumps(output_data, indent=2, default=str)
        else:
            output = json.dumps(output_data, indent=2, default=str)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding="utf-8")
            logger.info(f"Results written to {output_path}")
        else:
            print(output)

        return 0
