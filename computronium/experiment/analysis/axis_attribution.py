"""Axis Attribution Analysis (Phase D2).

Computes SHAP/ICE attributions for each ontology axis on objectives
to understand which axes drive performance.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.ensemble import RandomForestRegressor

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore


@dataclass(frozen=True, slots=True)
class AttributionResult:
    """Result of axis attribution analysis."""

    axis: str
    metric: str
    shap_values: dict[str, float]  # primitive -> mean |SHAP|
    ice_curves: dict[str, np.ndarray]  # primitive -> ICE curve
    feature_importance: dict[str, float]  # primitive -> importance
    interaction_effects: dict[str, float]  # axis pair -> interaction strength
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AttributionConfig:
    """Configuration for attribution analysis."""

    n_samples_shap: int = 100
    n_ice_points: int = 20
    random_state: int = 42
    n_estimators: int = 100


def _prepare_design_matrix(
    records: list[Any],
    axes: list[str],
    metric: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, list[str]]]:
    """Prepare design matrix from records for ML-based attribution."""
    # Collect unique primitive values per axis
    axis_values = {axis: sorted({getattr(r, axis) for r in records}) for axis in axes}

    # Build design matrix
    X_rows = []
    y_values = []

    for r in records:
        row = {}
        for axis in axes:
            val = getattr(r, axis)
            # One-hot encode
            for primitive in axis_values[axis]:
                row[f"{axis}_{primitive}"] = 1.0 if val == primitive else 0.0

        metric_val = r.payload.get(metric)
        if metric_val is not None:
            X_rows.append(row)
            y_values.append(float(metric_val))

    # Convert to numpy
    feature_names = list(X_rows[0].keys()) if X_rows else []
    X = np.array([[row[f] for f in feature_names] for row in X_rows])
    y = np.array(y_values)

    return X, y, axis_values


def compute_shap_attribution(
    records: list[Any],
    axes: list[str],
    metric: str,
    config: AttributionConfig | None = None,
) -> dict[str, dict[str, float]]:
    """Compute SHAP-like attribution using tree-based feature importance.

    Note: This uses Random Forest feature importance as a proxy for SHAP.
    For true SHAP values, use the shap library directly.
    """
    config = config or AttributionConfig()

    X, y, axis_values = _prepare_design_matrix(records, axes, metric)
    if len(X) == 0:
        return {}

    # Train a random forest
    rf = RandomForestRegressor(
        n_estimators=config.n_estimators,
        random_state=config.random_state,
        n_jobs=-1,
    )
    rf.fit(X, y)

    # Get feature importances
    importances = rf.feature_importances_

    # Aggregate by axis
    feature_names = []
    for axis in axes:
        for primitive in axis_values[axis]:
            feature_names.append(f"{axis}_{primitive}")

    shap_by_axis = {}
    for axis in axes:
        shap_by_axis[axis] = {}
        for primitive in axis_values[axis]:
            idx = feature_names.index(f"{axis}_{primitive}")
            shap_by_axis[axis][primitive] = float(importances[idx])

    return shap_by_axis


def compute_ice_curves(
    records: list[Any],
    axes: list[str],
    metric: str,
    config: AttributionConfig | None = None,
) -> dict[str, dict[str, np.ndarray]]:
    """Compute Individual Conditional Expectation (ICE) curves for each axis."""
    config = config or AttributionConfig()

    X, y, axis_values = _prepare_design_matrix(records, axes, metric)
    if len(X) == 0:
        return {}

    # Train a model
    rf = RandomForestRegressor(
        n_estimators=config.n_estimators,
        random_state=config.random_state,
        n_jobs=-1,
    )
    rf.fit(X, y)

    # Feature names
    feature_names = []
    for axis in axes:
        for primitive in axis_values[axis]:
            feature_names.append(f"{axis}_{primitive}")

    ice_by_axis = {}
    for axis in axes:
        ice_by_axis[axis] = {}
        for primitive in axis_values[axis]:
            # Create partial dependence for this feature
            feature_idx = feature_names.index(f"{axis}_{primitive}")

            # Sample values to evaluate at
            grid = np.linspace(0, 1, config.n_ice_points)

            # For each sample, vary this feature and predict
            ice_curves = []
            for sample_idx in range(min(config.n_samples_shap, len(X))):
                sample = X[sample_idx].copy()
                predictions = []
                for val in grid:
                    sample[feature_idx] = val
                    pred = rf.predict(sample.reshape(1, -1))[0]
                    predictions.append(pred)
                ice_curves.append(predictions)

            ice_by_axis[axis][primitive] = np.array(ice_curves)

    return ice_by_axis


def analyze_axis_importance(
    records: list[Any],
    axes: list[str],
    metric: str,
    config: AttributionConfig | None = None,
) -> AttributionResult:
    """Full axis attribution analysis."""
    config = config or AttributionConfig()

    shap_values = compute_shap_attribution(records, axes, metric, config)
    ice_curves = compute_ice_curves(records, axes, metric, config)

    # Feature importance from SHAP
    X, y, axis_values = _prepare_design_matrix(records, axes, metric)
    rf = RandomForestRegressor(
        n_estimators=config.n_estimators,
        random_state=config.random_state,
        n_jobs=-1,
    )
    if len(X) > 0:
        rf.fit(X, y)
        feature_names = []
        for axis in axes:
            for primitive in axis_values[axis]:
                feature_names.append(f"{axis}_{primitive}")
        importance = {
            k: float(v) for k, v in zip(feature_names, rf.feature_importances_)
        }
    else:
        importance = {}

    # Interaction effects (simplified: correlation between axis effects)
    interaction_effects = {}
    if len(axes) >= 2:
        for i, axis1 in enumerate(axes):
            for axis2 in axes[i + 1 :]:
                # Compute interaction via variance of combined effects
                key = f"{axis1}×{axis2}"
                # Simple proxy: variance of product of one-hot encoded features
                vals1 = np.array([getattr(r, axis1) for r in records])
                vals2 = np.array([getattr(r, axis2) for r in records])
                # Use categorical encoding
                from sklearn.preprocessing import LabelEncoder

                le1 = LabelEncoder().fit(vals1)
                le2 = LabelEncoder().fit(vals2)
                encoded1 = le1.transform(vals1)
                encoded2 = le2.transform(vals2)
                interaction_effects[key] = (
                    float(np.corrcoef(encoded1, encoded2)[0, 1])
                    if len(vals1) > 1
                    else 0.0
                )

    return AttributionResult(
        axis="all",
        metric=metric,
        shap_values={k: v for d in shap_values.values() for k, v in d.items()},
        ice_curves={k: v for d in ice_curves.values() for k, v in d.items()},
        feature_importance=importance,
        interaction_effects=interaction_effects,
        metadata={
            "n_records": len(records),
            "axes": axes,
            "metric": metric,
            "n_samples_shap": config.n_samples_shap,
        },
    )


class AxisAttributionAnalyzer:
    """Analyze axis attributions on objectives."""

    def __init__(
        self,
        store: RecordStore,
        run_id: str,
        config: AttributionConfig | None = None,
    ):
        self.store = store
        self.run_id = run_id
        self.config = config or AttributionConfig()

    def analyze(
        self, axes: list[str] | None = None, metric: str = "val_acc"
    ) -> AttributionResult:
        """Run attribution analysis."""
        from computronium.experiment.surface.report import ReportGenerator

        generator = ReportGenerator(self.store)
        records = generator._store.query_records(run_id=self.run_id)

        if axes is None:
            axes = [
                "substrate",
                "geometry",
                "dynamics",
                "plasticity",
                "credit",
                "update",
            ]

        return analyze_axis_importance(records, axes, metric, self.config)
