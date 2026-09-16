"""Adapter: the standalone ceec-core package is the single source (Rule 6).

Legacy ``computronium.ceec`` import paths re-export from the ``ceec``
package (uv workspace member ``packages/ceec-core``).
"""

from __future__ import annotations

import warnings

warnings.warn(  # ruff: ignore[non-empty-init-module]  deprecation shim: non-re-export by design
    "computronium.ceec is deprecated; import `ceec` directly (TODO26 T26.G.3)",
    DeprecationWarning,
    stacklevel=2,
)

from ceec import *  # ruff: ignore[module-import-not-at-top-of-file, undefined-local-with-import-star]
from ceec import __all__ as _pkg_all  # ruff: ignore[module-import-not-at-top-of-file]
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    audit as audit,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    bootstrap as bootstrap,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    calibration as calibration,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    cli as cli,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    gates as gates,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    ids as ids,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    migrate as migrate,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    models as models,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    probe_adapter as probe_adapter,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    profile as profile,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    report as report,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    run as run,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    schemas as schemas,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    selection as selection,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    session as session,
)
from ceec import (  # ruff: ignore[module-import-not-at-top-of-file]
    store as store,
)

__all__ = list(_pkg_all)
