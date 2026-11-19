"""The case/reference contract common to every primitive spec.

The legacy per-package triples repeated four assertions for every primitive:
the case factory is deterministic under one seed and varies with the seed, the
reference entrypoint varies with the case, and the case's tensors live on the
requested device. Those properties are axis-independent, so they are asserted
once here over the registry; each axis adds only its own output contract.

Seed-insensitivity is a *contract* of a law that cannot read a seed, not a gap.
A substrate factory is a function of its spec (the case seed only names the
case), and a no-op plasticity returns its input unchanged. Both are declared
below with the reason; everything else must vary with the seed.
"""

from __future__ import annotations

import dataclasses

import pytest
import torch

from computronium.acceleration.parity import digest
from computronium.primitives.registry import list_primitives
from tests.primitives._contract import (
    axis_specs,
    case_class,
    config_reads,
    make_case,
    payload,
    reference,
    tensor_vector,
    tensors,
)

SPECS = tuple(
    sorted(
        (spec for spec in list_primitives()),
        key=lambda spec: spec.id,
    )
)
IDS = [spec.id for spec in SPECS]

#: Specs whose reference output legitimately ignores the seed.
SEED_BLIND: dict[str, str] = {
    **{
        spec.id: "a substrate is a function of its spec, not of the case seed"
        for spec in axis_specs("substrate")
    },
    "primitive.plasticity.null": "no-op plasticity returns its input unchanged",
    "primitive.plasticity.substrate_coupled": "psi is the substrate coupling",
}


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_case_is_the_type_its_module_declares(spec) -> None:
    """A case factory returns its module's ``Case`` type, else a dataclass case."""
    declared = case_class(spec)
    case = make_case(spec, seed=0)
    assert declared is not None or dataclasses.is_dataclass(case), spec.id
    if declared is not None:
        assert isinstance(case, declared), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_case_config_supplies_every_key_the_reference_reads(spec) -> None:
    """The case config names every knob its reference reads, defaults included."""
    missing = config_reads(spec) - set(make_case(spec, seed=0).config)
    assert not missing, (spec.id, sorted(missing))


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_case_is_seed_deterministic(spec) -> None:
    """Two case factories on one seed produce the same payload."""
    first = make_case(spec, seed=42)
    second = make_case(spec, seed=42)
    assert torch.equal(tensor_vector(payload(first)), tensor_vector(payload(second))), (
        spec.id
    )


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_case_follows_the_seed(spec) -> None:
    """Different seeds produce different case payloads, or record the seed."""
    first = make_case(spec, seed=0)
    second = make_case(spec, seed=1)
    differs = not torch.equal(
        tensor_vector(payload(first)), tensor_vector(payload(second))
    )
    assert differs or first.config["seed"] != second.config["seed"], spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_case_places_its_tensors_on_the_requested_device(spec) -> None:
    """Every tensor in the case lives on the requested device."""
    case = make_case(spec, device="cpu", seed=0)
    assert all(tensor.device.type == "cpu" for tensor in tensors(payload(case))), (
        spec.id
    )


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_reference_follows_the_seed(spec) -> None:
    """The reference entrypoint reads the case it is given."""
    if spec.id in SEED_BLIND:
        pytest.skip(SEED_BLIND[spec.id])
    outputs = [reference(spec, make_case(spec, seed=seed)) for seed in (0, 1)]
    assert digest(outputs[0]) != digest(outputs[1]), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_reference_output_is_finite(spec) -> None:
    """No reference output tensor contains NaN or infinity."""
    output = reference(spec, make_case(spec, seed=0))
    for tensor in tensors(output):
        assert tensor.isfinite().all(), spec.id
