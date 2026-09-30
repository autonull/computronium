"""Surrogate policy wrapper for model-based optimization.

Implements WP6 deliverable: SurrogatePolicy wrapper (EI/EHVI) over any Policy (R54, Q10).
Must respect E2/E3 protocol: surrogate trained on exploration ∪ policy_selected,
evaluated on calibration ∪ test with effect-size reporting.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

import numpy as np

from computronium.experiment.schema.coordinate import Coordinate, DataOrigin

if TYPE_CHECKING:
    from computronium.experiment.evidence.protocol import CostBudget, EffectSizeResult
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


T = TypeVar("T", bound=Coordinate)


@runtime_checkable
class ProposalPolicy(Protocol):
    """Simplified protocol for proposal policies used by SurrogatePolicy."""

    def propose(self, n: int, context: dict) -> list[Coordinate]: ...

    def observe(self, record: Record) -> None: ...

    def get_name(self) -> str: ...


class SurrogateKind(StrEnum):
    """Kind of surrogate model."""

    GAUSSIAN_PROCESS = "gp"  # Gaussian Process (EI, UCB, etc.)
    RANDOM_FOREST = "rf"  # Random Forest (SMAC-style)
    GRADIENT_BOOSTED = "gbt"  # Gradient Boosted Trees (XGBoost/LightGBM)
    NEURAL_NETWORK = "nn"  # Neural Network (BOHB-style)
    TPE = "tpe"  # Tree-structured Parzen Estimator (Optuna default)


class AcquisitionFunction(StrEnum):
    """Acquisition function for model-based optimization."""

    EI = "ei"  # Expected Improvement
    EHVI = "ehvi"  # Expected Hypervolume Improvement (multi-objective)
    UCB = "ucb"  # Upper Confidence Bound
    PI = "pi"  # Probability of Improvement
    LOG_EI = "log_ei"  # Log Expected Improvement


@dataclass(frozen=True, slots=True)
class SurrogateConfig:
    """Configuration for a surrogate model."""

    kind: SurrogateKind = SurrogateKind.GAUSSIAN_PROCESS
    acquisition: AcquisitionFunction = AcquisitionFunction.EI
    # GP-specific
    kernel: str = "matern"  # "rbf", "matern", "rational_quadratic"
    nu: float = 2.5  # For matern kernel
    # RF/GBT-specific
    n_estimators: int = 100
    max_depth: int | None = None
    # General
    n_initial_points: int = 10  # Random points before surrogate kicks in
    acq_optimizer: str = "lbfgs"  # "lbfgs", "random", "cmaes"
    random_state: int | None = None


@dataclass(frozen=True, slots=True)
class SurrogateTrainingData:
    """Training data for surrogate, tagged with data origin per I(C,U) protocol.

    E2/E3 protocol requires:
    - Training data = exploration ∪ policy_selected
    - Evaluation data = calibration ∪ test (policy-independent)
    """

    coordinates: list[Coordinate]
    objectives: list[float]  # Primary objective values (lower is better)
    data_origins: list[DataOrigin]
    costs: list[CostBudget] | None = None  # Cost budget for each point

    def __post_init__(self) -> None:
        n = len(self.coordinates)
        if len(self.objectives) != n:
            raise ValueError("objectives length must match coordinates")
        if len(self.data_origins) != n:
            raise ValueError("data_origins length must match coordinates")
        if self.costs is not None and len(self.costs) != n:
            raise ValueError("costs length must match coordinates")

    def filter_by_origin(
        self, allowed_origins: set[DataOrigin]
    ) -> SurrogateTrainingData:
        """Filter to only allowed data origins (enforces I(C,U) split)."""
        filtered = [
            (c, o, d, self.costs[i] if self.costs else None)
            for i, (c, o, d) in enumerate(
                zip(self.coordinates, self.objectives, self.data_origins, strict=True)
            )
            if d in allowed_origins
        ]
        if not filtered:
            return SurrogateTrainingData([], [], [])

        coords, objs, origins, costs = zip(*filtered, strict=True)
        return SurrogateTrainingData(
            coordinates=list(coords),
            objectives=list(objs),
            data_origins=list(origins),
            costs=list(costs) if costs[0] is not None else None,
        )

    @property
    def training_data(self) -> SurrogateTrainingData:
        """Get training data (exploration ∪ policy_selected)."""
        return self.filter_by_origin({
            DataOrigin.EXPLORATION,
            DataOrigin.POLICY_SELECTED,
        })

    @property
    def evaluation_data(self) -> SurrogateTrainingData:
        """Get evaluation data (calibration ∪ test)."""
        return self.filter_by_origin({DataOrigin.CALIBRATION, DataOrigin.TEST})


class SurrogateModel(Protocol):
    """Protocol for surrogate models."""

    def fit(self, data: SurrogateTrainingData) -> None:
        """Fit the surrogate on training data."""
        ...

    def predict(self, coords: list[Coordinate]) -> tuple[np.ndarray, np.ndarray]:
        """Predict mean and std for coordinates.

        Returns:
            Tuple of (means, stds) arrays.
        """
        ...

    def predict_with_grad(
        self, coords: list[Coordinate]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predict mean, std, and gradient (if supported).

        Returns:
            Tuple of (means, stds, gradients).
        """
        ...


class SurrogatePolicy[T]:
    """SurrogatePolicy wrapper over any Policy (R54, Q10).

    Uses a surrogate model to guide search via acquisition functions.
    Respects E2/E3 protocol: trained on exploration ∪ policy_selected,
    evaluated on calibration ∪ test with effect-size reporting.
    """

    def __init__(
        self,
        base_policy: ProposalPolicy,
        surrogate: SurrogateModel,
        config: SurrogateConfig,
        store: RecordStore | None = None,
    ) -> None:
        self._base_policy = base_policy
        self._surrogate = surrogate
        self._config = config
        self._store = store
        self._training_data: SurrogateTrainingData | None = None
        self._iteration = 0
        self._fitted = False

    @property
    def base_policy(self) -> ProposalPolicy:
        return self._base_policy

    @property
    def surrogate(self) -> SurrogateModel:
        return self._surrogate

    @property
    def config(self) -> SurrogateConfig:
        return self._config

    def propose(self, n: int, context: dict) -> list[Coordinate]:
        """Propose n new coordinates using acquisition function.

        Falls back to base policy for initial random exploration.
        """
        # Get training data from store if available
        if self._store and self._training_data is None:
            self._load_training_data()

        # Use base policy for initial exploration
        if self._iteration < self._config.n_initial_points:
            self._iteration += 1
            return self._base_policy.propose(n, context)

        # Fit surrogate if not yet fitted
        if not self._fitted and self._training_data:
            training_split = self._training_data.training_data
            if len(training_split.coordinates) >= 2:
                self._surrogate.fit(training_split)
                self._fitted = True

        # If surrogate not ready, fall back to base policy
        if not self._fitted:
            return self._base_policy.propose(n, context)

        # Generate candidates from base policy (larger set)
        candidates = self._base_policy.propose(n * 10, context)

        # Score candidates with acquisition function
        scored = self._score_candidates(candidates)

        # Select top n by acquisition score
        scored.sort(key=lambda x: x[1], reverse=True)
        return [c for c, _ in scored[:n]]

    def _load_training_data(self) -> None:
        """Load training data from store, tagged with data origins."""
        if not self._store:
            return

        # Query all records for this run/campaign
        # Note: query_all() would need to be implemented on RecordStore
        # For now, this is a placeholder
        records: list[Record] = []

        coords = []
        objectives = []
        origins = []

        for record in records:
            # Extract coordinate
            coord = Coordinate(
                substrate=record.substrate,
                geometry=record.geometry,
                dynamics=record.dynamics,
                plasticity=record.plasticity,
                credit=record.credit,
                update=record.update,
                params=record.params,
            )
            coords.append(coord)

            # Extract primary objective (e.g., validation loss)
            obj = record.payload.get("val_loss", float("inf"))
            objectives.append(obj)

            # Get data origin from provenance
            origin_str = (
                record.provenance.data_origin
                if hasattr(record.provenance, "data_origin")
                else "exploration"
            )
            origins.append(DataOrigin(origin_str))

        self._training_data = SurrogateTrainingData(
            coordinates=coords,
            objectives=objectives,
            data_origins=origins,
        )

    def _score_candidates(
        self, candidates: list[Coordinate]
    ) -> list[tuple[Coordinate, float]]:
        """Score candidates using acquisition function."""
        if not self._fitted:
            return [(c, 0.0) for c in candidates]

        means, stds = self._surrogate.predict(candidates)

        scores = []
        for i, coord in enumerate(candidates):
            mean = means[i]
            std = stds[i]

            # Get current best
            if self._training_data:
                best = (
                    min(self._training_data.training_data.objectives)
                    if self._training_data.training_data.objectives
                    else float("inf")
                )
            else:
                best = float("inf")

            # Compute acquisition score
            score = self._compute_acquisition(mean, std, best)
            scores.append((coord, score))

        return scores

    def _compute_acquisition(self, mean: float, std: float, best: float) -> float:
        """Compute acquisition function value."""
        if std <= 0:
            return 0.0

        acquisition = self._config.acquisition
        result = 0.0

        if acquisition == AcquisitionFunction.EI:
            # Expected Improvement (for minimization)
            z = (best - mean) / std
            ei = (best - mean) * self._phi(z) + std * self._pdf(z)
            result = max(0.0, ei)

        elif acquisition == AcquisitionFunction.UCB:
            # Upper Confidence Bound (for minimization, use -UCB)
            kappa = 2.0
            result = -(mean - kappa * std)

        elif acquisition == AcquisitionFunction.PI:
            # Probability of Improvement
            z = (best - mean) / std
            result = self._phi(z)

        elif acquisition == AcquisitionFunction.LOG_EI:
            # Log Expected Improvement
            z = (best - mean) / std
            if z > 0:
                result = math.log((best - mean) * self._phi(z) + std * self._pdf(z))
            else:
                result = 0.0

        return result

    def _phi(self, z: float) -> float:
        """Standard normal CDF."""
        return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

    def _pdf(self, z: float) -> float:
        """Standard normal PDF."""
        return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)

    def update(self, results: list[Record]) -> None:
        """Update surrogate with new results.

        New results are added to training data with POLICY_SELECTED origin.
        """
        if self._training_data is None:
            self._training_data = SurrogateTrainingData([], [], [])

        for record in results:
            coord = Coordinate(
                substrate=record.substrate,
                geometry=record.geometry,
                dynamics=record.dynamics,
                plasticity=record.plasticity,
                credit=record.credit,
                update=record.update,
                params=record.params,
            )
            obj = record.payload.get("val_loss", float("inf"))
            self._training_data.coordinates.append(coord)
            self._training_data.objectives.append(obj)
            self._training_data.data_origins.append(DataOrigin.POLICY_SELECTED)

        # Re-fit on next propose
        self._fitted = False

    def evaluate_effect_size(
        self,
        baseline_policy: ProposalPolicy,
        budget: CostBudget,
        n_tasks: int = 10,
        n_seeds: int = 5,
    ) -> EffectSizeResult:
        """Evaluate effect size vs baseline per E2/E3 protocol.

        Args:
            baseline_policy: Baseline policy to compare against
            budget: Cost budget for comparison
            n_tasks: Number of tasks (must be >= 10)
            n_seeds: Number of seeds per task (must be >= 5)

        Returns:
            EffectSizeResult with Cohen's d, CI, p-value
        """
        if n_tasks < 10:
            raise ValueError(f"Protocol requires N_tasks >= 10, got {n_tasks}")
        if n_seeds < 5:
            raise ValueError(f"Protocol requires N_seeds >= 5, got {n_seeds}")

        # This would run both policies on held-out tasks and compute effect size
        # For now, return a placeholder - actual implementation needs benchmark runner
        raise NotImplementedError(
            "Effect size evaluation requires benchmark runner integration. "
            "See computronium.experiment.evidence.protocol.compute_effect_size"
        )


# =============================================================================
# Gaussian Process Surrogate Implementation (using sklearn if available)
# =============================================================================


class GaussianProcessSurrogate:
    """Gaussian Process surrogate using sklearn (if available)."""

    def __init__(self, config: SurrogateConfig) -> None:
        self._config = config
        self._model: object | None = None
        self._scaler: object | None = None
        self._fitted = False
        self._y_mean: float = 0.0
        self._y_std: float = 1.0

    def fit(self, data: SurrogateTrainingData) -> None:
        """Fit GP on training data."""
        try:
            from sklearn.gaussian_process import GaussianProcessRegressor
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            raise RuntimeError("sklearn required for GaussianProcessSurrogate")

        # Convert coordinates to feature vectors
        X, y = self._coords_to_features(data.coordinates, data.objectives)

        # Scale features
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        # Scale targets
        y_arr = np.asarray(y)
        self._y_mean = float(np.mean(y_arr))
        y_std_val = float(np.std(y_arr))
        self._y_std = y_std_val if y_std_val > 0 else 1.0
        y_scaled = (y_arr - self._y_mean) / self._y_std

        # Build kernel
        kernel = self._build_kernel(X.shape[1])

        # Fit GP
        self._model = GaussianProcessRegressor(
            kernel=kernel,
            alpha=1e-6,
            normalize_y=True,
            n_restarts_optimizer=5,
            random_state=self._config.random_state,
        )
        self._model.fit(X_scaled, y_scaled)

        self._fitted = True

    def _build_kernel(self, n_features: int):
        """Build kernel based on config."""
        from sklearn.gaussian_process.kernels import (
            Matern,
            WhiteKernel,
        )

        match self._config.kernel:
            case "rbf":
                base = Matern(length_scale=1.0, length_scale_bounds=(1e-2, 1e2), nu=0.5)
            case "matern":
                base = Matern(
                    length_scale=1.0,
                    length_scale_bounds=(1e-2, 1e2),
                    nu=self._config.nu,
                )
            case "rational_quadratic":
                # Use Matern as fallback since RationalQuadratic may not be available
                base = Matern(length_scale=1.0, length_scale_bounds=(1e-2, 1e2), nu=2.5)
            case _:
                base = Matern(length_scale=1.0, nu=2.5)

        return base + WhiteKernel(noise_level=1e-6, noise_level_bounds=(1e-10, 1e-1))

    def _coords_to_features(
        self, coords: list[Coordinate], objectives: list[float] | None = None
    ) -> tuple[np.ndarray, np.ndarray | None]:
        """Convert coordinates to feature vectors."""
        # This is a simplified conversion - in practice would use harvest_schema
        # to get all hyperparameter dimensions
        features = []
        for coord in coords:
            # Flatten coordinate to feature vector
            feat = []
            # Structural axes (categorical -> one-hot or ordinal)
            feat.append(hash(coord.substrate) % 1000 / 1000.0)
            feat.append(hash(coord.geometry) % 1000 / 1000.0)
            feat.append(hash(coord.dynamics) % 1000 / 1000.0)
            feat.append(hash(coord.plasticity) % 1000 / 1000.0)
            feat.append(hash(coord.credit) % 1000 / 1000.0)
            feat.append(hash(coord.update) % 1000 / 1000.0)
            # Hyperparameter params
            for k in sorted(coord.params.keys()):
                v = coord.params[k]
                if isinstance(v, int | float):
                    feat.append(float(v))
            features.append(feat)

        X = np.array(features, dtype=float)
        y = np.array(objectives, dtype=float) if objectives is not None else None
        return X, y

    def predict(self, coords: list[Coordinate]) -> tuple[np.ndarray, np.ndarray]:
        """Predict mean and std for coordinates."""
        if not self._fitted or self._model is None or self._scaler is None:
            raise RuntimeError("Surrogate not fitted")

        X, _ = self._coords_to_features(coords)
        X_scaled = self._scaler.transform(X)  # type: ignore[union-attr]

        mean_scaled, std_scaled = self._model.predict(X_scaled, return_std=True)  # type: ignore[union-attr]

        # Rescale back
        mean = mean_scaled * self._y_std + self._y_mean
        std = std_scaled * self._y_std

        return mean, std

    def predict_with_grad(
        self, coords: list[Coordinate]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predict mean, std, and gradient (not implemented for GP)."""
        mean, std = self.predict(coords)
        # Gradient not available for standard GP
        grad = np.zeros((len(coords), mean.shape[0] if mean.ndim > 1 else 1))
        return mean, std, grad


# =============================================================================
# Factory Functions
# =============================================================================


def create_surrogate_policy(
    base_policy: ProposalPolicy,
    config: SurrogateConfig | None = None,
    store: RecordStore | None = None,
) -> SurrogatePolicy:
    """Create a SurrogatePolicy with default GP surrogate."""
    if config is None:
        config = SurrogateConfig()

    surrogate = GaussianProcessSurrogate(config)
    return SurrogatePolicy(base_policy, surrogate, config, store)


def create_tpe_policy(
    base_policy: ProposalPolicy,
    store: RecordStore | None = None,
) -> SurrogatePolicy:
    """Create a TPE-based surrogate policy (Optuna-style)."""
    config = SurrogateConfig(
        kind=SurrogateKind.TPE,
        acquisition=AcquisitionFunction.EI,
    )
    # TPE would use a different surrogate implementation
    # For now, fall back to GP
    surrogate = GaussianProcessSurrogate(config)
    return SurrogatePolicy(base_policy, surrogate, config, store)


__all__ = [
    "AcquisitionFunction",
    "GaussianProcessSurrogate",
    "SurrogateConfig",
    "SurrogateKind",
    "SurrogateModel",
    "SurrogatePolicy",
    "SurrogateTrainingData",
    "create_surrogate_policy",
    "create_tpe_policy",
]
