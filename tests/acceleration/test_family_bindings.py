"""The binding layer has one table and one stated call site (TODO36 §4.3).

Before this, ``KernelRegistry`` held one family after ``import computronium``
and two after ``all_specs()`` — because asking the *other* layer a question
imported a kernel module that registered itself. These tests pin the properties
that make that impossible.
"""

import ast
import pathlib

import pytest

from computronium.acceleration import get_algorithm_kernels, register_all
from computronium.acceleration.families import BINDINGS as TABLE
from computronium.acceleration.kernel_backend import AlgorithmFamily, KernelRegistry

ACCELERATION = pathlib.Path("computronium/acceleration")


def test_importing_the_package_binds_every_family() -> None:
    assert set(KernelRegistry._backends) == {b.family for b in TABLE}


def test_registry_is_not_an_import_order_artifact() -> None:
    """Querying Layer A must not change Layer B's contents."""
    before = {f: set(v) for f, v in KernelRegistry._backends.items()}
    from computronium.acceleration.registry import all_specs

    all_specs()
    assert {f: set(v) for f, v in KernelRegistry._backends.items()} == before


def test_registration_is_idempotent() -> None:
    assert register_all() == TABLE
    assert set(KernelRegistry._backends) == {b.family for b in TABLE}


def test_one_binding_per_family() -> None:
    families = [b.family for b in TABLE]
    assert len(families) == len(set(families)), "a second row would displace the first"


def test_every_binding_resolves_to_its_named_class() -> None:
    import importlib

    for binding in TABLE:
        cls = getattr(importlib.import_module(binding.module), binding.backend)
        assert cls.__name__ == binding.backend
        for hardware in KernelRegistry._backends[binding.family]:
            assert KernelRegistry.get(binding.family, hardware) is not None


def test_get_algorithm_kernels_is_the_same_table() -> None:
    assert set(get_algorithm_kernels()) == {b.family.value for b in TABLE}


def _module_level_calls(tree: ast.Module) -> list[ast.Call]:
    """Calls executed when the module is imported, in any top-level block."""
    found: list[ast.Call] = []
    stack: list[ast.AST] = list(tree.body)
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.Call):
            found.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return found


def test_no_kernel_module_registers_on_import() -> None:
    """The census: registration happens in `families.register_all`, nowhere else."""
    offenders = [
        f"{path.name}:{node.lineno}"
        for path in sorted(ACCELERATION.glob("*.py"))
        if path.name != "families.py"
        for node in _module_level_calls(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "register"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "KernelRegistry"
    ]
    assert offenders == []


def test_contrastive_kernels_register_under_distinct_keys() -> None:
    """Contrastive kernels now have distinct family keys and coexist with standard backends."""
    from computronium.acceleration.contrastive_kernels import (
        get_contrastive_kernel,
    )

    # Standard families should resolve to standard backends, not contrastive kernels
    standard_families = {
        AlgorithmFamily.FA,
        AlgorithmFamily.HEBBIAN,
        AlgorithmFamily.FF,
        AlgorithmFamily.PEPITA,
        AlgorithmFamily.TP,
        AlgorithmFamily.PC,
        AlgorithmFamily.SNN,
        AlgorithmFamily.TILE,
        AlgorithmFamily.MEP,
        AlgorithmFamily.O1MEMORY,
    }
    for family in standard_families:
        if family not in KernelRegistry._backends:
            continue
        backend = KernelRegistry.get(family, next(iter(KernelRegistry._backends[family])))
        assert not backend.__class__.__name__.endswith("ContrastiveKernel"), (
            f"{family} resolves to a contrastive kernel by default"
        )

    # Contrastive families should resolve to contrastive kernels
    contrastive_families = {
        AlgorithmFamily.FA_CONTRASTIVE,
        AlgorithmFamily.HEBBIAN_CONTRASTIVE,
        AlgorithmFamily.FF_CONTRASTIVE,
        AlgorithmFamily.PEPITA_CONTRASTIVE,
        AlgorithmFamily.TP_CONTRASTIVE,
        AlgorithmFamily.PC_CONTRASTIVE,
        AlgorithmFamily.SNN_CONTRASTIVE,
        AlgorithmFamily.TILE_CONTRASTIVE,
        AlgorithmFamily.MEP_CONTRASTIVE,
        AlgorithmFamily.O1MEMORY_CONTRASTIVE,
    }
    for family in contrastive_families:
        if family not in KernelRegistry._backends:
            continue
        backend = KernelRegistry.get(family, next(iter(KernelRegistry._backends[family])))
        assert backend.__class__.__name__.endswith("ContrastiveKernel"), (
            f"{family} does not resolve to a contrastive kernel"
        )

    # Helper function still works for standard families (for backwards compat)
    assert get_contrastive_kernel(AlgorithmFamily.FA) is not None


def test_exports_the_binding_symbols() -> None:
    import computronium.acceleration as accel

    assert {"BINDINGS", "register_all"} <= set(accel.__all__)
