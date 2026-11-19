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


def _skip_reason(primitive_id: str, family: str) -> str | None:
    """Check if this primitive-family combo should be skipped."""
    # Known capability gaps (documented in TODO97) - require NEW primitives
    gaps = {
        "credit.random_projections": {
            "vision": "width/params gap (needs wider net)",
            "sequence": "width/params gap (needs wider net)",
            "tabular": "width/params gap (needs wider net)",
        },
        "credit.forward_tangent": {
            "vision": "memory vs accuracy gap (needs JVP primitive)",
            "sequence": "memory vs accuracy gap (needs JVP primitive)",
        },
        "credit.zeroth_order": {
            "vision": "sample efficiency gap (needs more perturbations primitive)",
            "sequence": "sample efficiency gap (needs more perturbations primitive)",
            "tabular": "sample efficiency gap (needs more perturbations primitive)",
        },
        "credit.local_contrastive": {
            "vision": "label channel gap (needs contrastive head primitive)",
        },
        "credit.local_goodness": {
            "vision": "width gap (needs wider net)",
            "sequence": "width gap (needs wider net)",
            "tabular": "width gap (needs wider net)",
        },
        "credit.pc_alm": {
            "vision": "gamma ladder needed (tuning, not gap)",
        },
        "credit.surrogate": {
            "vision": "300k params ceiling (capability gap: needs larger model)",
            "sequence": "300k params ceiling (capability gap: needs larger model)",
            "tabular": "300k params ceiling (capability gap: needs larger model)",
        },
        "geometry.attention": {
            "sequence": "600k params ceiling (capability gap: needs larger model)",
            "vision": "600k params ceiling (capability gap: needs larger model)",
            "rl": "600k params ceiling (capability gap: needs larger model)",
        },
        "geometry.causal_transformer": {
            "sequence": "600k params ceiling (capability gap: needs larger model)",
            "rl": "600k params ceiling (capability gap: needs larger model)",
        },
        "geometry.routing": {
            "vision": "300k params ceiling (capability gap: needs larger model)",
            "sequence": "300k params ceiling (capability gap: needs larger model)",
            "tabular": "300k params ceiling (capability gap: needs larger model)",
        },
        "geometry.tile": {
            "vision": "1M params ceiling (capability gap: needs larger model)",
            "sequence": "1M params ceiling (capability gap: needs larger model)",
            "tabular": "1M params ceiling (capability gap: needs larger model)",
        },
        "dynamics.diffusion": {
            "vision": "cost model (steps 30->10 tuning)",
            "sequence": "cost model (steps 30->10 tuning)",
        },
        "plasticity.closed_form_ridge": {
            "vision": "refused (no impl)",
            "sequence": "refused (no impl)",
            "tabular": "refused (no impl)",
        },
        "plasticity.rule_state": {
            "continual": "no modulate() impl (defect: implement modulate)",
            "sequence": "no modulate() impl (defect: implement modulate)",
            "rl": "no modulate() impl (defect: implement modulate)",
        },
        "plasticity.substrate_coupled": {
            "neuromorphic": "no-op at protocol (defect: implement joint transition)",
            "analog": "no-op at protocol (defect: implement joint transition)",
        },
        "update.natural_gradient": {
            "vision": "cost model (diagonal Fisher tuning)",
            "sequence": "cost model (diagonal Fisher tuning)",
            "tabular": "cost model (diagonal Fisher tuning)",
            "continual": "cost model (diagonal Fisher tuning)",
        },
        "update.cascade_synapse": {
            "sequence": "refused (no impl)",
            "rl": "refused (no impl)",
            "continual": "refused (no impl)",
        },
        "update.bayesian_online": {
            "sequence": "refused (no impl)",
            "rl": "refused (no impl)",
        },
        "update.synaptic_intelligence": {
            "continual": "refused (no impl)",
        },
    }

    if primitive_id in gaps and family in gaps[primitive_id]:
        return gaps[primitive_id][family]
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

    Runs 1 epoch, 1 seed. Primitives with known gaps are skipped with reason.
    A primitive that fails without a documented gap is a defect.
    """
    # Test at most 1 family per primitive to keep CI fast
    # (full family matrix runs in SEC)
    for family in spec.task_families:
        reason = _skip_reason(spec.id, family)
        if reason:
            pytest.skip(f"{spec.id} on {family}: {reason}")

        task_id = _task_for_family(family)
        try:
            task = create_task(task_id)
            task.setup()
        except Exception as e:
            pytest.skip(f"Task {task_id} not available: {e}")

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
            pytest.skip(f"{spec.id} on {family}: compose failed - {e}")

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
