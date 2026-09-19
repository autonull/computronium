"""Implementation Registry.

Register and discover implementations. Serves as the single source of truth
for implementation metadata and entrypoints.
"""

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.acceleration.spec import ImplementationSpec

_REGISTRY: dict[str, ImplementationSpec] = {}
_DISCOVERED: bool = False


def register(spec: ImplementationSpec) -> None:
    """Register an implementation specification."""
    if spec.id in _REGISTRY:
        # Allow re-registration of the same spec (e.g., during test discovery)
        existing = _REGISTRY[spec.id]
        if existing is not spec:
            raise ValueError(
                f"implementation already registered with different spec: {spec.id}"
            )
        return
    _REGISTRY[spec.id] = spec


def _try_import_module(module_name: str) -> object | None:
    """Try to import a module, returning None on failure."""
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None


def _discover_package(package_name: str) -> None:
    """Discover and register implementations from a single package."""
    package = _try_import_module(package_name)
    if package is None:
        return

    # package is a module with __path__ and __name__ attributes
    package_path = getattr(package, "__path__", None)
    package_name_attr = getattr(package, "__name__", None)
    if package_path is None or package_name_attr is None:
        return

    for _, module_name, _ in pkgutil.walk_packages(
        package_path, package_name_attr + "."
    ):
        module = _try_import_module(module_name)
        if module is not None and hasattr(module, "SPEC"):
            register(module.SPEC)  # type: ignore[attr-defined]


def _discover() -> None:
    """Discover and register implementations from primitives/ and algorithms/ packages."""
    global _DISCOVERED  # ruff: ignore[global-statement]
    if _DISCOVERED:
        return

    _discover_package("computronium.primitives")
    _discover_package("computronium.algorithms")

    _DISCOVERED = True


def get(implementation_id: str) -> ImplementationSpec:
    """Get an implementation specification by ID."""
    _discover()
    return _REGISTRY[implementation_id]


def all_specs() -> tuple[ImplementationSpec, ...]:
    """Get all registered implementation specifications."""
    _discover()
    return tuple(_REGISTRY.values())


def primitives() -> tuple[ImplementationSpec, ...]:
    """Get all registered primitive specifications."""
    _discover()
    return tuple(spec for spec in _REGISTRY.values() if spec.kind == "primitive")


def algorithms() -> tuple[ImplementationSpec, ...]:
    """Get all registered algorithm specifications."""
    _discover()
    return tuple(spec for spec in _REGISTRY.values() if spec.kind == "algorithm")
