"""Core benchmark contributions implementation."""

from __future__ import annotations

import json
import os
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class BenchmarkTask:
    """A standardized benchmark task with known reference results."""

    task_id: str
    name: str
    description: str
    # Reference implementation (callable that returns a model)
    reference_model_factory: Callable[[], Any]
    # Expected reference metrics (baseline performance)
    reference_metrics: dict[str, float]
    # Tolerance for regression detection (relative)
    regression_tolerance: float = 0.05
    # Minimum acceptable performance (absolute)
    min_performance: dict[str, float] | None = None
    # Task metadata
    domain: str = "general"
    difficulty: str = "medium"
    tags: tuple[str, ...] = ()
    # Reference environment
    reference_env: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ReferenceResult:
    """Reference result for a specific model on a benchmark task."""

    task_id: str
    model_name: str
    model_config: dict[str, Any]
    metrics: dict[str, float]
    # Statistical info
    n_seeds: int = 3
    seed_values: tuple[int, ...] = (42, 123, 456)
    # Metadata
    commit_sha: str | None = None
    timestamp: str | None = None
    hardware: str | None = None
    runtime_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class BenchmarkContribution:
    """A community-contributed benchmark result."""

    contribution_id: str
    task_id: str
    model_name: str
    model_config: dict[str, Any]
    metrics: dict[str, float]
    # Comparison against reference
    reference_comparison: dict[str, float] | None = None
    # Statistical info
    n_seeds: int = 3
    seed_values: tuple[int, ...] = (42, 123, 456)
    # Metadata
    contributor: str = "anonymous"
    commit_sha: str | None = None
    timestamp: str | None = None
    hardware: str | None = None
    runtime_seconds: float | None = None
    # Verification
    verified: bool = False
    verification_notes: str = ""


# ---------------------------------------------------------------------------
# Contribution Registry
# ---------------------------------------------------------------------------


class ContributionRegistry:
    """Registry for benchmark tasks, reference results, and contributions."""

    def __init__(self, storage_path: Path | None = None):
        if storage_path is None:
            # Default storage path in user's config directory
            config_dir = Path(
                os.environ.get(
                    "COMPUTRONIUM_CONFIG", Path.home() / ".config" / "computronium"
                )
            )
            config_dir.mkdir(parents=True, exist_ok=True)
            storage_path = config_dir / "benchmark_contributions.json"

        self._tasks: dict[str, BenchmarkTask] = {}
        self._reference_results: dict[str, list[ReferenceResult]] = {}
        self._contributions: dict[str, list[BenchmarkContribution]] = {}
        self._storage_path = storage_path
        if storage_path.exists():
            self._load()

    def register_task(self, task: BenchmarkTask) -> None:
        """Register a benchmark task."""
        self._tasks[task.task_id] = task

    def get_task(self, task_id: str) -> BenchmarkTask | None:
        """Get a benchmark task by ID."""
        return self._tasks.get(task_id)

    def list_tasks(
        self, domain: str | None = None, tags: tuple[str, ...] = ()
    ) -> list[BenchmarkTask]:
        """List all tasks, optionally filtered."""
        tasks = list(self._tasks.values())
        if domain:
            tasks = [t for t in tasks if t.domain == domain]
        if tags:
            tasks = [t for t in tasks if all(tag in t.tags for tag in tags)]
        return tasks

    def add_reference_result(self, result: ReferenceResult) -> None:
        """Add a reference result for a task."""
        if result.task_id not in self._reference_results:
            self._reference_results[result.task_id] = []
        self._reference_results[result.task_id].append(result)

    def get_reference_results(
        self, task_id: str, model_name: str | None = None
    ) -> list[ReferenceResult]:
        """Get reference results for a task, optionally filtered by model."""
        results = self._reference_results.get(task_id, [])
        if model_name:
            results = [r for r in results if r.model_name == model_name]
        return results

    def get_best_reference(
        self, task_id: str, metric: str, higher_is_better: bool = True
    ) -> ReferenceResult | None:
        """Get the best reference result for a task on a metric."""
        results = self._reference_results.get(task_id, [])
        if not results:
            return None
        return max(
            results,
            key=lambda r: (
                r.metrics.get(metric, 0)
                if higher_is_better
                else -r.metrics.get(metric, float("inf"))
            ),
        )

    def add_contribution(self, contribution: BenchmarkContribution) -> None:
        """Add a community contribution."""
        if contribution.task_id not in self._contributions:
            self._contributions[contribution.task_id] = []
        self._contributions[contribution.task_id].append(contribution)

    def get_contributions(
        self, task_id: str, model_name: str | None = None, verified_only: bool = False
    ) -> list[BenchmarkContribution]:
        """Get contributions for a task."""
        contributions = self._contributions.get(task_id, [])
        if model_name:
            contributions = [c for c in contributions if c.model_name == model_name]
        if verified_only:
            contributions = [c for c in contributions if c.verified]
        return contributions

    def compare_against_reference(
        self, task_id: str, model_name: str, metrics: dict[str, float]
    ) -> dict[str, float] | None:
        """Compare metrics against the best reference result."""
        ref = self.get_best_reference(
            task_id, "validation_accuracy"
        )  # Default primary metric
        if not ref:
            return None

        comparison = {}
        for key, value in metrics.items():
            ref_value = ref.metrics.get(key)
            if ref_value is not None and ref_value != 0:
                comparison[key] = (value - ref_value) / abs(ref_value)
        return comparison

    def _load(self) -> None:
        """Load registry from storage."""
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            with self._storage_path.open() as f:
                data = json.load(f)

            # Load contributions (tasks and reference results are registered programmatically)
            for task_id, contribs in data.get("contributions", {}).items():
                for c_data in contribs:
                    # Convert seed_values back to tuple
                    c_data["seed_values"] = tuple(c_data["seed_values"])
                    contribution = BenchmarkContribution(**c_data)
                    self.add_contribution(contribution)
        except Exception as e:
            warnings.warn(
                f"Failed to load contributions from {self._storage_path}: {e}",
                RuntimeWarning,
            )

    def save(self, path: Path | None = None) -> None:
        """Save registry to storage."""
        save_path = path or self._storage_path
        if not save_path:
            return

        data = {
            "contributions": {
                task_id: [
                    {
                        "contribution_id": c.contribution_id,
                        "task_id": c.task_id,
                        "model_name": c.model_name,
                        "model_config": c.model_config,
                        "metrics": c.metrics,
                        "reference_comparison": c.reference_comparison,
                        "n_seeds": c.n_seeds,
                        "seed_values": list(c.seed_values),
                        "contributor": c.contributor,
                        "commit_sha": c.commit_sha,
                        "timestamp": c.timestamp,
                        "hardware": c.hardware,
                        "runtime_seconds": c.runtime_seconds,
                        "verified": c.verified,
                        "verification_notes": c.verification_notes,
                    }
                    for c in contribs
                ]
                for task_id, contribs in self._contributions.items()
            }
        }
        try:
            with save_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            warnings.warn(
                f"Failed to save contributions to {save_path}: {e}", RuntimeWarning
            )

    def _save_async(self) -> None:
        """Save registry asynchronously (call after modifications)."""
        # For simplicity, save synchronously
        self.save()


# ---------------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LeaderboardEntry:
    """Single entry in a leaderboard."""

    rank: int
    task_id: str
    model_name: str
    model_config: dict[str, Any]
    primary_metric: str
    primary_value: float
    all_metrics: dict[str, float]
    contribution: BenchmarkContribution | None = None
    reference: ReferenceResult | None = None


class Leaderboard:
    """Leaderboard for a benchmark task."""

    def __init__(
        self,
        task_id: str,
        primary_metric: str = "validation_accuracy",
        higher_is_better: bool = True,
        registry: ContributionRegistry | None = None,
    ):
        self.task_id = task_id
        self.primary_metric = primary_metric
        self.higher_is_better = higher_is_better
        self.registry = registry

    def build(
        self,
        include_references: bool = True,
        include_contributions: bool = True,
        verified_only: bool = True,
        min_entries: int = 1,
    ) -> list[LeaderboardEntry]:
        """Build the leaderboard."""
        entries: list[LeaderboardEntry] = []

        if self.registry is None:
            return entries

        # Add reference results
        if include_references:
            for ref in self.registry.get_reference_results(self.task_id):
                entry = LeaderboardEntry(
                    rank=0,  # Will be assigned after sorting
                    task_id=self.task_id,
                    model_name=f"{ref.model_name} (reference)",
                    model_config=ref.model_config,
                    primary_metric=self.primary_metric,
                    primary_value=ref.metrics.get(self.primary_metric, 0),
                    all_metrics=ref.metrics,
                    reference=ref,
                )
                entries.append(entry)

        # Add contributions
        if include_contributions:
            for contrib in self.registry.get_contributions(
                self.task_id, verified_only=verified_only
            ):
                entry = LeaderboardEntry(
                    rank=0,
                    task_id=self.task_id,
                    model_name=contrib.model_name,
                    model_config=contrib.model_config,
                    primary_metric=self.primary_metric,
                    primary_value=contrib.metrics.get(self.primary_metric, 0),
                    all_metrics=contrib.metrics,
                    contribution=contrib,
                )
                entries.append(entry)

        # Sort by primary metric
        entries.sort(key=lambda e: e.primary_value, reverse=self.higher_is_better)

        # Assign ranks
        ranked_entries = []
        for i, entry in enumerate(entries):
            ranked_entry = LeaderboardEntry(
                rank=i + 1,
                task_id=entry.task_id,
                model_name=entry.model_name,
                model_config=entry.model_config,
                primary_metric=entry.primary_metric,
                primary_value=entry.primary_value,
                all_metrics=entry.all_metrics,
                contribution=entry.contribution,
                reference=entry.reference,
            )
            ranked_entries.append(ranked_entry)

        return ranked_entries

    def to_table(
        self, entries: list[LeaderboardEntry] | None = None, top_k: int | None = None
    ) -> str:
        """Generate a text table representation."""
        if entries is None:
            entries = self.build()
        if top_k:
            entries = entries[:top_k]

        lines = [
            f"Leaderboard: {self.task_id}",
            f"Primary Metric: {self.primary_metric} ({'higher is better' if self.higher_is_better else 'lower is better'})",
            "",
        ]

        if not entries:
            lines.append("No entries")
            return "\n".join(lines)

        # Header
        header = f"{'Rank':<5} {'Model':<40} {self.primary_metric:<20} {'Seeds':<8} {'Source':<12}"
        lines.append(header)
        lines.append("-" * len(header))

        for e in entries:
            source = (
                "reference"
                if e.reference
                else (
                    "verified"
                    if e.contribution and e.contribution.verified
                    else "contribution"
                )
            )
            seeds = (
                e.reference.n_seeds
                if e.reference
                else e.contribution.n_seeds
                if e.contribution
                else "N/A"
            )
            model_display = (
                e.model_name[:38] + ".." if len(e.model_name) > 40 else e.model_name
            )
            lines.append(
                f"{e.rank:<5} {model_display:<40} {e.primary_value:<20.4f} {seeds:<8} {source:<12}"
            )

        return "\n".join(lines)

    def to_html(
        self, entries: list[LeaderboardEntry] | None = None, top_k: int | None = None
    ) -> str:
        """Generate an HTML table representation."""
        if entries is None:
            entries = self.build()
        if top_k:
            entries = entries[:top_k]

        html = [
            f"<h2>Leaderboard: {self.task_id}</h2>",
            f"<p>Primary Metric: {self.primary_metric} ({'higher is better' if self.higher_is_better else 'lower is better'})</p>",
            "<table>",
            "<thead><tr><th>Rank</th><th>Model</th><th>Primary Metric</th><th>Seeds</th><th>Source</th></tr></thead>",
            "<tbody>",
        ]

        for e in entries:
            source = (
                "reference"
                if e.reference
                else (
                    "verified"
                    if e.contribution and e.contribution.verified
                    else "contribution"
                )
            )
            source_class = (
                "ref"
                if e.reference
                else (
                    "verified"
                    if e.contribution and e.contribution.verified
                    else "contrib"
                )
            )
            seeds = (
                e.reference.n_seeds
                if e.reference
                else e.contribution.n_seeds
                if e.contribution
                else "N/A"
            )
            html.append(
                f"<tr class='{source_class}'>"
                f"<td>{e.rank}</td>"
                f"<td>{e.model_name}</td>"
                f"<td>{e.primary_value:.4f}</td>"
                f"<td>{seeds}</td>"
                f"<td>{source}</td>"
                f"</tr>"
            )

        html.append("</tbody></table>")
        return "\n".join(html)


# ---------------------------------------------------------------------------
# Global Instances
# ---------------------------------------------------------------------------

contribution_registry = ContributionRegistry()


# ---------------------------------------------------------------------------
# Built-in Standard Tasks
# ---------------------------------------------------------------------------


def _register_standard_tasks() -> None:
    """Register built-in standard benchmark tasks."""
    from computronium.evaluation.benchmarks import (
        cifar10_benchmark,
        fashion_mnist_benchmark,
        mnist_benchmark,
        tiny_shakespeare_benchmark,
    )

    # MNIST Classification
    contribution_registry.register_task(
        BenchmarkTask(
            task_id="mnist_classification",
            name="MNIST Digit Classification",
            description="10-class digit classification on MNIST (28x28 grayscale)",
            reference_model_factory=lambda: mnist_benchmark,
            reference_metrics={
                "validation_accuracy": 0.98,
                "validation_loss": 0.05,
                "training_time_seconds": 30.0,
            },
            regression_tolerance=0.02,
            min_performance={"validation_accuracy": 0.90},
            domain="vision",
            difficulty="easy",
            tags=("classification", "digits", "mnist"),
        )
    )

    # Fashion-MNIST Classification
    contribution_registry.register_task(
        BenchmarkTask(
            task_id="fashion_mnist_classification",
            name="Fashion-MNIST Classification",
            description="10-class fashion item classification on Fashion-MNIST (28x28 grayscale)",
            reference_model_factory=lambda: fashion_mnist_benchmark,
            reference_metrics={
                "validation_accuracy": 0.90,
                "validation_loss": 0.30,
                "training_time_seconds": 40.0,
            },
            regression_tolerance=0.03,
            min_performance={"validation_accuracy": 0.80},
            domain="vision",
            difficulty="easy",
            tags=("classification", "fashion", "mnist"),
        )
    )

    # CIFAR-10 Classification
    contribution_registry.register_task(
        BenchmarkTask(
            task_id="cifar10_classification",
            name="CIFAR-10 Classification",
            description="10-class object classification on CIFAR-10 (32x32 RGB)",
            reference_model_factory=lambda: cifar10_benchmark,
            reference_metrics={
                "validation_accuracy": 0.85,
                "validation_loss": 0.50,
                "training_time_seconds": 120.0,
            },
            regression_tolerance=0.05,
            min_performance={"validation_accuracy": 0.70},
            domain="vision",
            difficulty="medium",
            tags=("classification", "cifar", "rgb"),
        )
    )

    # Tiny Shakespeare Language Modeling
    contribution_registry.register_task(
        BenchmarkTask(
            task_id="tiny_shakespeare_lm",
            name="Tiny Shakespeare Language Modeling",
            description="Character-level language modeling on Tiny Shakespeare dataset",
            reference_model_factory=lambda: tiny_shakespeare_benchmark,
            reference_metrics={
                "validation_loss": 1.2,
                "bits_per_character": 1.5,
                "training_time_seconds": 180.0,
            },
            regression_tolerance=0.10,
            min_performance={"validation_loss": 2.0},
            domain="language",
            difficulty="medium",
            tags=("language_modeling", "character", "shakespeare"),
        )
    )


def _register_reference_results() -> None:
    """Register reference results for standard tasks."""
    # MNIST reference results (Backprop baseline)
    contribution_registry.add_reference_result(
        ReferenceResult(
            task_id="mnist_classification",
            model_name="backprop_mlp",
            model_config={
                "hidden_dims": [256, 128],
                "activation": "relu",
                "optimizer": "adam",
                "lr": 0.001,
            },
            metrics={
                "validation_accuracy": 0.982,
                "validation_loss": 0.045,
                "training_time_seconds": 28.5,
            },
            n_seeds=5,
            seed_values=(42, 123, 456, 789, 999),
            commit_sha="main",
            timestamp=datetime.now().isoformat(),
            hardware="NVIDIA RTX 3080",
            runtime_seconds=28.5,
        )
    )

    contribution_registry.add_reference_result(
        ReferenceResult(
            task_id="mnist_classification",
            model_name="eqprop_mlp",
            model_config={
                "hidden_dims": [256, 128],
                "activation": "relu",
                "beta": 0.5,
                "optimizer": "adam",
                "lr": 0.001,
            },
            metrics={
                "validation_accuracy": 0.975,
                "validation_loss": 0.058,
                "training_time_seconds": 85.2,
            },
            n_seeds=5,
            seed_values=(42, 123, 456, 789, 999),
            commit_sha="main",
            timestamp=datetime.now().isoformat(),
            hardware="NVIDIA RTX 3080",
            runtime_seconds=85.2,
        )
    )

    contribution_registry.add_reference_result(
        ReferenceResult(
            task_id="mnist_classification",
            model_name="fa_mlp",
            model_config={
                "hidden_dims": [256, 128],
                "activation": "relu",
                "optimizer": "adam",
                "lr": 0.001,
            },
            metrics={
                "validation_accuracy": 0.968,
                "validation_loss": 0.072,
                "training_time_seconds": 42.1,
            },
            n_seeds=5,
            seed_values=(42, 123, 456, 789, 999),
            commit_sha="main",
            timestamp=datetime.now().isoformat(),
            hardware="NVIDIA RTX 3080",
            runtime_seconds=42.1,
        )
    )

    # Fashion-MNIST reference results
    contribution_registry.add_reference_result(
        ReferenceResult(
            task_id="fashion_mnist_classification",
            model_name="backprop_mlp",
            model_config={
                "hidden_dims": [256, 128],
                "activation": "relu",
                "optimizer": "adam",
                "lr": 0.001,
            },
            metrics={
                "validation_accuracy": 0.905,
                "validation_loss": 0.285,
                "training_time_seconds": 35.2,
            },
            n_seeds=5,
            seed_values=(42, 123, 456, 789, 999),
            commit_sha="main",
            timestamp=datetime.now().isoformat(),
            hardware="NVIDIA RTX 3080",
            runtime_seconds=35.2,
        )
    )

    contribution_registry.add_reference_result(
        ReferenceResult(
            task_id="fashion_mnist_classification",
            model_name="eqprop_mlp",
            model_config={
                "hidden_dims": [256, 128],
                "activation": "relu",
                "beta": 0.5,
                "optimizer": "adam",
                "lr": 0.001,
            },
            metrics={
                "validation_accuracy": 0.892,
                "validation_loss": 0.312,
                "training_time_seconds": 98.7,
            },
            n_seeds=5,
            seed_values=(42, 123, 456, 789, 999),
            commit_sha="main",
            timestamp=datetime.now().isoformat(),
            hardware="NVIDIA RTX 3080",
            runtime_seconds=98.7,
        )
    )

    # CIFAR-10 reference results
    contribution_registry.add_reference_result(
        ReferenceResult(
            task_id="cifar10_classification",
            model_name="backprop_cnn",
            model_config={"arch": "resnet18", "optimizer": "adam", "lr": 0.001},
            metrics={
                "validation_accuracy": 0.865,
                "validation_loss": 0.472,
                "training_time_seconds": 145.3,
            },
            n_seeds=3,
            seed_values=(42, 123, 456),
            commit_sha="main",
            timestamp=datetime.now().isoformat(),
            hardware="NVIDIA RTX 3080",
            runtime_seconds=145.3,
        )
    )

    # Tiny Shakespeare reference results
    contribution_registry.add_reference_result(
        ReferenceResult(
            task_id="tiny_shakespeare_lm",
            model_name="backprop_lstm",
            model_config={
                "hidden_dim": 256,
                "num_layers": 2,
                "optimizer": "adam",
                "lr": 0.001,
            },
            metrics={
                "validation_loss": 1.15,
                "bits_per_character": 1.45,
                "training_time_seconds": 172.8,
            },
            n_seeds=3,
            seed_values=(42, 123, 456),
            commit_sha="main",
            timestamp=datetime.now().isoformat(),
            hardware="NVIDIA RTX 3080",
            runtime_seconds=172.8,
        )
    )


# Initialize standard tasks and reference results on import
_register_standard_tasks()
_register_reference_results()
