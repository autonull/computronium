"""Reference implementation for NTM Geometry.

Delegates to computronium.ontology.geometry.NtmGeometry. This wrapper provides
the uniform `forward(case)` interface for parity/microbench.
"""

from typing import Any

import torch

from computronium.ontology.substrate import DigitalSubstrate, SubstrateConfig


def _case_to_input(case: Any) -> torch.Tensor:
    """Extract input tensor from case."""
    return case.state


def _case_to_substrate(case: Any) -> DigitalSubstrate:
    """Create substrate from case config."""
    device = case.state.device
    return DigitalSubstrate(SubstrateConfig.digital(device=device))


def forward(case: Any) -> torch.Tensor:
    """Execute reference forward pass using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        Output logits tensor of shape (batch, seq_len, output_dim).
    """
    # Use pre-created geometry from case for determinism
    geometry = case.geometry

    # Get input
    x = _case_to_input(case)

    # Get substrate
    substrate = _case_to_substrate(case)

    # Run forward with deterministic RNG state
    rng_state = torch.get_rng_state()
    torch.manual_seed(case.config.get("seed", 0))
    try:
        output = geometry(x, substrate)
    finally:
        torch.set_rng_state(rng_state)

    return output


# Alias for the central registry test which expects `step`
step = forward
