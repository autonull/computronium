"""Adapter: the standalone stability package is the single source (Rule 6).

Legacy ``computronium.resources`` import paths re-export from
``stability.resources`` (uv workspace member ``packages/stability``).
"""

from __future__ import annotations

from stability.resources import MAC_ENERGY_J, ResourceUsage

__all__ = ["MAC_ENERGY_J", "ResourceUsage"]
