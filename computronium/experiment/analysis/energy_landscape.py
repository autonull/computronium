"""Energy Landscape Analysis (Phase D1).

Computes 2D slices of the energy landscape via PCA of activation space
for small models to visualize attractor basins and energy minima.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import torch
from sklearn.decomposition import PCA

if TYPE_CHECKING:
    from collections.abc import Callable

    from stability.state import SystemContext

from stability.state import CompositeState, activity_tensor


def _get_primary_activity(state: CompositeState) -> torch.Tensor:
    """Get the primary activity tensor from a composite state."""
    # Use the first activity key that contains a tensor
    for key, value in state.activity.items():
        try:
            return activity_tensor(state.activity, key)
        except TypeError:
            continue
    # Fallback: try the first key
    first_key = next(iter(state.activity))
    return activity_tensor(state.activity, first_key)


def _perturb_state(
    state: CompositeState, scale: float, generator: torch.Generator | None = None
) -> CompositeState:
    """Create a perturbed copy of a composite state."""
    primary_act = _get_primary_activity(state)
    perturbation = torch.randn_like(primary_act, generator=generator) * scale

    new_activity = {}
    for key, value in state.activity.items():
        if isinstance(value, torch.Tensor):
            new_activity[key] = value + perturbation
        elif isinstance(value, list):
            new_activity[key] = [
                v + torch.randn_like(v, generator=generator) * scale for v in value
            ]
        else:
            new_activity[key] = value

    return CompositeState(
        activity=new_activity,
        plastic=state.plastic,
        substrate=state.substrate,
    )


@dataclass(frozen=True, slots=True)
class EnergyLandscapeResult:
    """Result of energy landscape analysis."""

    grid_x: np.ndarray
    grid_y: np.ndarray
    energy_values: np.ndarray
    pca_components: np.ndarray
    pca_explained_variance: np.ndarray
    attractor_points: list[tuple[float, float]]  # PCA coordinates of attractors
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class EnergyLandscapeConfig:
    """Configuration for energy landscape analysis."""

    grid_resolution: int = 30
    grid_range: float = 3.0
    num_pca_components: int = 2
    max_samples: int = 1000
    perturbation_scale: float = 1.0
    seed: int = 42


class EnergyLandscapeAnalyzer:
    """Analyze energy landscapes via 2D PCA projections."""

    def __init__(
        self,
        transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
        context: SystemContext,
        config: EnergyLandscapeConfig | None = None,
    ):
        self.transition_fn = transition_fn
        self.context = context
        self.config = config or EnergyLandscapeConfig()
        self._pca = PCA(
            n_components=self.config.num_pca_components, random_state=self.config.seed
        )

    def collect_trajectories(
        self,
        init_state: CompositeState,
        num_trajectories: int = 20,
        trajectory_length: int = 50,
    ) -> list[np.ndarray]:
        """Collect state trajectories for PCA fitting."""
        trajectories = []
        rng = torch.Generator()
        rng.manual_seed(self.config.seed)

        for i in range(num_trajectories):
            # Perturb initial state
            perturbed_state = _perturb_state(
                init_state, self.config.perturbation_scale, rng
            )

            trajectory = []
            current = perturbed_state
            for _ in range(trajectory_length):
                with torch.no_grad():
                    current = self.transition_fn(current, self.context)
                # Flatten activity
                act = _get_primary_activity(current)
                trajectory.append(act.flatten().cpu().numpy())
            trajectories.append(np.array(trajectory))

        return trajectories

    def fit_pca(self, trajectories: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        """Fit PCA on collected trajectories."""
        # Stack all trajectory points
        all_points = np.vstack(trajectories)
        # Subsample if too many
        if len(all_points) > self.config.max_samples:
            idx = np.random.choice(
                len(all_points), self.config.max_samples, replace=False
            )
            all_points = all_points[idx]

        self._pca.fit(all_points)
        components = self._pca.components_
        explained_var = self._pca.explained_variance_ratio_
        if explained_var is None:
            explained_var = (
                np.ones(self.config.num_pca_components) / self.config.num_pca_components
            )
        return components, explained_var  # type: ignore[return-value]

    def project_to_2d(self, state: CompositeState) -> np.ndarray:
        """Project a state to 2D PCA space."""
        act = _get_primary_activity(state)
        flat = act.flatten().cpu().numpy().reshape(1, -1)
        return self._pca.transform(flat)[0]

    def compute_energy_grid(
        self,
        init_state: CompositeState,
        attractor_state: CompositeState,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute energy values on a 2D grid around the attractor."""
        # Project attractor to 2D
        attractor_2d = self.project_to_2d(attractor_state)

        # Create grid
        x_range = np.linspace(
            attractor_2d[0] - self.config.grid_range,
            attractor_2d[0] + self.config.grid_range,
            self.config.grid_resolution,
        )
        y_range = np.linspace(
            attractor_2d[1] - self.config.grid_range,
            attractor_2d[1] + self.config.grid_range,
            self.config.grid_resolution,
        )
        X, Y = np.meshgrid(x_range, y_range)

        # For each grid point, reconstruct approximate state and compute energy
        energy_grid = np.zeros_like(X)

        # We'll use a simple proxy: distance from attractor in PCA space
        # In practice, one would reconstruct the full state from PCA coords
        # and run a short settling to measure energy
        for i in range(self.config.grid_resolution):
            for j in range(self.config.grid_resolution):
                point_2d = np.array([X[i, j], Y[i, j]])
                # Distance-based energy proxy
                dist = np.linalg.norm(point_2d - attractor_2d)
                energy_grid[i, j] = dist**2

        return X, Y, energy_grid

    def find_attractors(
        self,
        init_state: CompositeState,
        num_starts: int = 20,
        settle_steps: int = 100,
    ) -> list[CompositeState]:
        """Find attractor states by settling from multiple random starts."""
        attractors = []
        rng = torch.Generator()
        rng.manual_seed(self.config.seed + 1)

        for _ in range(num_starts):
            # Random perturbation
            perturbed_state = _perturb_state(
                init_state, self.config.perturbation_scale, rng
            )

            # Settle
            current = perturbed_state
            with torch.no_grad():
                for _ in range(settle_steps):
                    current = self.transition_fn(current, self.context)

            # Check if this is a new attractor
            is_new = True
            for existing in attractors:
                existing_act = _get_primary_activity(existing)
                current_act = _get_primary_activity(current)
                if torch.allclose(existing_act, current_act, atol=1e-3):
                    is_new = False
                    break

            if is_new:
                attractors.append(current)

        return attractors

    def analyze(
        self,
        init_state: CompositeState,
        num_trajectories: int = 20,
        trajectory_length: int = 50,
    ) -> EnergyLandscapeResult:
        """Full energy landscape analysis pipeline."""
        # Collect trajectories
        trajectories = self.collect_trajectories(
            init_state, num_trajectories, trajectory_length
        )

        # Fit PCA
        components, explained_var = self.fit_pca(trajectories)

        # Find attractors
        attractors = self.find_attractors(init_state)

        # Compute energy grid around first attractor
        if attractors:
            grid_x, grid_y, energy = self.compute_energy_grid(init_state, attractors[0])
            attractor_points = [tuple(self.project_to_2d(a)) for a in attractors]
        else:
            grid_x = grid_y = energy = np.array([])
            attractor_points = []

        return EnergyLandscapeResult(
            grid_x=grid_x,
            grid_y=grid_y,
            energy_values=energy,
            pca_components=components,
            pca_explained_variance=explained_var,
            attractor_points=attractor_points,
            metadata={
                "num_trajectories": num_trajectories,
                "trajectory_length": trajectory_length,
                "num_attractors": len(attractors),
                "grid_resolution": self.config.grid_resolution,
                "explained_variance_ratio": float(explained_var.sum()),
            },
        )


def compute_energy_landscape_2d(
    transition_fn: Callable[[CompositeState, SystemContext], CompositeState],
    init_state: CompositeState,
    context: SystemContext,
    config: EnergyLandscapeConfig | None = None,
    num_trajectories: int = 20,
    trajectory_length: int = 50,
) -> EnergyLandscapeResult:
    """Convenience function to compute 2D energy landscape."""
    analyzer = EnergyLandscapeAnalyzer(transition_fn, context, config)
    return analyzer.analyze(init_state, num_trajectories, trajectory_length)


def plot_energy_landscape(
    result: EnergyLandscapeResult,
    output_path: Path | str,
    title: str = "Energy Landscape",
    grid_range: float = 3.0,
    grid_resolution: int = 30,
) -> Path:
    """Plot energy landscape as contour plot."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Energy contour plot
    if result.energy_values.size > 0:
        X, Y = np.meshgrid(
            np.linspace(-grid_range, grid_range, grid_resolution),
            np.linspace(-grid_range, grid_range, grid_resolution),
        )
        # Use stored grid if available
        if result.grid_x.size > 0:
            X = result.grid_x
            Y = result.grid_y

        contour = axes[0].contourf(
            X, Y, result.energy_values, levels=20, cmap="viridis"
        )
        plt.colorbar(contour, ax=axes[0], label="Energy (proxy)")
        axes[0].set_xlabel("PC1")
        axes[0].set_ylabel("PC2")
        axes[0].set_title(f"{title} - Energy Contour")

        # Plot attractors
        for attr in result.attractor_points:
            axes[0].plot(attr[0], attr[1], "r*", markersize=15, label="Attractor")
        axes[0].legend()

    # PCA explained variance
    axes[1].bar(
        range(1, len(result.pca_explained_variance) + 1),
        result.pca_explained_variance,
    )
    axes[1].set_xlabel("Principal Component")
    axes[1].set_ylabel("Explained Variance Ratio")
    axes[1].set_title("PCA Explained Variance")
    axes[1].grid(True, alpha=0.3)

    plt.suptitle(title)
    plt.tight_layout()

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_file
