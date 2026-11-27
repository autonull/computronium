"""Lock the lazy packages' declared surface to what actually binds it.

Each experiment package publishes an ``__all__`` built from a lazy map, so a
name can outlive the module that defines it: ``PipelineConfig`` stayed in
``__all__`` after ``pipeline.py`` became a package, and ``ShapeResolver``
outlived a rename. Nothing imported the name, so nothing noticed.

:func:`computronium._surface.bound_names` reads the file a name would be
defined in without importing it, so this check stays static (no torch, no
FastAPI) and reports the name and the target it fails to reach.
"""

from __future__ import annotations

import importlib

import pytest

from computronium._surface import bound_names, module_path

_LAZY_PACKAGES = (
    "computronium.experiment",
    "computronium.experiment.execution",
    "computronium.experiment.evidence",
    "computronium.experiment.schema",
    "computronium.experiment.surface",
)

#: Packages whose lazy map names a module with this prefix resolve it under
#: ``computronium.experiment`` instead (the kernel modules the execution
#: package moved out).
_KERNEL_PREFIX = "kernel."


def _target(package: str, mapped: str) -> str:
    if package == "computronium.experiment.execution" and mapped.startswith(
        _KERNEL_PREFIX
    ):
        return f"computronium.experiment.{mapped}"
    return f"{package}.{mapped}"


@pytest.mark.parametrize("package", _LAZY_PACKAGES)
def test_every_declared_name_resolves(package: str) -> None:
    module = importlib.import_module(package)
    lazy: dict[str, str] = getattr(module, "_symbol_to_module", {})

    unresolved: list[str] = []
    for name in module.__all__:
        if module_path(f"{package}.{name}") is not None:
            continue
        mapped = lazy.get(name)
        if mapped is None:
            unresolved.append(f"{name}: neither a submodule nor in the lazy map")
            continue
        target = _target(package, mapped)
        path = module_path(target)
        if path is None:
            unresolved.append(f"{name}: {target} is not a module")
        elif name not in bound_names(path):
            unresolved.append(f"{name}: {target} does not bind it")

    assert not unresolved, f"{package} declares names it cannot resolve:\n" + "\n".join(
        unresolved
    )


@pytest.mark.parametrize("package", _LAZY_PACKAGES)
def test_the_lazy_map_does_not_carry_undeclared_names(package: str) -> None:
    module = importlib.import_module(package)
    lazy: dict[str, str] = getattr(module, "_symbol_to_module", {})

    undeclared = sorted(set(lazy) - set(module.__all__))

    assert not undeclared, f"{package} imports names it does not declare: {undeclared}"


def test_the_dashboard_package_exports_what_its_web_module_binds() -> None:
    """The package's only module is the web dashboard, loaded lazily on access."""
    package = importlib.import_module("computronium.experiment.execution.dashboard")
    web = module_path("computronium.experiment.execution.dashboard.web")
    assert web is not None

    missing = sorted(name for name in package.__all__ if name not in bound_names(web))

    assert not missing, f"the dashboard declares names web.py does not bind: {missing}"
