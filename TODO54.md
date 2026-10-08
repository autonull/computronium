# TODO54 — Consolidated Remaining Work Plan

**Goal**: Finish the last few items to reach full production readiness. Most major milestones (P0-P6) are complete.

---

## Current Status Summary

| Phase | Focus | Status |
|-------|-------|--------|
| **P0** | GPU default + measured objectives | ✅ Complete |
| **P1** | Evaluator hardening + checkpointing | ✅ Complete |
| **P2** | Reporting + gallery | ✅ Complete (CI enabled) |
| **P3** | Agent-friendly CLI/Output | ✅ Complete |
| **P4** | Benchmark suites + analysis | ✅ Complete |
| **P5** | Campaign automation | ✅ Complete |
| **P6** | Reproducibility + packaging | ✅ Mostly complete |
| **Docs** | Full documentation suite | ✅ Complete |
| **Fixes** | GPU determinism, β≥1 constraint, memory leaks | ✅ Complete |

---

## Remaining Work (Priority Order)

### 1. Deeper Dynamical Analysis Integration (Analysis Infrastructure 7)

**Status**: Basic stability metrics integrated into `ProbeResult` (`spectral_radius`, `max_singular_value`, `min_singular_value`, `lyapunov_exponent`, `stability_margin`, `nonnormality`, `settle_steps`, `settle_converged`, `free_energy`). Primitives exist in `computronium/stability/` (Lyapunov, basin, spectral, settling).

**Tasks**:
- [ ] **Lyapunov spectra over trajectory**: Integrate `LyapunovSpectrumComputer` (QR decomposition over full training trajectory) into `CoreTrainerDriver` or `Evaluator`
- [ ] **Basin stability Monte Carlo**: Integrate `BasinStabilityAnalyzer` (perturbation sampling → return probability) for post-training analysis
- [ ] **Per-iteration energy tracking**: For PC/EqProp/Hopfield systems, track free energy/Hopfield energy per settle step
- [ ] **Expose in reports**: Add Lyapunov spectrum plot, basin stability histogram, energy trajectory to HTML/LaTeX reports
- [ ] **CLI access**: `comp stability-analysis --run-id <id> --metrics lyapunov_spectrum,basin_stability,energy_trajectory`

**Effort**: 2-3 days

**Files to modify**:
- `computronium/experiment/probe.py` — Add deeper analysis calls
- `computronium/experiment/surface/report.py` — Add new report sections
- `computronium/experiment/surface/cli.py` — Add `stability-analysis` subcommand

---

### 3. Minor Analysis Infrastructure Items

**Tasks**:
- [ ] **Effect size reporting in `comp stats`**: Add Cohen's d / Cliff's delta output when `--group-by` is used
- [ ] **Power analysis helper**: `comp power-analysis --metric val_acc --effect-size 0.5 --alpha 0.05 --power 0.8` → minimum seeds
- [ ] **Multi-objective scalarization**: `comp pareto --weights 0.5,0.3,0.2 --scalarize` (partially done)

**Effort**: 1 day

---

### 4. Nightly CI — Benchmark Regression Detection (P6)

**Status**: Nightly benchmark CI pipeline exists (`.github/workflows/nightly-benchmarks.yml`) and runs benchmarks nightly.

**Tasks**:
- [ ] Compare benchmark metrics against stored baselines (alert on >5% regression)
- [ ] Generate markdown regression report for PR comments
- [ ] Track latency/memory vs commit history

**Effort**: 0.5 days
---

## Quick Wins (< 1 Day Each)

| Item | Command | Effort |
|------|---------|--------|
| Add `--device` to `comp benchmark` | `cli.py` | 0.5 day |
| Add `--format` to `comp export` | `cli.py` | 0.5 day |
| Power analysis CLI | `cli.py` + `statistics.py` | 1 day |
| Effect size in `comp stats` | `cli.py` + `statistics.py` | 0.5 day |

---

## Deferred Indefinitely (Docker-Related)

| Item | Reason |
|------|--------|
| Full Docker round-trip testing | Requires Docker + NVIDIA Container Toolkit; export/repro code implemented but cannot verify bitwise match |
| Nightly CI Docker round-trip | Depends on above; nightly CI already tests benchmarks without Docker |
| Docker documentation updates | Depends on verified round-trip |

These are deferred because the current environment lacks Docker privileges and the export/repro functionality works without Docker (JSON export/repro is fully functional).

---

## Deferred / Nice-to-Have

These are not blockers for production readiness:

| Item | Reason |
|------|--------|
| Multi-GPU DDP/FSDP support | Requires multi-GPU hardware for testing; single-GPU works well |
| TileNet sharding | Niche use case; current primitives sufficient |
| Genealogy/t-SNE analysis | Advanced feature; not needed for core workflows |
| Energy landscape 2D slices | Research feature; stability package has primitives |
| Tile dynamics analysis | Research feature; not needed for core workflows |
| Z3 verification integration | Already in benchmark suite; not a runtime requirement |

---

## Execution Order

```
Week 1:
  □ Deeper dynamical analysis: Lyapunov spectra integration
  □ Deeper dynamical analysis: Basin stability Monte Carlo
  □ Deeper dynamical analysis: Per-iteration energy tracking
  □ Minor analysis: Effect size in comp stats, power analysis CLI
  
Week 2:
  □ Nightly CI: Benchmark regression detection
  □ Quick wins: --device to benchmark, --format to export
  □ Documentation updates for new features
```

---

## Success Criteria (Definition of Done)

- [ ] `comp stability-analysis --run-id <id> --metrics lyapunov_spectrum,basin_stability,energy_trajectory` produces plots/data
- [ ] Nightly CI runs benchmarks and compares against baseline (alert on >5% regression)
- [ ] All property locks still pass (L1-L7, J1-J7, axis locks, registry locks, gallery locks)
- [ ] All acceptance tests pass (U1-U5 kernel guarantees)
- [ ] `ruff format`, `ruff check`, `pyright` all pass
- [ ] JSON export/repro round-trip works: `comp export --format json` → `comp repro` → metrics match

---

## References

- `AGENTS.md` — Code guidelines, commit checklist
- `computronium/stability/` — Lyapunov, basin, spectral, settling analysis primitives
- `.github/workflows/nightly-benchmarks.yml` — Nightly CI pipeline
- `docs/experiments/reproducibility.md` — Reproducibility guide
- `computronium/experiment/probe.py` — CoreTrainerDriver with stability metrics integration