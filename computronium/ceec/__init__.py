"""Adapter: the standalone ceec-core package is the single source (Rule 6).

Legacy ``computronium.ceec`` import paths re-export from the ``ceec``
package (uv workspace member ``packages/ceec-core``).
"""

from __future__ import annotations

from ceec import *  # ruff: ignore[undefined-local-with-import-star]
from ceec import (
    audit as audit,
)
from ceec import (
    bootstrap as bootstrap,
)
from ceec import (
    calibration as calibration,
)
from ceec import (
    cli as cli,
)
from ceec import (
    gates as gates,
)
from ceec import (
    ids as ids,
)
from ceec import (
    migrate as migrate,
)
from ceec import (
    models as models,
)
from ceec import (
    probe_adapter as probe_adapter,
)
from ceec import (
    schemas as schemas,
)
from ceec import (
    selection as selection,
)
from ceec import (
    store as store,
)

from ceec import __all__ as _pkg_all

__all__ = list(_pkg_all)
