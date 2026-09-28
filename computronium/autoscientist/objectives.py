"""Objective registry for multi-objective AutoScientist (TODO31 Phase 1).

Defines objectives, their optimization directions, normalization, and axis grouping
for the 6-axis ontology (S×G×D×P×C×U).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable


class Objective(StrEnum):
    """All objectives the AutoScientist can optimize.

    Grouped by ontology axis for dashboard organization.
    """

    # Primary task objectives
    ACCURACY = "accuracy"

    # Resource objectives (Cost axis)
    WALLTIME_S = "walltime_s"
    PARAM_COUNT = "param_count"
    FLOPS = "flops"
    MEMORY_MB = "memory_mb"
    ENERGY_PER_STEP = "energy_per_step"
    LATENCY_MS = "latency_ms"

    # Substrate-aware objectives (Substrate axis) — TODO31 Phase 3.6 / TODO40 P2.2
    ENERGY_PER_OP = "energy_per_op"
    IR_DROP_VARIANCE = "ir_drop_variance"
    WRITE_ENERGY_PJ = "write_energy_pj"
    ENDURANCE_CYCLES = "endurance_cycles"
    SPIKE_RATE = "spike_rate"
    EVENT_DENSITY = "event_density"
    SYNAPTIC_OPS_PER_SAMPLE = "synaptic_ops_per_sample"
    SPIKE_ENERGY_PJ = "spike_energy_pj"
    PHASE_NOISE = "phase_noise"
    OPTICAL_POWER_MW = "optical_power_mw"
    INSERTION_LOSS_DB = "insertion_loss_db"
    PHASE_SHIFTER_ENERGY_PJ = "phase_shifter_energy_pj"
    GATE_FIDELITY = "gate_fidelity"
    COHERENCE_TIME_US = "coherence_time_us"
    SHOT_NOISE = "shot_noise"
    QUBIT_COUNT = "qubit_count"
    THERMAL_NOISE_VARIANCE = "thermal_noise_variance"
    NONLINEARITY_ERROR = "nonlinearity_error"
    DRIFT_RATE = "drift_rate"
    PRECISION_BITS = "precision_bits"

    # Ruler-relative objectives (Task axis)
    BP_DEFICIT = "bp_deficit"
    RULER_WALLTIME_RATIO = "ruler_walltime_ratio"
    RULER_ENERGY_RATIO = "ruler_energy_ratio"

    # Stability objectives (Dynamics axis)
    SPECTRAL_RADIUS = "spectral_radius"
    LYAPUNOV_EXPONENT = "lyapunov_exponent"
    MAX_SINGULAR_VALUE = "max_singular_value"

    # Plasticity objectives (Plasticity axis)
    PSI_CAPACITY = "psi_capacity"
    CONSOLIDATION_COST = "consolidation_cost"
    REWRITE_RATE = "rewrite_rate"

    # Credit objectives (Credit axis)
    CREDIT_ALIGNMENT = "credit_alignment"
    FEEDBACK_PATH_LENGTH = "feedback_path_length"
    TRACE_VARIANCE = "trace_variance"

    # Composite objectives (cross-axis)
    STABILITY_PLASTICITY_RATIO = (
        "stability_plasticity_ratio"  # spectral_radius / psi_capacity
    )
    CREDIT_EFFICIENCY = "credit_efficiency"  # credit_alignment / flops


@dataclass(frozen=True, slots=True)
class ObjectiveSpec:
    """One objective in a multi-objective optimization."""

    name: Objective
    direction: Literal["maximize", "minimize"]
    weight: float = 1.0
    normalizer: Callable[[float], float] | None = None
    axis: str | None = None


# Default normalizers for common objectives
def normalize_accuracy(x: float) -> float:
    return x


def normalize_walltime(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_param_count(x: float) -> float:
    return 1.0 / (1.0 + x / 1e6)


def normalize_flops(x: float) -> float:
    return 1.0 / (1.0 + x / 1e9)


def normalize_memory_mb(x: float) -> float:
    return 1.0 / (1.0 + x / 1024)


def normalize_energy_per_step(x: float) -> float:
    return 1.0 / (1.0 + x / 1e-3)


def normalize_latency_ms(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_spectral_radius(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x - 1.0))


def normalize_lyapunov_exponent(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x))


def normalize_max_singular_value(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x - 1.0))


def normalize_psi_capacity(x: float) -> float:
    return x / (1.0 + x)


def normalize_consolidation_cost(x: float) -> float:
    return 1.0 / (1.0 + x / 1e3)


def normalize_credit_alignment(x: float) -> float:
    return (x + 1.0) / 2.0


def normalize_feedback_path_length(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_trace_variance(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_bp_deficit(x: float) -> float:
    return 1.0 - x


def normalize_ruler_ratio(x: float) -> float:
    return 1.0 / (1.0 + max(0.0, x - 1.0))


def normalize_stability_plasticity_ratio(x: float) -> float:
    """Lower ratio is better (more stable per unit plasticity)."""
    return 1.0 / (1.0 + x)


def normalize_credit_efficiency(x: float) -> float:
    """Higher is better (more alignment per FLOP)."""
    return x / (1.0 + x)


def normalize_energy_per_op(x: float) -> float:
    return 1.0 / (1.0 + x / 1e-12)


def normalize_ir_drop_variance(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_write_energy_pj(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_endurance_cycles(x: float) -> float:
    return x / (1.0 + x / 1e12)


def normalize_spike_rate(x: float) -> float:
    return 1.0 / (1.0 + x / 1e3)


def normalize_event_density(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_synaptic_ops_per_sample(x: float) -> float:
    return 1.0 / (1.0 + x / 1e6)


def normalize_spike_energy_pj(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_phase_noise(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_optical_power_mw(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_insertion_loss_db(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_phase_shifter_energy_pj(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_gate_fidelity(x: float) -> float:
    return x


def normalize_coherence_time_us(x: float) -> float:
    return x / (1.0 + x / 1e3)


def normalize_shot_noise(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_qubit_count(x: float) -> float:
    return x / (1.0 + x / 1e3)


def normalize_thermal_noise_variance(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_nonlinearity_error(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_drift_rate(x: float) -> float:
    return 1.0 / (1.0 + x)


def normalize_precision_bits(x: float) -> float:
    return x / (1.0 + x / 32)


DEFAULT_NORMALIZERS: dict[Objective, Callable[[float], float]] = {
    Objective.ACCURACY: normalize_accuracy,
    Objective.WALLTIME_S: normalize_walltime,
    Objective.PARAM_COUNT: normalize_param_count,
    Objective.FLOPS: normalize_flops,
    Objective.MEMORY_MB: normalize_memory_mb,
    Objective.ENERGY_PER_STEP: normalize_energy_per_step,
    Objective.LATENCY_MS: normalize_latency_ms,
    Objective.ENERGY_PER_OP: normalize_energy_per_op,
    Objective.IR_DROP_VARIANCE: normalize_ir_drop_variance,
    Objective.WRITE_ENERGY_PJ: normalize_write_energy_pj,
    Objective.ENDURANCE_CYCLES: normalize_endurance_cycles,
    Objective.SPIKE_RATE: normalize_spike_rate,
    Objective.EVENT_DENSITY: normalize_event_density,
    Objective.SYNAPTIC_OPS_PER_SAMPLE: normalize_synaptic_ops_per_sample,
    Objective.SPIKE_ENERGY_PJ: normalize_spike_energy_pj,
    Objective.PHASE_NOISE: normalize_phase_noise,
    Objective.OPTICAL_POWER_MW: normalize_optical_power_mw,
    Objective.INSERTION_LOSS_DB: normalize_insertion_loss_db,
    Objective.PHASE_SHIFTER_ENERGY_PJ: normalize_phase_shifter_energy_pj,
    Objective.GATE_FIDELITY: normalize_gate_fidelity,
    Objective.COHERENCE_TIME_US: normalize_coherence_time_us,
    Objective.SHOT_NOISE: normalize_shot_noise,
    Objective.QUBIT_COUNT: normalize_qubit_count,
    Objective.THERMAL_NOISE_VARIANCE: normalize_thermal_noise_variance,
    Objective.NONLINEARITY_ERROR: normalize_nonlinearity_error,
    Objective.DRIFT_RATE: normalize_drift_rate,
    Objective.PRECISION_BITS: normalize_precision_bits,
    Objective.SPECTRAL_RADIUS: normalize_spectral_radius,
    Objective.LYAPUNOV_EXPONENT: normalize_lyapunov_exponent,
    Objective.MAX_SINGULAR_VALUE: normalize_max_singular_value,
    Objective.PSI_CAPACITY: normalize_psi_capacity,
    Objective.CONSOLIDATION_COST: normalize_consolidation_cost,
    Objective.CREDIT_ALIGNMENT: normalize_credit_alignment,
    Objective.FEEDBACK_PATH_LENGTH: normalize_feedback_path_length,
    Objective.TRACE_VARIANCE: normalize_trace_variance,
    Objective.BP_DEFICIT: normalize_bp_deficit,
    Objective.RULER_WALLTIME_RATIO: normalize_ruler_ratio,
    Objective.RULER_ENERGY_RATIO: normalize_ruler_ratio,
    Objective.STABILITY_PLASTICITY_RATIO: normalize_stability_plasticity_ratio,
    Objective.CREDIT_EFFICIENCY: normalize_credit_efficiency,
}


OBJECTIVE_DIRECTION: dict[Objective, Literal["maximize", "minimize"]] = {
    Objective.ACCURACY: "maximize",
    Objective.WALLTIME_S: "minimize",
    Objective.PARAM_COUNT: "minimize",
    Objective.FLOPS: "minimize",
    Objective.MEMORY_MB: "minimize",
    Objective.ENERGY_PER_STEP: "minimize",
    Objective.LATENCY_MS: "minimize",
    Objective.ENERGY_PER_OP: "minimize",
    Objective.IR_DROP_VARIANCE: "minimize",
    Objective.WRITE_ENERGY_PJ: "minimize",
    Objective.ENDURANCE_CYCLES: "maximize",
    Objective.SPIKE_RATE: "minimize",
    Objective.EVENT_DENSITY: "minimize",
    Objective.SYNAPTIC_OPS_PER_SAMPLE: "minimize",
    Objective.SPIKE_ENERGY_PJ: "minimize",
    Objective.PHASE_NOISE: "minimize",
    Objective.OPTICAL_POWER_MW: "minimize",
    Objective.INSERTION_LOSS_DB: "minimize",
    Objective.PHASE_SHIFTER_ENERGY_PJ: "minimize",
    Objective.GATE_FIDELITY: "maximize",
    Objective.COHERENCE_TIME_US: "maximize",
    Objective.SHOT_NOISE: "minimize",
    Objective.QUBIT_COUNT: "maximize",
    Objective.THERMAL_NOISE_VARIANCE: "minimize",
    Objective.NONLINEARITY_ERROR: "minimize",
    Objective.DRIFT_RATE: "minimize",
    Objective.PRECISION_BITS: "maximize",
    Objective.BP_DEFICIT: "minimize",
    Objective.RULER_WALLTIME_RATIO: "minimize",
    Objective.RULER_ENERGY_RATIO: "minimize",
    Objective.SPECTRAL_RADIUS: "minimize",
    Objective.LYAPUNOV_EXPONENT: "minimize",
    Objective.MAX_SINGULAR_VALUE: "minimize",
    Objective.PSI_CAPACITY: "maximize",
    Objective.CONSOLIDATION_COST: "minimize",
    Objective.REWRITE_RATE: "maximize",
    Objective.CREDIT_ALIGNMENT: "maximize",
    Objective.FEEDBACK_PATH_LENGTH: "minimize",
    Objective.TRACE_VARIANCE: "minimize",
    Objective.STABILITY_PLASTICITY_RATIO: "minimize",
    Objective.CREDIT_EFFICIENCY: "maximize",
}

OBJECTIVE_AXIS: dict[Objective, str] = {
    Objective.ENERGY_PER_STEP: "S",
    Objective.PARAM_COUNT: "G",
    Objective.FLOPS: "G",
    Objective.MEMORY_MB: "G",
    Objective.ENERGY_PER_OP: "S",
    Objective.IR_DROP_VARIANCE: "S",
    Objective.WRITE_ENERGY_PJ: "S",
    Objective.ENDURANCE_CYCLES: "S",
    Objective.SPIKE_RATE: "S",
    Objective.EVENT_DENSITY: "S",
    Objective.SYNAPTIC_OPS_PER_SAMPLE: "S",
    Objective.SPIKE_ENERGY_PJ: "S",
    Objective.PHASE_NOISE: "S",
    Objective.OPTICAL_POWER_MW: "S",
    Objective.INSERTION_LOSS_DB: "S",
    Objective.PHASE_SHIFTER_ENERGY_PJ: "S",
    Objective.GATE_FIDELITY: "S",
    Objective.COHERENCE_TIME_US: "S",
    Objective.SHOT_NOISE: "S",
    Objective.QUBIT_COUNT: "S",
    Objective.THERMAL_NOISE_VARIANCE: "S",
    Objective.NONLINEARITY_ERROR: "S",
    Objective.DRIFT_RATE: "S",
    Objective.PRECISION_BITS: "S",
    Objective.SPECTRAL_RADIUS: "D",
    Objective.LYAPUNOV_EXPONENT: "D",
    Objective.MAX_SINGULAR_VALUE: "D",
    Objective.PSI_CAPACITY: "P",
    Objective.CONSOLIDATION_COST: "P",
    Objective.REWRITE_RATE: "P",
    Objective.CREDIT_ALIGNMENT: "C",
    Objective.FEEDBACK_PATH_LENGTH: "C",
    Objective.TRACE_VARIANCE: "C",
    Objective.ACCURACY: "task",
    Objective.BP_DEFICIT: "task",
    Objective.RULER_WALLTIME_RATIO: "task",
    Objective.RULER_ENERGY_RATIO: "task",
    Objective.WALLTIME_S: "cost",
    Objective.LATENCY_MS: "cost",
    Objective.STABILITY_PLASTICITY_RATIO: "D",
    Objective.CREDIT_EFFICIENCY: "C",
}


def make_objective_spec(name: Objective, weight: float = 1.0) -> ObjectiveSpec:
    """Create an ObjectiveSpec with defaults from registry."""
    return ObjectiveSpec(
        name=name,
        direction=OBJECTIVE_DIRECTION[name],
        weight=weight,
        normalizer=DEFAULT_NORMALIZERS.get(name),
        axis=OBJECTIVE_AXIS.get(name),
    )


DEFAULT_OBJECTIVES: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.WALLTIME_S),
)

PRESET_ACCURACY_WALLTIME_PARAMS: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.WALLTIME_S),
    make_objective_spec(Objective.PARAM_COUNT),
)

PRESET_FULL_COST: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.WALLTIME_S),
    make_objective_spec(Objective.PARAM_COUNT),
    make_objective_spec(Objective.FLOPS),
    make_objective_spec(Objective.MEMORY_MB),
)

PRESET_EFFICIENCY: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.WALLTIME_S),
    make_objective_spec(Objective.PARAM_COUNT),
    make_objective_spec(Objective.ENERGY_PER_STEP),
)

PRESET_STABILITY_PLASTICITY: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.SPECTRAL_RADIUS),
    make_objective_spec(Objective.PSI_CAPACITY),
)

PRESET_STABILITY_PLASTICITY_RATIO: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.STABILITY_PLASTICITY_RATIO),
    make_objective_spec(Objective.PSI_CAPACITY),
)

PRESET_CREDIT_EFFICIENCY: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.CREDIT_ALIGNMENT),
    make_objective_spec(Objective.FEEDBACK_PATH_LENGTH),
)

PRESET_CREDIT_EFFICIENCY_FULL: tuple[ObjectiveSpec, ...] = (
    make_objective_spec(Objective.ACCURACY),
    make_objective_spec(Objective.CREDIT_EFFICIENCY),
    make_objective_spec(Objective.CREDIT_ALIGNMENT),
    make_objective_spec(Objective.FEEDBACK_PATH_LENGTH),
    make_objective_spec(Objective.TRACE_VARIANCE),
)


def parse_objectives(spec: str) -> tuple[ObjectiveSpec, ...]:
    """Parse comma-separated objective names into ObjectiveSpec tuple.

    Example: "accuracy,walltime,param_count" -> (ObjectiveSpec(...), ...)
    """
    names = [n.strip() for n in spec.split(",") if n.strip()]
    if not names:
        return DEFAULT_OBJECTIVES
    specs = []
    for name in names:
        try:
            obj = Objective(name)
        except ValueError:
            raise ValueError(
                f"Unknown objective: {name}. Valid: {[o.value for o in Objective]}"
            )
        specs.append(make_objective_spec(obj))
    return tuple(specs)


def objective_names(specs: tuple[ObjectiveSpec, ...]) -> tuple[str, ...]:
    """Extract objective names for display."""
    return tuple(s.name.value for s in specs)


__all__ = [
    "DEFAULT_NORMALIZERS",
    "DEFAULT_OBJECTIVES",
    "OBJECTIVE_AXIS",
    "OBJECTIVE_DIRECTION",
    "PRESET_ACCURACY_WALLTIME_PARAMS",
    "PRESET_CREDIT_EFFICIENCY",
    "PRESET_CREDIT_EFFICIENCY_FULL",
    "PRESET_EFFICIENCY",
    "PRESET_FULL_COST",
    "PRESET_STABILITY_PLASTICITY",
    "PRESET_STABILITY_PLASTICITY_RATIO",
    "Objective",
    "ObjectiveSpec",
    "make_objective_spec",
    "objective_names",
    "parse_objectives",
]
