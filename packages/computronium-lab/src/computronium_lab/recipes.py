"""Validated mechanism recipes — wrapped from the extracted platform packages.

Each recipe carries its scope and evidence references; nothing here invents
new mechanism semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from computronium.core.system_trainer.spec import compose_system_from_configs
from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics._dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.update import ParameterUpdateConfig

if TYPE_CHECKING:
    from collections.abc import Callable


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
}


def build_recipe(name: str, **kwargs: object) -> object:
    recipe = RECIPES.get(name)
    if recipe is None:
        raise ValueError(f"unknown recipe {name!r}; known: {sorted(RECIPES)}")
    merged = {**recipe.defaults, **kwargs}
    return recipe.build(**merged)  # type: ignore[arg-type]
