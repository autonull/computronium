"""Mechanism candidate catalog (TODO23 T23.1.4).

Each entry is a validated construction path (existing preset or recipe —
nothing new is invented here) with Pareto metadata, predictor features, and
a config builder for hard `SystemConfig.validate()` screening.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.system import SystemConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium_lab.synthesis.predictor import MechanismFeatures

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium_lab.synthesis.spec import ProblemSpec


@dataclass(frozen=True, slots=True)
class Pareto:
    """Pareto metadata for one mechanism (measured, not speculative)."""

    accuracy: float
    latency_ms: float
    memory_gb: float
    stability: float
    adaptation_speed: float = 0.0


@dataclass(frozen=True, slots=True)
class MechanismCandidate:
    """One synthesizable mechanism: a coordinate plus its build path."""

    name: str
    credit: str
    update: str
    geometry: str = "mlp"
    mechanism_class: str = "null"
    plasticity: str = "null"
    depth: int = 2
    width: int = 128
    interaction_i: float = 0.0
    substrates: tuple[str, ...] = ("digital",)
    local_credit: bool = False
    continual_capable: bool = False
    build_kind: str = "preset"  # "preset" | "recipe"
    build_name: str = ""
    pareto: Pareto = Pareto(0.5, 10.0, 1.0, 0.5)
    provenance: str = ""
    config_builder: Callable[[str, str], SystemConfig] | None = None
    recipe_kwargs: tuple[tuple[str, str], ...] = field(default=())

    def features(self, spec: ProblemSpec) -> MechanismFeatures:
        return MechanismFeatures(
            credit_class=_credit_class(self.credit),
            update_class=_update_class(self.update),
            geometry=self.geometry,
            geometry_class=_geometry_class(self.geometry),
            task=_task_domain(spec.dataset),
            mechanism_class=self.mechanism_class,
            plasticity=self.plasticity,
            depth=self.depth,
            width=self.width,
            interaction_i=self.interaction_i,
        )

    def coordinate(self) -> dict[str, str]:
        return {
            "substrate": "+".join(self.substrates),
            "geometry": self.geometry,
            "dynamics": _dynamics_name(self),
            "plasticity": self.plasticity,
            "credit": self.credit,
            "update": self.update,
        }

    def build(self, spec: ProblemSpec) -> object:
        """Compose the mechanism from its registered construction path."""
        from computronium_lab.presets import build_system_preset
        from computronium_lab.recipes import build_recipe

        if self.build_kind == "recipe":
            kwargs: dict[str, object] = {
                key: getattr(spec, arg) for key, arg in self.recipe_kwargs
            }
            return build_recipe(self.build_name, **kwargs)
        return build_system_preset(
            self.build_name,
            input_dim=spec.input_dim,
            output_dim=spec.num_classes,
        )


def _credit_class(credit: str) -> str:
    from computronium_lab.synthesis.predictor import CREDIT_CLASS

    return CREDIT_CLASS.get(credit, "other")


def _update_class(update: str) -> str:
    from computronium_lab.synthesis.predictor import UPDATE_CLASS

    return UPDATE_CLASS.get(update, "other")


def _geometry_class(geometry: str) -> str:
    from computronium_lab.synthesis.predictor import GEOMETRY_CLASS

    return GEOMETRY_CLASS.get(geometry, "other")


def _task_domain(dataset: str) -> str:
    """Map a user dataset onto the closest measured task domain."""
    lower = dataset.lower()
    if any(k in lower for k in ("mnist", "cifar", "vision", "image")):
        return "mnist"
    return "ordinary"


def _dynamics_name(candidate: MechanismCandidate) -> str:
    return "energy_minimization" if candidate.geometry == "eqprop" else "instantaneous"


def _substrate_config(name: str, precision: str) -> SubstrateConfig:
    if name == "memristive":
        return SubstrateConfig.memristive()
    if name == "neuromorphic":
        return SubstrateConfig.neuromorphic()
    return SubstrateConfig.digital(precision=precision)


def _mlp_config_builder(
    credit_config: Callable[[], object], update_config: Callable[[], object]
) -> Callable[[str, str], SystemConfig]:
    def build(substrate: str, precision: str) -> SystemConfig:
        return SystemConfig(
            substrate=_substrate_config(substrate, precision),
            geometry=GeometryConfig.feedforward(
                input_dim=32, output_dim=4, hidden_dims=(64, 32)
            ),
            dynamics=StateDynamicsConfig.instantaneous(),
            credit=credit_config(),  # type: ignore[arg-type]
            update=update_config(),  # type: ignore[arg-type]
        )

    return build


def _bp_config(substrate: str, precision: str) -> SystemConfig:
    return _mlp_config_builder(
        CreditAssignmentConfig.gradient,
        lambda: ParameterUpdateConfig.euclidean(step_size=0.01),
    )(substrate, precision)


def _ff_config(substrate: str, precision: str) -> SystemConfig:
    return _mlp_config_builder(
        CreditAssignmentConfig.local_goodness,
        lambda: ParameterUpdateConfig.euclidean(step_size=0.03),
    )(substrate, precision)


def _fa_config(substrate: str, precision: str) -> SystemConfig:
    return _mlp_config_builder(
        lambda: CreditAssignmentConfig.random_projections(
            beta=0.5, feedback_scale=0.01
        ),
        lambda: ParameterUpdateConfig.euclidean(step_size=0.05),
    )(substrate, precision)


def _pepita_config(substrate: str, precision: str) -> SystemConfig:
    return _mlp_config_builder(
        CreditAssignmentConfig.pepita,
        lambda: ParameterUpdateConfig.euclidean(step_size=0.01),
    )(substrate, precision)


def _role_split_config(substrate: str, precision: str) -> SystemConfig:
    return SystemConfig(
        substrate=_substrate_config(substrate, precision),
        geometry=GeometryConfig.feedforward(
            input_dim=32, output_dim=4, hidden_dims=(64, 32)
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        credit=CreditAssignmentConfig.gradient(),
        update=ParameterUpdateConfig.role_split(
            role_names=("4.weight",),
            on_role=ParameterUpdateConfig.riemannian_orthogonal(step_size=0.01),
            other=ParameterUpdateConfig.euclidean(step_size=0.05),
        ),
    )


CATALOG: tuple[MechanismCandidate, ...] = (
    MechanismCandidate(
        name="backprop_mlp",
        credit="bp",
        update="euclid",
        substrates=("digital", "memristive", "neuromorphic"),
        build_name="backprop_mlp",
        pareto=Pareto(accuracy=0.91, latency_ms=5.0, memory_gb=1.2, stability=0.95),
        provenance="w1_credit_ladder: bp×euclid 0.91 @ d2",
        config_builder=_bp_config,
    ),
    MechanismCandidate(
        name="role_split_muon_readout",
        credit="bp",
        update="ortho",
        substrates=("digital",),
        build_kind="recipe",
        build_name="role_split_muon_readout",
        pareto=Pareto(accuracy=0.92, latency_ms=6.0, memory_gb=1.4, stability=0.9),
        provenance="X-USU-001: role-split readout beats both parents on mlp",
        config_builder=_role_split_config,
    ),
    MechanismCandidate(
        name="temporal_psi_task_switcher",
        credit="bp",
        update="euclid",
        plasticity="psi",
        substrates=("digital",),
        local_credit=False,
        continual_capable=True,
        build_kind="recipe",
        build_name="temporal_psi",
        recipe_kwargs=(("feature_dim", "input_dim"), ("num_classes", "num_classes")),
        pareto=Pareto(
            accuracy=0.9,
            latency_ms=5.0,
            memory_gb=0.6,
            stability=0.92,
            adaptation_speed=0.9,
        ),
        provenance="X-TPC-001..003: frozen-θ task switching via temporal ψ",
        config_builder=_bp_config,
    ),
    MechanismCandidate(
        name="ff_mlp",
        credit="ff",
        update="euclid",
        local_credit=True,
        substrates=("digital", "neuromorphic"),
        build_name="ff_mlp",
        pareto=Pareto(accuracy=0.83, latency_ms=4.0, memory_gb=0.4, stability=0.9),
        provenance="w1_credit_ladder: ff×euclid 0.83 @ d2",
        config_builder=_ff_config,
    ),
    MechanismCandidate(
        name="fa_mlp",
        credit="fa",
        update="euclid",
        substrates=("digital",),
        build_name="fa_mlp",
        pareto=Pareto(accuracy=0.38, latency_ms=4.5, memory_gb=0.8, stability=0.6),
        provenance="w1_credit_ladder: fa×euclid 0.38 @ d2 (rescued only by muon)",
        config_builder=_fa_config,
    ),
    MechanismCandidate(
        name="pepita_mlp",
        credit="pepita",
        update="euclid",
        substrates=("digital",),
        build_name="pepita_mlp",
        pareto=Pareto(accuracy=0.10, latency_ms=6.0, memory_gb=1.0, stability=0.5),
        provenance="w1_credit_ladder: pepita×euclid ≈0.10 @ d2 (home update: adam)",
        config_builder=_pepita_config,
    ),
)


__all__ = ["CATALOG", "MechanismCandidate", "Pareto"]
