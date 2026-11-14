"""Shared machinery for the per-axis primitive contracts (TODO91 S1d).

Each axis contract asserts the same properties of every registered spec on that
axis. This module resolves a spec to its case factory and entrypoint so a new
primitive is covered by registering it, not by copying a test triple.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
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


def case_class(spec: ImplementationSpec) -> type | None:
    """The ``Case`` type the spec's cases module declares, if it declares one."""
    module = import_module(f"{package(spec)}.cases")
    declared = getattr(module, "Case", None)
    return declared if isinstance(declared, type) else None


class RecordingConfig(dict):
    """A case config that remembers every key read from it."""

    read: set[str]

    def __init__(self, source: dict[str, Any], read: set[str]) -> None:
        super().__init__(source)
        self.read = read

    def __getitem__(self, key: str) -> Any:
        self.read.add(key)
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        self.read.add(key)
        return super().get(key, default)


def case_factories(spec: ImplementationSpec) -> tuple[str, ...]:
    """Every case factory the spec's cases module declares."""
    module = import_module(f"{package(spec)}.cases")
    return tuple(
        sorted(
            name
            for name in dir(module)
            if name.startswith("make_case") and callable(getattr(module, name))
        )
    )


def config_reads(spec: ImplementationSpec) -> frozenset[str]:
    """The ``case.config`` keys the spec's reference reads, statically and at run time.

    A case factory that omits a key its own reference knows about silently uses
    the reference's default: the drift the legacy per-package
    ``config_structure`` assertions guarded against. The read set is derived
    from the reference, so adding a knob to a law adds its key here.

    Two passes, because neither is complete alone: an AST pass sees branches a
    single seed does not take, and a recording-dict pass sees reads that a
    factory helper or a passed-in config factory performs (where the static
    scan cannot follow).
    """
    return _static_config_reads(spec) | _runtime_config_reads(spec)


def _literal_config_read(node: ast.AST, aliases: set[str]) -> str | None:
    """The literal key ``node`` reads from the case config, if it reads one."""
    match node:
        case ast.Subscript(
            value=ast.Attribute(value=ast.Name(id="case"), attr="config"),
            slice=ast.Constant(value=str() as key),
        ):
            return key
        case ast.Subscript(
            value=ast.Name(id=name), slice=ast.Constant(value=str() as key)
        ) if name in aliases - {"case.config"}:
            return key
        case ast.Call(
            func=ast.Attribute(value=ast.Name(id=name), attr="get"),
            args=[ast.Constant(value=str() as key), *_],
        ) if name in aliases - {"case.config"}:
            return key
        case ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(value=ast.Name(id="case"), attr="config"),
                attr="get",
            ),
            args=[ast.Constant(value=str() as key), *_],
        ):
            return key
    return None


def _static_config_reads(spec: ImplementationSpec) -> frozenset[str]:
    """Literal keys read from ``case.config`` or a local alias, by AST."""
    module = import_module(spec.reference_entrypoint.rpartition(".")[0])
    tree = ast.parse(inspect.getsource(module))

    def is_case_config(node: ast.expr) -> bool:
        return (
            isinstance(node, ast.Attribute)
            and node.attr == "config"
            and isinstance(node.value, ast.Name)
            and node.value.id == "case"
        )

    keys: set[str] = set()
    for function in ast.walk(tree):
        if not isinstance(function, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        aliases = {"case.config"}
        for node in ast.walk(function):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and is_case_config(node.value)
            ):
                aliases.add(node.targets[0].id)
        for node in ast.walk(function):
            key = _literal_config_read(node, aliases)
            if key is not None:
                keys.add(key)
    return frozenset(keys)


def _runtime_config_reads(spec: ImplementationSpec) -> frozenset[str]:
    """Keys read from the case config while the reference runs."""
    case = make_case(spec, seed=0)
    config = getattr(case, "config", None)
    if not isinstance(config, dict):
        return frozenset()
    read: set[str] = set()
    instrumented = dataclasses.replace(case, config=RecordingConfig(config, read))
    reference(spec, instrumented)
    return frozenset(read)


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
