"""Adapter: the standalone ceec-core package is the single source (Rule 6).

Legacy ``computronium.ceec`` import paths re-export from the ``ceec``
package (uv workspace member ``packages/ceec-core``).
"""

from __future__ import annotations

from ceec.migrate import *  # ruff: ignore[undefined-local-with-import-star]
