"""Probe: does learning move at all? Cheap check for val_acc and settle_converged.

TODO51 B4: val_acc spans 0.008-0.203 over 240 records at 3 epochs — near-chance
on a 10-class task — and settle_converged is 0 on every cell. Both may be
genuine at L1 fidelity, but AGENTS.md says a low-performing experiment is
suspect for a defect. A cheap probe on whether learning moves at all is a
fix candidate, not an experiment.

Run: uv run python -m scripts.probes.t51_learning_signal_probe
"""

from __future__ import annotations

import torch

from computronium.core.system_trainer import SystemTrainer, SystemTrainerConfig
from computronium.domains.factory import create_task
from computronium.experiment.execution.compose import compose_cell_system
from computronium.experiment.execution.evaluate import compute_stability_metrics
from computronium.experiment.schema.coordinate import Coordinate


def _system(dynamics: str, credit: str, geometry: str = "feedforward"):
    # Use minimal params to avoid harvest schema issues; defaults will be used
    params: dict[str, object] = {"hidden_dim": 64, "num_layers": 3, "settle_step": 0.1}
    return compose_cell_system(
        coordinate=Coordinate(
            substrate="digital",
            geometry=geometry,
            dynamics=dynamics,
            plasticity="null",
            credit=credit,
            update="euclidean",
            params=params,
        ),
        geometry={},
        input_shape=(64,),
        output_dim=10,
        param_budget=2_000_000,
    ).system


def _flatten(loader):
    for x, y in loader:
        yield x.view(x.size(0), -1), y


def main() -> None:
    torch.manual_seed(0)

    # Test a few representative configurations
    configs = [
        ("energy_minimization", "thermodynamic_contrast", "feedforward"),
        ("instantaneous", "gradient", "feedforward"),
        ("predictive_settling", "thermodynamic_contrast", "feedforward"),
        ("error_predictive_coding", "thermodynamic_contrast", "feedforward"),
        ("pc_alm", "thermodynamic_contrast", "feedforward"),
        ("lazy", "gradient", "feedforward"),
    ]

    task = create_task("digits", device="cpu", quick_mode=True)
    task.setup()
    train_loader = task.get_dataloader("train")
    val_loader = task.get_dataloader("val")

    print(
        f"{'dynamics':<28}{'credit':<28}{'epoch':>6}{'train_acc':>10}{'val_acc':>10}{'settle_steps':>13}{'converged':>10}"
    )
    print("-" * 115)

    for dynamics, credit, geometry in configs:
        system = _system(dynamics, credit, geometry)
        config = SystemTrainerConfig(
            max_epochs=10,  # More epochs to see if learning moves
            device="cpu",
            seed=42,
            limit_train_batches=2,
            limit_val_batches=2,
            track_flops=False,
            track_memory=False,
        )

        with SystemTrainer(
            system, config, _flatten(train_loader), val_data=_flatten(val_loader)
        ) as trainer:
            history = trainer.fit()

        # Check settle telemetry from the evaluator (runs its own settle)
        sample_x = torch.randn(4, 64)
        stability = compute_stability_metrics(system, sample_x)

        final = history[-1]
        train_acc = final.get("train_acc", 0.0)
        val_acc = final.get("val_acc", 0.0)
        settle_steps = stability.get("settle_steps", 0)
        converged = stability.get("settle_converged", 0)
        horizon = stability.get("settle_horizon", 0)

        print(
            f"{dynamics:<28}{credit:<28}{len(history):>6}{train_acc:>10.4f}{val_acc:>10.4f}{settle_steps:>13.0f}{converged:>10.0f}"
        )

        # Also check if accuracy improves over epochs
        if len(history) > 1:
            first_acc = history[0].get("train_acc", 0.0)
            last_acc = history[-1].get("train_acc", 0.0)
            improvement = last_acc - first_acc
            print(
                f"  -> train_acc improvement over {len(history)} epochs: {improvement:+.4f}"
            )

    print("\n--- Checking if settle converges with more steps ---")
    # Test with higher max_steps and lower convergence threshold
    system = _system("energy_minimization", "thermodynamic_contrast", "feedforward")
    # Create new config with more settle steps (config is frozen)
    from computronium.ontology.dynamics import StateDynamicsConfig

    new_config = StateDynamicsConfig.energy_minimization(
        max_steps=100,
        convergence_threshold=1e-5,
        convergence_start=5,
        step_size=system.dynamics.config.step_size,
        beta=system.dynamics.config.beta,
    )
    system.dynamics.config = new_config

    config = SystemTrainerConfig(
        max_epochs=3,
        device="cpu",
        seed=42,
        limit_train_batches=2,
        limit_val_batches=2,
    )

    with SystemTrainer(
        system, config, _flatten(train_loader), val_data=_flatten(val_loader)
    ) as trainer:
        history = trainer.fit()

    # Check settle telemetry from evaluator
    sample_x = torch.randn(4, 64)
    stability = compute_stability_metrics(system, sample_x)

    final = history[-1]
    print("With max_steps=100, threshold=1e-5:")
    print(f"  train_acc: {final.get('train_acc', 0.0):.4f}")
    print(f"  val_acc: {final.get('val_acc', 0.0):.4f}")
    print(f"  settle_steps: {stability.get('settle_steps', 0):.0f}")
    print(f"  settle_converged: {stability.get('settle_converged', 0):.0f}")
    print(f"  settle_horizon: {stability.get('settle_horizon', 0):.0f}")

    # Also check the settle telemetry during training (from evaluator after each epoch)
    print("\n--- Per-epoch settle telemetry (from evaluator) ---")
    for i, h in enumerate(history):
        print(
            f"  Epoch {i + 1}: train_acc={h.get('train_acc', 0.0):.4f}, "
            f"val_acc={h.get('val_acc', 0.0):.4f}, "
            f"settle_steps={stability.get('settle_steps', 0):.0f}, "
            f"converged={stability.get('settle_converged', 0):.0f}"
        )


if __name__ == "__main__":
    main()
