# stability

Calibrated stability guard for dynamical neural systems. Attach an
`attach(model)` guard and kill runaway settling/energy dynamics with a
ROC-calibrated threshold — **<5% false-kill and >95% kill rate at
τ = 1.029** on the validated families.

## What it does

A `StabilityGuard` monitors a transition function's stability statistics:

- `windowed_growth` — peak activity growth over a settling window
  (deployed kill statistic; reads ≈1.0 on every known-good arm).
- `fast_proxy` — one-step Jacobian-vector gain (calibration only; blind to
  non-normal transients).

`attach(model)` wraps a PyTorch module with a `GuardHandle`:

```python
import torch
from stability import attach

model = torch.nn.Linear(10, 10)
guard = attach(model)

for step in range(100):
    x = torch.randn(32, 10)
    verdict = guard.check({"x": x})
    if verdict.kill:
        break
```

Also included: exact spectral metrics (σ_max vs ρ(J), mathematically
distinct), Lyapunov estimation, settling-time measurement, basin stability,
`FrontierRecord` aggregation with `ResourceUsage` vectors, ROC calibration
machinery (`calibrate_threshold`, Ginibre harvest helpers), and stable-matrix
construction helpers with realized-spectrum verification (`stability.matrices`).

## Installation

```bash
pip install -e packages/stability   # from the computronium repo
```

## CLI

```bash
stability check --gain 1.2        # attach guard to a linear map, print verdict
stability calibrate               # quick self-contained Ginibre ROC calibration
stability statistic --kind windowed_growth --gain 1.2
```

## Validated scope

Calibrated for **energy-minimization settling coordinates and non-normal
linear (Ginibre) dynamics** at tiny/demo scale, under the PR-5 acceptance
triple (<5% false-kill, >95% kill rate, <10% probe overhead at the calibrated
probe interval). Registered artifact: `docs/figures/registered/stability_guard_pr5.json`
(in the computronium repository). **No general-transformer-collapse claim.**

## Known limitations

- `fast_proxy` under-estimates σ_max on non-normal maps and is inflated by
  substrate noise — calibration-only, never the deployed kill statistic.
- Per-probe cost is 2–13× a transition step; deploy behind the calibrated
  probe interval (`probe_interval_for_overhead`).
- Power-iteration estimates are directional amplification, not certified
  σ_max/ρ for non-normal J — use `dominant_singular_value` /
  `spectral_radius_from_jacobian` for exact small-system metrics.
- Simulation only; no physical-hardware validation.

## Evidence

- TODO11 R11.3.3 "PR-5" calibration (computronium demo-harvest + Ginibre
  label rule; registered ROC artifact).
- Family sweep: `scripts/guard_family_sweep.py` (computronium repo).

## Verification level

Registered calibration artifact + parity test against the artifact
(`tests/platform/test_stability_parity.py` in the computronium repo);
package unit tests cover ROC semantics, probe/verdict behavior, Ginibre
label rule, and stable-matrix spectrum checks.

## Dependencies

`torch`, `numpy`. No computronium imports (boundary-tested).