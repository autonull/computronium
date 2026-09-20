"""Accelerated kernel for Rule State Plasticity.

Delegates to computronium.core.plasticity.rule_state.RuleStatePlasticity with triton acceleration.
Provides uniform `step(case)` interface.
"""

from typing import Any

from computronium.acceleration.backends import kernel_available

KERNEL_TECHNOLOGY = "triton"


def is_available() -> bool:
    return kernel_available(KERNEL_TECHNOLOGY)


def step(case: Any) -> Any:
    """Execute one accelerated step using the opaque case object."""
    if not is_available():
        from .reference import step as reference_step

        return reference_step(case)

    # Use accelerated implementation
    import torch

    from computronium.core.plasticity.rule_state import RuleStatePlasticity
    from computronium.state import CompositeState

    # Set seed BEFORE creating plasticity to ensure deterministic initialization
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        plasticity = RuleStatePlasticity(
            num_operators=case.config.get("num_operators", 4),
            operator_dim=case.config.get("operator_dim", 8),
            controller_hidden=case.config.get("controller_hidden", 16),
            temperature=case.config.get("temperature", 1.0),
            learning_rate=case.config.get("learning_rate", 0.01),
            decay=case.config.get("decay", 0.99),
            device=case.state.device,
        )

        psi = case.psi
        z = CompositeState(
            activity={"x": case.state},
            plastic={},
            substrate={},
        )

        class _MockContext:
            def __init__(self, device: torch.device):
                self._device = device

            @property
            def device(self) -> torch.device:
                return self._device

        context = _MockContext(device=case.state.device)

        new_psi = plasticity.step(psi, z, context)  # type: ignore[arg-type]
    finally:
        torch.set_rng_state(rng_state)
    return new_psi
