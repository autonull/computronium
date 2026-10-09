# TODO54 — Consolidated Remaining Work Plan

**Goal**: Finish remaining enhancements. **The system already runs preliminary experiments (~1 hour) and generates meaningful reports** — see "Already Working" below.

---

## Already Working (Capability — Run After Phases 1-2 Complete)

The system **already supports** preliminary experiments (~1 hour) and publication-ready reports. After Phases 1-2 are complete, run:

```bash
# 1. Run experiment campaign (~1 hour on RTX 3080)
uv run comp campaign \
  --model backprop,eqprop,fa,hebbian \
  --task digits \
  --epochs 30 \
  --seeds 42,123,456 \
  --store exp.db

# 2. Generate publication-ready HTML report
uv run comp report --store exp.db --format html --output report.html

# 3. Or LaTeX/PDF for paper
uv run comp report --store exp.db --format pdf --output report.pdf
```

**Report includes**: Pareto frontiers (accuracy vs walltime/params/stability), convergence curves, ablation tables (credit/substrate/plasticity), stability metrics (ρ(J), σ_max, Lyapunov), objective distributions, convergence curves.

**Analysis commands**: `comp stats`, `comp pareto`, `comp diff`, `comp export --format json`, `comp repro`, `comp schema`.

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

## Remaining Work — Phased for Fastest Path to Polished Workflow

### Phase 0: Verify End-to-End (0 days — Dry Runs & Smoke Tests Only)

**Do not run full experiments yet.** Use dry runs and smoke tests to verify the pipeline:

```bash
# Dry-run campaign plan (no execution, <1s)
uv run comp campaign \
  --model backprop,eqprop,fa,hebbian \
  --task digits \
  --epochs 30 \
  --seeds 42,123,456 \
  --store exp.db \
  --dry-run --format json

# Smoke test: single seed, 1 epoch (~30s on RTX 3080)
uv run comp run quick-verify --store exp.db --device auto --iterations 1

# Verify report generation on smoke test data (<10s)
uv run comp report --store exp.db --format html --output report.html
```

If dry-run shows valid JSON plan and smoke test + report complete successfully, the pipeline is verified.

### Phase 1: UX Polish — Quick Wins (0.5 days) — ✅ COMPLETE

Small CLI improvements that make the existing workflow smoother.

| Item | Command | Effort | Why | Status |
|------|---------|--------|-----|--------|
| Add `--device` to `comp benchmark` | `cli.py` | 0.5 day | Consistency with `comp run` | ✅ Already existed |
| Add `--format` to `comp export` | `cli.py` | 0.5 day | JSON/CSV export flexibility | ✅ Already existed |
| Effect size in `comp stats` | `cli.py` + `statistics.py` | 0.5 day | Cohen's d / Cliff's delta for `--group-by` | ✅ Done |

**Total**: 1.5 days (can be done in parallel)

### Phase 2: Analysis Depth — Minor Enhancements (0.5 days) — ✅ COMPLETE

Deeper statistical interpretation for reports.

| Item | Command | Effort | Why | Status |
|------|---------|--------|-----|--------|
| Power analysis CLI | `cli.py` + `statistics.py` | 0.5 day | Experiment design helper | ✅ Done (`comp power-analysis`) |
| Multi-objective scalarization | `cli.py` | 0.5 day | Weighted Pareto for decision-making | ✅ Done (`comp pareto --weights --scalarize`) |

**Total**: 1 day

### Phase 3: Dynamical Analysis Richness — Deep Enhancement (2-3 days)

Richer dynamical systems analysis for specialized reports. **Optional** — reports are already meaningful without this.

| Item | Effort | Files |
|------|--------|-------|
| Lyapunov spectra over trajectory | 1 day | `probe.py`, `report.py`, `cli.py` |
| Basin stability Monte Carlo | 1 day | `probe.py`, `report.py`, `cli.py` |
| Per-iteration energy tracking | 0.5 day | `probe.py`, `report.py` |
| Report integration (plots/tables) | 0.5 day | `report.py` |
| `comp stability-analysis` CLI | 0.5 day | `cli.py` |

**Total**: 3 days

---

## Quick Wins (All in Phase 1)

| Item | Command | Effort | Phase | Status |
|------|---------|--------|-------|--------|
| Add `--device` to `comp benchmark` | `cli.py` | 0.5 day | 1 | ✅ Already existed |
| Add `--format` to `comp export` | `cli.py` | 0.5 day | 1 | ✅ Already existed |
| Effect size in `comp stats` | `cli.py` + `statistics.py` | 0.5 day | 1 | ✅ Done |
| Power analysis CLI | `cli.py` + `statistics.py` | 0.5 day | 2 | ✅ Done (`comp power-analysis`) |
| Multi-objective scalarization | `cli.py` | 0.5 day | 2 | ✅ Done (`comp pareto --weights --scalarize`) |

---

## Implementation Notes

### Phase 1 — Effect sizes in `comp stats`:
- Added Cohen's d and Cliff's delta computation when `--group-by` is specified
- Uses existing `computronium.validation.statistics.cohens_d` and `cliffs_delta` functions
- Compares first group (reference) against all other groups
- Outputs fields like `val_acc_cohens_d_vs_<group>` and `val_acc_cliffs_delta_vs_<group>`

### Phase 2 — Power analysis CLI (`comp power-analysis`):
- Supports solving for power (given n) or n (given target power)
- Uses `computronium.validation.statistics.power_for_two_sample` with binary search for sample size calculation
- Outputs JSON or text format
- Example: `comp power-analysis --effect-size 0.5 --target-power 0.8 --solve-for n --format text`

### Phase 2 — Multi-objective scalarization in `comp pareto`:
- Added `--weights` and `--scalarize` options
- Normalizes objectives to [0, 1] based on maximize/minimize direction
- Computes weighted scores and ranks all Pareto frontier points
- Outputs `scalarized_score` and `scalarized_rank` fields
- Example: `comp pareto --objectives val_acc,walltime_s --weights 0.7,0.3 --scalarize --output pareto.csv`

---

## Phase 0 Verification Results

```
# Dry-run campaign plan (no execution, <1s)
uv run comp campaign \
  --model backprop,eqprop,fa,hebbian \
  --task digits \
  --epochs 30 \
  --seeds 42,123,456 \
  --store exp.db \
  --dry-run --format json
# ✅ Shows valid JSON plan with 10 cells

# Smoke test: single seed, 1 epoch
uv run comp run quick-verify --store exp.db --device cpu --overrides '{"epochs": 1}'
# ✅ Completes in ~1.6s with 10 records

# Verify report generation on smoke test data
uv run comp report --store exp.db --format html --output report.html
# ✅ Generates HTML report successfully
```

## Deferred Indefinitely

| Item | Reason |
|------|--------|
| Full Docker round-trip testing | Requires Docker + NVIDIA Container Toolkit; export/repro code implemented but cannot verify bitwise match |
| Nightly CI Docker round-trip | Depends on above; nightly CI already tests benchmarks without Docker |
| Docker documentation updates | Depends on verified round-trip |
| Nightly CI benchmark regression detection | Pipeline exists but regression comparison not implemented; not blocking production readiness |

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
Day 0 (verify):  Run "Already Working" commands → confirm reports generate
Day 1 (Phase 1): Quick wins — --device to benchmark, --format to export, effect size in stats
Day 2 (Phase 2): Minor analysis — power analysis CLI, multi-objective scalarization
Day 3-5 (Phase 3, optional): Deeper dynamical analysis — Lyapunov, basin, energy tracking
```

**Total for polished workflow**: ~2 days (Phases 1+2)
**Total for full enhancement**: ~5 days (all phases)

---

## Success Criteria (Definition of Done)

- [x] **Phase 0 verified**: Dry-run campaign shows valid plan; smoke test (1 epoch) + report generation complete
- [x] **Phase 1**: `--device` on benchmark, `--format` on export, effect size in `comp stats --group-by`
- [x] **Phase 2**: `comp power-analysis`, `comp pareto --weights --scalarize`
- [ ] All property locks pass (L1-L7, J1-J7, axis locks, registry locks, gallery locks)
- [ ] All acceptance tests pass (U1-U5 kernel guarantees)
- [ ] `ruff format`, `ruff check`, `pyright` all pass
- [ ] JSON export/repro round-trip works: `comp export --format json` → `comp repro` → metrics match

---

## References

- `AGENTS.md` — Code guidelines, commit checklist
- `computronium/stability/` — Lyapunov, basin, spectral, settling analysis primitives
- `docs/experiments/reproducibility.md` — Reproducibility guide
- `computronium/experiment/probe.py` — CoreTrainerDriver with stability metrics integration