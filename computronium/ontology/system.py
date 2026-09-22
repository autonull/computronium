"""System Composition: 6-D Ontology (S ⊗ G ⊗ D ⊗ M ⊗ C ⊗ U)."""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, TypeVar, cast, runtime_checkable

import torch
from torch import Tensor, nn

from computronium.ontology.credit import (
    CreditAssignment,
    CreditAssignmentConfig,
    GradientCredit,
)
from computronium.ontology.dynamics import (
    InstantaneousDynamics,
    StateDynamics,
    StateDynamicsConfig,
)
from computronium.ontology.geometry import FeedforwardGeometry, Geometry, GeometryConfig
from computronium.ontology.substrate import (
    AnalogSubstrate,
    DigitalSubstrate,
    MemristiveSubstrate,
    NeuromorphicSubstrate,
    OpticalSubstrate,
    QuantumSubstrate,
    Substrate,
    SubstrateConfig,
)
from computronium.ontology.update import (
    EuclideanUpdate,
    ParameterUpdate,
    ParameterUpdateConfig,
)
from computronium.state import PlasticityConfig

if TYPE_CHECKING:
    from collections.abc import Callable

# ============================================================
# SystemState: Mutable state for 5-D pipeline
# ============================================================


@dataclass(frozen=False, slots=True)
class SystemState:
    """Mutable state carried through the 5-layer pipeline.

    This is the single state object threaded through Substrate → Geometry
    → StateDynamics → CreditAssignment → ParameterUpdate. Each layer reads
    and writes a defined subset of fields.

    Attributes:
        x: Input batch
        y: Target batch
        activations: Current layer activations (list for multi-layer, tensor for single)
        free_state: Settled free-phase state
        nudged_state: Settled nudged-phase state
        pseudo_gradients: Computed pseudo-gradients per layer
        energy: Current energy value
        loss: Current loss value
        metrics: Accumulated metrics dict
        spike_counts: Per-step per-neuron spike counts (for spiking dynamics)
        spike_rasters: Per-layer per-step spike rasters [layer][step] = [batch, neurons]
            (for timing-asymmetric STDP credit assignment)
        dual_vars: Dual variables (Lagrange multipliers) per layer for PC-ALM
            dynamics. List of tensors [B, D_l] matching layer structure.
    """

    x: Tensor | None = None
    y: Tensor | None = None
    activations: list[Tensor] | Tensor | None = None
    free_state: list[Tensor] | Tensor | None = None
    nudged_state: list[Tensor] | Tensor | None = None
    pseudo_gradients: list[Tensor] | None = None
    energy: Tensor | float | None = None
    loss: Tensor | float | None = None
    metrics: dict[str, float] = None  # type: ignore[assignment]
    spike_counts: list[Tensor] | None = None
    spike_rasters: list[list[Tensor]] | None = None
    dual_vars: list[Tensor] | None = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


# ============================================================
# Phase enum (re-exported for convenience)
# ============================================================


Phase = StrEnum(
    "Phase",
    {
        "FREE": "free",
        "NUDGED": "nudged",
    },
)


# ============================================================
# System Protocol: The 5-Layer Tensor Product
# ============================================================


TS = TypeVar("TS", bound=Substrate)
TG = TypeVar("TG", bound=Geometry)
TD = TypeVar("TD", bound=StateDynamics)
TC = TypeVar("TC", bound=CreditAssignment)
TU = TypeVar("TU", bound=ParameterUpdate)


@runtime_checkable
class System(Protocol[TS, TG, TD, TC, TU]):
    """Composable computronium system: S ⊗ G ⊗ D ⊗ C ⊗ U.

    The tensor product of five orthogonal primitives. Every model in the
    zoo is a coordinate in this 5-D space. The System orchestrates the
    strict pipeline:

        Substrate.forward_op → Geometry.route → StateDynamics.settle
        → CreditAssignment.compute_pseudo_gradient → ParameterUpdate.step

    Type parameters ensure only valid compositions compile:
    - SpikingDynamics requires STDP CreditAssignment
    - EnergyMinimization requires ThermodynamicContrast
    - TileMesh Geometry requires Tile-aware StateDynamics
    """

    substrate: TS
    geometry: TG
    dynamics: TD
    credit: TC
    update: TU

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        """Execute one training step through the family-neutral pipeline."""
        from computronium.core.pipeline import run_train_step

        return run_train_step(
            self.substrate,
            self.geometry,
            self.dynamics,
            self.credit,
            self.update,
            x,
            y,
        )

    def forward(self, x: Tensor) -> Tensor:
        """Inference forward pass (free phase only, no weight updates)."""
        from computronium.core.pipeline import run_forward

        return run_forward(self.substrate, self.geometry, self.dynamics, x)

    def to_spec(self) -> dict[str, object]:
        """Serialize the System to a specification dictionary.

        Returns:
            Dictionary containing schema_version and all 5 axis configs.
        """
        ...

    @classmethod
    def from_spec(cls, spec: dict[str, object]) -> System[TS, TG, TD, TC, TU]:
        """Reconstruct a System from a specification dictionary.

        Args:
            spec: Dictionary with schema_version and 5 axis configs.

        Returns:
            A composed System instance.
        """
        ...


# ============================================================
# SystemConfig: Validated Composition of 6-D Ontology
# ============================================================


# Family-specific tolerances for validation
FAMILY_TOLERANCES: dict[str, tuple[float, float]] = {
    "eqprop": (0.15, 1e-2),
    "equilibrium": (0.15, 1e-2),
    "ep": (0.15, 1e-2),
    "chl": (0.15, 1e-2),
    "fa": (0.1, 5e-3),
    "feedback_alignment": (0.1, 5e-3),
    "dfa": (0.1, 5e-3),
    "forward_only": (0.05, 1e-3),
    "ff": (0.05, 1e-3),
    "pepita": (0.05, 1e-3),
    "hebbian": (0.2, 1e-2),
    "target_prop": (0.1, 5e-3),
    "target_inversion": (0.1, 5e-3),
    "spiking": (0.2, 1e-2),
    "stdp": (0.2, 1e-2),
    "snn": (0.2, 1e-2),
    "predictive_coding": (0.1, 5e-3),
    "pc": (0.1, 5e-3),
    "backprop": (0.01, 1e-4),
    "gradient": (0.01, 1e-4),
    "mep": (0.1, 5e-3),
    "tile": (0.1, 5e-3),
    "default": (0.1, 1e-3),
}


# ============================================================
# Valid Combinations Data (Module-level constants for valid_combinations)
# ============================================================

_SUBSTRATES: list[dict[str, object]] = [
    {"type": "digital", "precision": "float32", "noise_level": 0.0, "sparsity": 0.0},
    {
        "type": "memristive",
        "precision": "float32",
        "noise_level": 0.01,
        "sparsity": 0.0,
    },
    {
        "type": "neuromorphic",
        "precision": "float16",
        "noise_level": 0.0,
        "sparsity": 0.95,
    },
    {"type": "optical", "precision": "float32", "noise_level": 0.0, "sparsity": 0.0},
    {"type": "quantum", "precision": "complex64", "noise_level": 0.0, "sparsity": 0.0},
    {"type": "sparse", "precision": "float32", "noise_level": 0.0, "sparsity": 0.8},
    {"type": "ternary", "precision": "float32", "noise_level": 0.0, "sparsity": 0.0},
]

_GEOMETRIES: list[dict[str, object]] = [
    {
        "topology_type": "feedforward",
        "input_dim": 784,
        "output_dim": 10,
        "hidden_dims": [256, 128],
    },
    {
        "topology_type": "recurrent",
        "input_dim": 784,
        "output_dim": 10,
        "hidden_dims": [256],
    },
    {
        "topology_type": "tile_mesh",
        "input_dim": 784,
        "output_dim": 10,
        "num_layers": 4,
        "neurons_per_tile": 64,
        "tiles_per_layer": 4,
    },
]

_DYNAMICS_OPTIONS: list[dict[str, object]] = [
    {"dynamics_type": "energy_minimization", "max_steps": 20, "beta": 0.5},
    {"dynamics_type": "predictive_settling", "max_steps": 20, "beta": 0.5},
    {"dynamics_type": "spike_integration", "max_steps": 50, "beta": 0.5},
    {"dynamics_type": "instantaneous", "max_steps": 1, "beta": 0.5},
    {"dynamics_type": "diffusion", "max_steps": 100, "beta": 0.5},
]

_PLASTICITIES: list[dict[str, object]] = [
    {"type": "null"},
    {"type": "routing", "gate_dim": 64},
    {
        "type": "fast_weights",
        "fast_weight_dim": 512,
        "decay": 0.9,
        "learning_rate": 0.1,
    },
    {"type": "substrate_coupled"},
]

_CREDITS: list[dict[str, object]] = [
    {"credit_type": "thermodynamic_contrast", "beta": 0.5},
    {"credit_type": "random_projections", "beta": 0.5},
    {"credit_type": "local_goodness", "beta": 0.5},
    {"credit_type": "temporal_trace", "beta": 0.5},
    {"credit_type": "target_inversion", "beta": 0.5},
    {"credit_type": "gradient", "beta": 0.5},
]

_UPDATES: list[dict[str, object]] = [
    {"update_type": "euclidean", "step_size": 0.01},
    {"update_type": "adam", "step_size": 0.001},
    {"update_type": "ortho_adam", "step_size": 0.001, "ortho_lr": 0.003},
    {"update_type": "lion", "step_size": 0.003},
    {"update_type": "riemannian_orthogonal", "step_size": 0.01},
    {"update_type": "spectral_constrained", "step_size": 0.01},
    {"update_type": "mean_norm", "step_size": 0.01},
    {"update_type": "elastic_consolidation", "step_size": 0.01},
]

# Pre-computed validation rule sets for fast filtering
_RECURRENT_DYNAMICS = {"energy_minimization"}
_THERMO_CREDIT_DYNAMICS = {"energy_minimization"}
_SPIKE_INTEGRATION_CREDITS = {"temporal_trace", "target_inversion", "target_prop"}
_TILE_MESH_DYNAMICS = {"energy_minimization", "instantaneous"}
_QUANTUM_DYNAMICS = {"energy_minimization", "instantaneous", "diffusion"}
_PREDICTIVE_SETTLING_CREDITS = {
    "thermodynamic_contrast",
    "equilibrium",
    "local_goodness",
    "forward_only",
}


@dataclass(frozen=True, slots=True)
class SystemConfig:
    """Validated composition of 6-D ontology — single source of truth for a system.

    Composes the six orthogonal axes (S ⊗ G ⊗ D ⊗ M ⊗ C ⊗ U) and provides
    validated, cross-validated access. The 6th axis (M = Plasticity) enables
    meta-dynamics and fast plastic state evolution.
    """

    substrate: SubstrateConfig
    geometry: GeometryConfig
    dynamics: StateDynamicsConfig
    plasticity: PlasticityConfig
    credit: CreditAssignmentConfig
    update: ParameterUpdateConfig

    def __init__(
        self,
        substrate: SubstrateConfig,
        geometry: GeometryConfig,
        dynamics: StateDynamicsConfig,
        credit: CreditAssignmentConfig,
        update: ParameterUpdateConfig,
        plasticity: PlasticityConfig | None = None,
    ):
        object.__setattr__(self, "substrate", substrate)
        object.__setattr__(self, "geometry", geometry)
        object.__setattr__(self, "dynamics", dynamics)
        object.__setattr__(self, "credit", credit)
        object.__setattr__(self, "update", update)
        object.__setattr__(
            self,
            "plasticity",
            plasticity if plasticity is not None else PlasticityConfig.null(),
        )

    def validate(self) -> None:
        """Cross-axis validation (hard constraints only).

        Raises:
            ValueError: If configuration violates hard compatibility constraints.
        """
        # Geometry-Dynamics compatibility
        self._validate_recurrent_geometry_dynamics()
        self._validate_nonlayered_geometry_dynamics()
        self._validate_tile_mesh_dynamics()
        self._validate_nca_ntm_geometry()
        self._validate_diffusion_dynamics_credit()
        self._validate_spike_integration_credit()
        self._validate_predictive_settling_credit()
        self._validate_pc_alm_dynamics()
        self._validate_residual_connections()

        # Credit-Dynamics compatibility
        self._validate_thermodynamic_contrast_dynamics()

        # Beta matching (soft constraints)
        self._validate_beta_matching_energy_minimization()
        self._validate_beta_matching_pc_alm()

        # Substrate-Dynamics compatibility
        self._validate_neuromorphic_substrate_dynamics()
        self._validate_analog_substrate_noise()
        self._validate_complex_substrate_credit()
        self._validate_quantum_substrate_dynamics()
        self._validate_sparse_substrate_update()
        self._validate_ternary_substrate_credit()
        self._validate_diffusion_substrate_noise()

        # Geometry-Substrate compatibility
        self._validate_spatial_neuromorphic_geometry_substrate()
        self._validate_tile_mesh_sparse_substrate()

        # Special case validations
        self._validate_gradient_credit_beta_clamp()
        self._validate_per_element_displacement_step_size()
        self._validate_energy_minimization_momentum_update()

    # --- Geometry-Dynamics Validation Methods ---

    def _validate_recurrent_geometry_dynamics(self) -> None:
        """Recurrent geometry requires energy-based, PC-family, or instantaneous dynamics."""
        if self.geometry.topology_type in ("recurrent", "recurrent_attractor"):
            if self.dynamics.dynamics_type not in {
                "energy_minimization",
                "predictive_settling",
                "error_predictive_coding",
                "pc_alm",
                "instantaneous",
            }:
                raise ValueError(
                    f"Recurrent geometry (topology_type={self.geometry.topology_type!r}) "
                    f"requires energy-based, PC-family, or instantaneous dynamics, "
                    f"got {self.dynamics.dynamics_type!r}"
                )

    def _validate_nonlayered_geometry_dynamics(self) -> None:
        """Non-layered geometries cannot host settling dynamics."""
        if self.dynamics.dynamics_type != "instantaneous" and (
            self.geometry.topology_type
            in {
                "attention",
                "spatial_lattice",
                "graph",
                "conv",
                "nca",
                "ntm",
                "causal_transformer",
            }
        ):
            raise ValueError(
                f"{self.dynamics.dynamics_type!r} settling feeds raw states "
                f"into geometry.route(), which {self.geometry.topology_type!r} "
                f"geometry does not support (state-shape contract)"
            )

    def _validate_tile_mesh_dynamics(self) -> None:
        """Tile mesh geometry requires compatible dynamics."""
        if self.geometry.topology_type in ("tile_mesh", "tile"):
            if self.dynamics.dynamics_type not in (
                "energy_minimization",
                "pc_alm",
                "instantaneous",
            ):
                raise ValueError(
                    f"Tile mesh geometry requires energy_minimization, pc_alm, or instantaneous dynamics, "
                    f"got {self.dynamics.dynamics_type!r}"
                )

    def _validate_nca_ntm_geometry(self) -> None:
        """NCA/NTM geometries require instantaneous dynamics."""
        if self.geometry.topology_type in {"nca", "ntm"} and (
            self.dynamics.dynamics_type != "instantaneous"
        ):
            raise ValueError(
                f"{self.geometry.topology_type.upper()} geometry requires "
                f"instantaneous dynamics, got {self.dynamics.dynamics_type!r}"
            )

    def _validate_diffusion_dynamics_credit(self) -> None:
        """Diffusion settle produces non-differentiable state; gradient/backprop unsupported."""
        if self.dynamics.dynamics_type == "diffusion":
            if self.credit.credit_type in {"gradient", "backprop"}:
                raise ValueError(
                    f"Diffusion dynamics produce a non-differentiable settled "
                    f"state; gradient/backprop credit "
                    f"(credit_type={self.credit.credit_type!r}) is unsupported"
                )

    def _validate_spike_integration_credit(self) -> None:
        """Spike integration dynamics requires temporal trace or target inversion credit."""
        if self.dynamics.dynamics_type == "spike_integration":
            if self.credit.credit_type not in (
                "temporal_trace",
                "spiking",
                "target_inversion",
                "target_prop",
            ):
                raise ValueError(
                    f"Spike integration dynamics requires temporal trace or target inversion credit, "
                    f"got {self.credit.credit_type!r}"
                )

    def _validate_predictive_settling_credit(self) -> None:
        """Predictive settling dynamics requires compatible credit."""
        if self.dynamics.dynamics_type in (
            "predictive_settling",
            "error_predictive_coding",
        ):
            if self.credit.credit_type not in (
                "thermodynamic_contrast",
                "equilibrium",
                "local_goodness",
                "forward_only",
            ):
                raise ValueError(
                    f"{self.dynamics.dynamics_type} dynamics requires "
                    f"thermodynamic_contrast, local_goodness, or forward_only credit, "
                    f"got {self.credit.credit_type!r}"
                )

    def _validate_pc_alm_dynamics(self) -> None:
        """PC-ALM dynamics requires PCALMCredit (or thermodynamic_contrast) and layered geometry."""
        if self.dynamics.dynamics_type == "pc_alm":
            if self.credit.credit_type not in ("pc_alm", "thermodynamic_contrast"):
                raise ValueError(
                    f"PC-ALM dynamics requires pc_alm or thermodynamic_contrast credit, "
                    f"got {self.credit.credit_type!r}"
                )
            if self.geometry.topology_type not in (
                "feedforward",
                "recurrent",
                "tile_mesh",
            ):
                raise ValueError(
                    f"PC-ALM dynamics requires layered geometry, "
                    f"got {self.geometry.topology_type!r}"
                )

    def _validate_residual_connections(self) -> None:
        """Residual connections only supported on feedforward geometry."""
        if (
            getattr(self.geometry, "residual", False)
            and self.geometry.topology_type != "feedforward"
        ):
            raise ValueError(
                f"Residual connections (residual=True) require feedforward geometry, "
                f"got topology_type={self.geometry.topology_type!r}"
            )

    def _validate_thermodynamic_contrast_dynamics(self) -> None:
        """Thermodynamic contrast credit requires energy-based or PC-family dynamics."""
        if self.credit.credit_type in ("thermodynamic_contrast", "equilibrium"):
            if self.dynamics.dynamics_type not in (
                "energy_minimization",
                "predictive_settling",
                "error_predictive_coding",
                "lazy",
                "pc_alm",
            ):
                raise ValueError(
                    f"Thermodynamic contrast credit (credit_type={self.credit.credit_type!r}) "
                    f"requires energy-based or PC-family dynamics, got {self.dynamics.dynamics_type!r}"
                )

    # --- Beta Matching (Soft Constraints) ---

    def _validate_beta_matching_energy_minimization(self) -> None:
        """Energy minimization dynamics requires matching beta between dynamics and credit."""
        if self.dynamics.dynamics_type == "energy_minimization":
            if abs(self.dynamics.beta - self.credit.beta) > 1e-6:
                warnings.warn(
                    f"Beta mismatch: dynamics.beta={self.dynamics.beta} != credit.beta={self.credit.beta}. "
                    f"This may cause incorrect gradient scaling in EqProp.",
                    UserWarning,
                    stacklevel=2,
                )

    def _validate_beta_matching_pc_alm(self) -> None:
        """PC-ALM dynamics requires matching beta (dual LR scale)."""
        if self.dynamics.dynamics_type == "pc_alm":
            if abs(self.dynamics.beta - self.credit.beta) > 1e-6:
                warnings.warn(
                    f"PC-ALM beta mismatch: dynamics.beta={self.dynamics.beta} "
                    f"!= credit.beta={self.credit.beta}. Dual LR scaling may be incorrect.",
                    UserWarning,
                    stacklevel=2,
                )

    # --- Substrate-Dynamics Validation Methods ---

    def _validate_neuromorphic_substrate_dynamics(self) -> None:
        """Neuromorphic substrate requires temporal dynamics."""
        if self.substrate.precision == "float16" and self.substrate.sparsity > 0.9:
            if self.dynamics.dynamics_type not in (
                "spike_integration",
                "energy_minimization",
                "diffusion",
            ):
                raise ValueError(
                    f"Neuromorphic substrate (precision={self.substrate.precision}, "
                    f"sparsity={self.substrate.sparsity}) requires temporal dynamics "
                    f"(spike_integration, energy_minimization, or diffusion), "
                    f"got {self.dynamics.dynamics_type!r}"
                )

    def _validate_analog_substrate_noise(self) -> None:
        """Analog substrate with noise warns on instantaneous dynamics."""
        if self.substrate.precision == "float32" and self.substrate.noise_level > 0.0:
            if self.dynamics.dynamics_type == "instantaneous":
                warnings.warn(
                    f"Analog substrate with noise_level={self.substrate.noise_level} "
                    f"used with instantaneous dynamics. Noise only applied once at input. "
                    f"Consider energy_minimization or diffusion dynamics for continuous noise injection.",
                    UserWarning,
                    stacklevel=2,
                )

    def _validate_complex_substrate_credit(self) -> None:
        """Complex substrate works best with thermodynamic contrast or backprop."""
        if self.substrate.precision == "float32" and getattr(
            self.substrate, "_complex_emulated", False
        ):
            if self.credit.credit_type not in (
                "thermodynamic_contrast",
                "equilibrium",
                "gradient",
                "backprop",
            ):
                warnings.warn(
                    f"Complex substrate used with {self.credit.credit_type!r} credit. "
                    f"Best results with thermodynamic_contrast (holomorphic EqProp) "
                    f"or gradient (holomorphic backprop).",
                    UserWarning,
                    stacklevel=2,
                )

    def _validate_quantum_substrate_dynamics(self) -> None:
        """Quantum substrate requires compatible dynamics and beta matching."""
        if self.substrate.precision == "complex64":
            if self.dynamics.dynamics_type not in (
                "energy_minimization",
                "instantaneous",
                "diffusion",
            ):
                raise ValueError(
                    f"Quantum substrate requires energy_minimization, instantaneous, "
                    f"or diffusion dynamics, got {self.dynamics.dynamics_type!r}"
                )
            if self.credit.credit_type in ("thermodynamic_contrast", "equilibrium"):
                if abs(self.dynamics.beta - self.credit.beta) > 1e-6:
                    warnings.warn(
                        f"Quantum substrate with thermodynamic contrast: "
                        f"beta mismatch dynamics.beta={self.dynamics.beta} != credit.beta={self.credit.beta}. "
                        f"Phase-sensitive gradients require matched beta.",
                        UserWarning,
                        stacklevel=2,
                    )

    def _validate_sparse_substrate_update(self) -> None:
        """Sparse substrate warns on RiemannianOrthogonalUpdate."""
        if self.substrate.sparsity > 0.5:
            if self.update.update_type == "riemannian_orthogonal":
                warnings.warn(
                    f"Sparse substrate (sparsity={self.substrate.sparsity}) with "
                    f"RiemannianOrthogonalUpdate may densify weights. "
                    f"Consider SpectralConstrainedUpdate or ElasticConsolidationUpdate.",
                    UserWarning,
                    stacklevel=2,
                )

    def _validate_ternary_substrate_credit(self) -> None:
        """Ternary-like substrate works best with thermodynamic contrast or backprop."""
        if (
            self.substrate.precision == "float32"
            and self.substrate.sparsity == 0.0
            and self.substrate.weight_bounds == (-1.0, 1.0)
        ):
            if self.credit.credit_type not in (
                "thermodynamic_contrast",
                "equilibrium",
                "gradient",
                "backprop",
            ):
                warnings.warn(
                    f"Ternary-like substrate used with {self.credit.credit_type!r} credit. "
                    f"Best results with thermodynamic_contrast (Ternary EqProp) "
                    f"or gradient (Ternary backprop with STE).",
                    UserWarning,
                    stacklevel=2,
                )

    def _validate_diffusion_substrate_noise(self) -> None:
        """Diffusion dynamics requires substrate noise_level > 0."""
        if self.dynamics.dynamics_type == "diffusion":
            if self.substrate.noise_level == 0.0:
                warnings.warn(
                    "Diffusion dynamics (Langevin) requires substrate noise_level > 0 "
                    "for proper sampling. Consider setting noise_level on substrate.",
                    UserWarning,
                    stacklevel=2,
                )

    # --- Geometry-Substrate Validation Methods ---

    def _validate_spatial_neuromorphic_geometry_substrate(self) -> None:
        """Spatial/neuromorphic geometry works best with neuromorphic substrate."""
        if self.geometry.topology_type in ("spatial_lattice", "neuromorphic", "fabric"):
            if not (
                self.substrate.precision == "float16" and self.substrate.sparsity > 0.9
            ):
                warnings.warn(
                    f"Spatial/neuromorphic geometry ({self.geometry.topology_type}) "
                    f"works best with neuromorphic substrate (float16, high sparsity). "
                    f"Current substrate: precision={self.substrate.precision}, "
                    f"sparsity={self.substrate.sparsity}",
                    UserWarning,
                    stacklevel=2,
                )

    def _validate_tile_mesh_sparse_substrate(self) -> None:
        """Tile mesh with sparse substrate warns about structured sparsity."""
        if (
            self.geometry.topology_type in ("tile_mesh", "tile")
            and self.substrate.sparsity > 0.5
        ):
            warnings.warn(
                f"Sparse substrate (sparsity={self.substrate.sparsity}) "
                f"with tile mesh geometry may benefit from structured sparsity (N:M or block) "
                f"for efficient matmul.",
                UserWarning,
                stacklevel=2,
            )

    # --- Special Case Validations ---

    def _validate_gradient_credit_beta_clamp(self) -> None:
        """Gradient/backprop credit with beta >= 1.0 has zero pseudo-gradient."""
        if (
            self.credit.credit_type in {"gradient", "backprop"}
            and self.credit.beta >= 1.0
        ):
            raise ValueError(
                f"credit_type={self.credit.credit_type!r} with beta={self.credit.beta} "
                f"has an exactly-zero pseudo-gradient (the nudged output is fully "
                f"clamped to the target); use beta < 1.0."
            )

    def _validate_per_element_displacement_step_size(self) -> None:
        """Per-element-displacement update rules warn on gradient-relative step_size range."""
        if (
            self.update.step_semantics == "per_element_displacement"
            and self.update.step_size > 0.05
        ):
            warnings.warn(
                f"update_type={self.update.update_type!r} uses per-element-displacement "
                f"step semantics (step_size IS the displacement); "
                f"step_size={self.update.step_size} is in the gradient-relative lr range "
                f"and likely an overshoot mislabel.",
                UserWarning,
                stacklevel=2,
            )

    def _validate_energy_minimization_momentum_update(self) -> None:
        """EnergyMinimizationDynamics with momentum warns on RiemannianOrthogonalUpdate."""
        if (
            self.dynamics.dynamics_type == "energy_minimization"
            and self.dynamics.momentum > 0.0
            and self.update.update_type == "riemannian_orthogonal"
        ):
            warnings.warn(
                f"EnergyMinimizationDynamics with momentum={self.dynamics.momentum} "
                f"combined with RiemannianOrthogonalUpdate may cause instability. "
                f"Consider EuclideanUpdate with momentum.",
                UserWarning,
                stacklevel=2,
            )

    @classmethod
    def valid_combinations(cls) -> list[dict[str, dict[str, object]]]:
        """Return all valid 6-D coordinate combinations for AutoScientist.

        Returns:
            List of dicts, each representing a valid combination of
            substrate, geometry, dynamics, plasticity, credit, update.
            These are the coordinates that pass cross-axis validation.
        """
        from itertools import product

        combinations = [
            {
                "substrate": sub,
                "geometry": geom,
                "dynamics": dyn,
                "plasticity": plas,
                "credit": cred,
                "update": upd,
            }
            for sub, geom, dyn, plas, cred, upd in product(
                _SUBSTRATES,
                _GEOMETRIES,
                _DYNAMICS_OPTIONS,
                _PLASTICITIES,
                _CREDITS,
                _UPDATES,
            )
            if cls._is_valid_combination(sub, geom, dyn, cred)
        ]

        return combinations

    @classmethod
    def _is_valid_combination(
        cls,
        substrate: dict[str, object],
        geometry: dict[str, object],
        dynamics: dict[str, object],
        credit: dict[str, object],
    ) -> bool:
        """Check if a combination passes all hard validation rules.

        This mirrors the validation logic in SystemConfig.validate() but
        operates on raw config dicts for fast filtering during AutoScientist
        candidate generation.
        """
        geo_type = geometry["topology_type"]
        dyn_type = dynamics["dynamics_type"]
        cred_type = credit["credit_type"]
        sub_precision = substrate["precision"]

        validators: list[tuple[bool, bool]] = [
            # (condition, should_pass)
            (
                geo_type in ("recurrent", "recurrent_attractor"),
                dyn_type in _RECURRENT_DYNAMICS,
            ),
            (
                cred_type in ("thermodynamic_contrast", "equilibrium"),
                dyn_type in _THERMO_CREDIT_DYNAMICS,
            ),
            (dyn_type == "spike_integration", cred_type in _SPIKE_INTEGRATION_CREDITS),
            (geo_type in ("tile_mesh", "tile"), dyn_type in _TILE_MESH_DYNAMICS),
            (sub_precision == "complex64", dyn_type in _QUANTUM_DYNAMICS),
            (
                dyn_type == "predictive_settling",
                cred_type in _PREDICTIVE_SETTLING_CREDITS,
            ),
        ]

        return all(
            not condition or should_pass for condition, should_pass in validators
        )


# ============================================================
# ModelAdapter: Wrap existing models as System compositions
# ============================================================


class ModelAdapter:
    """Adapt an existing ``nn.Module`` to the 5-D System interface.

    Inference priority:
    1. Model attributes (backend, gradient_method, max_steps, etc.)
    2. Heuristics from class name
    3. Defaults (DigitalSubstrate, FeedforwardGeometry, InstantaneousDynamics, etc.)
    """

    def __init__(self, model: nn.Module):
        self.model = model

    def _get_family_tolerances(self) -> tuple[float, float]:
        """Get family-specific tolerances from the model's class name."""
        family = type(self.model).__name__.lower()
        if family in FAMILY_TOLERANCES:
            return FAMILY_TOLERANCES[family]
        for key, tol in FAMILY_TOLERANCES.items():
            if key != "default" and key in family:
                return tol
        return FAMILY_TOLERANCES["default"]

    def to_system(
        self,
    ) -> System[Substrate, Geometry, StateDynamics, CreditAssignment, ParameterUpdate]:
        """Project model into 5-D ontology (best-effort inference)."""
        substrate = self._infer_substrate()
        geometry = self._infer_geometry()
        dynamics = self._infer_dynamics()
        credit = self._infer_credit()
        update = self._infer_update()

        return _AdaptedSystem(
            substrate=substrate,
            geometry=geometry,
            dynamics=dynamics,
            credit=credit,
            update=update,
            model=self.model,
        )

    def _infer_substrate(self) -> Substrate:
        # Priority 1: Model attributes
        substrate = self._infer_substrate_from_backend()
        if substrate is not None:
            return substrate

        # Priority 3: Family tag heuristics
        substrate = self._infer_substrate_from_family()
        if substrate is not None:
            return substrate

        return DigitalSubstrate(
            SubstrateConfig(
                precision="float32",
                noise_level=0.0,
                weight_bounds=None,
                sparsity=0.0,
                device="cpu",
            )
        )

    def _infer_substrate_from_backend(self) -> Substrate | None:
        # Check model attributes for backend hints
        if hasattr(self.model, "backend"):
            backend = getattr(self.model, "backend", "").lower()
            if "analog" in backend:
                return AnalogSubstrate(SubstrateConfig.analog())
            if "memrist" in backend:
                return MemristiveSubstrate(SubstrateConfig.memristive())
            if "neuromorph" in backend:
                return NeuromorphicSubstrate(SubstrateConfig.neuromorphic())
            if "optical" in backend or "photonic" in backend:
                return OpticalSubstrate(SubstrateConfig.optical())
            if "quantum" in backend:
                return QuantumSubstrate(SubstrateConfig.quantum())
        return None

    def _infer_substrate_from_family(self) -> Substrate | None:
        family = type(self.model).__name__.lower()
        if "spiking" in family or "snn" in family or "stdp" in family:
            return NeuromorphicSubstrate(SubstrateConfig.neuromorphic())
        if "tile" in family:
            return DigitalSubstrate(SubstrateConfig.digital())
        return None

    _NON_FORWARD_LINEAR_MARKERS = ("feedback", "recurrent", "b_", "fa_")

    def _probe_linear_dims(self) -> tuple[int, ...] | None:
        """Chain the model's forward Linear layers into (input, *hidden, output).

        Walks registered modules in order, skipping non-forward Linears
        (FA feedback, recurrent). Returns None when the shapes don't form
        a single feedforward chain.
        """
        module_names = {id(mod): name for name, mod in self.model.named_modules()}
        linears = [
            m
            for m in self.model.modules()
            if isinstance(m, nn.Linear)
            and not any(
                marker in module_names[id(m)].lower()
                for marker in self._NON_FORWARD_LINEAR_MARKERS
            )
        ]
        if not linears:
            return None
        dims = [linears[0].in_features, linears[0].out_features]
        for layer in linears[1:]:
            if layer.in_features != dims[-1]:
                return None
            dims.append(layer.out_features)
        return tuple(dims)

    def _infer_geometry(self) -> Geometry:
        dims = self._probe_linear_dims()
        if dims is not None:
            input_dim, *hidden_dims, output_dim = dims
        elif (input_dim := getattr(self.model, "input_dim", None)) is not None and (
            output_dim := getattr(self.model, "output_dim", None)
        ) is not None:
            hidden_dims = []
        else:
            raise TypeError(
                f"Cannot infer geometry for {type(self.model).__name__}: "
                "no Linear chain and no input_dim/output_dim attributes. "
                "Register the model with explicit ontology geometry metadata."
            )
        return FeedforwardGeometry(
            GeometryConfig.feedforward(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden_dims=tuple(hidden_dims),
            )
        )

    def _infer_dynamics(self) -> StateDynamics:
        # Simplified: return InstantaneousDynamics
        return InstantaneousDynamics(StateDynamicsConfig.instantaneous())

    def _infer_credit(self) -> CreditAssignment:
        # Simplified: return GradientCredit
        return GradientCredit(CreditAssignmentConfig.gradient())

    def _infer_update(self) -> ParameterUpdate:
        # Simplified: return EuclideanUpdate
        return EuclideanUpdate(ParameterUpdateConfig.euclidean())

    def validate(
        self,
        x: Tensor | None = None,
        y: Tensor | None = None,
        rtol: float | None = None,
        atol: float | None = None,
    ) -> dict[str, object]:
        """Validate the 5-D projection against the legacy model.

        Runs a forward/backward pass on both the legacy model and the adapted
        System, comparing key metrics (loss, gradients) to ensure the ontology
        projection preserves the model's learning behavior.

        Args:
            x: Input tensor. If None, generates synthetic data based on
               inferred input_dim.
            y: Target tensor. If None, generates synthetic labels based on
               inferred output_dim.
            rtol: Relative tolerance for metric comparison. If None, uses
                  family-specific tolerance from FAMILY_TOLERANCES.
            atol: Absolute tolerance for metric comparison. If None, uses
                  family-specific tolerance from FAMILY_TOLERANCES.

        Returns:
            Dictionary with validation results:
            - "passed": bool indicating if all checks passed
            - "legacy_metrics": metrics from legacy model train_step
            - "system_metrics": metrics from System train_step
            - "differences": dict of metric differences
            - "details": additional diagnostic info
        """
        # Use family-specific tolerances if not explicitly provided
        if rtol is None or atol is None:
            family_rtol, family_atol = self._get_family_tolerances()
            rtol = rtol if rtol is not None else family_rtol
            atol = atol if atol is not None else family_atol

        # Generate test data if not provided
        if x is None:
            input_dim = getattr(self.model, "input_dim", 10)
            x = torch.randn(4, input_dim)
        if y is None:
            output_dim = getattr(self.model, "output_dim", 3)
            y = torch.randint(0, output_dim, (x.shape[0],))

        # Ensure model is in train mode
        self.model.train()

        # Run legacy model train_step
        legacy_metrics: dict[str, object] = {}
        legacy_train_step = getattr(self.model, "train_step", None)
        if callable(legacy_train_step):
            try:
                legacy_result = legacy_train_step(x, y)
                if legacy_result is not None:
                    legacy_metrics = legacy_result  # type: ignore[assignment]
            except Exception as e:
                legacy_metrics = {"error": str(e)}
        else:
            legacy_metrics = self._standard_metrics(x, y)

        # Run System train_step
        system = self.to_system()
        system_metrics: dict[str, object] = {}
        try:
            system_metrics = system.train_step(x, y)  # type: ignore[assignment]
        except Exception as e:
            system_metrics = {"error": str(e)}

        # Compare metrics
        differences, all_passed = self._compare_metrics(
            legacy_metrics, system_metrics, rtol, atol
        )

        return {
            "passed": all_passed,
            "legacy_metrics": legacy_metrics,
            "system_metrics": system_metrics,
            "differences": differences,
            "details": {
                "rtol": rtol,
                "atol": atol,
                "input_shape": tuple(x.shape),
                "target_shape": tuple(y.shape),
                "family": type(self.model).__name__.lower(),
            },
        }

    def _standard_metrics(self, x: Tensor, y: Tensor) -> dict[str, object]:
        """Loss/accuracy for models without a ``train_step`` method."""
        from computronium.core.losses import compute_loss

        was_training = self.model.training
        self.model.eval()
        with torch.no_grad():
            logits = self.model(x)
            loss = compute_loss(nn.CrossEntropyLoss(), logits, y)
        if was_training:
            self.model.train()
        acc = (logits.argmax(-1) == y).float().mean().item()
        return {"loss": float(loss.item()), "accuracy": acc}

    @staticmethod
    def _compare_metrics(
        legacy: dict[str, object],
        system: dict[str, object],
        rtol: float,
        atol: float,
    ) -> tuple[dict[str, dict[str, object]], bool]:
        """Compare legacy and system metrics, return differences and pass status."""
        differences: dict[str, dict[str, object]] = {}
        all_passed = True

        for key in set(legacy.keys()) | set(system.keys()):
            legacy_val = legacy.get(key)
            system_val = system.get(key)
            if legacy_val is not None and system_val is not None:
                if isinstance(legacy_val, (int, float)) and isinstance(
                    system_val, (int, float)
                ):
                    diff = abs(legacy_val - system_val)
                    rel_diff = diff / (abs(legacy_val) + atol)
                    differences[key] = {
                        "legacy": legacy_val,
                        "system": system_val,
                        "abs_diff": diff,
                        "rel_diff": rel_diff,
                    }
                    if rel_diff > rtol and diff > atol:
                        all_passed = False
                elif isinstance(legacy_val, Tensor) and isinstance(system_val, Tensor):
                    diff = (legacy_val - system_val).abs().max().item()
                    differences[key] = {"abs_diff": diff}
                    if diff > atol:
                        all_passed = False
                else:
                    differences[key] = {
                        "legacy": legacy_val,
                        "system": system_val,
                        "type_mismatch": True,
                    }
                    all_passed = False
            else:
                differences[key] = {
                    "legacy": legacy_val,
                    "system": system_val,
                    "missing": True,
                }
                all_passed = False

        return differences, all_passed


class _AdaptedSystem:
    """Internal adapter wrapping a model as a System."""

    def __init__(
        self,
        substrate: Substrate,
        geometry: Geometry,
        dynamics: StateDynamics,
        credit: CreditAssignment,
        update: ParameterUpdate,
        model: nn.Module,
    ):
        self.substrate = substrate
        self.geometry = geometry
        self.dynamics = dynamics
        self.credit = credit
        self.update = update
        self._model = model
        self._optimizer: torch.optim.Optimizer | None = None

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        model_train_step = cast(
            "Callable[[Tensor, Tensor], dict[str, float]] | None",
            getattr(self._model, "train_step", None),
        )
        if model_train_step is not None:
            return model_train_step(x, y)
        from computronium.core.trainer import bptt_step

        if self._optimizer is None:
            self._optimizer = torch.optim.SGD(
                self._model.parameters(), lr=self.update.config.step_size
            )
        out = bptt_step(self._model, self._optimizer, x, y)
        logits: Tensor = out["logits"]  # type: ignore[assignment]
        acc = (logits.argmax(-1) == y).float().mean().item()
        loss_raw = out["loss"]
        if not isinstance(loss_raw, int | float | Tensor):
            raise TypeError(f"bptt_step returned non-numeric loss: {type(loss_raw)!r}")
        return {"loss": float(loss_raw), "accuracy": acc}

    def forward(self, x: Tensor) -> Tensor:
        return self._model(x)

    def to_spec(self) -> dict[str, object]:
        return {
            "schema_version": "1.0",
            "substrate": self.substrate.config.__dict__,
            "geometry": self.geometry.config.__dict__,
            "dynamics": self.dynamics.config.__dict__,
            "credit": self.credit.config.__dict__,
            "update": self.update.config.__dict__,
        }

    @classmethod
    def from_spec(
        cls, spec: dict[str, object]
    ) -> System[Substrate, Geometry, StateDynamics, CreditAssignment, ParameterUpdate]:
        raise NotImplementedError("Cannot reconstruct adapted system from spec")
