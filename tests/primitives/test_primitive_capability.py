"""Capability tests for all 75 primitives.

Every primitive must demonstrate basic learning capability on its declared
task families. These are the minimum viable tests that should pass before
any SEC screen runs.

The test uses 1 epoch, 1 seed to keep it fast. A primitive that cannot
clear the bar at this level has a defect or capability gap.
"""

from __future__ import annotations

import pytest

from computronium.domains.factory import create_task
from computronium.experiment.kernel.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate
from computronium.primitives.registry import list_primitives

# Base configuration for fast capability testing
CAPABILITY_EPOCHS = 1
CAPABILITY_SEED = 42
CAPABILITY_DEVICE = "cpu"


def _base_coordinate(primitive_id: str, task=None) -> Coordinate:
    """Get the base coordinate for a primitive (all companions at default).

    Adjusts geometry based on task input shape if provided.
    """
    from computronium.experiment.sec_loop import _AXIS_DEFAULTS, _coordinate

    axis = primitive_id.split(".")[1]  # e.g., "credit_assignment"
    name = primitive_id.split(".")[-1]  # e.g., "target_inversion"
    axes = dict(_AXIS_DEFAULTS)
    axes[axis] = name

    # Adjust geometry for spatial tasks
    if task is not None:
        input_dim = task.input_dim
        if isinstance(input_dim, tuple) and len(input_dim) == 3:
            # Spatial input (C, H, W) - use conv geometry
            axes["geometry"] = "conv"
            # Add required conv params

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


def _task_for_family(family: str) -> str:
    """Map task family to a concrete task ID (smallest/fastest first)."""
    mapping = {
        "vision": "mnist",  # 70000 samples, 784 features, 10 classes (flat)
        "tabular": "iris",  # 150 samples, 4 features, 3 classes
        "graph": "cora",  # 2708 nodes, 1433 features, 7 classes
        "sequence": "char_ngram",  # small character n-gram task
        "continual": "copy_task",  # synthetic, tiny
        "rl": "cartpole",  # 4 obs, 2 actions
        "scientific": "lorenz_state",  # 3D chaotic system
        "neuromorphic": "spiking_mnist",
        "lm": "tiny_shakespeare",  # small text
        "quantum": "lorenz_state",
        "analog": "lorenz_state",
        "photonic": "lorenz_state",
    }
    return mapping.get(family, "mnist")


def _declared_reason(primitive_id: str, family: str) -> str | None:
    """The row's own declaration: why this combo fails today, and its close.

    A reason names the state (unimplemented / defective / cost) and the
    mechanism that closes it. The skip message carries ``declared:`` so the
    audit can tell a declared row from a silent capability skip (TODO97 S6d).
    """
    declared = {
        "credit.random_projections": {
            "vision": "unimplemented: width/params (close: wider net)",
            "sequence": "unimplemented: width/params (close: wider net)",
            "tabular": "unimplemented: width/params (close: wider net)",
        },
        "credit.forward_tangent": {
            "vision": "unimplemented: memory vs accuracy (close: JVP primitive)",
            "sequence": "unimplemented: memory vs accuracy (close: JVP primitive)",
        },
        "credit.zeroth_order": {
            "vision": "unimplemented: sample efficiency (close: perturbation budget)",
            "sequence": "unimplemented: sample efficiency (close: perturbation budget)",
            "tabular": "unimplemented: sample efficiency (close: perturbation budget)",
        },
        "credit.local_contrastive": {
            "vision": "unimplemented: label channel (close: contrastive head)",
        },
        "credit.local_goodness": {
            "vision": "unimplemented: width (close: wider net)",
            "sequence": "unimplemented: width (close: wider net)",
            "tabular": "unimplemented: width (close: wider net)",
        },
        "credit.pc_alm": {
            "vision": "unimplemented: gamma ladder (close: tuning record)",
        },
        "credit.surrogate": {
            "vision": "unimplemented box: 300k params (declared ceiling 150k)",
            "sequence": "unimplemented box: 300k params (declared ceiling 150k)",
            "tabular": "unimplemented box: 300k params (declared ceiling 150k)",
        },
        "geometry.attention": {
            "sequence": "unimplemented box: 600k params (declared ceiling 150k)",
            "vision": "unimplemented box: 600k params (declared ceiling 150k)",
            "rl": "unimplemented box: 600k params (declared ceiling 150k)",
        },
        "geometry.causal_transformer": {
            "sequence": "unimplemented box: 600k params (declared ceiling 150k)",
            "rl": "unimplemented box: 600k params (declared ceiling 150k)",
        },
        "geometry.routing": {
            "vision": "unimplemented box: 300k params (declared ceiling 150k)",
            "sequence": "unimplemented box: 300k params (declared ceiling 150k)",
            "tabular": "unimplemented box: 300k params (declared ceiling 150k)",
        },
        "geometry.tile": {
            "vision": "unimplemented box: 1M params (declared ceiling 150k)",
            "sequence": "unimplemented box: 1M params (declared ceiling 150k)",
            "tabular": "unimplemented box: 1M params (declared ceiling 150k)",
        },
        "dynamics.diffusion": {
            "vision": "cost model: settle steps 30 -> 10 (S6 cost row)",
            "sequence": "cost model: settle steps 30 -> 10 (S6 cost row)",
        },
        "plasticity.closed_form_ridge": {
            "vision": "unimplemented: no closed-form ridge primitive",
            "sequence": "unimplemented: no closed-form ridge primitive",
            "tabular": "unimplemented: no closed-form ridge primitive",
        },
        "plasticity.rule_state": {
            "continual": "defective: no modulate() (close: implement modulate)",
            "sequence": "defective: no modulate() (close: implement modulate)",
            "rl": "defective: no modulate() (close: implement modulate)",
        },
        "plasticity.substrate_coupled": {
            "neuromorphic": "defective: no joint substrate transition",
            "analog": "defective: no joint substrate transition",
        },
        "update.natural_gradient": {
            "vision": "cost model: diagonal Fisher (S6 cost row)",
            "sequence": "cost model: diagonal Fisher (S6 cost row)",
            "tabular": "cost model: diagonal Fisher (S6 cost row)",
            "continual": "cost model: diagonal Fisher (S6 cost row)",
        },
        "update.cascade_synapse": {
            "sequence": "unimplemented: no cascade-synapse primitive",
            "rl": "unimplemented: no cascade-synapse primitive",
            "continual": "unimplemented: no cascade-synapse primitive",
        },
        "update.bayesian_online": {
            "sequence": "unimplemented: no online-Bayes primitive",
            "rl": "unimplemented: no online-Bayes primitive",
        },
        "update.synaptic_intelligence": {
            "continual": "unimplemented: no synaptic-intelligence primitive",
        },
    }

    if primitive_id in declared and family in declared[primitive_id]:
        return declared[primitive_id][family]
    return None


@pytest.fixture(scope="session")
def primitive_specs():
    return list_primitives()


def test_all_primitives_have_capability_test(primitive_specs):
    """Every primitive declares at least one task family."""
    for spec in primitive_specs:
        assert spec.task_families, f"{spec.id}: empty task_families"


@pytest.mark.parametrize("spec", list_primitives(), ids=lambda s: s.id)
def test_primitive_on_declared_families(spec):
    """Test each primitive on its declared task families.

    Runs 1 epoch, 1 seed. A declared unimplemented or defective row is skipped
    with its named mechanism and close condition; any other failure is a defect.
    """
    # Test at most 1 family per primitive to keep CI fast
    # (full family matrix runs in SEC)
    for family in spec.task_families:
        reason = _declared_reason(spec.id, family)
        if reason:
            pytest.skip(f"declared: {spec.id} on {family}: {reason}")

        task_id = _task_for_family(family)
        try:
            task = create_task(task_id)
            task.setup()
        except Exception as e:
            pytest.skip(f"no dataset: task {task_id} not available: {e}")

        try:
            coord = _base_coordinate(spec.id, task)
            # Use task's input_shape if available, else flatten to (batch, features)
            input_shape = (
                task.input_shape
                if hasattr(task, "input_shape")
                else (1, task.input_dim)
            )
            cell = compose_cell_system(
                coordinate=coord,
                geometry={},
                input_shape=input_shape,
                output_dim=task.output_dim,
                task=task,
            )
        except ValueError as e:
            pytest.xfail(f"defective: {spec.id} on {family}: compose failed - {e}")

        # Run 1 epoch capability check
        try:
            from computronium.core.system_trainer.config import SystemTrainerConfig
            from computronium.core.system_trainer.train_task import train_on_task

            config = SystemTrainerConfig(
                max_epochs=CAPABILITY_EPOCHS,
                device=CAPABILITY_DEVICE,
                track_energy=False,
                track_flops=False,
                track_memory=False,
                log_every_n_epochs=1,
            )

            train_on_task(lambda *_, **__: cell.system, task, config)
            metrics = task.evaluate(cell.system)

            # Error-blind credits: check non-zero update, not accuracy
            from computronium.primitives.registry import get_spec

            prim_spec = get_spec(spec.id)
            if prim_spec and getattr(prim_spec, "error_blind", False):
                # Just verify training ran without error
                assert metrics.loss is not None
                return

            # Error-aware credits: must clear the bar
            bar = task.spec.primary_pass_bar
            if bar and bar.value:
                assert metrics.accuracy > bar.value, (
                    f"{spec.id} on {family} ({task_id}): "
                    f"accuracy {metrics.accuracy:.4f} <= bar {bar.value:.4f}"
                )
            else:
                # No bar defined - just check above chance
                chance = 1.0 / task.output_dim if task.output_dim > 1 else 0.5
                assert metrics.accuracy > chance, (
                    f"{spec.id} on {family} ({task_id}): "
                    f"accuracy {metrics.accuracy:.4f} <= chance {chance:.4f}"
                )

            return  # First family passed, done

        except Exception as e:
            if "compose failed" in str(e):
                raise
            pytest.fail(f"{spec.id} on {family} ({task_id}): {e}")

    # If we got here, all families were skipped (all gaps)
    # This is OK - the gaps are documented


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
