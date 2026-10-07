"""The lazy re-export surface is code, so it is locked like code.

Five experiment-kernel packages resolve their ``__all__`` through a
module-level ``__getattr__`` backed by a hand-maintained
``_symbol_to_module`` map, which is what keeps ``import
computronium.experiment`` off the torch/ontology path (~40ms instead of
~3.5s). A map is a wiring table, and a wiring table drifts: TODO52 batch 5
added ``EvolutionPolicy`` to a test's imports and forgot it in the map, and
``schema.__all__`` carried ``harvest_weights`` and ``schema_version``, which
resolve to nothing at all — an ``ImportError`` on the path that takes them.

So this asserts three directions, because a wiring table has three ways to be
wrong:

* every ``__all__`` name resolves through the package (nothing advertised and
  absent);
* every map entry names a symbol its target submodule actually defines (no
  entry pointing at nothing);
* every submodule the package lists is importable (no ``__all__`` naming a
  module that is not there).

The map is populated, not derived, so this cannot be satisfied by regenerating
anything: it fails until a human adds the row.
"""

from __future__ import annotations

import ast
import importlib
import pathlib
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

#: Package -> its own submodule names, which ``__all__`` may list directly
#: (the submodule branch of ``__getattr__``) rather than through the map.
LAZY_PACKAGES: dict[str, tuple[str, ...]] = {
    "computronium.experiment": ("evidence", "execution", "schema", "surface"),
    "computronium.experiment.schema": (
        "axis",
        "coordinate",
        "harvest",
        "metrics",
        "record",
        "registries",
        "registry",
        "run_spec",
        "seed_registries",
        "versioning",
    ),
    "computronium.experiment.evidence": (
        "artifacts",
        "claims",
        "failure",
        "limitations",
        "procedures",
        "protocol",
        "significance",
        "statistics",
        "status",
        "store",
    ),
    "computronium.experiment.execution": (
        "allocator",
        "backends",
        "budget",
        "compose",
        "decision",
        "optuna_adapter",
        "pipeline",
        "policy",
        "pricing",
        "replay",
        "search_space",
        "settle_operator",
        "stage",
        "stages_impl",
        "sysctx",
    ),
    "computronium.experiment.surface": (
        "cli",
        "codegen",
        "conformance",
        "evidence",
        "operations",
        "profiles",
        "report",
        "service",
    ),
}


def _package(name: str) -> ModuleType:
    return importlib.import_module(name)


def _resolve(package: str, target: str) -> ModuleType:
    """The submodule a map entry or submodule name points at."""
    return importlib.import_module(f"{package}.{target}")


def _duplicate_keys(source: str | None) -> list[str]:
    """Keys written more than once in the package's ``_symbol_to_module`` literal.

    Parsed, not imported: the runtime dict is a strict function of its source, so
    it cannot report which row was the redundant one.
    """
    assert source is not None
    tree = ast.parse(pathlib.Path(source).read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.AnnAssign):
            continue
        if getattr(node.target, "id", "") != "_symbol_to_module":
            continue
        assert isinstance(node.value, ast.Dict)
        constants = [k for k in node.value.keys if isinstance(k, ast.Constant)]
        keys: list[str] = [str(k.value) for k in constants]
        return sorted(k for k in set(keys) if keys.count(k) > 1)
    raise AssertionError(f"{source} declares no _symbol_to_module literal")


@pytest.mark.parametrize("package", sorted(LAZY_PACKAGES))
def test_every_advertised_name_resolves(package: str) -> None:
    module = _package(package)
    unresolvable = []
    for name in module.__all__:
        try:
            getattr(module, name)
        except AttributeError:
            unresolvable.append(name)
    assert unresolvable == [], (
        f"{package}.__all__ advertises {unresolvable}, which its __getattr__ "
        "cannot resolve — an ImportError for anything that imports them"
    )


@pytest.mark.parametrize("package", sorted(LAZY_PACKAGES))
def test_every_map_entry_names_a_symbol_its_submodule_defines(package: str) -> None:
    module = _package(package)
    dead = [
        f"{name} -> {target}"
        for name, target in sorted(module._symbol_to_module.items())
        if not hasattr(_resolve(package, target), name)
    ]
    assert dead == [], (
        f"{package}._symbol_to_module entries that resolve to nothing: {dead}"
    )


@pytest.mark.parametrize("package", sorted(LAZY_PACKAGES))
def test_submodules_are_listed_and_importable(package: str) -> None:
    """The submodule branch of ``__getattr__`` names real modules.

    Not derived from the filesystem: a submodule that exists but was never
    listed is reachable by ``from pkg.sub import ...`` while ``pkg.sub`` fails
    the surface lock, which is the drift this catches.
    """
    module = _package(package)
    listed = set(LAZY_PACKAGES[package])
    missing = sorted(name for name in listed if name not in module.__all__)
    assert missing == [], f"{package}.__all__ omits submodules {missing}"
    unimportable = []
    for name in sorted(listed):
        try:
            _resolve(package, name)
        except ImportError:
            unimportable.append(name)
    assert unimportable == [], f"{package}.__all__ lists {unimportable}, not modules"


@pytest.mark.parametrize("package", sorted(LAZY_PACKAGES))
def test_the_map_holds_no_dead_rows(package: str) -> None:
    """Nothing is mapped that the package does not advertise.

    A map row for a name absent from ``__all__`` is unreachable through the
    documented surface, so it is dead weight that reads as coverage.
    """
    module = _package(package)
    dead = sorted(set(module._symbol_to_module) - set(module.__all__))
    assert dead == [], f"{package} maps {dead}, which __all__ does not advertise"


@pytest.mark.parametrize("package", sorted(LAZY_PACKAGES))
def test_the_map_has_no_duplicate_keys(package: str) -> None:
    """A repeated key is a row silently overridden by a later one.

    Read off the source rather than the imported dict, because the dict has
    already collapsed the duplicate: ``schema`` mapped ``PRIORS`` to both
    ``registries`` (wrong — the list lives in ``seed_registries``) and
    ``seed_registries``, and only the AST shows the wrong row was ever written.
    """
    module = _package(package)
    duplicate = _duplicate_keys(module.__file__)
    assert duplicate == [], (
        f"{package}._symbol_to_module repeats {duplicate}; the later row wins "
        "and the earlier one is unreachable — keep the one that resolves"
    )
