"""One contract for every primitive spec (TODO91 S1d).

Each primitive ships a ``cases`` module, a reference entrypoint, and a kernel
entrypoint, and every spec declares the tolerance the two must agree within.
The contract is therefore the same for all of them: it is written once here and
parameterized by spec, so a new primitive is covered by registering it.

This module replaces the per-package ``test_<name>_{cases,reference,kernel_parity,
structural}.py`` triples. Per-axis invariants that do not generalize — the
reference's output shape, a case's private config keys — stay with the axis
harness or the S2/S6 smoke; what generalizes lives here:

* a case is seeded, reproducible, and seed-sensitive in its config;
* the reference is deterministic, has a seed-stable output structure, and (on
  a geometry) changes when the seed changes;
* the kernel agrees with the reference at two seeds;
* a substrate spec survives the config → spec → config projection.
"""

from __future__ import annotations

import dataclasses
from importlib import import_module
from typing import Any

import pytest
import torch

from computronium.acceleration.parity import assert_parity, digest
from computronium.acceleration.registry import all_specs

#: Reference entrypoints whose callable takes the case's own spec.
_TAKES_SPEC = frozenset({"make_substrate"})

SPECS = tuple(
    sorted(
        (spec for spec in all_specs() if spec.kind == "primitive"),
        key=lambda spec: spec.id,
    )
)
IDS = [spec.id for spec in SPECS]


def _module_of(entrypoint: str) -> str:
    return entrypoint.rpartition(".")[0]


def _call(entrypoint: str, case: Any) -> Any:
    module_path, _, function_name = entrypoint.rpartition(".")
    function = getattr(import_module(module_path), function_name)
    return function(case.spec) if function_name in _TAKES_SPEC else function(case)


def _case(spec: Any, seed: int) -> Any:
    cases = import_module(
        f"{_module_of(spec.reference_entrypoint).rpartition('.')[0]}.cases"
    )
    return cases.make_case(seed=seed, device="cpu")


def _run(spec: Any, entrypoint: str, seed: int) -> Any:
    return _call(entrypoint, _case(spec, seed))


def _schema(value: Any) -> Any:
    """Output structure: types, tensor shapes/dtypes, and container keys."""
    if isinstance(value, torch.Tensor):
        return ("tensor", tuple(value.shape), value.dtype)
    if isinstance(value, dict):
        return ("dict", tuple((key, _schema(item)) for key, item in value.items()))
    if isinstance(value, list | tuple):
        return (type(value).__name__, tuple(_schema(item) for item in value))
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return (
            type(value).__name__,
            tuple(
                (field.name, _schema(getattr(value, field.name)))
                for field in dataclasses.fields(value)
            ),
        )
    if hasattr(value, "__dict__") and not isinstance(value, type):
        return (
            type(value).__name__,
            tuple(
                (key, _schema(item))
                for key, item in sorted(vars(value).items())
                if not key.startswith("_")
            ),
        )
    return type(value).__name__


def test_every_primitive_declares_a_kernel_entrypoint() -> None:
    """A spec with a kernel backend must name the kernel rung's entrypoint."""
    missing = [
        spec.id
        for spec in SPECS
        if "kernel" in spec.supported_backends and not spec.kernel_entrypoint
    ]
    assert not missing, missing


def test_an_explicit_axis_declaration_is_explained() -> None:
    """A spec that overrides its axis's batch or seed rule states why."""
    unexplained = [
        spec.id
        for spec in SPECS
        if (spec.batch_axis is not None and not spec.batch_axis_reason)
        or (spec.seed_sensitive is not None and not spec.seed_free_reason)
    ]
    assert not unexplained, unexplained


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_case_is_seeded_and_reproducible(spec) -> None:
    """A case reproduces under one seed and moves under another."""
    first = _case(spec, 7)
    second = _case(spec, 7)
    other = _case(spec, 8)

    assert isinstance(first.config, dict), spec.id
    assert digest(first) == digest(second), spec.id
    assert digest(first) != digest(other), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_reference_output_structure_is_seed_stable(spec) -> None:
    """The reference emits the same output structure at a different seed."""
    assert _schema(_run(spec, spec.reference_entrypoint, 0)) == _schema(
        _run(spec, spec.reference_entrypoint, 1)
    ), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_reference_is_deterministic(spec) -> None:
    """Two reference calls on one seed produce the same output."""
    first = _run(spec, spec.reference_entrypoint, 3)
    second = _run(spec, spec.reference_entrypoint, 3)
    assert digest(first) == digest(second), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_kernel_matches_reference(spec) -> None:
    """The kernel rung agrees with the reference within the spec's tolerance.

    A substrate factory returns an object rather than tensors, so its parity is
    structural: the same configuration, digested.
    """
    assert spec.kernel_entrypoint is not None, spec.id
    reference = _run(spec, spec.reference_entrypoint, seed=0)
    kernel = _run(spec, spec.kernel_entrypoint, seed=0)
    if isinstance(reference, torch.Tensor | dict | list | tuple):
        assert_parity(reference, kernel, spec.parity)
    else:
        assert digest(reference) == digest(kernel), spec.id


@pytest.mark.parametrize("spec", SPECS, ids=IDS)
def test_kernel_matches_reference_at_a_second_seed(spec) -> None:
    """Parity is not a coincidence of one seeded case."""
    assert spec.kernel_entrypoint is not None, spec.id
    reference = _run(spec, spec.reference_entrypoint, seed=1)
    kernel = _run(spec, spec.kernel_entrypoint, seed=1)
    if isinstance(reference, torch.Tensor | dict | list | tuple):
        assert_parity(reference, kernel, spec.parity)
    else:
        assert digest(reference) == digest(kernel), spec.id


GEOMETRIES = tuple(spec for spec in SPECS if spec.axis == "geometry")
SUBSTRATES = tuple(spec for spec in SPECS if spec.axis == "substrate")
DYNAMICS = tuple(spec for spec in SPECS if spec.axis == "state_dynamics")
CREDITS = tuple(spec for spec in SPECS if spec.axis == "credit_assignment")
PLASTICITIES = tuple(spec for spec in SPECS if spec.axis == "plasticity")
UPDATES = tuple(spec for spec in SPECS if spec.axis == "parameter_update")
SEED_VARYING = tuple(spec for spec in SPECS if spec.varies_with_seed)


def _ids(specs: tuple[Any, ...]) -> list[str]:
    return [spec.id for spec in specs]


@pytest.mark.parametrize("spec", SEED_VARYING, ids=_ids(SEED_VARYING))
def test_reference_varies_with_seed(spec) -> None:
    """A seed-varying reference cannot be seed-blind."""
    first = _run(spec, spec.reference_entrypoint, seed=0)
    second = _run(spec, spec.reference_entrypoint, seed=1)
    assert digest(first) != digest(second), spec.id


@pytest.mark.parametrize("spec", DYNAMICS, ids=_ids(DYNAMICS))
def test_dynamics_step_returns_a_composite_state(spec) -> None:
    """Every dynamics step settles the case state, not an unrelated shape."""
    from computronium.state import CompositeState

    case = _case(spec, 0)
    state = _run(spec, spec.reference_entrypoint, seed=0)
    assert isinstance(state, CompositeState), spec.id
    assert state.x is not None and state.x.shape == case.state.shape, spec.id
    activations = state.activations
    assert isinstance(activations, list) and activations, spec.id
    assert activations[0].shape == case.state.shape, spec.id


@pytest.mark.parametrize("spec", UPDATES, ids=_ids(UPDATES))
def test_update_step_covers_the_harness_parameters(spec) -> None:
    """An update returns one updated tensor per harness parameter."""
    from computronium.harness import update_geometry

    case = _case(spec, 0)
    expected = update_geometry(case).params
    updated = _run(spec, spec.reference_entrypoint, seed=0)
    assert isinstance(updated, dict), spec.id
    assert set(updated) == set(expected), spec.id
    for name, tensor in updated.items():
        assert torch.is_tensor(tensor), (spec.id, name)
        assert tensor.shape == expected[name].shape, (spec.id, name)


@pytest.mark.parametrize("spec", CREDITS, ids=_ids(CREDITS))
def test_credit_step_returns_one_gradient_per_parameter(spec) -> None:
    """A credit returns tensors shaped like the geometry's parameters."""
    case = _case(spec, 0)
    grads = _run(spec, spec.reference_entrypoint, seed=0)
    assert isinstance(grads, list) and grads, spec.id
    assert all(torch.is_tensor(grad) for grad in grads), spec.id
    geometry = getattr(case, "geometry", None)
    if geometry is None:
        return
    parameter_shapes = {tuple(param.shape) for param in geometry.params.values()}
    assert {tuple(grad.shape) for grad in grads} <= parameter_shapes, spec.id


@pytest.mark.parametrize("spec", PLASTICITIES, ids=_ids(PLASTICITIES))
def test_plasticity_step_returns_named_tensors(spec) -> None:
    """A plasticity step returns a tensor per plastic variable it changes."""
    case = _case(spec, 0)
    updated = _run(spec, spec.reference_entrypoint, seed=0)
    assert isinstance(updated, dict), spec.id
    assert all(torch.is_tensor(value) for value in updated.values()), spec.id
    plastic = getattr(case, "psi", None)
    if plastic:
        assert set(updated) == set(plastic), spec.id
        for name, tensor in updated.items():
            assert tensor.shape == plastic[name].shape, (spec.id, name)


@pytest.mark.parametrize("spec", SUBSTRATES, ids=[s.id for s in SUBSTRATES])
def test_substrate_spec_survives_the_config_projection(spec) -> None:
    """config → spec → config is lossless for every substrate family."""
    from computronium.ontology.substrate.spec import SubstrateSpec

    config = _case(spec, 0).spec.to_config()
    assert SubstrateSpec.from_config(config).to_config() == config, spec.id
