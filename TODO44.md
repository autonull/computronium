# TODO44.md — Codebase Cleanup & Experiment Readiness

**Follows:** TODO43.plan3.md (WP22 complete, all kernel work done)
**Goal:** Physically delete legacy pillars, update non-kernel consumers, refresh README.md, prepare demonstration experiments

---

## 1. Legacy Pillar Deletion (Actual — WP21 was claimed complete but not executed)

### 1.1 Directories to Delete
| Pillar | Path | Lines of Code | Notes |
|---|---|---|---|
| AutoScientist | `computronium/autoscientist/` | ~300KB | Replaced by `experiment/execution/` policies + `cli/scientist.py` |
| Hyperopt | `computronium/hyperopt/` | ~180KB | Replaced by `ModelBasedPolicy` (TPE/NSGA-II/GP) |
| Legacy Execution | `computronium/execution/` | ~280KB | Replaced by `PipelineRunner` + Stage dispatch |
| Core Campaign | `computronium/core/campaign/` | ~200KB | Replaced by `EvidenceDrivenAllocator` + `RecordStore` |
| Lightning | `computronium/lightning_/` | ~25KB | Replaced by `TrainerDrivenPolicy` adapter |
| **Total** | | **~985KB** | |

### 1.2 Non-Kernel Consumers to Migrate or Delete
These modules import legacy pillars and must be updated to use kernel equivalents or deleted:

| Module | Legacy Imports | Action |
|---|---|---|
| `computronium/cli/campaign.py` | `core.campaign.*`, `core.campaign.stack` | Migrate to `experiment/surface/cli` or delete |
| `computronium/cli/continuous.py` | `autoscientist.broad_map`, `autoscientist.defects`, `autoscientist.objectives` | Migrate to kernel `continuous` policy loop |
| `computronium/cli/daemon.py` | `autoscientist.daemon` | Migrate to kernel `daemon` surface |
| `computronium/cli/frontier.py` | `hyperopt.frontier` | Migrate to kernel Pareto/frontier |
| `computronium/cli/shared.py` | `hyperopt.eval_tiers`, `hyperopt.experiment` | Delete or migrate |
| `computronium/cli/commands/search.py` | `hyperopt.create_study`, `hyperopt.eval_tiers` | Delete or migrate |
| `computronium/cli/commands/verify.py` | `hyperopt.eval_tiers`, `hyperopt.experiment` | Delete or migrate |
| `computronium/cli/commands/compare.py` | `hyperopt.comparison`, `hyperopt.storage` | Delete or migrate |
| `computronium/cli/commands/portfolio.py` | `hyperopt.storage` | Delete or migrate |
| `computronium/analysis/results.py` | `hyperopt.comparison`, `hyperopt.metrics` | Migrate to kernel analysis |
| `computronium/analysis/dominance.py` | `autoscientist.objectives` | Migrate to kernel |
| `computronium/analysis/counterfactual.py` | `autoscientist.counterfactual`, `core.campaign.frontier_record` | Migrate or delete |
| `computronium/analysis/failure_manifesto.py` | `execution._state.FailureTracker` | Migrate to `experiment.evidence.failure` |

### 1.3 Package-Level Cleanup
- `packages/computronium-lab/` — research layer; verify its `Lab` API uses kernel (`experiment/`) not legacy. If it wraps legacy, rewrite or delete.

---

## 2. Import Graph Verification

After deletion, run isolation lock to confirm zero legacy imports anywhere:

```bash
# Extended to scan ALL computronium/ modules, not just experiment/
uv run python -m pytest tests/property/test_kernel_isolation_lock.py -v
```

**New test needed:** `tests/property/test_full_import_isolation_lock.py` — scans entire `computronium/` tree (except `packages/`) for forbidden imports.

---

## 3. README.md Update

### 3.1 Sections to Rewrite
| Section | Current State | Target |
|---|---|---|
| **Architecture Diagram** | Shows legacy 6-axis flow | Update to show `experiment/` kernel: RunSpec → SearchSpace → Policy → Stage → RecordStore |
| **CLI Reference** | Lists legacy commands | Verify `comp` subcommands match `_SUBCOMMANDS` in `cli/__main__.py` |
| **13 Model Factories** | Some reference legacy configs | Verify all factories compose via `experiment/execution/compose.py` |
| **Quickstarts** | May reference deleted paths | Update to kernel entry points |
| **Status Line** | "Active development" | Update to "Unified kernel v3.0 — all WPs complete" |

### 3.2 Add New Sections
- **Unified Kernel Overview** — one-page summary of `experiment/` architecture
- **Policy Interchangeability Demo** — code snippet showing U4 (swap policy, same RunSpec/Store)
- **Multi-Objective Campaign** — `comp continuous --objectives accuracy,walltime_s,param_count`
- **Pause/Resume/Replay** — `run_id` based workflow

---

## 4. Demonstration Experiments

Create runnable scripts in `scripts/demos/` that exercise new kernel capabilities end-to-end:

### 4.1 Core Demos (must pass)
| Demo | Purpose | Kernel Features |
|---|---|---|
| `demo_unified_pipeline.py` | Single run: Question → RunSpec → SynthesisPolicy → Pipeline → RecordStore | U1 |
| `demo_policy_swap.py` | Same RunSpec/Space, 4 policies (Random/TPE/Evolution/Synthesis) | U4 |
| `demo_pause_resume.py` | Run → pause (Ctrl-C) → resume via `run_id` → report | U3 |
| `demo_multi_objective.py` | Pareto front over accuracy/walltime/params | U5 + `--objectives` |
| `demo_cross_policy_reuse.py` | Random → TPE → Evolution over same store | U5 |
| `demo_contrast_design.py` | OFAT/fractional factorial DOE with DataOrigin | WP18 |

### 4.2 Benchmark Reproduction (E-class)
| Script | Benchmark | Expected |
|---|---|---|
| `scripts/probes/e3_seeded_axis_effect.py` | E3: Seeded axis-effect reproduction | d ≈ -1.5, p < 0.01 |
| `scripts/probes/e4_transfer_provenance.py` | E4: Cross-task transfer with provenance | d ≈ -1.5, p < 0.01 |
| `scripts/probes/conformance_evidence_audit.py` | C1–C88 audit | 46 pass, 42 skip, 0 fail |

### 4.3 Gallery Regeneration
```bash
# Re-render all figures from live kernel runs
comp gallery --run --generate-broad-demo
# Updates docs/figures/manifest.json + run_records/*.json
```

---

## 5. Dependency & Environment Hygiene

| Task | Command |
|---|---|
| Verify dev-env smoke | `uv run python -c "import duckdb, optuna, scipy, torchvision, pytest"` |
| Regenerate `uv.lock` after deletions | `uv sync --dev --all-extras` |
| Re-pin gallery manifest | `comp gallery --run` → `docs/figures/manifest.json` |
| Regenerate `capabilities.json` | `uv run python -m computronium.experiment.schema.registries` |

---

## 6. Execution Order (Dependency-Ordered)

```text
WP44.1 Legacy pillar physical deletion
    │
    ├─► WP44.2 Migrate/delete non-kernel consumers (cli/, analysis/)
    │
    ├─► WP44.3 Extend import isolation lock to full tree
    │
    ├─► WP44.4 Update README.md (architecture, CLI, quickstarts)
    │
    ├─► WP44.5 Create demo scripts (scripts/demos/)
    │
    ├─► WP44.6 Run E3/E4 + conformance audit to re-verify
    │
    └─► WP44.7 Gallery regeneration + manifest pin
```

---

## 7. Acceptance Criteria

- [ ] All 6 legacy pillar directories physically deleted
- [ ] Zero `import computronium.autoscientist|hyperopt|lightning_|core.campaign|execution` in `computronium/` (except `packages/`)
- [ ] `test_full_import_isolation_lock.py` passes
- [ ] All 6 demo scripts run without error, produce expected outputs
- [ ] `comp gallery --run` completes, updates `docs/figures/manifest.json`
- [ ] README.md reflects unified kernel (no legacy references)
- [ ] `uv sync --dev --all-extras` installs cleanly
- [ ] All existing tests still pass (U1–U5, property locks, atomic append)

---

## 8. Risk Mitigation

| Risk | Mitigation |
|---|---|
| CLI commands break after legacy delete | Each `comp` subcommand in `_SUBCOMMANDS` must be tested post-delete |
| `packages/computronium-lab` depends on legacy | Audit its imports first; rewrite to kernel or vendor what it needs |
| `analysis/` module loses functionality | Only migrate what's used by demos/CI; delete rest |
| Gallery figures regenerate differently | Accept new figures; pin manifest; document expected visual changes |

---

## 9. Notes

- **No backwards compatibility** — same as TODO43 Directive 1. Delete wholesale.
- **Kernel is the single source of truth** — `computronium/experiment/` owns all semantics.
- **Non-kernel code is disposable** — `cli/`, `analysis/`, `benchmarks/` etc. exist only to serve demos/CI. If they import legacy, they are legacy.
- **Keep `packages/`** — `ceec-core`, `psi-peft`, `local-feedback`, `stability` are active platform packages, not legacy.