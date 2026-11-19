"""System Composition: 6-D Ontology (S ⊗ G ⊗ D ⊗ M ⊗ C ⊗ U)."""

from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass
from enum import StrEnum
from typing import (
    TYPE_CHECKING,
    Final,
    Protocol,
    Self,
    TypeVar,
    cast,
    runtime_checkable,
)

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

# Declared structural voids: credits that assume sample-mode activations cannot
# run on an NCA geometry's cell-mode activations [B*H*W, C] with instantaneous
# dynamics. This tuple is the one source: ``SystemConfig.validate`` refuses
# these coordinates and the constraint registry projects the same names into
# its rows (TODO90 B9). Adding a credit here changes both at once.
NCA_CELL_MODE_CREDITS: Final[tuple[str, ...]] = ("homeostatic", "pc_alm")

# Geometries with no layer stack for the settle kernel to iterate, so every
# settling dynamic is refused at compose time ("Energy-based settling requires
# a layered geometry", measured 2026-11-13 TODO91 S6). This set is the one
# source: ``SystemConfig.validate`` refuses these coordinates and the
# constraint registry projects the same names into its rows. ``graph`` is
# deliberately absent — measured, graph + energy_minimization settles.
# ``routing`` joins them: a hard top-k selection is a discrete mixture, not
# a layer the settle math can iterate.
NONLAYERED_GEOMETRIES: Final[frozenset[str]] = frozenset({
    "attention",
    "spatial_lattice",
    "nca",
    "ntm",
    "tile",
    "tile_mesh",
    "conv",
    "causal_transformer",
    "routing",
})

# Dynamics that need a layer stack to settle.
SETTLING_DYNAMICS: Final[frozenset[str]] = frozenset({
    "energy_minimization",
    "predictive_settling",
    "error_predictive_coding",
    "pc_alm",
    "diffusion",
    "spike_integration",
    "lazy",
})

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Iterable, Iterator

    from computronium.acceleration.kernel_backend import KernelBackend

logger = logging.getLogger(__name__)

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
    _kernel_backend: KernelBackend | None
    # The task's declared loss (``DomainTask.compute_loss``), or ``None`` for
    # the cross-entropy fallback. Declared where the task and the system meet
    # (composition), never inferred from the output width.
    loss_fn: Callable[[Tensor, Tensor], Tensor] | None

    def train_step(self, x: Tensor, y: Tensor, **graph_kwargs) -> dict[str, float]:
        """Execute one training step through the family-neutral pipeline.

        Extra keyword arguments (e.g., edge_index, batch for graph classification)
        are forwarded to geometry.forward and dynamics.settle.
        """
        from computronium.core.pipeline import run_train_step

        return run_train_step(
            self.substrate,
            self.geometry,
            self.dynamics,
            self.credit,
            self.update,
            x,
            y,
            loss_fn=getattr(self, "loss_fn", None),
            **graph_kwargs,
        )

    def forward(self, x: Tensor, *args, **kwargs) -> Tensor:
        """Inference forward pass (free phase only, no weight updates).

        Supports additional arguments for graph classification:
        forward(x, edge_index, batch) -> passes through to geometry.forward
        """
        from computronium.core.pipeline import run_forward

        return run_forward(
            self.substrate, self.geometry, self.dynamics, x, *args, **kwargs
        )

    def __call__(self, x: Tensor) -> Tensor:
        """Call the system like a model: ``system(x)``."""
        ...

    @property
    def training(self) -> bool:
        """PyTorch compatibility: training mode flag."""
        ...

    def train(self, mode: bool = True) -> Self:
        """Set training mode (nn.Module compat)."""
        ...

    def eval(self) -> Self:
        """Set evaluation mode (nn.Module compat)."""
        ...

    def zero_grad(self, set_to_none: bool = True) -> None:
        """Clear parameter gradients (nn.Module compat)."""
        ...

    def parameters(self) -> Iterable[Tensor]:
        """Iterate over learnable parameters (nn.Module compat)."""
        ...

    def attach_kernel_backend(self, backend: KernelBackend) -> None:
        """Attach a kernel backend for accelerated training.

        The backend will be bound to this system's geometry via
        ``backend.bind_system(self)``.
        """
        ...

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


# Coordinate-based tolerances for validation
# Keyed by (credit_type, dynamics_type) tuple for precise matching
COORDINATE_TOLERANCES: dict[tuple[str, str], tuple[float, float]] = {
    ("thermodynamic_contrast", "energy_minimization"): (0.15, 1e-2),  # EqProp
    ("equilibrium", "energy_minimization"): (0.15, 1e-2),  # EqProp variants
    ("thermodynamic_contrast", "predictive_settling"): (0.1, 5e-3),  # PC
    ("local_goodness", "predictive_settling"): (0.05, 1e-3),  # FF/PEPITA
    ("pepita", "instantaneous"): (0.05, 1e-3),  # PEPITA
    ("local_goodness", "instantaneous"): (0.05, 1e-3),  # Forward-Forward
    ("random_projections", "instantaneous"): (0.1, 5e-3),  # FA/DFA
    ("temporal_trace", "instantaneous"): (0.2, 1e-2),  # Hebbian
    ("temporal_trace", "spike_integration"): (0.2, 1e-2),  # SNN/STDP
    ("target_inversion", "instantaneous"): (0.1, 5e-3),  # Target Prop
    ("gradient", "instantaneous"): (0.01, 1e-4),  # Backprop
}

DEFAULT_TOLERANCES: tuple[float, float] = (0.1, 1e-3)


# The axis-value compatibility tables. Each is the one table for its rule:
# ``SystemConfig.validate`` reads it and the declarative constraint row is
# its projection (``seed_registries`` builds the predicate from the same
# tuple), so the planner and the trainer cannot disagree.
RECURRENT_DYNAMICS: Final[frozenset[str]] = frozenset({
    "energy_minimization",
    "predictive_settling",
    "error_predictive_coding",
    "pc_alm",
    "diffusion",
    "instantaneous",
})
THERMO_CREDITS: Final[frozenset[str]] = frozenset({
    "thermodynamic_contrast",
    "equilibrium",
})
THERMO_CREDIT_DYNAMICS: Final[frozenset[str]] = frozenset({
    "energy_minimization",
    "predictive_settling",
    "error_predictive_coding",
    "lazy",
    "pc_alm",
})
SPIKE_INTEGRATION_CREDITS: Final[frozenset[str]] = frozenset({
    "temporal_trace",
    "spiking",
    "target_inversion",
    "target_prop",
})
QUANTUM_DYNAMICS: Final[frozenset[str]] = frozenset({
    "energy_minimization",
    "instantaneous",
    "diffusion",
})
PREDICTIVE_SETTLING_CREDITS: Final[frozenset[str]] = frozenset({
    "thermodynamic_contrast",
    "equilibrium",
    "local_goodness",
    "forward_only",
})
# Credits that read a dense ``Linear`` stack directly (``_stack``). The local
# family, plus ``local_supervision`` whose name predates it. Their only legal
# geometry is ``LOCAL_STACK_GEOMETRIES``.
LOCAL_STACK_CREDITS: Final[frozenset[str]] = frozenset({
    "local_goodness",
    "forward_only",
    "pepita",
    "local_contrastive",
    "local_supervision",
})
LOCAL_STACK_GEOMETRIES: Final[frozenset[str]] = frozenset({"feedforward"})
# Credits that pair each weight with the act it *produces* (target
# propagation's transpose feedback, STDP's correlation). The causal
# transformer's chain carries inputs only, so these have no partner act there.
TRANSFORMER_UNPAIRED_CREDITS: Final[frozenset[str]] = frozenset({
    "target_inversion",
    "temporal_trace",
})
# Credits whose per-head form the multi-head attention mix breaks (measured
# shape mismatch, TODO89).
ATTENTION_INCOMPATIBLE_CREDITS: Final[frozenset[str]] = frozenset({
    "pepita",
    "local_goodness",
    "local_contrastive",
    "forward_only",
})
# PC-ALM's dual/ALM settle runs over these credits and layer stacks.
PC_ALM_CREDITS: Final[frozenset[str]] = frozenset({
    "pc_alm",
    "thermodynamic_contrast",
})
PC_ALM_GEOMETRIES: Final[frozenset[str]] = frozenset({
    "feedforward",
    "recurrent",
    "tile_mesh",
})
# The PC-ALM credit reads ``dual_vars``, which only ``pc_alm`` dynamics
# writes; with any other dynamics it degenerates to a zero update.
PC_ALM_DUAL_CREDITS: Final[frozenset[str]] = frozenset({"pc_alm"})
PC_ALM_CREDIT_DYNAMICS: Final[frozenset[str]] = frozenset({"pc_alm"})
# Fast-weight plasticity modulates per-sample activations ``[B, fw_dim]``;
# these geometries give per-cell (nca/ntm) or tiled (tile/tile_mesh)
# activations instead.
NO_FAST_WEIGHT_GEOMETRIES: Final[frozenset[str]] = frozenset({
    "nca",
    "ntm",
    "tile",
    "tile_mesh",
})

__all__ = [
    "ATTENTION_INCOMPATIBLE_CREDITS",
    "LOCAL_STACK_CREDITS",
    "LOCAL_STACK_GEOMETRIES",
    "NO_FAST_WEIGHT_GEOMETRIES",
    "PC_ALM_CREDITS",
    "PC_ALM_CREDIT_DYNAMICS",
    "PC_ALM_DUAL_CREDITS",
    "PC_ALM_GEOMETRIES",
    "PREDICTIVE_SETTLING_CREDITS",
    "QUANTUM_DYNAMICS",
    "RECURRENT_DYNAMICS",
    "SPIKE_INTEGRATION_CREDITS",
    "THERMO_CREDITS",
    "THERMO_CREDIT_DYNAMICS",
    "TRANSFORMER_UNPAIRED_CREDITS",
    "ModelAdapter",
    "Phase",
    "System",
    "SystemConfig",
    "SystemState",
]


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
        self._validate_diffusion_dynamics_credit()
        self._validate_diffusion_dynamics_geometry()
        self._validate_spike_integration_credit()
        self._validate_predictive_settling_credit()
        self._validate_pc_alm_dynamics()
        self._validate_residual_connections()
        self._validate_nca_cell_mode_credits()

        # Geometry-Plasticity compatibility
        self._validate_fast_weight_plasticity_geometry()

        # Credit-Geometry compatibility
        self._validate_local_contrastive_geometry()
        self._validate_hybrid_geometry()
        self._validate_attention_geometry_compatibility()
        self._validate_transformer_pairing_credit()
        self._validate_temporal_credit_sequence()

        # Credit-Dynamics compatibility
        self._validate_thermodynamic_contrast_dynamics()

        # Beta matching (soft constraints, log only)
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
        self._validate_gradient_credit_instantaneous_recurrent()
        self._validate_per_element_displacement_step_size()
        self._validate_energy_minimization_momentum_update()

    # --- Validation Helpers ---

    def _require_when(
        self,
        condition: bool,
        allowed_values: Collection[str],
        axis_name: str,
        actual_value: str,
        context: str = "",
    ) -> None:
        """Raise ValueError if condition is true and actual_value not in allowed_values."""
        if condition and actual_value not in allowed_values:
            ctx = f" ({context})" if context else ""
            raise ValueError(
                f"{axis_name}={actual_value!r} requires one of {sorted(allowed_values)!r}{ctx}"
            )

    def _forbid_when(
        self,
        condition: bool,
        forbidden_values: Collection[str],
        axis_name: str,
        actual_value: str,
        context: str = "",
    ) -> None:
        """Raise ValueError if condition is true and actual_value in forbidden_values."""
        if condition and actual_value in forbidden_values:
            ctx = f" ({context})" if context else ""
            raise ValueError(f"{axis_name}={actual_value!r} is incompatible{ctx}")

    def _require_all_when(
        self,
        condition: bool,
        requirements: dict[str, set[str]],
        context: str = "",
    ) -> None:
        """Raise ValueError if condition is true and any requirement not met.

        requirements maps axis_name -> allowed_values for that axis.
        """
        if not condition:
            return
        for axis_name, allowed in requirements.items():
            actual = getattr(self, axis_name)
            # Handle nested attributes like geometry.topology_type
            if "." in axis_name:
                obj_name, attr_name = axis_name.split(".", 1)
                obj = getattr(self, obj_name)
                actual = getattr(obj, attr_name)
            self._require_when(True, allowed, axis_name, actual, context)

    def _forbid_any_when(
        self,
        condition: bool,
        forbidden: dict[str, set[str]],
        context: str = "",
    ) -> None:
        """Raise ValueError if condition is true and any forbidden value is present."""
        if not condition:
            return
        for axis_name, forbidden_vals in forbidden.items():
            actual = getattr(self, axis_name)
            if "." in axis_name:
                obj_name, attr_name = axis_name.split(".", 1)
                obj = getattr(self, obj_name)
                actual = getattr(obj, attr_name)
            self._forbid_when(True, forbidden_vals, axis_name, actual, context)

    # --- Geometry-Dynamics Validation Methods ---

    def _validate_recurrent_geometry_dynamics(self) -> None:
        """Recurrent geometry requires energy-based, PC-family, diffusion, or instantaneous dynamics."""
        self._require_when(
            condition=self.geometry.topology_type in {"recurrent"},
            allowed_values=RECURRENT_DYNAMICS,
            axis_name="dynamics.dynamics_type",
            actual_value=self.dynamics.dynamics_type,
            context=f"recurrent geometry (topology_type={self.geometry.topology_type!r})",
        )

    def _validate_nonlayered_geometry_dynamics(self) -> None:
        """Non-layered geometries cannot host settling dynamics."""
        self._forbid_when(
            condition=self.geometry.topology_type in NONLAYERED_GEOMETRIES,
            forbidden_values=SETTLING_DYNAMICS,
            axis_name="dynamics.dynamics_type",
            actual_value=self.dynamics.dynamics_type,
            context=f"{self.geometry.topology_type!r} geometry cannot host settling dynamics",
        )

    def _validate_diffusion_dynamics_credit(self) -> None:
        """Diffusion settle produces non-differentiable state; gradient/backprop unsupported."""
        self._forbid_when(
            condition=self.dynamics.dynamics_type == "diffusion",
            forbidden_values={"gradient", "backprop"},
            axis_name="credit.credit_type",
            actual_value=self.credit.credit_type,
            context="diffusion dynamics produce non-differentiable settled state",
        )

    def _validate_diffusion_dynamics_geometry(self) -> None:
        """Diffusion dynamics requires an energy-based, single-batch geometry.

        A time-major geometry (``sequence=True``, which a credit's
        ``requires_sequence`` declaration sets) unrolls its own time axis, so
        the Langevin interaction energy sees a 3-D activation stack and refuses
        it (measured: diffusion × eligibility_prop × recurrent raised
        ``size of tensor a (3) must match tensor b (4)`` in
        ``_compute_interaction_energy``). Diffusion iterates to a fixed point
        over one batch; the two time axes cannot coexist.
        """
        self._require_when(
            condition=self.dynamics.dynamics_type == "diffusion",
            allowed_values={"recurrent"},
            axis_name="geometry.topology_type",
            actual_value=self.geometry.topology_type,
            context="diffusion dynamics requires recurrent geometry",
        )
        if self.dynamics.dynamics_type == "diffusion" and self.geometry.sequence:
            msg = (
                "diffusion dynamics settle one batch; a time-major geometry "
                "(geometry.sequence=True) unrolls a second time axis, which "
                "the Langevin interaction energy cannot read"
            )
            raise ValueError(msg)

    def _validate_spike_integration_credit(self) -> None:
        """Spike integration dynamics requires temporal trace or target inversion credit."""
        self._require_when(
            condition=self.dynamics.dynamics_type == "spike_integration",
            allowed_values=SPIKE_INTEGRATION_CREDITS,
            axis_name="credit.credit_type",
            actual_value=self.credit.credit_type,
            context="spike integration dynamics",
        )

    def _validate_predictive_settling_credit(self) -> None:
        """Predictive settling dynamics requires compatible credit."""
        self._require_when(
            condition=self.dynamics.dynamics_type
            in {"predictive_settling", "error_predictive_coding"},
            allowed_values=PREDICTIVE_SETTLING_CREDITS,
            axis_name="credit.credit_type",
            actual_value=self.credit.credit_type,
            context=f"{self.dynamics.dynamics_type} dynamics",
        )

    def _validate_pc_alm_dynamics(self) -> None:
        """PC-ALM dynamics requires its credit family and a layered geometry."""
        self._require_when(
            condition=self.dynamics.dynamics_type == "pc_alm",
            allowed_values=PC_ALM_CREDITS,
            axis_name="credit.credit_type",
            actual_value=self.credit.credit_type,
            context="PC-ALM dynamics",
        )
        self._require_when(
            condition=self.dynamics.dynamics_type == "pc_alm",
            allowed_values=PC_ALM_GEOMETRIES,
            axis_name="geometry.topology_type",
            actual_value=self.geometry.topology_type,
            context="PC-ALM dynamics requires layered geometry",
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

    def _validate_nca_cell_mode_credits(self) -> None:
        """NCA + instantaneous dynamics refuses credits that read sample-mode activations."""
        if (
            self.geometry.topology_type == "nca"
            and self.dynamics.dynamics_type == "instantaneous"
            and self.credit.credit_type in NCA_CELL_MODE_CREDITS
        ):
            raise ValueError(
                "NCA geometry with instantaneous dynamics incompatible with "
                f"{self.credit.credit_type} credit (cell-mode activations)"
            )

    def _validate_fast_weight_plasticity_geometry(self) -> None:
        """Fast-weight plasticity needs per-sample activations these geometries lack."""
        self._forbid_when(
            condition=self.geometry.topology_type in NO_FAST_WEIGHT_GEOMETRIES,
            forbidden_values={"fast_weights"},
            axis_name="plasticity.plasticity_type",
            actual_value=self.plasticity.plasticity_type,
            context=(
                f"{self.geometry.topology_type!r} geometry gives per-cell or "
                "tiled activations, not per-sample"
            ),
        )

    def _validate_thermodynamic_contrast_dynamics(self) -> None:
        """Thermodynamic contrast credit requires energy-based or PC-family dynamics."""
        self._require_when(
            condition=self.credit.credit_type in THERMO_CREDITS,
            allowed_values=THERMO_CREDIT_DYNAMICS,
            axis_name="dynamics.dynamics_type",
            actual_value=self.dynamics.dynamics_type,
            context=f"{self.credit.credit_type!r} credit reads an energy settle",
        )

    # --- Beta Matching (Soft Constraints) ---

    def _validate_beta_matching_energy_minimization(self) -> None:
        """Energy minimization dynamics requires matching beta between dynamics and credit."""
        if self.dynamics.dynamics_type == "energy_minimization":
            if abs(self.dynamics.beta - self.credit.beta) > 1e-6:
                logger.debug(
                    "Beta mismatch: dynamics.beta=%s != credit.beta=%s. "
                    "This may cause incorrect gradient scaling in EqProp.",
                    self.dynamics.beta,
                    self.credit.beta,
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
        if self.substrate.substrate_type == "neuromorphic":
            if self.dynamics.dynamics_type not in {
                "spike_integration",
                "energy_minimization",
                "diffusion",
            }:
                raise ValueError(
                    f"Neuromorphic substrate requires temporal dynamics "
                    f"(spike_integration, energy_minimization, or diffusion), "
                    f"got {self.dynamics.dynamics_type!r}"
                )

    def _validate_analog_substrate_noise(self) -> None:
        """Analog substrate with noise warns on instantaneous dynamics."""
        if self.substrate.precision == "float32" and self.substrate.noise_level > 0.0:
            if self.dynamics.dynamics_type == "instantaneous":
                logger.debug(
                    "Analog substrate with noise_level=%s "
                    "used with instantaneous dynamics. Noise only applied once at input. "
                    "Consider energy_minimization or diffusion dynamics for continuous noise injection.",
                    self.substrate.noise_level,
                )

    def _validate_complex_substrate_credit(self) -> None:
        """Complex substrate works best with thermodynamic contrast or backprop."""
        if (
            self.substrate.precision == "float32"
            and getattr(self.substrate, "_complex_emulated", False)
            and self.credit.credit_type
            not in {
                "thermodynamic_contrast",
                "equilibrium",
                "gradient",
                "backprop",
            }
        ):
            logger.debug(
                "Complex substrate used with %s credit. "
                "Best results with thermodynamic_contrast (holomorphic EqProp) "
                "or gradient (holomorphic backprop).",
                self.credit.credit_type,
            )

    def _validate_quantum_substrate_dynamics(self) -> None:
        """Quantum substrate requires compatible dynamics and beta matching."""
        if self.substrate.precision == "complex64":
            if self.dynamics.dynamics_type not in QUANTUM_DYNAMICS:
                raise ValueError(
                    f"Quantum substrate requires energy_minimization, instantaneous, "
                    f"or diffusion dynamics, got {self.dynamics.dynamics_type!r}"
                )
            if self.credit.credit_type in {"thermodynamic_contrast", "equilibrium"}:
                if abs(self.dynamics.beta - self.credit.beta) > 1e-6:
                    logger.debug(
                        "Quantum substrate with thermodynamic contrast: "
                        "beta mismatch dynamics.beta=%s != credit.beta=%s. "
                        "Phase-sensitive gradients require matched beta.",
                        self.dynamics.beta,
                        self.credit.beta,
                    )

    def _validate_sparse_substrate_update(self) -> None:
        """Sparse substrate warns on RiemannianOrthogonalUpdate."""
        if self.substrate.sparsity > 0.5:
            if self.update.update_type == "riemannian_orthogonal":
                logger.debug(
                    "Sparse substrate (sparsity=%s) with "
                    "RiemannianOrthogonalUpdate may densify weights. "
                    "Consider SpectralConstrainedUpdate or ElasticConsolidationUpdate.",
                    self.substrate.sparsity,
                )

    def _validate_ternary_substrate_credit(self) -> None:
        """Ternary-like substrate works best with thermodynamic contrast or backprop."""
        if (
            self.substrate.precision == "float32"
            and self.substrate.sparsity == 0.0
            and self.substrate.weight_bounds == (-1.0, 1.0)
        ) and self.credit.credit_type not in {
            "thermodynamic_contrast",
            "equilibrium",
            "gradient",
            "backprop",
        }:
            logger.debug(
                "Ternary-like substrate used with %s credit. "
                "Best results with thermodynamic_contrast (Ternary EqProp) "
                "or gradient (Ternary backprop with STE).",
                self.credit.credit_type,
            )

    def _validate_diffusion_substrate_noise(self) -> None:
        """Diffusion dynamics requires substrate noise_level > 0."""
        if self.dynamics.dynamics_type == "diffusion":
            if self.substrate.noise_level == 0.0:
                warnings.warn(
                    f"Diffusion dynamics (Langevin) with substrate "
                    f"noise_level={self.substrate.noise_level} has no noise term, so "
                    f"the dynamics degenerates to deterministic relaxation; set a "
                    f"positive noise_level on the substrate for proper sampling.",
                    UserWarning,
                    stacklevel=2,
                )

    def _validate_local_contrastive_geometry(self) -> None:
        """Credits that read a dense ``Linear`` stack require feedforward geometry."""
        geom_type = getattr(self.geometry, "config", self.geometry).topology_type
        self._require_when(
            condition=self.credit.credit_type in LOCAL_STACK_CREDITS,
            allowed_values=LOCAL_STACK_GEOMETRIES,
            axis_name="geometry.topology_type",
            actual_value=geom_type,
            context=f"{self.credit.credit_type!r} credit reads the layer stack",
        )

    def _validate_hybrid_geometry(self) -> None:
        """The hybrid's split is a dense stack boundary; refuse other shapes."""
        if self.credit.credit_type != "hybrid":
            return
        geom_type = getattr(self.geometry, "config", self.geometry).topology_type
        if geom_type != "feedforward":
            raise ValueError(
                f"HybridCredit (credit_type='hybrid') requires a feedforward "
                f"layer stack with split_layer at a Linear, got {geom_type!r}"
            )

    def _validate_attention_geometry_compatibility(self) -> None:
        """Attention geometry refuses the credits whose per-head shape it breaks."""
        geom_type = getattr(self.geometry, "config", self.geometry).topology_type
        self._forbid_when(
            condition=geom_type == "attention",
            forbidden_values=ATTENTION_INCOMPATIBLE_CREDITS,
            axis_name="credit.credit_type",
            actual_value=self.credit.credit_type,
            context="known shape mismatch in multi-head attention",
        )

    def _validate_transformer_pairing_credit(self) -> None:
        """Credits that pair a weight with the act it produces need a chain
        the transformer's does not provide.

        The transformer's activation chain carries one act per weight (the
        act the weight consumes) plus the logits: the fused QKV widens the
        error space to 3d before the attention narrows it back, and the
        vision readout pools the sequence. A credit that pairs each weight
        with the act it *produces* — the target propagation's transpose
        feedback, the STDP correlation — therefore has no partner act, and
        the coordinate cannot train. Reject it here rather than let it
        crash on a shape mismatch mid-epoch.
        """
        if self.credit.credit_type not in TRANSFORMER_UNPAIRED_CREDITS:
            return
        geom_type = getattr(self.geometry, "config", self.geometry).topology_type
        self._forbid_when(
            condition=geom_type == "causal_transformer",
            forbidden_values=TRANSFORMER_UNPAIRED_CREDITS,
            axis_name="credit.credit_type",
            actual_value=self.credit.credit_type,
            context="the causal_transformer chain carries inputs only",
        )

    def _validate_temporal_credit_sequence(self) -> None:
        """A temporal credit reads a time-major state; the geometry owns the axis.

        The credit's contract is ``x (time, batch, input)`` and
        ``y (time, batch)`` (TODO93 §19). A geometry that folds the time
        axis into features has no time axis, so the credit would fail loud
        inside the cell; refuse the composition here, by name, instead.
        """
        if not self.credit.requires_sequence:
            return
        if self.geometry.topology_type == "recurrent" and self.geometry.sequence:
            return
        raise ValueError(
            f"{self.credit.credit_type!r} credit reads a sequence "
            "(time, batch, input); a recurrent geometry with sequence=True "
            f"owns that axis, got geometry={self.geometry.topology_type!r} "
            f"with sequence={self.geometry.sequence}"
        )

    # --- Geometry-Substrate Validation Methods ---

    def _validate_spatial_neuromorphic_geometry_substrate(self) -> None:
        """Spatial/neuromorphic geometry works best with neuromorphic substrate."""
        if self.geometry.topology_type in {"spatial_lattice", "neuromorphic", "fabric"}:
            if not (
                self.substrate.precision == "float16" and self.substrate.sparsity > 0.9
            ):
                logger.debug(
                    "Spatial/neuromorphic geometry (%s) "
                    "works best with neuromorphic substrate (float16, high sparsity). "
                    "Current substrate: precision=%s, sparsity=%s",
                    self.geometry.topology_type,
                    self.substrate.precision,
                    self.substrate.sparsity,
                )

    def _validate_tile_mesh_sparse_substrate(self) -> None:
        """Tile mesh with sparse substrate warns about structured sparsity."""
        if (
            self.geometry.topology_type in {"tile_mesh", "tile"}
            and self.substrate.sparsity > 0.5
        ):
            logger.debug(
                "Sparse substrate (sparsity=%s) "
                "with tile mesh geometry may benefit from structured sparsity (N:M or block) "
                "for efficient matmul.",
                self.substrate.sparsity,
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

    def _validate_gradient_credit_instantaneous_recurrent(self) -> None:
        """Gradient/backprop credit with instantaneous dynamics on recurrent geometry
        fails because the recurrent weights are not in the feedforward loss graph."""
        if (
            self.dynamics.dynamics_type == "instantaneous"
            and self.geometry.topology_type in {"recurrent"}
            and self.credit.credit_type in {"gradient", "backprop"}
        ):
            raise ValueError(
                "GradientCredit/BackpropCredit with instantaneous dynamics on recurrent "
                "geometry cannot compute gradients for recurrent weights (not in "
                "feedforward pass). Use energy_minimization, predictive_settling, "
                "error_predictive_coding, pc_alm, or diffusion dynamics instead."
            )

    def _validate_per_element_displacement_step_size(self) -> None:
        """Per-element-displacement update rules warn on gradient-relative step_size range."""
        if (
            self.update.step_semantics == "per_element_displacement"
            and self.update.step_size > 0.05
        ):
            warnings.warn(
                f"update_type={self.update.update_type} uses per-element-displacement "
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
            logger.debug(
                "EnergyMinimizationDynamics with momentum=%s "
                "combined with RiemannianOrthogonalUpdate may cause instability. "
                "Consider EuclideanUpdate with momentum.",
                self.dynamics.momentum,
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

    def _get_coordinate_tolerances(self) -> tuple[float, float]:
        """Get coordinate-specific tolerances from the adapted system's axes."""
        # Build a temporary system to read the coordinate axes
        system = self.to_system()
        credit_type = system.credit.config.credit_type
        dynamics_type = system.dynamics.config.dynamics_type
        return COORDINATE_TOLERANCES.get(
            (credit_type, dynamics_type), DEFAULT_TOLERANCES
        )

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
        # Use coordinate-specific tolerances if not explicitly provided
        if rtol is None or atol is None:
            coord_rtol, coord_atol = self._get_coordinate_tolerances()
            rtol = rtol if rtol is not None else coord_rtol
            atol = atol if atol is not None else coord_atol

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
                "credit_type": system.credit.config.credit_type,
                "dynamics_type": system.dynamics.config.dynamics_type,
                "topology_type": system.geometry.config.topology_type,
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
        self._kernel_backend: KernelBackend | None = None

    def train_step(self, x: Tensor, y: Tensor) -> dict[str, float]:
        # Delegate to kernel backend if attached
        if self._kernel_backend is not None:
            return self._kernel_backend.train_step(x, y)
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

    def __call__(self, x: Tensor) -> Tensor:
        return self.forward(x)

    @property
    def training(self) -> bool:
        return self._model.training

    def train(self, mode: bool = True) -> Self:
        self._model.train(mode)
        return self

    def eval(self) -> Self:
        self._model.eval()
        return self

    def zero_grad(self, set_to_none: bool = True) -> None:
        self._model.zero_grad(set_to_none)

    def parameters(self) -> Iterator[Tensor]:
        return self._model.parameters()

    def attach_kernel_backend(self, backend: KernelBackend) -> None:
        """Attach a kernel backend for accelerated training."""
        backend.bind_system(self)
        self._kernel_backend = backend

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
