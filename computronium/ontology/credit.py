"""Layer 4: CreditAssignment — Error Routing & Pseudo-Gradients."""

from __future__ import annotations

import zlib
from abc import abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar, Literal, Protocol, cast, runtime_checkable

import torch
from torch import Tensor, nn

from computronium.ontology.utils import _learnable_weight_names

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.ontology.geometry import Geometry, TransformerGeometry
    from computronium.ontology.system import SystemState
    from computronium.ontology.update import ParameterUpdate


# ============================================================
# CreditAssignment Configuration
# ============================================================


CreditNormMode = Literal["none", "relative", "rms", "beta_adaptive", "spectral"]


def _apply_credit_norm(
    grads: list[Tensor],
    mode: CreditNormMode,
    error_refs: list[Tensor] | None = None,
) -> list[Tensor]:
    """Per-layer credit-signal normalization (TODO12 A4).

    ``grads`` are the per-layer credit tensors at formation; zeros stay
    zeros (a zero norm leaves the layer untouched — no fabricated signal).
    """
    if mode == "none":
        return grads
    out: list[Tensor] = []
    for i, g in enumerate(grads):
        if not torch.isfinite(g).all():
            # Diverged credit: SVD/RMS on inf/NaN would crash or poison
            # downstream sweeps — pass the layer through untouched (the
            # run is already lost; the crash only destroys the evidence;
            # the RiemannianOrthogonalUpdate diverged-step precedent).
            out.append(g)
            continue
        if mode == "spectral":
            if g.ndim < 2:
                out.append(g)
                continue
            radius = torch.linalg.matrix_norm(g, ord=2)
            out.append(g / (radius + 1e-8) if radius > 0 else g)
        elif mode == "rms":
            rms = g.square().mean().sqrt()
            out.append(g / (rms + 1e-8) if rms > 0 else g)
        else:  # "relative" | "beta_adaptive"
            ref = (
                error_refs[i]
                if error_refs is not None and i < len(error_refs)
                else None
            )
            if ref is None:
                out.append(g)
                continue
            mag = ref.norm() if mode == "relative" else ref.square().mean().sqrt()
            out.append(g / (mag + 1e-8) if mag > 0 else g)
    return out


@dataclass(frozen=True, slots=True)
class CreditAssignmentConfig:
    """Configuration for credit assignment.

    Attributes:
        credit_type: "thermodynamic_contrast", "random_projections",
            "local_goodness", "temporal_trace", "target_inversion"
        beta: Nudge strength (for thermodynamic contrast)
        credit_norm: Per-layer credit-signal normalization (TODO12 A4,
            RESEARCH4 Lever 1 — "Muon applied to the backward signal").
            Applied at pseudo-gradient formation: ``relative`` rescales
            each layer's gradient by its settled error magnitude
            ε = (free − nudged)/β; ``rms`` rescales to unit RMS per
            layer; ``beta_adaptive`` is the ePC-native per-layer β
            tuning (unit-scale error, Fix-2 option 2); ``spectral``
            rescales matrix gradients to spectral radius 1 (Fix-2
            option 3). Zeros stay zeros — never fabricates signal.
        feedback_matrix: Optional fixed feedback matrix
            (for random projections)
        local_objective: Local-credit algorithm selection (for
            local_goodness): "ff" runs the Forward-Forward layer-local
            goodness contrast (no inverse pass); "pepita" runs the
            PEPITA error-modulated update (output differential routed
            through fixed random inverse projections)
        orthogonal_init: Initialize feedback matrices with orthogonal weights
        feedback_scale: Scaling factor for feedback matrices
        readout_error: Augment the FF goodness contrast with CE on the
            free output logits (the "FF hybrid"): pure FF's norm-contrast
            is error-blind — no term sees the target — which refutes it
            on tasks whose difficulty is the output mapping (LM: flat at
            chance across beta/lr/ctx). The readout CE carries the target
            through the shared autograd graph; hidden layers keep the
            layer-local objective
        a_plus: STDP potentiation amplitude (for temporal_trace)
        a_minus: STDP depression amplitude (for temporal_trace)
        tau: STDP time constant (for temporal_trace, legacy)
        tau_pre: STDP pre-synaptic trace time constant (for timing-asymmetric STDP)
        tau_post: STDP post-synaptic trace time constant (for timing-asymmetric STDP)
        learned_feedback: Train the PEPITA inverse projections B as
            credit-internal state via a transport-free reconstruction
            objective (TODO12 B1, RESEARCH4 Fix 1a): each B_i is regressed
            (closed-form ridge, autograd-free) to map the broadcast output
            error e₁ back into the post-synaptic activity space of its
            weight, EMA-blended at ``feedback_lr`` every
            ``feedback_update_every`` steps. Never reads forward weights
            (the L3 transport lock is the guard — B0's legacy-AdaptiveFA
            defect is not inherited)
        feedback_lr: EMA rate toward the ridge solution (learned_feedback)
        feedback_update_every: Steps between learned-feedback updates
    homeostatic_target: Target row-norm for homeostatic synaptic
        scaling (timing-asymmetric STDP)
    homeostatic_scaling: Gate the homeostatic synaptic-scaling term on
        the timing-asymmetric STDP path (False = naive unconstrained
        rule, F2's collapse regime)
    """

    credit_type: str
    beta: float
    feedback_matrix: Tensor | None
    local_objective: Literal["ff", "pepita"]
    orthogonal_init: bool
    feedback_scale: float
    readout_error: bool = False
    credit_norm: CreditNormMode = "none"
    a_plus: float = 1.0
    a_minus: float = 1.0
    tau: float = 20.0
    tau_pre: float = 0.9
    tau_post: float = 0.9
    homeostatic_target: float = 1.0
    homeostatic_scaling: bool = False
    learned_feedback: bool = False
    feedback_lr: float = 0.5
    feedback_update_every: int = 1
    label_dim: int = 0
    ema_beta: float = 0.99
    stream_norm: bool = True
    contrast_threshold: float = 2.0
    readout_scale: float = 1.0
    sequential_lr: float = 0.0

    @classmethod
    def local_contrastive(
        cls,
        *,
        label_dim: int = 10,
        ema_beta: float = 0.99,
        stream_norm: bool = True,
        contrast_threshold: float = 2.0,
        readout_scale: float = 1.0,
        sequential_lr: float = 0.0,
    ) -> CreditAssignmentConfig:
        """Per-layer recomputed FF contrast with EMA-magnitude normalization.

        The O(1)-peak-memory forward-local class (TODO13b W2). Contract:
        inputs must be **label-augmented** (last ``label_dim`` features =
        the one-hot target; b4/`scripts/probes/w2_ema_rung.py` pattern) —
        the good/bad contrast lives in the input label channel, NOT in
        the FREE/NUDGED phases (which are structurally identical at hidden
        layers under instantaneous settle — verified 2026-09-07: hidden
        max|free−nudged| = 0.0 exactly). The output readout layer trains
        on local CE; hidden layers on the softplus-gated goodness
        contrast; every pseudo-gradient is EMA-normalized (the probe-
        confirmed repair for the instantaneous-norm depth collapse).

        ``sequential_lr``: Hinton within-batch layer propagation. When > 0,
        each hidden layer's EMA-normalized update is applied to the
        credit's recompute view before later layers' inputs are formed —
        the b4/`w2_ema_rung` recipe, and the load-bearing mechanism for
        depth (Jacobi ordering collapses d4 0.757 → 0.27, d8 0.512 → 0.14,
        measured 2026-09-07). Must equal the update rule's step size;
        ``0`` gives simultaneous (Jacobi) ordering.
        """
        return cls(
            credit_type="local_contrastive",
            beta=0.5,
            feedback_matrix=None,
            local_objective="ff",
            orthogonal_init=False,
            feedback_scale=0.01,
            readout_error=True,
            credit_norm="none",
            label_dim=label_dim,
            ema_beta=ema_beta,
            stream_norm=stream_norm,
            contrast_threshold=contrast_threshold,
            readout_scale=readout_scale,
            sequential_lr=sequential_lr,
        )

    @classmethod
    def thermodynamic_contrast(
        cls,
        *,
        beta: float = 0.5,
        feedback_matrix: Tensor | None = None,
        local_objective: Literal["ff", "pepita"] = "ff",
        orthogonal_init: bool = False,
        feedback_scale: float = 0.01,
        credit_norm: CreditNormMode = "none",
    ) -> CreditAssignmentConfig:
        return cls(
            credit_type="thermodynamic_contrast",
            beta=beta,
            feedback_matrix=feedback_matrix,
            local_objective=local_objective,
            orthogonal_init=orthogonal_init,
            feedback_scale=feedback_scale,
            credit_norm=credit_norm,
        )

    @classmethod
    def random_projections(
        cls,
        *,
        beta: float = 0.5,
        feedback_matrix: Tensor | None = None,
        local_objective: Literal["ff", "pepita"] = "ff",
        orthogonal_init: bool = False,
        feedback_scale: float = 0.01,
    ) -> CreditAssignmentConfig:
        return cls(
            credit_type="random_projections",
            beta=beta,
            feedback_matrix=feedback_matrix,
            local_objective=local_objective,
            orthogonal_init=orthogonal_init,
            feedback_scale=feedback_scale,
        )

    @classmethod
    def local_goodness(  # ruff: ignore[too-many-arguments] (config mirrors the knobs)
        cls,
        *,
        beta: float = 0.5,
        feedback_matrix: Tensor | None = None,
        local_objective: Literal["ff", "pepita"] = "ff",
        orthogonal_init: bool = False,
        feedback_scale: float = 0.01,
        readout_error: bool = False,
        credit_norm: CreditNormMode = "none",
        learned_feedback: bool = False,
        feedback_lr: float = 0.5,
        feedback_update_every: int = 1,
    ) -> CreditAssignmentConfig:
        return cls(
            credit_type="local_goodness",
            readout_error=readout_error,
            credit_norm=credit_norm,
            learned_feedback=learned_feedback,
            feedback_lr=feedback_lr,
            feedback_update_every=feedback_update_every,
            beta=beta,
            feedback_matrix=feedback_matrix,
            local_objective=local_objective,
            orthogonal_init=orthogonal_init,
            feedback_scale=feedback_scale,
        )

    @classmethod
    def temporal_trace(  # ruff: ignore[too-many-arguments] (config mirrors the STDP knobs)
        cls,
        *,
        beta: float = 0.5,
        feedback_matrix: Tensor | None = None,
        local_objective: Literal["ff", "pepita"] = "ff",
        orthogonal_init: bool = False,
        feedback_scale: float = 0.01,
        a_plus: float = 1.0,
        a_minus: float = 0.5,
        tau: float = 20.0,
        tau_pre: float = 0.9,
        tau_post: float = 0.9,
        homeostatic_scaling: bool = False,
        homeostatic_target: float = 1.0,
    ) -> CreditAssignmentConfig:
        """Potentiation/depression weights must differ: the rate-coded
        surrogate correlates the same (pre, post) activity pair in both
        directions, so ``a_plus == a_minus`` yields an identically-zero
        pseudo-gradient.

        For timing-asymmetric STDP (when spike rasters are available),
        ``tau_pre`` and ``tau_post`` control the exponential decay of the
        pre- and post-synaptic eligibility traces.
        """
        return cls(
            credit_type="temporal_trace",
            beta=beta,
            feedback_matrix=feedback_matrix,
            local_objective=local_objective,
            orthogonal_init=orthogonal_init,
            feedback_scale=feedback_scale,
            a_plus=a_plus,
            a_minus=a_minus,
            tau=tau,
            tau_pre=tau_pre,
            tau_post=tau_post,
            homeostatic_scaling=homeostatic_scaling,
            homeostatic_target=homeostatic_target,
        )

    @classmethod
    def target_inversion(
        cls,
        *,
        beta: float = 0.5,
        feedback_matrix: Tensor | None = None,
        local_objective: Literal["ff", "pepita"] = "ff",
        orthogonal_init: bool = False,
        feedback_scale: float = 0.01,
    ) -> CreditAssignmentConfig:
        return cls(
            credit_type="target_inversion",
            beta=beta,
            feedback_matrix=feedback_matrix,
            local_objective=local_objective,
            orthogonal_init=orthogonal_init,
            feedback_scale=feedback_scale,
        )

    @classmethod
    def homeostatic(
        cls,
        *,
        beta: float = 0.5,
        feedback_matrix: Tensor | None = None,
        local_objective: Literal["ff", "pepita"] = "ff",
        orthogonal_init: bool = False,
        feedback_scale: float = 0.01,
    ) -> CreditAssignmentConfig:
        return cls(
            credit_type="homeostatic",
            beta=beta,
            feedback_matrix=feedback_matrix,
            local_objective=local_objective,
            orthogonal_init=orthogonal_init,
            feedback_scale=feedback_scale,
        )

    @classmethod
    def gradient(
        cls,
        *,
        beta: float = 0.5,
        feedback_matrix: Tensor | None = None,
        local_objective: Literal["ff", "pepita"] = "ff",
        orthogonal_init: bool = False,
        feedback_scale: float = 0.01,
    ) -> CreditAssignmentConfig:
        return cls(
            credit_type="gradient",
            beta=beta,
            feedback_matrix=feedback_matrix,
            local_objective=local_objective,
            orthogonal_init=orthogonal_init,
            feedback_scale=feedback_scale,
        )


# ============================================================
# CreditAssignment Protocol
# ============================================================


class Phase(StrEnum):
    """Settling phase declared by a credit rule.

    Credits declare exactly the phases they consume (``phases`` ClassVar);
    the pipeline settles only declared phases, removing wasted settles for
    families that ignore free or nudged states.
    """

    FREE = "free"
    NUDGED = "nudged"


@runtime_checkable
class CreditAssignment(Protocol):
    """How the network computes the direction of learning (pseudo-gradient).

    Uses only locally available signals to compute a gradient-like update
    direction. The five canonical types:
    - ThermodynamicContrast: (nudged - free) / beta (EqProp)
    - RandomProjections: Fixed/adaptive random feedback matrices (FA, DFA)
    - LocalGoodness: Layer-local contrastive objectives (FF, PEPITA)
    - TemporalTrace: Spike-timing correlations (STDP)
    - TargetInversion: Propagating local targets (Target Prop)

    Capabilities are declared, not assumed:
    - ``phases``: settling phases the rule consumes; the pipeline settles
      only these.
    - ``requires_autograd``: True when the rule needs autograd through
      settling (the default detached/no-grad path is bypassed only then).

    Output is a list of pseudo-gradients, one per learnable weight layer,
    matching the Geometry's parameter structure.
    """

    config: CreditAssignmentConfig

    phases: ClassVar[tuple[Phase, ...]]
    requires_autograd: ClassVar[bool]

    @abstractmethod
    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        """Compute pseudo-gradients from the settled phase states.

        Args:
            states: Phase-keyed settled states; contains exactly the phases
                this rule declares.
            loss: Task loss at the pipeline's output state (None-safe).
            geometry: Network topology (provides layer structure)

        Returns:
            List of pseudo-gradient tensors, one per learnable weight layer
        """
        ...

    # DEFAULT METHOD — non-breaking, only overridden by LocalGoodness/TargetInversion
    def surrogate_objective(
        self,
        free_state: SystemState,
        nudged_state: SystemState,
        geometry: Geometry,
    ) -> Tensor:
        """Compute layer-local surrogate loss for gradient checking.

        Only LocalGoodnessCredit and TargetInversionCredit override this.
        Others raise NotImplementedError.
        """
        raise NotImplementedError(
            "Surrogate objective not defined for this credit rule"
        )


def _acts_list(activations: list[Tensor] | Tensor | None) -> list[Tensor]:
    """Normalize activations to a list of layer tensors."""
    if activations is None:
        return []
    if isinstance(activations, list):
        return activations
    return [activations]


def _block_transition_acts(
    acts: list[Tensor], geometry: Geometry
) -> list[Tensor] | None:
    """The settled acts when the geometry declares a block transition table
    and they align with it (tile meshes, R11.1.4); else None."""
    count = getattr(geometry, "block_act_count", None)
    if count is not None and len(acts) == count:
        return acts
    return None


def _propagate_targets(
    acts: list[Tensor],
    y: Tensor,
    weight_names: list[str],
    geometry: Geometry,
) -> list[Tensor | None]:
    """Transpose-feedback target propagation: t_L = one-hot(y), t_l = t_{l+1} @ W_{l+1}."""
    out_dim = acts[-1].shape[-1]
    targets: list[Tensor | None] = [None] * len(acts)
    targets[-1] = torch.nn.functional.one_hot(y, num_classes=out_dim).float()
    for l in range(min(len(weight_names), len(acts) - 1) - 1, -1, -1):  # ruff: ignore[ambiguous-variable-name]
        nxt = targets[l + 1]
        if nxt is None:
            break
        w = geometry.params[weight_names[l]]
        if nxt.shape[-1] != w.shape[0]:
            # Ragged weight (e.g. tile meshes): the transition contract
            # does not hold — stop propagating rather than crash.
            break
        targets[l] = nxt @ w
    return targets


def _weight_acts(
    weight_names: list[str], acts: list[Tensor], geometry: Geometry
) -> list[tuple[Tensor, Tensor] | None]:
    """(pre, post) activation pair each learnable weight consumes.

    Positional over act transitions: weight i maps acts[i] -> acts[i+1].
    Surplus weights (recurrent self-connections) consume the last hidden
    layer as both pre and post — the correlate the settle kernel itself
    feeds them. Weights whose shape does not match their act-pair widths
    (tile/ragged meshes) map to None — credits emit zeros for them.
    """
    n_trans = len(acts) - 1
    pairs: list[tuple[Tensor, Tensor] | None] = []
    for i, name in enumerate(weight_names):
        w = geometry.params[name]
        if i < n_trans:
            pre, post = acts[i], acts[i + 1]
        elif n_trans >= 1:
            pre = post = acts[n_trans - 1]
        else:
            pairs.append(None)
            continue
        if w.shape[0] == post.shape[-1] and w.shape[1] == pre.shape[-1]:
            pairs.append((pre, post))
        else:
            pairs.append(None)
    return pairs


# ============================================================
# Default/Reference CreditAssignment Implementations
# ============================================================


class ThermodynamicContrast:
    """Equilibrium Propagation credit assignment: (nudged - free) / beta.

    For feedforward networks, computes parameter pseudo-gradients using the
    contrastive Hebbian rule: ΔW = (free_pre @ free_post - nudged_pre @ nudged_post) / β
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE, Phase.NUDGED)
    requires_autograd: ClassVar[bool] = False

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.thermodynamic_contrast()

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        free_state = states.get(Phase.FREE)
        nudged_state = states.get(Phase.NUDGED)
        if free_state is None or nudged_state is None:
            return []
        if free_state.activations is None or nudged_state.activations is None:
            return []

        free_acts = (
            free_state.activations
            if isinstance(free_state.activations, list)
            else [free_state.activations]
        )
        nudged_acts = (
            nudged_state.activations
            if isinstance(nudged_state.activations, list)
            else [nudged_state.activations]
        )

        # Tile meshes: per-transition block contrast scattered to per-edge
        # weights (R11.1.4).
        if _block_transition_acts(free_acts, geometry) is not None and (
            len(nudged_acts) == len(free_acts)
        ):
            batch = free_acts[0].shape[0]
            block_grads = [
                (
                    free_acts[i].T @ free_acts[i + 1]
                    - nudged_acts[i].T @ nudged_acts[i + 1]
                ).T
                / self.config.beta
                / batch
                for i in range(len(free_acts) - 1)
            ]
            eps = [
                (free_acts[i + 1] - nudged_acts[i + 1]) / self.config.beta
                for i in range(len(free_acts) - 1)
            ]
            return geometry.scatter_block_grads(
                _apply_credit_norm(block_grads, self.config.credit_norm, eps)
            )

        weight_names = _learnable_weight_names(geometry.params)
        n_layers = len(free_acts) - 1
        eps = [
            (free_acts[i + 1] - nudged_acts[i + 1]) / self.config.beta
            for i in range(n_layers)
        ]
        grads = []
        # Contrastive Hebbian gradients per weight matrix; activations are
        # ordered [input, hidden1, ..., output].
        for i in range(min(n_layers, len(weight_names))):
            contrast = (
                (
                    free_acts[i].T @ free_acts[i + 1]
                    - nudged_acts[i].T @ nudged_acts[i + 1]
                )
                / self.config.beta
                / free_acts[i].shape[0]
            )
            grads.append(contrast.T)
        return _apply_credit_norm(grads, self.config.credit_norm, eps)

    def surrogate_objective(
        self,
        free_state: SystemState,
        nudged_state: SystemState,
        geometry: Geometry,
    ) -> Tensor:
        """Surrogate objective for EqProp: negative free energy difference."""
        if free_state.energy is not None and nudged_state.energy is not None:
            return torch.as_tensor(nudged_state.energy - free_state.energy)
        return torch.tensor(0.0)


# Alias for backwards compatibility with README/docs
ThermodynamicContrastCredit = ThermodynamicContrast


class RandomProjectionsCredit:
    """Fixed random feedback pathways (FA/DFA) with an autograd readout.

    Top error δ_L = ∂L/∂a_L via autograd on the task loss (no weight
    transport at the readout), propagated down through FIXED random
    matrices: δ_i = δ_{i+1} @ B_i with B_i ~ feedback_scale · N(0,1),
    fixed at first use. Per-layer pseudo-gradient ΔW_i = δ_{i+1}ᵀ a_i / batch;
    recurrent self-connections project the last hidden layer's error
    through their own fixed feedback. When the settle graph is unavailable
    the signal is zeros — never fabricated noise.
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE, Phase.NUDGED)
    requires_autograd: ClassVar[bool] = True

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.random_projections()
        self._feedback_weights: dict[str, Tensor] = {}

    def _init_feedback_weights(
        self, geometry: Geometry, device: torch.device | None = None
    ) -> None:
        """Initialize fixed random feedback matrices for each learnable weight.

        Feedback matrices are initialized once and kept constant throughout training.
        This implements the FA/DFA assumption of fixed feedback pathways.
        """
        if self._feedback_weights:
            return  # Already initialized
        for name in _learnable_weight_names(geometry.params):
            param = geometry.params[name]
            # Initialize with small random values
            fb = torch.randn_like(param, device=device) * self.config.feedback_scale
            self._feedback_weights[name] = fb

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        """Compute FA pseudo-gradients through fixed feedback matrices."""
        nudged_state = states.get(Phase.NUDGED)
        if loss is None or nudged_state is None or nudged_state.activations is None:
            return []

        acts = _acts_list(nudged_state.activations)
        weight_names = _learnable_weight_names(geometry.params)
        if len(acts) < 2 or not weight_names:
            return []

        self._init_feedback_weights(geometry, acts[-1].device)
        logits = acts[-1]
        if not logits.requires_grad:
            # Settle graph not preserved (e.g. detached settle paths): no
            # error signal exists — zeros, never fabricated signal.
            return [torch.zeros_like(geometry.params[n]) for n in weight_names]

        delta_out = torch.autograd.grad(loss, logits)[0].detach()
        n_trans = len(acts) - 1
        batch = acts[0].shape[0]

        # Tile meshes: feedback blocks assembled per transition, error
        # walked back over the block layout, grads scattered to per-edge
        # weights (R11.1.4). B_e shares its weight's shape, so the layered
        # contract (B maps act_{k+1} widths down to act_k) holds per edge.
        if _block_transition_acts(acts, geometry) is not None:
            blocks = geometry.assemble_blocks(self._feedback_weights)
            err = _apply_credit_norm([delta_out], self.config.credit_norm)[0]
            block_grads: list[Tensor] = []
            for i in range(n_trans - 1, -1, -1):
                block_grads.append(err.T @ acts[i] / batch)
                err = _apply_credit_norm(
                    [err @ blocks[i]], self.config.credit_norm, [acts[i]]
                )[0]
            block_grads.reverse()
            return geometry.scatter_block_grads(block_grads)

        # Layered contract: feedback B_k must map the act-space of layer
        # k+1 down to layer k. Tile/ragged weights (e.g. per-tile matrices
        # not aligned with the act widths) break the chain — zeros, never
        # fabricated signal.
        for k in range(n_trans):
            b = self._feedback_weights[weight_names[k]]
            if b.shape[0] != acts[k + 1].shape[-1] or b.shape[1] != acts[k].shape[-1]:
                return [torch.zeros_like(geometry.params[n]) for n in weight_names]

        # Feedback-propagated error at each act layer:
        # err_at[L] = ∂L/∂a_L; err_at[k] = err_at[k+1] @ B_k.
        # During the sweep, err is err_at[i + 1] on entering iteration i.
        grads: list[Tensor] = []
        err = _apply_credit_norm([delta_out], self.config.credit_norm)[0]
        hidden_err = err
        for i in range(n_trans - 1, -1, -1):
            grads.append(err.T @ acts[i] / batch)
            err = _apply_credit_norm(
                [err @ self._feedback_weights[weight_names[i]]],
                self.config.credit_norm,
                [acts[i]],
            )[0]
            if i == n_trans - 1:
                # Error at the last hidden layer: upstream of the recurrent
                # self-connection.
                hidden_err = err
        grads.reverse()
        for _name in weight_names[n_trans:]:
            # Recurrent self-connection at the last hidden layer: its
            # upstream error is the propagated error at that layer.
            grads.append(hidden_err.T @ acts[n_trans - 1] / batch)
        return grads

    def surrogate_objective(
        self,
        free_state: SystemState,
        nudged_state: SystemState,
        geometry: Geometry,
    ) -> Tensor:
        """Surrogate objective not defined for RandomProjectionsCredit."""
        raise NotImplementedError(
            "Surrogate objective not defined for RandomProjectionsCredit"
        )


class LocalGoodnessCredit:
    """Layer-local contrastive credit — two realized algorithms.

    ``local_objective="ff"`` (Forward-Forward, Hinton 2022): layer-local
    goodness G_l = mean(acts_l^2); the pseudo-gradient descends
    (G_free − G_nudged) so nudged goodness increases, free goodness
    decreases. Layer-local loss, no inverse pass.

    ``local_objective="pepita"`` (Dellaferrera & Kreiman 2022): the
    output-layer differential e₁ = nudged_out − free_out is routed back
    through fixed random inverse projections (orthogonal rows, scaled by
    ``feedback_scale``) and each weight receives ΔW ∝ −(e₁ @ Bᵀ)ᵀ a_pre
    from the modulated (nudged) pass — forward differential + inverse
    propagation modulation, closed form, no autograd through the settle.

    The two are genuinely different algorithms: FF's gradient is the
    autograd derivative of the per-layer goodness contrast; PEPITA's is a
    fixed-random-feedback error modulation. They are NOT interchangeable
    (the D13 record's byte-identical numbers were the defect this
    realization fixes).
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE, Phase.NUDGED)
    requires_autograd: ClassVar[bool] = True

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.local_goodness()
        self._feedback: dict[tuple[str, tuple[int, int], str, str], Tensor] = {}
        self._learned: dict[tuple[str, tuple[int, int], str, str], Tensor] = {}
        self._feedback_step = 0

    def _inverse_projection(
        self, name: str, width: int, out_dim: int, device: str, dtype
    ) -> Tensor:
        """Fixed random inverse projection B: (out_dim, width)."""
        key = (name, (out_dim, width), str(device), str(dtype))
        if key not in self._feedback:
            gen = torch.Generator(device=device)
            gen.manual_seed(zlib.crc32(name.encode()))
            b = torch.empty(out_dim, width, device=device, dtype=torch.float32)
            if self.config.orthogonal_init:
                torch.nn.init.orthogonal_(b, generator=gen)
            else:
                b.normal_(generator=gen)
            self._feedback[key] = b.to(dtype) * self.config.feedback_scale
        return self._feedback[key]

    def _learned_projection(
        self, name: str, width: int, out_dim: int, device: str, dtype
    ) -> Tensor:
        """Credit-internal learned B: (out_dim, width), same deterministic
        init as the fixed projection until the first reconstruction update."""
        key = (name, (out_dim, width), device, str(dtype))
        if key not in self._learned:
            self._learned[key] = self._inverse_projection(
                name, width, out_dim, device, dtype
            ).clone()
        return self._learned[key]

    def _update_learned_feedback(
        self,
        free_acts: list[Tensor],
        e1: Tensor,
        weight_names: list[str],
        n_trans: int,
    ) -> None:
        """Transport-free reconstruction update of the learned B matrices.

        Objective (RESEARCH4 Fix 1a): B_i maps the broadcast output error
        e₁ back into weight i's post-synaptic activity space. The ridge
        solution is the closed-form local regression post @ C ≈ e₁ with
        B_i = Cᵀ — autoencoder-style, autograd-free, reads only settled
        activations and e₁ (never ``param.data``: the L3 transport lock).
        """
        self._feedback_step += 1
        if (self._feedback_step - 1) % max(1, self.config.feedback_update_every):
            return
        for k, name in enumerate(weight_names):
            if k >= n_trans:
                continue
            post = free_acts[k + 1].detach()
            width = post.shape[-1]
            key = (name, (e1.shape[-1], width), str(post.device), str(e1.dtype))
            if key not in self._learned:
                continue
            if not (torch.isfinite(post).all() and torch.isfinite(e1).all()):
                continue  # diverged settle: skip, don't poison B
            a = post.float()
            g = a.T @ a
            lam = 1e-3 * g.diagonal().mean().clamp_min(1e-12)
            c = torch.linalg.solve(
                g + lam * torch.eye(g.shape[0], device=g.device), a.T @ e1.float()
            )
            b_new = (c.T * self.config.feedback_scale).to(e1.dtype)
            if not torch.isfinite(b_new).all():
                continue
            cur = self._learned[key]
            lr = self.config.feedback_lr
            self._learned[key] = ((1.0 - lr) * cur.float() + lr * b_new.float()).to(
                cur.dtype
            )

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        """Snapshot protocol (A1 precedent): learned-B matrices + step counter."""
        if not self._learned:
            return {}
        return {
            "learned_feedback": {
                f"{name}|{shape[0]}x{shape[1]}|{device}|{dtype}": t.detach().clone()
                for (name, shape, device, dtype), t in self._learned.items()
            },
            "step": {"counter": torch.tensor(self._feedback_step)},
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        step_group = state.get("step", {})
        step = step_group.get("counter") if isinstance(step_group, dict) else None
        if not isinstance(step, Tensor):
            msg = "learned-feedback credit state is missing the step counter"
            raise RuntimeError(msg)  # ruff: ignore[type-check-without-type-error]
        self._feedback_step = int(step.item())
        for key, tensor in state.get("learned_feedback", {}).items():
            name, shape_s, device, dtype = key.split("|", 3)
            rows, cols = (int(s) for s in shape_s.split("x"))
            t_key = (name, (rows, cols), device, dtype)
            cached = self._learned.get(t_key)
            if cached is not None and cached.shape != tensor.shape:
                msg = (
                    f"learned-feedback state shape mismatch for {name!r}: "
                    f"state {tuple(tensor.shape)} vs cache {tuple(cached.shape)} "
                    "(system-scoped state cannot be re-targeted)"
                )
                raise RuntimeError(msg)
            self._learned[t_key] = tensor.detach().clone()

    def _pepita_gradient(
        self,
        free_state: SystemState,
        free_acts: list[Tensor],
        nudged_acts: list[Tensor],
        weight_names: list[str],
        geometry: Geometry,
    ) -> list[Tensor]:
        n_trans = min(len(free_acts), len(nudged_acts)) - 1
        out = free_acts[-1].detach()
        y = free_state.y
        if y is None:
            return [torch.zeros_like(geometry.params[n]) for n in weight_names]
        num_classes = out.shape[-1]
        onehot = torch.nn.functional.one_hot(y, num_classes).to(out.dtype)
        # Probability-space output error (PEPITA's e = y − ŷ). The raw
        # nudged differential is β·(onehot − logits) under
        # InstantaneousDynamics — dominated by the constant one-hot term,
        # which carries no per-sample error information.
        e1 = (onehot - torch.softmax(out, dim=-1)).detach()
        out_dim = e1.shape[1]
        batch = e1.shape[0]
        learned = self.config.learned_feedback
        if learned:
            self._update_learned_feedback(free_acts, e1, weight_names, n_trans)
        grads: list[Tensor] = []
        for k, name in enumerate(weight_names):
            if k >= n_trans:
                # Surplus weights (recurrent self-connections): no route.
                grads.append(torch.zeros_like(geometry.params[name]))
                continue
            width = geometry.params[name].shape[0]
            if learned:
                b = self._learned_projection(
                    name,
                    width,
                    out_dim,
                    str(e1.device),
                    e1.dtype,
                )
            else:
                b = self._inverse_projection(
                    name,
                    width,
                    out_dim,
                    str(e1.device),
                    e1.dtype,
                )
            err = e1 @ b  # (batch, width)
            err = _apply_credit_norm([err], self.config.credit_norm, [free_acts[k]])[0]
            grads.append(-(err.T @ nudged_acts[k].detach()) / batch)
        return grads

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        free_state = states.get(Phase.FREE)
        nudged_state = states.get(Phase.NUDGED)
        if free_state is None or nudged_state is None:
            return []

        free_acts = _acts_list(free_state.activations)
        nudged_acts = _acts_list(nudged_state.activations)
        if not free_acts or not nudged_acts:
            return []

        weight_names = _learnable_weight_names(geometry.params)
        if not weight_names:
            return []

        if self.config.local_objective == "pepita":
            return self._pepita_gradient(
                free_state, free_acts, nudged_acts, weight_names, geometry
            )

        # Layer-local goodness objective summed over act transitions
        # (surplus weights — recurrent self-connections — receive their
        # gradient through the shared hidden-layer goodness).
        n_trans = min(len(free_acts), len(nudged_acts)) - 1
        if n_trans < 1 or not nudged_acts[-1].requires_grad:
            # Settle graph not preserved: no autograd signal — zeros.
            return [torch.zeros_like(geometry.params[n]) for n in weight_names]

        total = torch.zeros((), device=nudged_acts[-1].device)
        for i in range(1, n_trans + 1):
            total += free_acts[i].pow(2).mean() - nudged_acts[i].pow(2).mean()
        y = free_state.y
        if self.config.readout_error and y is not None:
            # FF hybrid: pure FF is error-blind (no term sees the target —
            # measured flat on LM across beta/lr/ctx); the readout CE
            # carries the target through the shared autograd graph while
            # hidden layers keep the layer-local objective.
            total = torch.add(
                total, torch.nn.functional.cross_entropy(free_acts[-1], y)
            )

        params = [geometry.params[n] for n in weight_names]
        grads = torch.autograd.grad(
            total, params, retain_graph=False, create_graph=False, allow_unused=True
        )
        return [
            g if g is not None else torch.zeros_like(p)
            for p, g in zip(params, grads, strict=True)
        ]

    def surrogate_objective(
        self,
        free_state: SystemState,
        nudged_state: SystemState,
        geometry: Geometry,
    ) -> Tensor:
        """Sum of layer-local goodness differences."""
        free_acts = _acts_list(free_state.activations)
        nudged_acts = _acts_list(nudged_state.activations)
        if not free_acts or not nudged_acts:
            return torch.tensor(0.0)
        total = torch.tensor(0.0)
        for i in range(1, min(len(free_acts), len(nudged_acts))):
            total = total + free_acts[i].pow(2).mean() - nudged_acts[i].pow(2).mean()
        return total


class LocalContrastiveCredit:
    """Per-layer recomputed goodness-contrast credit — the O(1)-memory FF
    class (TODO13b W2 flagship).

    Contract: ``requires_autograd=False`` — the pipeline settles under
    ``no_grad`` (no whole-stack graph ever exists) and this credit builds
    each layer's autograd graph alone inside ``compute_pseudo_gradient``
    and releases it before building the next (peak saved bytes = ONE
    layer's graph, never the stack — F5's ratchet). The good/bad contrast
    comes from the **label channel in the input** (``label_dim`` trailing
    features; the negative stream rolls the label one class), NOT from
    the FREE/NUDGED phases — under instantaneous settle those are
    bit-identical at hidden layers (measured 2026-09-07), so a phase
    contrast is structurally starved there.

    Per layer: hidden weights descend a softplus-gated goodness contrast
    (threshold ``contrast_threshold``, Hinton-length stream normalization
    when ``stream_norm``); the readout (last linear) descends local CE on
    its recomputed logits. Every pseudo-gradient is divided by a
    bias-corrected per-element EMA of its squared magnitude (``ema_beta``;
    ``ema_beta=0`` disables) — the probe-confirmed repair for the
    instantaneous-normalization depth collapse
    (``scripts/probes/w2_ema_rung.py``: d4 0.757 vs 0.19 instantaneous,
    raw parity; depth 8 trains for the first time in this class). With
    ``sequential_lr`` > 0 the credit also reproduces Hinton's within-batch
    layer propagation — measured 2026-09-07 as the load-bearing depth
    mechanism (Jacobi ordering collapses d4 to 0.27, d8 to 0.14).

    Supports linear-stack geometries (``FeedforwardGeometry``) and
    ``TransformerGeometry`` (per-layer targets through the credit-owned
    label injection; the head trains local per-position CE). Any other
    topology raises at first use rather than silently mis-recomputing.
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE,)
    requires_autograd: ClassVar[bool] = False

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.local_contrastive()
        self._ema: dict[str, Tensor] = {}
        self._step = 0
        self._step_view: dict[int, nn.Linear] = {}
        self._tf_views: dict[str, Tensor] = {}
        self._tf_label_emb: Tensor | None = None
        self._update_rule: ParameterUpdate | None = None

    def set_update_rule(self, update: ParameterUpdate) -> None:
        """Register the system's update rule (wired by ``compose_system``).

        With a rule registered, ``sequential_lr`` recomputation views use
        the rule's ACTUAL per-parameter displacement (TODO14 §8) instead
        of assuming displacement ≈ step_size — a plain-SGD identity that
        is false for the matrix rules and made a failed
        local_contrastive × Muon/OrthoAdam cell ambiguous.
        """
        self._update_rule = update

    def _sequential_view(self, name: str, weight: Tensor, gw: Tensor) -> Tensor:
        """Post-update weight for within-batch (Hinton) propagation.

        Snapshot-replay through the registered update rule when present;
        the legacy plain-SGD step (``sequential_lr`` × grad) otherwise.
        """
        weight = weight.detach()
        if self._update_rule is None:
            return weight - self.config.sequential_lr * gw
        from computronium.ontology.update import actual_parameter_displacement

        disp = actual_parameter_displacement(self._update_rule, {name: weight}, [gw])
        return weight - disp[name]

    def _stack(self, geometry: Geometry) -> list[nn.Module]:
        layers = getattr(geometry, "_layers", None)
        if not layers:
            msg = (
                "LocalContrastiveCredit requires a linear-stack geometry "
                "(FeedforwardGeometry); the settled activations cannot be "
                "recomputed per layer through this topology"
            )
            raise NotImplementedError(msg)
        return list(layers)

    def _linear_index(self, name: str, k: int) -> int:
        parts = name.split("_")
        if len(parts) >= 3 and parts[0] == "layer" and parts[2] == "weight":
            return int(parts[1])
        return k

    def _recompute_prefix(self, x: Tensor, stack: list[nn.Module], upto: int) -> Tensor:
        """no-grad sweep to layer ``upto``'s input (O(depth) compute, O(1) memory).

        Prefix layers already updated this step (``sequential_lr`` > 0) are
        read from ``_step_view`` so later layers see the propagated input —
        Hinton within-batch ordering.
        """
        with torch.no_grad():
            h = x
            for j, prefix_layer in enumerate(stack[:upto]):
                layer = self._step_view.get(j, prefix_layer)
                h = layer(h)
                if self.config.stream_norm and not isinstance(layer, nn.Linear):
                    h = h / (h.norm(dim=-1, keepdim=True) + 1e-12) * h.shape[-1] ** 0.5
        return h

    def _layer_grad(
        self,
        a_pos: Tensor,
        a_neg: Tensor,
        lin: nn.Linear,
        act: nn.Module | None,
    ) -> Tensor:
        """One layer's graph, built and released inside this call."""
        with torch.enable_grad():
            w = lin.weight.detach().requires_grad_(True)
            bias = lin.bias.detach() if lin.bias is not None else None
            g_pos = torch.nn.functional.linear(a_pos, w, bias)
            g_neg = torch.nn.functional.linear(a_neg, w, bias)
            if act is not None:
                g_pos, g_neg = act(g_pos), act(g_neg)
            loss = torch.nn.functional.softplus(
                self.config.contrast_threshold
                - (g_pos.pow(2).mean() - g_neg.pow(2).mean())
            )
            (gw,) = torch.autograd.grad(loss, w)
        return gw

    def _ema_normalize(self, name: str, gw: Tensor) -> Tensor:
        if self.config.ema_beta <= 0.0:
            return gw
        # Element-wise EMA of gw^2, zeros-warm-started, Adam-style bias
        # correction (ema/(1-beta^t)) — the exact recipe the w2_ema_rung
        # probe confirmed (d4 0.757, d8 0.512 at lr 0.3). A ones-warm-start
        # uncorrected EMA leaves the first ~100 steps mis-normalized (t=1
        # step is raw gw) and destabilizes the high-lr regime the EMA rung
        # exists for; a scalar mean likewise distorts the label-channel
        # columns whose gradient magnitude differs from the data columns.
        sq = gw.detach().pow(2)
        cached = self._ema.get(name)
        ema = (
            self.config.ema_beta * cached + (1 - self.config.ema_beta) * sq
            if cached is not None
            else (1 - self.config.ema_beta) * sq
        )
        self._ema[name] = ema
        bias = 1 - self.config.ema_beta**self._step
        # eps INSIDE the sqrt (probe-exact): near-zero gradients must stay
        # near-zero — an outside eps re-amplifies satisfied-gate ~0 grads
        # into full-size destructive steps (the collapse the EMA rung fixes).
        return gw / (ema / bias + 1e-12).sqrt()

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        if not self._ema:
            return {}
        return {
            "ema": {name: t.detach().clone() for name, t in self._ema.items()},
            "step": {"counter": torch.tensor(self._step)},
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        step_group = state.get("step", {})
        step = step_group.get("counter") if isinstance(step_group, dict) else None
        if not isinstance(step, Tensor):
            msg = "local-contrastive credit state is missing the step counter"
            raise RuntimeError(msg)  # ruff: ignore[type-check-without-type-error] — snapshot protocol precedent
        self._step = int(step.item())
        self._ema = {
            name: tensor.detach().clone()
            for name, tensor in state.get("ema", {}).items()
        }

    def _resolve_layer(
        self, stack: list[nn.Module], i: int
    ) -> tuple[int, nn.Linear, nn.Module | None] | None:
        """(stack index, linear, following activation) for linear number ``i``."""
        count = -1
        for j, layer in enumerate(stack):
            if not isinstance(layer, nn.Linear):
                continue
            count += 1
            if count == i:
                nxt = stack[j + 1] if j + 1 < len(stack) else None
                return j, layer, None if isinstance(nxt, nn.Linear) else nxt
        return None

    def _readout_grad(self, a_pos: Tensor, lin: nn.Linear, y: Tensor) -> Tensor:
        with torch.enable_grad():
            w = lin.weight.detach().requires_grad_(True)
            bias = lin.bias.detach() if lin.bias is not None else None
            logits = torch.nn.functional.linear(a_pos, w, bias)
            (gw,) = torch.autograd.grad(torch.nn.functional.cross_entropy(logits, y), w)
        return gw

    def _augment(self, d: Tensor, lab: Tensor) -> Tensor:
        """Hinton-normalized label-augmented stream: unit DIRECTION, length
        sqrt(dim) — applied to the WHOLE augmented vector for BOTH streams
        (b4 contract; a scale-mismatched negative halves accuracy at d2)."""
        z = torch.cat((d, lab), dim=-1)
        if not self.config.stream_norm:
            return z
        return z / (z.norm(dim=-1, keepdim=True) + 1e-12) * z.shape[-1] ** 0.5

    def _resolve_readout(
        self, geometry: Geometry
    ) -> tuple[list[nn.Module], int, nn.Linear, str] | None:
        """(stack, prefix index, readout linear, bias param name) or None."""
        stack = self._stack(geometry)
        n_linears = sum(isinstance(layer, nn.Linear) for layer in stack)
        resolved = self._resolve_layer(stack, n_linears - 1)
        if resolved is None:
            return None
        stack_idx, lin, _ = resolved
        bias_names = [
            n for n, p in geometry.params.items() if "bias" in n and p is lin.bias
        ]
        if not bias_names:
            return None
        return stack, stack_idx, lin, bias_names[0]

    def compute_bias_pseudo_gradients(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> dict[str, Tensor]:
        """Readout-bias gradient (local CE, raw magnitude × ``readout_scale``).

        The b4/w2_ema_rung recipe trains the readout bias — measured
        2026-09-07 as load-bearing (freezing it collapses d2 0.824 → 0.52,
        d4 0.757 → 0.29). Called by the pipeline after
        ``compute_pseudo_gradient`` so the sequential step-view applies.
        """
        if self.config.readout_scale <= 0.0:
            return {}
        if self._tf_linears(geometry):
            return {}  # transformer head is bias-free — nothing to train
        free_state = states.get(Phase.FREE)
        if free_state is None or free_state.x is None or free_state.y is None:
            return {}
        resolved = self._resolve_readout(geometry)
        if resolved is None:
            return {}
        stack, stack_idx, lin, bias_name = resolved
        x = free_state.x
        label = x[..., -self.config.label_dim :]
        data = x[..., : -self.config.label_dim]
        a_pos = self._recompute_prefix(self._augment(data, label), stack, stack_idx)
        with torch.enable_grad():
            bias = lin.bias.detach().requires_grad_(True)
            logits = torch.nn.functional.linear(a_pos, lin.weight.detach(), bias)
            (gb,) = torch.autograd.grad(
                torch.nn.functional.cross_entropy(logits, free_state.y), bias
            )
        return {bias_name: self.config.readout_scale * gb}

    def compute_pseudo_gradient(  # ruff: ignore[too-many-locals] — protocol axis assembly, kept linear
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        free_state = states.get(Phase.FREE)
        if free_state is None:
            return []
        tf_grads = self._tf_gradient_if_applicable(free_state, geometry)
        if tf_grads is not None:
            return tf_grads
        x = free_state.x
        y = free_state.y
        if x is None or y is None or self.config.label_dim <= 0:
            return []
        stack = self._stack(geometry)
        weight_names = _learnable_weight_names(geometry.params)
        if not weight_names:
            return []

        label = x[..., -self.config.label_dim :]
        data = x[..., : -self.config.label_dim]

        x_pos = self._augment(data, label)
        x_neg = self._augment(data, label.roll(1, 0))
        self._step += 1
        self._step_view = {}
        n_linears = sum(isinstance(layer, nn.Linear) for layer in stack)
        grads: list[Tensor] = []
        for name in weight_names:
            param = geometry.params[name]
            i = self._linear_index(name, len(grads))
            resolved = self._resolve_layer(stack, i)
            if i >= n_linears or resolved is None:
                grads.append(torch.zeros_like(param))
                continue
            stack_idx, lin_i, act_i = resolved
            a_pos = self._recompute_prefix(x_pos, stack, stack_idx)
            a_neg = self._recompute_prefix(x_neg, stack, stack_idx)
            if i == n_linears - 1:  # readout: local CE, b4's separate-readout recipe
                gw = self._readout_grad(a_pos, lin_i, y)
                # Readout rides RAW-magnitude CE gradients: the probe bisection
                # (2026-09-07) shows EMA-normalized or goodness-space readout
                # updates collapse to chance — only raw CE (SGD-style) trains
                # the readout. EMA normalization is for the hidden goodness
                # grads only. ``readout_scale`` folds the probe's separate
                # readout lr (CE x 0.1 vs hidden x 0.3) into the single
                # update-axis lr — one lr cannot serve both gradient scales.
                grads.append(self.config.readout_scale * gw)
                continue
            gw = self._layer_grad(a_pos, a_neg, lin_i, act_i)
            gw = self._ema_normalize(name, gw)
            grads.append(gw)
            if self.config.sequential_lr > 0.0 and i < n_linears - 1:
                # Hinton within-batch propagation: later layers' inputs are
                # formed against this layer's post-update weights (detached
                # view; the real parameters are updated once by the pipeline).
                lin_view = nn.Linear(
                    lin_i.in_features, lin_i.out_features, bias=lin_i.bias is not None
                )
                lin_view.weight = nn.Parameter(
                    self._sequential_view(name, lin_i.weight, gw)
                )
                if lin_i.bias is not None:
                    lin_view.bias = nn.Parameter(lin_i.bias.detach().clone())
                self._step_view[stack_idx] = lin_view
        return grads

    def surrogate_objective(
        self,
        free_state: SystemState,
        nudged_state: SystemState,
        geometry: Geometry,
    ) -> Tensor:
        return torch.tensor(0.0)

    # ---------------------------------------------------------------
    # TransformerGeometry path (W2 P4): per-layer targets with zero
    # global signals. The label enters as a credit-owned embedding
    # injected additively at the embedding output (pos = true next
    # tokens, neg = batch-rolled) — the phase contrast is structurally
    # starved under instantaneous settle, so the contrast lives in the
    # label channel exactly as in the MLP contract. Head trains local
    # per-position CE (raw magnitude, readout_scale) — calibrated, so
    # val CE is reportable. Each weight's graph is built and released
    # alone (O(1) peak); sequential_lr propagates within-batch updates
    # through the recompute, keyed by parameter NAME (transformer
    # weights have no positional index contract).
    # ---------------------------------------------------------------

    _tf_label_emb: Tensor | None

    def _tf_linears(self, geometry: Geometry) -> list[tuple[str, nn.Linear]]:
        from computronium.ontology.geometry import TransformerGeometry

        if not isinstance(geometry, TransformerGeometry):
            return []
        seq: list[tuple[str, nn.Linear]] = [("embed.weight", geometry.embed)]
        for j, block in enumerate(geometry.blocks):
            seq += [
                (f"blocks.{j}.in_proj.weight", block.in_proj),
                (f"blocks.{j}.out_proj.weight", block.out_proj),
                (f"blocks.{j}.ffn1.weight", block.ffn1),
                (f"blocks.{j}.ffn2.weight", block.ffn2),
            ]
        seq.append(("head.weight", geometry.head))
        return seq

    def _tf_weight(self, geometry: Geometry, name: str, lin: nn.Linear) -> Tensor:
        view = self._tf_views.get(name)
        return lin.weight if view is None else view

    def _tf_label_embedding(
        self, vocab: int, d: int, device: torch.device, dtype: torch.dtype
    ) -> Tensor:
        if self._tf_label_emb is None or self._tf_label_emb.shape != (vocab, d):
            gen = torch.Generator(device="cpu").manual_seed(
                zlib.crc32(b"local_contrastive_label_emb")
            )
            emb = torch.empty(vocab, d, dtype=torch.float32).normal_(generator=gen)
            emb /= emb.shape[1] ** 0.5
            self._tf_label_emb = emb.to(device=device, dtype=dtype)
        return self._tf_label_emb

    def _tf_recompute(
        self,
        geometry: Geometry,
        x: Tensor,
        y_lab: Tensor,
        upto: int,
        b: int,
        t: int,
        linears: list[tuple[str, nn.Linear]],
        inject: bool = True,
    ) -> Tensor:
        """no-grad sweep to the input stream of ordered linear ``upto``.

        O(depth) compute, O(1) memory. ``upto == 0`` returns the one-hot
        token matrix (the embedding's input).
        """
        tf = cast("TransformerGeometry", geometry)
        with torch.no_grad():
            if upto == 0:
                onehot = torch.nn.functional.one_hot(x, geometry.config.input_dim)
                return onehot.reshape(b * t, -1).to(tf.embed.weight.dtype)
            d = tf.d_model
            w = {name: self._tf_weight(geometry, name, lin) for name, lin in linears}
            onehot = torch.nn.functional.one_hot(x, geometry.config.input_dim)
            flat = onehot.reshape(b * t, -1).to(w["embed.weight"].dtype)
            h = torch.nn.functional.linear(flat, w["embed.weight"])
            label = self._tf_label_embedding(
                geometry.config.input_dim, d, h.device, h.dtype
            )[y_lab]
            h += tf.pe[:t].reshape(1, t, d).expand(b, t, d).reshape(b * t, d)
            h += label
            # No stream norm here: the blocks' own LayerNorms normalize
            # every deeper input, and a norm on the goodness stream would
            # pin G == 1 for both phases — a structurally zero contrast
            # (measured 2026-09-07: embed/label gradients exactly 0).
            for j, block in enumerate(tf.blocks):
                a1 = torch.nn.functional.layer_norm(
                    h, (d,), block.ln1.weight, block.ln1.bias
                )
                if upto == 1 + 4 * j:  # in_proj's input = a1
                    return a1
                qkv = torch.nn.functional.linear(a1, w[f"blocks.{j}.in_proj.weight"])
                ctx1 = tf._attention(qkv, b, t)
                if upto == 2 + 4 * j:  # out_proj's input = ctx1
                    return ctx1
                h += torch.nn.functional.linear(ctx1, w[f"blocks.{j}.out_proj.weight"])
                a2 = torch.nn.functional.layer_norm(
                    h, (d,), block.ln2.weight, block.ln2.bias
                )
                if upto == 3 + 4 * j:  # ffn1's input = a2
                    return a2
                f1 = torch.nn.functional.gelu(
                    torch.nn.functional.linear(a2, w[f"blocks.{j}.ffn1.weight"])
                )
                if upto == 4 + 4 * j:  # ffn2's input = f1
                    return f1
                h += torch.nn.functional.linear(f1, w[f"blocks.{j}.ffn2.weight"])
            return h  # head's input (upto == last)

    def _tf_layer_grad(
        self,
        geometry: Geometry,
        x: Tensor,
        y_lab: Tensor,
        i: int,
        b: int,
        t: int,
        linears: list[tuple[str, nn.Linear]],
    ) -> Tensor:
        """Goodness-contrast gradient for ordered linear ``i`` (its own
        graph, built and released here)."""
        tf = cast("TransformerGeometry", geometry)
        lin = linears[i][1]
        a_pos = self._tf_recompute(geometry, x, y_lab, i, b, t, linears)
        y_neg = y_lab.view(b, t).roll(1, 0).reshape(b * t)
        a_neg = self._tf_recompute(geometry, x, y_neg, i, b, t, linears)
        with torch.enable_grad():
            w = lin.weight.detach().requires_grad_(True)
            g_pos = torch.nn.functional.linear(a_pos, w)
            g_neg = torch.nn.functional.linear(a_neg, w)
            if i == 0:
                # Goodness excludes pe: the sinusoidal entries (+-1) would
                # swamp the label contrast (pe alone contributes ~1.0 to G,
                # the label ~0.008). pe stays in the recompute stream for
                # the deeper layers; the contrast measures this layer's
                # own output against the (fixed) label injection.
                label_emb = self._tf_label_embedding(
                    geometry.config.input_dim, tf.d_model, a_pos.device, a_pos.dtype
                )
                g_pos += label_emb[y_lab]
                g_neg += label_emb[y_neg]
            elif (i - 1) % 4 == 0:  # in_proj: goodness on attention output
                g_pos = tf._attention(g_pos, b, t)
                g_neg = tf._attention(g_neg, b, t)
            elif i == len(linears) - 1:  # head handled by the readout path
                msg = "head gradients take the readout path"
                raise AssertionError(msg)
            loss = torch.nn.functional.softplus(
                self.config.contrast_threshold
                - (g_pos.pow(2).mean() - g_neg.pow(2).mean())
            )
            (gw,) = torch.autograd.grad(loss, w)
        return gw

    def _tf_readout_grad(
        self,
        geometry: Geometry,
        x: Tensor,
        y: Tensor,
        b: int,
        t: int,
        linears: list[tuple[str, nn.Linear]],
    ) -> Tensor:
        lin = linears[-1][1]
        a = self._tf_recompute(geometry, x, y, len(linears) - 1, b, t, linears)
        with torch.enable_grad():
            w = lin.weight.detach().requires_grad_(True)
            logits = torch.nn.functional.linear(a, w)
            (gw,) = torch.autograd.grad(torch.nn.functional.cross_entropy(logits, y), w)
        return gw

    def _tf_gradient_if_applicable(
        self, free_state: SystemState, geometry: Geometry
    ) -> list[Tensor] | None:
        """Transformer-path dispatch: the label channel is the credit-owned
        injection (label_dim is an MLP-contract knob, unused here); None
        selects the linear-stack path."""
        if not self._tf_linears(geometry):
            return None
        x, y = free_state.x, free_state.y
        if x is None or y is None or x.dim() != 2:
            return []
        return self._tf_gradient(free_state, geometry)

    def _tf_gradient(
        self,
        free_state: SystemState,
        geometry: Geometry,
    ) -> list[Tensor]:
        x = free_state.x
        y = free_state.y
        if x is None or y is None or x.dim() != 2:
            return []
        b, t = x.shape
        y_flat = y.reshape(-1)
        linears = self._tf_linears(geometry)
        n_weight = len(linears) - 1  # head is the readout, not a hidden layer
        self._step += 1
        self._tf_views = {}
        weight_names = _learnable_weight_names(geometry.params)
        name_to_idx = {name: i for i, (name, _) in enumerate(linears)}
        grad_by_name: dict[str, Tensor] = {}
        for name in weight_names:
            i = name_to_idx.get(name)
            if i is None or i >= n_weight:
                grad_by_name[name] = torch.zeros_like(geometry.params[name])
                continue
            gw = self._tf_layer_grad(geometry, x, y_flat, i, b, t, linears)
            grad_by_name[name] = self._ema_normalize(name, gw)
            if self.config.sequential_lr > 0.0:
                self._tf_views[name] = self._sequential_view(
                    name, linears[i][1].weight, gw
                )
        # Head: local per-position CE on the EMA-normalized axis — the
        # MLP raw-CE contract does NOT transfer to the transformer scale
        # (measured 2026-09-07: raw CE grad RMS ~1e-5 vs hidden ~0.65 —
        # a ~5e4 imbalance the readout can never win; EMA normalization
        # puts both on the same unit-RMS step axis, readout_scale sets
        # the readout's share).
        head_name = linears[-1][0]
        if head_name in grad_by_name or head_name in weight_names:
            grad_by_name[head_name] = self.config.readout_scale * self._ema_normalize(
                head_name,
                self._tf_readout_grad(geometry, x, y_flat, b, t, linears),
            )
        # Label embedding stays FIXED (a random label projection): the
        # MLP contract's label channel is a constant one-hot feature —
        # never learned. A learned injection magnitude is a runaway
        # positive feedback (measured 2026-09-07: norm 8 -> 349 in 200
        # steps, CE diverging in lockstep).
        # Pseudo-gradients in the geometry's declared weight order.
        return [
            grad_by_name.get(n, torch.zeros_like(geometry.params[n]))
            for n in weight_names
        ]


class TemporalTraceCredit:
    """Spike-timing correlations (STDP).

    Supports two modes:
    - Rate-coded surrogate: uses settled (pre, post) activity pairs as
      weighted Hebbian correlation. This is the fallback when spike timing
      data is unavailable.
    - Timing-asymmetric STDP: uses per-neuron per-step spike rasters from
      ``SpikeIntegrationDynamics`` to compute eligibility traces (pre/post
      traces) and applies the canonical STDP update:
        Δw ∝ a_plus * post^T @ pre_trace - a_minus * post_trace^T @ pre
      where traces are exponential filters over spike history.
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE,)
    requires_autograd: ClassVar[bool] = False

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.temporal_trace()

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        free_state = states.get(Phase.FREE)
        if free_state is None or free_state.activations is None:
            return []

        acts = _acts_list(free_state.activations)
        if len(acts) < 2:
            return []

        weight_names = _learnable_weight_names(geometry.params)
        if not weight_names:
            return []

        # Check if spike rasters are available for timing-asymmetric STDP
        spike_rasters = getattr(free_state, "spike_rasters", None)
        use_timing_stdp = (
            spike_rasters is not None
            and len(spike_rasters) > 0
            and isinstance(spike_rasters[0], list)
        )

        batch = acts[0].shape[0]
        grads = []

        if use_timing_stdp:
            # Timing-asymmetric STDP using eligibility traces
            # spike_rasters[layer][step] = [batch, neurons] for that layer's output
            tau_pre = getattr(self.config, "tau_pre", 0.9)
            tau_post = getattr(self.config, "tau_post", 0.9)
            a_plus = self.config.a_plus
            a_minus = self.config.a_minus

            # For each weight layer, we need pre and post spike rasters
            # Weight i connects acts[i] (pre) -> acts[i+1] (post)
            # Post-synaptic spikes for weight i: spike_rasters[i] (output of layer i)
            # Pre-synaptic spikes for weight i: spike_rasters[i-1] (output of layer i-1)
            # For i=0 (first layer), pre-synaptic is the input - rate encode it
            for w_idx, name in enumerate(weight_names):
                if w_idx >= len(spike_rasters):
                    grads.append(torch.zeros_like(geometry.params[name]))
                    continue

                post_rasters = spike_rasters[w_idx]  # [step] -> [batch, post_neurons]
                if not post_rasters:
                    grads.append(torch.zeros_like(geometry.params[name]))
                    continue

                # Get pre-synaptic spikes
                if w_idx == 0:
                    # First layer: rate-encode input as pre-synaptic spikes
                    # Input is acts[0] = x, shape [batch, in_dim]
                    # We need to encode it as spikes for each time step
                    # Use the same encoding as STDPLearningRule: sigmoid + Bernoulli
                    x = acts[0]
                    probs = torch.sigmoid(x)
                    # Generate spikes for each time step (same pattern each step for rate coding)
                    pre_rasters = [
                        (torch.rand_like(probs) < probs).float()
                        for _ in range(len(post_rasters))
                    ]
                else:
                    pre_rasters = spike_rasters[w_idx - 1]

                if not pre_rasters or len(pre_rasters) != len(post_rasters):
                    grads.append(torch.zeros_like(geometry.params[name]))
                    continue

                # Compute eligibility traces
                # pre_trace accumulates pre-synaptic spikes with exponential decay
                pre_trace = torch.zeros_like(pre_rasters[0])  # [batch, pre_neurons]
                for pre_spikes in pre_rasters:
                    pre_trace = tau_pre * pre_trace + pre_spikes

                # post_trace accumulates post-synaptic spikes with exponential decay
                post_trace = torch.zeros_like(post_rasters[0])  # [batch, post_neurons]
                for post_spikes in post_rasters:
                    post_trace = tau_post * post_trace + post_spikes

                # STDP update: pot = a_plus * post^T @ pre_trace, dep = a_minus * post_trace^T @ pre
                # We need the final pre and post activity (last time step or average)
                pre_final = pre_rasters[-1]  # [batch, pre_neurons]
                post_final = post_rasters[-1]  # [batch, post_neurons]

                # Potentiation: post^T @ pre_trace -> [post, pre]
                pot = a_plus * (post_final.T @ pre_trace) / batch
                # Depression: post_trace^T @ pre -> [post, pre]
                dep = a_minus * (post_trace.T @ pre_final) / batch

                stdp_grad = -(pot - dep)
                if self.config.homeostatic_scaling:
                    # Synaptic scaling (gain control): pull each incoming
                    # row toward the target norm. Descent on this term is
                    # zero exactly at ||row|| = target — the equilibrium
                    # that stops runaway potentiation (F2 audit).
                    w = geometry.params[name].detach()
                    row_norms = w.norm(dim=1, keepdim=True)
                    scale = w * (
                        1 - self.config.homeostatic_target / (row_norms + 1e-8)
                    )
                    stdp_grad += scale
                grads.append(stdp_grad)
        else:
            # Rate-coded surrogate (fallback)
            for pair, name in zip(
                _weight_acts(weight_names, acts, geometry), weight_names, strict=True
            ):
                if pair is None:
                    grads.append(torch.zeros_like(geometry.params[name]))
                    continue
                pre, post = pair

                # Causal correlation: post^T @ pre -> [out_dim, in_dim] (matches weight shape)
                causal = post.T @ pre / batch
                # Anti-causal: pre^T @ post -> [in_dim, out_dim], transpose for weight shape
                anticausal = pre.T @ post / batch
                anticausal_w = anticausal.T

                # STDP: potentiate causal, depress anti-causal
                # Pseudo-gradient descended: -(a_plus * causal - a_minus * anticausal_w)
                stdp_grad = -(
                    self.config.a_plus * causal - self.config.a_minus * anticausal_w
                )
                grads.append(stdp_grad)

        return grads

    def compute_stdp_window(
        self,
        pre_spikes: Tensor,  # [batch, 1] or [batch] - spike times (unused for window function)
        post_spikes: Tensor,  # [batch, 1] or [batch] - spike times (unused for window function)
        dt: Tensor,  # [n_dt] - time lag grid
    ) -> Tensor:
        """Compute STDP window W(Δt) over the lag grid dt.

        The STDP window is an antisymmetric function of the time lag Δt:
        W(Δt) = A+ exp(-Δt/τ) for Δt > 0 (potentiation),
              = -A- exp(Δt/τ) for Δt < 0 (depression),
              = 0 for Δt = 0.

        The pre_spikes and post_spikes arguments are retained for API consistency
        (e.g., batching multiple spike pairs) but the window function itself
        depends only on the time lag grid dt.

        Returns: Tensor of shape [batch, n_dt] where each row is W(dt).
        """
        # Standard STDP window function evaluated at dt grid
        pos_mask = dt > 0
        neg_mask = dt < 0

        window = torch.zeros_like(dt)
        window[pos_mask] = self.config.a_plus * torch.exp(
            -dt[pos_mask] / self.config.tau
        )
        window[neg_mask] = -self.config.a_minus * torch.exp(
            dt[neg_mask] / self.config.tau
        )

        # Expand to [batch, n_dt] for API consistency (same window for all pairs in batch)
        batch_size = pre_spikes.shape[0] if pre_spikes.ndim > 0 else 1
        return window.expand(batch_size, -1)


class TargetInversionCredit:
    """Propagating local targets (Target Prop) with transpose feedback.

    Output target = one-hot(y). Local targets propagated backward through
    transpose of weight matrices: t_l = t_{l+1} @ W_{l+1}.
    Per-layer pseudo-gradient = (acts_l - t_l)^T @ acts_{l-1} / batch.
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE, Phase.NUDGED)
    requires_autograd: ClassVar[bool] = True

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.target_inversion()

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        nudged_state = states.get(Phase.NUDGED)
        if nudged_state is None or nudged_state.activations is None:
            return []

        acts = _acts_list(nudged_state.activations)
        if len(acts) < 2:
            return []

        weight_names = _learnable_weight_names(geometry.params)
        if not weight_names:
            return []

        # Target at output layer: one-hot of class indices
        y = nudged_state.y
        if y is None:
            return [torch.zeros_like(geometry.params[n]) for n in weight_names]

        n_trans = len(acts) - 1

        # Tile meshes: targets propagate over the assembled blocks, grads
        # scattered to per-edge weights (R11.1.4).
        if _block_transition_acts(acts, geometry) is not None:
            blocks = geometry.assemble_blocks(geometry.params)
            targets: list[Tensor | None] = [None] * len(acts)
            targets[-1] = torch.nn.functional.one_hot(
                y, num_classes=acts[-1].shape[-1]
            ).float()
            batch = acts[0].shape[0]
            for i in range(n_trans - 1, -1, -1):
                nxt = targets[i + 1]
                targets[i] = nxt @ blocks[i] if nxt is not None else None
            block_grads = [
                (acts[i + 1] - targets[i + 1]).T @ acts[i] / batch
                if targets[i + 1] is not None
                else torch.zeros(acts[i + 1].shape[-1], acts[i].shape[-1])
                for i in range(n_trans)
            ]
            return geometry.scatter_block_grads(block_grads)

        targets = _propagate_targets(acts, y, weight_names[:n_trans], geometry)
        pairs = _weight_acts(weight_names, acts, geometry)

        # Layer-local deltas and pseudo-gradients
        grads = []
        for i, name in enumerate(weight_names):
            pair = pairs[i]
            if pair is None or i >= n_trans:
                # Surplus/ragged weights (recurrent self-connections, tile
                # meshes) receive no propagated target — zeros, not
                # fabricated signal.
                grads.append(torch.zeros_like(geometry.params[name]))
                continue
            pre, post = pair
            tgt = targets[i + 1]
            if tgt is None:
                grads.append(torch.zeros_like(geometry.params[name]))
                continue
            delta = post - tgt  # [batch, out]
            # pseudo_grad = delta^T @ pre / batch -> [out, in]
            grad = delta.T @ pre / pre.shape[0]
            grads.append(grad)

        return grads

    def surrogate_objective(
        self,
        free_state: SystemState,
        nudged_state: SystemState,
        geometry: Geometry,
    ) -> Tensor:
        """Sum of layer-local target matching errors."""
        nudged_acts = _acts_list(nudged_state.activations)
        if not nudged_acts or nudged_state.y is None:
            return torch.tensor(0.0)
        y = nudged_state.y
        weight_names = _learnable_weight_names(geometry.params)
        targets = _propagate_targets(nudged_acts, y, weight_names, geometry)
        total = torch.tensor(0.0, device=nudged_acts[-1].device)
        for i in range(1, len(nudged_acts)):
            tgt = targets[i]
            if tgt is None:
                continue
            delta = nudged_acts[i] - tgt
            total = total + (delta**2).mean()  # ruff: ignore[non-augmented-assignment]
        return total


class HomeostaticCredit:
    """Homeostatic credit assignment (autonomous Lipschitz scaling).

    Per-layer scaling to keep activation norms near homeostatic_target.
    Pseudo-gradient: (mean|post| - target) * W / |W|_F (directional).
    """

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE, Phase.NUDGED)
    requires_autograd: ClassVar[bool] = False

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.homeostatic()

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        free_state = states.get(Phase.FREE)
        if free_state is None or free_state.activations is None:
            return []

        acts = _acts_list(free_state.activations)
        if len(acts) < 2:
            return []

        weight_names = _learnable_weight_names(geometry.params)
        if not weight_names:
            return []

        target = self.config.homeostatic_target
        grads = []
        for pair, name in zip(
            _weight_acts(weight_names, acts, geometry), weight_names, strict=True
        ):
            if pair is None:
                grads.append(torch.zeros_like(geometry.params[name]))
                continue
            _, post = pair
            weight = geometry.params[name]  # [out_dim, in_dim]

            # Mean post-activation norm (L2 across features, then mean across batch)
            post_norm = post.norm(dim=1).mean()  # scalar
            # Error from target
            err = post_norm - target
            # Direction: scale W by error, normalized by Frobenius norm
            weight_norm = weight.norm()
            if weight_norm > 0:
                grad = err * weight / weight_norm
            else:
                grad = torch.zeros_like(weight)
            grads.append(grad)

        return grads


class GradientCredit:
    """Standard backprop credit (for comparison)."""

    phases: ClassVar[tuple[Phase, ...]] = (Phase.FREE, Phase.NUDGED)
    requires_autograd: ClassVar[bool] = True

    def __init__(self, config: CreditAssignmentConfig | None = None):
        self.config = config or CreditAssignmentConfig.gradient()

    def compute_pseudo_gradient(
        self,
        states: Mapping[Phase, SystemState],
        loss: Tensor | None,
        geometry: Geometry,
    ) -> list[Tensor]:
        """Compute true gradients via autograd on nudged state loss."""
        if loss is None:
            return []

        weight_names = _learnable_weight_names(geometry.params)
        params = [geometry.params[n] for n in weight_names]
        grads = torch.autograd.grad(
            loss, params, retain_graph=False, create_graph=False, allow_unused=True
        )
        detached = [n for n, g in zip(weight_names, grads, strict=True) if g is None]
        if detached:
            raise RuntimeError(
                f"GradientCredit: no gradient reached {detached}. The loss "
                "graph does not touch every learnable weight — a dynamics "
                "that detaches activations would silently degrade learning "
                "to the reached layers only. Zero-filling hides that failure."
            )
        return list(grads)

    def surrogate_objective(
        self,
        free_state: SystemState,
        nudged_state: SystemState,
        geometry: Geometry,
    ) -> Tensor:
        """The nudged loss is the surrogate objective for true gradients."""
        loss = nudged_state.loss
        if isinstance(loss, Tensor):
            return loss
        return torch.tensor(0.0)


# Alias for backwards compatibility
BackpropCredit = GradientCredit
