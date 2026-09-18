"""SubstrateSpec: structured substrate description (TODO18 4.1).

Decomposes a substrate into orthogonal, composable dimensions — execution
model, device model, numeric representation, noise, structural constraints,
and cost — so compound configurations ("noisy + sparse + complex") are
stated explicitly instead of implied by class choice. Round-trips with the
legacy :class:`SubstrateConfig`; ``make_substrate`` builds the concrete
substrate instance from a spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Literal

from computronium.ontology.substrate._substrate import SubstrateType

if TYPE_CHECKING:
    from computronium.ontology.substrate._substrate import Substrate, SubstrateConfig

__all__ = [
    "SUBSTRATE_OBJECTIVE_MAP",
    "ConstraintConfig",
    "CostConfig",
    "DeviceModel",
    "ExecutionModel",
    "NoiseConfig",
    "NumericRepresentation",
    "SubstrateSpec",
    "compute_substrate_objectives",
    "make_substrate",
]


class ExecutionModel(StrEnum):
    """How the substrate's physics are realized."""

    NATIVE = "native"
    SIMULATED = "simulated"
    EMULATED = "emulated"


class DeviceModel(StrEnum):
    """Physical device family the substrate models."""

    DIGITAL = "digital"
    MEMRISTIVE = "memristive"
    PHOTONIC = "photonic"
    QUANTUM = "quantum"
    ANALOG = "analog"
    NEUROMORPHIC = "neuromorphic"


class NumericRepresentation(StrEnum):
    """Value domain of substrate state and weights."""

    REAL = "real"
    COMPLEX = "complex"
    TERNARY = "ternary"
    INT8 = "int8"


_NOISE_KIND = Literal["none", "additive_gaussian"]


@dataclass(frozen=True, slots=True)
class NoiseConfig:
    """Additive noise characterization of the substrate."""

    kind: _NOISE_KIND = "none"
    level: float = 0.0


@dataclass(frozen=True, slots=True)
class ConstraintConfig:
    """Structural constraints the substrate enforces on state/weights."""

    weight_bounds: tuple[float, float] | None = None
    sparsity: float = 0.0


@dataclass(frozen=True, slots=True)
class CostConfig:
    """Resource cost accounting coefficients (simulated energy, FLOPs weights)."""

    joules_per_mac: float = 0.0
    fab_cost_ratio: float = 1.0


_PRECISION_TO_NUMERIC: dict[str, NumericRepresentation] = {
    "float32": NumericRepresentation.REAL,
    "float16": NumericRepresentation.REAL,
    "bfloat16": NumericRepresentation.REAL,
    "complex": NumericRepresentation.COMPLEX,
    "ternary": NumericRepresentation.TERNARY,
    "int8": NumericRepresentation.INT8,
    "int4": NumericRepresentation.INT8,
    "binary": NumericRepresentation.INT8,
}

_TYPE_TO_DEVICE: dict[str, DeviceModel] = {
    "digital": DeviceModel.DIGITAL,
    "analog": DeviceModel.ANALOG,
    "memristive": DeviceModel.MEMRISTIVE,
    "neuromorphic": DeviceModel.NEUROMORPHIC,
    "sparse": DeviceModel.DIGITAL,
    "ternary": DeviceModel.DIGITAL,
    "optical": DeviceModel.PHOTONIC,
    "quantum": DeviceModel.QUANTUM,
    "complex": DeviceModel.DIGITAL,
}

_SIMULATED_TYPES = frozenset({
    "analog",
    "memristive",
    "neuromorphic",
    "optical",
    "quantum",
})


@dataclass(frozen=True, slots=True)
class SubstrateSpec:
    """Fully explicit substrate description (TODO18 4.1).

    Attributes:
        execution_model: native / simulated / emulated realization.
        device_model: physical device family.
        numeric_representation: value domain of state and weights.
        noise_model: additive noise characterization.
        structural_constraints: weight bounds, sparsity, etc.
        cost_model: energy/cost coefficients.
    """

    execution_model: ExecutionModel = ExecutionModel.NATIVE
    device_model: DeviceModel = DeviceModel.DIGITAL
    numeric_representation: NumericRepresentation = NumericRepresentation.REAL
    noise_model: NoiseConfig = field(default_factory=NoiseConfig)
    structural_constraints: ConstraintConfig = field(default_factory=ConstraintConfig)
    cost_model: CostConfig = field(default_factory=CostConfig)
    # Legacy SubstrateConfig is lossy for the digital-family trio
    # (ternary/complex/sparse); when lifted from a config this hint
    # preserves the declared family through round-trips.
    substrate_type: SubstrateType | None = None

    @classmethod
    def from_config(cls, config: SubstrateConfig) -> SubstrateSpec:
        """Lift a legacy SubstrateConfig into a structured spec."""
        numeric = _PRECISION_TO_NUMERIC.get(
            config.precision, NumericRepresentation.REAL
        )
        if config.substrate_type == SubstrateType.TERNARY:
            numeric = NumericRepresentation.TERNARY
        return cls(
            execution_model=(
                ExecutionModel.SIMULATED
                if config.substrate_type.value in _SIMULATED_TYPES
                else ExecutionModel.NATIVE
            ),
            device_model=_TYPE_TO_DEVICE[config.substrate_type.value],
            numeric_representation=numeric,
            noise_model=NoiseConfig(
                kind="additive_gaussian" if config.noise_level > 0 else "none",
                level=config.noise_level,
            ),
            structural_constraints=ConstraintConfig(
                weight_bounds=config.weight_bounds,
                sparsity=config.sparsity,
            ),
            substrate_type=config.substrate_type,
        )

    def to_config(self) -> SubstrateConfig:
        """Project back to a legacy SubstrateConfig (substrate_type preserved)."""
        from computronium.ontology.substrate._substrate import (
            SubstrateConfig,
            SubstrateType,
        )

        numeric_to_precision = {
            NumericRepresentation.REAL: "float32",
            NumericRepresentation.COMPLEX: "complex",
            NumericRepresentation.TERNARY: "ternary",
            NumericRepresentation.INT8: "int8",
        }
        device_to_type = {
            DeviceModel.DIGITAL: None,  # disambiguated below
            DeviceModel.ANALOG: SubstrateType.ANALOG,
            DeviceModel.MEMRISTIVE: SubstrateType.MEMRISTIVE,
            DeviceModel.NEUROMORPHIC: SubstrateType.NEUROMORPHIC,
            DeviceModel.PHOTONIC: SubstrateType.OPTICAL,
            DeviceModel.QUANTUM: SubstrateType.QUANTUM,
        }
        substrate_type = device_to_type[self.device_model]
        if self.substrate_type is not None:
            substrate_type = self.substrate_type
        elif substrate_type is None:
            # Digital-family devices differentiate by numeric repr / constraints.
            if self.numeric_representation == NumericRepresentation.COMPLEX:
                substrate_type = SubstrateType.DIGITAL
            elif self.numeric_representation == NumericRepresentation.TERNARY:
                substrate_type = SubstrateType.TERNARY
            elif self.structural_constraints.sparsity > 0:
                substrate_type = SubstrateType.SPARSE
            else:
                substrate_type = SubstrateType.DIGITAL
        return SubstrateConfig(
            substrate_type=substrate_type,
            precision=numeric_to_precision[self.numeric_representation],
            noise_level=self.noise_model.level,
            weight_bounds=self.structural_constraints.weight_bounds,
            sparsity=self.structural_constraints.sparsity,
            device="cpu",
        )


def make_substrate(spec: SubstrateSpec) -> Substrate:
    """Build a concrete substrate instance from a SubstrateSpec.

    Delegates to :func:`substrate_from_config` on the projected config —
    single dispatch source, no duplicated class table.
    """
    from computronium.ontology.substrate._substrate import substrate_from_config

    return substrate_from_config(spec.to_config())


# --- Substrate-aware objectives (TODO31 Phase 3.6) ----------------------------


# Mapping from DeviceModel to the objectives it should auto-populate
SUBSTRATE_OBJECTIVE_MAP: dict[DeviceModel, tuple[str, ...]] = {
    DeviceModel.MEMRISTIVE: (
        "energy_per_op",
        "ir_drop_variance",
        "write_energy_pj",
        "endurance_cycles",
    ),
    DeviceModel.NEUROMORPHIC: (
        "spike_rate",
        "event_density",
        "synaptic_ops_per_sample",
        "spike_energy_pj",
    ),
    DeviceModel.PHOTONIC: (
        "phase_noise",
        "optical_power_mw",
        "insertion_loss_db",
        "phase_shifter_energy_pj",
    ),
    DeviceModel.QUANTUM: (
        "gate_fidelity",
        "coherence_time_us",
        "shot_noise",
        "qubit_count",
    ),
    DeviceModel.ANALOG: (
        "thermal_noise_variance",
        "nonlinearity_error",
        "drift_rate",
        "precision_bits",
    ),
    DeviceModel.DIGITAL: (
        "flops",
        "memory_mb",
        "energy_per_op",
        "latency_ms",
    ),
}


def compute_substrate_objectives(
    spec: SubstrateSpec,
    settle_telemetry: dict[str, float] | None = None,
    runtime_stats: dict[str, float] | None = None,
) -> dict[str, float]:
    """Compute substrate-specific objectives from spec and telemetry.

    Args:
        spec: SubstrateSpec describing the device model and characteristics.
        settle_telemetry: Per-step settle telemetry (energy, steps, etc.).
        runtime_stats: Runtime measurements (walltime, memory, etc.).

    Returns:
        Dict of objective_name -> value for the substrate's objective set.
    """
    objectives: dict[str, float] = {}
    device = spec.device_model
    settle = settle_telemetry or {}
    runtime = runtime_stats or {}

    # Common objectives for all substrates
    objectives["energy_per_step"] = settle.get("energy_per_step", 0.0)
    objectives["settle_steps_used"] = float(settle.get("settle_steps_used", 0))
    objectives["free_energy_final"] = settle.get("free_energy_final", 0.0)

    # Runtime stats (if available)
    objectives["walltime_s"] = runtime.get("walltime_s", 0.0)
    objectives["memory_mb"] = runtime.get("memory_mb", 0.0)
    objectives["flops"] = runtime.get("flops", 0.0)
    objectives["latency_ms"] = runtime.get("latency_ms", 0.0)

    # Device-specific objectives
    match device:
        case DeviceModel.MEMRISTIVE:
            # Memristive: IR-drop, write energy, endurance
            objectives["energy_per_op"] = spec.cost_model.joules_per_mac * 1e12  # pJ
            # IR-drop variance: modeled as noise_level * weight_bounds spread
            wb = spec.structural_constraints.weight_bounds
            if wb:
                spread = abs(wb[1] - wb[0])
                objectives["ir_drop_variance"] = spec.noise_model.level * spread
            else:
                objectives["ir_drop_variance"] = 0.0
            objectives["write_energy_pj"] = (
                spec.cost_model.joules_per_mac * 1e12 * 10
            )  # Write ~10x MAC
            objectives["endurance_cycles"] = 1e12  # Typical endurance

        case DeviceModel.NEUROMORPHIC:
            # Neuromorphic: spike rate, event density
            objectives["spike_rate"] = settle.get("spike_rate", 0.0)
            objectives["event_density"] = settle.get("event_density", 0.0)
            # Synaptic ops per sample: approximate from spike rate
            objectives["synaptic_ops_per_sample"] = (
                objectives["spike_rate"] * 100
            )  # Fan-in proxy
            objectives["spike_energy_pj"] = spec.cost_model.joules_per_mac * 1e12

        case DeviceModel.PHOTONIC:
            # Photonic: phase noise, optical power
            objectives["phase_noise"] = spec.noise_model.level
            objectives["optical_power_mw"] = (
                spec.cost_model.joules_per_mac * 1e3 * 1e6
            )  # mW proxy
            objectives["insertion_loss_db"] = (
                0.1 * spec.noise_model.level * 100
            )  # Proxy
            objectives["phase_shifter_energy_pj"] = (
                spec.cost_model.joules_per_mac * 1e12
            )

        case DeviceModel.QUANTUM:
            # Quantum: gate fidelity, coherence time
            objectives["gate_fidelity"] = 1.0 - spec.noise_model.level
            objectives["coherence_time_us"] = 100.0 / max(spec.noise_model.level, 1e-6)
            objectives["shot_noise"] = spec.noise_model.level
            objectives["qubit_count"] = float(runtime.get("qubit_count", 0))

        case DeviceModel.ANALOG:
            # Analog: thermal noise, nonlinearity, drift
            objectives["thermal_noise_variance"] = spec.noise_model.level**2
            objectives["nonlinearity_error"] = (
                spec.structural_constraints.sparsity * 0.1
            )
            objectives["drift_rate"] = 1e-6  # Proxy
            objectives["precision_bits"] = 10.0  # Proxy

        case DeviceModel.DIGITAL:
            # Digital: already captured in common
            pass

    return objectives


def get_substrate_objective_names(device: DeviceModel) -> tuple[str, ...]:
    """Get the objective names for a device model."""
    return SUBSTRATE_OBJECTIVE_MAP.get(device, ())
