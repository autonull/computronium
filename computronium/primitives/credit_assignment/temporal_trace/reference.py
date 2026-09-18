"""Reference implementation for Temporal Trace Credit (STDP).

Delegates to computronium.ontology.credit.TemporalTraceCredit (the source of truth).
This wrapper provides the uniform `step(case)` interface for parity/microbench.
"""

from typing import TYPE_CHECKING, Any

import torch

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    Phase,
    TemporalTraceCredit,
)
from computronium.ontology.system import SystemState

if TYPE_CHECKING:
    from computronium.ontology.geometry import Geometry


def _make_activations(tensor: torch.Tensor, n_layers: int, seed: int) -> list[torch.Tensor]:
    """Create a list of deterministic activations from a single tensor for n_layers."""
    # For a minimal feedforward network, we need input + hidden + output
    # The tensor represents the input, so we create deterministic hidden/output
    generator = torch.Generator(device=tensor.device).manual_seed(seed + 1000)
    acts = [tensor]
    for i in range(n_layers):
        acts.append(torch.randn_like(tensor, generator=generator))
    return acts


def _case_to_states(case: Any) -> dict[Phase, SystemState]:
    """Convert opaque case object to phase-keyed states for the credit protocol."""
    # TemporalTraceCredit expects activations as a list [input, hidden..., output]
    # We have 2 weight layers (input->hidden, hidden->output) so 3 activations
    seed = case.config.get("seed", 0)
    free_acts = _make_activations(case.state, 2, seed)
    nudged_acts = _make_activations(case.prediction, 2, seed + 1)

    free_state = SystemState(
        activations=free_acts,
        x=case.state,
        y=case.config.get("target"),
    )
    nudged_state = SystemState(
        activations=nudged_acts,
        x=case.state,
        y=case.config.get("target"),
    )
    return {
        Phase.FREE: free_state,
        Phase.NUDGED: nudged_state,
    }


def _case_to_geometry(case: Any) -> Geometry:
    """Create a minimal geometry from the case."""
    from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig

    # Extract dimensions from case tensors
    _, input_dim = case.state.shape
    _, output_dim = case.prediction.shape

    config = GeometryConfig.feedforward(
        input_dim=input_dim,
        output_dim=output_dim,
        hidden_dims=(output_dim,),
    )
    return FeedforwardGeometry(config)


def step(case: Any) -> list[torch.Tensor]:
    """
    Execute one reference step using the opaque case object.

    The case object is produced by cases.make_case and contains all
    tensors, parameters, and configuration needed for a small deterministic
    execution.

    Returns:
        List of pseudo-gradient tensors, one per learnable weight layer.
    """
    config = CreditAssignmentConfig.temporal_trace(
        a_plus=case.config.get("a_plus", 1.0),
        a_minus=case.config.get("a_minus", 0.5),
        tau=case.config.get("tau", 20.0),
        tau_pre=case.config.get("tau_pre", 0.9),
        tau_post=case.config.get("tau_post", 0.9),
    )
    credit = TemporalTraceCredit(config)
    states = _case_to_states(case)
    geometry = _case_to_geometry(case)
    return credit.compute_pseudo_gradient(states, None, geometry)
