"""Loader for the site builder (shared by the site locks).

``docs/`` is a directory of prose and build scripts, not a package, so the
builder is imported by path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

SITE = Path(__file__).resolve().parents[2] / "docs"


def load_site_builder() -> ModuleType:
    """Import ``docs/build_site.py`` as a module."""
    path = SITE / "build_site.py"
    spec = importlib.util.spec_from_file_location("site_builder", path)
    if spec is None or spec.loader is None:  # pragma: no cover - import plumbing
        msg = f"cannot import {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
