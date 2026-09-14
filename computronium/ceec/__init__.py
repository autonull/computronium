"""Adapter: the standalone ceec-core package is the single source (Rule 6).

Legacy ``computronium.ceec`` import paths re-export from the ``ceec``
package (uv workspace member ``packages/ceec-core``).
"""

from __future__ import annotations

import warnings

warnings.warn(  # noqa: RUF067  deprecation shim: non-re-export by design
    "computronium.ceec is deprecated; import `ceec` directly (TODO26 T26.G.3)",
    DeprecationWarning,
    stacklevel=2,
)

from ceec import *  # noqa: E402, F403
from ceec import __all__ as _pkg_all  # noqa: E402
from ceec import (  # noqa: E402
    audit as audit,
)
from ceec import (  # noqa: E402
    bootstrap as bootstrap,
)
from ceec import (  # noqa: E402
    calibration as calibration,
)
from ceec import (  # noqa: E402
    cli as cli,
)
from ceec import (  # noqa: E402
    gates as gates,
)
from ceec import (  # noqa: E402
    ids as ids,
)
from ceec import (  # noqa: E402
    migrate as migrate,
)
from ceec import (  # noqa: E402
    models as models,
)
from ceec import (  # noqa: E402
    probe_adapter as probe_adapter,
)
from ceec import (  # noqa: E402
    profile as profile,
)
from ceec import (  # noqa: E402
    report as report,
)
from ceec import (  # noqa: E402
    run as run,
)
from ceec import (  # noqa: E402
    schemas as schemas,
)
from ceec import (  # noqa: E402
    selection as selection,
)
from ceec import (  # noqa: E402
    session as session,
)
from ceec import (  # noqa: E402
    store as store,
)

__all__ = list(_pkg_all)
