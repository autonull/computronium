from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class BudgetStrategy(Enum):
    """Campaign strategy profiles."""

    BROAD_SHALLOW = "broad_shallow"  # Many components, few epochs/seeds
    NARROW_DEEP = "narrow_deep"  # Few components, many epochs/seeds
    BALANCED = "balanced"  # Balanced coverage


class DeviceClass(Enum):
    """Device class for time estimation."""

    GPU = "gpu"
    CPU = "cpu"


@dataclass(frozen=True, slots=True)
class TimeEstimates:
    """Empirical time estimates per cell (seconds)."""

    # Measured cell seconds per dynamics primitive (from MEASURED_CELL_SECONDS registry)
    # These are for 1 epoch at L0 fidelity on reference hardware
    measured_cell_seconds: dict[str, float] = field(default_factory=dict)
    # Base time per cell per epoch on GPU (RTX 3080 reference) - fallback
    gpu_base: float = 1.5
    # Base time per cell per epoch on CPU - fallback
    cpu_base: float = 8.0
    # Overhead per round (scheduling, measurement, etc.)
    round_overhead: float = 5.0
    # HPO startup trial overhead
    startup_overhead: float = 2.0

    def __post_init__(self):
        # Load measured cell seconds from registry if not provided
        if not self.measured_cell_seconds:
            from computronium.experiment.schema.registries import MEASURED_CELL_SECONDS
            object.__setattr__(self, "measured_cell_seconds", dict(MEASURED_CELL_SECONDS))

    def per_cell_per_epoch(self, device: DeviceClass, dynamics: str | None = None) -> float:
        """Get time per cell per epoch, using measured data if available."""
        if dynamics and dynamics in self.measured_cell_seconds:
            base = self.measured_cell_seconds[dynamics]
            # Scale for device (measured on GPU, CPU is ~5-10x slower)
            return base * (1.0 if device == DeviceClass.GPU else 8.0)
        return self.gpu_base if device == DeviceClass.GPU else self.cpu_base

    def round_time(self, n_cells: int, epochs: int, device: DeviceClass, dynamics: str | None = None) -> float:
        """Estimate time for one round of n_cells with given epochs."""
        cell_time = self.per_cell_per_epoch(device, dynamics) * epochs
        return self.round_overhead + n_cells * cell_time


@dataclass(frozen=True, slots=True)
class ComponentSet:
    """Defines a set of ontology axes to include."""

    substrates: list[str]
    geometries: list[str]
    dynamics: list[str]
    credits: list[str]
    updates: list[str]
    plasticities: list[str]
    tasks: list[str]

    @property
    def n_combinations(self) -> int:
        return (
            len(self.substrates)
            * len(self.geometries)
            * len(self.dynamics)
            * len(self.credits)
            * len(self.updates)
            * len(self.plasticities)
            * len(self.tasks)
        )


def _discover_components() -> dict[str, list[str]]:
    """Discover all available primitives from ontology registries."""
    # Import here to avoid circular imports at module level
    from computronium.experiment.schema.axis import (
        GEOMETRY_REGISTRY,
        UPDATE_REGISTRY,
        StructuralAxis,
    )
    from computronium.ontology.substrate import SubstrateType
    from computronium.ontology.dynamics import DYNAMICS_REGISTRY
    from computronium.domains.registry import SUPPORTED_TASKS

    # Get available substrates from SubstrateType enum
    substrates = [s.value for s in SubstrateType]

    # Get available geometries from public registry
    geometries = list(GEOMETRY_REGISTRY.keys())

    # Get available credits from known credit types
    credits = [
        "gradient",
        "equilibrium_prop",
        "feedback_alignment",
        "hebbian",
        "pepita",
        "local_contrastive",
        "random_projections",
        "temporal_trace",
        "target_inversion",
        "homeostatic",
        "pcalm",
        "lemma",
        "local_goodness",
    ]

    # Get available dynamics from registry
    dynamics = list(DYNAMICS_REGISTRY.keys())

    # Get available updates from public registry
    updates = list(UPDATE_REGISTRY.keys())

    # Get available plasticities from PlasticityConfig factory methods
    plasticities = [
        "null",
        "routing",
        "fast_weights",
        "substrate_coupled",
        "rule_state",
        "temporal_psi",
        "conflict_adaptive",
    ]

    # Get supported tasks
    tasks = sorted(SUPPORTED_TASKS)

    return {
        "substrates": substrates,
        "geometries": geometries,
        "credits": credits,
        "dynamics": dynamics,
        "updates": updates,
        "plasticities": plasticities,
        "tasks": tasks,
    }


# Cache discovered components
_DISCOVERED = None


def _get_components() -> dict[str, list[str]]:
    global _DISCOVERED
    if _DISCOVERED is None:
        _DISCOVERED = _discover_components()
    return _DISCOVERED


# Predefined component sets for different strategies (derived from registries)
def _build_component_sets() -> dict["BudgetStrategy", ComponentSet]:
    """Build component sets from discovered primitives."""
    c = _get_components()

    return {
        # Broad: many components, minimal depth
        BudgetStrategy.BROAD_SHALLOW: ComponentSet(
            substrates=c["substrates"],
            geometries=c["geometries"],
            dynamics=c["dynamics"],
            credits=c["credits"],
            updates=c["updates"],
            plasticities=c["plasticities"],
            tasks=c["tasks"],
        ),
        # Narrow: core models, digital substrate, gradient/equilibrium credit
        BudgetStrategy.NARROW_DEEP: ComponentSet(
            substrates=["digital"],
            geometries=["feedforward"],
            dynamics=["energy_minimization"],
            credits=["gradient", "equilibrium_prop"],
            updates=["euclidean"],
            plasticities=["null"],
            tasks=["mnist"],
        ),
        # Balanced: representative sample
        BudgetStrategy.BALANCED: ComponentSet(
            substrates=c["substrates"],
            geometries=c["geometries"],
            dynamics=c["dynamics"],
            credits=c["credits"],
            updates=c["updates"],
            plasticities=c["plasticities"],
            tasks=c["tasks"],
        ),
    }


# Build component sets at module load
COMPONENT_SETS = _build_component_sets()


@dataclass(frozen=True, slots=True)
class BudgetPlan:
    """Complete campaign plan derived from budget."""

    time_budget_hours: float
    strategy: BudgetStrategy
    device_class: DeviceClass

    # Derived parameters
    n_trials: int
    n_seeds: int
    epochs: int
    n_rounds: int
    cells_per_round: int

    # Component selection (ontology axes)
    substrates: list[str]
    geometries: list[str]
    dynamics: list[str]
    credits: list[str]
    updates: list[str]
    plasticities: list[str]
    tasks: list[str]

    # Estimated total time
    estimated_hours: float

    # Run breakdown
    runs: list[dict[str, Any]] = field(default_factory=list)


class BudgetPlanner:
    """Plans campaign parameters from time budget and strategy."""

    def __init__(
        self,
        estimates: TimeEstimates | None = None,
        min_trials: int = 10,
        min_seeds: int = 1,
        min_epochs: int = 1,
        min_cells_per_round: int = 5,
    ):
        self.estimates = estimates or TimeEstimates()
        self.min_trials = min_trials
        self.min_seeds = min_seeds
        self.min_epochs = min_epochs
        self.min_cells_per_round = min_cells_per_round

    def _estimate_round_time(
        self,
        cells_per_round: int,
        epochs: int,
        device_class: DeviceClass,
        dynamics_list: list[str],
    ) -> float:
        """Estimate round time considering the mix of dynamics primitives."""
        if not dynamics_list:
            return self.estimates.round_time(cells_per_round, epochs, device_class)
        
        # Average time per cell across the dynamics mix
        total_cell_time = sum(
            self.estimates.per_cell_per_epoch(device_class, dyn) for dyn in dynamics_list
        )
        avg_cell_time = total_cell_time / len(dynamics_list)
        
        return self.estimates.round_overhead + cells_per_round * avg_cell_time * epochs

    def plan(
        self,
        time_budget_hours: float,
        strategy: BudgetStrategy = BudgetStrategy.BALANCED,
        device_class: DeviceClass = DeviceClass.GPU,
        max_parallel: int = 1,
    ) -> BudgetPlan:
        """Generate a budget plan from time budget and strategy."""
        budget_seconds = time_budget_hours * 3600
        component_set = COMPONENT_SETS[strategy]

        # Start with strategy-specific defaults
        if strategy == BudgetStrategy.BROAD_SHALLOW:
            target_seeds = 1
            target_epochs = 3
            target_trials = 60
        elif strategy == BudgetStrategy.NARROW_DEEP:
            target_seeds = 5
            target_epochs = 20
            target_trials = 20
        else:  # BALANCED
            target_seeds = 3
            target_epochs = 10
            target_trials = 40

        # Estimate cells per round from component combinations
        cells_per_round = max(self.min_cells_per_round, 10)

        # Time per round - consider dynamics mix
        time_per_round = self._estimate_round_time(
            cells_per_round, target_epochs, device_class, component_set.dynamics
        )

        # If even 1 round exceeds budget, reduce scope to fit
        if time_per_round > budget_seconds * 0.8:  # Leave 20% margin
            # Reduce epochs first, then cells_per_round, then seeds
            # Target: time_per_round <= budget_seconds * 0.8
            max_time_per_round = budget_seconds * 0.8
            
            # Reduce epochs
            if target_epochs > self.min_epochs:
                target_epochs = max(
                    self.min_epochs,
                    int(max_time_per_round / (cells_per_round * self.estimates.per_cell_per_epoch(device_class, component_set.dynamics[0]) + self.estimates.round_overhead / cells_per_round))
                )
                time_per_round = self._estimate_round_time(
                    cells_per_round, target_epochs, device_class, component_set.dynamics
                )
            
            # Reduce cells_per_round
            if time_per_round > max_time_per_round and cells_per_round > self.min_cells_per_round:
                cells_per_round = max(
                    self.min_cells_per_round,
                    int(max_time_per_round / (target_epochs * self.estimates.per_cell_per_epoch(device_class, component_set.dynamics[0]) + self.estimates.round_overhead / target_epochs))
                )
                time_per_round = self._estimate_round_time(
                    cells_per_round, target_epochs, device_class, component_set.dynamics
                )
            
            # Reduce seeds (affects total time but not per-round time)
            if target_seeds > self.min_seeds and time_per_round > max_time_per_round:
                # We can't reduce per-round time further, but we can note that total time will be n_rounds * time_per_round * seeds
                # For now, just reduce seeds to minimum
                target_seeds = self.min_seeds

        # Total rounds possible
        n_rounds = max(1, int(budget_seconds / (time_per_round * max_parallel)))

        # Total trials = n_rounds * cells_per_round (approximately)
        estimated_trials = n_rounds * cells_per_round

        # Adjust to fit budget
        if estimated_trials > target_trials:
            # We have more capacity than needed - increase depth
            scale = estimated_trials / target_trials
            target_epochs = min(50, int(target_epochs * scale**0.5))
            target_seeds = min(10, int(target_seeds * scale**0.25))
            estimated_trials = target_trials
        elif estimated_trials < target_trials * 0.5:
            # Not enough capacity - reduce breadth
            scale = (target_trials / estimated_trials) ** 0.5
            component_set = self._reduce_components(component_set, scale)
            # Re-estimate with reduced component set
            time_per_round = self._estimate_round_time(
                cells_per_round, target_epochs, device_class, component_set.dynamics
            )
            n_rounds = max(1, int(budget_seconds / (time_per_round * max_parallel)))
            estimated_trials = n_rounds * cells_per_round

        # Final estimates
        total_cells = estimated_trials * target_seeds
        estimated_seconds = (
            n_rounds * time_per_round * max_parallel
            + self.estimates.startup_overhead * 5
        )
        estimated_hours = estimated_seconds / 3600

        # Build runs from component set
        runs = self._build_runs(component_set, target_trials, target_seeds, target_epochs, time_budget_hours)

        return BudgetPlan(
            time_budget_hours=time_budget_hours,
            strategy=strategy,
            device_class=device_class,
            n_trials=int(estimated_trials),
            n_seeds=target_seeds,
            epochs=target_epochs,
            n_rounds=n_rounds,
            cells_per_round=cells_per_round,
            substrates=component_set.substrates,
            geometries=component_set.geometries,
            dynamics=component_set.dynamics,
            credits=component_set.credits,
            updates=component_set.updates,
            plasticities=component_set.plasticities,
            tasks=component_set.tasks,
            estimated_hours=estimated_hours,
            runs=runs,
        )

    def _reduce_components(
        self, component_set: ComponentSet, scale: float
    ) -> ComponentSet:
        """Reduce component set by scale factor."""

        def _reduce(lst: list[str], scale: float) -> list[str]:
            n = max(1, int(len(lst) / scale))
            return lst[:n]

        return ComponentSet(
            substrates=_reduce(component_set.substrates, scale),
            geometries=_reduce(component_set.geometries, scale),
            credits=_reduce(component_set.credits, scale),
            dynamics=_reduce(component_set.dynamics, scale),
            updates=_reduce(component_set.updates, scale),
            plasticities=_reduce(component_set.plasticities, scale),
            tasks=_reduce(component_set.tasks, scale),
        )

    def _build_runs(
        self,
        component_set: ComponentSet,
        n_trials: int,
        n_seeds: int,
        epochs: int,
        time_budget_hours: float,
    ) -> list[dict[str, Any]]:
        """Build campaign runs from component set."""
        runs = []

        # Calculate per-run budget (divide global budget by estimated number of runs)
        num_runs = 1 + max(0, len(component_set.tasks) - 1)
        per_run_budget_seconds = (time_budget_hours * 3600) / max(1, num_runs)

        # Phase 1: Main comprehensive run
        runs.append(
            {
                "name": "main",
                "profile": "production-map",
                "overrides": {
                    "substrates": component_set.substrates,
                    "geometries": component_set.geometries,
                    "dynamics": component_set.dynamics,
                    "credits": component_set.credits,
                    "updates": component_set.updates,
                    "plasticities": component_set.plasticities,
                    "tasks": component_set.tasks,
                    "hpo": {"n_trials": n_trials, "n_seeds": n_seeds},
                    "epochs": epochs,
                    "budget_seconds": per_run_budget_seconds,
                },
                "depends_on": [],
            }
        )

        # Add dependent runs for strategy
        if len(component_set.tasks) > 1:
            for i, task in enumerate(component_set.tasks[1:], 1):
                runs.append(
                    {
                        "name": f"task_{task}",
                        "profile": "production-map",
                        "overrides": {
                            "task": task,
                            "hpo": {"n_trials": max(10, n_trials // 2), "n_seeds": n_seeds},
                            "epochs": epochs,
                            "budget_seconds": per_run_budget_seconds,
                        },
                        "depends_on": [0],
                    }
                )

        return runs


def create_campaign_yaml(plan: BudgetPlan, output_path: str | Path) -> str:
    """Generate campaign YAML from budget plan."""
    import yaml

    store_path = f"results/adaptive_{plan.strategy.value}_{plan.time_budget_hours}h.db"

    data = {
        "meta": {
            "name": f"adaptive_{plan.strategy.value}_{plan.time_budget_hours}h",
            "description": f"Auto-generated: {plan.strategy.value}, "
            f"{plan.time_budget_hours}h budget, {plan.device_class.value}",
            "strategy": plan.strategy.value,
            "time_budget_hours": plan.time_budget_hours,
            "estimated_hours": round(plan.estimated_hours, 2),
            "device_class": plan.device_class.value,
        },
        "compute": {
            "device": "auto",
            "max_parallel": 1,
            "max_wall_hours": plan.time_budget_hours * 1.2,  # 20% buffer
        },
        "store": store_path,
        "search_space": {
            "base": {
                "hidden_dim": [64, 128, 256],
                "num_layers": [2, 3, 4],
                "lr": [1e-4, 1e-3, 1e-2, "log"],
                "batch_size": [128, 256],
            }
        },
        "constraints": ["estimate(config) <= 500000"],
        "protocols": {
            "default": "end2end",
            "overrides": {
                "fa_mlp": "layerwise",
                "three_factor_hebbian": "layerwise",
            },
        },
        "arms": {
            "adaptive": {
                "input_dim": 784,
                "num_classes": 10,
                "flatten": True,
                "max_params": 500000,
                "substrates": plan.substrates,
                "geometries": plan.geometries,
                "dynamics": plan.dynamics,
                "credits": plan.credits,
                "updates": plan.updates,
                "plasticities": plan.plasticities,
            }
        },
        "tasks": [
            {"name": t, "epochs": plan.epochs, "input_dim": 784, "num_classes": 10}
            for t in plan.tasks
        ],
        "hpo": {
            "sampler": "nsga2",
            "objectives": ["accuracy", "param_count", "epoch_time_s"],
            "n_trials": plan.n_trials,
            "n_startup_trials": min(10, plan.n_trials // 4),
            "n_seeds": plan.n_seeds,
        },
        "resources": {
            "max_wall_hours": plan.time_budget_hours * 1.2,
            "max_epoch_time_sec": 120,
            "early_stop_patience": 10,
        },
        "output": {
            "db": store_path,
            "artifacts_dir": f"artifacts/adaptive_{plan.strategy.value}_{plan.time_budget_hours}h",
            "log_level": "INFO",
            "emit_every": 5,
        },
        "reproducibility": {
            "seed": 42,
            "capture_env": True,
            "artifact_hash": True,
        },
        "runs": [
            {**run, "store": store_path}
            for run in plan.runs
        ],
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    return str(output_path)


def plan_from_args(
    time_hours: float,
    strategy: str = "balanced",
    device: str = "auto",
) -> BudgetPlan:
    """Convenience function to create a plan from CLI args."""
    strat = BudgetStrategy(strategy.lower())
    dev = DeviceClass.GPU if device in ("auto", "cuda") else DeviceClass.CPU
    if device == "auto":
        import torch

        dev = DeviceClass.GPU if torch.cuda.is_available() else DeviceClass.CPU

    planner = BudgetPlanner()
    return planner.plan(time_budget_hours=time_hours, strategy=strat, device_class=dev)