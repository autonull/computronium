"""Stability-Plasticity Frontier Benchmark (New Suite).

Question: What is the trade-off between stability and plasticity?

Toy Task: Sequential task learning with varying stability constraints
- Spectral radius (ρ) sweep: 0.5, 0.7, 0.9, 1.0, 1.05, 1.2
- Plasticity types: null, routing, fast_weights, rule_state, substrate_coupled
- Tasks: Sequential task switching (Task A -> Task B -> Task A)
- Measure: stability metrics (ρ, σ_max, Lyapunov), plasticity metrics (adaptation speed, retention)

This suite maps the stability-plasticity frontier by systematically
varying the contraction factor and measuring both stability and
plasticity metrics.
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

# Stability parameter sweep
RHO_VALUES = [0.5, 0.7, 0.9, 1.0, 1.05, 1.2]
PLASTICITY_TYPES = [
    "null",
    "routing",
    "fast_weights",
    "rule_state",
    "substrate_coupled",
]


class StabilityPlasticityModel(nn.Module):
    """Model for stability-plasticity benchmark with controllable spectral radius."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        rho: float,
        plasticity_type: str = "null",
        plasticity_config: dict | None = None,
    ):
        super().__init__()
        self.rho = rho
        self.plasticity_type = plasticity_type
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim

        # Build recurrent network with controlled spectral radius
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        self.recurrent = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.output_proj = nn.Linear(hidden_dim, output_dim)

        # Initialize recurrent weights with controlled spectral radius
        self._init_recurrent_weights(rho)

        # Plasticity components
        self.plasticity_config = plasticity_config or {}
        self._init_plasticity()

        self.h = None  # Hidden state

    def _init_recurrent_weights(self, rho: float):
        """Initialize recurrent weights with target spectral radius."""
        with torch.no_grad():
            # Random orthogonal initialization
            nn.init.orthogonal_(self.recurrent.weight)
            # Scale to target spectral radius
            self.recurrent.weight.mul_(rho)

    def _init_plasticity(self):
        """Initialize plasticity components."""
        if self.plasticity_type == "routing":
            self.gate = nn.Linear(self.hidden_dim, self.hidden_dim)
        elif self.plasticity_type == "fast_weights":
            self.fast_weights = nn.Parameter(
                torch.zeros(self.hidden_dim, self.hidden_dim)
            )
        elif self.plasticity_type == "rule_state":
            self.rule_logits = nn.Parameter(torch.zeros(4))  # 4 rules
        # substrate_coupled uses the recurrent weights directly

    def forward(self, x: Tensor) -> Tensor:
        """Forward pass with recurrence."""
        batch_size = x.shape[0]

        # Initialize hidden state
        if self.h is None or self.h.shape[0] != batch_size:
            self.h = torch.zeros(batch_size, self.hidden_dim, device=x.device)

        # Input projection
        x = self.input_proj(x)

        # Recurrent step
        self.h = torch.tanh(self.recurrent(self.h) + x)

        # Apply plasticity modulation
        if self.plasticity_type == "routing":
            gate = torch.sigmoid(self.gate(self.h))
            self.h = self.h * gate
        elif self.plasticity_type == "fast_weights":
            self.h = self.h + self.h @ self.fast_weights.t()
        elif self.plasticity_type == "rule_state":
            # Apply rule-based modulation (simplified)
            rules = torch.softmax(self.rule_logits, dim=0)
            # Rule 0: amplify, Rule 1: suppress, Rule 2: decorrelate, Rule 3: identity
            self.h = self.h * (1 + rules[0] - rules[1])

        return self.output_proj(self.h)

    def reset_state(self):
        """Reset hidden state."""
        self.h = None

    def compute_spectral_radius(self) -> float:
        """Compute actual spectral radius of recurrent weights."""
        with torch.no_grad():
            eigvals = torch.linalg.eigvals(self.recurrent.weight)
            return float(eigvals.abs().max().item())

    def compute_max_singular_value(self) -> float:
        """Compute max singular value."""
        with torch.no_grad():
            sv = torch.linalg.svdvals(self.recurrent.weight)
            return float(sv.max().item())


def create_task_a(
    batch_size: int,
    input_dim: int,
    num_classes: int,
    device: torch.device | str = "cpu",
) -> tuple[Tensor, Tensor]:
    """Task A: Classify by mean > 0."""
    device = get_device(device)
    x = torch.randn(batch_size, input_dim, device=device)
    y = (x.mean(dim=1) > 0).long() % num_classes
    return x, y


def create_task_b(
    batch_size: int,
    input_dim: int,
    num_classes: int,
    device: torch.device | str = "cpu",
) -> tuple[Tensor, Tensor]:
    """Task B: Classify by variance > threshold."""
    device = get_device(device)
    x = torch.randn(batch_size, input_dim, device=device)
    y = (x.var(dim=1) > 1.0).long() % num_classes
    return x, y


def evaluate_stability_plasticity(  # ruff: ignore[complex-structure, too-many-locals, too-many-statements]
    rho: float,
    plasticity_type: str,
    epochs_per_task: int = 15,
    batch_size: int = 64,
    input_dim: int = 64,
    hidden_dim: int = 128,
    output_dim: int = 10,
    device: torch.device | str = "cpu",
    seed: int = 42,
) -> dict:
    """Evaluate stability-plasticity trade-off."""
    torch.manual_seed(seed)
    random.seed(seed)
    device = get_device(device)
    start_time = time.perf_counter()

    model = StabilityPlasticityModel(
        input_dim, hidden_dim, output_dim, rho, plasticity_type
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    # Track metrics
    results = {
        "rho_target": rho,
        "rho_actual": model.compute_spectral_radius(),
        "sigma_max": model.compute_max_singular_value(),
        "plasticity_type": plasticity_type,
        "task_a_losses": [],
        "task_b_losses": [],
        "task_a_accuracies": [],
        "task_b_accuracies": [],
        "task_a_after_b_accuracies": [],  # Retention
    }

    # Task A training
    model.train()
    model.reset_state()
    for epoch in range(epochs_per_task):
        x, y = create_task_a(batch_size, input_dim, output_dim, device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        results["task_a_losses"].append(loss.item())

        # Evaluate
        with torch.no_grad():
            eval_x, eval_y = create_task_a(200, input_dim, output_dim, device)
            model.reset_state()
            pred = model(eval_x).argmax(dim=-1)
            acc = (pred == eval_y).float().mean().item()
            results["task_a_accuracies"].append(acc)

    task_a_final_acc = (
        results["task_a_accuracies"][-1] if results["task_a_accuracies"] else 0
    )

    # Task B training (plasticity test)
    model.train()
    model.reset_state()
    for epoch in range(epochs_per_task):
        x, y = create_task_b(batch_size, input_dim, output_dim, device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        results["task_b_losses"].append(loss.item())

        # Evaluate on Task B
        with torch.no_grad():
            eval_x, eval_y = create_task_b(200, input_dim, output_dim, device)
            model.reset_state()
            pred = model(eval_x).argmax(dim=-1)
            acc = (pred == eval_y).float().mean().item()
            results["task_b_accuracies"].append(acc)

    task_b_final_acc = (
        results["task_b_accuracies"][-1] if results["task_b_accuracies"] else 0
    )

    # Test retention: Task A after Task B (stability test)
    model.eval()
    model.reset_state()
    with torch.no_grad():
        eval_x, eval_y = create_task_a(200, input_dim, output_dim, device)
        pred = model(eval_x).argmax(dim=-1)
        retention_acc = (pred == eval_y).float().mean().item()
        results["task_a_after_b_accuracies"].append(retention_acc)

    # Compute stability-plasticity metrics
    adaptation_speed = (
        epochs_per_task
        - results["task_b_accuracies"].index(max(results["task_b_accuracies"]))
        if results["task_b_accuracies"]
        else epochs_per_task
    )
    retention = retention_acc / task_a_final_acc if task_a_final_acc > 0 else 0
    plasticity = task_b_final_acc
    stability = retention

    # Lyapunov exponent approximation (largest eigenvalue of Jacobian)
    # For RNN: λ ≈ log(ρ)
    lyapunov = max(0, torch.log(torch.tensor(results["rho_actual"])).item())

    elapsed = time.perf_counter() - start_time
    resources = measure_suite_resources(
        model=model,
        coordinate=f"stability_plasticity/rho_{rho}/{plasticity_type}",
        device=str(device),
        batch_size=batch_size,
        elapsed_s=elapsed,
    )

    return {
        "claims_scope": CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED,
        "coordinate": f"rho_{rho}/{plasticity_type}",
        "rho_target": rho,
        "rho_actual": results["rho_actual"],
        "sigma_max": results["sigma_max"],
        "lyapunov_exponent": lyapunov,
        "plasticity_type": plasticity_type,
        "task_a_accuracy": task_a_final_acc,
        "task_b_accuracy": task_b_final_acc,
        "retention_accuracy": retention_acc,
        "adaptation_speed": adaptation_speed,
        "retention": retention,
        "plasticity": plasticity,
        "stability": stability,
        "stability_plasticity_ratio": stability / plasticity if plasticity > 0 else 0,
        "task_a_losses": results["task_a_losses"],
        "task_b_losses": results["task_b_losses"],
        "task_a_accuracies": results["task_a_accuracies"],
        "task_b_accuracies": results["task_b_accuracies"],
        "resources": resources.to_dict(),
    }


def run_stability_plasticity_frontier_suite(
    rho_values: list[float] | None = None,
    plasticity_types: list[str] | None = None,
    output_dir: Path = Path("benchmark_results/stability_plasticity_frontier"),
    epochs_per_task: int = 15,
    batch_size: int = 64,
    seeds: int = 3,
    device: str = "auto",
) -> list[dict]:
    """Run stability-plasticity frontier benchmark suite."""
    rho_values = rho_values or RHO_VALUES
    plasticity_types = plasticity_types or PLASTICITY_TYPES
    resolved_device = get_device(device)

    all_results = []

    print("\nStability-Plasticity Frontier Benchmark")
    print(f"  Rho values: {rho_values}")
    print(f"  Plasticity types: {plasticity_types}")
    print(f"  Epochs per task: {epochs_per_task}, Batch size: {batch_size}")
    print(f"  Seeds: {seeds}, Device: {device}")

    for rho in rho_values:
        for plasticity in plasticity_types:
            coord = f"rho_{rho}/{plasticity}"
            print(f"\nEvaluating: {coord}")
            coord_results = {
                "coordinate": coord,
                "rho": rho,
                "plasticity_type": plasticity,
                "seeds": [],
            }

            for seed in range(seeds):
                print(f"  Seed {seed}...")
                result = evaluate_stability_plasticity(
                    rho=rho,
                    plasticity_type=plasticity,
                    epochs_per_task=epochs_per_task,
                    batch_size=batch_size,
                    device=resolved_device,
                    seed=seed,
                )
                coord_results["seeds"].append(result)
                print(
                    f"    Task A: {result['task_a_accuracy']:.4f}, "
                    f"Task B: {result['task_b_accuracy']:.4f}, "
                    f"Retention: {result['retention_accuracy']:.4f}, "
                    f"ρ_actual: {result['rho_actual']:.4f}"
                )

            # Aggregate
            if coord_results["seeds"]:
                task_a_accs = [s["task_a_accuracy"] for s in coord_results["seeds"]]
                task_b_accs = [s["task_b_accuracy"] for s in coord_results["seeds"]]
                retentions = [s["retention_accuracy"] for s in coord_results["seeds"]]
                stabilities = [s["stability"] for s in coord_results["seeds"]]
                plasticities = [s["plasticity"] for s in coord_results["seeds"]]

                coord_results["mean_task_a_accuracy"] = sum(task_a_accs) / len(
                    task_a_accs
                )
                coord_results["mean_task_b_accuracy"] = sum(task_b_accs) / len(
                    task_b_accs
                )
                coord_results["mean_retention"] = sum(retentions) / len(retentions)
                coord_results["mean_stability"] = sum(stabilities) / len(stabilities)
                coord_results["mean_plasticity"] = sum(plasticities) / len(plasticities)
                coord_results["mean_rho_actual"] = sum(
                    s["rho_actual"] for s in coord_results["seeds"]
                ) / len(coord_results["seeds"])

            all_results.append(coord_results)

    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    results_file = output_dir / "stability_plasticity_frontier_results.json"
    with results_file.open("w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to {results_file}")

    # Print summary
    print("\n" + "=" * 120)
    print("Stability-Plasticity Frontier Benchmark Summary")
    print("=" * 120)
    print(
        f"{'Rho':<6} {'Plasticity':<18} {'Task A Acc':<12} {'Task B Acc':<12} {'Retention':<10} "
        f"{'Stability':<10} {'Plasticity':<12} {'ρ_actual':<10} {'Claim Scope'}"
    )
    print("-" * 120)
    for r in all_results:
        print(
            f"{r['rho']:<6.2f} {r['plasticity_type']:<18} "
            f"{r.get('mean_task_a_accuracy', 0):<12.4f} "
            f"{r.get('mean_task_b_accuracy', 0):<12.4f} "
            f"{r.get('mean_retention', 0):<10.4f} "
            f"{r.get('mean_stability', 0):<10.4f} "
            f"{r.get('mean_plasticity', 0):<12.4f} "
            f"{r.get('mean_rho_actual', 0):<10.4f} "
            f"{r['seeds'][0].get('claims_scope', 'N/A')}"
        )

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Stability-Plasticity Frontier Benchmark"
    )
    parser.add_argument(
        "--rho-values", nargs="+", type=float, help="Rho values to test"
    )
    parser.add_argument(
        "--plasticity-types", nargs="+", help="Plasticity types to test"
    )
    parser.add_argument(
        "--output-dir",
        default="benchmark_results/stability_plasticity_frontier",
        help="Output directory",
    )
    parser.add_argument("--epochs", type=int, default=15, help="Epochs per task")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--seeds", type=int, default=3, help="Number of seeds")
    parser.add_argument("--device", default="auto", help="Device (auto, cpu, cuda)")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode (fewer rho/plasticity/epochs/seeds)",
    )
    args = parser.parse_args()

    if args.quick:
        args.rho_values = [0.7, 0.9, 1.05]
        args.plasticity_types = ["null", "routing", "fast_weights"]
        args.epochs = 5
        args.seeds = 1

    run_stability_plasticity_frontier_suite(
        rho_values=args.rho_values,
        plasticity_types=args.plasticity_types,
        output_dir=Path(args.output_dir),
        epochs_per_task=args.epochs,
        batch_size=args.batch_size,
        seeds=args.seeds,
        device=args.device,
    )


if __name__ == "__main__":
    main()
