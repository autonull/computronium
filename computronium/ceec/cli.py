"""Adapter: the standalone ceec-core package is the single source (Rule 6).

Legacy ``computronium.ceec`` import paths re-export from the ``ceec``
package (uv workspace member ``packages/ceec-core``).
"""

from __future__ import annotations

from ceec.cli import *  # ruff: ignore[undefined-local-with-import-star]
from ceec.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
