"""Mediation Analysis (Phase D2).

Tests whether stability metrics mediate the relationship between
credit assignment and accuracy (or other objectives).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy import stats

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


@dataclass(frozen=True, slots=True)
class MediationResult:
    """Result of mediation analysis."""

    independent_var: str  # e.g., "credit"
    mediator_var: str  # e.g., "stability_margin"
    dependent_var: str  # e.g., "val_acc"
    total_effect: float
    direct_effect: float
    indirect_effect: float
    proportion_mediated: float
    sobel_test_statistic: float
    sobel_p_value: float
    bootstrap_ci: tuple[float, float]
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class MediationConfig:
    """Configuration for mediation analysis."""

    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    random_state: int = 42


def _encode_categorical(values: list[Any]) -> np.ndarray:
    """Encode categorical values as integers."""
    unique = sorted(set(values))
    mapping = {v: i for i, v in enumerate(unique)}
    return np.array([mapping[v] for v in values])


def _extract_variables(
    records: list[Record],
    independent: str,
    mediator: str,
    dependent: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract X, M, Y arrays from records."""
    X = []
    M = []
    Y = []

    for r in records:
        x_val = getattr(r, independent, None)
        m_val = r.payload.get(mediator)
        y_val = r.payload.get(dependent)

        if x_val is not None and m_val is not None and y_val is not None:
            X.append(x_val)
            M.append(float(m_val))
            Y.append(float(y_val))

    if not X:
        return np.array([]), np.array([]), np.array([])

    # Encode X if categorical
    X_arr = _encode_categorical(X)
    M_arr = np.array(M)
    Y_arr = np.array(Y)

    return X_arr, M_arr, Y_arr


def _regression_coefficient(X: np.ndarray, Y: np.ndarray) -> tuple[float, float]:
    """Simple linear regression, returns (coef, se)."""
    if len(X) < 2:
        return 0.0, 0.0
    # Add intercept
    X_design = np.column_stack([np.ones(len(X)), X])
    try:
        coef = np.linalg.lstsq(X_design, Y, rcond=None)[0]
        residuals = Y - X_design @ coef
        se = np.sqrt(
            np.sum(residuals**2)
            / (len(X) - 2)
            * np.linalg.inv(X_design.T @ X_design)[1, 1]
        )
        return float(coef[1]), float(se)
    except np.linalg.LinAlgError:
        return 0.0, 0.0


def analyze_mediation(
    records: list[Record],
    independent: str,  # e.g., "credit"
    mediator: str,  # e.g., "stability_margin"
    dependent: str,  # e.g., "val_acc"
    config: MediationConfig | None = None,
) -> MediationResult:
    """Analyze mediation: X -> M -> Y."""
    config = config or MediationConfig()

    X, M, Y = _extract_variables(records, independent, mediator, dependent)

    if len(X) < 10:
        return MediationResult(
            independent_var=independent,
            mediator_var=mediator,
            dependent_var=dependent,
            total_effect=0.0,
            direct_effect=0.0,
            indirect_effect=0.0,
            proportion_mediated=0.0,
            sobel_test_statistic=0.0,
            sobel_p_value=1.0,
            bootstrap_ci=(0.0, 0.0),
            metadata={"error": "Insufficient data", "n_samples": len(X)},
        )

    # Path a: X -> M
    a_coef, a_se = _regression_coefficient(X, M)

    # Path b: M -> Y (controlling for X)
    # Multiple regression: Y ~ X + M
    X_design = np.column_stack([np.ones(len(X)), X, M])
    try:
        coefs = np.linalg.lstsq(X_design, Y, rcond=None)[0]
        b_coef = float(coefs[2])  # M coefficient
        # Direct effect c': X -> Y controlling for M
        c_prime_coef = float(coefs[1])
        # Calculate SE for b
        residuals = Y - X_design @ coefs
        mse = np.sum(residuals**2) / (len(X) - 3)
        cov = mse * np.linalg.inv(X_design.T @ X_design)
        b_se = float(np.sqrt(cov[2, 2]))
    except np.linalg.LinAlgError:
        b_coef, b_se = 0.0, 0.0
        c_prime_coef = 0.0

    # Total effect c: X -> Y
    c_coef, _c_se = _regression_coefficient(X, Y)

    # Indirect effect
    indirect = a_coef * b_coef

    # Proportion mediated
    prop_mediated = indirect / c_coef if abs(c_coef) > 1e-10 else 0.0

    # Sobel test
    sobel_se = np.sqrt(a_coef**2 * b_se**2 + b_coef**2 * a_se**2)
    sobel_stat = indirect / sobel_se if sobel_se > 0 else 0.0
    sobel_p = 2 * (1 - stats.norm.cdf(abs(sobel_stat)))

    # Bootstrap CI for indirect effect
    np.random.seed(config.random_state)
    bootstrap_indirect = []
    for _ in range(config.n_bootstrap):
        idx = np.random.choice(len(X), len(X), replace=True)
        X_b, M_b, Y_b = X[idx], M[idx], Y[idx]
        a_b, _ = _regression_coefficient(X_b, M_b)
        X_design_b = np.column_stack([np.ones(len(X_b)), X_b, M_b])
        try:
            coefs_b = np.linalg.lstsq(X_design_b, Y_b, rcond=None)[0]
            b_b = float(coefs_b[2])
            bootstrap_indirect.append(a_b * b_b)
        except np.linalg.LinAlgError:
            continue

    if bootstrap_indirect:
        alpha = 1 - config.confidence_level
        ci_lower = float(np.percentile(bootstrap_indirect, 100 * alpha / 2))
        ci_upper = float(np.percentile(bootstrap_indirect, 100 * (1 - alpha / 2)))
    else:
        ci_lower, ci_upper = 0.0, 0.0

    return MediationResult(
        independent_var=independent,
        mediator_var=mediator,
        dependent_var=dependent,
        total_effect=float(c_coef),
        direct_effect=float(c_prime_coef),
        indirect_effect=float(indirect),
        proportion_mediated=float(prop_mediated),
        sobel_test_statistic=float(sobel_stat),
        sobel_p_value=float(sobel_p),
        bootstrap_ci=(ci_lower, ci_upper),
        metadata={
            "n_samples": len(X),
            "a_coef": float(a_coef),
            "b_coef": float(b_coef),
            "a_se": float(a_se),
            "b_se": float(b_se),
        },
    )


class MediationAnalyzer:
    """Analyze mediation effects."""

    def __init__(
        self,
        store: RecordStore,
        run_id: str,
        config: MediationConfig | None = None,
    ):
        self.store = store
        self.run_id = run_id
        self.config = config or MediationConfig()

    def analyze(
        self,
        independent: str,
        mediator: str,
        dependent: str,
    ) -> MediationResult:
        """Run mediation analysis."""
        from computronium.experiment.surface.report import ReportGenerator

        generator = ReportGenerator(self.store)
        records = generator._store.query_records(run_id=self.run_id)

        return analyze_mediation(records, independent, mediator, dependent, self.config)

    def analyze_all_mediators(
        self,
        independent: str,
        dependent: str,
        mediators: list[str] | None = None,
    ) -> list[MediationResult]:
        """Test multiple mediators."""
        if mediators is None:
            mediators = [
                "stability_margin",
                "spectral_radius",
                "lyapunov_exponent",
                "settle_steps",
            ]

        results = []
        for mediator in mediators:
            try:
                result = self.analyze(independent, mediator, dependent)
                results.append(result)
            except Exception:
                continue

        return results
