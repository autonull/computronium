"""Atlas visualization (TODO28 Phases 2-3) — the broad map as an HTML dashboard.

Reads the broad-map KnowledgeBase (measured cells) and
``structural_voids.jsonl`` (gate-rejected coordinates), one-hot encodes the
ontology axes, derives physics metrics (BP-deficit against the ruler
ceiling), embeds the space with UMAP (t-SNE fallback), and renders three
views into one HTML file:

1. Islands & voids — embedding scatter colored by BP-deficit, voids overlaid.
2. River of computation — parallel coordinates across the ontology axes.
3. Instrument radar — top-3 Pareto cells vs. the available continuous metrics.

Usage::

    uv run python scripts/visualize_atlas.py --root artifacts/broad_map
    uv run python scripts/visualize_atlas.py --root artifacts/broad_map --multi-task
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, TypedDict

import numpy as np
import pandas as pd

from computronium.autoscientist.objectives import (
    DEFAULT_OBJECTIVES,
    ObjectiveSpec,
)

logger = logging.getLogger("atlas")
if TYPE_CHECKING:
    import argparse
    from pathlib import Path

    from plotly.graph_objects import Figure as go_Figure


class AtlasRow(TypedDict):
    dynamics: str
    credit: str
    update: str
    topology: str
    task: str
    accuracy: float
    train_accuracy: float
    loss: float
    bp_deficit: float
    param_count: float
    lr: float
    spectral_radius: float
    settle_horizon: float
    credit_alignment: float
    walltime_s: float
    is_void: bool
    # Multi-objective fields (TODO31)
    flops: float
    memory_mb: float
    energy_per_step: float
    latency_ms: float
    ruler_walltime_ratio: float
    ruler_energy_ratio: float
    lyapunov_exponent: float
    max_singular_value: float
    psi_capacity: float
    consolidation_cost: float
    rewrite_rate: float
    feedback_path_length: float
    trace_variance: float
    free_energy_final: float
    nan_loss: bool


AXIS_NAMES: tuple[str, ...] = ("dynamics", "credit", "update", "topology")


def _axis_values(df: pd.DataFrame, axis: str) -> tuple[str, ...]:
    return tuple(sorted(df[axis].dropna().unique()))


def load_cells(kb_path: Path, task: str | None = None) -> pd.DataFrame:
    """Measured cells from the KB's experiment entries.

    If task is None, load all tasks and include a 'task' column.
    """
    from computronium.knowledge import KnowledgeBase

    kb = KnowledgeBase(kb_path)
    rows: list[AtlasRow] = []
    for entry in kb.query():
        hp = entry.hyperparameters
        topic = str(entry.topic)
        if not topic.startswith("experiment:"):
            continue
        entry_task = topic.split(":", 1)[1]
        if task is not None and entry_task != task:
            continue
        if not (hp.get("dynamics") and hp.get("credit") and hp.get("update")):
            continue
        geometry = hp.get("geometry") or {}
        if not isinstance(geometry, dict):
            continue
        metrics = entry.metrics
        rows.append({
            "dynamics": str(hp["dynamics"]),
            "credit": str(hp["credit"]),
            "update": str(hp["update"]),
            "topology": str(geometry.get("topology_type", "feedforward")),
            "task": entry_task,
            "accuracy": float(metrics.get("final_accuracy", 0.0)),
            "train_accuracy": float(metrics.get("train_accuracy", 0.0)),
            "loss": float(metrics.get("final_loss", 0.0)),
            "bp_deficit": float(metrics.get("bp_deficit", 0.0)),
            "param_count": float(metrics.get("param_count", 0.0)),
            "lr": float(metrics.get("lr", 0.0)),
            "spectral_radius": float(metrics.get("spectral_radius", 0.0)),
            "settle_horizon": float(metrics.get("settle_horizon", 0.0)),
            "credit_alignment": float(metrics.get("credit_alignment", 0.0)),
            "walltime_s": float(metrics.get("walltime_s", 0.0)),
            # Multi-objective fields (TODO31)
            "flops": float(metrics.get("flops", 0.0)),
            "memory_mb": float(metrics.get("memory_mb", 0.0)),
            "energy_per_step": float(metrics.get("energy_per_step", 0.0)),
            "latency_ms": float(metrics.get("latency_ms", 0.0)),
            "ruler_walltime_ratio": float(metrics.get("ruler_walltime_ratio", 0.0)),
            "ruler_energy_ratio": float(metrics.get("ruler_energy_ratio", 0.0)),
            "lyapunov_exponent": float(metrics.get("lyapunov_exponent", 0.0)),
            "max_singular_value": float(metrics.get("max_singular_value", 0.0)),
            "psi_capacity": float(metrics.get("psi_capacity", 0.0)),
            "consolidation_cost": float(metrics.get("consolidation_cost", 0.0)),
            "rewrite_rate": float(metrics.get("rewrite_rate", 0.0)),
            "feedback_path_length": float(metrics.get("feedback_path_length", 0.0)),
            "trace_variance": float(metrics.get("trace_variance", 0.0)),
            "free_energy_final": float(metrics.get("free_energy_final", 0.0)),
            "nan_loss": bool(metrics.get("nan_loss", False)),
            "is_void": False,
        })
    df = pd.DataFrame(rows)
    logger.info("Loaded %d measured cells", len(df))
    return df


def load_voids(voids_path: Path) -> pd.DataFrame:
    """Structural voids: coordinates the dry-run gate rejected."""
    if not voids_path.exists():
        return pd.DataFrame()
    rows = [
        json.loads(line)
        for line in voids_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    df = pd.DataFrame(rows)
    logger.info("Loaded %d structural voids", len(df))
    return df


def apply_bp_deficit(
    df: pd.DataFrame, ruler_table: Path, task: str | None = None
) -> pd.DataFrame:
    """BP-deficit = ruler ceiling - measured accuracy (clipped at 0)."""
    if df.empty:
        return df
    df = df.copy()
    if task is None:
        # Multi-task: apply per-task ceiling
        if ruler_table.exists():
            rulers = json.loads(ruler_table.read_text(encoding="utf-8"))["rows"]
            ceilings = {r["task"]: float(r["bp_val_accuracy"]) for r in rulers}
            for t, ceiling in ceilings.items():
                mask = df["task"] == t
                df.loc[mask, "bp_deficit"] = (ceiling - df.loc[mask, "accuracy"]).clip(
                    lower=0.0
                )
    else:
        ceiling = 1.0
        if ruler_table.exists():
            rows = json.loads(ruler_table.read_text(encoding="utf-8"))["rows"]
            ceiling = next(
                (float(r["bp_val_accuracy"]) for r in rows if r["task"] == task),
                ceiling,
            )
        df["bp_deficit"] = (ceiling - df["accuracy"]).clip(lower=0.0)
    return df


def feature_matrix(df: pd.DataFrame, multi_task: bool = False) -> np.ndarray:
    """One-hot ontology axes concatenated with continuous physics metrics."""
    axes = list(AXIS_NAMES)
    if multi_task and "task" in df.columns:
        axes.append("task")
    parts = [
        pd.get_dummies(df[axis], prefix=axis).astype(float).reset_index(drop=True)
        for axis in axes
    ]
    parts.append(df[["accuracy", "bp_deficit"]].reset_index(drop=True))  # type: ignore[arg-type]
    return np.asarray(pd.concat(parts, axis=1), dtype=np.float64)


def embed(features: np.ndarray) -> np.ndarray:
    """UMAP when available; sklearn t-SNE otherwise (deterministic seed).

    The fallback also covers UMAP crashes on broken optional GPU stacks
    (e.g. stubbed cupy in test environments)."""
    try:
        import umap

        reducer = umap.UMAP(n_components=2, random_state=0)
        return np.asarray(reducer.fit_transform(features))
    except (ImportError, TypeError, ValueError) as error:
        logger.info("UMAP unavailable (%s); falling back to t-SNE", error)
    from sklearn.manifold import TSNE

    # Perplexity must stay below the sample count: tiny maps (dashboard
    # smoke tests) need a scaled value, not the 30-sample default.
    perplexity = max(2.0, min(30.0, (len(features) - 1) / 3.0))
    return np.asarray(
        TSNE(
            n_components=2,
            random_state=0,
            init="pca",
            perplexity=perplexity,
        ).fit_transform(features)
    )


def pareto_top(
    df: pd.DataFrame,
    k: int = 3,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> pd.DataFrame:
    """Non-dominated cells on configurable objectives.

    Args:
        df: DataFrame with objective columns
        k: Maximum number of front cells to return
        objectives: Tuple of ObjectiveSpec defining the optimization
    """
    if df.empty or not objectives:
        return df

    # Build objective vectors with directions
    obj_names = [o.name.value for o in objectives]
    directions = [o.direction for o in objectives]

    # Check all objective columns exist
    for name in obj_names:
        if name not in df.columns:
            logger.warning("Objective column %s not in DataFrame; skipping", name)
            return df

    pts = df[obj_names].to_numpy()
    dominated = np.zeros(len(df), dtype=bool)

    for i, row_vals in enumerate(pts):
        # A point is dominated if another point is >= in all maximize objectives
        # and <= in all minimize objectives, with at least one strict
        for j, other_vals in enumerate(pts):
            if i == j:
                continue
            dominates = True
            strict = False
            for val_i, val_j, direction in zip(row_vals, other_vals, directions, strict=False):
                if direction == "maximize":
                    if val_j < val_i:
                        dominates = False
                        break
                    if val_j > val_i:
                        strict = True
                else:  # minimize
                    if val_j > val_i:
                        dominates = False
                        break
                    if val_j < val_i:
                        strict = True
            if dominates and strict:
                dominated[i] = True
                break

    front = df.loc[np.flatnonzero(~dominated)].sort_values(
        obj_names[0], ascending=(directions[0] == "minimize")
    )
    return front.head(k)


def _islands_figure(
    live: pd.DataFrame, ghost: pd.DataFrame, multi_task: bool = False
) -> go_Figure:
    """Islands & voids: embedding scatter colored by BP-deficit."""
    import plotly.graph_objects as go

    fig = go.Figure()
    if not ghost.empty:
        fig.add_trace(
            go.Scatter(
                x=ghost["x"],
                y=ghost["y"],
                mode="markers",
                marker={"color": "#cccccc", "size": 5, "opacity": 0.4},
                name="structural void",
                text=ghost["topology"],
                hovertemplate="void %{text}<extra></extra>",
            )
        )
    families = sorted(live["dynamics"].unique())
    symbols = (
        "circle",
        "triangle-up",
        "square",
        "diamond",
        "cross",
        "star",
        "hexagram",
    )
    if multi_task and "task" in live.columns:
        # Color by task, symbol by dynamics
        tasks = sorted(live["task"].unique())
        task_colors = {
            "mnist": "#1f77b4",
            "digits": "#ff7f0e",
            "fashion_mnist": "#2ca02c",
            "cifar10": "#d62728",
            "cifar100": "#9467bd",
        }
        for i, dyn in enumerate(families):
            for j, tsk in enumerate(tasks):
                sub = live[(live["dynamics"] == dyn) & (live["task"] == tsk)]
                if sub.empty:
                    continue
                fig.add_trace(
                    go.Scatter(
                        x=sub["x"],
                        y=sub["y"],
                        mode="markers",
                        name=f"{dyn} | {tsk}",
                        marker={
                            "symbol": symbols[i % len(symbols)],
                            "size": 8,
                            "color": task_colors.get(tsk, f"hsl({j * 60}, 70%, 50%)"),
                            "opacity": 0.8,
                        },
                        text=sub["credit"]
                        + " × "
                        + sub["update"]
                        + " × "
                        + sub["topology"],
                        hovertemplate="%{text}<br>acc %{customdata:.3f}<extra>"
                        + dyn
                        + " | "
                        + tsk
                        + "</extra>",
                        customdata=sub["accuracy"],
                        legendgroup=dyn,
                        legendgrouptitle_text=dyn,
                    )
                )
        fig.update_layout(
            title=f"Islands & Voids — Multi-Task ({len(live)} cells, {len(ghost)} voids)",
            xaxis_title="embedding-1",
            yaxis_title="embedding-2",
        )
    else:
        # Original: color by BP-deficit, symbol by dynamics
        for i, dyn in enumerate(families):
            sub = live[live["dynamics"] == dyn]
            fig.add_trace(
                go.Scatter(
                    x=sub["x"],
                    y=sub["y"],
                    mode="markers",
                    name=dyn,
                    marker={
                        "symbol": symbols[i % len(symbols)],
                        "size": 8,
                        "color": sub["bp_deficit"],
                        "cmin": 0.0,
                        "cmax": 1.0,
                        "colorscale": "RdYlBu",
                        "colorbar": {"title": "BP-deficit"} if i == 0 else None,
                    },
                    text=sub["credit"]
                    + " × "
                    + sub["update"]
                    + " × "
                    + sub["topology"],
                    hovertemplate="%{text}<br>acc %{customdata:.3f}<extra>"
                    + dyn
                    + "</extra>",
                    customdata=sub["accuracy"],
                )
            )
        fig.update_layout(
            title=f"Islands & Voids ({len(live)} cells, {len(ghost)} voids)",
            xaxis_title="embedding-1",
            yaxis_title="embedding-2",
        )
    return fig


def _river_figure(measured: pd.DataFrame) -> go_Figure:
    """River of computation: parallel coordinates across the ontology axes."""
    import plotly.graph_objects as go

    indexed = measured.reset_index(drop=True)
    axis_codes = {
        axis: {v: i for i, v in enumerate(_axis_values(indexed, axis))}
        for axis in AXIS_NAMES
    }
    par = indexed.copy()
    for axis, codes in axis_codes.items():
        par[axis] = par[axis].map(lambda v, c=codes: c.get(str(v), -1))
    fig = go.Figure(
        go.Parcoords(
            line={
                "color": par["accuracy"],
                "colorscale": "RdYlBu",
                "showscale": True,
                "cmin": 0.0,
                "cmax": 1.0,
            },
            dimensions=[
                {
                    "label": axis,
                    "values": par[axis],
                    "tickvals": list(codes.values()),
                    "ticktext": list(codes),
                }
                for axis, codes in axis_codes.items()
            ]
            + [{"label": "accuracy", "values": par["accuracy"]}],
        )
    )
    fig.update_layout(title="River of Computation")
    return fig


def _radar_figure(
    measured: pd.DataFrame,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> go_Figure:
    """Instrument radar: the Pareto front against available continuous metrics.

    Instrument axes (settle_horizon, spectral_radius, acc/walltime) are
    min-max normalized across the Pareto set so all spokes share [0, 1];
    they appear only when the campaign recorded them.
    """
    import plotly.graph_objects as go

    fig = go.Figure()
    top = pareto_top(measured, objectives=objectives)

    def norm(col: str) -> list[float]:
        vals = top[col].astype(float).to_numpy()
        span = float(vals.max() - vals.min())
        if span <= 0:
            return [0.5] * len(vals)
        return ((vals - vals.min()) / span).tolist()

    metric_cols = ["accuracy", "train_accuracy"]
    axes: list[tuple[str, list[float]]] = [
        (name, norm(col))
        for name, col in (
            ("settle_horizon", "settle_horizon"),
            ("σ_max(J)", "spectral_radius"),
        )
        if float(top[col].astype(float).abs().sum()) > 0  # type: ignore[arg-type]
    ]
    if (
        "walltime_s" in top.columns and float(top["walltime_s"].astype(float).sum()) > 0  # type: ignore[arg-type]
    ):
        # Compute-efficiency spoke (TODO29 Phase 1): accuracy per second of
        # trainer.fit() walltime, min-max normalized across the Pareto set.
        efficiency = top["accuracy"] / top["walltime_s"].clip(lower=1e-9)
        span = float(efficiency.max() - efficiency.min())
        axes.append((
            "acc/walltime",
            (
                [0.5] * len(efficiency)
                if span <= 0
                else ((efficiency - efficiency.min()) / span).tolist()
            ),
        ))
    for i, (_, row) in enumerate(top.iterrows()):
        label = f"{row['dynamics'][:12]}|{row['credit'][:12]}|{row['update'][:10]}"
        values = [float(row[c]) for c in metric_cols]  # type: ignore[arg-type]
        theta = [*metric_cols]
        values.append(1.0 - float(row["bp_deficit"]))  # type: ignore[arg-type]
        theta.append("1−bp_deficit")
        values.append(1.0 / (1.0 + float(row["loss"])))  # type: ignore[arg-type]
        theta.append("1/(1+loss)")
        for name, normed in axes:
            values.append(normed[i])
            theta.append(name)
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=theta,
                fill="toself",
                name=label,
            )
        )
    fig.update_layout(title="Instrument Radar — Pareto front (range [0,1])")
    return fig


def render_atlas(
    df: pd.DataFrame,
    voids: pd.DataFrame,
    out: Path,
    task: str | None,
    multi_task: bool = False,
    objectives: tuple[ObjectiveSpec, ...] = DEFAULT_OBJECTIVES,
) -> None:
    import plotly.io as pio

    measured = df.query("~is_void") if "is_void" in df else df
    all_cells = df.copy()
    coords = embed(feature_matrix(all_cells, multi_task=multi_task))
    all_cells["x"], all_cells["y"] = coords[:, 0], coords[:, 1]
    live = all_cells.query("~is_void")
    ghost = all_cells.query("is_void")

    fig_map = _islands_figure(live, ghost, multi_task=multi_task)
    fig_river = _river_figure(measured)
    fig_radar = _radar_figure(measured.reset_index(drop=True), objectives=objectives)

    html = pio.to_html(fig_map, include_plotlyjs=True, full_html=True)
    html += pio.to_html(fig_river, include_plotlyjs=False)
    html += pio.to_html(fig_radar, include_plotlyjs=False)
    out.write_text(html, encoding="utf-8")
    logger.info("Atlas written to %s", out)


def _atlas_png(df: pd.DataFrame, out: Path, task: str) -> None:
    """Static islands-&-voids PNG for docs/figures (matplotlib, Agg)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    all_cells = df.copy()
    coords = embed(feature_matrix(all_cells))
    all_cells["x"], all_cells["y"] = coords[:, 0], coords[:, 1]
    live = all_cells.query("~is_void")
    ghost = all_cells.query("is_void")

    fig, ax = plt.subplots(figsize=(9, 7))
    if not ghost.empty:
        ax.scatter(
            ghost["x"],
            ghost["y"],
            s=12,
            c="#bbbbbb",
            alpha=0.5,
            marker="x",
            label=f"structural voids ({len(ghost)})",
        )
    families = sorted(live["dynamics"].unique())
    markers = ("o", "^", "s", "D", "P", "*", "h")
    for i, dyn in enumerate(families):
        sub = live[live["dynamics"] == dyn]
        sc = ax.scatter(
            sub["x"],
            sub["y"],
            s=40,
            marker=markers[i % len(markers)],
            c=sub["bp_deficit"],
            cmap="RdYlBu_r",
            vmin=0.0,
            vmax=1.0,
            edgecolors="black",
            linewidths=0.3,
            label=dyn,
        )
    if not live.empty:
        fig.colorbar(sc, ax=ax, label="BP-deficit (ruler ceiling − accuracy)")
    ax.set_title(
        f"Computronium broad map — {task}\n({len(live)} cells, {len(ghost)} structural voids)"
    )
    ax.set_xlabel("embedding-1")
    ax.set_ylabel("embedding-2")
    ax.legend(loc="best", fontsize=7, framealpha=0.8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    logger.info("PNG atlas written to %s", out)


def align_void_columns(voids: pd.DataFrame) -> pd.DataFrame:
    """Give void rows the measured-frame columns they need for embedding
    and overlay (accuracy/deficit zero: a void was never measured)."""
    if voids.empty:
        return voids
    voids = voids.copy()
    voids["accuracy"] = 0.0
    voids["train_accuracy"] = 0.0
    voids["loss"] = 0.0
    voids["bp_deficit"] = 0.0
    voids["is_void"] = True
    return voids


def main(args: argparse.Namespace) -> None:
    """Render the atlas from the parsed CLI arguments."""
    logging.basicConfig(level=logging.INFO)
    cells = load_cells(
        args.root / "kb.sqlite", args.task if not args.multi_task else None
    )
    voids = load_voids(args.root / "structural_voids.jsonl")
    cells = apply_bp_deficit(
        cells, args.ruler_table, args.task if not args.multi_task else None
    )
    voids = align_void_columns(voids)
    combined = (
        pd.concat([cells, voids], ignore_index=True) if not voids.empty else cells
    )
    if combined.empty:
        logger.warning(
            "No data found under %s — run the broad mapping sweep first", args.root
        )
        return
    objectives = getattr(args, "objectives", DEFAULT_OBJECTIVES)
    render_atlas(
        combined,
        voids,
        args.root / "atlas.html",
        args.task if not args.multi_task else None,
        multi_task=args.multi_task,
        objectives=objectives,
    )
    if args.png:
        _atlas_png(
            combined, args.png, args.task if not args.multi_task else "multi-task"
        )
