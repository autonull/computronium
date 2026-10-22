"""Implementation Registry.

Register and discover implementations. Serves as the single source of truth
for implementation metadata and entrypoints.
"""

import importlib
import pkgutil
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.acceleration.spec import ImplementationSpec


def register_module(
    module_name: str,
    docstring: str,
    *,
    has_factory: bool = False,
    factory_name: str | None = None,
    kernel_fn: str = "step",
    reference_fn: str = "step",
) -> dict[str, object]:
    """Register a primitive/algorithm module and return its exports.

    This replaces the boilerplate in each module's __init__.py with a single call.

    Args:
        module_name: The module's __name__ (e.g., "computronium.algorithms.fa").
        docstring: The module's docstring.
        has_factory: Whether the module has a factory.py with a create_* function.
        factory_name: The name of the factory function to export (e.g., "create_fa_mlp").
            Required if has_factory is True.
        kernel_fn: The function name to import from kernel module (default: "step").
        reference_fn: The function name to import from reference module (default: "step").

    Returns:
        Dict of exports to update the module's globals with.
    """
    # Import submodules
    cases_mod = importlib.import_module(".cases", module_name)
    kernel_mod = importlib.import_module(".kernel", module_name)
    reference_mod = importlib.import_module(".reference", module_name)
    spec_mod = importlib.import_module(".spec", module_name)

    # Register the spec
    register(spec_mod.SPEC)

    # Build exports
    exports: dict[str, object] = {
        "SPEC": spec_mod.SPEC,
        "kernel_step": getattr(kernel_mod, kernel_fn),
        "make_case": cases_mod.make_case,
        "reference_step": getattr(reference_mod, reference_fn),
    }

    # Optionally export is_available from kernel module
    if hasattr(kernel_mod, "is_available"):
        exports["is_available"] = kernel_mod.is_available

    if has_factory:
        if factory_name is None:
            raise ValueError("factory_name required when has_factory=True")
        factory_mod = importlib.import_module(".factory", module_name)
        exports[factory_name] = getattr(factory_mod, factory_name)

    return exports


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
    global _DISCOVERED  # ruff: ignore[global-statement] - required for module-level cache
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


def list_by_axis() -> dict[str, list[str]]:
    """Get all registered primitive specifications grouped by axis.

    Returns:
        Dictionary mapping axis name to list of implementation IDs.
        Algorithms (which have axis=None) are grouped under "algorithm".
    """
    _discover()
    by_axis: dict[str, list[str]] = defaultdict(list)
    for spec in _REGISTRY.values():
        axis = spec.axis or "algorithm"
        by_axis[axis].append(spec.id)
    return dict(by_axis)
