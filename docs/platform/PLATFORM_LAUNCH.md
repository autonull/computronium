# Computronium Platform Launch

TODO20 converts the internal research laboratory into an external platform.
Normative plan: `TODO20.md`.

## Products

| Package | Path | Dependencies | Purpose |
|---|---|---|---|
| **ceec-core** | `packages/ceec-core` | stdlib only | Standalone epistemic governance ledger (evidence, beliefs, gates, audit) |
| **psi-peft** | `packages/psi-peft` | torch | Frozen-backbone task switching via temporal-ψ readouts |
| **local-feedback** | `packages/local-feedback` | torch | Adaptive local feedback projections (local credit without backprop) |
| **stability** | `packages/stability` | torch, numpy | Calibrated stability guard + stable-matrix helpers (single source, Rule 6) |
| **computronium-lab** | `packages/computronium-lab` | computronium | High-level API over the 6-axis ontology: presets, recipes, comparisons |
| **blueprints/docs** | `docs/platform/` | — | Recipe book, edge blueprint, external summary, publication draft |

## Package boundaries (G-RELEASE-1)

- `ceec-core`, `psi-peft`, `local-feedback`, `stability` must never import
  `computronium.*`.
- `computronium-lab` may import Computronium; its purpose is to expose it.
- Enforced by `tests/platform/test_package_boundaries.py` and per-package
  `test_psi_no_computronium_imports.py` / `test_lf_no_computronium_imports.py`
  (prefixed basenames — T21.3.3 single-command gate).
- **T21.3A.7 decision (2026-09-11):** the lab↔computronium integration is
  **sanctioned direction (a)** — the lab is the integration layer; nothing
  else may import it. Enforced by
  `packages/computronium-lab/tests/test_lab_boundary.py` (lab must import
  computronium; computronium + standalone packages must not import the
  lab). Inverting (moving preset factories into the package) was rejected:
  the factories consume internal modules the packages must not see.

## Release gates

Every released package must pass:

- **G-0** — supporting evidence not quarantined.
- **G-1** — package boundary respected (see above).
- **G-2** — runnable CPU demo, deterministic under seed, < 2 min quick mode.
- **G-3** — reproducible benchmark vs a meaningful baseline, ≥ 3 seeds,
  mean + variance, quick mode available.
- **G-4** — scoped README: summary, usage, validated scope, limitations,
  evidence refs, verification level.
- **G-5** — claim discipline: no universal-superiority claims.
- **G-6** — tests pass: unit, quick demo, determinism, parity where applicable.

Current gate status per package: `docs/platform/RELEASE_MANIFEST.md`.

## Harvest-only rule

No internal knowledge accumulation unless it directly supports a platform
release, a required validation, a hard defect fix, or an external blueprint.
No new ontology axes, no new ledger features, no benchmark campaigns outside
released packages.