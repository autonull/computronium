"""Loader for the README builder (shared by the README locks).

``docs/readme`` is a directory of prose, not a package, so the builder is
imported by path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

SNIPPETS = Path(__file__).resolve().parents[2] / "docs" / "readme"


def load_readme_builder() -> ModuleType:
    """Import ``docs/readme/build_readme.py`` as a module."""
    path = SNIPPETS / "build_readme.py"
    spec = importlib.util.spec_from_file_location("readme_builder", path)
    if spec is None or spec.loader is None:  # pragma: no cover - import plumbing
        msg = f"cannot import {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
