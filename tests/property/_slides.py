"""Loader for the slides builder (shared by the slides locks).

``docs/slides`` is a directory of prose, not a package, so the builder is
imported by path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

SNIPPETS = Path(__file__).resolve().parents[2] / "docs" / "slides"


def load_slides_builder() -> ModuleType:
    """Import ``docs/slides/build_slides.py`` as a module."""
    path = SNIPPETS / "build_slides.py"
    spec = importlib.util.spec_from_file_location("slides_builder", path)
    if spec is None or spec.loader is None:  # pragma: no cover - import plumbing
        msg = f"cannot import {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
