"""The surface CLI's dynamical-analysis commands."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from computronium.core.logging import get_logger
from computronium.experiment.surface.report import (
    ReportGenerator,
)

from ._execution import _open_store

if TYPE_CHECKING:
    import argparse

    from computronium.experiment.evidence.store import RecordStore

logger = get_logger()


def _resolve_device(device: str) -> str:
    """Resolve 'auto' to 'cuda' if available, otherwise 'cpu'."""
    import torch

    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def _load_record_for_analysis(
    store: RecordStore, run_id: str | None, record_id: str | None
):
    """Load the record to analyze, preferring claim-eligible records."""

    if run_id is None:
        run_id = store.latest_run_id()
        if run_id is None:
            logger.error("No runs found in store")
            return None, None

    if record_id:
        record = store.get_record(record_id)
        if record is None:
            logger.error(f"Record {record_id} not found")
            return None, None
        return record, run_id

    # Get latest claim-eligible record
    generator = ReportGenerator(store)
    eligible = generator.claim_eligible_records(run_id)
    if eligible:
        return eligible[-1], run_id

    # Fallback: use any record (e.g., quick-verify runs with n_seeds=1)
    all_records = list(store.query_records(run_id=run_id))
    if not all_records:
        logger.error(f"No records for run {run_id}")
        return None, None
    return all_records[-1], run_id


def _run_lyapunov_analysis(transition_fn, init_state, args):
    """Run Lyapunov spectrum analysis."""
    from computronium.stability import estimate_lyapunov_spectrum

    logger.info("Computing Lyapunov spectrum...")
    try:
        spectrum = estimate_lyapunov_spectrum(
            transition_fn,
            init_state,
            None,
            num_vectors=args.lyapunov_vectors,
            num_steps=args.lyapunov_steps,
        )
        return {
            "lyapunov_spectrum": spectrum,
            "lyapunov_max": max(spectrum) if spectrum else 0.0,
        }
    except Exception as exc:
        logger.warning(f"Lyapunov spectrum failed: {exc}")
        return {"lyapunov_spectrum": [], "lyapunov_error": str(exc)}


def _run_basin_analysis(
    transition_fn,
    init_state,
    args,
    dynamics_type: str | None = None,
    geometry_type: str | None = None,
):
    """Run basin stability analysis."""
    from computronium.stability import estimate_basin_stability_multistart

    # Basin stability is only meaningful for iterative dynamics with attractor basins.
    # Requires: iterative dynamics (not instantaneous) AND recurrent geometry (not feedforward).
    ITERATIVE_DYNAMICS = {
        "energy_minimization",
        "predictive_settling",
        "error_predictive_coding",
        "pc_alm",
        "spike_integration",
        "diffusion",
        "lazy",
    }
    RECURRENT_GEOMETRIES = {"recurrent", "tile_mesh", "quantum", "nca", "ntm"}

    if dynamics_type and dynamics_type not in ITERATIVE_DYNAMICS:
        logger.info(
            f"Skipping basin stability for {dynamics_type} dynamics (no iterative settling)"
        )
        return {
            "basin_stability": {},
            "basin_skipped": f"not applicable for {dynamics_type} dynamics",
        }
    if geometry_type and geometry_type not in RECURRENT_GEOMETRIES:
        logger.info(
            f"Skipping basin stability for {geometry_type} geometry (no recurrent connections)"
        )
        return {
            "basin_stability": {},
            "basin_skipped": f"not applicable for {geometry_type} geometry",
        }

    logger.info("Computing basin stability...")
    try:
        radii = [float(r.strip()) for r in args.basin_radii.split(",")]
        basin_results = estimate_basin_stability_multistart(
            transition_fn,
            init_state,
            None,
            num_samples=args.basin_samples,
            perturbation_radii=radii,
            max_steps=args.basin_steps,
        )
    except Exception as exc:
        logger.warning(f"Basin stability failed: {exc}")
        return {"basin_stability": {}, "basin_error": str(exc)}
    return {"basin_stability": basin_results}


def _run_settling_analysis(transition_fn, init_state, args):
    """Run settling trajectory analysis."""
    from computronium.stability import measure_settling_time

    logger.info("Computing settling trajectory...")
    try:
        steps, norms = measure_settling_time(
            transition_fn,
            init_state,
            None,
            tolerance=args.settling_tolerance,
            max_steps=args.settling_steps,
        )
    except Exception as exc:
        logger.warning(f"Settling trajectory failed: {exc}")
        return {"settling_steps": 0, "settling_norms": [], "settling_error": str(exc)}
    return {
        "settling_steps": steps,
        "settling_norms": norms,
        "settling_converged": steps < args.settling_steps,
    }


def _format_output(results, args):
    """Format output as JSON or text."""

    if args.format == "json":
        return json.dumps(results, indent=2, default=str)
    else:
        lines = [
            f"Stability Analysis for {results['record_id']}",
            f"Coordinate: {results['coordinate']}",
            "",
        ]
        if results.get("lyapunov_spectrum"):
            lines.append(
                f"Lyapunov Spectrum: {results['lyapunov_spectrum']} (max: {results['lyapunov_max']:.4f})"
            )
        if results.get("basin_stability"):
            lines.append("Basin Stability:")
            for radius, stability in results["basin_stability"].items():
                lines.append(f"  radius={radius}: {stability:.4f}")
        if "settling_steps" in results:
            lines.append(
                f"Settling: {results['settling_steps']} steps, converged: {results['settling_converged']}"
            )
        # Show errors if any
        for key in ["lyapunov_error", "basin_error", "settling_error"]:
            if key in results:
                lines.append(f"{key}: {results[key]}")
        return "\n".join(lines)


def _cmd_stability_analysis(args: argparse.Namespace) -> int:  # ruff: ignore[too-many-locals]
    """Run dynamical stability analysis on a trained system."""

    device = _resolve_device(args.device)

    if args.dry_run:
        plan = {
            "command": "stability-analysis",
            "store": args.store,
            "run_id": args.run_id,
            "record_id": args.record_id,
            "device": device,
            "lyapunov": args.lyapunov,
            "lyapunov_vectors": args.lyapunov_vectors,
            "lyapunov_steps": args.lyapunov_steps,
            "basin": args.basin,
            "basin_samples": args.basin_samples,
            "basin_radii": args.basin_radii,
            "basin_steps": args.basin_steps,
            "settling": args.settling,
            "settling_steps": args.settling_steps,
            "settling_tolerance": args.settling_tolerance,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    # Open store
    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        record, _run_id = _load_record_for_analysis(store, args.run_id, args.record_id)
        if record is None:
            return 1

        # Recompose the cell system
        from computronium.domains.factory import create_task
        from computronium.experiment.analysis.transition import build_transition
        from computronium.experiment.kernel.compose import compose_cell_system
        from computronium.experiment.schema.coordinate import Coordinate

        # Build coordinate from record fields
        coordinate = Coordinate(
            substrate=record.substrate,
            geometry=record.geometry,
            dynamics=record.dynamics,
            plasticity=record.plasticity,
            credit=record.credit,
            update=record.update,
            params=dict(record.params),
        )
        schedule = record.schedule

        task = create_task(
            schedule.task_id, device=device, quick_mode=True, num_workers=0
        )
        task.setup()

        from computronium.experiment.kernel.evaluate import task_shape

        shape = task_shape(schedule.task_id, device)
        cell = compose_cell_system(
            coordinate=coordinate,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=schedule.param_budget,
        )

        system = cell.system
        # Move system to target device
        system = system.to(device)  # type: ignore[attr-defined]

        # Get a sample input for stability analysis
        sample_x, _ = next(iter(task.get_dataloader("train")))  # type: ignore[attr-defined]

        # Build transition function and initial state
        transition = build_transition(system, sample_x)
        transition_fn = transition.step
        init_state = transition.initial

        results = {"record_id": record.record_id, "coordinate": coordinate.cell_key()}

        # Run requested analyses
        if args.lyapunov:
            results.update(_run_lyapunov_analysis(transition_fn, init_state, args))  # type: ignore[arg-type]
        if args.basin:
            results.update(
                _run_basin_analysis(
                    transition_fn,
                    init_state,
                    args,
                    coordinate.dynamics,
                    coordinate.geometry,
                )
            )  # type: ignore[arg-type]
        if args.settling:
            results.update(_run_settling_analysis(transition_fn, init_state, args))  # type: ignore[arg-type]

        # Output
        output = _format_output(results, args)

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Stability analysis written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_energy_landscape(args: argparse.Namespace) -> int:  # ruff: ignore[too-many-locals]
    """Compute 2D energy landscape via PCA."""

    device = _resolve_device(args.device)

    if args.dry_run:
        plan = {
            "command": "energy-landscape",
            "store": args.store,
            "run_id": args.run_id,
            "record_id": args.record_id,
            "device": device,
            "grid_resolution": args.grid_resolution,
            "grid_range": args.grid_range,
            "num_trajectories": args.num_trajectories,
            "trajectory_length": args.trajectory_length,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    # Open store
    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        record, _run_id = _load_record_for_analysis(store, args.run_id, args.record_id)
        if record is None:
            return 1

        # Recompose the cell system
        from computronium.domains.factory import create_task
        from computronium.experiment.analysis.transition import build_transition
        from computronium.experiment.kernel.compose import compose_cell_system
        from computronium.experiment.schema.coordinate import Coordinate

        coordinate = Coordinate(
            substrate=record.substrate,
            geometry=record.geometry,
            dynamics=record.dynamics,
            plasticity=record.plasticity,
            credit=record.credit,
            update=record.update,
            params=dict(record.params),
        )
        schedule = record.schedule

        task = create_task(
            schedule.task_id, device=device, quick_mode=True, num_workers=0
        )
        task.setup()

        from computronium.experiment.kernel.evaluate import task_shape

        shape = task_shape(schedule.task_id, device)
        cell = compose_cell_system(
            coordinate=coordinate,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=schedule.param_budget,
        )

        system = cell.system
        system = system.to(device)  # type: ignore[attr-defined]

        sample_x, _ = next(iter(task.get_dataloader("train")))  # type: ignore[attr-defined]

        transition = build_transition(system, sample_x)
        transition_fn = transition.step
        init_state = transition.initial

        from computronium.experiment.analysis import EnergyLandscapeConfig

        config = EnergyLandscapeConfig(
            grid_resolution=args.grid_resolution,
            grid_range=args.grid_range,
        )

        from computronium.experiment.analysis import EnergyLandscapeAnalyzer

        analyzer = EnergyLandscapeAnalyzer(transition_fn, None, config)
        result = analyzer.analyze(
            init_state,
            num_trajectories=args.num_trajectories,
            trajectory_length=args.trajectory_length,
        )

        output = _format_output(
            {
                "record_id": record.record_id,
                "coordinate": coordinate.cell_key(),
                "grid_x": result.grid_x.tolist() if result.grid_x.size > 0 else [],
                "grid_y": result.grid_y.tolist() if result.grid_y.size > 0 else [],
                "energy_values": result.energy_values.tolist()
                if result.energy_values.size > 0
                else [],
                "pca_explained_variance": result.pca_explained_variance.tolist(),
                "attractor_points": result.attractor_points,
                "metadata": result.metadata,
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Energy landscape written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_nonnormality(args: argparse.Namespace) -> int:  # ruff: ignore[too-many-locals]
    """Compute pseudospectra and transient amplification bounds."""

    device = _resolve_device(args.device)

    if args.dry_run:
        plan = {
            "command": "nonnormality",
            "store": args.store,
            "run_id": args.run_id,
            "record_id": args.record_id,
            "device": device,
            "max_time": args.max_time,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    # Open store
    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        record, _run_id = _load_record_for_analysis(store, args.run_id, args.record_id)
        if record is None:
            return 1

        from computronium.domains.factory import create_task
        from computronium.experiment.analysis.transition import build_transition
        from computronium.experiment.kernel.compose import compose_cell_system
        from computronium.experiment.schema.coordinate import Coordinate

        coordinate = Coordinate(
            substrate=record.substrate,
            geometry=record.geometry,
            dynamics=record.dynamics,
            plasticity=record.plasticity,
            credit=record.credit,
            update=record.update,
            params=dict(record.params),
        )
        schedule = record.schedule

        task = create_task(
            schedule.task_id, device=device, quick_mode=True, num_workers=0
        )
        task.setup()

        from computronium.experiment.kernel.evaluate import task_shape

        shape = task_shape(schedule.task_id, device)
        cell = compose_cell_system(
            coordinate=coordinate,
            geometry={},
            input_shape=shape.input_shape,
            output_dim=shape.output_dim,
            param_budget=schedule.param_budget,
        )

        system = cell.system
        system = system.to(device)  # type: ignore[attr-defined]

        sample_x, _ = next(iter(task.get_dataloader("train")))  # type: ignore[attr-defined]

        transition = build_transition(system, sample_x)
        transition_fn = transition.step
        init_state = transition.initial

        from computronium.experiment.analysis import (
            NonnormalityConfig,
            analyze_nonnormality,
        )

        config = NonnormalityConfig(max_time=args.max_time)
        result = analyze_nonnormality(transition_fn, init_state, None, config)

        output = _format_output(
            {
                "record_id": record.record_id,
                "coordinate": coordinate.cell_key(),
                "spectral_radius": result.spectral_radius,
                "max_singular_value": result.max_singular_value,
                "nonnormality_ratio": result.nonnormality_ratio,
                "transient_amplification_bounds": result.transient_amplification_bounds,
                "eigenvalues": [complex(e) for e in result.eigenvalues],
                "metadata": result.metadata,
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Nonnormality analysis written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_axis_attribution(args: argparse.Namespace) -> int:
    """Compute SHAP/ICE attribution for ontology axes."""

    if args.dry_run:
        plan = {
            "command": "axis-attribution",
            "store": args.store,
            "run_id": args.run_id,
            "metric": args.metric,
            "axes": args.axes,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        run_id = args.run_id or store.latest_run_id()
        if run_id is None:
            logger.error("No runs found")
            return 1

        axes = (
            args.axes.split(",")
            if args.axes
            else ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"]
        )

        from computronium.experiment.analysis import (
            AxisAttributionAnalyzer,
        )

        analyzer = AxisAttributionAnalyzer(store, run_id)
        result = analyzer.analyze(axes=axes, metric=args.metric)

        output = _format_output(
            {
                "run_id": run_id,
                "metric": args.metric,
                "axes": axes,
                "shap_values": result.shap_values,
                "feature_importance": result.feature_importance,
                "interaction_effects": result.interaction_effects,
                "metadata": result.metadata,
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Axis attribution written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_counterfactual(args: argparse.Namespace) -> int:
    """Compute counterfactual trajectories."""

    if args.dry_run:
        plan = {
            "command": "counterfactual",
            "store": args.store,
            "run_id": args.run_id,
            "metric": args.metric,
            "axes": args.axes,
            "n_targets": args.n_targets,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        run_id = args.run_id or store.latest_run_id()
        if run_id is None:
            logger.error("No runs found")
            return 1

        from computronium.experiment.analysis import (
            CounterfactualAnalyzer,
        )

        analyzer = CounterfactualAnalyzer(store, run_id)
        axes = (
            args.axes.split(",")
            if args.axes
            else ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"]
        )

        results = analyzer.analyze(
            axes=axes, metric=args.metric, n_targets=args.n_targets
        )

        output = _format_output(
            {
                "run_id": run_id,
                "metric": args.metric,
                "n_results": len(results),
                "results": [
                    {
                        "counterfactual_axis": r.counterfactual_axis,
                        "counterfactual_value": r.counterfactual_value,
                        "predicted_metric": r.predicted_metric,
                        "actual_metric": r.actual_metric,
                        "difference": r.difference,
                        "confidence": r.confidence,
                        "metadata": r.metadata,
                    }
                    for r in results[:50]  # Limit output
                ],
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Counterfactual analysis written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_mediation(args: argparse.Namespace) -> int:
    """Test mediation effects."""

    if args.dry_run:
        plan = {
            "command": "mediation",
            "store": args.store,
            "run_id": args.run_id,
            "independent": args.independent,
            "mediator": args.mediator,
            "dependent": args.dependent,
            "all_mediators": args.all_mediators,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        from computronium.experiment.analysis import MediationAnalyzer

        analyzer = MediationAnalyzer(store, args.run_id or store.latest_run_id())

        if args.all_mediators:
            results = analyzer.analyze_all_mediators(args.independent, args.dependent)
        else:
            results = [
                analyzer.analyze(args.independent, args.mediator, args.dependent)
            ]

        output = _format_output(
            {
                "run_id": args.run_id,
                "independent": args.independent,
                "dependent": args.dependent,
                "results": [
                    {
                        "mediator": r.mediator_var,
                        "total_effect": r.total_effect,
                        "direct_effect": r.direct_effect,
                        "indirect_effect": r.indirect_effect,
                        "proportion_mediated": r.proportion_mediated,
                        "sobel_p_value": r.sobel_p_value,
                        "bootstrap_ci": r.bootstrap_ci,
                        "metadata": r.metadata,
                    }
                    for r in results
                ],
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Mediation analysis written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_pareto_advanced(args: argparse.Namespace) -> int:
    """Advanced Pareto analysis: hypervolume, scalarization sweeps."""

    if args.dry_run:
        plan = {
            "command": "pareto-advanced",
            "store": args.store,
            "run_id": args.run_id,
            "objectives": args.objectives,
            "maximize": args.maximize,
            "n_weights": args.n_weights,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        run_id = args.run_id or store.latest_run_id()
        if run_id is None:
            logger.error("No runs found")
            return 1

        from computronium.experiment.analysis import ParetoAnalyzer, ParetoConfig

        objectives = args.objectives.split(",")
        maximize = [m.lower() == "true" for m in args.maximize.split(",")]

        analyzer = ParetoAnalyzer(
            store, run_id, ParetoConfig(n_weight_samples=args.n_weights)
        )
        result = analyzer.analyze(objectives=objectives, maximize=maximize)

        output = _format_output(
            {
                "run_id": run_id,
                "objectives": objectives,
                "maximize": maximize,
                "n_pareto": len(result.pareto_points),
                "n_dominated": len(result.dominated_points),
                "hypervolume": result.hypervolume,
                "pareto_points": [
                    {
                        "record_id": p["record_id"],
                        "objectives": p["objectives"],
                        "coordinate": p["coordinate"],
                    }
                    for p in result.pareto_points[:20]
                ],
                "scalarization_results": {
                    k: [
                        {"record_id": p["record_id"], "score": p["scalarized_score"]}
                        for p in v[:5]
                    ]
                    for k, v in result.scalarization_results.items()
                },
                "metadata": result.metadata,
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Advanced Pareto analysis written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_seed_variability(args: argparse.Namespace) -> int:
    """Analyze variability across seeds."""

    if args.dry_run:
        plan = {
            "command": "seed-variability",
            "store": args.store,
            "run_id": args.run_id,
            "metric": args.metric,
            "group_by": args.group_by,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        from computronium.experiment.analysis import SeedVariabilityAnalyzer

        analyzer = SeedVariabilityAnalyzer(store, args.run_id or store.latest_run_id())
        result = analyzer.analyze(metric=args.metric, group_by_axis=args.group_by)

        if args.plot:
            plot_path = (
                args.output.replace(".json", "_violin.png")
                if args.output
                else f"seed_variability_{args.metric}.png"
            )
            from computronium.experiment.analysis import plot_violin_plots

            plot_violin_plots(
                result, plot_path, title=f"Seed Variability: {args.metric}"
            )
            logger.info(f"Violin plot saved to {plot_path}")

        output = _format_output(
            {
                "run_id": args.run_id or store.latest_run_id(),
                "metric": args.metric,
                "group_by": args.group_by,
                "overall_mean": result.overall_mean,
                "overall_std": result.overall_std,
                "cv": result.coefficient_of_variation,
                "seed_effect_pvalue": result.seed_effect_pvalue,
                "groups": {
                    k: {kk: vv for kk, vv in v.items() if kk != "values"}
                    for k, v in result.groups.items()
                },
                "metadata": result.metadata,
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Seed variability analysis written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_hardware_variance(args: argparse.Namespace) -> int:
    """Compare performance across hardware devices."""

    if args.dry_run:
        plan = {
            "command": "hardware-variance",
            "store": args.store,
            "run_ids": args.run_ids,
            "metric": args.metric,
            "device_field": args.device_field,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        from computronium.experiment.analysis import HardwareVarianceAnalyzer

        analyzer = HardwareVarianceAnalyzer(store)
        run_ids = args.run_ids.split(",")
        result = analyzer.analyze_from_runs(
            run_ids, metric=args.metric, device_field=args.device_field
        )

        output = _format_output(
            {
                "metric": args.metric,
                "run_ids": run_ids,
                "devices": result.devices,
                "device_effect_pvalue": result.device_effect_pvalue,
                "pairwise_comparisons": result.pairwise_comparisons,
                "metadata": result.metadata,
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Hardware variance analysis written to {args.output}")
        else:
            print(output)

    return 0


def _cmd_repro_advanced(args: argparse.Namespace) -> int:
    """Verify checkpoint replay and bitwise reproducibility."""

    if args.dry_run:
        plan = {
            "command": "repro-advanced",
            "store": args.store,
            "run_id": args.run_id,
            "tolerance": args.tolerance,
        }
        output = _format_output(plan, args)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Dry run plan written to {args.output}")
        else:
            print(output)
        return 0

    store = _open_store(args.store)
    if store is None:
        return 1

    with store:
        from computronium.experiment.analysis import (
            ReproducibilityAnalyzer,
            ReproducibilityConfig,
        )

        analyzer = ReproducibilityAnalyzer(
            store, ReproducibilityConfig(tolerance=args.tolerance)
        )
        result = analyzer.verify_run_reproducibility(args.run_id)

        output = _format_output(
            {
                "run_id": args.run_id,
                "metrics_match": result.metrics_match,
                "bitwise_match": result.bitwise_match,
                "max_relative_diff": result.max_relative_diff,
                "mismatched_keys": result.mismatched_keys,
                "metadata": result.metadata,
            },
            args,
        )

        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            logger.info(f"Reproducibility verification written to {args.output}")
        else:
            print(output)

    return 0
