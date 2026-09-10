"""SubstrateSpec round-trip and compound construction (TODO18 4.1).

Level 4 sampled numerical tests: every legacy SubstrateConfig preset lifts
into a structured SubstrateSpec, round-trips substrate_type faithfully,
and builds the same substrate class via ``make_substrate`` as the legacy
``substrate_from_config`` dispatch.
"""

import pytest
import torch

from computronium.ontology.substrate import (
    ConstraintConfig,
    DeviceModel,
    ExecutionModel,
    NoiseConfig,
    NumericRepresentation,
    SubstrateConfig,
    SubstrateSpec,
    make_substrate,
    substrate_from_config,
)

_PRESETS = [
    "digital",
    "analog",
    "memristive",
    "neuromorphic",
    "optical",
    "quantum",
    "sparse",
    "ternary",
    "complex",
]


@pytest.mark.parametrize("name", _PRESETS)
def test_spec_roundtrip_and_factory_parity(name):
    cfg = getattr(SubstrateConfig, name)()
    spec = SubstrateSpec.from_config(cfg)

    assert spec.to_config().substrate_type == cfg.substrate_type

    via_spec = make_substrate(spec)
    via_cfg = substrate_from_config(cfg)
    assert type(via_spec) is type(via_cfg)


def test_execution_model_separates_native_from_simulated():
    native = SubstrateSpec.from_config(SubstrateConfig.digital())
    analog = SubstrateSpec.from_config(SubstrateConfig.analog())
    assert native.execution_model is ExecutionModel.NATIVE
    assert analog.execution_model is ExecutionModel.SIMULATED


def test_numeric_representation_mapping():
    assert (
        SubstrateSpec.from_config(SubstrateConfig.memristive()).numeric_representation
        is NumericRepresentation.INT8
    )
    assert (
        SubstrateSpec.from_config(SubstrateConfig.ternary()).numeric_representation
        is NumericRepresentation.TERNARY
    )


def test_compound_noisy_sparse_configuration():
    """Compound spec: noisy + sparse digital substrate stated explicitly."""
    spec = SubstrateSpec(
        execution_model=ExecutionModel.NATIVE,
        device_model=DeviceModel.DIGITAL,
        numeric_representation=NumericRepresentation.REAL,
        noise_model=NoiseConfig(kind="additive_gaussian", level=0.05),
        structural_constraints=ConstraintConfig(sparsity=0.5),
    )
    substrate = make_substrate(spec)
    assert type(substrate).__name__.startswith("Sparse")
    x = torch.randn(4, 4)
    noisy = substrate.inject_state_noise(x)
    assert noisy.shape == x.shape


def test_defaults_are_fully_stated():
    spec = SubstrateSpec()
    assert spec.execution_model is ExecutionModel.NATIVE
    assert spec.device_model is DeviceModel.DIGITAL
    assert spec.numeric_representation is NumericRepresentation.REAL
    assert spec.noise_model.kind == "none"
    assert spec.structural_constraints.weight_bounds is None
    assert spec.cost_model.joules_per_mac == pytest.approx(0.0)
