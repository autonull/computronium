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
    "ConstraintConfig",
    "CostConfig",
    "DeviceModel",
    "ExecutionModel",
    "NoiseConfig",
    "NumericRepresentation",
    "SubstrateSpec",
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
