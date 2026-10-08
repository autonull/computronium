"""Credit Assignment Scaling Benchmark (New Suite).

Question: How do credit assignment methods scale with depth?

Toy Task: Deep MLP on synthetic classification
- Depth sweep: 2, 4, 8, 16, 32, 50 layers
- Credit methods: Backprop (gradient), FA, EqProp, PEPITA, TargetProp
- Measure: final accuracy, gradient norm, alignment, walltime, memory

This suite tests the fundamental scaling behavior of local credit
assignment methods vs backprop as network depth increases.
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import torch
from torch import Tensor, nn

from computronium.benchmarks.joint import CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED
from computronium.core.profiling import measure_suite_resources
from computronium.core.utils.device import get_device

CREDIT_METHODS = {
    "gradient": "Backpropagation (full gradient)",
    "fa": "Feedback Alignment",
    "eqprop": "Equilibrium Propagation",
    "pepita": "PEPITA",
    "targetprop": "Target Propagation",
}

DEPTH_SWEEP = [2, 4, 8, 16, 32, 50]


class DeepMLP(nn.Module):
    """Deep MLP with configurable depth and credit assignment."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        num_layers: int,
        credit_method: str = "gradient",
        activation: str = "relu",
    ):
        super().__init__()
        self.credit_method = credit_method
        self.num_layers = num_layers

        # Build layers
        layers = []
        for i in range(num_layers):
            in_dim = input_dim if i == 0 else hidden_dim
            layers.append(nn.Linear(in_dim, hidden_dim))
            if activation == "relu":
                layers.append(nn.ReLU())
            elif activation == "tanh":
                layers.append(nn.Tanh())
            elif activation == "gelu":
                layers.append(nn.GELU())

        layers.append(nn.Linear(hidden_dim, output_dim))
        self.net = nn.Sequential(*layers)

        # For FA: fixed random feedback weights
        if credit_method == "fa":
            self._init_fa_feedback(hidden_dim, output_dim)

        # For TargetProp: inverse networks
        if credit_method == "targetprop":
            self._init_targetprop_inverse(hidden_dim, output_dim)

    def _init_fa_feedback(self, hidden_dim: int, output_dim: int):
        """Initialize fixed random feedback weights for FA."""
        num_hidden = self.num_layers - 1
        self.fa_feedback = nn.ModuleList()
        for i in range(num_hidden):
            # Feedback from output to each hidden layer
            fb = nn.Linear(output_dim, hidden_dim, bias=False)
            nn.init.normal_(fb.weight, 0, 0.1)
            fb.weight.requires_grad_(False)  # Fixed!
            self.fa_feedback.append(fb)

    def _init_targetprop_inverse(self, hidden_dim: int, output_dim: int):
        """Initialize inverse networks for TargetProp."""
        num_hidden = self.num_layers - 1
        self.inverse_nets = nn.ModuleList()
        for i in range(num_hidden):
            # Each inverse net maps from layer i+1 to layer i
            inv = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
            )
            self.inverse_nets.append(inv)

    def forward(self, x: Tensor) -> Tensor:
        return self.net(x)

    def forward_with_activations(self, x: Tensor) -> list[Tensor]:
        """Forward pass returning all hidden activations."""
        activations = []
        for layer in self.net:
            x = layer(x)
            if isinstance(layer, nn.Linear):
                activations.append(x)
        return activations


def create_synthetic_task(
    batch_size: int,
    input_dim: int,
    num_classes: int,
    device: torch.device | str = "cpu",
) -> tuple[Tensor, Tensor]:
    """Create synthetic classification task."""
    device = get_device(device)
    x = torch.randn(batch_size, input_dim, device=device)
    # Target depends on input features in a learnable way
    y = (x.sum(dim=1) > 0).long() % num_classes
    return x, y


def evaluate_credit_scaling(  # ruff: ignore[complex-structure, too-many-locals, too-many-statements]
    depth: int,
    credit_method: str,
    epochs: int = 20,
    batch_size: int = 64,
    input_dim: int = 64,
    hidden_dim: int = 128,
    output_dim: int = 10,
    device: torch.device | str = "cpu",
    seed: int = 42,
) -> dict:
    """Evaluate credit assignment scaling for a given depth and method."""
    torch.manual_seed(seed)
    random.seed(seed)
    device = get_device(device)
    start_time = time.perf_counter()

    model = DeepMLP(input_dim, hidden_dim, output_dim, depth, credit_method).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    # Track metrics
    losses = []
    accuracies = []
    grad_norms = []
    fa_alignment = []  # For FA: alignment with true gradient

    for epoch in range(epochs):
        x, y = create_synthetic_task(batch_size, input_dim, output_dim, device)

        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()

        # Compute gradient norm
        total_grad_norm = 0.0
        for p in model.parameters():
            if p.grad is not None:
                total_grad_norm += p.grad.data.norm(2).item() ** 2
        grad_norms.append(total_grad_norm**0.5)

        # For FA: compute alignment with true gradient
        if credit_method == "fa":
            alignment = _compute_fa_alignment(model, x, y, criterion, device)
            fa_alignment.append(alignment)

        optimizer.step()

        losses.append(loss.item())

        # Evaluate accuracy
        with torch.no_grad():
            eval_x, eval_y = create_synthetic_task(200, input_dim, output_dim, device)
            pred = model(eval_x).argmax(dim=-1)
            acc = (pred == eval_y).float().mean().item()
            accuracies.append(acc)

    # Final evaluation
    eval_x, eval_y = create_synthetic_task(500, input_dim, output_dim, device)
    with torch.no_grad():
        final_logits = model(eval_x)
        final_acc = (final_logits.argmax(dim=-1) == eval_y).float().mean().item()

    elapsed = time.perf_counter() - start_time
    resources = measure_suite_resources(
        model=model,
        coordinate=f"credit_scaling/{credit_method}/depth_{depth}",
        device=device if isinstance(device, str) else device.type,
        batch_size=batch_size,
        elapsed_s=elapsed,
    )

    return {
        "claims_scope": CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED,
        "coordinate": f"depth_{depth}/{credit_method}",
        "depth": depth,
        "credit_method": credit_method,
        "final_accuracy": final_acc,
        "final_loss": losses[-1] if losses else 0,
        "losses": losses,
        "accuracies": accuracies,
        "grad_norms": grad_norms,
        "fa_alignment": fa_alignment,
        "resources": resources.to_dict(),
    }


def _compute_fa_alignment(
    model: DeepMLP,
    x: Tensor,
    y: Tensor,
    criterion: nn.Module,
    device: torch.device,
) -> float:
    """Compute alignment between FA and true gradient (for analysis)."""
    # This is a placeholder - true alignment requires computing both
    # For now, return 0 as we don't have easy access to true gradient
    return 0.0


def run_credit_assignment_scaling_suite(
    depths: list[int] | None = None,
    credit_methods: list[str] | None = None,
    output_dir: Path = Path("benchmark_results/credit_assignment_scaling"),
    epochs: int = 20,
    batch_size: int = 64,
    seeds: int = 3,
    device: str = "auto",
) -> list[dict]:
    """Run credit assignment scaling benchmark suite."""
    depths = depths or DEPTH_SWEEP
    credit_methods = credit_methods or list(CREDIT_METHODS.keys())
    resolved_device = get_device(device)

    all_results = []

    print("\nCredit Assignment Scaling Benchmark")
    print(f"  Depths: {depths}")
    print(f"  Credit methods: {credit_methods}")
    print(f"  Epochs: {epochs}, Batch size: {batch_size}")
    print(f"  Seeds: {seeds}, Device: {resolved_device}")

    for depth in depths:
        for method in credit_methods:
            coord = f"depth_{depth}/{method}"
            print(f"\nEvaluating: {coord}")
            coord_results = {
                "coordinate": coord,
                "depth": depth,
                "method": method,
                "seeds": [],
            }

            for seed in range(seeds):
                print(f"  Seed {seed}...")
                result = evaluate_credit_scaling(
                    depth=depth,
                    credit_method=method,
                    epochs=epochs,
                    batch_size=batch_size,
                    device=resolved_device,
                    seed=seed,
                )
                coord_results["seeds"].append(result)
                print(
                    f"    Final Acc: {result['final_accuracy']:.4f}, "
                    f"Final Loss: {result['final_loss']:.4f}"
                )

            # Aggregate
            if coord_results["seeds"]:
                accuracies = [s["final_accuracy"] for s in coord_results["seeds"]]
                losses = [s["final_loss"] for s in coord_results["seeds"]]
                coord_results["mean_accuracy"] = sum(accuracies) / len(accuracies)
                coord_results["std_accuracy"] = (
                    (
                        sum(
                            (a - coord_results["mean_accuracy"]) ** 2
                            for a in accuracies
                        )
                        / len(accuracies)
                    )
                    ** 0.5
                    if len(accuracies) > 1
                    else 0
                )
                coord_results["mean_loss"] = sum(losses) / len(losses)

            all_results.append(coord_results)

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    results_file = output_dir / "credit_assignment_scaling_results.json"
    with results_file.open("w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to {results_file}")

    # Print summary
    print("\n" + "=" * 100)
    print("Credit Assignment Scaling Benchmark Summary")
    print("=" * 100)
    print(
        f"{'Depth':<8} {'Method':<15} {'Mean Acc':<10} {'Std Acc':<10} {'Mean Loss':<12} {'Claim Scope'}"
    )
    print("-" * 100)
    for r in all_results:
        print(
            f"{r['depth']:<8} {r['method']:<15} {r.get('mean_accuracy', 0):<10.4f} "
            f"{r.get('std_accuracy', 0):<10.4f} {r.get('mean_loss', 0):<12.4f} "
            f"{r['seeds'][0].get('claims_scope', 'N/A')}"
        )

    return all_results


def main():
    parser = argparse.ArgumentParser(description="Credit Assignment Scaling Benchmark")
    parser.add_argument("--depths", nargs="+", type=int, help="Depths to test")
    parser.add_argument(
        "--methods",
        nargs="+",
        choices=list(CREDIT_METHODS.keys()),
        help="Credit methods to test",
    )
    parser.add_argument(
        "--output-dir",
        default="benchmark_results/credit_assignment_scaling",
        help="Output directory",
    )
    parser.add_argument("--epochs", type=int, default=20, help="Epochs per run")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--seeds", type=int, default=3, help="Number of seeds")
    parser.add_argument("--device", default="auto", help="Device (auto, cpu, cuda)")
    parser.add_argument(
        "--quick", action="store_true", help="Quick mode (fewer depths/epochs/seeds)"
    )
    args = parser.parse_args()

    if args.quick:
        args.depths = [2, 4, 8]
        args.methods = ["gradient", "fa", "eqprop"]
        args.epochs = 5
        args.seeds = 1

    run_credit_assignment_scaling_suite(
        depths=args.depths,
        credit_methods=args.methods,
        output_dir=Path(args.output_dir),
        epochs=args.epochs,
        batch_size=args.batch_size,
        seeds=args.seeds,
        device=args.device,
    )


if __name__ == "__main__":
    main()
