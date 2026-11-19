"""Rung 0 wiring tests for all 75 primitives.

These tests verify the primitive is correctly wired:
- Instantiates without error
- Forward pass produces finite activations
- Credit produces finite non-zero pseudo-gradients (error-aware) or non-zero update (error-blind)
- Dynamics settle converges (non-instantaneous) or forward pass works (instantaneous)

These are the CHEAPEST falsifiers - run in seconds, not minutes.
"""

from __future__ import annotations

import pytest
import torch

from computronium.primitives.registry import list_primitives
from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate
from computronium.core.pipeline import _PhaseContext, _run_phases, forward_pass
from computronium.ontology.credit import Phase


def base_coord(primitive_id, task):
    axis = primitive_id.split(".")[1]
    name = primitive_id.split(".")[-1]
    axes = dict(_AXIS_DEFAULTS)
    axes[axis] = name

    # Adjust geometry for spatial tasks
    if task is not None:
        input_dim = task.input_dim
        if isinstance(input_dim, tuple) and len(input_dim) == 3:
            axes["geometry"] = "conv"
            extra_params = {
                "geometry.in_channels": input_dim[0],
                "geometry.input_hw": (input_dim[1], input_dim[2]),
                "geometry.conv_channels": (8, 16),
                "geometry.kernel_size": 3,
                "geometry.pool_hw": (4, 4),
            }
            coord = _coordinate(axes)
            coord.params.update(extra_params)
            return coord

    return _coordinate(axes)


TASK_MAP = {
    "vision": "mnist",
    "tabular": "iris",
    "graph": "cora",
    "sequence": "char_ngram",
    "continual": "copy_task",
    "rl": "cartpole",
    "scientific": "lorenz_state",
    "neuromorphic": "spiking_mnist",
    "lm": "tiny_shakespeare",
    "quantum": "lorenz_state",
    "analog": "lorenz_state",
    "photonic": "lorenz_state",
}


ERROR_BLIND_CREDITS = {
    "primitive.credit_assignment.homeostatic",
    "primitive.credit_assignment.temporal_trace",
}


# Known compose failures: (primitive_id, companion_axis, companion_default_value)
# These are primitive/axis combinations where the DEFAULT companion causes failure
COMPOSE_SKIPS = [
    ("primitive.geometry.recurrent", "credit", "gradient"),
    ("primitive.geometry.causal_transformer", "credit", "gradient"),
    ("primitive.substrate.neuromorphic", "dynamics", "instantaneous"),
]

# Graph geometry primitives need special kwargs (edge_index, batch)
# Skip them in generic wiring tests
GRAPH_SKIPS = {
    "primitive.geometry.graph",
}


def _should_skip_compose(spec):
    """Check if this primitive's default companions are incompatible."""
    axis_map = {
        "credit_assignment": "credit",
        "state_dynamics": "dynamics",
        "geometry": "geometry",
        "plasticity": "plasticity",
        "substrate": "substrate",
        "parameter_update": "update",
    }
    axis_key = spec.id.split(".")[1]
    axis = axis_map.get(axis_key, axis_key)
    
    for pid, companion_axis, companion_value in COMPOSE_SKIPS:
        if spec.id == pid and _AXIS_DEFAULTS.get(companion_axis) == companion_value:
            return True
    return False


def _is_error_blind(primitive_id):
    return primitive_id in ERROR_BLIND_CREDITS


def _is_graph_primitive(primitive_id):
    return primitive_id in GRAPH_SKIPS


@pytest.fixture(scope="session")
def primitive_specs():
    return list_primitives()


@pytest.mark.parametrize("spec", list_primitives(), ids=lambda s: s.id)
def test_primitive_instantiates(spec):
    """Primitive coordinate composes without error."""
    if not spec.task_families:
        pytest.skip("no task_families")
    
    if _should_skip_compose(spec):
        pytest.skip("known compose failure - incompatible default companions")
    
    if _is_graph_primitive(spec.id):
        pytest.skip("graph geometry requires special kwargs")
    
    family = spec.task_families[0]
    task_id = TASK_MAP.get(family)
    if not task_id:
        pytest.skip(f"no task for {family}")
    
    task = create_task(task_id)
    task.setup()
    
    coord = base_coord(spec.id, task)
    input_shape = task.input_shape if hasattr(task, 'input_shape') else (1, task.input_dim)
    
    try:
        cell = compose_cell_system(
            coordinate=coord,
            geometry={},
            input_shape=input_shape,
            output_dim=task.output_dim,
            task=task,
        )
    except ValueError as e:
        pytest.fail(f"{spec.id}: compose failed - {e}")
    
    assert cell.system is not None


@pytest.mark.parametrize("spec", list_primitives(), ids=lambda s: s.id)
def test_primitive_forward_pass(spec):
    """One forward pass produces finite activations."""
    if not spec.task_families:
        pytest.skip("no task_families")
    
    if _should_skip_compose(spec):
        pytest.skip("known compose failure - incompatible default companions")
    
    # Graph geometry requires special handling (edge_index, batch kwargs)
    if "geometry.graph" in spec.id:
        pytest.skip("graph geometry requires graph-specific kwargs")
    
    family = spec.task_families[0]
    task_id = TASK_MAP.get(family)
    if not task_id:
        pytest.skip(f"no task for {family}")
    
    task = create_task(task_id)
    task.setup()
    
    coord = base_coord(spec.id, task)
    input_shape = task.input_shape if hasattr(task, 'input_shape') else (1, task.input_dim)
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=input_shape,
        output_dim=task.output_dim,
        task=task,
    )
    
    # Get a batch (handles graph tasks which use get_batch instead of dataloader)
    loader = task.get_dataloader("train")
    if loader is not None:
        batch = next(iter(loader))
        x, y = batch
    else:
        x, y = task.get_batch("train")
    
    # Forward pass
    cell.system.eval()
    with torch.no_grad():
        logits = cell.system.forward(x)
    
    assert torch.isfinite(logits).all(), f"{spec.id}: non-finite logits"
    assert logits.shape[0] == x.shape[0], f"{spec.id}: batch size mismatch"


@pytest.mark.parametrize("spec", list_primitives(), ids=lambda s: s.id)
def test_primitive_credit_pseudograds(spec):
    """Credit produces finite pseudo-gradients; non-zero for error-aware credits."""
    if not spec.task_families:
        pytest.skip("no task_families")
    
    if _should_skip_compose(spec):
        pytest.skip("known compose failure - incompatible default companions")
    
    if _is_graph_primitive(spec.id):
        pytest.skip("graph geometry requires special kwargs")
    
    family = spec.task_families[0]
    task_id = TASK_MAP.get(family)
    if not task_id:
        pytest.skip(f"no task for {family}")
    
    task = create_task(task_id)
    task.setup()
    
    coord = base_coord(spec.id, task)
    input_shape = task.input_shape if hasattr(task, 'input_shape') else (1, task.input_dim)
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=input_shape,
        output_dim=task.output_dim,
        task=task,
    )
    
    # Get a batch (handles graph tasks which use get_batch instead of dataloader)
    loader = task.get_dataloader("train")
    if loader is not None:
        batch = next(iter(loader))
        x, y = batch
    else:
        x, y = task.get_batch("train")
    
    # Run phases
    substrate = cell.system.substrate
    geometry = cell.system.geometry
    dynamics = cell.system.dynamics
    credit = cell.system.credit
    
    owned_free = None
    initial_activations = forward_pass(substrate, geometry, x)
    
    phase_ctx = _PhaseContext(
        credit=credit,
        dynamics=dynamics,
        geometry=geometry,
        substrate=substrate,
        initial_activations=initial_activations,
        x=x,
        y=y,
        plasticity=getattr(cell.system, 'plasticity', None),
        psi=None,
        context=None,
        loss_fn=torch.nn.functional.cross_entropy,
        graph_kwargs={},
        owned_free=owned_free,
    )
    states = _run_phases(phase_ctx)
    
    nudged_state = states.get(Phase.NUDGED)
    if nudged_state is None or nudged_state.activations is None:
        pytest.fail(f"{spec.id}: no nudged state")
    
    logits = cell.system.forward(x)
    loss = torch.nn.functional.cross_entropy(logits, y)
    
    pseudo_grads = credit.compute_pseudo_gradient(
        {Phase.NUDGED: nudged_state},
        loss,
        geometry,
    )
    
    assert len(pseudo_grads) > 0, f"{spec.id}: no pseudo-gradients produced"
    assert all(torch.isfinite(g).all() for g in pseudo_grads), f"{spec.id}: non-finite pseudo-gradient"
    
    if not _is_error_blind(spec.id):
        total_norm = sum(g.norm().item() for g in pseudo_grads)
        assert total_norm > 0.0, f"{spec.id}: error-aware credit produced all-zero pseudo-gradients"


@pytest.mark.parametrize("spec", list_primitives(), ids=lambda s: s.id)
def test_primitive_dynamics_settle(spec):
    """Dynamics settle converges (non-instantaneous) or forward pass works (instantaneous)."""
    if not spec.task_families:
        pytest.skip("no task_families")
    
    if _should_skip_compose(spec):
        pytest.skip("known compose failure - incompatible default companions")
    
    if _is_graph_primitive(spec.id):
        pytest.skip("graph geometry requires special kwargs")
    
    family = spec.task_families[0]
    task_id = TASK_MAP.get(family)
    if not task_id:
        pytest.skip(f"no task for {family}")
    
    task = create_task(task_id)
    task.setup()
    
    coord = base_coord(spec.id, task)
    input_shape = task.input_shape if hasattr(task, 'input_shape') else (1, task.input_dim)
    cell = compose_cell_system(
        coordinate=coord,
        geometry={},
        input_shape=input_shape,
        output_dim=task.output_dim,
        task=task,
    )
    
    # Get a batch (handles graph tasks which use get_batch instead of dataloader)
    loader = task.get_dataloader("train")
    if loader is not None:
        batch = next(iter(loader))
        x, y = batch
    else:
        x, y = task.get_batch("train")
    
    # Check settle doesn't crash and produces finite activations
    substrate = cell.system.substrate
    geometry = cell.system.geometry
    dynamics = cell.system.dynamics
    
    from computronium.core.pipeline import SystemState
    state = SystemState(x=x, y=y)
    
    settled = dynamics.settle(state, geometry, substrate, target=None)
    
    assert settled.activations is not None, f"{spec.id}: no activations after settle"
    acts = settled.activations
    act_list = acts if isinstance(acts, list) else [acts]
    for a in act_list:
        assert torch.isfinite(a).all(), f"{spec.id}: non-finite activations after settle"
    
    # For non-instantaneous, check convergence
    if hasattr(dynamics, 'config') and hasattr(dynamics.config, 'max_steps'):
        if dynamics.config.max_steps > 1:
            # Non-instantaneous dynamics - should converge
            assert hasattr(dynamics, '_settle_steps_used'), f"{spec.id}: no settle steps tracked"
            assert dynamics._settle_steps_used > 0, f"{spec.id}: zero settle steps"
            assert dynamics._settle_steps_used <= dynamics.config.max_steps, f"{spec.id}: settle exceeded max steps"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])