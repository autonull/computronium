#!/usr/bin/env python
"""Fit cost model from cells.jsonl data.

Fits walltime_s ~ log(param_count) + geometry + dynamics + credit + update
for use in SEC budget allocation policy.
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def load_cells_from_results(results_dir: Path) -> pd.DataFrame:
    """Load all measured cells from result directories."""
    all_cells = []
    for cells_file in results_dir.glob("**/cells.jsonl"):
        try:
            with Path(cells_file).open() as f:
                for line in f:
                    cell = json.loads(line)
                    screen = cell.get("screen", {})
                    record = cell.get("record", {})
                    payload = record.get("payload", {}) if record else {}
                    if screen.get("status") == "MEASURED":
                        params = record.get("params", {}) if record else {}
                        all_cells.append({
                            "primitive": screen.get("primitive"),
                            "geometry": screen.get("box", {}).get("geometry"),
                            "credit": screen.get("box", {}).get("credit"),
                            "update": screen.get("box", {}).get("update"),
                            "dynamics": screen.get("box", {}).get("dynamics"),
                            "substrate": screen.get("box", {}).get("substrate"),
                            "plasticity": screen.get("box", {}).get("plasticity"),
                            "val_acc": screen.get("val_acc"),
                            "walltime_s": payload.get("walltime_s"),
                            "params": params,
                            "task": screen.get("box", {}).get("task_id"),
                        })
        except Exception as e:
            print(f"Error loading {cells_file}: {e}")

    return pd.DataFrame(all_cells)


def estimate_param_count(params: dict) -> int:
    """Estimate parameter count from box params."""
    hidden_dim = 128
    depth = 2
    for k, v in params.items():
        if "hidden_dim" in k:
            hidden_dim = int(v)
        elif "depth" in k or "num_layers" in k:
            depth = int(v)
    return hidden_dim * hidden_dim * depth


def fit_cost_model(df: pd.DataFrame) -> tuple[LinearRegression, list[str]]:
    """Fit linear regression for walltime prediction."""

    # Estimate param count
    df["param_count_est"] = df["params"].apply(estimate_param_count)
    df["log_params"] = np.log(df["param_count_est"])

    # Prepare features
    features = []
    targets = []
    for _, row in df.iterrows():
        if pd.notna(row["walltime_s"]) and pd.notna(row["param_count_est"]):
            feat = [
                row["log_params"],
                1 if row["geometry"] != "feedforward" else 0,
                1 if row["dynamics"] != "instantaneous" else 0,
                1 if row["credit"] != "gradient" else 0,
                1 if row["update"] != "euclidean" else 0,
            ]
            features.append(feat)
            targets.append(row["walltime_s"])

    X = np.array(features)
    y = np.array(targets)

    feature_names = [
        "log_params",
        "non_feedforward_geom",
        "non_instantaneous_dyn",
        "non_gradient_credit",
        "non_euclidean_update",
    ]

    model = LinearRegression()
    model.fit(X, y)

    return model, feature_names


def predict_walltime(
    model: LinearRegression, feature_names: list[str], primitive_info: dict
) -> float:
    """Predict walltime for a primitive configuration."""
    # Extract features
    log_params = np.log(primitive_info.get("param_count", 32768))
    feat = [
        log_params,
        1 if primitive_info.get("geometry") != "feedforward" else 0,
        1 if primitive_info.get("dynamics") != "instantaneous" else 0,
        1 if primitive_info.get("credit") != "gradient" else 0,
        1 if primitive_info.get("update") != "euclidean" else 0,
    ]
    X = np.array([feat])
    return float(model.predict(X)[0])


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fit cost model from SEC results")
    parser.add_argument(
        "--results-dir", type=Path, default=Path("results"), help="Results directory"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("configs/cost_model.pkl"),
        help="Output model file",
    )
    args = parser.parse_args()

    print(f"Loading cells from {args.results_dir}...")
    df = load_cells_from_results(args.results_dir)
    print(f"Loaded {len(df)} measured cells")

    # Filter to cells with walltime
    df_wt = df[df["walltime_s"].notna()]
    print(f"Cells with walltime: {len(df_wt)}")

    model, feature_names = fit_cost_model(df_wt)

    print("\nModel coefficients:")
    for name, coef in zip(feature_names, model.coef_):
        print(f"  {name}: {coef:.4f}")
    print(f"  Intercept: {model.intercept_:.4f}")

    # Compute R^2 properly
    X = np.array([
        [
            row["log_params"],
            1 if row["geometry"] != "feedforward" else 0,
            1 if row["dynamics"] != "instantaneous" else 0,
            1 if row["credit"] != "gradient" else 0,
            1 if row["update"] != "euclidean" else 0,
        ]
        for _, row in df_wt.iterrows()
    ])
    y = df_wt["walltime_s"].values
    r2 = model.score(X, y)
    print(f"  R^2: {r2:.4f}")

    # Save model
    args.out.parent.mkdir(parents=True, exist_ok=True)
    model_data = {
        "model": model,
        "feature_names": feature_names,
        "fitted_at": pd.Timestamp.now().isoformat(),
        "n_samples": len(df_wt),
        "r2": r2,
    }
    with Path(args.out).open("wb") as f:
        pickle.dump(model_data, f)
    print(f"\nModel saved to {args.out}")


if __name__ == "__main__":
    main()
