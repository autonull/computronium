"""Shared utilities for substrate energy estimation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple


class EnergyEstimate(NamedTuple):
    """Energy estimate components."""

    forward_energy_per_batch: float
    update_energy_per_batch: float
    total_energy_per_step: float
    energy_per_sample: float


@dataclass(frozen=True, slots=True)
class LayerShapes:
    """Extracted and validated layer shapes for energy estimation."""

    batch: int
    in_features: int
    out_features: int
    num_layers: int


def extract_layer_shapes(
    input_shape: tuple[int, ...],
    weight_shape: tuple[int, ...],
    num_layers: int = 1,
) -> LayerShapes:
    """Extract and validate layer shapes for energy estimation.

    Args:
        input_shape: Shape of input tensor (batch, ..., in_features)
        weight_shape: Shape of weight tensor (out_features, in_features)
        num_layers: Number of layers using this substrate

    Returns:
        LayerShapes with validated dimensions

    Raises:
        ValueError: If input feature dimensions don't match
    """
    batch = input_shape[0]
    in_features = input_shape[-1]
    out_features = weight_shape[0]
    in_features_w = weight_shape[1]

    if in_features != in_features_w:
        raise ValueError(f"Input feature mismatch: {in_features} != {in_features_w}")

    return LayerShapes(
        batch=batch,
        in_features=in_features,
        out_features=out_features,
        num_layers=num_layers,
    )


def build_energy_estimate(
    forward_energy: float,
    update_energy: float,
    batch_size: int,
    num_layers: int = 1,
) -> EnergyEstimate:
    """Build energy estimate dictionary from per-layer forward/update energies.

    Args:
        forward_energy: Energy per forward pass (single layer, single batch)
        update_energy: Energy per weight update (single layer, single batch)
        batch_size: Batch size
        num_layers: Number of layers

    Returns:
        EnergyEstimate with all four required fields
    """
    total_energy = (forward_energy + update_energy) * num_layers
    return EnergyEstimate(
        forward_energy_per_batch=forward_energy,
        update_energy_per_batch=update_energy,
        total_energy_per_step=total_energy,
        energy_per_sample=total_energy / batch_size,
    )


def estimate_digital_energy(
    shapes: LayerShapes, energy_per_flop: float = 1e-12
) -> EnergyEstimate:
    """Estimate energy for digital substrate (GPU/CPU).

    Args:
        shapes: Validated layer shapes
        energy_per_flop: Energy per FLOP (default: 1 pJ for FP32 on GPU)

    Returns:
        EnergyEstimate for digital substrate
    """
    # FLOPs for matrix multiply: 2 * M * N * K (multiply-add = 2 ops)
    flops_per_forward = 2 * shapes.batch * shapes.in_features * shapes.out_features
    flops_per_update = flops_per_forward  # Backward pass similar cost

    forward_energy = flops_per_forward * energy_per_flop
    update_energy = flops_per_update * energy_per_flop

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_analog_energy(
    shapes: LayerShapes,
    energy_per_mac: float = 1e-13,
    adc_dac_energy_per_output: float = 1e-12,
) -> EnergyEstimate:
    """Estimate energy for analog substrate.

    Args:
        shapes: Validated layer shapes
        energy_per_mac: Energy per MAC (default: 0.1 pJ)
        adc_dac_energy_per_output: ADC/DAC overhead per output element (default: 1 pJ)

    Returns:
        EnergyEstimate for analog substrate
    """
    macs_per_forward = shapes.batch * shapes.in_features * shapes.out_features
    macs_per_update = macs_per_forward

    adc_dac_energy = shapes.out_features * shapes.batch * adc_dac_energy_per_output

    forward_energy = macs_per_forward * energy_per_mac + adc_dac_energy
    update_energy = macs_per_update * energy_per_mac + adc_dac_energy

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_memristive_energy(
    shapes: LayerShapes,
    energy_per_mac: float = 1e-15,
    programming_energy_per_device: float = 1e-14,
) -> EnergyEstimate:
    """Estimate energy for memristive crossbar substrate.

    Args:
        shapes: Validated layer shapes
        energy_per_mac: Energy per MAC (default: 1 fJ)
        programming_energy_per_device: Programming energy per device (default: 10 fJ)

    Returns:
        EnergyEstimate for memristive substrate
    """
    macs_per_forward = shapes.batch * shapes.in_features * shapes.out_features
    macs_per_update = macs_per_forward

    num_devices = 2 * shapes.in_features * shapes.out_features  # Differential pair
    programming_energy = num_devices * programming_energy_per_device

    forward_energy = macs_per_forward * energy_per_mac
    update_energy = macs_per_update * energy_per_mac + programming_energy

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_neuromorphic_energy(
    shapes: LayerShapes,
    sparsity: float = 0.5,
    energy_per_event: float = 1e-14,
    neuron_energy_per_output: float = 1e-13,
) -> EnergyEstimate:
    """Estimate energy for neuromorphic substrate.

    Args:
        shapes: Validated layer shapes
        sparsity: Sparsity ratio (default: 0.5)
        energy_per_event: Energy per synaptic event (default: 0.01 pJ)
        neuron_energy_per_output: Neuron update overhead per output (default: 0.1 pJ)

    Returns:
        EnergyEstimate for neuromorphic substrate
    """
    effective_macs_per_forward = (
        shapes.batch * shapes.in_features * shapes.out_features * (1 - sparsity)
    )
    effective_macs_per_update = effective_macs_per_forward

    neuron_energy = shapes.out_features * shapes.batch * neuron_energy_per_output

    forward_energy = effective_macs_per_forward * energy_per_event + neuron_energy
    update_energy = effective_macs_per_update * energy_per_event + neuron_energy

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_optical_energy(
    shapes: LayerShapes,
    laser_power: float = 1e-3,
    time_per_step: float = 1e-9,
    phase_shifter_energy: float = 1e-14,
) -> EnergyEstimate:
    """Estimate energy for optical/photonic substrate.

    Args:
        shapes: Validated layer shapes
        laser_power: Laser power in watts (default: 1 mW)
        time_per_step: Time per step in seconds (default: 1 ns)
        phase_shifter_energy: Energy per phase shifter (default: 10 fJ)

    Returns:
        EnergyEstimate for optical substrate
    """
    laser_energy = laser_power * time_per_step
    phase_shifter_energy_total = (
        shapes.in_features * shapes.out_features * phase_shifter_energy
    )

    forward_energy = laser_energy
    update_energy = laser_energy + phase_shifter_energy_total

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_quantum_energy(
    shapes: LayerShapes,
    gate_energy_per_gate: float = 1e-18,
    control_energy_per_qubit: float = 1e-12,
    ec_overhead: int = 10,
) -> EnergyEstimate:
    """Estimate energy for quantum substrate.

    Args:
        shapes: Validated layer shapes
        gate_energy_per_gate: Energy per gate (default: 1 aJ for superconducting)
        control_energy_per_qubit: Control/readout energy per qubit (default: 1 pJ)
        ec_overhead: Error correction overhead factor (default: 10x)

    Returns:
        EnergyEstimate for quantum substrate
    """
    num_qubits = max(shapes.in_features, shapes.out_features)
    circuit_depth = int(num_qubits * 2)
    num_gates = circuit_depth * num_qubits

    gate_energy = num_gates * gate_energy_per_gate
    shots = shapes.batch
    control_energy = num_qubits * shots * control_energy_per_qubit

    forward_energy = (gate_energy + control_energy) * ec_overhead
    update_energy = forward_energy  # Similar for variational update

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_complex_energy(
    shapes: LayerShapes,
    energy_per_flop: float = 1e-12,
) -> EnergyEstimate:
    """Estimate energy for complex-valued substrate (emulated).

    Args:
        shapes: Validated layer shapes
        energy_per_flop: Energy per real FLOP (default: 1 pJ)

    Returns:
        EnergyEstimate for complex substrate
    """
    # Complex MAC = 4 real MACs
    real_macs_per_forward = 4 * shapes.batch * shapes.in_features * shapes.out_features
    real_macs_per_update = real_macs_per_forward

    # FLOPs = 2 * MACs for real (multiply-add), so 8 FLOPs per complex MAC
    real_flops_per_forward = 2 * real_macs_per_forward
    real_flops_per_update = 2 * real_macs_per_update

    forward_energy = real_flops_per_forward * energy_per_flop
    update_energy = real_flops_per_update * energy_per_flop

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_sparse_energy(
    shapes: LayerShapes,
    sparsity: float = 0.9,
    energy_per_mac: float = 5e-13,
    indexing_overhead: float = 0.1,
) -> EnergyEstimate:
    """Estimate energy for sparse substrate.

    Args:
        shapes: Validated layer shapes
        sparsity: Sparsity ratio (default: 0.9)
        energy_per_mac: Energy per sparse MAC (default: 0.5 pJ)
        indexing_overhead: Indexing overhead fraction (default: 10%)

    Returns:
        EnergyEstimate for sparse substrate
    """
    effective_macs_per_forward = (
        shapes.batch * shapes.in_features * shapes.out_features * (1 - sparsity)
    )
    effective_macs_per_update = effective_macs_per_forward

    forward_energy = (
        effective_macs_per_forward * energy_per_mac * (1 + indexing_overhead)
    )
    update_energy = effective_macs_per_update * energy_per_mac * (1 + indexing_overhead)

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_ternary_energy(
    shapes: LayerShapes,
    energy_per_mac: float = 1e-13,
) -> EnergyEstimate:
    """Estimate energy for ternary substrate.

    Args:
        shapes: Validated layer shapes
        energy_per_mac: Energy per ternary MAC (default: 0.1 pJ)

    Returns:
        EnergyEstimate for ternary substrate
    """
    macs_per_forward = shapes.batch * shapes.in_features * shapes.out_features
    macs_per_update = macs_per_forward

    forward_energy = macs_per_forward * energy_per_mac
    update_energy = macs_per_update * energy_per_mac

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


def estimate_quantized_energy(
    shapes: LayerShapes,
    energy_per_mac: float = 2e-13,
) -> EnergyEstimate:
    """Estimate energy for int8 quantized substrate.

    Args:
        shapes: Validated layer shapes
        energy_per_mac: Energy per INT8 MAC (default: 0.2 pJ)

    Returns:
        EnergyEstimate for quantized substrate
    """
    macs_per_forward = shapes.batch * shapes.in_features * shapes.out_features
    macs_per_update = macs_per_forward

    forward_energy = macs_per_forward * energy_per_mac
    update_energy = macs_per_update * energy_per_mac

    return build_energy_estimate(
        forward_energy, update_energy, shapes.batch, shapes.num_layers
    )


__all__ = [
    "EnergyEstimate",
    "LayerShapes",
    "build_energy_estimate",
    "estimate_analog_energy",
    "estimate_complex_energy",
    "estimate_digital_energy",
    "estimate_memristive_energy",
    "estimate_neuromorphic_energy",
    "estimate_optical_energy",
    "estimate_quantized_energy",
    "estimate_quantum_energy",
    "estimate_sparse_energy",
    "estimate_ternary_energy",
    "extract_layer_shapes",
]
