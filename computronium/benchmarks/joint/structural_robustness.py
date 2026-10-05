"""Structural Robustness Benchmark (Level 3).

Question: Can system recover after damage?

Toy Task: Damage recovery
- Zeroed weights, removed nodes, dead channels, noisy memristive states

Compare: Null vs Routing vs SubstrateCoupled
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import torch
from torch import Tensor

from computronium.benchmarks.joint import (
    CLAIMS_SCOPE_PSI_ENGAGED,
    CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED,
)
from computronium.benchmarks.joint._plasticity_wiring import (
    modulate_hidden,
    step_psi,
)
from computronium.core.logging import get_logger
from computronium.core.profiling import measure_suite_resources
from computronium.core.utils.device import get_device

logger = get_logger(__name__)


def create_damage_scenarios(
    model: torch.nn.Module, damage_type: str, severity: float = 0.5
) -> dict:
    """Apply damage to model and return original state for recovery.

    Args:
        model: Model to damage
        damage_type: Type of damage ("zero_weights", "remove_nodes", "noise")
        severity: Fraction of weights/nodes to damage (0-1)

    Returns:
        Dict with original state for recovery
    """
    original_state = {}

    for name, param in model.named_parameters():
        original_state[name] = param.data.clone()

        if damage_type == "zero_weights":
            # Zero out random weights
            mask = torch.rand_like(param) < severity
            param.data[mask] = 0

        elif damage_type == "remove_nodes":
            # Zero out entire output neurons (for Linear layers)
            if param.dim() == 2:  # weight matrix [out_features, in_features]
                num_neurons = param.shape[0]
                num_damage = int(num_neurons * severity)
                damage_indices = torch.randperm(num_neurons)[:num_damage]
                param.data[damage_indices] = 0

        elif damage_type == "noise":
            # Add noise to weights
            noise = torch.randn_like(param) * severity * param.data.std()
            param.data += noise

        elif damage_type == "dead_channels":
            # For conv-like: zero out entire channels
            if param.dim() >= 2:
                num_channels = param.shape[0]
                num_damage = int(num_channels * severity)
                damage_indices = torch.randperm(num_channels)[:num_damage]
                param.data[damage_indices] = 0

    return original_state


def evaluate_recovery(  # ruff: ignore[complex-structure, too-many-statements]
    model: torch.nn.Module,
    original_state: dict,
    damage_type: str,
    recovery_steps: int,
    train_loader,
    criterion,
    optimizer,
    device: torch.device,
    frozen_theta: bool = False,
) -> dict:
    """Evaluate recovery after damage.

    With ``frozen_theta=True`` the recovery loop is ψ-only: all θ
    parameters are frozen and wrapped in a ``ThetaInvarianceAudit``; no
    optimizer step runs. This is the frozen-θ control that upgrades the
    suite's claims scope.
    """
    from computronium.core.plasticity.theta_audit import ThetaInvarianceAudit

    # Measure initial performance after damage
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in train_loader:
            x, y = x.to(device), y.to(device)  # ruff: ignore[redefined-loop-name]
            logits = model(x)
            pred = logits.argmax(dim=-1)
            correct += (pred == y).sum().item()
            total += y.shape[0]
    initial_accuracy = correct / total

    psi_before = {k: v.detach().clone() for k, v in model.psi.items()}  # type: ignore[attr-defined]

    if frozen_theta:
        for p in model.parameters():
            p.requires_grad_(False)

    def psi_moved_during() -> bool:
        return any(
            not torch.equal(
                psi_before[k],
                model.psi[k].detach().to(psi_before[k].device),  # type: ignore[index]
            )
            for k in psi_before
            if k in model.psi  # type: ignore[attr-defined]
        )

    # Recovery training
    model.train()
    recovery_losses = []
    recovery_accuracies = []
    theta_audit_report: dict = {}
    psi_moved = False

    def run_recovery() -> None:
        for step in range(recovery_steps):
            epoch_loss = 0
            epoch_correct = 0
            epoch_total = 0

            for x, y in train_loader:
                x, y = x.to(device), y.to(device)  # ruff: ignore[redefined-loop-name]
                psi = step_psi(
                    model.plasticity,
                    model.psi,  # type: ignore[arg-type]
                    x,
                    training=True,
                    live_param=next(model.parameters()),
                )
                model.psi = psi  # type: ignore[assignment]
                logits = model(x)
                loss = criterion(logits, y)
                if not frozen_theta:
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                epoch_loss += loss.item()
                epoch_correct += (logits.argmax(dim=-1) == y).sum().item()
                epoch_total += y.shape[0]

            recovery_losses.append(epoch_loss / len(train_loader))
            recovery_accuracies.append(
                epoch_correct / epoch_total if epoch_total > 0 else 0
            )

    if frozen_theta:
        with ThetaInvarianceAudit(model) as audit:
            run_recovery()
        # Restore trainability — the caller may run standard recovery next.
        for p in model.parameters():
            p.requires_grad_(True)
        theta_audit_report = {
            "invariant": audit.report.invariant if audit.report else False,
            "max_abs_change": audit.report.max_abs_change
            if audit.report
            else float("nan"),
        }
        psi_moved = psi_moved_during()
    else:
        run_recovery()

    # Final accuracy
    final_accuracy = recovery_accuracies[-1] if recovery_accuracies else 0

    # Recovery metric: how much accuracy recovered relative to original
    # We need original accuracy - approximate from pre-damage
    recovery_ratio = final_accuracy / initial_accuracy if initial_accuracy > 0 else 0

    out = {
        "initial_accuracy": initial_accuracy,
        "final_accuracy": final_accuracy,
        "recovery_ratio": recovery_ratio,
        "recovery_losses": recovery_losses,
        "recovery_accuracies": recovery_accuracies,
    }
    if frozen_theta:
        out["theta_audit"] = theta_audit_report
        out["psi_moved"] = psi_moved
    return out


def evaluate_structural_robustness(  # ruff: ignore[complex-structure, too-many-arguments, too-many-locals, too-many-statements, too-many-positional-arguments]
    coordinate: str,
    epochs: int = 10,
    batch_size: int = 64,
    input_dim: int = 64,
    hidden_dim: int = 128,
    output_dim: int = 10,
    recovery_steps: int = 20,
    damage_severity: float = 0.3,
    device: str | torch.device = "cpu",
    seed: int = 42,
) -> dict:
    """Evaluate structural robustness for a coordinate."""
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    torch.manual_seed(seed)
    random.seed(seed)
    device = get_device(device)
    start_time = time.perf_counter()

    parts = coordinate.split("/")
    if len(parts) != 6:
        raise ValueError(f"Invalid coordinate: {coordinate}")

    plasticity_type = parts[3]

    # Build plasticity primitive
    from computronium.core.joint.transition import NullPlasticity, PlasticityConfig
    from computronium.core.plasticity import (
        create_fast_weight_plasticity,
        create_routing_plasticity,
        create_rule_state_plasticity,
        create_substrate_coupled_plasticity,
    )

    plasticity_config = PlasticityConfig(
        plasticity_type=plasticity_type,
        plastic_state_dims={"gate_logits": 64, "active_routes": 64}
        if plasticity_type == "routing"
        else {"fast_weights": hidden_dim}
        if plasticity_type == "fast_weights"
        else {"operator_logits": 8}
        if plasticity_type == "rule_state"
        else None,
    )

    if plasticity_type == "null":
        plasticity = NullPlasticity()
    elif plasticity_type == "routing":
        plasticity = create_routing_plasticity(plasticity_config)
    elif plasticity_type == "fast_weights":
        plasticity = create_fast_weight_plasticity(plasticity_config)
    elif plasticity_type == "substrate_coupled":
        plasticity = create_substrate_coupled_plasticity(plasticity_config)
    elif plasticity_type == "rule_state":
        plasticity = create_rule_state_plasticity(plasticity_config)
    else:
        raise ValueError(f"Unknown plasticity: {plasticity_type}")

    # SystemContext is not needed for initial_psi in benchmark harness; None is accepted
    psi = {k: v.to(device) for k, v in plasticity.initial_psi(None, batch_size).items()}  # type: ignore[arg-type]

    # Simple MLP model. Hidden activations are modulated by the
    # coordinate's plasticity state ψ (stepped per batch in the loops
    # below) so recovery measurably conditions on the P-axis.
    class SimpleMLP(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim),
            )
            self.psi: dict[str, Tensor] = {}
            self.plasticity = plasticity

        def forward(self, x):
            h = torch.relu(self.net[0](x))
            h = modulate_hidden(self.plasticity, h, self.psi)
            h = torch.relu(self.net[2](h))
            h = modulate_hidden(self.plasticity, h, self.psi)
            return self.net[4](h)

    model = SimpleMLP().to(device)

    # Pre-train on synthetic task
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Generate synthetic training data
    train_x = torch.randn(1000, input_dim, device=device)
    train_y = (train_x.sum(dim=-1) > 0).long() % output_dim
    train_dataset = TensorDataset(train_x, train_y)
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, drop_last=True
    )

    # Pre-train: the damage/recovery premise requires a trained model —
    # pre_damage_accuracy on an untrained net made recovery_ratio meaningless.
    model.train()
    for _ in range(epochs):
        for x, y in train_loader:
            psi = step_psi(
                plasticity,
                psi,
                x.to(device),
                training=True,
                live_param=next(model.parameters()),
            )
            model.psi = psi
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)
            loss.backward()
            optimizer.step()

    # Save original model state after pre-training
    original_model_state = {k: v.clone() for k, v in model.state_dict().items()}

    # Measure pre-damage accuracy
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in train_loader:
            psi = step_psi(plasticity, psi, x.to(device))
            model.psi = psi
            logits = model(x)
            pred = logits.argmax(dim=-1)
            correct += (pred == y).sum().item()
            total += y.shape[0]
    pre_damage_accuracy = correct / total

    # Apply multiple damage types and measure recovery
    damage_types = ["zero_weights", "remove_nodes", "noise"]
    damage_results = {}
    psi_only_recovery = {}

    for damage_type in damage_types:
        # Restore original model
        model.load_state_dict(original_model_state)

        # Apply damage
        original_state = create_damage_scenarios(model, damage_type, damage_severity)

        # PR-1 optimizer-phase hygiene: fresh optimizer per scenario — recovery
        # of one damage type must not inherit momentum from another.
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

        # Frozen-θ ψ-only recovery FIRST (it does not mutate θ, so the
        # standard recovery below starts from the same pristine damaged
        # state it always did).
        psi_only_recovery[damage_type] = evaluate_recovery(
            model,
            original_state,
            damage_type,
            recovery_steps,
            train_loader,
            criterion,
            optimizer,
            device,
            frozen_theta=True,
        )

        # Evaluate recovery
        recovery = evaluate_recovery(
            model,
            original_state,
            damage_type,
            recovery_steps,
            train_loader,
            criterion,
            optimizer,
            device,
        )

        damage_results[damage_type] = recovery

    # Average recovery across damage types
    avg_recovery_ratio = sum(
        r["recovery_ratio"] for r in damage_results.values()
    ) / len(damage_results)
    avg_final_accuracy = sum(
        r["final_accuracy"] for r in damage_results.values()
    ) / len(damage_results)

    avg_psi_only_recovery_ratio = sum(
        r["recovery_ratio"] for r in psi_only_recovery.values()
    ) / len(psi_only_recovery)

    all_audits_invariant = all(
        r["theta_audit"]["invariant"] for r in psi_only_recovery.values()
    )
    psi_moved_all = all(r["psi_moved"] for r in psi_only_recovery.values())
    claims_scope = (
        CLAIMS_SCOPE_PSI_ENGAGED
        if all_audits_invariant and psi_moved_all
        else CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED
    )

    return {
        "claims_scope": claims_scope,
        "coordinate": coordinate,
        "pre_damage_accuracy": pre_damage_accuracy,
        "damage_severity": damage_severity,
        "damage_results": damage_results,
        "psi_only_recovery": psi_only_recovery,
        "avg_recovery_ratio": avg_recovery_ratio,
        "avg_final_accuracy": avg_final_accuracy,
        "avg_psi_only_recovery_ratio": avg_psi_only_recovery_ratio,
        "resources": measure_suite_resources(
            model=model,
            coordinate=coordinate,
            device=str(device),
            batch_size=batch_size,
            elapsed_s=time.perf_counter() - start_time,
        ).to_dict(),
    }


_RESULTS_FILENAME = "structural_robustness_results.json"


def _load_completed(results_file: Path) -> dict[str, dict]:
    """Coordinates this suite already measured, keyed by coordinate.

    An unreadable or partial file yields ``{}``: a resumed suite re-measures
    rather than reporting a truncated matrix as complete.
    """
    if not results_file.exists():
        return {}
    try:
        measured = json.loads(results_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("unreadable results at %s (%s); re-measuring", results_file, exc)
        return {}
    if not isinstance(measured, list):
        return {}
    return {
        entry["coordinate"]: entry
        for entry in measured
        if isinstance(entry, dict) and entry.get("seeds")
    }


def _persist(results_file: Path, results: list[dict]) -> None:
    """Write the suite's results atomically, one coordinate at a time."""
    results_file.parent.mkdir(parents=True, exist_ok=True)
    scratch = results_file.with_suffix(".json.partial")
    scratch.write_text(json.dumps(results, indent=2), encoding="utf-8")
    scratch.replace(results_file)


def run_structural_robustness_suite(
    coordinates: list[str],
    output_dir: Path,
    epochs: int = 10,
    batch_size: int = 64,
    recovery_steps: int = 20,
    damage_severity: float = 0.3,
    seeds: int = 3,
    device: str | torch.device = "auto",
) -> list[dict]:
    """Run structural robustness benchmark suite.

    Every coordinate is persisted as soon as it finishes, and a coordinate
    already in the results file is skipped. The suite is 24 coordinates x 10
    seeds of real training — long enough that a session boundary ends it — and
    a suite that writes once at the end throws away everything it measured. The
    resume seam is the file the measurements already landed in.
    """
    device = get_device(device)
    results_file = output_dir / _RESULTS_FILENAME
    done = _load_completed(results_file)
    if done:
        print(f"Resuming: {len(done)} coordinate(s) already measured")
    all_results = list(done.values())

    for coord in coordinates:
        if coord in done:
            print(f"\nSkipping (already measured): {coord}")
            continue
        print(f"\nEvaluating: {coord}")
        coord_results = {"coordinate": coord, "seeds": []}

        for seed in range(seeds):
            print(f"  Seed {seed}...")
            result = evaluate_structural_robustness(
                coordinate=coord,
                epochs=epochs,
                batch_size=batch_size,
                recovery_steps=recovery_steps,
                damage_severity=damage_severity,
                device=device,
                seed=seed,
            )
            coord_results["seeds"].append(result)
            print(
                f"    Pre-damage: {result['pre_damage_accuracy']:.4f}, Recovery: {result['avg_recovery_ratio']:.4f}"
            )

        # Aggregate
        if coord_results["seeds"]:
            recovery_ratios = [s["avg_recovery_ratio"] for s in coord_results["seeds"]]
            final_accs = [s["avg_final_accuracy"] for s in coord_results["seeds"]]
            coord_results["mean_recovery_ratio"] = sum(recovery_ratios) / len(
                recovery_ratios
            )
            coord_results["std_recovery_ratio"] = (
                (
                    sum(
                        (r - coord_results["mean_recovery_ratio"]) ** 2
                        for r in recovery_ratios
                    )
                    / len(recovery_ratios)
                )
                ** 0.5
                if len(recovery_ratios) > 1
                else 0
            )
            coord_results["mean_final_accuracy"] = sum(final_accs) / len(final_accs)

        all_results.append(coord_results)
        _persist(results_file, all_results)

    _persist(results_file, all_results)
    print(f"\nResults saved to {results_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("Structural Robustness Benchmark Summary")
    print("=" * 80)
    print(
        f"{'Coordinate':<50} {'Pre-Dmg Acc':<12} {'Recovery Ratio':<14} {'Final Acc':<10} {'Plasticity'}"
    )
    print("-" * 80)
    for r in all_results:
        coord_short = (
            r["coordinate"][:48] + ".."
            if len(r["coordinate"]) > 50
            else r["coordinate"]
        )
        prim = r["coordinate"].split("/")[3]
        print(
            f"{coord_short:<50} {r['seeds'][0]['pre_damage_accuracy']:<12.4f} {r.get('mean_recovery_ratio', 0):<14.4f} {r.get('mean_final_accuracy', 0):<10.4f} {prim}"
        )

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="Structural Robustness Benchmark (Level 3)"
    )
    parser.add_argument("--coordinates", nargs="+", help="Coordinates to test")
    parser.add_argument(
        "--output-dir",
        default="benchmark_results/structural_robustness",
        help="Output directory",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Pre-training epochs")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument(
        "--recovery-steps", type=int, default=20, help="Recovery training steps"
    )
    parser.add_argument(
        "--damage-severity", type=float, default=0.3, help="Damage severity (0-1)"
    )
    parser.add_argument("--seeds", type=int, default=3, help="Number of seeds")
    parser.add_argument("--device", default="auto", help="Device (auto, cpu, cuda)")
    parser.add_argument(
        "--quick", action="store_true", help="Quick mode (3 epochs, 1 seed)"
    )
    args = parser.parse_args()

    if args.quick:
        args.epochs = 3
        args.recovery_steps = 5
        args.seeds = 1

    coordinates = args.coordinates or [
        "digital/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
        "digital/recurrent/energy_minimization/routing/thermodynamic_contrast/euclidean",
        "memristive/recurrent/energy_minimization/substrate_coupled/thermodynamic_contrast/euclidean",
        "neuromorphic/recurrent/spike_integration/null/thermodynamic_contrast/euclidean",
    ]

    run_structural_robustness_suite(
        coordinates=coordinates,
        output_dir=Path(args.output_dir),
        epochs=args.epochs,
        batch_size=args.batch_size,
        recovery_steps=args.recovery_steps,
        damage_severity=args.damage_severity,
        seeds=args.seeds,
        device=args.device,
    )


if __name__ == "__main__":
    main()
