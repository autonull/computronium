"""Live Monitoring Dashboard (Phase E5).

Provides web-based and TUI dashboards for monitoring campaign execution.

The web dashboard imports FastAPI, so it is loaded on first access: the
package's ``__all__`` names must exist without paying that import.
"""

from __future__ import annotations

_LAZY: dict[str, tuple[str, str]] = {
    "DashboardConfig": (
        "computronium.experiment.execution.dashboard.web",
        "DashboardConfig",
    ),
    "WebDashboard": (
        "computronium.experiment.execution.dashboard.web",
        "WebDashboard",
    ),
    "create_dashboard": (
        "computronium.experiment.execution.dashboard.web",
        "create_dashboard",
    ),
}

# `_LAZY` is the only source of the names, and pyright cannot read a computed
# `__all__`; a literal copy would let the two drift apart.
__all__ = sorted(_LAZY)  # ruff: ignore[invalid-all-format]  # pyright: ignore[reportUnsupportedDunderAll]


def __getattr__(name: str) -> object:
    if name not in _LAZY:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute = _LAZY[name]
    module = __import__(module_name, fromlist=[attribute])
    value = getattr(module, attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
