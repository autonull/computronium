"""Unified configuration for experiment entry points (W1).

Single configuration surface for both:
- question_first (single RunSpec via Synthesis policy)
- LoopDriver (continuous cycles with explore/exploit)

This ensures the two entry points share the same configuration structure
and do not drift.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from computronium.experiment.schema.registries import StageId
from computronium.experiment.schema.run_spec import AxisSelection, Fidelity, RunSpec

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from computronium.experiment.registry.loop import LoopConfig, LoopDriver


# Canonical StageIds for a question-first run (S1 Frame first)
# Matches QUESTION_FIRST_STAGES from profiles.py
QUESTION_FIRST_STAGES: tuple[str, ...] = (
    "s1_frame",
    "s2_space",
    "s3_schedule",
    "s4_gate",
    "s5_compose",
    "s6_train",
    "s7_measure",
    "s8_record",
    "s9_attribute",
    "s10_decide",
    "s11_report",
)


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    """Unified experiment configuration.

    This is the single source of truth for both question_first and LoopDriver.
    """

    # Core identification
    run_id: str | None = None  # Auto-generated if None
    profile: str = "question_first"  # "question_first" | "loop"

    # Task configuration
    task: str = "xor"
    task_schedule: tuple[str, ...] = field(default_factory=tuple)

    # Objectives
    objectives: tuple[str, ...] = ("validation_accuracy",)

    # Structural axes (what the search space covers)
    axes: tuple[AxisSelection, ...] = field(default_factory=tuple)

    # Hyperparameters to sweep
    hyperparameters: Mapping[str, Any] = field(default_factory=dict)

    # Operating point (budget, fidelity, seeds, etc.)
    fidelity: Fidelity = "L1"
    n_seeds: int = 3
    epochs: int = 1
    seed: int = 0
    budget_seconds: float | None = None
    param_budget: int = 1_000_000

    # Device
    device: str = "auto"

    # Policy
    policy: str = "synthesis"

    # Stages to run
    stages: tuple[str, ...] = field(default_factory=tuple)

    # Checkpointing
    checkpoint_every_n: int = 0

    # Loop-specific (used only when profile="loop")
    hours: float = 8.0
    cycles: int = 0
    explore_fidelity: Fidelity = "L0"
    exploit_fidelity: Fidelity = "L1"
    explore_hours: float = 0.5
    exploit_hours: float = 0.5
    explore_sweep_steps: int = 30
    exploit_sweep_steps: int = 15
    epochs_explore: int = 1
    epochs_exploit: int = 3
    cell_workers: int = 4
    master_seed: int | None = None
    hypothesis_ids: tuple[str, ...] = field(default_factory=tuple)
    hypothesis_registry_path: Path | None = None
    use_icu_guided: bool = False

    # Store/state paths
    store_path: Path | None = None
    state_dir: Path | None = None

    # Code provenance
    code_sha: str = "unknown"

    def to_runspec(self, task: str | None = None, kind: str | None = None) -> RunSpec:
        """Convert to a RunSpec for the given task and kind.

        Args:
            task: Override the task (for LoopDriver cycles)
            kind: "explore" or "exploit" (for LoopDriver fidelity/epochs)

        Returns:
            RunSpec ready for PipelineConfig
        """
        target_task = task or self.task
        is_explore = kind == "explore"
        is_exploit = kind == "exploit"

        # Determine fidelity, epochs, sweep_steps based on kind
        if is_explore:
            fidelity = self.explore_fidelity
            epochs = self.epochs_explore
            sweep_steps = self.explore_sweep_steps
            budget_seconds = self.explore_hours * 3600
        elif is_exploit:
            fidelity = self.exploit_fidelity
            epochs = self.epochs_exploit
            sweep_steps = self.exploit_sweep_steps
            budget_seconds = self.exploit_hours * 3600
        else:
            fidelity = self.fidelity
            epochs = self.epochs
            sweep_steps = 30
            budget_seconds = self.budget_seconds

        # Determine policy
        policy = self.policy
        if self.profile == "loop" and kind in {"explore", "exploit"}:
            policy = "round_robin_grid"

        # Determine stages
        stages = self.stages
        if not stages:
            if self.profile == "question_first":
                stages = QUESTION_FIRST_STAGES
            else:
                stages = tuple(s.value for s in StageId)

        return RunSpec(
            profile=f"{self.profile}-{kind}" if kind else self.profile,
            task=target_task,
            objectives=self.objectives,
            stages=stages,
            fidelity=fidelity,
            n_seeds=self.n_seeds,
            epochs=epochs,
            batch_limit=0,
            budget_seconds=budget_seconds,
            param_budget=self.param_budget,
            policy=policy,
            axes=self.axes,
            hyperparameters=dict(self.hyperparameters),
            checkpoint_every_n=self.checkpoint_every_n,
            seed=self.seed,
            device=self.device,
            sweep_steps=sweep_steps,
            code_sha=self.code_sha,
            dataset=target_task,
            dataset_version="1.0",
        )

    def to_loop_config(self) -> LoopConfig:
        """Convert to LoopConfig for LoopDriver.

        Requires store_path and state_dir to be set.
        """
        from computronium.experiment.registry.loop import LoopConfig

        if self.store_path is None or self.state_dir is None:
            raise ValueError("store_path and state_dir required for LoopConfig")

        return LoopConfig(
            store_path=self.store_path,
            state_dir=self.state_dir,
            stages=self.stages or tuple(s.value for s in StageId),
            param_budget=self.param_budget,
            policy=self.policy,
            hyperparameters=dict(self.hyperparameters),
            checkpoint_every_n=self.checkpoint_every_n,
            device=self.device,
            master_seed=self.master_seed,
            hours=self.hours,
            cycles=self.cycles,
            n_seeds=self.n_seeds,
            explore_fidelity=self.explore_fidelity,
            exploit_fidelity=self.exploit_fidelity,
            explore_hours=self.explore_hours,
            exploit_hours=self.exploit_hours,
            explore_sweep_steps=self.explore_sweep_steps,
            exploit_sweep_steps=self.exploit_sweep_steps,
            epochs_explore=self.epochs_explore,
            epochs_exploit=self.epochs_exploit,
            cell_workers=self.cell_workers,
            task_schedule=self.task_schedule or (self.task,),
            hypothesis_ids=self.hypothesis_ids,
            hypothesis_registry_path=self.hypothesis_registry_path,
            use_icu_guided=self.use_icu_guided,
        )

    @classmethod
    def from_question_first(
        cls,
        objective: str,
        task: str,
        operating_point: dict[str, Any] | None = None,
    ) -> ExperimentConfig:
        """Create config from question-first parameters.

        Raises:
            ValueError: The operating point names a field the config does not
                carry; a silently ignored constraint is dead configuration.
        """
        # Create config from question-first parameters
        point = dict(operating_point or {})
        known = {"budget_seconds", "epochs", "fidelity", "n_seeds", "seed"}
        unknown = sorted(set(point) - known)
        if unknown:
            msg = f"unknown field(s) in operating point: {unknown}"
            raise ValueError(msg)
        return cls(
            profile="question_first",
            task=task,
            objectives=(objective,),
            fidelity=point.get("fidelity", "L1"),
            n_seeds=point.get("n_seeds", 3),
            epochs=point.get("epochs", 1),
            seed=point.get("seed", 0),
            budget_seconds=point.get("budget_seconds"),
            policy="synthesis",
            stages=QUESTION_FIRST_STAGES,
        )

    @classmethod
    def from_loop_profile(cls, _profile_name: str) -> ExperimentConfig:
        """Create config from a loop profile name (e.g., from RUN_PROFILES)."""
        # This would load from the CLI's RUN_PROFILES
        # For now, return defaults
        return cls(profile="loop")


def question_first_from_config(config: ExperimentConfig) -> RunSpec:
    """Build a RunSpec from ExperimentConfig for question-first entry.

    This is the unified entry point that replaces the old question_first function.
    """
    return config.to_runspec()


def loop_driver_from_config(config: ExperimentConfig) -> LoopDriver:
    """Create a LoopDriver from ExperimentConfig.

    This is the unified entry point for the continuous loop.
    """
    from computronium.experiment.registry.loop import LoopDriver

    loop_config = config.to_loop_config()
    return LoopDriver(loop_config)


__all__ = [
    "ExperimentConfig",
    "loop_driver_from_config",
    "question_first_from_config",
]
