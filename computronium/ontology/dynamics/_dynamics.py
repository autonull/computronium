"""Layer 3: StateDynamics — Forward Evolution & Settling."""

from __future__ import annotations

import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol, cast, runtime_checkable

import torch
from torch import Tensor, nn

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology.geometry import Geometry
    from computronium.ontology.substrate import Substrate
    from computronium.state import CompositeState
    from computronium.state.composite import ActivityValue

from computronium.ontology._settle_kernel import (
    LayeredParams,
    SubstrateSettleKernel,
    _compiled_eqprop_settle,
    _one_hot,
    extract_layered_params,
)
from computronium.ontology.geometry import layer_stack

GainControlMode = Literal["none", "unit_rms", "spectral"]


def _apply_gain_control(acts: list[Tensor], mode: GainControlMode) -> list[Tensor]:
    """Settle-path gain homeostasis (TODO12 A5, RESEARCH4 Lever 3).

    Renormalizes hidden-layer activations at settle emit — the structural
    pipeline primitive replacing scattered per-rule renorms. "unit_rms" is
    the μPC recipe (a·√d/‖a‖ per sample); "spectral" rescales each hidden
    layer's batch matrix to unit spectral norm. Input and output layers
    pass through untouched (the output carries the readout logits); zero
    and non-finite layers pass through untouched — never fabricated signal.
    """
    if mode == "none" or len(acts) < 3:
        return acts
    out = list(acts)
    for i in range(1, len(acts) - 1):
        a = acts[i]
        if not torch.isfinite(a).all():
            continue
        if mode == "unit_rms":
            norm = a.float().norm(dim=-1, keepdim=True)
            scale = torch.where(
                norm > 0,
                a.shape[-1] ** 0.5 / (norm + 1e-8),
                torch.ones_like(norm),
            ).to(a.dtype)
            out[i] = a * scale
        else:  # "spectral"
            sigma = torch.linalg.matrix_norm(a.float(), ord=2)
            if sigma > 0:
                out[i] = (a.float() / (sigma + 1e-8)).to(a.dtype)
    return out


# ============================================================
# State type detection helpers (duck typing for SystemState + CompositeState)
# ============================================================


def _is_composite_state(state: object) -> bool:
    """Check if state is a CompositeState (has activity/plastic/substrate dicts)."""
    return hasattr(state, "activity") and isinstance(
        getattr(state, "activity", None), dict
    )


def _get_state_x(state: object) -> Tensor | None:
    """Get input x from either SystemState or CompositeState."""
    return getattr(state, "x", None)


def _get_state_activations(state: object) -> list[Tensor] | Tensor | None:
    """Get activations from either SystemState or CompositeState."""
    return getattr(state, "activations", None)


def _get_state_free_state(state: object) -> list[Tensor] | Tensor | None:
    """Get free_state from either SystemState or CompositeState."""
    return getattr(state, "free_state", None)


def _get_state_dual_vars(state: object) -> list[Tensor] | None:
    """Get dual_vars from either SystemState or CompositeState."""
    if _is_composite_state(state):
        activity = cast("CompositeState", state).activity
        return activity.get("dual_vars")
    return getattr(state, "dual_vars", None)


def _get_state_activity(state: object) -> dict[str, ActivityValue] | None:
    """Get the activity dict from a CompositeState-shaped state, else None."""
    if _is_composite_state(state):
        return cast("CompositeState", state).activity
    return None


def _energy_tensor(value: ActivityValue) -> Tensor:
    """Coerce an activity value to the tensor form used for energy sums."""
    match value:
        case Tensor():
            return value
        case int() | float():
            return torch.tensor(float(value))
        case list():
            if value and isinstance(value[0], Tensor):
                return value[-1]
            return torch.zeros(1)
        case dict():
            return torch.zeros(1)
        case _:
            return torch.zeros(1)


def _state_energy_vector(state: object) -> Tensor:
    """The activity field an output-energy reads: the last activation, else
    the ``output`` activity."""
    acts = _get_state_activations(state)
    if acts is not None:
        acts = acts if isinstance(acts, list) else [acts]
        return acts[-1] if acts else torch.zeros(1)
    activity = _get_state_activity(state)
    if not activity:
        return torch.zeros(1)
    return _energy_tensor(activity.get("output", torch.zeros(1)))


def _create_output_state(
    state: object,
    *,
    x: Tensor | None = None,
    output: Tensor | None = None,
    free_state: list[Tensor] | Tensor | None = None,
    nudged_state: list[Tensor] | Tensor | None = None,
    activations: list[Tensor] | Tensor | None = None,
    spike_counts: list[Tensor] | None = None,
    spike_rasters: list[list[Tensor]] | None = None,
    dual_vars: list[Tensor] | None = None,
) -> CompositeState:
    """Create a new state of the same type with updated fields.

    The 5-D pipeline passes SystemState, the 6-D joint path passes
    CompositeState; both are duck-typed here (circular imports forbid
    importing them statically). Legacy SystemState results are cast to the
    declared CompositeState contract.
    """
    if _is_composite_state(state):
        from computronium.state import CompositeState

        # Structural duck-typing: callers may pass either CompositeState
        # implementation (computronium.state / core.joint.state) — circular
        # imports forbid importing them here, hence the runtime check + cast.
        composite = cast("CompositeState", state)
        activity = dict(composite.activity)
        if x is not None:
            activity["x"] = x
        if output is not None:
            activity["output"] = output
        if free_state is not None:
            activity["free_state"] = free_state
        if nudged_state is not None:
            activity["nudged_state"] = nudged_state
        if activations is not None:
            activity["activations"] = activations
        if spike_counts is not None:
            activity["spike_counts"] = spike_counts
        if spike_rasters is not None:
            activity["spike_rasters"] = spike_rasters
        if dual_vars is not None:
            activity["dual_vars"] = dual_vars
        result: dict[str, ActivityValue] = activity
        return CompositeState(
            activity=result,
            plastic=composite.plastic,
            substrate=composite.substrate,
        )
    else:
        # SystemState - create new instance with updated fields
        from computronium.ontology.system import SystemState

        return cast(
            "CompositeState",
            SystemState(
                x=x if x is not None else getattr(state, "x", None),
                y=getattr(state, "y", None),
                activations=activations
                if activations is not None
                else getattr(state, "activations", None),
                free_state=free_state
                if free_state is not None
                else getattr(state, "free_state", None),
                nudged_state=nudged_state
                if nudged_state is not None
                else getattr(state, "nudged_state", None),
                pseudo_gradients=getattr(state, "pseudo_gradients", None),
                energy=getattr(state, "energy", None),
                loss=getattr(state, "loss", None),
                metrics=dict(getattr(state, "metrics", {}) or {}),
                spike_counts=spike_counts
                if spike_counts is not None
                else getattr(state, "spike_counts", None),
                spike_rasters=spike_rasters
                if spike_rasters is not None
                else getattr(state, "spike_rasters", None),
                dual_vars=dual_vars
                if dual_vars is not None
                else getattr(state, "dual_vars", None),
            ),
        )


# ============================================================
# StateDynamics Configuration
# ============================================================


@dataclass(frozen=True, slots=True)
class StateDynamicsConfig:
    """Configuration for state dynamics/settling.

    Attributes:
        dynamics_type: "energy_minimization", "predictive_settling",
            "error_predictive_coding", "spike_integration", "instantaneous",
            "diffusion", "lazy", "pc_alm"
        max_steps: Maximum settling iterations
        convergence_threshold: Early stopping threshold
        convergence_start: Step to start checking convergence
        step_size: Learning rate for state updates
        beta: Nudge strength for energy-based methods
        momentum: Momentum coefficient for heavy-ball dynamics (energy_minimization)
        threshold: Spike threshold for spike_integration dynamics
        track_free_energy_per_iter: Record free energy at each iteration
            for Control-Lyapunov analysis
        gradient_checkpointing: Use gradient checkpointing to trade compute
            for memory during settling (energy_minimization only)
        compiled: Run the layered settle loop under ``torch.compile``
            (predictive_settling, digital substrate, no recurrent weights,
            no per-iteration energy tracking; other combinations fall back
            to the eager path). First call pays a one-time compile; measured
            ~2x end-to-end train_step speedup at depth 8 / 60 steps.
        gain_control: Settle-path gain homeostasis (TODO12 A5, RESEARCH4
            Lever 3): renormalize hidden-layer activations at settle emit.
            "unit_rms" rescales each hidden layer per-sample to unit RMS
            (μPC-style: a·√d/‖a‖); "spectral" rescales each hidden layer's
            batch matrix to unit spectral norm. Input and output layers
            pass through untouched (the output carries the readout
            logits); non-finite layers pass through untouched. Realized on
            instantaneous and error_predictive_coding settles; other
            dynamics ignore it until their own audited pull.
        rho: Augmented Lagrangian penalty parameter for PC-ALM dynamics.
            Controls the weight of the quadratic penalty term in the
            augmented Lagrangian. Higher values enforce constraints more
            strictly but may slow convergence.
        prospective_leak: Leaky integration coefficient for the dual
            variables in PC-ALM. 0.0 = pure PC-ALM (integral-only PI
            controller). Values > 0 interpolate toward prospective
            configuration (proportional component), recovering gradient
            alignment properties. Range: [0.0, 1.0].
        warm_start_duals: Whether to warm-start dual variables from the
            previous train step's nudged phase. Default True. When False,
            dual variables are reset to zero at the start of each settle.
        rho_schedule: Schedule for the augmented Lagrangian penalty
            parameter rho during training. "constant" keeps rho fixed;
            "linear" increases linearly from rho to rho_final over training;
            "cosine" uses a cosine annealing schedule.
        rho_final: Final value of rho for scheduled increase (used when
            rho_schedule != "constant").
        gradient_checkpointing: Use gradient checkpointing to trade compute
            for memory during the primal-dual relaxation loop (PC-ALM only).
            Checkpoints every k steps where k = max_steps // 4.
    """

    dynamics_type: str
    max_steps: int
    convergence_threshold: float
    convergence_start: int
    step_size: float
    beta: float
    momentum: float
    track_free_energy_per_iter: bool
    threshold: float = 1.0
    gradient_checkpointing: bool = False
    compiled: bool = False
    gain_control: GainControlMode = "none"
    rho: float = 1.0
    prospective_leak: float = 0.0
    warm_start_duals: bool = True
    rho_schedule: Literal["constant", "linear", "cosine"] = "constant"
    rho_final: float = 1.0

    @classmethod
    def energy_minimization(  # ruff: ignore[too-many-arguments] (config mirrors the knobs)
        cls,
        *,
        max_steps: int = 30,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 5,
        step_size: float = 0.1,
        beta: float = 0.5,
        momentum: float = 0.0,
        track_free_energy_per_iter: bool = False,
        gradient_checkpointing: bool = False,
        compiled: bool = False,
        gain_control: GainControlMode = "none",
    ) -> StateDynamicsConfig:
        return cls(
            dynamics_type="energy_minimization",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=momentum,
            track_free_energy_per_iter=track_free_energy_per_iter,
            gradient_checkpointing=gradient_checkpointing,
            compiled=compiled,
            gain_control=gain_control,
        )

    @classmethod
    def predictive_settling(
        cls,
        *,
        max_steps: int = 30,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 5,
        step_size: float = 0.1,
        beta: float = 0.5,
        momentum: float = 0.0,
        track_free_energy_per_iter: bool = False,
        compiled: bool = False,
    ) -> StateDynamicsConfig:
        return cls(
            dynamics_type="predictive_settling",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=momentum,
            track_free_energy_per_iter=track_free_energy_per_iter,
            compiled=compiled,
        )

    @classmethod
    def spike_integration(
        cls,
        *,
        max_steps: int = 30,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 5,
        step_size: float = 0.1,
        beta: float = 0.5,
        momentum: float = 0.0,
        threshold: float = 1.0,
        track_free_energy_per_iter: bool = False,
        compiled: bool = False,
    ) -> StateDynamicsConfig:
        return cls(
            dynamics_type="spike_integration",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=momentum,
            threshold=threshold,
            track_free_energy_per_iter=track_free_energy_per_iter,
            compiled=compiled,
        )

    @classmethod
    def instantaneous(
        cls,
        *,
        max_steps: int = 1,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 1,
        step_size: float = 0.1,
        beta: float = 0.1,
        momentum: float = 0.0,
        track_free_energy_per_iter: bool = False,
        gain_control: GainControlMode = "none",
    ) -> StateDynamicsConfig:
        return cls(
            dynamics_type="instantaneous",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=momentum,
            track_free_energy_per_iter=track_free_energy_per_iter,
            gain_control=gain_control,
        )

    @classmethod
    def diffusion(
        cls,
        *,
        max_steps: int = 30,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 5,
        step_size: float = 0.1,
        beta: float = 0.5,
        momentum: float = 0.0,
        track_free_energy_per_iter: bool = False,
    ) -> StateDynamicsConfig:
        """Diffusion-based dynamics for continuous-time settling.

        Implements the dynamics: dh/dt = -∇E(h) + noise
        where E is the energy function and noise models diffusion.
        """
        return cls(
            dynamics_type="diffusion",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=momentum,
            track_free_energy_per_iter=track_free_energy_per_iter,
        )

    @classmethod
    def lazy(
        cls,
        *,
        max_steps: int = 30,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 5,
        step_size: float = 0.1,
        beta: float = 0.5,
        track_free_energy_per_iter: bool = False,
    ) -> StateDynamicsConfig:
        """Sequential (Gauss–Seidel) EqProp settle — lazy per-layer activation.

        Same symmetric-energy fixed point as energy_minimization, reached in
        systematically fewer sweeps: layers update one at a time per sweep,
        each reading its freshest neighbors. Layer-structured geometry
        required (fail-loud otherwise); no momentum.
        """
        return cls(
            dynamics_type="lazy",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=0.0,
            track_free_energy_per_iter=track_free_energy_per_iter,
        )

    @classmethod
    def error_predictive_coding(
        cls,
        *,
        max_steps: int = 10,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 1,
        step_size: float = 0.1,
        beta: float = 0.5,
        momentum: float = 0.0,
        track_free_energy_per_iter: bool = False,
        gain_control: GainControlMode = "none",
    ) -> StateDynamicsConfig:
        """Error-parameterized PC (ePC, Goemaere et al., arXiv:2505.20137, ICML 2026).

        Reparameterizes PC dynamics in terms of prediction errors εᵢ instead of
        states sᵢ. The state is sᵢ = ŝᵢ + εᵢ where ŝᵢ = f_θᵢ(sᵢ₋₁). Reverse-mode AD
        carries the output-loss gradient to all errors simultaneously — no signal
        decay — reaching the same PC equilibrium as sPC in a handful of steps.
        """
        return cls(
            dynamics_type="error_predictive_coding",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=momentum,
            track_free_energy_per_iter=track_free_energy_per_iter,
            gain_control=gain_control,
        )

    @classmethod
    def pc_alm(
        cls,
        *,
        max_steps: int = 30,
        convergence_threshold: float = 1e-4,
        convergence_start: int = 5,
        step_size: float = 0.1,
        beta: float = 0.5,
        rho: float = 1.0,
        prospective_leak: float = 0.0,
        momentum: float = 0.0,
        track_free_energy_per_iter: bool = False,
        compiled: bool = False,
        warm_start_duals: bool = True,
        rho_schedule: Literal["constant", "linear", "cosine"] = "constant",
        rho_final: float = 1.0,
    ) -> StateDynamicsConfig:
        """Augmented Lagrangian Predictive Coding (PC-ALM; Seely & Gould 2026, arXiv:2605.31022).

        Layer-local primal–dual dynamics replacing global backprop. Each layer
        maintains primal states (activations) and dual states (Lagrange
        multipliers / PI controller state). The augmented Lagrangian:

            L_ρ = Σₗ ½‖hₗ − f_θₗ(hₗ₋₁)‖² + Σₗ ⟨λₗ, hₗ − f_θₗ(hₗ₋₁)⟩
                  + (ρ/2) Σₗ ‖hₗ − f_θₗ(hₗ₋₁)‖²

        Dynamics (discretized):
            cₗ = hₗ − f_θₗ(hₗ₋₁)         # constraint violation
            λₗ ← λₗ + step_size · cₗ       # dual update (PI controller)
            hₗ ← hₗ − step_size · (cₗ + λₗ + ρ·cₗ − Jₗ₊₁ᵀ·(cₗ₊₁ + λₗ₊₁ + ρ·cₗ₊₁))

        Weight update (local Hebbian):
            ΔWₗ ∝ −λₗ hₗ₋₁ᵀ

        Args:
            max_steps: Maximum primal–dual iterations (inference budget T)
            convergence_threshold: Early stopping on max constraint violation
            convergence_start: Step to begin convergence checking
            step_size: Primal/dual learning rate (ηₕ = η_λ)
            beta: Nudge strength for nudged phase (output layer)
            rho: Augmented Lagrangian penalty parameter (ρ ≥ 0)
            prospective_leak: Leaky dual integration coefficient α ∈ [0,1].
                0.0 = pure PC-ALM (integral-only). >0 recovers prospective
                configuration properties (proportional component).
            momentum: Heavy-ball momentum for primal updates
            track_free_energy_per_iter: Record L_ρ per iteration
            compiled: Use torch.compile for the settle loop
            warm_start_duals: Warm-start dual variables from previous step.
            rho_schedule: Schedule for rho: "constant", "linear", "cosine".
            rho_final: Final rho value for scheduled increase.
        """
        return cls(
            dynamics_type="pc_alm",
            max_steps=max_steps,
            convergence_threshold=convergence_threshold,
            convergence_start=convergence_start,
            step_size=step_size,
            beta=beta,
            momentum=momentum,
            track_free_energy_per_iter=track_free_energy_per_iter,
            compiled=compiled,
            rho=rho,
            prospective_leak=prospective_leak,
            warm_start_duals=warm_start_duals,
            rho_schedule=rho_schedule,
            rho_final=rho_final,
        )


# ============================================================
# Compiled layered-settle loop (predictive_settling fast path)
# ============================================================


def _layered_settle_loop(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    step_size: float,
    n_steps: int,
) -> list[Tensor]:
    """Top-down prediction / bottom-up error correction over all layers.

    Digital-substrate arithmetic inlined (``op(x, w) == x @ w.T`` — bitwise
    equal to the eager path, verified by the compiled-settle lock). The
    whole settle is one compiled graph: one launch per settle instead of
    per layer-step.
    """
    for _ in range(n_steps):
        new_acts: list[Tensor] = [acts[0]]
        for i, w in enumerate(weights):
            h_upper = acts[i + 1]
            error = acts[i] - h_upper @ w
            new_acts.append(h_upper + step_size * (error @ w.T))
        acts = new_acts
    return acts


_compiled_layered_settle = torch.compile(_layered_settle_loop, dynamic=False)


# ============================================================
# Compiled LIF layer loop (spike_integration fast path)
# ============================================================


def _lif_layer_loop(
    I_syn: Tensor,
    step_size: float,
    threshold: float,
    n_steps: int,
) -> tuple[Tensor, Tensor]:
    """LIF membrane integration for one layer, whole loop as one graph.

    Bitwise-equal to the eager per-step collection (verified by the
    compiled-settle lock): membrane trajectory, per-step spike rasters
    stacked as ``[n_steps, batch, neurons]``.
    """
    v = torch.zeros_like(I_syn)
    rasters: list[Tensor] = []
    for _ in range(n_steps):
        v = v + step_size * (-v + I_syn)
        spikes = v > threshold
        rasters.append(spikes.float())
        v = torch.where(spikes, torch.zeros_like(v), v)
    return v, torch.stack(rasters)


_compiled_lif_layer = torch.compile(_lif_layer_loop, dynamic=False)


# ============================================================
# StateDynamics Protocol
# ============================================================


@runtime_checkable
class StateDynamics(Protocol):
    """How the network's activations evolve over time (the forward pass).

    Encapsulates the differential equation or iterative map governing state
    evolution: energy minimization (EqProp), predictive settling (PC), spike
    integration (LIF), or instantaneous pass (backprop/FF). The StateDynamics
    uses Geometry.route() and Substrate operators to evolve the state. It
    produces free and nudged states for CreditAssignment.

    Canonical contract (read this before writing ``settle``/``compute_energy``;
    consolidated from the ePC landing retro, TODO.md R2.1):

    Activation layout:
        Layered states are ``[input, hidden1, ..., hiddenN, output]`` — the
        input tensor is element 0 and the network output is element -1.
        Consumers: ``_state_energy_vector`` (output-energy reads element -1),
        ``SubstrateSettleKernel.step`` (alignment 1:1 with
        ``extract_layered_params`` transitions), and CreditAssignment's
        per-layer correlation walks.

    Phase loop and energy timing:
        ``settle`` runs the free phase when ``target is None`` and the nudged
        phase otherwise. ``compute_energy`` is called by the pipeline *after*
        settle returns, reading the settled state — never mid-settle.

    Autograd context:
        Settle runs under the caller's ``no_grad`` by default. Implementations
        needing internal differentiation (ePC error gradients, diffusion
        Langevin steps) open ``with torch.enable_grad():`` around the reverse
        sweep and detach before returning. Out-of-place tensor adds are the
        graph-safety idiom — do not use ``+=`` on state tensors.

    Input flattening:
        Implementations flatten non-2-D inputs themselves
        (``x.flatten(1) if x.dim() > 2``); geometry may hand over raw
        image-shaped inputs.

    Free/nudged target semantics:
        ``target is None`` → write the settled acts to ``free_state``;
        ``target`` provided → nudge toward it (``beta * (one_hot - out)`` at
        the output layer) and write to ``nudged_state``. Both phases also
        populate ``activations``. Metrics schema: imp-46.

    The mutation contract below is enforced by the caller census AST lock
    (``tests/property/test_settle_caller_census.py``).
    """

    config: StateDynamicsConfig

    @abstractmethod
    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
        on_step: Callable[[int, float], None] | None = None,
    ) -> CompositeState:
        """Settle the network to a fixed point (or run single pass).

        Args:
            state: Current system state (contains input x)
            geometry: Network topology for routing
            substrate: Physical substrate for operators/noise
            target: Optional target for nudged phase
            on_step: Optional callback invoked at each settle step with
                (step_index, current_energy). Used for live telemetry.

        Returns:
            Updated state with settled activations in state.activations

        Note:
            Canonical mutation contract (imp-27/imp-47): ``settle`` always
            returns the state to use — implementations may rebuild rather
            than mutate. Callers must bind and use the returned state;
            reading the input state after the call reads pre-settle
            activations.
        """
        ...

    @abstractmethod
    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        """Compute the energy of the current state.

        For energy-based dynamics (EqProp, Hopfield, PC), this is the
        Lyapunov function. For non-energy dynamics, returns a proxy.
        """
        ...


# ============================================================
# EnergyMinimizationDynamics: Full EqProp Implementation
# ============================================================


def _compute_hopfield_energy(all_acts: list[Tensor], geometry: Geometry) -> Tensor:  # ruff: ignore[complex-structure, too-many-branches, too-many-locals]
    """Compute Hopfield energy for the current state.

    E = 0.5 * sum(h_i^2) - sum_{i,j} W_{ij} h_i h_j - sum_i b_i h_i
    For ReLU networks with symmetric weights approximation.

    Tile meshes answer through their block-view energy when the acts carry
    the settled block layout.
    """
    tile_energy = getattr(geometry, "hopfield_energy", None)
    block_count = getattr(geometry, "block_act_count", None)
    if (
        callable(tile_energy)
        and block_count is not None
        and len(all_acts) == block_count
    ):
        return tile_energy(all_acts)

    if not all_acts or len(all_acts) < 2:
        return torch.tensor(0.0, device=all_acts[0].device if all_acts else "cpu")

    # Use hidden + output layers (skip input)
    acts = all_acts[1:]  # [hidden1, hidden2, ..., output]
    device = acts[0].device
    total_energy = torch.tensor(0.0, device=device)

    # Extract weight matrices from geometry params
    params = geometry.params
    weight_names = [
        n
        for n in params
        if "weight" in n and params[n].ndim == 2 and not n.startswith("recurrent")
    ]
    # Sort by layer index (e.g., "0.weight" -> 0, "2.weight" -> 2)
    weight_names.sort(
        key=lambda x: (
            int(x.split("_")[1]) if "_" in x and x.split("_")[1].isdigit() else 0
        )
    )

    if not weight_names:
        return torch.tensor(0.0, device=device)

    num_hidden = len(acts) - 1  # Number of hidden layers (excluding output)
    num_ff_weights = len(weight_names)  # Number of feedforward weight matrices

    # For each hidden/output layer, compute energy contribution
    # E = 0.5 * ||h||^2 - h^T * W * h_prev (for each layer)
    for i in range(len(acts)):
        h = acts[i]
        # 0.5 * ||h||^2
        total_energy = total_energy + 0.5 * (h**2).sum()

    # Subtract interaction terms: h^T * W * h_prev
    for i in range(len(acts)):
        h = acts[i]
        if i < num_hidden:
            # Hidden layer i: weight index i (0, 1, ..., num_hidden-1)
            weight_idx = i
            h_prev = acts[i - 1] if i > 0 else all_acts[0]
        else:
            # Output layer: last feedforward weight (hidden -> output)
            weight_idx = num_ff_weights - 1
            # For linear network (no hidden layers), h_prev should be input
            if num_hidden == 0:  # ruff: ignore[if-else-block-instead-of-if-exp]
                h_prev = all_acts[0]
            else:
                h_prev = acts[i - 1]  # Last hidden layer

        if weight_idx < num_ff_weights:
            W = params[weight_names[weight_idx]]
            # h^T * W * h_prev -> sum over batch, then mean
            # h: (batch, dim_i), W: (dim_i, dim_{i-1}), h_prev: (batch, dim_{i-1})
            # h @ W: (batch, dim_{i-1}) @ h_prev.T: (dim_{i-1}, batch) -> (batch, batch)
            if W.shape[0] != h.shape[-1] or W.shape[1] != h_prev.shape[-1]:
                continue  # ragged pairing (e.g. per-edge tile weights)
            interaction = (h @ W @ h_prev.T).trace()
            total_energy = total_energy - interaction

    # Subtract bias terms (exclude recurrent bias if any)
    bias_names = [
        n
        for n in params
        if "bias" in n and params[n].ndim == 1 and not n.startswith("recurrent")
    ]
    bias_names.sort(
        key=lambda x: (
            int(x.split("_")[1]) if "_" in x and x.split("_")[1].isdigit() else 0
        )
    )
    num_ff_biases = len(bias_names)
    for i in range(len(acts)):
        h = acts[i]
        if i < num_hidden:  # ruff: ignore[if-else-block-instead-of-if-exp]
            bias_idx = i
        else:
            bias_idx = num_ff_biases - 1
        if bias_idx < num_ff_biases:
            b = params[bias_names[bias_idx]]
            if b.shape[0] != h.shape[-1]:
                continue
            total_energy = total_energy - (h @ b).sum()

    # Return mean per sample
    batch_size = acts[0].size(0)
    return total_energy / batch_size


class _SettleTelemetry:
    """Records the horizon (steps actually used) of the most recent settle."""

    config: StateDynamicsConfig  # provided by every concrete dynamics class
    _settle_steps_used: int = 0

    def _note_settle_start(self) -> None:
        self._settle_steps_used = self.config.max_steps


class EnergyMinimizationDynamics(_SettleTelemetry):
    """Energy-based settling (Equilibrium Propagation, Hopfield, CHL).

    Supports heavy-ball momentum for accelerated convergence.
    Implements the contrastive nudged phase: output layer receives
    beta * (target - output) during the nudged phase.

    Gradient checkpointing trades compute for memory by recomputing
    intermediate activations during backward pass.

    Free energy tracking enables Control-Lyapunov analysis of the
    thermodynamic contrast between free and nudged phases.
    """

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.energy_minimization()
        self._velocity: list[Tensor] | None = None
        self._free_energy_history: list[float] | None = None

    def settle(  # ruff: ignore[complex-structure, too-many-branches, too-many-locals, too-many-statements]
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
        on_step: Callable[[int, float], None] | None = None,
    ) -> CompositeState:
        # Run settling iterations for full multi-layer EqProp dynamics
        # Implements the same dynamics as legacy EquilibriumMLP.forward_dynamics

        if state.x is None:
            return state

        # Tile meshes seed the relaxation from their block layout
        # ([x, z0..z_{L-1}, output]); layered geometries from their
        # forward intermediates. Both align 1:1 with the settle kernel's
        # extracted weight/bias transitions.
        block_builder = getattr(geometry, "settle_blocks", None)
        if callable(block_builder):
            all_acts = block_builder(state.x, substrate)
        else:
            all_acts = geometry.forward_with_intermediates(state.x, substrate)
        if not all_acts:
            return state

        # Extract layered params and construct substrate-native settle kernel
        params = extract_layered_params(geometry)
        if params is None:
            raise TypeError("Energy-based settling requires a layered geometry")
        kernel = SubstrateSettleKernel(
            substrate=substrate,
            params=params,
            step_size=self.config.step_size,
            momentum=self.config.momentum,
            residual=params.residual,
        )

        # Number of hidden layers (excluding input and output)
        # all_acts = [input, hidden1, hidden2, ..., output]  # ruff: ignore[commented-out-code]
        num_hidden = len(all_acts) - 2

        # Initialize velocity for momentum (per hidden layer)
        if self.config.momentum > 0:
            batch_size = all_acts[0].size(0)
            self._velocity = [
                torch.zeros_like(all_acts[i + 1]) for i in range(num_hidden)
            ]
        else:
            self._velocity = None

        # Initialize free energy history if tracking enabled
        if self.config.track_free_energy_per_iter:
            self._free_energy_history = []
            # Track initial energy
            self._free_energy_history.append(
                _compute_hopfield_energy(all_acts, geometry).item()
            )
        else:
            self._free_energy_history = None

        beta = self.config.beta if target is not None else 0.0

        # Auto-detect gradient checkpointing: never on CPU (pure overhead),
        # on GPU enable only if explicitly set OR if VRAM would be exceeded.
        device = all_acts[0].device
        use_checkpointing = self.config.gradient_checkpointing
        if use_checkpointing and device.type == "cpu":
            # Never checkpoint on CPU - it's pure compute overhead with no memory benefit
            use_checkpointing = False
        elif use_checkpointing is False and device.type == "cuda":
            # Auto-enable if model + activations would exceed ~80% of available VRAM
            try:  # ruff: ignore[too-many-statements-in-try-clause]
                free_vram, _ = torch.cuda.mem_get_info(device)
                # Estimate: params + optimizer state + activations (max_steps * layers * batch * hidden)
                total_params = sum(
                    p.numel() for p in geometry.params.values() if p.requires_grad
                )
                hidden_size = (
                    all_acts[1].numel() // all_acts[1].shape[0]
                )  # per-sample hidden dim
                batch_size = all_acts[0].shape[0]
                # Rough estimate: activations for all settle steps (each step has ~layers activations)
                est_activation_mem = (
                    self.config.max_steps
                    * (len(layer_stack(geometry) or ()))
                    * batch_size
                    * hidden_size
                    * 4  # fp32 bytes
                )
                est_total = (
                    total_params * 4 * 3
                ) + est_activation_mem  # params + optimizer + activations
                if est_total > free_vram * 0.8:
                    use_checkpointing = True
            except Exception:  # ruff: ignore[try-except-pass]
                pass  # Fall back to config value

        # Kernel step function for checkpointing
        def _kernel_step(
            acts: list[Tensor],
            beta_: float,
            target_: Tensor | None,
            velocity_: list[Tensor] | None,
        ) -> tuple[list[Tensor], list[Tensor] | None]:
            return kernel.step(acts, beta_, target_, velocity_)

        # Compiled fast path (R11.2.25): whole settle as one graph. Guards
        # keep it on the kernel's common case; runs a fixed step budget
        # (skips the eager convergence early-exit).
        use_compiled = (
            self.config.compiled
            and self.config.momentum == 0
            and params.recurrent_weight is None
            and not self.config.track_free_energy_per_iter
            and not use_checkpointing
            and type(substrate).__name__ == "DigitalSubstrate"
            and len(all_acts) == len(params.weights) + 1
        )
        if use_compiled:
            self._settle_steps_used = self.config.max_steps
            all_acts = list(
                _compiled_eqprop_settle(
                    cast("list[Tensor]", all_acts),
                    params.weights,
                    params.biases,
                    params.activations,
                    self.config.step_size,
                    beta,
                    target,
                    self.config.max_steps,
                    params.residual,
                )
            )
        elif use_checkpointing:
            from torch.utils import checkpoint

            self._note_settle_start()
            for _step in range(self.config.max_steps):  # ruff: ignore[used-dummy-variable]
                prev_output = all_acts[-1].detach()
                # Checkpoint the kernel step function
                all_acts, self._velocity = checkpoint.checkpoint(
                    _kernel_step,
                    all_acts,
                    beta,
                    target,
                    self._velocity,
                    use_reentrant=False,
                )

                # Track free energy if enabled
                if self._free_energy_history is not None:
                    energy_val = _compute_hopfield_energy(all_acts, geometry).item()
                    self._free_energy_history.append(energy_val)
                    if on_step is not None:
                        on_step(_step, energy_val)

                # Check convergence (can't checkpoint this as it's not differentiable)
                if _step >= self.config.convergence_start:
                    delta = torch.dist(all_acts[-1], prev_output, p=float("inf")).item()
                    if delta < self.config.convergence_threshold:
                        self._settle_steps_used = _step + 1
                        break
        else:
            # Non-checkpointed path
            self._note_settle_start()
            for step in range(self.config.max_steps):
                new_acts, new_velocity = kernel.step(
                    all_acts, beta, target, self._velocity
                )
                if new_velocity is not None:
                    self._velocity = new_velocity

                # Track free energy if enabled
                if self._free_energy_history is not None:
                    energy_val = _compute_hopfield_energy(new_acts, geometry).item()
                    self._free_energy_history.append(energy_val)
                    if on_step is not None:
                        on_step(step, energy_val)

                # Check convergence
                if step >= self.config.convergence_start:
                    delta = torch.dist(
                        new_acts[-1], all_acts[-1], p=float("inf")
                    ).item()
                    if delta < self.config.convergence_threshold:
                        all_acts = new_acts
                        self._settle_steps_used = step + 1
                        break
                all_acts = new_acts

        if target is None:
            state.free_state = all_acts
        else:
            state.nudged_state = all_acts
        state.activations = all_acts
        return state

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        """Compute free energy (Hopfield energy) for the current state."""
        acts = state.free_state
        if acts is None:
            acts = state.nudged_state
        if acts is None:
            acts = state.activations
        if acts is None:
            return torch.tensor(0.0)
        if isinstance(acts, list):
            # Use hidden + output layers
            energy_val = _compute_hopfield_energy(acts, geometry)
            return energy_val
        return (acts**2).mean()

    def get_free_energy_history(self) -> list[float] | None:
        """Return the free energy history tracked during settling.

        Returns None if tracking was not enabled (track_free_energy_per_iter=False).
        """
        return self._free_energy_history


# ============================================================
# Other Default/Reference StateDynamics Implementations
# ============================================================


class PredictiveSettlingDynamics(_SettleTelemetry):
    """Predictive coding settling (Rao & Ballard, Whittington & Bogacz).

    Minimizes prediction error via iterative inference.
    """

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.predictive_settling()

    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
        on_step: Callable[[int, float], None] | None = None,
    ) -> CompositeState:
        # Predictive coding settling: minimize prediction error
        x = _get_state_x(state)
        if x is None:
            raise ValueError("State must contain input 'x'")

        # Initialize free energy history if tracking enabled
        if self.config.track_free_energy_per_iter:
            self._free_energy_history: list[float] | None = []
        else:
            self._free_energy_history = None

        # Tile meshes settle through the block-view relaxation kernel —
        # target-responsive (the nudged phase pulls the output toward the
        # target with the configured beta); R11.1.4.
        self._note_settle_start()
        if hasattr(geometry, "_graph"):
            return self._settle_tile(state, x, geometry, substrate, target, on_step)

        # For layered geometries (feedforward, recurrent with layered params),
        # settle layer-wise to produce per-layer activations for credit assignment.
        layered = extract_layered_params(geometry)
        if layered is not None and len(layered.weights) > 0:
            return self._settle_layered(
                state, x, geometry, layered, substrate, target, on_step
            )

        # Fallback: standard predictive coding settling for recurrent geometries
        # (single state vector, no per-layer structure)
        h = substrate.initial_state(x)
        op = substrate.get_forward_operator()

        for step in range(self.config.max_steps):
            # Predictive coding update
            prediction = geometry.route(h)
            # Ensure prediction matches input dimension for shape-safe error computation
            if prediction.shape[-1] != h.shape[-1]:
                if prediction.shape[-1] >= h.shape[-1]:
                    prediction = prediction[..., : h.shape[-1]]
                else:
                    pad_size = h.shape[-1] - prediction.shape[-1]
                    prediction = torch.nn.functional.pad(prediction, (0, pad_size)).to(
                        prediction.device
                    )
            error = x - prediction
            h = h + self.config.step_size * op(
                error,
                geometry.params.get("weight", torch.eye(h.shape[-1], device=h.device)),
            )
            # Track free energy per iteration
            if self.config.track_free_energy_per_iter and (
                self._free_energy_history is not None
            ):
                fe = error.pow(2).sum().item()
                self._free_energy_history.append(fe)
                if on_step is not None:
                    on_step(step, fe)

        new_state = _create_output_state(
            state,
            x=x,
            output=h,
            free_state=[h] if target is None else None,
            nudged_state=[h] if target is not None else None,
            activations=[h],
        )

        return new_state

    def _settle_layered(
        self,
        state: CompositeState,
        x: Tensor,
        geometry: Geometry,
        layered: LayeredParams,
        substrate: Substrate,
        target: Tensor | None,
        on_step: Callable[[int, float], None] | None = None,
    ) -> CompositeState:
        """Layer-wise predictive coding settle over the geometry's Linear transitions.

        Each layer minimizes its prediction error against the layer below.
        The input layer is clamped to x; each subsequent layer predicts the
        previous layer's activity. Returns activations for all layers.
        """
        op = substrate.get_forward_operator()

        # Initialize layer states from a feedforward pass
        # This gives us the correct shapes for each layer
        init_acts = (
            geometry.forward_with_intermediates(x, substrate)
            if hasattr(geometry, "forward_with_intermediates")
            else None
        )
        if init_acts is not None and len(init_acts) == len(layered.weights) + 1:
            # Use feedforward activations as initial states
            acts = list(init_acts)  # [input, hidden1, hidden2, ..., output]
        else:
            # Fallback: initialize with zeros of correct shape
            h = substrate.initial_state(x)
            h = h.flatten(1) if h.dim() > 2 else h
            acts = [h]
            for weight, bias in zip(layered.weights, layered.biases, strict=True):
                out_shape = (h.shape[0], weight.shape[0])
                h = torch.zeros(out_shape, device=h.device, dtype=h.dtype)
                acts.append(h)

        # Track free energy per iteration across all layers
        layer_free_energy: list[float] = (
            [] if self.config.track_free_energy_per_iter else None
        )

        use_compiled = (
            self.config.compiled
            and layered.recurrent_weight is None
            and not self.config.track_free_energy_per_iter
            and type(substrate).__name__ == "DigitalSubstrate"
        )
        if use_compiled:
            acts = _compiled_layered_settle(
                acts,
                layered.weights,
                self.config.step_size,
                self.config.max_steps,
            )
            acts = list(acts)
        else:
            acts = self._eager_layered_steps(
                acts, layered, op, layer_free_energy, on_step
            )

        if target is not None:
            # Nudge the output layer toward the target
            acts[-1] = acts[-1] + self.config.beta * (
                _one_hot(target, acts[-1]) - acts[-1]
            )

        if self.config.track_free_energy_per_iter and layer_free_energy is not None:
            self._free_energy_history = layer_free_energy

        return _create_output_state(
            state,
            x=x,
            output=acts[-1],
            free_state=acts if target is None else None,
            nudged_state=acts if target is not None else None,
            activations=acts,
        )

    def _eager_layered_steps(
        self,
        acts: list[Tensor],
        layered: LayeredParams,
        op: object,
        layer_free_energy: list[float] | None,
        on_step: Callable[[int, float], None] | None = None,
    ) -> list[Tensor]:
        """Eager settle loop: top-down prediction, bottom-up error correction.

        All layers settle simultaneously for ``max_steps`` iterations; the
        substrate operator and recurrent weights keep this path general
        (any substrate, per-iteration energy tracking).
        """
        for step in range(self.config.max_steps):
            new_acts = [acts[0]]  # Input layer is clamped
            step_energy = 0.0

            for i, (weight, bias) in enumerate(
                zip(layered.weights, layered.biases, strict=True)
            ):
                # acts[i+1] is current state of layer i+1; weight maps from
                # layer i to layer i+1. Top-down prediction uses the weight
                # transpose (no bias in top-down).
                h_upper = acts[i + 1]
                prediction = op(h_upper, weight.T)  # type: ignore[operator]
                error = acts[i] - prediction
                h_upper_new = h_upper + self.config.step_size * op(error, weight)  # type: ignore[operator]
                new_acts.append(h_upper_new)

                if (
                    self.config.track_free_energy_per_iter
                    and layer_free_energy is not None
                ):
                    fe = error.pow(2).sum().item()
                    layer_free_energy.append(fe)
                    step_energy += fe

            # Recurrent connection on the last hidden layer (RecurrentGeometry)
            if layered.recurrent_weight is not None and len(new_acts) >= 3:
                hidden_idx = len(new_acts) - 2
                h_hidden = new_acts[hidden_idx]
                new_acts[hidden_idx] = h_hidden + self.config.step_size * op(
                    h_hidden, layered.recurrent_weight
                )  # type: ignore[operator]

            if on_step is not None:
                on_step(step, step_energy)
            acts = new_acts
        return acts

    def _settle_tile(
        self,
        state: CompositeState,
        x: Tensor,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None,
        on_step: Callable[[int, float], None] | None = None,
    ) -> CompositeState:
        """Block-view relaxation over the tile mesh via the settle kernel."""
        kernel = SubstrateSettleKernel(
            substrate=substrate,
            params=self._tile_layered_params(geometry),
            step_size=self.config.step_size,
            momentum=self.config.momentum,
        )
        beta = self.config.beta if target is not None else 0.0
        all_acts = self._tile_block_acts(geometry, x, substrate)

        for step in range(self.config.max_steps):
            new_acts, _ = kernel.step(all_acts, beta, target, None)
            if self.config.track_free_energy_per_iter and (
                self._free_energy_history is not None
            ):
                # Free energy in predictive coding = squared prediction errors
                fe = 0.0
                for i, (w, b) in enumerate(
                    zip(kernel.params.weights, kernel.params.biases, strict=True)
                ):
                    pred = new_acts[i] @ w.T
                    if b is not None:
                        pred = pred + b
                    fe += (new_acts[i + 1] - pred).pow(2).sum().item()
                self._free_energy_history.append(fe)
                if on_step is not None:
                    on_step(step, fe)
            if step >= self.config.convergence_start:
                delta = torch.dist(new_acts[-1], all_acts[-1], p=float("inf")).item()
                if delta < self.config.convergence_threshold:
                    all_acts = new_acts
                    self._settle_steps_used = step + 1
                    break
            all_acts = new_acts

        return _create_output_state(
            state,
            x=x,
            output=all_acts[-1],
            free_state=all_acts if target is None else None,
            nudged_state=all_acts if target is not None else None,
            activations=all_acts,
        )

    def _tile_layered_params(self, geometry: Geometry):
        layered = extract_layered_params(geometry)
        if layered is None:
            raise TypeError("Tile settling requires the mesh's block view")
        return layered

    def _tile_block_acts(
        self, geometry: Geometry, x: Tensor, substrate: Substrate
    ) -> list[Tensor]:
        builder = getattr(geometry, "settle_blocks", None)
        if not callable(builder):
            raise TypeError("Tile settling requires settle_blocks")
        return builder(x, substrate)

    def get_free_energy_history(self) -> list[float] | None:
        """Return the free energy history tracked during settling.

        Returns None if tracking was not enabled (track_free_energy_per_iter=False).
        """
        return self._free_energy_history

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        return _energy_tensor(_state_energy_vector(state)).pow(2).sum()


class ErrorPredictiveCodingDynamics(_SettleTelemetry):
    """Error-parameterized predictive coding (ePC) — Goemaere et al., "ePC: Fast
    and Deep Predictive Coding in Digital Simulation", arXiv:2505.20137 (ICML 2026).

    sPC's state dynamics attenuate the output-loss signal exponentially with depth
    (each layer traversal compounds a λ<1 attenuation), stalling deep networks.
    ePC reparameterizes the dynamics in terms of prediction errors εᵢ: the state
    at layer i is sᵢ = ŝᵢ + εᵢ with ŝᵢ = f_θᵢ(sᵢ₋₁), so the predicted output is a
    function of every error directly. Reverse-mode AD carries the output-loss
    gradient to all errors simultaneously — unattenuated — reaching the same PC
    equilibrium as sPC in a handful of steps instead of hundreds. Weight updates
    remain the same PC rule (Eq. 3): Δθᵢ ∝ (∂ŝᵢ/∂θᵢ)ᵀ εᵢ.

    Not biologically local (a digital-simulation device): trading locality for
    propagation reach is exactly the ePC trade-off — see the paper's §4.2.
    """

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.error_predictive_coding()
        self._last_errors: list[Tensor] | None = None

    def _build_forward_with_errors(
        self,
        x: Tensor,
        transitions: tuple[
            tuple[Tensor, Tensor | None, tuple[torch.nn.Module, ...]], ...
        ],
        substrate: Substrate,
        eps: list[Tensor],
        residual: bool = False,
    ) -> tuple[list[Tensor], Tensor]:
        """Feedforward pass with error perturbations: sᵢ = ŝᵢ + εᵢ.

        With ``residual`` (``GeometryConfig.residual``), a transition whose
        output width matches its input width adds its input activity back —
        ``a_ℓ = a_{ℓ−1} + φ(W_ℓ a_{ℓ−1} + b_ℓ)``, mirroring
        ``FeedforwardGeometry._apply_stack``; the skip is part of the
        prediction ŝᵢ, so εᵢ rides on top of it.

        Returns (states, ŷ) where states = [x, s₀, ..., s_{L-2}, ŷ]; hidden
        states carry their error, the output carries none (Algorithm 2).
        """
        op = substrate.get_forward_operator()
        h = x.flatten(1) if x.dim() > 2 else x
        states = [h]
        last = len(transitions) - 1
        for i, (weight, bias, activations) in enumerate(transitions):
            h_in = h
            h = op(h, weight)
            if bias is not None:
                h = h + bias
            for activation in activations:
                h = activation(h)
            if residual and h.shape == h_in.shape:
                h = h + h_in
            if i < last:
                if i < len(eps):
                    h = h + eps[i]
                states.append(h)
        states.append(h)
        return states, h

    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
    ) -> CompositeState:
        x = _get_state_x(state)
        if x is None:
            raise ValueError("State must contain input 'x'")

        layered = extract_layered_params(geometry)
        if layered is None or not layered.transitions:
            raise TypeError("ePC settling requires a layer-structured geometry")
        transitions = layered.transitions

        xf = x.flatten(1) if x.dim() > 2 else x
        with torch.no_grad():
            probe_states, _ = self._build_forward_with_errors(
                xf, transitions, substrate, [], residual=layered.residual
            )
        eps = [
            torch.zeros(s.shape, device=s.device, dtype=s.dtype).requires_grad_(True)
            for s in probe_states[1:-1]
        ]

        self._note_settle_start()
        for step in range(self.config.max_steps):
            with torch.enable_grad():
                states, y_hat = self._build_forward_with_errors(
                    xf, transitions, substrate, eps, residual=layered.residual
                )
                # PC energy (Algorithm 2): ½ Σ ‖εᵢ‖² + β·ℒ(ŷ, y)
                energy = torch.zeros((), device=xf.device, dtype=xf.dtype)
                for e in eps:
                    energy = energy + 0.5 * e.pow(2).sum()
                if target is not None:
                    energy = (
                        energy
                        + self.config.beta
                        * torch.nn.functional.cross_entropy(y_hat, target)
                    )
                # ∇εⱼE = εⱼ + (∂ŷ/∂εⱼ)ᵀ ∇ŷℒ — one reverse-mode sweep, unattenuated
                grads = torch.autograd.grad(energy, eps, allow_unused=True)

            new_eps = [
                e
                - self.config.step_size * (g if g is not None else torch.zeros_like(e))
                for e, g in zip(eps, grads, strict=True)
            ]
            with torch.no_grad():
                delta = max(
                    (new - old).abs().max().item()
                    for new, old in zip(new_eps, eps, strict=True)
                )
            eps = [e.detach().requires_grad_(True) for e in new_eps]

            if (
                step >= self.config.convergence_start
                and delta < self.config.convergence_threshold
            ):
                self._settle_steps_used = step + 1
                break

        states, _ = self._build_forward_with_errors(
            xf, transitions, substrate, eps, residual=layered.residual
        )
        states = _apply_gain_control(states, self.config.gain_control)
        self._last_errors = eps

        if target is None:
            state.free_state = states
        else:
            state.nudged_state = states
        state.activations = states
        return state

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        """PC energy of the last settle: ½ Σ ‖εᵢ‖²."""
        if self._last_errors is None:
            return torch.tensor(0.0)
        energy = torch.zeros((), device=self._last_errors[0].device)
        for e in self._last_errors:
            energy = energy + 0.5 * e.pow(2).sum()
        return energy


class PCALMDynamics(_SettleTelemetry):
    """Augmented Lagrangian Predictive Coding (PC-ALM; Seely & Gould 2026,
    arXiv:2605.31022).

    Layer-local primal–dual dynamics replacing global backprop. Each layer
    maintains:
    - Primal states `h_l` (activations)
    - Dual states `λ_l` (Lagrange multipliers / PI controller state)

    The augmented Lagrangian for layer `l`:
        L_ρ = Σₗ [ ½‖hₗ − f_θₗ(hₗ₋₁)‖² ]
              + Σₗ ⟨λₗ, hₗ − f_θₗ(hₗ₋₁)⟩
              + (ρ/2) Σₗ ‖hₗ − f_θₗ(hₗ₋₁)‖²

    Dynamics (discretized continuous time):
        cₗ = hₗ − f_θₗ(hₗ₋₁)                  # constraint violation
        λₗ ← λₗ + step_size · cₗ                # dual update (PI controller)
        hₗ ← hₗ − step_size · [cₗ + λₗ + ρ·cₗ
              − Jₗ₊₁ᵀ·(cₗ₊₁ + λₗ₊₁ + ρ·cₗ₊₁)]  # primal update

    Weight update (local Hebbian, computed by PCALMCredit):
        ΔWₗ ∝ −λₗ hₗ₋₁ᵀ

    The `prospective_leak` parameter interpolates between pure PC-ALM
    (α=0, integral-only PI controller) and prospective configuration
    (α→1, proportional component). With α>0:
        λₗ ← λₗ + step_size · (cₗ + α·λₗ)
    """

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.pc_alm()
        self._dual_vars: list[Tensor] | None = None
        self._free_energy_history: list[float] | None = None
        self._rho_override: float | None = None
        self._train_step: int = 0

    def set_rho_override(self, rho: float | None) -> None:
        """Override rho for the next settle (e.g., for scheduling)."""
        self._rho_override = rho

    def increment_train_step(self) -> None:
        """Increment the training step counter (for rho scheduling)."""
        self._train_step += 1

    def _get_current_rho(self) -> float:
        """Get the current rho value, considering override and schedule."""
        if self._rho_override is not None:
            rho = self._rho_override
            self._rho_override = None  # Clear after use
            return rho

        # Apply schedule if configured
        if self.config.rho_schedule == "constant":
            return self.config.rho
        elif self.config.rho_schedule == "linear":
            # Linear increase from rho to rho_final over training
            # Assume max_train_steps ~ 10000; scale appropriately
            max_steps = getattr(self, "_max_train_steps", 10000)
            progress = min(self._train_step / max_steps, 1.0)
            return self.config.rho + progress * (
                self.config.rho_final - self.config.rho
            )
        elif self.config.rho_schedule == "cosine":
            # Cosine annealing from rho to rho_final
            max_steps = getattr(self, "_max_train_steps", 10000)
            progress = min(self._train_step / max_steps, 1.0)
            return self.config.rho_final + (
                self.config.rho - self.config.rho_final
            ) * 0.5 * (1 + math.cos(math.pi * progress))
        return self.config.rho

    def set_max_train_steps(self, max_steps: int) -> None:
        """Set the maximum training steps for scheduling."""
        self._max_train_steps = max_steps

    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
        on_step: Callable[[int, float], None] | None = None,
    ) -> CompositeState:
        x = _get_state_x(state)
        if x is None:
            raise ValueError("State must contain input 'x'")

        # Initialize free energy history if tracking enabled
        if self.config.track_free_energy_per_iter:
            self._free_energy_history = []
        else:
            self._free_energy_history = None

        # Extract layered parameters
        layered = extract_layered_params(geometry)
        if layered is None or not layered.weights:
            raise TypeError("PC-ALM dynamics requires a layer-structured geometry")

        op = substrate.get_forward_operator()

        # Initialize layer states from a feedforward pass
        init_acts = geometry.forward_with_intermediates(x, substrate)
        if init_acts is not None and len(init_acts) == len(layered.weights) + 1:
            acts = list(init_acts)  # [input, hidden1, hidden2, ..., output]
        else:
            raise TypeError("PC-ALM requires valid feedforward intermediates")

        # Number of layers (excluding input)
        num_layers = len(acts) - 1
        batch_size = acts[0].shape[0]

        # Initialize dual variables λ to zero (or warm-start from previous step)
        if (
            self.config.warm_start_duals
            and self._dual_vars is not None
            and len(self._dual_vars) == num_layers
        ):
            dual_vars = self._dual_vars
        else:
            dual_vars = [torch.zeros_like(acts[i + 1]) for i in range(num_layers)]

        # Get current rho (with scheduling/override)
        current_rho = self._get_current_rho()

        # Track initial augmented Lagrangian
        if self._free_energy_history is not None:
            self._free_energy_history.append(
                self._compute_augmented_lagrangian(
                    acts, dual_vars, layered, op, current_rho
                ).item()
            )

        # Primal–dual relaxation loop
        self._note_settle_start()
        use_compiled = (
            self.config.compiled
            and layered.recurrent_weight is None
            and not layered.residual
            and not self.config.track_free_energy_per_iter
            and not self.config.gradient_checkpointing
            and type(substrate).__name__ == "DigitalSubstrate"
            and len(acts) == len(layered.weights) + 1
        )
        if use_compiled:
            from computronium.acceleration.pcalm_kernels import _compiled_pcalm_settle

            beta = self.config.beta if target is not None else 0.0
            acts, dual_vars = _compiled_pcalm_settle(
                list(acts),
                list(dual_vars),
                layered.weights,
                layered.biases,
                layered.activations,
                self.config.step_size,
                current_rho,
                self.config.prospective_leak,
                beta,
                target,
                self.config.max_steps,
            )
            self._settle_steps_used = self.config.max_steps
        else:
            acts = self._eager_relaxation(
                acts, dual_vars, layered, op, target, current_rho
            )

        # Store dual variables for credit assignment
        self._dual_vars = dual_vars

        # Write dual_vars to state for PCALMCredit to read
        # Use the dedicated dual_vars field (nudged phase) and metrics for backward compat
        dual_vars_for_state = [lam.detach() for lam in dual_vars]

        if target is None:
            state.free_state = acts
            state.metrics = state.metrics or {}
            state.metrics["dual_vars_free"] = dual_vars_for_state
        else:
            state.nudged_state = acts
            # Nudged phase duals are the ones used for credit assignment
            state.dual_vars = dual_vars_for_state
            state.metrics = state.metrics or {}
            state.metrics["dual_vars"] = dual_vars_for_state
            state.metrics["dual_vars_nudged"] = dual_vars_for_state
        state.activations = acts

        return state

    def _eager_relaxation(
        self,
        acts: list[Tensor],
        dual_vars: list[Tensor],
        layered: LayeredParams,
        op: object,
        target: Tensor | None,
        rho: float | None = None,
    ) -> list[Tensor]:
        """Eager primal-dual loop: per-iteration energy tracking + early exit."""
        num_layers = len(layered.weights)
        current_rho = rho if rho is not None else self.config.rho
        alpha = self.config.prospective_leak
        step_size = self.config.step_size

        # Gradient checkpointing: checkpoint every k steps
        use_checkpointing = self.config.gradient_checkpointing
        if use_checkpointing:
            checkpoint_every = max(1, self.config.max_steps // 4)
        else:
            checkpoint_every = 0

        def _relaxation_step(acts_step, dual_vars_step, step_idx):
            """Single relaxation step for checkpointing."""
            # Compute constraint violations c_l = h_l - f_θ_l(h_{l-1})
            constraints = []
            for i in range(num_layers):
                # f_θ_l(h_{l-1}) = activation(W_l @ h_{l-1} + b_l)
                pre = acts_step[i]
                weight = layered.weights[i]
                bias = layered.biases[i]
                activation = (
                    layered.activations[i]
                    if i < len(layered.activations)
                    else nn.Identity()
                )

                predicted = op(pre, weight)
                if bias is not None:
                    predicted = predicted + bias
                predicted = activation(predicted)

                if layered.residual and i > 0 and acts_step[i].shape == predicted.shape:
                    predicted = predicted + acts_step[i]

                c = acts_step[i + 1] - predicted
                constraints.append(c)

            # Dual update: λ_l ← λ_l + step_size * (c_l + alpha * λ_l)
            # alpha=0 -> pure integral (PC-ALM); alpha>0 -> leaky integral (prospective config)
            for i in range(num_layers):
                dual_vars_step[i] = dual_vars_step[i] + step_size * (
                    constraints[i] + alpha * dual_vars_step[i]
                )

            # Primal update: h_l ← h_l - step_size * (c_l + λ_l + ρ*c_l - J_{l+1}^T * (c_{l+1} + λ_{l+1} + ρ*c_{l+1}))
            new_acts = [acts_step[0]]  # input layer clamped
            for i in range(num_layers):
                # Bottom-up: c_{i+1} + λ_{i+1} + ρ*c_{i+1}
                primal_grad = (
                    constraints[i] + dual_vars_step[i] + current_rho * constraints[i]
                )

                # Top-down coupling: J_{i+2}^T * (c_{i+2} + λ_{i+2} + ρ*c_{i+2})
                # Only for hidden layers (not output layer)
                if i < num_layers - 1:
                    # Error signal from layer i+2: v = c_{i+2} + λ_{i+2} + ρ*c_{i+2}
                    v = (
                        constraints[i + 1]
                        + dual_vars_step[i + 1]
                        + current_rho * constraints[i + 1]
                    )
                    # Jacobian J_{i+2} = diag(act'(z_{i+2})) @ W_{i+2}
                    # where z_{i+2} = h_{i+1} @ W_{i+2}^T + b_{i+2}
                    # h_{i+1} = acts_step[i+1], W_{i+2} = layered.weights[i+1]
                    pre = acts_step[i + 1]
                    weight = layered.weights[i + 1]
                    bias = layered.biases[i + 1]
                    z = op(pre, weight)
                    if bias is not None:
                        z = z + bias
                    act_derivative = (z > 0).to(v.dtype)  # ReLU derivative
                    # J_{i+2}^T @ v = W_{i+2}^T @ (act'(z_{i+2}) * v)
                    top_down = op(v * act_derivative, weight.T)
                else:
                    # Output layer: no top-down coupling
                    top_down = torch.zeros_like(acts_step[i + 1])

                total_grad = primal_grad - top_down
                h_new = acts_step[i + 1] - step_size * total_grad
                new_acts.append(h_new)

            # Nudge output layer in nudged phase
            if target is not None:
                beta = self.config.beta
                target_one_hot = _one_hot(target, new_acts[-1])
                new_acts[-1] = new_acts[-1] + beta * (target_one_hot - new_acts[-1])

            return new_acts, dual_vars_step, constraints

        if use_checkpointing:
            from torch.utils import checkpoint

            for step in range(self.config.max_steps):
                if step % checkpoint_every == 0 and step > 0:
                    acts, dual_vars, constraints = checkpoint.checkpoint(
                        _relaxation_step, acts, dual_vars, step, use_reentrant=False
                    )
                else:
                    acts, dual_vars, constraints = _relaxation_step(
                        acts, dual_vars, step
                    )

                # Track augmented Lagrangian per iteration
                if self._free_energy_history is not None:
                    self._free_energy_history.append(
                        self._compute_augmented_lagrangian(
                            acts, dual_vars, layered, op, current_rho
                        ).item()
                    )

                # Check convergence on constraint violation norm
                if step >= self.config.convergence_start:
                    constraint_norm = max(c.abs().max().item() for c in constraints)
                    if constraint_norm < self.config.convergence_threshold:
                        self._settle_steps_used = step + 1
                        return acts
        else:
            for step in range(self.config.max_steps):
                acts, dual_vars, constraints = _relaxation_step(acts, dual_vars, step)

                # Track augmented Lagrangian per iteration
                if self._free_energy_history is not None:
                    self._free_energy_history.append(
                        self._compute_augmented_lagrangian(
                            acts, dual_vars, layered, op, current_rho
                        ).item()
                    )

                # Check convergence on constraint violation norm
                if step >= self.config.convergence_start:
                    constraint_norm = max(c.abs().max().item() for c in constraints)
                    if constraint_norm < self.config.convergence_threshold:
                        self._settle_steps_used = step + 1
                        return acts
        return acts

    def _compute_augmented_lagrangian(
        self,
        acts: list[Tensor],
        dual_vars: list[Tensor],
        layered: LayeredParams,
        op: object,
        rho: float | None = None,
    ) -> Tensor:
        """Compute the augmented Lagrangian L_ρ at the current state."""
        num_layers = len(acts) - 1
        batch_size = acts[0].shape[0]
        current_rho = rho if rho is not None else self.config.rho

        total = torch.zeros((), device=acts[0].device, dtype=acts[0].dtype)

        for i in range(num_layers):
            pre = acts[i]
            weight = layered.weights[i]
            bias = layered.biases[i]
            activation = (
                layered.activations[i]
                if i < len(layered.activations)
                else nn.Identity()
            )

            predicted = op(pre, weight)
            if bias is not None:
                predicted = predicted + bias
            predicted = activation(predicted)

            if layered.residual and i > 0 and acts[i].shape == predicted.shape:
                predicted = predicted + acts[i]

            c = acts[i + 1] - predicted

            # ½‖c‖² + ⟨λ, c⟩ + (ρ/2)‖c‖² = ½(1+ρ)‖c‖² + ⟨λ, c⟩
            constraint_norm_sq = (c**2).sum()
            dual_term = (dual_vars[i] * c).sum()

            total = total + 0.5 * (1 + rho) * constraint_norm_sq + dual_term

        return total / batch_size

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        """Compute the augmented Lagrangian energy at the settled state."""
        acts = state.free_state if state.free_state is not None else state.activations
        if acts is None:
            return torch.tensor(0.0)
        if isinstance(acts, Tensor):
            acts = [acts]

        layered = extract_layered_params(geometry)
        if layered is None:
            return torch.tensor(0.0)

        op = (
            geometry.substrate.get_forward_operator()
            if hasattr(geometry, "substrate")
            else None
        )
        if op is None:
            from computronium.ontology.substrate import DigitalSubstrate

            op = DigitalSubstrate().get_forward_operator()

        # Need dual_vars from state metrics or internal buffer
        dual_vars = state.metrics.get("dual_vars") if state.metrics else None
        if dual_vars is None and self._dual_vars is not None:
            dual_vars = self._dual_vars

        if dual_vars is None:
            # Fallback: zero duals
            dual_vars = [torch.zeros_like(acts[i + 1]) for i in range(len(acts) - 1)]

        # Get current rho (with scheduling)
        current_rho = self._get_current_rho()
        return self._compute_augmented_lagrangian(
            acts, dual_vars, layered, op, current_rho
        )

    def get_free_energy_history(self) -> list[float] | None:
        """Return the augmented Lagrangian history tracked during settling."""
        return self._free_energy_history


class SpikeIntegrationDynamics(_SettleTelemetry):
    """Spiking neuron integration (LIF, AdEx).

    Layer-structured geometries settle layer-wise: each Linear transition
    integrates a constant input current (through the substrate's forward
    operator) into LIF membranes for ``max_steps`` steps — spike at
    threshold, reset — and the settled membrane carries activity to the
    next layer. Dim-preserving geometries (recurrent attractors) keep the
    single-membrane loop routed through ``Geometry.route``.
    """

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.spike_integration()

    @property
    def _spike_threshold(self) -> float:
        return getattr(self.config, "threshold", 1.0)

    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
    ) -> CompositeState:
        x = _get_state_x(state)
        if x is None:
            raise ValueError("State must contain input 'x'")

        self._note_settle_start()
        layered = extract_layered_params(geometry)
        if layered is not None and layered.recurrent_weight is None:
            # Tile meshes consume the target in the nudged phase via the
            # output clamp (R11.1.4); layered LIF stays target-free (imp-29).
            nudge_beta = (
                self.config.beta
                if target is not None and hasattr(geometry, "settle_blocks")
                else None
            )
            return self._settle_layered(
                state, x, layered, substrate, target, nudge_beta=nudge_beta
            )

        h = substrate.initial_state(x)

        spike_counts: list[Tensor] = []
        spike_rasters: list[Tensor] = []
        threshold = self._spike_threshold

        for _step in range(self.config.max_steps):
            # LIF dynamics: tau * dh/dt = -h + I_syn
            I_syn = geometry.route(h)
            h = h + self.config.step_size * (-h + I_syn)
            # Count spikes: neurons where membrane potential crosses threshold
            spikes = (h > threshold).float()
            spike_counts.append(spikes.sum(dim=1))  # [batch]
            spike_rasters.append(spikes)  # [batch, neurons] per step
            # Reset spiking neurons
            h = torch.where(h > threshold, torch.zeros_like(h), h)

        new_state = _create_output_state(
            state,
            x=x,
            output=h,
            free_state=[h] if target is None else None,
            nudged_state=[h] if target is not None else None,
            activations=[h],
            spike_counts=spike_counts,
            spike_rasters=[spike_rasters],  # Single layer: wrap in list
        )

        return new_state

    def _settle_layered(
        self,
        state: CompositeState,
        x: Tensor,
        layered: LayeredParams,
        substrate: Substrate,
        target: Tensor | None,
        *,
        nudge_beta: float | None = None,
    ) -> CompositeState:
        """Layer-wise LIF settle over the geometry's Linear transitions.

        Drive is fixed within a layer (the previous layer's settled
        membrane), so the substrate operator runs once per layer;
        membranes integrate ``max_steps`` LIF steps against it and the
        post-reset membrane carries activity to the next layer. Bounded
        membranes and per-(layer, step) spike counts are the settle's own
        observables.
        """
        op = substrate.get_forward_operator()
        h = substrate.initial_state(x)
        h = h.flatten(1) if h.dim() > 2 else h

        layer_params = list(zip(layered.weights, layered.biases, strict=True))
        # Compiled fast path (R11.2.25 recipe): whole LIF loop per layer as
        # one graph; fixed step budget, digital arithmetic inlined. Guard
        # keeps it on the eager path's common case (biases present, no
        # tile-mesh nudged-phase clamp).
        use_compiled = (
            self.config.compiled
            and nudge_beta is None
            and type(substrate).__name__ == "DigitalSubstrate"
            and all(b is not None for _, b in layer_params)
        )

        acts = [h]
        spike_counts: list[Tensor] = []
        spike_rasters: list[list[Tensor]] = []  # [layer][step] = [batch, neurons]
        threshold = self._spike_threshold

        for weight, bias in layer_params:
            if use_compiled:
                assert bias is not None  # guarded: compiled requires biases  # ruff: ignore[assert]
                I_syn = h @ weight.T + bias
                h, rasters = _compiled_lif_layer(
                    I_syn, self.config.step_size, threshold, self.config.max_steps
                )
                spike_counts.extend(r.sum(dim=1) for r in rasters.unbind(0))
                spike_rasters.append(list(rasters.unbind(0)))
            else:
                I_syn = op(h, weight)
                if bias is not None:
                    I_syn = I_syn + bias
                v = torch.zeros_like(I_syn)
                layer_rasters: list[Tensor] = []
                for _step in range(self.config.max_steps):
                    v = v + self.config.step_size * (-v + I_syn)
                    spikes = v > threshold
                    spike_counts.append(spikes.float().sum(dim=1))
                    layer_rasters.append(spikes.float())  # [batch, neurons]
                    v = torch.where(spikes, torch.zeros_like(v), v)
                spike_rasters.append(layer_rasters)
                h = v
            acts.append(h)

        if nudge_beta is not None and target is not None:
            h += nudge_beta * (_one_hot(target, h) - h)
            acts[-1] = h

        return _create_output_state(
            state,
            x=x,
            output=h,
            free_state=acts if target is None else None,
            nudged_state=acts if target is not None else None,
            activations=acts,
            spike_counts=spike_counts,
            spike_rasters=spike_rasters,
        )

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        return _energy_tensor(_state_energy_vector(state)).pow(2).sum()


class InstantaneousDynamics(_SettleTelemetry):
    """Single-pass feedforward (Backprop, Forward-Forward)."""

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.instantaneous()

    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
    ) -> CompositeState:
        # Single forward pass - no settling. Tile meshes route through the
        # block layout and consume the target in the nudged phase via the
        # output clamp (R11.1.4). For standard geometries, nudge the output
        # layer toward the target when provided.
        self._settle_steps_used = 1
        if state.x is not None:
            block_builder = getattr(geometry, "settle_blocks", None)
            if callable(block_builder):
                acts = block_builder(state.x, substrate)
                if target is not None:
                    acts = [
                        *acts[:-1],
                        acts[-1]
                        + self.config.beta * (_one_hot(target, acts[-1]) - acts[-1]),
                    ]
            else:
                acts = geometry.forward_with_intermediates(state.x, substrate)
                if target is not None and acts:
                    # Nudge the output activation toward the target
                    acts = [
                        *acts[:-1],
                        acts[-1]
                        + self.config.beta * (_one_hot(target, acts[-1]) - acts[-1]),
                    ]
        else:
            acts = state.activations if state.activations is not None else []
        if isinstance(acts, list):
            acts = _apply_gain_control(acts, self.config.gain_control)
        if target is None:
            state.free_state = acts
        else:
            state.nudged_state = acts
        state.activations = acts
        return state

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        # Proxy: negative log-likelihood for instantaneous pass
        if state.loss is not None:
            return torch.as_tensor(state.loss)
        return torch.tensor(0.0)


class DiffusionDynamics(_SettleTelemetry):
    """Langevin dynamics over the geometry's Hopfield energy.

    The settle is a noisy relaxer: each step descends the same symmetric
    energy the em family settles (``_compute_hopfield_energy`` through the
    geometry's weights) with Langevin noise
    ``dh = -∇E dt + sqrt(2·D)·dW``. This makes diffusion a stochastic
    sampler over the *geometry's* fixed points — not a prior-only random
    walk (the pre-TODO28-audit defect: the energy never read the
    weights, so every topology produced the same trajectory statistics).

    Layer-structured geometries only (the validate() constraint map
    already forbids the rest): the energy is defined over the full
    activation stack. Falls back to a documented prior-only walk on the
    raw state when no layer structure exists (never reached through the
    campaign grid).
    """

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.diffusion()

    def _langevin_energy(
        self,
        leaves: list[Tensor],
        geometry: Geometry,
        target: Tensor | None,
        beta: float,
    ) -> Tensor:
        """Hopfield energy through the geometry + β output nudge."""
        energy = _compute_hopfield_energy(leaves, geometry)
        if target is not None and beta > 0:
            out = leaves[-1]
            energy = energy + beta * (out - _one_hot(target, out)).pow(2).sum()
        return energy

    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
    ) -> CompositeState:
        x = _get_state_x(state)
        if x is None:
            raise ValueError("State must contain input 'x'")

        self._note_settle_start()
        layered = extract_layered_params(geometry)
        if layered is not None and layered.weights:
            block_builder = getattr(geometry, "settle_blocks", None)
            acts: list[Tensor] = (
                list(cast("list[Tensor]", block_builder(x, substrate)))
                if callable(block_builder)
                else list(geometry.forward_with_intermediates(x, substrate))
            )
            if len(acts) < 2:
                raise TypeError(
                    "Diffusion settling requires a layered activation stack"
                )
            input_act = acts[0]
            for _step in range(self.config.max_steps):
                leaves = [a.detach().requires_grad_(True) for a in acts]
                with torch.enable_grad():
                    energy = self._langevin_energy(
                        leaves, geometry, target, self.config.beta
                    )
                    grads = torch.autograd.grad(energy, leaves)
                with torch.no_grad():
                    noise_scale = math.sqrt(2 * self.config.step_size)
                    acts = [
                        a
                        - self.config.step_size * g
                        + noise_scale * torch.randn_like(a)
                        for a, g in zip(leaves, grads, strict=True)
                    ]
                acts[0] = input_act  # clamp the input

            acts = [a.detach() for a in acts]
        else:
            # Fallback: prior-only walk on the raw state (no geometry
            # weights to descend) — unreachable through the campaign grid.
            h = substrate.initial_state(x).detach().requires_grad_(True)
            for _step in range(self.config.max_steps):
                with torch.enable_grad():
                    energy = self._prior_energy(h, target)
                    energy_grad = torch.autograd.grad(energy, h)[0]
                noise = torch.randn_like(h) * math.sqrt(2 * self.config.step_size)
                with torch.no_grad():
                    h = h - self.config.step_size * energy_grad + noise
                h = h.detach().requires_grad_(True)
            acts = [h.detach()]

        new_state = _create_output_state(
            state,
            x=x,
            output=acts[-1],
            free_state=acts if target is None else None,
            nudged_state=acts if target is not None else None,
            activations=acts,
        )
        return new_state

    def _prior_energy(self, h: Tensor, target: Tensor | None) -> Tensor:
        """Fallback energy: weight shrinkage + β one-hot pull (prior-only)."""
        energy = h.pow(2).sum()
        if target is not None and self.config.beta > 0:
            energy = energy + self.config.beta * (h - _one_hot(target, h)).pow(2).sum()
        return energy

    def compute_energy_from_state(
        self,
        h: Tensor,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
        beta: float = 0.0,
    ) -> Tensor:
        """Prior-only energy of the raw state (shrinkage + β one-hot pull).

        The geometry-dependent energy lives in ``settle``/
        ``_langevin_energy`` over the full activation stack; this scalar
        form only serves the single-vector fallback and external probes.
        """
        energy = h.pow(2).sum()
        if target is not None and beta > 0:
            target_onehot = _one_hot(target, h)
            energy += beta * (h - target_onehot).pow(2).sum()
        return energy

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        """Hopfield energy of the last settle's activation stack."""
        acts = state.free_state
        if acts is None:
            acts = state.nudged_state
        if acts is None:
            acts = state.activations
        if isinstance(acts, list) and len(acts) >= 2:
            return _compute_hopfield_energy(acts, geometry)
        h = _state_energy_vector(state)
        return self._prior_energy(_energy_tensor(h), None)


class LazyStateDynamics(_SettleTelemetry):
    """Sequential (Gauss–Seidel) EqProp settle — lazy per-layer activation.

    The Jacobi settle (EnergyMinimization family) updates every hidden
    layer simultaneously from the previous step's activations; this
    dynamics updates layers one at a time within a sweep, each reading
    the freshest neighbor values — the same symmetric-energy fixed point
    reached in systematically fewer sweeps (Gauss–Seidel vs Jacobi).
    On-demand activation: a layer is recomputed only when its turn comes,
    so the sweep-count contrast against an equivalent Jacobi settle is
    directly measurable on large-dim builds.

    Settles through the Substrate operator API (bottom-up passes via
    ``get_forward_operator()``; top-down reads are mathematical
    transposes). Requires a layer-structured geometry without recurrent
    weights — fail-loud otherwise. No momentum (the sequential sweep
    already carries fresh information per layer).

    Canonical contract (StateDynamics Protocol): settle runs the free
    phase when ``target is None`` and the nudged phase otherwise (output
    nudge applied each sweep, mirroring ``SubstrateSettleKernel.step``);
    compute_energy is the shared Hopfield energy of the settled acts.
    """

    def __init__(self, config: StateDynamicsConfig | None = None):
        self.config = config or StateDynamicsConfig.lazy()
        self._activation_cache: dict[int, list[Tensor]] = {}

    def _layered(self, geometry: Geometry) -> LayeredParams:
        params = extract_layered_params(geometry)
        if params is None or not params.weights:
            raise TypeError(
                f"LazyStateDynamics requires a layer-structured geometry, "
                f"got {type(geometry).__name__}"
            )
        if params.recurrent_weight is not None:
            raise TypeError(
                "LazyStateDynamics does not support recurrent geometry "
                "(SystemConfig.validate() already rejects the pairing)"
            )
        return params

    def settle(
        self,
        state: CompositeState,
        geometry: Geometry,
        substrate: Substrate,
        target: Tensor | None = None,
    ) -> CompositeState:
        """Sequential per-layer settle (Gauss–Seidel sweeps)."""
        params = self._layered(geometry)
        op = substrate.get_forward_operator()
        weights, biases, activations = (
            params.weights,
            params.biases,
            params.activations,
        )
        if state.x is None:
            return state
        acts = list(geometry.forward_with_intermediates(state.x, substrate))
        beta = self.config.beta if target is not None else 0.0

        self._note_settle_start()
        for sweep in range(self.config.max_steps):
            max_delta = 0.0
            for i in range(len(acts) - 2):
                pre = op(acts[i], weights[i])
                b = biases[i]
                if b is not None:
                    pre = pre + b
                total = pre + acts[i + 2] @ weights[i + 1]
                if params.residual and i > 0 and acts[i].shape == acts[i + 1].shape:
                    total = total + acts[i]
                target_h = activations[i](total) if i < len(activations) else total
                h_new = acts[i + 1] + self.config.step_size * (target_h - acts[i + 1])
                max_delta = max(
                    max_delta, torch.dist(h_new, acts[i + 1], p=float("inf")).item()
                )
                acts[i + 1] = h_new
            out = op(acts[-2], weights[-1])
            b = biases[-1]
            if b is not None:
                out = out + b
            if beta > 0 and target is not None:
                out = out + beta * (_one_hot(target, out) - out)
            max_delta = max(max_delta, torch.dist(out, acts[-1], p=float("inf")).item())
            acts[-1] = out

            if sweep >= self.config.convergence_start:
                self._activation_cache[sweep] = [a.clone() for a in acts]
                if max_delta < self.config.convergence_threshold:
                    self._settle_steps_used = sweep + 1
                    break

        new_state = _create_output_state(
            state,
            output=acts[-1],
            free_state=acts if target is None else None,
            nudged_state=acts if target is not None else None,
            activations=acts,
        )
        return new_state

    def compute_energy(self, state: CompositeState, geometry: Geometry) -> Tensor:
        """Hopfield energy of the settled state (shared with the EqProp family)."""
        acts = _get_state_free_state(state)
        if acts is None:
            acts = _get_state_activations(state)
        if acts is None or isinstance(acts, Tensor):
            return torch.tensor(0.0)
        return _compute_hopfield_energy(list(acts), geometry)

    def get_cached_activations(self) -> dict[int, list[Tensor]]:
        """Return the per-sweep activation snapshots recorded during settling."""
        return self._activation_cache

    def clear_cache(self) -> None:
        """Clear the per-sweep activation cache."""
        self._activation_cache.clear()


__all__ = [
    "DiffusionDynamics",
    "EnergyMinimizationDynamics",
    "ErrorPredictiveCodingDynamics",
    "InstantaneousDynamics",
    "LazyStateDynamics",
    "PredictiveSettlingDynamics",
    "SpikeIntegrationDynamics",
    "StateDynamics",
    "StateDynamicsConfig",
]
