"""Adapter: the standalone stability package is the single source (Rule 6).

Legacy ``computronium.stability`` import paths re-export from the
``stability`` package (uv workspace member ``packages/stability``). The
computronium-coupled PR-5 demo-harvest orchestration lives in
``computronium.stability.calibration`` (it drives the internal campaign
demo-suite coordinate builder); everything generic comes from the package.
"""

from __future__ import annotations

import stability as _stability
from stability import *  # ruff: ignore[undefined-local-with-import-star]
from stability import (  # ruff: ignore[unused-import]  # adapter re-exports
    OVERHEAD_BUDGET,
    PR5Calibration,
    calibrate_ginibre_harvest,
    calibrate_threshold,
    ginibre_run,
    harvest_bad_statistics,
    harvest_good_statistics,
    measure_guard_overhead,
    probe_interval_for_overhead,
    quantify_proxy_disagreement,
    unrolled_divergence,
)
from stability import (  # submodule binding for legacy paths
    basin as basin,
)
from stability import (
    calibration as calibration,
)
from stability import (
    config as config,
)
from stability import (
    frontier as frontier,
)
from stability import (
    guard as guard,
)
from stability import (
    lyapunov as lyapunov,
)
from stability import (
    matrices as matrices,
)
from stability import (
    resources as resources,
)
from stability import (
    settling as settling,
)
from stability import (
    spectral_radius as spectral_radius,
)

from computronium.stability.calibration import (
    DEMO_GOOD_COORDINATES,
    DISAGREEMENT_COORDINATES,
    calibrate_demo_harvest,
)

__version__ = _stability.__version__

__all__ = [  # ruff: ignore[invalid-all-object]
    *_stability.__all__,
    "DEMO_GOOD_COORDINATES",
    "DISAGREEMENT_COORDINATES",
    "calibrate_demo_harvest",
]
