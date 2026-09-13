"""Validated mechanism recipes — wrapped from the extracted platform packages.

Each recipe carries its scope and evidence references; nothing here invents
new mechanism semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from computronium.core.system_trainer.spec import compose_system_from_configs
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.update import ParameterUpdateConfig

if TYPE_CHECKING:
    from collections.abc import Callable

    from torch import Tensor


@dataclass(frozen=True, slots=True)
class Recipe:
    """A validated mechanism recipe with its evidence scope."""

    name: str
    summary: str
    when_to_use: str
    when_not: str
    evidence: tuple[str, ...]
    build: Callable[..., object]
    defaults: dict[str, object] = field(default_factory=dict)


def build_temporal_psi(
    feature_dim: int = 64,
    num_classes: int = 4,
    conflict_threshold: float = 0.6,
    forget_decay: float = 0.5,
) -> object:
    """AdaptivePsiReadout from packages/psi-peft (X-TPC-001..003)."""
    from psi_peft import AdaptivePsiReadout

    return AdaptivePsiReadout(
        feature_dim=feature_dim,
        num_classes=num_classes,
        conflict_threshold=conflict_threshold,
        forget_decay=forget_decay,
    )


def build_adaptive_feedback(
    in_features: int = 32,
    out_features: int = 4,
    feedback_lr: float = 0.02,
) -> object:
    """AdaptiveFeedback from packages/local-feedback (X-ALI-001/002).

    ``feedback_lr=0.02`` is the validated slow-blend setting; ``1.0``
    reproduces the original per-step re-projection (thrashes at quick
    horizons).
    """
    from local_feedback import AdaptiveFeedback

    return AdaptiveFeedback(
        in_features=in_features,
        out_features=out_features,
        feedback_lr=feedback_lr,
    )


def build_role_split_muon_readout(
    input_dim: int = 32,
    hidden_dims: tuple[int, ...] = (64, 32),
    output_dim: int = 4,
    readout_name: str | None = None,
) -> object:
    """Role-split update system: muon-class orthogonalization on the readout,
    euclidean elsewhere (X-USU-001 winner: beats both parents on mlp)."""
    if readout_name is None:
        # feedforward layer params are "0.weight", "2.weight", ... — the
        # readout is the last one
        readout_name = f"{2 * len(hidden_dims)}.weight"
    return compose_system_from_configs(
        substrate=SubstrateConfig(
            precision="float32",
            noise_level=0.0,
            weight_bounds=None,
            sparsity=0.0,
            device="cpu",
        ),
        geometry=GeometryConfig.feedforward(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
            init_scale=0.1,
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        credit=CreditAssignmentConfig.gradient(),
        update=ParameterUpdateConfig.role_split(
            role_names=(readout_name,),
            on_role=ParameterUpdateConfig.riemannian_orthogonal(step_size=0.01),
            other=ParameterUpdateConfig.euclidean(step_size=0.05),
        ),
    )


@dataclass(frozen=True, slots=True)
class StableAmplifier:
    """A linear coordinate with verified stable-transient amplification."""

    weight: Tensor
    rho: float
    sigma_max: float
    rho_ok: bool
    sigma_ok: bool

    def __call__(self, x: Tensor) -> Tensor:
        return x @ self.weight.T


def build_stable_amplification(
    gain: float = 0.85,
    rho_limit: float = 0.95,
    dim: int = 4,
) -> StableAmplifier:
    """Jordan-block stable-transient coordinate from packages/stability.

    rho <= rho_limit while sigma_max > 1: transient amplification without
    divergence (X-STA-001/002). Raises if the realized spectrum misses the
    requested window.
    """
    from stability.matrices import (
        jordan_block,
        linear_transition,
        realized_rho,
        realized_sigma_max,
    )

    weight = jordan_block(gain=gain, dim=dim)
    transition, state = linear_transition(weight)
    rho = realized_rho(transition, state)
    sigma_max = realized_sigma_max(transition, state)
    if rho > rho_limit or sigma_max <= 1.0:
        raise ValueError(
            f"realized spectrum misses window: rho={rho:.4f} "
            f"(limit {rho_limit}), sigma_max={sigma_max:.4f}"
        )
    return StableAmplifier(
        weight=weight, rho=rho, sigma_max=sigma_max, rho_ok=True, sigma_ok=True
    )


def build_epc_deep(
    input_dim: int = 32,
    hidden_dims: tuple[int, ...] = (64, 32),
    output_dim: int = 4,
    depth: int = 2,
    beta: float = 0.5,
) -> object:
    """Error-parameterized PC (ePC) system (docs/family_recipes.md flagship).

    ThermodynamicContrast + ErrorPredictiveCodingDynamics + OrthoAdamUpdate
    on a μPC-initialized residual feedforward geometry. The recorded
    operating point is depth-32 harvest (0.917, 3 seeds) — ``depth`` scales
    ``hidden_dims`` accordingly when left implicit.
    """
    if depth > len(hidden_dims):
        hidden_dims += (128,) * (depth - 1 - len(hidden_dims))
    return compose_system_from_configs(
        substrate=SubstrateConfig(
            precision="float32",
            noise_level=0.0,
            weight_bounds=None,
            sparsity=0.0,
            device="cpu",
        ),
        geometry=GeometryConfig.feedforward(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
            init_scheme="mupc",
            residual=True,
        ),
        dynamics=StateDynamicsConfig.error_predictive_coding(
            max_steps=depth, beta=beta
        ),
        credit=CreditAssignmentConfig.thermodynamic_contrast(beta=beta),
        update=ParameterUpdateConfig.ortho_adam(step_size=1e-3),
    )


def build_spatial_lattice_bp(
    input_dim: int = 32,
    hidden_dims: tuple[int, ...] = (64, 32),
    output_dim: int = 4,
    lattice_dims: tuple[int, int, int] = (4, 4, 4),
) -> object:
    """Backprop classification on a 3D spatial-lattice geometry (D11 arm).

    Same composition as the D11 gallery arm (BackpropCredit + Euclidean on
    ``SpatialLattice3DGeometry``); ``input_dim`` should equal the lattice's
    input projection width.
    """
    return compose_system_from_configs(
        substrate=SubstrateConfig(
            precision="float32",
            noise_level=0.0,
            weight_bounds=None,
            sparsity=0.0,
            device="cpu",
        ),
        geometry=GeometryConfig.spatial_lattice(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
            lattice_dims=lattice_dims,
            connectivity_radius=1,
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        credit=CreditAssignmentConfig.gradient(),
        update=ParameterUpdateConfig.euclidean(step_size=0.1),
    )


def build_ntm_classifier(
    input_dim: int = 32,
    output_dim: int = 4,
    hidden: int = 32,
    mem_slots: int = 16,
    mem_width: int = 16,
    step_size: float = 0.05,
) -> object:
    """Backprop classification on an NTM geometry (W8.5 construction).

    LSTM controller + content-addressed external memory (static per-slot
    identity embeddings, non-negative content) with GradientCredit +
    Euclidean update. On one-step classification the memory degrades to a
    fixed learned projection — the honest quick-tier measurement is the
    2026-09-13 campaign below, not the sequential-copy regime (D20).
    """
    return compose_system_from_configs(
        substrate=SubstrateConfig(
            precision="float32",
            noise_level=0.0,
            weight_bounds=None,
            sparsity=0.0,
            device="cpu",
        ),
        geometry=GeometryConfig.ntm(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden=hidden,
            mem_slots=mem_slots,
            mem_width=mem_width,
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        credit=CreditAssignmentConfig.gradient(),
        update=ParameterUpdateConfig.euclidean(step_size=step_size),
    )


RECIPES: dict[str, Recipe] = {
    "temporal_psi": Recipe(
        name="temporal_psi",
        summary="Adaptive temporal-ψ ridge readout for frozen-backbone task "
        "switching with conflict-adaptive trace decay.",
        when_to_use="A frozen backbone must acquire/switch tasks without "
        "retraining θ; label geometry conflicts between tasks.",
        when_not="Non-conflicting incremental tasks, generative modeling, "
        "cases requiring backbone adaptation.",
        evidence=("X-TPC-001", "X-TPC-002", "X-TPC-003", "X-TAC-001"),
        build=build_temporal_psi,
    ),
    "adaptive_feedback": Recipe(
        name="adaptive_feedback",
        summary="Slow-blend adaptive feedback projection improving local "
        "descent quality per unit displacement under matched norm.",
        when_to_use="Local learning rules needing hidden-layer credit "
        "without global backward passes; matched-norm comparisons.",
        when_not="Very short horizons with a saturated task; zero/degenerate "
        "forward weights; depth beyond the validated two-layer scope.",
        evidence=("X-ALI-001", "X-ALI-002"),
        build=build_adaptive_feedback,
    ),
    "stable_amplification": Recipe(
        name="stable_amplification",
        summary="Jordan-block linear coordinate: rho <= limit while "
        "sigma_max > 1 — large transient signal retention without divergence.",
        when_to_use="Noisy linear substrates needing a transient gain boost "
        "at matched spectral radius; resonance-free short-horizon recall.",
        when_not="Isotropic-noise SNR improvement (noise is amplified at the "
        "same transient rate as signal — retention gain, not SNR gain); "
        "long-horizon memory (settling still decays the transient).",
        evidence=("X-STA-001", "X-STA-002"),
        build=build_stable_amplification,
    ),
    "role_split_muon_readout": Recipe(
        name="role_split_muon_readout",
        summary="Role-split dispatcher: Riemannian-orthogonal (Muon-class) "
        "update on the readout weight, euclidean on the rest.",
        when_to_use="Backprop MLPs where readout orthogonalization rescues "
        "one-step descent; heterogeneous update budgets.",
        when_not="Local-credit (FF×Muon) coordinates — the lift collapses "
        "under Newton–Schulz whitening at width 32.",
        evidence=("X-USU-001",),
        build=build_role_split_muon_readout,
    ),
    "epc_deep": Recipe(
        name="epc_deep",
        summary="Error-parameterized Predictive Coding (ePC): "
        "ThermodynamicContrast + error-parameterized settling + OrthoAdam on "
        "a μPC residual feedforward geometry.",
        when_to_use="Deep stacks (32+) under weight averaging/harvest; the "
        "recorded program frontier (0.917 @ d32, 3 seeds).",
        when_not="Depth ≤ 4 without harvest (EqProp-family depth wall); "
        "latency-critical inference (multi-step settling).",
        evidence=("docs/family_recipes.md#ePC", "TODO16 harvest ladder"),
        defaults={"depth": 32},
        build=build_epc_deep,
    ),
    "spatial_lattice_bp": Recipe(
        name="spatial_lattice_bp",
        summary="Backprop classification on a 3D spatial-lattice geometry — "
        "the D11 arm as a parameterized construction.",
        when_to_use="Problems with explicit 3D spatial structure; "
        "noise-robustness comparisons vs a feedforward twin.",
        when_not="Tasks without spatial structure (no advantage over an "
        "MLP at matched params); extremely wide lattices on CPU.",
        evidence=("D11 spatial_lattice_geometry_swap",),
        build=build_spatial_lattice_bp,
    ),
    "ntm_classifier": Recipe(
        name="ntm_classifier",
        summary="Backprop classification on an NTM geometry — LSTM "
        "controller + content-addressed external memory (W8.5 "
        "construction) as a parameterized lab recipe.",
        when_to_use="Sequential/memory-addressed problems; a stepping "
        "stone toward ontology-NTM continual composition (TODO17 E4).",
        when_not="Pure one-step classification (memory degenerates to a "
        "fixed projection; an MLP dominates at matched params); "
        "sequential-copy regimes are not wired into Lab's quick tier.",
        evidence=(
            "2026-09-13 ntm_classifier campaign (TODO23 §12): "
            "1.0 @ 10 epochs, 3 seeds, digital + memristive",
        ),
        build=build_ntm_classifier,
    ),
}


def build_recipe(name: str, **kwargs: object) -> object:
    recipe = RECIPES.get(name)
    if recipe is None:
        raise ValueError(f"unknown recipe {name!r}; known: {sorted(RECIPES)}")
    merged = {**recipe.defaults, **kwargs}
    return recipe.build(**merged)  # type: ignore[arg-type]
