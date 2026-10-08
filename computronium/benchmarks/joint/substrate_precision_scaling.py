"""Substrate Precision Scaling Benchmark (New Suite).

Question: How do substrates perform across precision levels?

Toy Task: Classification on synthetic data
- Digital substrates: FP32, FP16, BF16, INT8, Ternary
- Analog substrates: Memristive, Neuromorphic, Photonic, Complex, Quantum
- Measure: accuracy, energy_per_step, latency, precision_degradation

This suite tests the accuracy-efficiency trade-off across precision
levels for each substrate type.
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

# Substrate precision configurations
DIGITAL_PRECISIONS = ["fp32", "fp16", "bf16", "int8", "ternary"]
ANALOG_SUBSTRATES = ["memristive", "neuromorphic", "photonic", "complex", "quantum"]

# Default hidden dim per substrate (some need larger for precision)
SUBSTRATE_CONFIGS = {
    "digital": {"hidden_dim": 128, "supports_mixed_precision": True},
    "memristive": {"hidden_dim": 128, "noise_level": 0.01},
    "neuromorphic": {"hidden_dim": 128, "threshold": 1.0},
    "photonic": {"hidden_dim": 128, "phase_noise": 0.01},
    "complex": {"hidden_dim": 128, "noise_level": 0.01},
    "analog": {"hidden_dim": 128, "noise_level": 0.01},
    "quantum": {
        "hidden_dim": 64,
        "noise_level": 0.05,
    },  # Smaller due to simulation cost
}


class SubstrateModel(nn.Module):
    """Model that simulates different substrate behaviors."""

    def __init__(
        self,
        substrate: str,
        precision: str,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        noise_level: float = 0.01,
    ):
        super().__init__()
        self.substrate = substrate
        self.precision = precision
        self.noise_level = noise_level

        # Determine compute dtype
        if precision == "fp32":
            self.compute_dtype = torch.float32
        elif precision == "fp16":
            self.compute_dtype = torch.float16
        elif precision == "bf16":
            self.compute_dtype = torch.bfloat16
        elif precision == "int8":
            self.compute_dtype = torch.int8
        elif precision == "ternary":
            self.compute_dtype = torch.float32  # Simulated
        else:
            self.compute_dtype = torch.float32

        # Build network
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def _apply_precision(self, x: Tensor) -> Tensor:
        """Apply precision quantization/simulation."""
        if self.precision == "fp16":
            return x.half().float()
        elif self.precision == "bf16":
            return x.bfloat16().float()
        elif self.precision == "int8":
            # Simulate INT8 quantization
            scale = 127.0 / x.abs().max().clamp(min=1e-8)
            quantized = (x * scale).round().clamp(-128, 127)
            return quantized.float() / scale
        elif self.precision == "ternary":
            # Ternary quantization: {-1, 0, 1}
            threshold = x.abs().mean()
            return torch.where(
                x > threshold, 1.0, torch.where(x < -threshold, -1.0, 0.0)
            )
        return x

    def _apply_substrate_noise(self, x: Tensor) -> Tensor:
        """Apply substrate-specific noise."""
        if self.noise_level > 0 and self.training:
            if self.substrate in {"memristive", "analog", "complex"}:
                # Additive Gaussian noise
                noise = torch.randn_like(x) * self.noise_level * x.abs().mean()
                return x + noise
            elif self.substrate == "neuromorphic":
                # Spike-like noise: random dropout
                mask = torch.rand_like(x) > self.noise_level
                return x * mask.float()
            elif self.substrate == "photonic":
                # Phase noise: multiplicative
                phase = torch.randn_like(x) * self.noise_level
                return x * torch.cos(phase)
            elif self.substrate == "quantum":
                # Quantum noise: depolarizing
                noise = torch.randn_like(x) * self.noise_level
                return x + noise
        return x

    def forward(self, x: Tensor) -> Tensor:
        # Use autocast for mixed precision
        if self.precision in {"fp16", "bf16"}:
            dtype = torch.float16 if self.precision == "fp16" else torch.bfloat16
            with torch.autocast(device_type=x.device.type, dtype=dtype):
                return self._forward_impl(x)
        else:
            return self._forward_impl(x)

    def _forward_impl(self, x: Tensor) -> Tensor:
        for i, layer in enumerate(self.net):
            if isinstance(layer, nn.Linear):
                x = layer(x)
                x = self._apply_substrate_noise(x)
                x = self._apply_precision(x)
            else:
                x = layer(x)
        return x


def create_synthetic_task(
    batch_size: int,
    input_dim: int,
    num_classes: int,
    device: torch.device | str = "cpu",
) -> tuple[Tensor, Tensor]:
    """Create synthetic classification task."""
    device = get_device(device)
    x = torch.randn(batch_size, input_dim, device=device)
    y = (x.sum(dim=1) > 0).long() % num_classes
    return x, y


def evaluate_precision_scaling(  # ruff: ignore[complex-structure, too-many-locals, too-many-statements]
    substrate: str,
    precision: str,
    epochs: int = 20,
    batch_size: int = 64,
    input_dim: int = 64,
    output_dim: int = 10,
    device: torch.device | str = "cpu",
    seed: int = 42,
) -> dict:
    """Evaluate substrate precision scaling."""
    torch.manual_seed(seed)
    random.seed(seed)
    device = get_device(device)
    start_time = time.perf_counter()

    config = SUBSTRATE_CONFIGS.get(substrate, {"hidden_dim": 128, "noise_level": 0.01})
    hidden_dim = config.get("hidden_dim", 128)
    noise_level = config.get("noise_level", 0.01)

    model = SubstrateModel(
        substrate, precision, input_dim, hidden_dim, output_dim, noise_level
    ).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    losses = []
    accuracies = []

    for epoch in range(epochs):
        x, y = create_synthetic_task(batch_size, input_dim, output_dim, device)

        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()

        losses.append(loss.item())

        # Evaluate
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
        coordinate=f"substrate_precision/{substrate}/{precision}",
        device=str(device),
        batch_size=batch_size,
        elapsed_s=elapsed,
    )

    # Compute precision degradation (accuracy drop from FP32 baseline)
    # This would need a reference run; for now compute relative to first precision
    precision_degradation = 0.0  # Placeholder

    return {
        "claims_scope": CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED,
        "coordinate": f"{substrate}/{precision}",
        "substrate": substrate,
        "precision": precision,
        "final_accuracy": final_acc,
        "final_loss": losses[-1] if losses else 0,
        "losses": losses,
        "accuracies": accuracies,
        "precision_degradation": precision_degradation,
        "resources": resources.to_dict(),
    }


def run_substrate_precision_scaling_suite(
    substrates: list[str] | None = None,
    precisions: list[str] | None = None,
    output_dir: Path = Path("benchmark_results/substrate_precision_scaling"),
    epochs: int = 20,
    batch_size: int = 64,
    seeds: int = 3,
    device: str = "auto",
) -> list[dict]:
    """Run substrate precision scaling benchmark suite."""
    substrates = substrates or list(SUBSTRATE_CONFIGS.keys())
    # Default precisions: digital gets all, analog gets fp32/fp16
    if precisions is None:
        precisions = DIGITAL_PRECISIONS  # Will filter per substrate

    resolved_device = get_device(device)

    all_results = []

    print("\nSubstrate Precision Scaling Benchmark")
    print(f"  Substrates: {substrates}")
    print(f"  Epochs: {epochs}, Batch size: {batch_size}")
    print(f"  Seeds: {seeds}, Device: {resolved_device}")

    for substrate in substrates:
        # Determine valid precisions for this substrate
        if substrate == "digital":
            valid_precisions = precisions
        else:
            # Analog substrates: primarily fp32/fp16 for simulation
            valid_precisions = [p for p in precisions if p in {"fp32", "fp16", "bf16"}]

        for precision in valid_precisions:
            coord = f"{substrate}/{precision}"
            print(f"\nEvaluating: {coord}")
            coord_results = {
                "coordinate": coord,
                "substrate": substrate,
                "precision": precision,
                "seeds": [],
            }

            for seed in range(seeds):
                print(f"  Seed {seed}...")
                result = evaluate_precision_scaling(
                    substrate=substrate,
                    precision=precision,
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
    results_file = output_dir / "substrate_precision_scaling_results.json"
    with results_file.open("w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nResults saved to {results_file}")

    # Print summary
    print("\n" + "=" * 100)
    print("Substrate Precision Scaling Benchmark Summary")
    print("=" * 100)
    print(
        f"{'Substrate':<15} {'Precision':<10} {'Mean Acc':<10} {'Std Acc':<10} {'Mean Loss':<12} {'Claim Scope'}"
    )
    print("-" * 100)
    for r in all_results:
        print(
            f"{r['substrate']:<15} {r['precision']:<10} {r.get('mean_accuracy', 0):<10.4f} "
            f"{r.get('std_accuracy', 0):<10.4f} {r.get('mean_loss', 0):<12.4f} "
            f"{r['seeds'][0].get('claims_scope', 'N/A')}"
        )

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Substrate Precision Scaling Benchmark"
    )
    parser.add_argument("--substrates", nargs="+", help="Substrates to test")
    parser.add_argument("--precisions", nargs="+", help="Precisions to test")
    parser.add_argument(
        "--output-dir",
        default="benchmark_results/substrate_precision_scaling",
        help="Output directory",
    )
    parser.add_argument("--epochs", type=int, default=20, help="Epochs per run")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--seeds", type=int, default=3, help="Number of seeds")
    parser.add_argument("--device", default="auto", help="Device (auto, cpu, cuda)")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode (fewer substrates/epochs/seeds)",
    )
    args = parser.parse_args()

    if args.quick:
        args.substrates = ["digital", "memristive", "neuromorphic"]
        args.precisions = ["fp32", "fp16"]
        args.epochs = 5
        args.seeds = 1

    run_substrate_precision_scaling_suite(
        substrates=args.substrates,
        precisions=args.precisions,
        output_dir=Path(args.output_dir),
        epochs=args.epochs,
        batch_size=args.batch_size,
        seeds=args.seeds,
        device=args.device,
    )


if __name__ == "__main__":
    main()
