"""The case/reference contract common to every primitive spec.

The legacy per-package triples repeated four assertions for every primitive:
the case factory is deterministic under one seed and varies with the seed, the
reference entrypoint varies with the case, and the case's tensors live on the
requested device. Those properties are axis-independent, so they are asserted
once here over the registry; each axis adds only its own output contract.

Seed-insensitivity is a *contract* of a law that cannot read a seed, not a gap.
A no-op plasticity returns its input unchanged, so both are declared below with
the reason; everything else must vary with the seed.

A row the declared space refuses is ``impossible``, and only such a row may be
quiet: it carries a refusal test and a necessity test (TODO97 §0.4).
"""

from __future__ import annotations

import dataclasses

import pytest
import torch

from computronium.acceleration.parity import digest
from computronium.primitives.cases import (
    IMPOSSIBLE,
    PrimitiveImpossibleError,
    cell_config,
)
from computronium.primitives.protocol import PrimitiveCase
from computronium.primitives.registry import list_primitives
from tests.primitives._contract import (
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
        (spec for spec in list_primitives() if spec.id not in IMPOSSIBLE),
        key=lambda spec: spec.id,
    )
)
IDS = [spec.id for spec in SPECS]

#: Specs whose reference output legitimately ignores the seed.
SEED_BLIND: dict[str, str] = {
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
        pytest.skip(f"declared: {SEED_BLIND[spec.id]}")
    outputs = [reference(spec, make_case(spec, seed=seed)) for seed in (0, 1)]
    assert digest(outputs[0]) != digest(outputs[1]), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_reference_output_is_finite(spec) -> None:
    """No reference output tensor contains NaN or infinity.

    The two no-op plasticity laws return an empty plastic state by their
    declared contract, so emptiness is theirs; every other row must emit a
    tensor.
    """
    output = reference(spec, make_case(spec, seed=0))
    found = tensors(output)
    if spec.id in SEED_BLIND:
        return
    assert found, spec.id
    for tensor in found:
        assert tensor.isfinite().all(), spec.id


@pytest.mark.parametrize("primitive_id", sorted(IMPOSSIBLE))
def test_impossible_row_is_refused_by_a_declared_constraint(primitive_id: str) -> None:
    """An impossible row's refusal names the constraint that refuses it."""
    spec = next(spec for spec in list_primitives() if spec.id == primitive_id)
    with pytest.raises(PrimitiveImpossibleError) as refused:
        cell_config(spec)
    assert refused.value.constraint == IMPOSSIBLE[primitive_id], spec.id


@pytest.mark.parametrize("primitive_id", sorted(IMPOSSIBLE))
def test_impossible_row_refusal_is_necessary(primitive_id: str) -> None:
    """Compose accepts the cell; only the declared constraint refuses it.

    The system's own builder and validator accept the combination, so the void
    rule is the sole cause of the refusal — the necessity the taxonomy
    requires of an ``impossible`` row.
    """
    from computronium.experiment.kernel.compose import compose_configs
    from computronium.experiment.sec_loop import (
        _AXIS_DEFAULTS,
        _coordinate,
    )
    from computronium.primitives.cases import (
        MICRO_INPUT_SHAPE,
        MICRO_OUTPUT_DIM,
        _declared_legal,
        _family_task,
    )

    spec = next(spec for spec in list_primitives() if spec.id == primitive_id)
    axes = dict(_AXIS_DEFAULTS)
    axes[spec.axis] = primitive_id.rsplit(".", 1)[-1]
    task = _family_task(spec, "mnist")

    assert compose_configs(
        coordinate=_coordinate(axes),
        geometry={},
        input_shape=MICRO_INPUT_SHAPE,
        output_dim=MICRO_OUTPUT_DIM,
    ), spec.id
    assert _declared_legal(axes, task) == IMPOSSIBLE[primitive_id], spec.id


def test_every_registered_row_is_measured_or_impossible() -> None:
    """Every spec has a case, or is a counted impossible row."""
    unaccounted = [
        spec.id
        for spec in list_primitives()
        if spec.id not in IMPOSSIBLE
        and not isinstance(make_case(spec, seed=0), PrimitiveCase)
    ]
    assert not unaccounted, unaccounted
