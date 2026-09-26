"""TODO35 §10.3: is the demo suite's float output a function of the seed?

§10.3 recorded that `d16` emitted under the tiered runner's `-n 4` differed
from a single-process emit of the same commit on 15 of 36 arms, and could
not say which run was right. This probe narrows the question to what a
cheap experiment can answer: is one seeded CPU arm's accuracy *stable*
within a process and across processes, and does the answer depend on the
OpenMP thread count?

Regime (2026-09-26, RTX 3080 host, 16 cores, torch 2.x CPU/MKL):

    OMP=8, same process, 2 calls   -> see `within`
    OMP=8, 2 processes             -> see `across8`
    OMP=1, 2 processes             -> see `across1`

Run: `uv run python scripts/probes/todo35_d16_determinism.py`
"""

from __future__ import annotations

import importlib.util
import os
import subprocess  # ruff: ignore[suspicious-subprocess-import]
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "tests" / "integration" / "test_demo_uaxis_coverage.py"


def _load_d16():
    spec = importlib.util.spec_from_file_location("d16", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _one_arm(credit: str, update: str, geometry_name: str) -> float:
    d16 = _load_d16()
    return d16._run(credit, update, d16._geometries()[geometry_name], 0)


if __name__ == "__main__":
    import torch

    threads = int(os.environ.get("OMP_NUM_THREADS", "0")) or torch.get_num_threads()
    credit, update, geometry = sys.argv[1:4]
    if os.environ.get("CHILD"):
        print(f"{_one_arm(credit, update, geometry):.17g}")
        sys.exit(0)

    print(f"torch threads: {torch.get_num_threads()}")
    within = [_one_arm(credit, update, geometry) for _ in range(2)]
    print(f"arm: {credit}/{update}/{geometry}")
    print(f"within-process (OMP={threads}): {[f'{a:.17g}' for a in within]}")
    print(f"  stable within one process: {within[0] == within[1]}")

    for setting in ("8", "1"):
        env = dict(
            os.environ, OMP_NUM_THREADS=setting, MKL_NUM_THREADS=setting, CHILD="1"
        )
        runs = [
            subprocess.run(  # ruff: ignore[subprocess-without-shell-equals-true]
                [sys.executable, __file__, credit, update, geometry],
                env=env,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            for _ in range(2)
        ]
        print(f"across processes (OMP={setting}): {runs} stable: {runs[0] == runs[1]}")
