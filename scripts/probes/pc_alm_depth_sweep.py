#!/usr/bin/env python
"""PC-ALM Depth Scaling Probe (scripts/probes/pc_alm_depth_sweep.py).

Measures PC-ALM trainability across depths with InnocentiInit.
Informs: demo D23 (pc_alm_mnist), paper claim (depth 1000 trainable).

Usage:
    python scripts/probes/pc_alm_depth_sweep.py --depths 10 20 50 100 200 500 1000 --epochs 3
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import torch

from computronium.core.system_trainer import compose_system
from computronium.ontology import (
    CreditAssignmentConfig,
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    ParameterUpdateConfig,
    PCALMCredit,
    PCALMDynamics,
    StateDynamicsConfig,
    SubstrateConfig,
)


def create_pc_alm_system(
    depth: int,
    hidden_dim: int = 128,
    max_steps: int = 150,
    step_size: float = 0.1,
    rho: float = 1.0,
    prospective_leak: float = 0.0,
    beta: float = 0.5,
    compiled: bool = False,
    seed: int = 42,
):
    """Create a PC-ALM system for depth scaling experiments."""
    torch.manual_seed(seed)
    substrate = DigitalSubstrate(SubstrateConfig.digital(device="cpu"))
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=784,
            output_dim=10,
            hidden_dims=tuple([hidden_dim] * depth),
            init_scheme="innocenti",
            residual=True,
        )
    )
    dynamics = PCALMDynamics(
        StateDynamicsConfig.pc_alm(
            max_steps=max_steps,
            step_size=step_size,
            beta=beta,
            rho=rho,
            prospective_leak=prospective_leak,
            compiled=compiled,
            convergence_threshold=1e-3,
            convergence_start=5,
        )
    )
    credit = PCALMCredit(CreditAssignmentConfig.pc_alm(beta=beta))
    update = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.02))

    return compose_system(substrate, geometry, dynamics, credit, update)


def run_depth_sweep(
    depths: list[int],
    hidden_dim: int = 128,
    epochs: int = 3,
    batch_size: int = 32,
    max_steps: int = 150,
    step_size: float = 0.1,
    rho: float = 1.0,
    prospective_leak: float = 0.0,
    compiled: bool = False,
) -> list[dict]:
    """Run PC-ALM training at multiple depths and return results."""

    results = []

    for depth in depths:
        print(f"\n{'=' * 60}")
        print(f"Testing depth={depth}, hidden_dim={hidden_dim}")
        print(f"{'=' * 60}")

        system = create_pc_alm_system(
            depth=depth,
            hidden_dim=hidden_dim,
            max_steps=max_steps,
            step_size=step_size,
            rho=rho,
            prospective_leak=prospective_leak,
            compiled=compiled,
        )

        # Synthetic MNIST-like data
        torch.manual_seed(42)
        n_batches = 20
        x = torch.randn(n_batches, batch_size, 784)
        y = torch.randint(0, 10, (n_batches, batch_size))

        depth_results = {
            "depth": depth,
            "hidden_dim": hidden_dim,
            "max_steps": max_steps,
            "step_size": step_size,
            "rho": rho,
            "prospective_leak": prospective_leak,
            "epochs": epochs,
            "batch_size": batch_size,
            "epochs_data": [],
        }

        start_time = time.time()

        for epoch in range(epochs):
            epoch_losses = []
            epoch_accs = []

            for batch_idx in range(n_batches):
                result = system.train_step(x[batch_idx], y[batch_idx])
                epoch_losses.append(result["loss"])
                epoch_accs.append(result.get("nudged_fit_accuracy", 0.0))

            avg_loss = sum(epoch_losses) / len(epoch_losses)
            avg_acc = sum(epoch_accs) / len(epoch_accs)

            steps_used = system.dynamics._settle_steps_used

            epoch_data = {
                "epoch": epoch,
                "avg_loss": avg_loss,
                "avg_acc": avg_acc,
                "settle_steps_used": steps_used,
            }
            depth_results["epochs_data"].append(epoch_data)

            print(
                f"  Epoch {epoch + 1}/{epochs}: loss={avg_loss:.4f}, acc={avg_acc:.2%}, settle_steps={steps_used}"
            )

        elapsed = time.time() - start_time
        depth_results["walltime_seconds"] = elapsed
        depth_results["final_loss"] = depth_results["epochs_data"][-1]["avg_loss"]
        depth_results["final_acc"] = depth_results["epochs_data"][-1]["avg_acc"]
        depth_results["diverged"] = not torch.isfinite(
            torch.tensor(depth_results["final_loss"])
        )

        print(
            f"  Final: loss={depth_results['final_loss']:.4f}, acc={depth_results['final_acc']:.2%}, time={elapsed:.1f}s"
        )
        if depth_results["diverged"]:
            print(f"  *** DIVERGED ***")

        results.append(depth_results)

        # Early stop if diverged
        if depth_results["diverged"]:
            print(f"\nStopping sweep at depth {depth} due to divergence")
            break

    return results


def main():
    parser = argparse.ArgumentParser(description="PC-ALM Depth Scaling Probe")
    parser.add_argument(
        "--depths",
        nargs="+",
        type=int,
        default=[10, 20, 50, 100, 200, 500, 1000],
        help="Depths to test",
    )
    parser.add_argument("--hidden-dim", type=int, default=128, help="Hidden dimension")
    parser.add_argument("--epochs", type=int, default=3, help="Epochs per depth")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--max-steps", type=int, default=150, help="Max settle steps")
    parser.add_argument(
        "--step-size", type=float, default=0.1, help="Primal/dual step size"
    )
    parser.add_argument(
        "--rho", type=float, default=1.0, help="Augmented Lagrangian penalty"
    )
    parser.add_argument(
        "--prospective-leak", type=float, default=0.0, help="Prospective leak (alpha)"
    )
    parser.add_argument("--compiled", action="store_true", help="Use torch.compile")
    parser.add_argument(
        "--output", type=str, default="pc_alm_depth_sweep.json", help="Output JSON file"
    )

    args = parser.parse_args()

    print(f"PC-ALM Depth Scaling Probe")
    print(f"Depths: {args.depths}")
    print(f"Hidden dim: {args.hidden_dim}")
    print(f"Epochs: {args.epochs}")
    print(f"Max steps: {args.max_steps}")
    print(f"Step size: {args.step_size}")
    print(f"Rho: {args.rho}")
    print(f"Prospective leak: {args.prospective_leak}")
    print(f"Compiled: {args.compiled}")

    results = run_depth_sweep(
        depths=args.depths,
        hidden_dim=args.hidden_dim,
        epochs=args.epochs,
        batch_size=args.batch_size,
        max_steps=args.max_steps,
        step_size=args.step_size,
        rho=args.rho,
        prospective_leak=args.prospective_leak,
        compiled=args.compiled,
    )

    # Save results
    output_path = Path(args.output)
    output_path.write_text(json.dumps(results, indent=2))
    print(f"\nResults saved to {output_path}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(
        f"{'Depth':>6} | {'Final Loss':>10} | {'Final Acc':>8} | {'Steps':>5} | {'Time (s)':>8} | {'Diverged':>8}"
    )
    print("-" * 60)
    for r in results:
        print(
            f"{r['depth']:>6} | {r['final_loss']:>10.4f} | {r['final_acc']:>7.2%} | "
            f"{r['epochs_data'][-1]['settle_steps_used']:>5} | {r['walltime_seconds']:>8.1f} | {str(r['diverged']):>8}"
        )

    # Find max trainable depth
    trainable = [r for r in results if not r["diverged"]]
    if trainable:
        max_depth = max(r["depth"] for r in trainable)
        print(f"\nMax trainable depth (no divergence): {max_depth}")
    else:
        print("\nNo trainable depths found!")


if __name__ == "__main__":
    main()
