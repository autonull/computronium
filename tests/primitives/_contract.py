"""Shared machinery for the per-axis primitive contracts (TODO91 S1d).

Each axis contract asserts the same properties of every registered spec on that
axis. This module resolves a spec to its case factory and entrypoint so a new
primitive is covered by registering it, not by copying a test triple.
"""

from __future__ import annotations

import dataclasses
from importlib import import_module
from typing import TYPE_CHECKING, Any

import torch

from computronium.acceleration.registry import all_specs

if TYPE_CHECKING:
    from computronium.acceleration.spec import ImplementationSpec

#: Reference entrypoints whose callable takes the case's own spec.
_TAKES_SPEC = frozenset({"make_substrate"})


def axis_specs(axis: str) -> tuple[ImplementationSpec, ...]:
    """Every primitive spec on ``axis``, sorted by ID."""
    return tuple(
        sorted(
            (
                spec
                for spec in all_specs()
                if spec.kind == "primitive" and spec.axis == axis
            ),
            key=lambda spec: spec.id,
        )
    )


def package(spec: ImplementationSpec) -> str:
    """The primitive package of ``spec`` (the reference module's parent)."""
    return spec.reference_entrypoint.rpartition(".")[0].rpartition(".")[0]


def make_case(spec: ImplementationSpec, **kwargs: Any) -> Any:
    """Build a case from the spec's own cases module."""
    return import_module(f"{package(spec)}.cases").make_case(**kwargs)


def call(spec: ImplementationSpec, entrypoint: str, case: Any) -> Any:
    """Call ``entrypoint`` with ``case`` (or its spec for a substrate factory)."""
    module_path, _, function_name = entrypoint.rpartition(".")
    function = getattr(import_module(module_path), function_name)
    return function(case.spec) if function_name in _TAKES_SPEC else function(case)


def reference(spec: ImplementationSpec, case: Any) -> Any:
    """Run the spec's reference entrypoint on ``case``."""
    return call(spec, spec.reference_entrypoint, case)


def payload(case: Any) -> dict[str, Any]:
    """The case's seed-derived structure, with its config excluded.

    Config carries the seed itself, so including it would make any two seeds
    differ trivially; the payload is what a case factory must actually vary.
    """
    if dataclasses.is_dataclass(case) and not isinstance(case, type):
        fields = {
            field.name: getattr(case, field.name)
            for field in dataclasses.fields(case)
            if field.name != "config"
        }
    else:
        fields = {key: value for key, value in vars(case).items() if key != "config"}
    return fields


def tensors(value: Any) -> list[torch.Tensor]:
    """Every tensor nested in ``value``, in traversal order."""
    match value:
        case torch.Tensor():
            return [value]
        case torch.nn.Module():
            return [*value.parameters(), *value.buffers()]
        case dict():
            return [tensor for item in value.values() for tensor in tensors(item)]
        case list() | tuple():
            return [tensor for item in value for tensor in tensors(item)]
        case _ if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return [
                tensor
                for field in dataclasses.fields(value)
                for tensor in tensors(getattr(value, field.name))
            ]
        case _:
            return []


def tensor_vector(value: Any) -> torch.Tensor:
    """Every tensor in ``value`` flattened and concatenated, in traversal order.

    ``digest`` summarizes a tensor by its sum, which cannot see a permutation:
    two one-hot states with the same number of ones digest identically. A seed
    check needs order, so this returns the values themselves.
    """
    parts = [tensor.detach().reshape(-1).float() for tensor in tensors(value)]
    return torch.cat(parts) if parts else torch.empty(0)
