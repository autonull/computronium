"""Computronium CLI Tools.

Lazy (Sprint 0.5): this package previously eagerly imported ``cli.__main__``
via a chain of legacy pillar imports. With lazy top-level imports that
pre-warming is gone, so the console scripts now expose their entry points
on demand instead.
"""

_LAZY: dict[str, tuple[str, str | None]] = {  # ruff: ignore[non-empty-init-module]
    "main": ("computronium.cli.__main__", "main"),
}

__all__ = sorted(_LAZY)  # ruff: ignore[invalid-all-format]


def __getattr__(name: str) -> object:
    if name not in _LAZY:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr = _LAZY[name]
    module = __import__(module_name, fromlist=[attr] if attr else ["*"])
    value: object = module if attr is None else getattr(module, attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(__all__)
