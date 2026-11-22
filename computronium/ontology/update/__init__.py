"""Layer 5: ParameterUpdate — The Optimization Rule."""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import (
    Mapping,  # ruff: ignore[typing-only-standard-library-import] (used at runtime for isinstance)
)
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol, cast, runtime_checkable

import torch
from torch import Tensor

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.ontology._registry import ImplementationRegistry
from computronium.ontology.update._base import (
    AdamStateMixin,
    BufferManager,
    ClippingMixin,
    LionStateMixin,
    SecondMomentMixin,
    StatefulUpdate,
    StateSnapshotMixin,
)
from computronium.ontology.utils import _learnable_weight_names, apply_pseudo_gradients

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.ontology.geometry import Geometry


# ============================================================
# ParameterUpdate Configuration
# ============================================================

type StepSemantics = Literal["gradient_relative", "per_element_displacement"]

# TODO12b R5 (H1/H4): update rules carry incompatible step-size
# semantics. `gradient_relative` rules multiply step_size by a
# gradient-scale quantity; `per_element_displacement` rules normalize
# magnitude so step_size IS the per-element displacement (‖Δθ‖ =
# step_size·√n per tensor). An lr grid borrowed across the boundary is
# a category error (V1's "noise floor" and H4's Muon "divergence" were
# both exactly this).
_STEP_SEMANTICS: dict[str, StepSemantics] = {
    "euclidean": "gradient_relative",
    "adam": "per_element_displacement",
    "local_adam": "per_element_displacement",
    "ortho_adam": "per_element_displacement",
    "unit_rms": "per_element_displacement",
    "mean_norm": "per_element_displacement",
    "riemannian_orthogonal": "per_element_displacement",
    "muon": "per_element_displacement",
    "lion": "per_element_displacement",
    "spectral_constrained": "per_element_displacement",
    "natural_gradient": "per_element_displacement",
    "adafactor": "per_element_displacement",
    "quantized_adam": "per_element_displacement",
    "schedule_free": "per_element_displacement",
}


@dataclass(frozen=True, slots=True)  # ruff: ignore[too-many-public-methods]
class ParameterUpdateConfig:
    """Configuration for parameter update rule.

    Attributes:
        update_type: "riemannian_orthogonal", "spectral_constrained",
            "mean_norm", "elastic_consolidation", "euclidean"
        step_size: Learning rate
        momentum: Momentum coefficient (for euclidean)
        ortho_steps: Newton-Schulz iterations (for riemannian)
        spectral_norm: Target spectral norm (for spectral_constrained)
        fisher_damping: Damping for natural gradient
        ewc_lambda: EWC regularization strength
        grad_clip: Gradient clipping norm (for euclidean)
        handles_own_clipping: Whether the update rule implements its own
            gradient clipping (pipeline will skip global-norm clip if True)
    """

    update_type: str
    step_size: float
    momentum: float
    ortho_steps: int
    spectral_norm: float
    fisher_damping: float
    ewc_lambda: float
    grad_clip: float = 1.0
    beta2: float = 0.999
    eps: float = 1e-8
    ortho_lr: float = 0.003
    role_names: tuple[str, ...] = ()
    sub_rules: RoleSplitSpec | None = None
    handles_own_clipping: bool = False
    si_lambda: float = 0.1
    cascade_levels: int = 8
    cascade_up: float = 0.05
    cascade_down: float = 0.01
    von_init_var: float = 1.0
    von_min_var: float = 1e-8
    factor_decay: float = 0.999
    quant_block: int = 256
    schedule_beta: float = 0.9

    def __post_init__(self) -> None:
        object.__setattr__(self, "role_names", tuple(self.role_names))

    @property
    def step_semantics(self) -> StepSemantics:
        """What ``step_size`` displaces (see ``_STEP_SEMANTICS``)."""
        return _STEP_SEMANTICS.get(self.update_type, "gradient_relative")

    @classmethod
    def euclidean(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        ortho_steps: int = 0,
        spectral_norm: float = 1.0,
        fisher_damping: float = 1e-3,
        ewc_lambda: float = 1000.0,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Euclidean SGD update config."""
        return cls(
            update_type="euclidean",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=ortho_steps,
            spectral_norm=spectral_norm,
            fisher_damping=fisher_damping,
            ewc_lambda=ewc_lambda,
            grad_clip=grad_clip,
            handles_own_clipping=True,
        )

    @classmethod
    def riemannian_orthogonal(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        ortho_steps: int = 0,
        spectral_norm: float = 1.0,
        fisher_damping: float = 1e-3,
        ewc_lambda: float = 1000.0,
    ) -> ParameterUpdateConfig:
        """Riemannian-orthogonal (Muon-class) update config.

        ``ortho_steps == 0`` (default) selects the EXACT SVD polar factor —
        full-spectrum whitening, the configuration under which D13's
        FF×Muon lift and D15's depth-frontier claims are measured. Values
        > 0 select Newton–Schulz iteration (Muon's cheaper recipe, partial
        whitening): measured at width 32 it PRESERVES the BP×Muon lift but
        COLLAPSES FF×Muon (0.29 vs 0.838) — the local-credit lift is
        whitening-driven, so NS is an opt-in variant, never the default.
        """
        return cls(
            update_type="riemannian_orthogonal",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=ortho_steps,
            spectral_norm=spectral_norm,
            fisher_damping=fisher_damping,
            ewc_lambda=ewc_lambda,
            handles_own_clipping=False,
        )

    @classmethod
    def muon(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        ortho_steps: int = 0,
        spectral_norm: float = 1.0,
        fisher_damping: float = 1e-3,
        ewc_lambda: float = 1000.0,
    ) -> ParameterUpdateConfig:
        """Muon update config (alias of the exact-polar Muon-class rule).

        Registry alias for ``riemannian_orthogonal`` with the Muon name,
        so the coverage grid can name the axis by its literature identity.
        Same NS caveat: ``ortho_steps > 0`` is an opt-in variant.
        """
        return cls(
            update_type="muon",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=ortho_steps,
            spectral_norm=spectral_norm,
            fisher_damping=fisher_damping,
            ewc_lambda=ewc_lambda,
            handles_own_clipping=False,
        )

    @classmethod
    def spectral_constrained(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        ortho_steps: int = 5,
        spectral_norm: float = 1.0,
        fisher_damping: float = 1e-3,
        ewc_lambda: float = 1000.0,
    ) -> ParameterUpdateConfig:
        return cls(
            update_type="spectral_constrained",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=ortho_steps,
            spectral_norm=spectral_norm,
            fisher_damping=fisher_damping,
            ewc_lambda=ewc_lambda,
            handles_own_clipping=False,
        )

    @classmethod
    def mean_norm(
        cls,
        *,
        # The rule normalizes every element to unit magnitude, so its step is
        # an absolute displacement, not a gradient-scaled lr: 1e-2 diverged to
        # chance (0.101) on MNIST at 375 batches; 1e-3 measured 0.923 in the
        # same box (2026-11-18).
        step_size: float = 1e-3,
        momentum: float = 0.9,
        ortho_steps: int = 5,
        spectral_norm: float = 1.0,
        fisher_damping: float = 1e-3,
        ewc_lambda: float = 1000.0,
    ) -> ParameterUpdateConfig:
        return cls(
            update_type="mean_norm",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=ortho_steps,
            spectral_norm=spectral_norm,
            fisher_damping=fisher_damping,
            ewc_lambda=ewc_lambda,
            handles_own_clipping=False,
        )

    @classmethod
    def unit_rms(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Unit-RMS momentum config (the magnitude-only ladder rung)."""
        return cls(
            update_type="unit_rms",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            handles_own_clipping=False,
        )

    @classmethod
    def local_adam(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        beta2: float = 0.999,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Per-tensor scalar-second-moment Adam config (LAMB-style)."""
        return cls(
            update_type="local_adam",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=beta2,
            handles_own_clipping=False,
        )

    @classmethod
    def elastic_consolidation(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        ortho_steps: int = 5,
        spectral_norm: float = 1.0,
        fisher_damping: float = 1e-3,
        ewc_lambda: float = 1000.0,
    ) -> ParameterUpdateConfig:
        return cls(
            update_type="elastic_consolidation",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=ortho_steps,
            spectral_norm=spectral_norm,
            fisher_damping=fisher_damping,
            ewc_lambda=ewc_lambda,
            handles_own_clipping=False,
        )

    @classmethod
    def natural_gradient(
        cls,
        *,
        step_size: float = 1e-3,
        momentum: float = 0.9,
        fisher_damping: float = 1e-3,
        beta2: float = 0.999,
        eps: float = 1e-8,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Natural gradient update config (Fisher-geometry preconditioning).

        Implements the Amari natural gradient: Δθ = −lr · F⁻¹ · g
        where F is the Fisher Information Matrix. This uses a diagonal
        Fisher approximation with Tikhonov damping for numerical stability.

        Distinct from ``mean_norm`` (per-tensor mean-|g| normalization):
        natural gradient uses the actual diagonal Fisher (E[g²]) as the
        preconditioner, not a uniform per-tensor scale. The D14 regime
        showed this distinction is load-bearing for deep local learning.
        """
        return cls(
            update_type="natural_gradient",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=fisher_damping,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=beta2,
            eps=eps,
            handles_own_clipping=True,
        )

    @classmethod
    def adam(
        cls,
        *,
        step_size: float = 1e-3,
        momentum: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Adam update config.

        ``momentum`` is β1 (first-moment decay), ``beta2`` the
        second-moment decay, ``eps`` the denominator floor. Distinct from
        ``euclidean`` (plain SGD + momentum): the per-coordinate
        second-moment normalization is a different optimizer family, not a
        step-size variant — the D14 jpc-faithful regime showed it is
        load-bearing for deep local learning, and the D16 coverage map
        never swept it (a known instrument gap).
        """
        return cls(
            update_type="adam",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=beta2,
            eps=eps,
            handles_own_clipping=True,
        )

    @classmethod
    def lion(
        cls,
        *,
        step_size: float = 1e-3,
        momentum: float = 0.9,
        beta2: float = 0.99,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Lion (Chen et al. 2023) update config: sign of the momentum
        interpolant.

        ``update = sign(β1·m + (1−β1)·g)``, then ``m ← β2·m + (1−β2)·g``
        (β2 > β1; no bias correction, no second moment — one momentum
        buffer, O(1)-memory). ``momentum`` is β1, ``beta2`` is β2.

        NOTE: Lion's canonical "3–10× Adam's LR" guidance does NOT
        transfer to local pseudo-gradients — measured 2026-09-07 (mnist
        ff, local_goodness, 30 batches): peak at ADAM-EQUAL lr (1e-3 →
        0.781 vs Adam 1e-3 → 0.739); collapses at ≥1e-2 (0.09) and
        degrades below 3e-4. Sign steps are unit-norm per coordinate, so
        the effective displacement is lr-driven and Adam's adaptive
        shrinkage is absent — start at the Adam-calibrated lr and sweep
        DOWN. Research role (TODO14 I(C,U)): per-coordinate SIGN
        binarization is a third optimizer class between Adam's per-
        coordinate rescale (diverges on EMA-normalized local pseudo-
        gradients) and Muon's orthogonalization (rescues them) — the W0
        transformer cell discriminates "magnitude discarding" vs
        "normalization-ratio" as the blowup mechanism; the W1 ladder
        reads its credit-recovery fingerprint. Note also: sign steps are
        global-clip-invariant above zero — ``grad_clip`` only guards
        exact-zero/non-finite gradients here.
        """
        return cls(
            update_type="lion",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=beta2,
            handles_own_clipping=True,
        )

    @classmethod
    def ortho_adam(
        cls,
        *,
        step_size: float = 1e-3,
        ortho_lr: float = 0.003,
        momentum: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
        grad_clip: float = 1.0,
        ortho_steps: int = 0,
    ) -> ParameterUpdateConfig:
        """OrthoAdam (orthogonalized Adam) update config.

        Adam moments with bias correction; matrix-shaped first-moment
        directions are orthogonalized (SVD polar factor, Muon's recipe)
        before the step, rescaled to the Adam step magnitude; vector
        params keep plain Adam. First measured in the learning-algorithm
        hunt (2026-09-05): it beats BOTH parents on mlp (0.930 vs Muon
        0.919 / Adam 0.892), attention (0.911 vs 0.900/0.874), and
        lattice (0.924 vs 0.905/0.895) at the D16 regime, and beats Adam
        on graph (0.411 vs 0.332, still below Muon 0.433) — the first
        update rule that dominates the coverage map's headline cells.
        ``step_size`` is the vector-param lr; ``ortho_lr`` the
        matrix-direction lr (calibrated on mlp across {1e-3, 3e-3,
        1e-2}). ``ortho_steps == 0`` (default) keeps the exact SVD polar
        factor — the configuration of record for D15/D16; ``>0`` selects
        Newton–Schulz iteration (Muon's cheaper recipe) — probe before
        quoting: the D13 whitening lesson says NS may not preserve
        local-credit lifts.
        """
        return cls(
            update_type="ortho_adam",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=ortho_steps,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=beta2,
            eps=eps,
            ortho_lr=ortho_lr,
            handles_own_clipping=True,
        )

    @classmethod
    def role_split(
        cls,
        *,
        step_size: float = 0.01,
        momentum: float = 0.9,
        grad_clip: float = 1.0,
        role_names: tuple[str, ...] = ("readout",),
        on_role: ParameterUpdateConfig | None = None,
        other: ParameterUpdateConfig | None = None,
    ) -> ParameterUpdateConfig:
        """Role-split dispatcher config (X-USU-001 hybrid rule).

        The declared default is the X-USU-001 winner: ``on_role`` is Muon
        (orthogonalized) and ``other`` is Euclidean, with ``role_names`` naming
        the readout. The token ``"readout"`` is resolved by
        :class:`RoleSplitUpdate` against the composed geometry's output
        dimension, because a factory cannot know a parameter name before the
        geometry exists.
        """
        on_role = on_role or cls.riemannian_orthogonal(
            step_size=step_size, momentum=momentum
        )
        other = other or cls.euclidean(
            step_size=step_size, momentum=momentum, grad_clip=grad_clip
        )
        return cls(
            update_type="role_split",
            step_size=on_role.step_size,
            momentum=on_role.momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            role_names=tuple(role_names),
            sub_rules=RoleSplitSpec(on_role=on_role, other=other),
            handles_own_clipping=False,
        )

    @classmethod
    def synaptic_intelligence(
        cls,
        *,
        step_size: float = 1e-2,
        si_lambda: float = 0.1,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Synaptic Intelligence: the penalty lifted into an update rule."""
        return cls(
            update_type="synaptic_intelligence",
            step_size=step_size,
            momentum=0.9,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            si_lambda=si_lambda,
            handles_own_clipping=False,
        )

    @classmethod
    def cascade_synapse(
        cls,
        *,
        step_size: float = 1e-2,
        cascade_levels: int = 8,
        cascade_up: float = 0.05,
        cascade_down: float = 0.01,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Benna–Fusi cascade: a metaplastic multi-level state per parameter."""
        return cls(
            update_type="cascade_synapse",
            step_size=step_size,
            momentum=0.9,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            cascade_levels=cascade_levels,
            cascade_up=cascade_up,
            cascade_down=cascade_down,
            handles_own_clipping=False,
        )

    @classmethod
    def bayesian_online(
        cls,
        *,
        step_size: float = 0.01,
        von_init_var: float = 1.0,
        von_min_var: float = 1e-8,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """VON: an online diagonal Gaussian posterior per parameter."""
        return cls(
            update_type="bayesian_online",
            step_size=step_size,
            momentum=0.9,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            von_init_var=von_init_var,
            von_min_var=von_min_var,
            handles_own_clipping=False,
        )

    @classmethod
    def adafactor(
        cls,
        *,
        step_size: float = 1e-3,
        momentum: float = 0.9,
        factor_decay: float = 0.999,
        eps: float = 1e-8,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Adafactor: a factored row × column second moment."""
        return cls(
            update_type="adafactor",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=0.999,
            factor_decay=factor_decay,
            eps=eps,
            handles_own_clipping=False,
        )

    @classmethod
    def quantized_adam(
        cls,
        *,
        step_size: float = 1e-3,
        momentum: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
        quant_block: int = 256,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """8-bit Adam: blockwise-quantized first and second moments."""
        return cls(
            update_type="quantized_adam",
            step_size=step_size,
            momentum=momentum,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=beta2,
            eps=eps,
            quant_block=quant_block,
            handles_own_clipping=False,
        )

    @classmethod
    def schedule_free(
        cls,
        *,
        step_size: float = 1e-3,
        schedule_beta: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
        grad_clip: float = 1.0,
    ) -> ParameterUpdateConfig:
        """Schedule-free AdamW: the averaged sequence iterate is the step."""
        return cls(
            update_type="schedule_free",
            step_size=step_size,
            momentum=schedule_beta,
            ortho_steps=0,
            spectral_norm=1.0,
            fisher_damping=1e-3,
            ewc_lambda=1000.0,
            grad_clip=grad_clip,
            beta2=beta2,
            eps=eps,
            schedule_beta=schedule_beta,
            handles_own_clipping=False,
        )

    @classmethod
    def hyperparameters(cls, _primitive_name: str = "") -> dict[str, object]:
        """Hyperparameter ranges owned by the parameter_update axis.

        These are the knobs the update config reads. The sweep unions the
        hyperparameters() of all primitives named by a coordinate.

        Args:
            primitive_name: The specific update primitive name for availability predicates.
        """
        from computronium.experiment.legality.dsl import expr_from_string

        # EWC/SI/cascade/VON need wider step_size domain: they reach 0.1x at 0.3
        step_domain = (1e-5, 1.0, "log") if _primitive_name in (
            "elastic_consolidation",
            "synaptic_intelligence",
            "cascade_synapse",
            "bayesian_online",
        ) else (1e-5, 0.1, "log")

        return {
            "step_size": {"domain": step_domain},
            "momentum": {"domain": (0.0, 0.99, "linear")},
            "ortho_steps": {
                "domain": (0, 10, "int"),
                "availability": expr_from_string(
                    'update in ["riemannian_orthogonal", "muon", "ortho_adam"]'
                ),
            },
            "spectral_norm": {
                "domain": (0.1, 10.0, "log"),
                "availability": expr_from_string('update == "spectral_constrained"'),
            },
            "fisher_damping": {
                "domain": (1e-6, 1.0, "log"),
                "availability": expr_from_string(
                    'update in ["natural_gradient", "elastic_consolidation"]'
                ),
            },
            "ewc_lambda": {
                "domain": (1e-1, 1e4, "log"),
                "availability": expr_from_string('update == "elastic_consolidation"'),
            },
            "grad_clip": {"domain": (0.1, 10.0, "log")},
            "beta2": {
                "domain": (0.9, 0.9999, "linear"),
                "availability": expr_from_string(
                    'update in ["adam", "local_adam", "ortho_adam", "lion"]'
                ),
            },
            "eps": {
                "domain": (1e-10, 1e-4, "log"),
                "availability": expr_from_string(
                    'update in ["adam", "local_adam", "ortho_adam", "lion"]'
                ),
            },
            "ortho_lr": {
                "domain": (1e-5, 1.0, "log"),
                "availability": expr_from_string('update == "ortho_adam"'),
            },
        }


# ============================================================
# Role-split sub-rule pair
# ============================================================


@dataclass(frozen=True, slots=True)
class RoleSplitSpec:
    """Sub-rule pair for ``update_type="role_split"`` (X-USU-001 hybrid).

    Attributes:
        on_role: Rule applied to the parameters named in
            ``ParameterUpdateConfig.role_names``.
        other: Rule applied to every other learnable weight.
    """

    on_role: ParameterUpdateConfig
    other: ParameterUpdateConfig

    @classmethod
    def coerce(cls, obj: RoleSplitSpec | Mapping[str, object]) -> RoleSplitSpec:
        """Accept a spec or its ``dataclasses.asdict`` form (ledger/spec round-trip)."""
        if isinstance(obj, RoleSplitSpec):
            return obj
        return cls(
            on_role=ParameterUpdateConfig(**obj["on_role"]),  # type: ignore[arg-type]
            other=ParameterUpdateConfig(**obj["other"]),  # type: ignore[arg-type]
        )


# ============================================================
# ParameterUpdate Protocol
# ============================================================


@runtime_checkable
class ParameterUpdate(Protocol):
    """How pseudo-gradients translate into physical weight changes (ΔW).

    Maps the pseudo-gradient tensor (from CreditAssignment) to actual
    parameter deltas. The five canonical types:
    - RiemannianOrthogonal: Muon-style orthogonal updates
    - SpectralConstrained: Lipschitz-bounded updates
    - MeanNorm: mean-magnitude-normalized gradient step (NOT Fisher; A0 verdict)
    - ElasticConsolidation: EWC-style importance-weighted updates
    - Euclidean: Standard SGD/Adam in flat space

    The update is applied to the Geometry's parameters.
    """

    config: ParameterUpdateConfig

    @abstractmethod
    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        """Compute parameter updates from pseudo-gradients.

        Args:
            params: Current parameters (name -> tensor)
            pseudo_grads: Pseudo-gradients from CreditAssignment
            geometry: Network topology (for layer-wise adaptation)

        Returns:
            Updated parameters (name -> tensor)
        """
        ...


def actual_parameter_displacement(
    update: StatefulUpdate,
    params: dict[str, Tensor],
    pseudo_grads: list[Tensor],
    geometry: Geometry | None = None,
    bias_grads: dict[str, Tensor] | None = None,
) -> dict[str, Tensor]:
    """The optimizer-induced per-parameter change, WITHOUT consuming
    optimizer state (TODO14 §8 / W2: ``sequential_lr`` recomputation
    views assumed displacement ≈ step_size — a plain-SGD identity that
    is false for the matrix rules (Muon orthogonalizes the momentum,
    OrthoAdam rescales to the Adam norm), leaving a failed
    local_contrastive × Muon/OrthoAdam cell ambiguous. The recompute
    view must use the ACTUAL displacement).

    Snapshot-replay: the update rule's state is snapshotted via the
    snapshot protocol (``get_state``/``load_state`` — all rules expose
    momentum buffers AND step counters), ``step`` runs on the requested
    parameter subset, and the state is restored. Per-parameter update
    state is independent (momentum/moments keyed by name), so a
    single-parameter replay is exact; a rule with cross-parameter
    coupling (global-norm clip over the full stack) must be called with
    the full grad list, or configured with ``grad_clip=0`` for
    per-layer replays.

    Returns:
        Displacement per requested weight name (``new - old``).
    """
    snapshot = update.get_state()
    try:
        new_params = update.step(params, pseudo_grads, geometry, bias_grads)
    finally:
        update.load_state(snapshot)
    return {
        name: new_params[name] - params[name] for name in params if name in new_params
    }


_UPDATE_REGISTRY = ImplementationRegistry[ParameterUpdate]("update")
_UPDATE_REGISTRY.add_discovery_package("computronium.ontology.update")


def update_backend[T: ParameterUpdate](
    *update_types: str,
) -> Callable[[type[T]], type[T]]:
    """Register a ParameterUpdate implementation under its ``update_type`` keys.

    The table used to be hand-kept at the bottom of this module, which is
    how ``NaturalGradientUpdate`` shipped with a config factory and a
    primitive spec but no dispatch entry — ``update_from_config`` raised
    for a documented update type, and a test grew a special case to
    instantiate the class directly instead of fixing it (TODO34 §5.4).
    Deriving the table from the class declarations makes that state
    unrepresentable, and the pairing with ``ParameterUpdateConfig``'s
    factories is proved by ``tests/property/test_registry_completeness_lock.py``.
    """
    return _UPDATE_REGISTRY.register(*update_types)


@update_backend("euclidean")
class EuclideanUpdate(BufferManager, ClippingMixin, StateSnapshotMixin):
    """Standard Euclidean update: plain SGD (optionally with momentum).

    Not Adam — the per-coordinate second-moment family is
    :class:`AdamUpdate`. The ParameterUpdate Protocol docstring's
    "SGD/Adam" phrasing refers to the update *shapes* both realize
    (ΔW = f(∇) in flat space), not to the same algorithm.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="EuclideanUpdate",
        reference_equations="vanilla SGD with optional heavy-ball momentum; Polyak (1964), Sutskever et al. (2013)",
        deviations_from_literature=(
            "global-norm grad_clip (clip_grad_norm_ semantics) preserving "
            "relative per-parameter magnitudes",
            "per_element_displacement sibling rules exist — step_size "
            "semantics are gradient_relative here (lr × gradient-scale)",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · (momentum buffer v with v ← μv + g), global-norm clipped",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "momentum", "grad_clip"),
        validated_limits=(
            "the 5-D benchmark baseline across all credit families; "
            "first-step displacement linear in step_size (calibration "
            "identity used by the 5.1 mechanistic study)",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.euclidean()
        self._momentum_buffers: dict[str, Tensor] = {}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            if self.config.momentum > 0:
                buf = self._get_buffer(
                    self._momentum_buffers, name, param, "Momentum buffer"
                )
                buf.mul_(self.config.momentum).add_(grad)
                self._momentum_buffers[name] = buf
                return param - self.config.step_size * buf
            return param - self.config.step_size * grad

        return apply_pseudo_gradients(
            params,
            self._clip(list(pseudo_grads), self.config.grad_clip),
            apply,
            bias_grads,
        )

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        """Snapshot protocol: named groups of state tensors (clones)."""
        return self._snapshot_momentum()

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_momentum(state)


@update_backend("unit_rms")
class UnitRMSUpdate(BufferManager, StateSnapshotMixin):
    """Unit-RMS momentum: the magnitude-only ladder rung (TODO12 A1).

    The EMA momentum buffer is normalized to unit RMS per tensor —
    Muon's step-scale control with NO orthogonalization. The decisive
    rung of the magnitude-vs-direction ladder: UnitRMS ≈ Muon on the
    fragile cells ⇒ magnitude is the whole story; UnitRMS < Muon ⇒
    orthogonalization carries direction signal beyond scale. Optimizer
    state is system-scoped (fail-loud reuse, Euclidean precedent).
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="UnitRMSUpdate",
        reference_equations="internal magnitude-only ladder rung (TODO12 A1); Muon's step-scale control without orthogonalization",
        deviations_from_literature=(
            "EMA momentum buffer normalized to unit RMS PER TENSOR — "
            "magnitude-only: no whitening, no direction signal",
            "the decisive magnitude-vs-direction rung: UnitRMS ≈ Muon on "
            "fragile cells ⇒ magnitude suffices; UnitRMS < Muon ⇒ "
            "orthogonalization carries direction",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · buf / RMS(buf), buf ← μ·buf + g",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "momentum"),
        validated_limits=("TODO12 magnitude-vs-direction ladder cells",),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.unit_rms()
        self._momentum_buffers: dict[str, Tensor] = {}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            buf = self._get_buffer(
                self._momentum_buffers, name, param, "Momentum buffer"
            )
            buf.mul_(self.config.momentum).add_(grad)
            self._momentum_buffers[name] = buf
            if self.config.momentum <= 0:
                buf = grad
            rms = buf.square().mean().sqrt().add_(1e-8)
            return param - self.config.step_size * buf / rms

        return apply_pseudo_gradients(params, list(pseudo_grads), apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_momentum()

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_momentum(state)


@update_backend("local_adam")
class LocalAdamUpdate(BufferManager, AdamStateMixin):
    """Per-tensor scalar-second-moment Adam (LAMB-style; RESEARCH4 A1 rung).

    ``u = m̂ / sqrt(mean(v̂))`` — the denominator is ONE scalar per
    tensor, not per-coordinate: a local second-moment normalizer that
    preserves within-tensor relative gradient structure (unlike Adam).
    Optimizer state is system-scoped (fail-loud reuse, Adam precedent).
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="LocalAdamUpdate",
        reference_equations="LAMB-style scalar-second-moment variant (RESEARCH4 A1 rung); You et al. (2020) for the LAMB family",
        deviations_from_literature=(
            "denominator is ONE scalar per tensor (mean of v̂), not "
            "per-coordinate — preserves within-tensor relative gradient "
            "structure",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · m̂ / (sqrt(mean(v̂)) + ε), standard Adam moment updates with bias correction",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "momentum (β1)", "beta2", "eps"),
        validated_limits=("RESEARCH4 A1 local-normalizer rung cells",),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.local_adam()
        self._m: dict[str, Tensor] = {}
        self._v: dict[str, Tensor] = {}
        self._t = 0

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        self._t += 1
        beta1 = self.config.momentum
        beta2 = self.config.beta2
        bias1 = 1 - beta1**self._t
        bias2 = 1 - beta2**self._t

        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            m = self._get_buffer(self._m, name, param, "LocalAdam state")
            v = self._get_buffer(self._v, name, param, "LocalAdam state")
            m.mul_(beta1).add_(grad, alpha=1 - beta1)
            v.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
            m_hat = m / bias1
            v_hat = v / bias2
            denom = v_hat.mean().sqrt().add_(self.config.eps)
            return param - self.config.step_size * m_hat / denom

        return apply_pseudo_gradients(params, list(pseudo_grads), apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_adam()

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_adam(state)


@update_backend("adam")
class AdamUpdate(BufferManager, ClippingMixin, AdamStateMixin):
    """Adam (Kingma & Ba 2015) on pseudo-gradients.

    Per-coordinate first/second-moment estimates with bias correction.
    Optimizer state is system-scoped: reusing one instance across
    geometries fails loud (the D13 momentum-buffer lesson). A distinct
    optimizer family from EuclideanUpdate's plain SGD+momentum — the
    U-axis coverage map (D16) measured only the SGD family, which the
    D14 jpc-faithful regime showed is the wrong default at depth.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="AdamUpdate",
        reference_equations="Adam; Kingma & Ba (2015), arXiv 1412.6980",
        deviations_from_literature=(
            "operates on credit pseudo-gradients (identical math)",
            "global-norm grad_clip before moment updates",
            "step semantics: per_element_displacement — step_size is the "
            "per-element displacement scale, NOT comparable to SGD lr",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · m̂ / (sqrt(v̂) + ε) per coordinate, with bias-corrected m, v",
        symmetry_requirements=("none",),
        approximation_parameters=(
            "step_size",
            "momentum (β1)",
            "beta2",
            "eps",
            "grad_clip",
        ),
        validated_limits=(
            "D16 coverage-map gap noted: first swept in the D14 "
            "jpc-faithful deep regime; the 5.1 mechanistic study "
            "norm-matches Adam vs SGD at matched first-step displacement",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.adam()
        self._m: dict[str, Tensor] = {}
        self._v: dict[str, Tensor] = {}
        self._t = 0

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        self._t += 1
        beta1 = self.config.momentum
        beta2 = self.config.beta2
        bias1 = 1 - beta1**self._t
        bias2 = 1 - beta2**self._t

        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            m = self._get_buffer(self._m, name, param, "Adam state")
            v = self._get_buffer(self._v, name, param, "Adam state")
            m.mul_(beta1).add_(grad, alpha=1 - beta1)
            v.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
            m_hat = m / bias1
            v_hat = v / bias2
            denom = v_hat.sqrt().add_(self.config.eps)
            return param - self.config.step_size * m_hat / denom

        return apply_pseudo_gradients(params, grads, apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_adam()

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_adam(state)


@update_backend("ortho_adam")
class OrthoAdamUpdate(AdamUpdate):
    """Orthogonalized Adam: Adam moments, Muon's matrix direction.

    Per-coordinate Adam first/second moments with bias correction; for
    matrix-shaped parameters the bias-corrected first moment is replaced
    by its SVD polar factor (Muon's orthogonalize-the-momentum recipe),
    rescaled to the plain Adam step's Frobenius magnitude so ``ortho_lr``
    stays comparable across geometries. Vector params take plain Adam.
    Optimizer state is system-scoped (inherited fail-loud reuse check).

    Measured (learning-algorithm hunt 2026-09-05, D16 regime, seeds 0-2,
    mnist quick 150 batches, bp credit): mlp 0.930 ± 0.002 / attention
    0.911 ± 0.003 / lattice 0.924 ± 0.003 / graph 0.411 ± 0.008 — beats
    both parents on mlp, attention, lattice; beats Adam on graph.

    ``config.ortho_steps`` selects the orthogonalizer: 0 (default) is the
    exact SVD polar factor — full-spectrum whitening, the configuration
    of record; ``>0`` is Newton–Schulz iteration (canonical Muon quintic
    coefficients) — the cheaper per-step recipe, opt-in pending the hunt
    probe (the D13 whitening lesson: NS preserves BP lifts but can
    collapse local-credit lifts that depend on full-spectrum whitening).
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="OrthoAdamUpdate",
        reference_equations="Adam (Kingma & Ba 2015) direction-swapped with Muon's orthogonalize-the-momentum; Liu et al. (2023) for Muon",
        deviations_from_literature=(
            "matrix params: bias-corrected first moment replaced by its "
            "SVD polar factor (ortho_steps=0, config of record) or "
            "Newton–Schulz (ortho_steps>0), rescaled to the plain Adam "
            "step's Frobenius magnitude",
            "vector params ride plain Adam; non-finite grad / SVD "
            "non-convergence skip the tensor update",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −ortho_lr · polar(m̂)·(‖adam_step‖/‖polar‖); vectors: −lr · adam_step",
        symmetry_requirements=("none",),
        approximation_parameters=(
            "ortho_lr",
            "momentum (β1)",
            "beta2",
            "ortho_steps",
            "eps",
        ),
        validated_limits=(
            "measured D16 regime (seeds 0-2, mnist quick 150 batches, bp): "
            "mlp 0.930±0.002 / attention 0.911±0.003 / lattice 0.924±0.003 "
            "/ graph 0.411±0.008 — beats both parents except graph vs Adam",
        ),
    )

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        self._t += 1
        beta1 = self.config.momentum
        beta2 = self.config.beta2
        bias1 = 1 - beta1**self._t
        bias2 = 1 - beta2**self._t
        ortho_steps = self.config.ortho_steps

        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            if not torch.isfinite(grad).all():
                # Non-finite gradient: poisoning the m/v moments would be
                # permanent (NaNs propagate through the EMA) — skip.
                return param
            m = self._get_buffer(self._m, name, param, "OrthoAdam state")
            v = self._get_buffer(self._v, name, param, "OrthoAdam state")
            m.mul_(beta1).add_(grad, alpha=1 - beta1)
            v.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
            m_hat = m / bias1
            denom = (v / bias2).sqrt().add_(self.config.eps)
            adam_step = m_hat / denom
            if param.ndim == 2:
                if ortho_steps > 0:
                    from computronium.core.optimization.strategies.update import (
                        newton_schulz5,
                    )

                    ortho = newton_schulz5(m_hat, steps=ortho_steps)
                else:
                    try:
                        U, _, Vh = torch.linalg.svd(m_hat, full_matrices=False)
                    except (
                        RuntimeError
                    ):  # svd convergence failure surfaces as RuntimeError
                        return param  # ill-conditioned moment — skip
                    ortho = U @ Vh
                ortho *= adam_step.norm() / (ortho.norm() + 1e-8)
                return param - self.config.ortho_lr * ortho
            return param - self.config.step_size * adam_step

        return apply_pseudo_gradients(params, grads, apply, bias_grads)


@update_backend("lion")
class LionUpdate(BufferManager, ClippingMixin, LionStateMixin):
    """Lion (Chen et al. 2023): sign of the momentum interpolant.

    ``update = sign(β1·m + (1−β1)·g)`` then ``m ← β2·m + (1−β2)·g`` —
    one momentum buffer, no second moment, no bias correction. Memory
    footprint is half of Adam's (O(1)-memory narrative). Reuses Adam's
    clip/state/reuse-guard machinery; only the ``m`` buffer is live
    (``v`` stays empty for snapshot-protocol compatibility).

    Optimizer state is system-scoped (inherited fail-loud reuse check).
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="LionUpdate",
        reference_equations="Lion; Chen et al. (2023), arXiv 2302.06675",
        deviations_from_literature=(
            "operates on credit pseudo-gradients (identical math)",
            "reuses Adam's clip/state machinery; only m buffer live (v "
            "empty for snapshot-protocol compatibility)",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · sign(β1·m + (1−β1)·g); m ← β2·m + (1−β2)·g",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "momentum (β1)", "beta2", "grad_clip"),
        validated_limits=(
            "O(1)-memory narrative cells; half of Adam's memory footprint",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.lion()
        self._m: dict[str, Tensor] = {}
        self._t = 0

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        self._t += 1
        beta1 = self.config.momentum
        beta2 = self.config.beta2

        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            if not torch.isfinite(grad).all():
                # Non-finite gradient: poisoning the m buffer would be
                # permanent (NaNs propagate through the EMA) — skip.
                return param
            m = self._get_buffer(self._m, name, param, "Lion state")
            interp = m.mul(beta1).add(grad, alpha=1 - beta1)
            m.mul_(beta2).add_(grad, alpha=1 - beta2)
            return param - self.config.step_size * torch.sign(interp)

        return apply_pseudo_gradients(params, grads, apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_lion()

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_lion(state)


@update_backend("riemannian_orthogonal", "muon")
class RiemannianOrthogonalUpdate(BufferManager, StateSnapshotMixin):
    """Muon-style orthogonal update: orthogonalize the momentum buffer.

    The orthogonalizer is Newton–Schulz iteration (Muon's actual recipe,
    ``ortho_steps`` iterations — MEP fast paths: Triton kernel on Triton
    targets, CUDA kernel on CUDA, torch otherwise), NOT the full SVD:
    the SVD polar factor was the placeholder, its per-matrix-per-step
    cost dominating deep sweeps. ``ortho_steps == 0`` selects the exact
    SVD polar factor as an audit escape hatch.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="RiemannianOrthogonalUpdate",
        reference_equations="Muon; Liu et al. (2023), arXiv 2409.00125 (Newton-Schulz orthogonalized momentum)",
        deviations_from_literature=(
            "orthogonalizes the MOMENTUM buffer (EMA), not the raw "
            "single-batch gradient — orthogonalization amplifies the "
            "noise floor",
            "vectors (biases) ride plain SGD (matrix-only rule)",
            "ortho_steps=0 selects the exact SVD polar factor (NOT "
            "reduced QR — its R-diagonal is sign-arbitrary, direction "
            "uncorrelated with the gradient, measured cos ≈ 0)",
            "non-finite momentum / SVD non-convergence skip the tensor "
            "instead of killing long runs",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · polar(μ·buf + g) for matrices; −lr·g for vectors",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "momentum", "ortho_steps"),
        validated_limits=(
            "FF×Muon and depth-frontier lifts measured under the exact "
            "SVD polar factor (ortho_steps=0, D13); NS (>0) preserves BP "
            "lifts but can collapse local-credit lifts",
            "step semantics: per_element_displacement — the 5.1 study "
            "norm-matches it against SGD at equal first-step ‖Δθ‖",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.riemannian_orthogonal()
        self._momentum_buffers: dict[str, Tensor] = {}

    def _orthogonalize(self, grad: Tensor) -> Tensor:
        if self.config.ortho_steps <= 0:
            # Exact polar factor: U @ Vh is the nearest orthogonal matrix
            # to grad in Frobenius norm. Reduced QR is NOT a substitute:
            # its R-diagonal is sign-arbitrary, so the resulting direction
            # is uncorrelated with the gradient (measured cos ≈ 0).
            U, _, Vh = torch.linalg.svd(grad, full_matrices=False)
            return U @ Vh
        from computronium.core.optimization.strategies.update import (
            newton_schulz5,
        )

        return newton_schulz5(grad, self.config.ortho_steps)

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            # Muon orthogonalizes the MOMENTUM, not the raw single-batch
            # gradient: orthogonalization amplifies the noise floor, so the
            # EMA buffer must accumulate signal across batches first.
            if self.config.momentum > 0:
                buf = self._get_buffer(
                    self._momentum_buffers, name, param, "Momentum buffer"
                )
                buf.mul_(self.config.momentum).add_(grad)
                self._momentum_buffers[name] = buf
                grad = buf
            if not torch.isfinite(grad).all():
                # Diverged step: SVD would crash on inf/NaN — skip this
                # tensor's update instead of killing a long run (the run
                # is already lost; the crash only destroys the evidence).
                return param
            if grad.ndim < 2:
                # Muon is a matrix rule; vectors (biases) ride plain SGD.
                return param - self.config.step_size * grad
            try:
                ortho_grad = self._orthogonalize(grad)
            except RuntimeError:  # svd convergence failure surfaces as RuntimeError
                # Ill-conditioned momentum (repeated singular values):
                # SVD fails to converge — skip this tensor's update.
                return param
            return param - self.config.step_size * ortho_grad

        return apply_pseudo_gradients(params, list(pseudo_grads), apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_momentum()

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_momentum(state)


@update_backend("spectral_constrained", "spectral")
class SpectralConstrainedUpdate:
    """Lipschitz-bounded update: constrain spectral norm of updates."""

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="SpectralConstrainedUpdate",
        reference_equations="Lipschitz-bounded optimization; spectral-norm regularization family (Szegedy et al. 2014 lineage)",
        deviations_from_literature=(
            "constrains the spectral norm of the UPDATE GRADIENT, not of "
            "the weights (σ₂-norm rescale when grad σ > spectral_norm)",
            "vectors (biases) ride plain SGD",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · g·min(1, spectral_norm/σ₂(g)) for matrices; −lr·g for vectors",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "spectral_norm"),
        validated_limits=(
            "Kinetics-discovery campaign cells (memristive settling stabilization question)",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.spectral_constrained()

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            if grad.ndim < 2:
                return param - self.config.step_size * grad
            # Normalize gradient to target spectral norm
            grad_norm = torch.linalg.matrix_norm(grad, ord=2)
            if grad_norm > self.config.spectral_norm:
                grad *= self.config.spectral_norm / (grad_norm + 1e-8)
            return param - self.config.step_size * grad

        return apply_pseudo_gradients(params, list(pseudo_grads), apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return {}

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        pass


@update_backend("mean_norm")
class MeanNormUpdate:
    """Fisher-information geometry update (natural gradient)."""

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="MeanNormUpdate",
        reference_equations="natural-gradient / Fisher-geometry family; Amari (1998) — simplified rung",
        deviations_from_literature=(
            "SIMPLIFIED: per-tensor mean-|g| normalization standing in "
            "for a true inverse-Fisher preconditioner — direction "
            "preserving, magnitude per-element-normalized",
        ),
        objective_function=None,
        pseudo_gradient_def="ΔW = −lr · g / (mean|g| + ε) per tensor",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size",),
        validated_limits=(
            "treated as a magnitude-normalizer rung, not a Fisher-faithful rule",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.mean_norm()

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            # Simplified: scale by inverse Fisher approximation
            return param - self.config.step_size * grad / (grad.abs().mean() + 1e-8)

        return apply_pseudo_gradients(params, list(pseudo_grads), apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return {}

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        pass


@update_backend("natural_gradient")
class NaturalGradientUpdate:
    """Fisher-information geometry update (natural gradient).

    Implements Amari's natural gradient: Δθ = −lr · F⁻¹ · g
    where F is the Fisher Information Matrix. Uses a diagonal Fisher
    approximation with Tikhonov damping for numerical stability.

    This is the Fisher-faithful rule; ``MeanNormUpdate`` is a simplified
    per-tensor magnitude normalizer rung.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="NaturalGradientUpdate",
        reference_equations="Natural gradient; Amari (1998) — Fisher Information Geometry; diagonal Fisher approximation with Tikhonov damping",
        deviations_from_literature=(
            "Diagonal Fisher approximation: F ≈ diag(E[g²]) instead of "
            "full Fisher matrix; Tikhonov damping (fisher_damping) added "
            "for numerical stability",
        ),
        objective_function="min_θ E[L(θ)] under Fisher-Rao metric",
        pseudo_gradient_def="ΔW = −lr · (F + λI)⁻¹ · g  (diagonal F, λ = fisher_damping)",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "fisher_damping", "beta2"),
        validated_limits=(
            "diagonal Fisher faithful to direction but underestimates "
            "cross-parameter curvature; load-bearing for deep local credit",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.natural_gradient()
        self._fisher_diag: dict[str, Tensor] = {}
        self._momentum: dict[str, Tensor] = {}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            # Update diagonal Fisher estimate (EMA of g²)
            g2 = grad.detach() ** 2
            if name not in self._fisher_diag:
                self._fisher_diag[name] = g2
            else:
                beta2 = self.config.beta2
                self._fisher_diag[name].mul_(beta2).add_(g2, alpha=1 - beta2)

            # Natural gradient: g / (sqrt(F) + eps)
            fisher_sqrt = self._fisher_diag[name].sqrt() + self.config.eps
            nat_grad = grad / fisher_sqrt

            # Optional momentum
            if self.config.momentum > 0:
                if name not in self._momentum:
                    self._momentum[name] = torch.zeros_like(nat_grad)
                self._momentum[name].mul_(self.config.momentum).add_(nat_grad)
                nat_grad = self._momentum[name]

            # Gradient clipping (global norm)
            if self.config.grad_clip and self.config.grad_clip > 0:
                total_norm = torch.norm(
                    torch.stack([torch.norm(g) for g in nat_grad.flatten()])
                )
                if total_norm > self.config.grad_clip:
                    nat_grad.mul_(self.config.grad_clip / (total_norm + 1e-8))

            return param - self.config.step_size * nat_grad

        return apply_pseudo_gradients(params, list(pseudo_grads), apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return {
            "fisher_diag": {k: v.clone() for k, v in self._fisher_diag.items()},
            "momentum": {k: v.clone() for k, v in self._momentum.items()},
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._fisher_diag = {
            k: v.clone() for k, v in state.get("fisher_diag", {}).items()
        }
        self._momentum = {k: v.clone() for k, v in state.get("momentum", {}).items()}


@update_backend("elastic_consolidation", "ewc")
class ElasticConsolidationUpdate:
    """EWC-style importance-weighted update.

    In standard EWC (Kirkpatrick et al., 2017):
    - Fisher information F = (param - old_param)^2 (squared distance from old task)
    - Regularization: lambda * F * (param - old_param)
    - lambda (ewc_lambda) is the importance weight controlling regularization strength

    This implementation separates:
    - fisher_damping: small constant added to Fisher for numerical stability
    - ewc_lambda: importance weight for the EWC regularization term
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="ElasticConsolidationUpdate",
        reference_equations="Elastic Weight Consolidation; Kirkpatrick et al. (2017), arXiv 1612.00796",
        deviations_from_literature=(
            "Fisher information approximated as squared drift from the "
            "consolidation baseline (params − old)² + fisher_damping, "
            "not the true diagonal Fisher of the new-task likelihood",
            "consolidate() anchors old params at episode boundaries "
            "(two-argument form imports an external old-task snapshot)",
        ),
        objective_function="L + (ewc_lambda/2)·Σ F·(param − old)² implicitly applied as a gradient term",
        pseudo_gradient_def="ΔW = −lr·(g + ewc_lambda·F·(param − old_param))",
        symmetry_requirements=("none",),
        approximation_parameters=("ewc_lambda", "fisher_damping"),
        validated_limits=(
            "continual-learning drift locks (elastic drift vs plain SGD at consolidation boundaries)",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.elastic_consolidation()
        self._old_params: dict[str, Tensor] = {}
        self._fisher: dict[str, Tensor] = {}
        self._baseline: dict[str, Tensor] = {}

    def consolidate(
        self, params: dict[str, Tensor], old_params: dict[str, Tensor] | None = None
    ) -> None:
        """Store old parameters and compute Fisher importance (squared distance from old).

        With ``old_params`` given, importance is ``(params - old_params)^2``.
        Single-argument form anchors the current snapshot for future tasks and
        derives importance from drift since the previous consolidation
        baseline (uniform damping on the first call).
        """
        if old_params is None:
            old_params = self._baseline or params
        self._old_params = {k: v.clone().detach() for k, v in old_params.items()}
        # Fisher = (current - old)^2 + fisher_damping (for numerical stability)
        self._fisher = {
            k: (params[k].detach() - old_params[k].detach()) ** 2
            + self.config.fisher_damping
            for k in params
            if k in old_params
        }
        self._baseline = {k: v.clone().detach() for k, v in params.items()}

    def anchor(self, params: dict[str, Tensor]) -> None:
        """Move the consolidation anchor to ``params`` without recomputing it.

        A task start must anchor to the previous task's solution while keeping
        the drift importance measured at the previous boundary; recomputing on
        the same parameters would reset every Fisher entry to ``damping``.
        """
        self._old_params = {k: v.clone().detach() for k, v in params.items()}
        self._baseline = {k: v.clone().detach() for k, v in params.items()}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        def apply(name: str, param: Tensor, grad: Tensor) -> Tensor:
            # EWC update: param - lr * grad - lr * ewc_lambda * fisher * (param - old_param)
            if name in self._old_params and name in self._fisher:
                ewc_term = (
                    self.config.ewc_lambda
                    * self._fisher[name]
                    * (param - self._old_params[name])
                )
                return (
                    param
                    - self.config.step_size * grad
                    - self.config.step_size * ewc_term
                )
            return param - self.config.step_size * grad

        return apply_pseudo_gradients(params, list(pseudo_grads), apply, bias_grads)

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return {
            "old_params": {k: v.clone() for k, v in self._old_params.items()},
            "fisher": {k: v.clone() for k, v in self._fisher.items()},
            "baseline": {k: v.clone() for k, v in self._baseline.items()},
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._old_params = {
            k: v.clone() for k, v in state.get("old_params", {}).items()
        }
        self._fisher = {k: v.clone() for k, v in state.get("fisher", {}).items()}
        self._baseline = {k: v.clone() for k, v in state.get("baseline", {}).items()}

    def state_bytes(self) -> int:
        """Bytes of consolidation state carried beside the parameters."""
        return sum(
            t.numel() * t.element_size()
            for state in (self._old_params, self._fisher, self._baseline)
            for t in state.values()
        )


#: The role name the role-split factory declares for the output projection.
#: A factory cannot know a parameter name before the geometry exists, so the
#: token is resolved against the composed geometry at step time.
_READOUT_ROLE = "readout"


def _resolve_readout_role(
    roles: frozenset[str], params: dict[str, Tensor], geometry: Geometry | None
) -> frozenset[str]:
    """Expand the ``readout`` token to the parameter that projects to output."""
    if _READOUT_ROLE not in roles:
        return roles
    learnable = _learnable_weight_names(params)
    output_dim = getattr(getattr(geometry, "config", None), "output_dim", None)
    readout = next(
        (
            name
            for name in reversed(learnable)
            if output_dim is not None and params[name].shape[0] == output_dim
        ),
        learnable[-1] if learnable else None,
    )
    resolved = set(roles - {_READOUT_ROLE})
    if readout is not None:
        resolved.add(readout)
    return frozenset(resolved)


@update_backend("role_split")
class RoleSplitUpdate:
    """Per-name dispatcher: the ``on_role`` rule on ``role_names``, the
    ``other`` rule on the rest (X-USU-001 hybrid primitive).

    Promoted from the X-USU-001 probe (B-H5 winner: muon-on-readout +
    euclid-elsewhere beat both uniform arms on improvement_per_norm on
    3/3 seeds). Each sub-rule sees ONLY its own names — params,
    pseudo-grads and bias grads are partitioned — so momentum buffers
    stay per-role, no parameter is stepped twice, and a sub-rule's
    global-norm clip (Euclidean) applies to its own name set only.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="RoleSplitUpdate",
        reference_equations=(
            "per-parameter-name rule dispatch (composition primitive, "
            "no canonical optimizer reference)"
        ),
        deviations_from_literature=(
            "not a new optimizer — routes each parameter name to exactly "
            "one sub-rule (X-USU-001: muon-on-readout + euclid-elsewhere)",
            "global-norm clip semantics are per-subset: each sub-rule "
            "clips its own name set independently",
        ),
        objective_function=None,
        pseudo_gradient_def=(
            "ΔW_n = on_role.step(g_n) for n ∈ role_names; other.step(g_n) otherwise"
        ),
        symmetry_requirements=("role_names must name existing parameters",),
        approximation_parameters=("role_names",),
        validated_limits=(
            "X-USU-001: hybrid_muon_out beat both uniform arms on "
            "improvement_per_norm on 3/3 seeds (B-H5); muon-on-forward "
            "is destructive at matched norm",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig) -> None:
        if config.update_type.lower() != "role_split" or config.sub_rules is None:
            raise ValueError(
                "RoleSplitUpdate requires update_type='role_split' with a "
                f"role_split spec (got {config.update_type!r})"
            )
        spec = RoleSplitSpec.coerce(config.sub_rules)
        self.config = config
        self._role_names = frozenset(config.role_names)
        self._on_role = cast("StatefulUpdate", update_from_config(spec.on_role))
        self._other = cast("StatefulUpdate", update_from_config(spec.other))

    def _partitions(
        self, params: dict[str, Tensor], geometry: Geometry | None
    ) -> tuple[tuple[StatefulUpdate, frozenset[str]], ...]:
        names = frozenset(params)
        roles = _resolve_readout_role(self._role_names, params, geometry)
        return (
            (self._on_role, names & roles),
            (self._other, names - roles),
        )

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry | None,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = dict(zip(_learnable_weight_names(params), pseudo_grads))
        bgrads = bias_grads or {}
        updated = dict(params)
        for rule, names in self._partitions(params, geometry):
            if not names:
                continue
            sub_params = {n: params[n] for n in names}
            sub_grads = [grads[n] for n in _learnable_weight_names(sub_params)]
            sub_bias = {n: bgrads[n] for n in bgrads if n in sub_params}
            sub_out = rule.step(sub_params, sub_grads, geometry, sub_bias or None)
            updated.update({n: sub_out[n] for n in sub_params})
        return updated

    def get_state(self) -> dict[str, dict[str, dict[str, Tensor]]]:
        return {"on_role": self._on_role.get_state(), "other": self._other.get_state()}

    def load_state(self, state: dict[str, dict[str, dict[str, Tensor]]]) -> None:
        self._on_role.load_state(state.get("on_role", {}))
        self._other.load_state(state.get("other", {}))


@update_backend("synaptic_intelligence")
class SynapticIntelligenceUpdate(BufferManager, ClippingMixin, StateSnapshotMixin):
    """Synaptic Intelligence, lifted from the continual penalty to a rule.

    The source of truth stays ``core.continual.losses.SynapticIntelligence``:
    this rule holds one *stable* parameter store (so the loss object's
    id-keyed state stays valid across steps), feeds it the clipped
    pseudo-gradients, and adds its ``penalty_gradients()`` to the task
    gradient: ``Δθ = −lr·(g + ξ·Ω̃·(θ − θ*))``. ``consolidate()`` closes
    the task at the boundary. The extra parameter copy is the penalty's
    price, named on the card.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="SynapticIntelligenceUpdate",
        reference_equations=(
            "Synaptic Intelligence; Zenke, Poole & Ganguli (2017), arXiv 1703.04200"
        ),
        deviations_from_literature=(
            "the path integral is optimizer state, not a loss object's field",
            "the rule keeps one stable parameter store so the loss object's "
            "id-keyed state survives the step",
        ),
        objective_function="L + (ξ/2)·Σ Ω̃·(θ − θ*)² applied as a gradient term",
        pseudo_gradient_def="ΔW = −lr·(g + ξ·Ω̃·(θ − θ*))",
        symmetry_requirements=("none",),
        approximation_parameters=("si_lambda", "step_size"),
        validated_limits=(
            "the lifted rule and the loss object agree at a task boundary",
            "the penalty vanishes at the anchor",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        from computronium.core.continual.losses import SynapticIntelligence

        self.config = config or ParameterUpdateConfig.synaptic_intelligence()
        self._store: dict[str, Tensor] = {}
        self._view = _ParameterView(self._store)
        self._intelligence = SynapticIntelligence(
            self._view, xi=self.config.si_lambda, epsilon=self.config.fisher_damping
        )

    def consolidate(self, params: dict[str, Tensor] | None = None) -> None:
        """Close the task at the boundary: finalize Ω̃ on the rule's store."""
        if not self._store and params is not None:
            self._store.update({
                name: tensor.detach().clone() for name, tensor in params.items()
            })
            self._intelligence.start_task()
        self._intelligence.update_importance()

    def state_tensors(self) -> dict[str, Tensor]:
        """Live SI state, without the snapshot clone."""
        return {
            f"importance.{name}": self._intelligence.omega[id(tensor)]
            for name, tensor in self._store.items()
            if id(tensor) in self._intelligence.omega
        } | {f"store.{name}": tensor for name, tensor in self._store.items()}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        if not self._store:
            self._store.update({
                name: tensor.detach().clone() for name, tensor in params.items()
            })
            self._intelligence.start_task()
        self._intelligence.accumulate_pseudo_grads(grads, geometry)
        penalty = self._intelligence.penalty_gradients()
        names = [name for name in self._store if "weight" in name]
        updated = dict(self._store)
        for name, grad in zip(names, grads, strict=True):
            identity = id(self._store[name])
            extra = penalty.get(identity)
            updated[name] = self._store[name] - self.config.step_size * grad
            if extra is not None:
                updated[name] -= self.config.step_size * extra
        for name, tensor in updated.items():
            self._store[name].copy_(tensor)
        return {name: tensor.detach().clone() for name, tensor in updated.items()}

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return {
            "store": {k: v.detach().clone() for k, v in self._store.items()},
            "importance": {
                name: self._intelligence.omega[id(tensor)].detach().clone()
                for name, tensor in self._store.items()
                if id(tensor) in self._intelligence.omega
            },
            "anchor": {
                name: self._intelligence.prev_params[id(tensor)].detach().clone()
                for name, tensor in self._store.items()
                if id(tensor) in self._intelligence.prev_params
            },
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._store = {k: v.clone() for k, v in state.get("store", {}).items()}
        self._view = _ParameterView(self._store)
        self._intelligence.model = self._view
        self._intelligence.omega = {
            id(self._store[name]): value.clone()
            for name, value in state.get("importance", {}).items()
            if name in self._store
        }
        self._intelligence.prev_params = {
            id(self._store[name]): value.clone()
            for name, value in state.get("anchor", {}).items()
            if name in self._store
        }


class _ParameterView:
    """A ``named_parameters()`` view over the rule's stable parameter store."""

    def __init__(self, store: dict[str, Tensor]) -> None:
        self._store = store

    def named_parameters(self, *args: object, **kwargs: object):
        return iter(self._store.items())

    def parameters(self, *args: object, **kwargs: object):
        return iter(self._store.values())


@update_backend("cascade_synapse")
class CascadeSynapseUpdate(BufferManager, ClippingMixin, StateSnapshotMixin):
    """Benna–Fusi cascade: a metaplastic multi-level state per parameter.

    ``Δθ = −lr·g·(1 + c)``, then the cascade moves: ``c ← min(levels, c + up)``
    when the step's sign disagrees with the stored sign, else
    ``c ← c·(1 − down)``. The levels are the synapse's history, so a
    parameter that keeps changing direction becomes harder to move.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="CascadeSynapsePlasticity",
        reference_equations=(
            "Benna & Fusi (2016), Nature Neuroscience 19:1695; cascade "
            "model with discrete metaplastic levels"
        ),
        deviations_from_literature=(
            "cascade levels are stored per parameter, not per synapse of a "
            "spiking network",
            "the step's sign uses the pseudo-gradient, not a spike pair",
        ),
        objective_function="Δθ = −lr·g·(1 + c)",
        pseudo_gradient_def="ΔW = −lr·g·(1 + c); c ← c + up on a sign flip",
        symmetry_requirements=("none",),
        approximation_parameters=(
            "cascade_levels",
            "cascade_up",
            "cascade_down",
            "step_size",
        ),
        validated_limits=(
            "the cascade saturates at its level count",
            "a repeated direction decays the cascade by (1 − down)",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.cascade_synapse()
        self._cascade: dict[str, Tensor] = {}
        self._sign: dict[str, Tensor] = {}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        names = [name for name in params if "weight" in name and params[name].ndim == 2]
        for name, grad in zip(names, grads, strict=True):
            param = params[name]
            cascade = self._get_buffer(self._cascade, name, param, "Cascade state")
            sign = self._sign.get(name)
            if sign is None:
                self._sign[name] = torch.zeros_like(param)
                sign = self._sign[name]
            if not torch.isfinite(grad).all():
                continue
            flipped = (torch.sign(grad) != sign) & (sign != 0)
            cascade += flipped.to(cascade.dtype) * self.config.cascade_up
            cascade *= 1 - self.config.cascade_down * (~flipped).to(cascade.dtype)
            cascade.clamp_(0.0, float(self.config.cascade_levels))
            sign.copy_(torch.sign(grad))
            params[name] = param - self.config.step_size * grad * (1 + cascade)
        return params

    def state_tensors(self) -> dict[str, Tensor]:
        """Live cascade state, without the snapshot clone."""
        return {f"cascade.{k}": v for k, v in self._cascade.items()} | {
            f"sign.{k}": v for k, v in self._sign.items()
        }

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return {
            "cascade": {k: v.detach().clone() for k, v in self._cascade.items()},
            "sign": {k: v.detach().clone() for k, v in self._sign.items()},
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._cascade = {k: v.clone() for k, v in state.get("cascade", {}).items()}
        self._sign = {k: v.clone() for k, v in state.get("sign", {}).items()}


@update_backend("bayesian_online")
class BayesianOnlineUpdate(BufferManager, ClippingMixin, StateSnapshotMixin):
    """VON: an online diagonal Gaussian posterior per parameter.

    ``μ ← μ − α·σ²·g`` and ``σ² ← max(min_var, σ²·(1 − α·σ²·g²))`` — the
    law-of-the-total-variance for the weight posterior (Aitchison 2021). The
    variance is the trust region: an uncertain parameter takes a long step,
    a settled one barely moves.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="BayesianOnlineUpdate",
        reference_equations=(
            "VON (Aitchison 2021, arXiv 2010.11995); online Gaussian "
            "posterior over the weights"
        ),
        deviations_from_literature=(
            "the posterior is diagonal per parameter (no covariance "
            "factors); the variance is the per-coordinate trust region",
        ),
        objective_function="−log E_{q(θ)}[L] with q = N(μ, σ²)",
        pseudo_gradient_def="μ ← μ − lr·σ²g; σ² ← σ²(1 − lr·σ²g²)",
        symmetry_requirements=("none",),
        approximation_parameters=("step_size", "von_init_var", "von_min_var"),
        validated_limits=(
            "the variance falls monotonically under a constant gradient",
            "the variance recovers toward its init once gradients vanish",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.bayesian_online()
        self._mu: dict[str, Tensor] = {}
        self._var: dict[str, Tensor] = {}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        names = [name for name in params if "weight" in name and params[name].ndim == 2]
        lr = self.config.step_size
        for name, grad in zip(names, grads, strict=True):
            param = params[name]
            variance = self._get_buffer(
                dict(self._var),
                name,
                param,
                "VON state",
            )
            if variance.norm() == 0:
                variance = torch.full_like(param, self.config.von_init_var)
            self._var[name] = variance
            if not torch.isfinite(grad).all():
                continue
            self._mu[name] = param
            variance = (variance * (1 - lr * variance * grad.square())).clamp_min(
                self.config.von_min_var
            )
            self._var[name] = variance
            params[name] = param - lr * variance * grad
        return params

    def state_tensors(self) -> dict[str, Tensor]:
        """Live VON state, without the snapshot clone."""
        return {f"variance.{k}": v for k, v in self._var.items()}

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return {
            "mean": {k: v.detach().clone() for k, v in self._mu.items()},
            "variance": {k: v.detach().clone() for k, v in self._var.items()},
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._mu = {k: v.clone() for k, v in state.get("mean", {}).items()}
        self._var = {k: v.clone() for k, v in state.get("variance", {}).items()}


CascadeSynapsePlasticity = CascadeSynapseUpdate
"""The plan's literature name; the class name follows the axis convention."""


@update_backend("adafactor")
class FactoredSecondMomentUpdate(
    BufferManager, ClippingMixin, SecondMomentMixin, StateSnapshotMixin
):
    """Adafactor: a factored (row × column) second moment.

    ``V ≈ R Cᵀ / mean(R)``; ``m ← β1·m + (1−β1)·g``; ``R ← β2·R + (1−β2)·mean(g², rows)``;
    ``C ← β2·C + (1−β2)·mean(g², columns)``; ``Δθ = −lr·m/√(V + eps)``. One
    row and one column vector replace the full second moment, so the optimizer
    state is ``O(rows + cols)`` per matrix instead of ``O(rows·cols)``.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="FactoredSecondMomentUpdate",
        reference_equations=("Adafactor; Shazeer & Stern (2018), arXiv 1804.04235"),
        deviations_from_literature=(
            "the factored second moment is stored per 2-D weight; the update "
            "applies no relative-step clip and no warmup",
        ),
        objective_function="the task loss at the FREE-phase input/target",
        pseudo_gradient_def="ΔW = −lr·m/√(R Cᵀ/mean(R) + eps)",
        symmetry_requirements=("none",),
        approximation_parameters=("momentum (β1)", "factor_decay (β2)", "eps"),
        validated_limits=(
            "the factored estimate tracks the full second moment on a rank-1 "
            "gradient fixture",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.adafactor()
        self._m: dict[str, Tensor] = {}
        self._second: dict[str, Tensor] = {}

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        names = [name for name in params if "weight" in name and params[name].ndim == 2]
        beta1 = self.config.momentum
        beta2 = self.config.factor_decay
        for name, grad in zip(names, grads, strict=True):
            param = params[name]
            if not torch.isfinite(grad).all():
                continue
            moment = self._get_buffer(self._m, name, param, "Adafactor state")
            moment.mul_(beta1).add_(grad, alpha=1 - beta1)
            self._m[name] = moment
            row = self._second.get(f"{name}.row")
            column = self._second.get(f"{name}.column")
            if row is None or row.shape != (param.shape[0],):
                row = torch.zeros(
                    param.shape[0], device=param.device, dtype=param.dtype
                )
            if column is None or column.shape != (param.shape[1],):
                column = torch.zeros(
                    param.shape[1], device=param.device, dtype=param.dtype
                )
            square = grad.square()
            row.mul_(beta2).add_(square.mean(dim=1), alpha=1 - beta2)
            column.mul_(beta2).add_(square.mean(dim=0), alpha=1 - beta2)
            self._second[f"{name}.row"] = row
            self._second[f"{name}.column"] = column
            estimate = row[:, None] * column[None, :] / row.mean().clamp_min(1e-12)
            params[name] = (
                param
                - self.config.step_size * moment / (estimate + self.config.eps).sqrt()
            )
        return params

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_second() | {
            "momentum": {k: v.detach().clone() for k, v in self._m.items()}
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_second(state)
        self._m = {k: v.clone() for k, v in state.get("momentum", {}).items()}


@update_backend("quantized_adam")
class QuantizedStateUpdate(
    BufferManager, ClippingMixin, SecondMomentMixin, StateSnapshotMixin
):
    """8-bit Adam: blockwise-quantized first and second moments.

    Both moments are stored as int8 blocks with one scale per block, so the
    optimizer state is 4× smaller than fp32 Adam and the step is the usual
    bias-corrected Adam on the dequantized moments. The scale is the block's
    absolute maximum over 127 — the bitsandbytes layout.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="QuantizedStateUpdate",
        reference_equations=(
            "8-bit Adam; Dettmers et al. (2022), arXiv 2110.02861 "
            "(blockwise quantization of the optimizer state)"
        ),
        deviations_from_literature=(
            "the block size is fixed at ``quant_block`` elements and the "
            "scale is the block absolute maximum over 127",
            "the second moment is dequantized with a one-LSB floor: a block "
            "with one dominant gradient packs its small elements to zero, and "
            "the step would otherwise divide by eps alone (measured 120×)",
            "the step is exact Adam on the dequantized moments",
        ),
        objective_function="the task loss at the FREE-phase input/target",
        pseudo_gradient_def=("ΔW = −lr·m̂/(√v̂ + eps); m̂, v̂ = dequantized int8 blocks"),
        symmetry_requirements=("none",),
        approximation_parameters=(
            "momentum (β1)",
            "beta2",
            "eps",
            "quant_block",
        ),
        validated_limits=(
            "the quantized state's memory is 4× smaller than fp32 Adam",
            "the dequantized step matches fp32 Adam within the block scale",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.quantized_adam()
        self._moment: dict[str, Tensor] = {}
        self._second: dict[str, Tensor] = {}
        self._shapes: dict[str, torch.Size] = {}
        self._t = 0

    def _quantize(self, tensor: Tensor) -> tuple[Tensor, Tensor]:
        """Int8 blocks and one scale per block; the last block is trimmed."""
        block = max(1, int(self.config.quant_block))
        flat = tensor.flatten()
        blocks = -(-flat.numel() // block)
        pad = blocks * block - flat.numel()
        padded = flat if not pad else torch.cat([flat, flat.new_zeros(pad)])
        view = padded.view(blocks, block)
        scale = view.abs().amax(dim=1).clamp_min(1e-12) / 127
        packed = torch.round(view / scale[:, None]).to(torch.int8).flatten()
        return packed[: flat.numel()], scale

    def _dequantize(
        self, packed: Tensor, scale: Tensor, numel: int, *, floor: bool = False
    ) -> Tensor:
        """Int8 blocks back to a tensor, at least one LSB per block when floored.

        ``floor`` is for the second moment only: a block with one dominant
        gradient packs its small elements to zero, and Adam's denominator
        would then be ``eps`` alone — the measured 12,000× overshoot. One
        LSB is the smallest value the quantized state can represent, so it is
        the honest lower bound on the moment, not a clamp on the step.
        """
        block = max(1, int(self.config.quant_block))
        blocks = scale.numel()
        flat = packed
        if flat.numel() < blocks * block:
            flat = torch.cat([flat, flat.new_zeros(blocks * block - flat.numel())])
        decoded = flat.view(blocks, block).to(scale.dtype) * scale[:, None]
        if floor:
            decoded = torch.maximum(decoded, scale[:, None])
        return decoded.flatten()[:numel]

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        names = [name for name in params if "weight" in name and params[name].ndim == 2]
        self._t += 1
        beta1 = self.config.momentum
        beta2 = self.config.beta2
        for name, grad in zip(names, grads, strict=True):
            param = params[name]
            if not torch.isfinite(grad).all():
                continue
            stored = self._shapes.setdefault(name, param.shape)
            if stored != param.shape:
                raise RuntimeError(
                    f"QuantizedStateUpdate state for {name!r} has shape "
                    f"{tuple(stored)} but parameter has {tuple(param.shape)} "
                    "-- the update instance is being reused across different "
                    "geometries; create one update per system (optimizer "
                    "state is system-scoped)"
                )
            packed_m = self._moment.get(f"{name}.m")
            packed_v = self._second.get(f"{name}.v")
            if packed_m is None or packed_v is None:
                first = torch.zeros_like(param)
                second = torch.zeros_like(param)
            else:
                first = self._dequantize(
                    packed_m, self._moment[f"{name}.m.scale"], param.numel()
                ).view(param.shape)
                second = self._dequantize(
                    packed_v,
                    self._second[f"{name}.v.scale"],
                    param.numel(),
                    floor=True,
                ).view(param.shape)
            first.mul_(beta1).add_(grad, alpha=1 - beta1)
            second.mul_(beta2).add_(grad.square(), alpha=1 - beta2)
            self._moment[f"{name}.m"], self._moment[f"{name}.m.scale"] = self._quantize(
                first
            )
            self._second[f"{name}.v"], self._second[f"{name}.v.scale"] = self._quantize(
                second
            )
            bias1 = 1 - beta1**self._t
            bias2 = 1 - beta2**self._t
            params[name] = param - self.config.step_size * (first / bias1) / (
                (second / bias2).sqrt() + self.config.eps
            )
        return params

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_second() | {
            "momentum": {k: v.detach().clone() for k, v in self._moment.items()}
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_second(state)
        self._moment = {k: v.clone() for k, v in state.get("momentum", {}).items()}


@update_backend("schedule_free")
class ScheduleFreeUpdate(
    BufferManager, ClippingMixin, SecondMomentMixin, StateSnapshotMixin
):
    """Schedule-free AdamW: ``x`` is averaged over a ``z`` sequence.

    ``z ← z − lr·g/√(v + eps)``, ``v ← β2·v + (1−β2)·g²``, then
    ``x_avg ← (1 − c)·x_avg + c·z`` with ``c = 1/(t + 1)``. The evaluation
    point is the average, so the rule needs no decreasing schedule and no
    warmup: the averaging is the schedule.
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="ScheduleFreeUpdate",
        reference_equations=(
            "Schedule-Free AdamW; Defazio et al. (2024), arXiv 2405.15682"
        ),
        deviations_from_literature=(
            "the evaluation point is the running average of the sequence "
            "iterate; no warmup schedule and no weight decay are applied",
        ),
        objective_function="the task loss at the averaged evaluation point",
        pseudo_gradient_def="z ← z − lr·g/√v; x ← (1 − c)x + c·z",
        symmetry_requirements=("none",),
        approximation_parameters=(
            "step_size",
            "schedule_beta (β1)",
            "beta2",
            "eps",
        ),
        validated_limits=(
            "the averaged point reaches the same loss as a tuned schedule on "
            "a convex fixture",
        ),
    )

    def __init__(self, config: ParameterUpdateConfig | None = None):
        self.config = config or ParameterUpdateConfig.schedule_free()
        self._z: dict[str, Tensor] = {}
        self._second: dict[str, Tensor] = {}
        self._t = 0

    def step(
        self,
        params: dict[str, Tensor],
        pseudo_grads: list[Tensor],
        geometry: Geometry,
        bias_grads: dict[str, Tensor] | None = None,
    ) -> dict[str, Tensor]:
        grads = self._clip(list(pseudo_grads), self.config.grad_clip)
        names = [name for name in params if "weight" in name and params[name].ndim == 2]
        self._t += 1
        beta2 = self.config.beta2
        average = 1.0 / self._t
        for name, grad in zip(names, grads, strict=True):
            param = params[name]
            if not torch.isfinite(grad).all():
                continue
            sequence = self._z.get(name)
            if sequence is None or sequence.shape != param.shape:
                sequence = param.detach().clone()
            second = self._second.get(name)
            if second is None or second.shape != param.shape:
                second = torch.zeros_like(param)
            second.mul_(beta2).add_(grad.square(), alpha=1 - beta2)
            sequence -= self.config.step_size * grad / (second.sqrt() + self.config.eps)
            self._z[name] = sequence
            self._second[name] = second
            params[name] = (1 - average) * param + average * sequence
        return params

    def get_state(self) -> dict[str, dict[str, Tensor]]:
        return self._snapshot_second() | {
            "sequence": {k: v.detach().clone() for k, v in self._z.items()},
            "counters": {"t": torch.tensor(self._t)},
        }

    def load_state(self, state: dict[str, dict[str, Tensor]]) -> None:
        self._restore_second(state)
        self._z = {k: v.clone() for k, v in state.get("sequence", {}).items()}
        count = state.get("counters", {}).get("t")
        self._t = int(count.item()) if count is not None else 0


def update_from_config(config: ParameterUpdateConfig) -> ParameterUpdate:
    """Instantiate the update rule named by ``config.update_type``.

    Single dispatch point shared by the joint-system factory and
    ``System.from_spec``; unknown values raise (no silent Euclidean
    fallback: a typo'd update_type must not masquerade as SGD).
    """
    return _UPDATE_REGISTRY.build(config.update_type.lower(), config)


# Backwards compatibility: the old dict interface
class _UpdateRegistryView:
    """Read-only view of the registry for backwards compatibility."""

    def __getitem__(self, key: str) -> type[ParameterUpdate]:
        return _UPDATE_REGISTRY.get(key)

    def __contains__(self, key: str) -> bool:
        try:
            _UPDATE_REGISTRY.get(key)
        except KeyError:
            return False
        else:
            return True

    def __iter__(self):
        return iter(_UPDATE_REGISTRY.aliases())

    def __len__(self):
        return len(_UPDATE_REGISTRY.aliases())

    def get(self, key: str, default=None):
        try:
            result = _UPDATE_REGISTRY.get(key)
        except KeyError:
            return default
        else:
            return result

    def keys(self):
        return _UPDATE_REGISTRY.aliases()

    def values(self):
        return [_UPDATE_REGISTRY.get(k) for k in self.keys()]

    def items(self):
        return [(k, _UPDATE_REGISTRY.get(k)) for k in self.keys()]


# Export the view for backwards compatibility with tests using _UPDATE_BACKENDS
_UPDATE_BACKENDS = _UpdateRegistryView()  # type: ignore[assignment]
