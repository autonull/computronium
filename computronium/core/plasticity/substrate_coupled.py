"""Substrate-Coupled Plasticity: Reuse substrate physics as plasticity."""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.core.identity_card import AlgorithmIdentityCard
from computronium.core.joint.transition import PlasticityConfig

if TYPE_CHECKING:
    from torch import Tensor

if TYPE_CHECKING:
    from computronium.state import CompositeState, SystemContext


class SubstrateCoupledPlasticity:
    """Substrate-coupled plasticity: reuse substrate adapters as physical plasticity.

    In this formulation, the plastic state ψ IS the substrate state σ
    (or a subset thereof). The plasticity dynamics are exactly the
    substrate's physical evolution laws (memristive drift, analog noise,
    quantum decoherence, etc.).

    This is a no-op at the plasticity protocol level — the substrate
    itself handles state evolution through its forward/update operators.

    ψ ≡ σ  (plastic state is substrate state)
    """

    IDENTITY_CARD = AlgorithmIdentityCard(
        name="SubstrateCoupledPlasticity",
        reference_equations="physical plasticity = substrate state evolution (memristive drift, analog noise, decoherence); internal formulation",
        deviations_from_literature=(
            "no separate plasticity law: ψ ≡ σ, a no-op at the plasticity "
            "protocol level — the substrate's forward/update operators "
            "carry all dynamics",
        ),
        objective_function=None,
        pseudo_gradient_def="none (substrate weight_update_operator evolves σ within the joint transition)",
        symmetry_requirements=("inherits the substrate's physical constraints",),
        approximation_parameters=(),
        validated_limits=(
            "J4 lock: substrate_owned variables mutate only via "
            "Substrate.forward_operator; physical-hardware validation is "
            "future work (simulated substrates only)",
        ),
    )

    config: PlasticityConfig

    def __init__(self, **kwargs) -> None:
        """Initialize substrate-coupled plasticity.

        Args:
            **kwargs: Ignored (kept for config compatibility).
        """
        self.config = PlasticityConfig.substrate_coupled()

    def initial_psi(
        self, context: SystemContext | None, batch_size: int = 1
    ) -> dict[str, Tensor]:
        """Create initial plastic state.

        Substrate-coupled plasticity has no separate plastic state —
        plasticity IS the substrate state evolution.

        Args:
            context: System context (unused).
            batch_size: Batch size (unused, kept for protocol compliance).

        Returns:
            Empty dict (ψ is empty, substrate state in σ).
        """
        return {}

    def step(
        self,
        psi: dict[str, Tensor],
        z: CompositeState,
        context: SystemContext,
    ) -> dict[str, Tensor]:
        """No-op at plasticity level.

        Substrate state evolution is handled by the substrate's
        weight_update operator within the joint transition.

        Args:
            psi: Current plastic state (empty).
            z: Full joint state (substrate state in z.substrate).
            context: Immutable system context.

        Returns:
            Unchanged plastic state (empty).
        """
        return psi


def create_substrate_coupled_plasticity(
    config: PlasticityConfig,
) -> SubstrateCoupledPlasticity:
    """Factory to create SubstrateCoupledPlasticity from PlasticityConfig.

    Args:
        config: PlasticityConfig with plasticity_type="substrate_coupled".

    Returns:
        SubstrateCoupledPlasticity instance.

    Raises:
        ValueError: If config is not substrate_coupled type.
    """
    if config.plasticity_type != "substrate_coupled":
        raise ValueError(
            f"Expected substrate_coupled config, got {config.plasticity_type}"
        )

    return SubstrateCoupledPlasticity(**(config.consolidation_config or {}))
