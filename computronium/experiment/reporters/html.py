"""Enhanced HTML Reporter for experiment results.

Generates rich interactive reports with:
1. Pareto frontiers (accuracy vs latency vs params)
2. Axis coverage heatmaps (geometry × dynamics × credit)
3. Failure mode clustering
4. Convergence curves
5. Resource scaling laws
6. Seed stability analysis
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd

    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


@dataclass(frozen=True, slots=True)
class ReportConfig:
    """Configuration for HTML report generation."""

    title: str = "Experiment Report"
    output_dir: str = "experiments/reports"
    include_pareto: bool = True
    include_heatmaps: bool = True
    include_failure_clustering: bool = True
    include_convergence: bool = True
    include_scaling_laws: bool = True
    include_seed_stability: bool = True


def _records_to_dataframe(records: list[Record]) -> pd.DataFrame:
    """Convert records to a pandas DataFrame for analysis."""
    import pandas as pd

    rows = []
    for r in records:
        row = {
            "run_id": r.run_id,
            "cell_key": r.cell_key,
            "measurement_key": r.measurement_key,
            "substrate": r.substrate,
            "geometry": r.geometry,
            "dynamics": r.dynamics,
            "plasticity": r.plasticity,
            "credit": r.credit,
            "update": r.update,
            "seed": r.schedule.seed,
            "task_id": r.schedule.task_id,
            "fidelity": r.schedule.fidelity,
            "gate_verdict": r.status.gate_verdict.value,
            "defect": r.status.defect,
            "severity": r.status.severity.value,
            "maturity": r.status.maturity.value,
            "walltime_s": r.payload.get("walltime_total", 0),
            "param_count": r.payload.get("param_count", 0),
            "flops": r.payload.get("flops", 0),
            "memory_usage": r.payload.get("memory_usage", 0),
        }
        # Add all payload metrics
        for k, v in r.payload.items():
            if isinstance(v, (int, float)):
                row[k] = v
        rows.append(row)

    return pd.DataFrame(rows)


def _compute_pareto_frontier(
    df: pd.DataFrame,
    x_metric: str,
    y_metric: str,
    maximize_y: bool = True,
    minimize_x: bool = True,
) -> pd.DataFrame:
    """Compute Pareto frontier for two metrics."""
    import pandas as pd

    # Filter to measured cells with valid metrics
    valid = df.dropna(subset=[x_metric, y_metric])
    if valid.empty:
        return pd.DataFrame()

    # Sort by x metric
    valid = valid.sort_values(x_metric, ascending=minimize_x)

    pareto = []
    best_y = -float("inf") if maximize_y else float("inf")

    for _, row in valid.iterrows():
        y_val = row[y_metric]
        if maximize_y:
            if y_val > best_y:
                pareto.append(row)
                best_y = y_val
        elif y_val < best_y:
            pareto.append(row)
            best_y = y_val

    return pd.DataFrame(pareto) if pareto else pd.DataFrame()


def _generate_pareto_plot(
    df: pd.DataFrame,
    x_metric: str,
    y_metric: str,
    color_by: str | None = None,
) -> str:
    """Generate a Plotly pareto frontier plot as HTML."""
    try:
        import plotly.graph_objects as go

        pareto_df = _compute_pareto_frontier(df, x_metric, y_metric)

        fig = go.Figure()

        # All points
        fig.add_trace(
            go.Scatter(
                x=df[x_metric],
                y=df[y_metric],
                mode="markers",
                name="All cells",
                marker={"size": 6, "opacity": 0.5, "color": "lightblue"},
                text=df["cell_key"],
                hovertemplate=(
                    f"Cell: %{{text}}<br>"
                    f"{x_metric}: %{{x:.4f}}<br>"
                    f"{y_metric}: %{{y:.4f}}<extra></extra>"
                ),
            )
        )

        # Pareto frontier
        if not pareto_df.empty:
            fig.add_trace(
                go.Scatter(
                    x=pareto_df[x_metric],
                    y=pareto_df[y_metric],
                    mode="lines+markers",
                    name="Pareto frontier",
                    line={"color": "red", "width": 2, "dash": "dash"},
                    marker={"size": 10, "color": "red"},
                    text=pareto_df["cell_key"],
                    hovertemplate=(
                        f"Pareto Cell: %{{text}}<br>"
                        f"{x_metric}: %{{x:.4f}}<br>"
                        f"{y_metric}: %{{y:.4f}}<extra></extra>"
                    ),
                )
            )

        fig.update_layout(
            title=f"Pareto Frontier: {y_metric} vs {x_metric}",
            xaxis_title=x_metric,
            yaxis_title=y_metric,
            template="plotly_white",
            height=500,
        )

        return fig.to_html(
            include_plotlyjs="cdn", div_id=f"pareto-{x_metric}-{y_metric}"
        )
    except ImportError:
        return f"<div class='warning'>Plotly not available for Pareto plot: {x_metric} vs {y_metric}</div>"


def _generate_coverage_heatmap(
    df: pd.DataFrame,
    axis_x: str,
    axis_y: str,
    metric: str = "validation_accuracy",
) -> str:
    """Generate a coverage heatmap for two axes."""
    try:
        import numpy as np
        import plotly.graph_objects as go

        # Filter measured cells
        measured = df[df["gate_verdict"] == "PASS"]
        if measured.empty:
            return f"<div class='warning'>No measured cells for heatmap: {axis_x} × {axis_y}</div>"

        # Get unique values
        x_vals = sorted(measured[axis_x].unique())
        y_vals = sorted(measured[axis_y].unique())

        # Create matrix
        z = np.full((len(y_vals), len(x_vals)), np.nan)
        counts = np.zeros((len(y_vals), len(x_vals)), dtype=int)

        for _, row in measured.iterrows():
            xi = x_vals.index(row[axis_x])
            yi = y_vals.index(row[axis_y])
            val = row.get(metric)
            if val is not None and not np.isnan(val):
                if np.isnan(z[yi, xi]):
                    z[yi, xi] = val
                else:
                    z[yi, xi] = max(z[yi, xi], val)  # Best across seeds
                counts[yi, xi] += 1

        # Also track void/failed cells
        void_failed = df[df["gate_verdict"] != "PASS"]
        void_counts = np.zeros((len(y_vals), len(x_vals)), dtype=int)
        for _, row in void_failed.iterrows():
            if row[axis_x] in x_vals and row[axis_y] in y_vals:
                xi = x_vals.index(row[axis_x])
                yi = y_vals.index(row[axis_y])
                void_counts[yi, xi] += 1

        fig = go.Figure()

        # Measured cells heatmap
        fig.add_trace(
            go.Heatmap(
                z=z,
                x=x_vals,
                y=y_vals,
                colorscale="Viridis",
                name=f"Measured ({metric})",
                colorbar={"title": metric},
                hovertemplate=f"{axis_x}: %{{x}}<br>{axis_y}: %{{y}}<br>{metric}: %{{z:.4f}}<extra></extra>",
            )
        )

        # Overlay void/failed counts as text
        annotations = []
        for i, y_val in enumerate(y_vals):
            for j, x_val in enumerate(x_vals):
                if void_counts[i, j] > 0:
                    annotations.append({
                        "x": x_val,
                        "y": y_val,
                        "text": f"V:{void_counts[i, j]}",
                        "showarrow": False,
                        "font": {"color": "red", "size": 10},
                        "bgcolor": "rgba(255,255,255,0.8)",
                    })

        fig.update_layout(
            title=f"Axis Coverage: {axis_x} × {axis_y}",
            xaxis_title=axis_x,
            yaxis_title=axis_y,
            template="plotly_white",
            height=500,
            annotations=annotations,
        )

        return fig.to_html(include_plotlyjs="cdn", div_id=f"heatmap-{axis_x}-{axis_y}")
    except ImportError:
        return f"<div class='warning'>Plotly not available for heatmap: {axis_x} × {axis_y}</div>"


def _generate_failure_clustering(
    df: pd.DataFrame,
) -> str:
    """Generate failure mode clustering visualization."""
    try:
        import numpy as np
        import plotly.express as px
        import plotly.graph_objects as go
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE

        failed = df[df["gate_verdict"] != "PASS"]
        if failed.empty:
            return "<div class='info'>No failed cells to cluster</div>"

        # Create feature vectors from coordinate
        features = []
        labels = []
        for _, row in failed.iterrows():
            # One-hot encode structural axes
            feat = []
            for axis in [
                "substrate",
                "geometry",
                "dynamics",
                "plasticity",
                "credit",
                "update",
            ]:
                vals = sorted(df[axis].unique())
                one_hot = [1 if row[axis] == v else 0 for v in vals]
                feat.extend(one_hot)
            features.append(feat)
            labels.append(f"{row['gate_verdict']}: {row['defect'] or 'unknown'}")

        if len(features) < 2:
            return "<div class='info'>Insufficient failed cells for clustering</div>"

        features = np.array(features)

        # Reduce dimensionality
        if features.shape[1] > 2:
            if features.shape[0] > 50:
                reducer = PCA(n_components=2)
            else:
                reducer = TSNE(
                    n_components=2,
                    random_state=42,
                    perplexity=min(5, len(features) - 1),
                )
            coords = reducer.fit_transform(features)
        else:
            coords = features

        fig = go.Figure()

        unique_labels = list(set(labels))
        colors = (
            px.colors.qualitative.Set1
            if len(unique_labels) <= 9
            else px.colors.qualitative.Alphabet
        )

        for i, label in enumerate(unique_labels):
            mask = [l == label for l in labels]
            fig.add_trace(
                go.Scatter(
                    x=coords[mask, 0],
                    y=coords[mask, 1],
                    mode="markers",
                    name=label,
                    marker={"size": 8, "color": colors[i % len(colors)]},
                    text=[failed.iloc[j]["cell_key"] for j, m in enumerate(mask) if m],
                    hovertemplate="Cell: %{text}<br>Cluster: %{fullData.name}<extra></extra>",
                )
            )

        fig.update_layout(
            title="Failure Mode Clustering (PCA/t-SNE on coordinate features)",
            xaxis_title="Component 1",
            yaxis_title="Component 2",
            template="plotly_white",
            height=500,
        )

        return fig.to_html(include_plotlyjs="cdn", div_id="failure-clustering")
    except ImportError:
        return "<div class='warning'>sklearn/plotly not available for failure clustering</div>"


def _generate_convergence_curves(
    records: list[Record],
) -> str:
    """Generate convergence curves from records with trajectory data."""
    try:
        import plotly.graph_objects as go

        # Check if any records have trajectory data
        has_trajectory = any(
            r.payload.get("trajectory") or r.payload.get("convergence_curve")
            for r in records
        )

        if not has_trajectory:
            return "<div class='info'>No convergence curve data available</div>"

        fig = go.Figure()

        for r in records[:20]:  # Limit to first 20 for readability
            trajectory = r.payload.get("trajectory") or r.payload.get(
                "convergence_curve"
            )
            if trajectory and isinstance(trajectory, list):
                fig.add_trace(
                    go.Scatter(
                        y=trajectory,
                        mode="lines",
                        name=r.cell_key[:12],
                        line={"width": 1},
                        opacity=0.7,
                    )
                )

        fig.update_layout(
            title="Convergence Curves (first 20 cells)",
            xaxis_title="Step",
            yaxis_title="Metric",
            template="plotly_white",
            height=400,
            showlegend=True,
        )

        return fig.to_html(include_plotlyjs="cdn", div_id="convergence-curves")
    except ImportError:
        return "<div class='warning'>Plotly not available for convergence curves</div>"


def _generate_scaling_laws(
    df: pd.DataFrame,
) -> str:
    """Generate resource scaling law plots."""
    try:
        import numpy as np
        import plotly.graph_objects as go
        from scipy import stats

        measured = df[df["gate_verdict"] == "PASS"].dropna(
            subset=["param_count", "walltime_s"]
        )
        if measured.empty or len(measured) < 3:
            return "<div class='info'>Insufficient data for scaling laws</div>"

        fig = go.Figure()

        # Param count vs walltime
        x = measured["param_count"].values
        y = measured["walltime_s"].values

        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name="Cells",
                marker={"size": 6, "opacity": 0.6},
                text=measured["cell_key"],
                hovertemplate="Cell: %{text}<br>Params: %{x}<br>Walltime: %{y:.2f}s<extra></extra>",
            )
        )

        # Fit power law: walltime = a * params^b
        mask = (x > 0) & (y > 0)
        if mask.sum() > 2:
            log_x = np.log(x[mask])
            log_y = np.log(y[mask])
            slope, intercept, r_value, _, _ = stats.linregress(log_x, log_y)
            a = np.exp(intercept)
            b = slope

            x_fit = np.logspace(np.log10(x[mask].min()), np.log10(x[mask].max()), 50)
            y_fit = a * x_fit**b

            fig.add_trace(
                go.Scatter(
                    x=x_fit,
                    y=y_fit,
                    mode="lines",
                    name=f"Fit: t ∝ p^{b:.2f} (R²={r_value**2:.3f})",
                    line={"color": "red", "width": 2, "dash": "dash"},
                )
            )

        fig.update_layout(
            title="Scaling Law: Walltime vs Parameter Count",
            xaxis_title="Parameter Count",
            yaxis_title="Walltime (s)",
            xaxis_type="log",
            yaxis_type="log",
            template="plotly_white",
            height=400,
        )

        return fig.to_html(include_plotlyjs="cdn", div_id="scaling-laws")
    except ImportError:
        return "<div class='warning'>Plotly/scipy not available for scaling laws</div>"


def _generate_seed_stability(
    df: pd.DataFrame,
    metric: str = "val_acc",
) -> str:
    """Generate seed stability analysis."""
    try:
        import plotly.graph_objects as go

        measured = df[df["gate_verdict"] == "PASS"].dropna(subset=[metric])
        if measured.empty:
            return f"<div class='info'>No measured cells for seed stability: {metric}</div>"

        # Group by coordinate (excluding seed) and compute statistics
        coord_cols = [
            "substrate",
            "geometry",
            "dynamics",
            "plasticity",
            "credit",
            "update",
        ]
        grouped = (
            measured
            .groupby(coord_cols)[metric]
            .agg(["mean", "std", "count"])
            .reset_index()
        )
        grouped = grouped[grouped["count"] > 1]  # Only coordinates with multiple seeds

        if grouped.empty:
            return f"<div class='info'>No coordinates with multiple seeds for {metric}</div>"

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=grouped["mean"],
                y=grouped["std"],
                mode="markers",
                name="Coordinates",
                marker=dict(size=8, opacity=0.7),
                text=[
                    f"{row['geometry']}/{row['dynamics']}/{row['credit']}/{row['update']}"
                    for _, row in grouped.iterrows()
                ],
                hovertemplate="Config: %{text}<br>Mean: %{x:.4f}<br>Std: %{y:.4f}<extra></extra>",
            )
        )

        fig.update_layout(
            title=f"Seed Stability: Std vs Mean of {metric}",
            xaxis_title=f"Mean {metric}",
            yaxis_title=f"Std {metric} (across seeds)",
            template="plotly_white",
            height=400,
        )

        return fig.to_html(include_plotlyjs="cdn", div_id="seed-stability")
    except ImportError:
        return "<div class='warning'>Plotly not available for seed stability</div>"


def _generate_summary_stats(records: list[Record]) -> dict[str, Any]:
    """Generate summary statistics."""
    total = len(records)
    measured = sum(1 for r in records if r.status.gate_verdict.value == "PASS")
    void = sum(1 for r in records if r.status.gate_verdict.value == "VOID")
    failed = sum(1 for r in records if r.status.gate_verdict.value == "FAIL")

    # Count by axis
    axes = ["substrate", "geometry", "dynamics", "plasticity", "credit", "update"]
    axis_coverage = {}
    for axis in axes:
        measured_vals = {
            getattr(r, axis) for r in records if r.status.gate_verdict.value == "PASS"
        }
        all_vals = {getattr(r, axis) for r in records}
        axis_coverage[axis] = {
            "measured": len(measured_vals),
            "total": len(all_vals),
            "coverage": len(measured_vals) / len(all_vals) if all_vals else 0,
        }

    return {
        "total_cells": total,
        "measured": measured,
        "void": void,
        "failed": failed,
        "measured_rate": measured / total if total > 0 else 0,
        "axis_coverage": axis_coverage,
    }


def generate_html_report(
    store: RecordStore,
    run_id: str,
    config: ReportConfig | None = None,
) -> Path:
    """Generate an HTML report for a run."""
    config = config or ReportConfig()
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Query records
    records = store.query_records(run_id=run_id)
    if not records:
        raise ValueError(f"No records found for run_id: {run_id}")

    # Convert to DataFrame
    df = _records_to_dataframe(records)
    summary = _generate_summary_stats(records)

    # Generate plots
    plots = {}

    # Determine metric names from actual data
    accuracy_metrics = [
        c for c in df.columns if c in ("validation_accuracy", "val_acc", "val_accuracy")
    ]
    walltime_metrics = [
        c for c in df.columns if c in ("walltime_total", "walltime_s", "walltime")
    ]
    acc_metric = accuracy_metrics[0] if accuracy_metrics else "val_acc"
    wt_metric = walltime_metrics[0] if walltime_metrics else "walltime_s"

    if config.include_pareto and acc_metric in df.columns:
        plots["pareto_acc_walltime"] = _generate_pareto_plot(df, wt_metric, acc_metric)
        plots["pareto_params_acc"] = _generate_pareto_plot(
            df, "param_count", acc_metric
        )
        plots["pareto_flops_acc"] = _generate_pareto_plot(df, "flops", acc_metric)

    if config.include_heatmaps:
        plots["heatmap_geom_dyn"] = _generate_coverage_heatmap(
            df, "geometry", "dynamics"
        )
        plots["heatmap_geom_credit"] = _generate_coverage_heatmap(
            df, "geometry", "credit"
        )
        plots["heatmap_dyn_credit"] = _generate_coverage_heatmap(
            df, "dynamics", "credit"
        )
        plots["heatmap_credit_update"] = _generate_coverage_heatmap(
            df, "credit", "update"
        )

    if config.include_failure_clustering:
        plots["failure_clustering"] = _generate_failure_clustering(df)

    if config.include_convergence:
        plots["convergence"] = _generate_convergence_curves(records)

    if config.include_scaling_laws:
        plots["scaling_laws"] = _generate_scaling_laws(df)

    if config.include_seed_stability:
        plots["seed_stability"] = _generate_seed_stability(df, acc_metric)

    # Generate HTML report
    html = _render_html_template(config.title, summary, plots)

    output_path = output_dir / f"{run_id}_report.html"
    output_path.write_text(html)
    return output_path


def _render_html_template(
    title: str, summary: dict[str, Any], plots: dict[str, str]
) -> str:
    """Render the HTML report template."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #4a90d9; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; margin-top: 40px; }}
        h3 {{ color: #34495e; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #4a90d9; }}
        .stat-card h3 {{ margin: 0 0 10px 0; font-size: 14px; color: #666; }}
        .stat-card .value {{ font-size: 32px; font-weight: bold; color: #1a1a2e; }}
        .stat-card.measured {{ border-left-color: #27ae60; }}
        .stat-card.void {{ border-left-color: #f39c12; }}
        .stat-card.failed {{ border-left-color: #e74c3c; }}
        .plot-container {{ margin: 30px 0; }}
        .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 4px; color: #856404; }}
        .info {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 4px; color: #0c5460; }}
        .axis-coverage {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 20px 0; }}
        .axis-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .axis-card h4 {{ margin: 0 0 5px 0; font-size: 12px; color: #666; }}
        .axis-card .coverage {{ font-size: 24px; font-weight: bold; color: #1a1a2e; }}
        .axis-card .detail {{ font-size: 11px; color: #888; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>

        <div class="summary-grid">
            <div class="stat-card">
                <h3>Total Cells</h3>
                <div class="value">{summary["total_cells"]}</div>
            </div>
            <div class="stat-card measured">
                <h3>Measured</h3>
                <div class="value">{summary["measured"]}</div>
                <div>({summary["measured_rate"]:.1%})</div>
            </div>
            <div class="stat-card void">
                <h3>Void</h3>
                <div class="value">{summary["void"]}</div>
            </div>
            <div class="stat-card failed">
                <h3>Failed</h3>
                <div class="value">{summary["failed"]}</div>
            </div>
        </div>

        <h2>Axis Coverage</h2>
        <div class="axis-coverage">
"""

    for axis, cov in summary["axis_coverage"].items():
        html += f"""
            <div class="axis-card">
                <h4>{axis}</h4>
                <div class="coverage">{cov["coverage"]:.0%}</div>
                <div class="detail">{cov["measured"]} / {cov["total"]} primitives</div>
            </div>
"""

    html += """
        </div>

        <h2>Visualizations</h2>
"""

    for plot_id, plot_html in plots.items():
        html += f"""
        <div class="plot-container" id="{plot_id}">
            {plot_html}
        </div>
"""

    html += """
    </div>
</body>
</html>
"""
    return html


def generate_report_from_db(
    db_path: str,
    run_id: str | None = None,
    output_dir: str = "experiments/reports",
) -> Path:
    """Convenience function to generate report directly from database."""
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    store = RecordStore(StoreConfig(path=Path(db_path), read_only=True))
    with store:
        if run_id is None:
            run_info = store.latest_run_id()
            if run_info is None:
                raise ValueError("No runs found in database")
            run_id = run_info
        config = ReportConfig(output_dir=output_dir)
        return generate_html_report(store, run_id, config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate HTML report from experiment database"
    )
    parser.add_argument("--db", required=True, help="Path to experiment database")
    parser.add_argument("--run-id", help="Run ID (default: latest)")
    parser.add_argument(
        "--output", default="experiments/reports", help="Output directory"
    )

    args = parser.parse_args()

    path = generate_report_from_db(args.db, args.run_id, args.output)
    print(f"Report generated: {path}")
