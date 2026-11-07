# TODO83 — From Laboratory to Evidence to Institution (Revised Post-Phase-0)

**Status:** Supersedes TODO82.md. Incorporates measured data from 2026-11-06 Phase 0 runs + bug fixes.
**Machine:** 16 cores, RTX 3080 10 GB, 31 GB RAM, Linux 7.3.1-1-cachyos
**Codebase:** computronium main (commit `cf9356c5` → latest)

> **Key insight from Phase 0:** The system runs. TPE sampler consumes full budget (16 cells in 22 min). Random sampler exhausts L0 in 50s. Two pre-existing bugs limit pass rate to 62.5%. Fidelity ladder is the critical path to claim-grade evidence.

---

## 🎯 FRESH SESSION ENTRY POINT — Start Here

**All primitive bugs fixed. Architecture converged. Fidelity ladder complete. H1 ran on CPU (20 records). Ladder test running (0.1h).**

### Current Background Process (0.1h fidelity ladder test)
```bash
# Check status (PID 1089510)
uv run comp status --store /tmp/test_ladder2.duckdb

# Expected: L1/L2 cells with 3/5 seed replication, claim-eligible > 0
```

### Immediate Next Actions (When Ladder Completes)
1. **Verify claim-eligible > 0** — First claim-grade evidence in computronium history
2. **Run H1** — Credit × Update on digits (0.5h, --device cpu)
3. **Run H2** — Dynamics × Substrate on digits (0.5h, --device cpu)
3. **Run H3** — Plasticity × Credit on digits (0.5h, --device cpu)

---

## Measured Baseline (2026-11-06)

| Run | Sampler | Budget | Walltime | Cells | Pass Rate | Coverage (sub/dyn/plas/cred/upd) |
|---|---|---|---|---|---|---|
| `exp_134031` | random | 0.5h | 50.6s | 11 | 91% | 4/2/5/5/7 |
| `exp_140428` | **tpe** | **0.5h** | **22m** | **16** | **62.5%** | **5/4/5/5/7** |
| `exp_185146` | **tpe+ladder** | **0.5h** | **30m** | **47** | **~60%** | **L0:40, L1:5, L2:2** |

**Bugs surfaced (pre-existing, all fixed):**
1. ✅ `temporal_psi` shape mismatch — auto-truncate batch
2. ✅ `ConvGeometry` even kernel_size — auto-correct to odd
3. ✅ Ladder promotion logic — reserved budget + `_run_ladder_promotion()`
4. ✅ Maturity from schedule fidelity — L0→l0, L1→l1, L2→l2
5. ✅ Normalized metric in payload — `normalize_score(val_acc, baseline)`
6. ✅ Record.coordinate reconstruction — from stored fields
7. ✅ Claim eligibility query — `normalized_metric` key mismatch fixed (`normalized_val_acc` → `normalized_metric`)
8. ✅ Ladder promotion replication — L1/L2 cells now expand to `n_seeds` replicates (3/5 seeds)
9. ✅ ProcessPoolExecutor forkserver hang — force 'spawn' start method (scipy sets forkserver)

---

## Phase 1 — The Laboratory Runs (Week 1–2 Remaining)

**Goal:** Unattended, reproducible, powered runs; first H1–H6 verdicts; gate calibrated.

### Week 1: COMPLETE (Bug Fixes + Fidelity Ladder)

| ID | Task | Status |
|---|---|---|
| **F1** | Fix `temporal_psi` shape mismatch | ✅ Done |
| **F2** | Fix `ConvGeometry` kernel_size | ✅ Done |
| **F3** | Verify fixes with 0.05h TPE smoke | ✅ Done |
| **F4** | Fix claim eligibility query (`normalized_metric` key) | ✅ Done |
| **F5** | Fix ladder promotion replication (expand to n_seeds) | ✅ Done |
| **L1** | Run fidelity ladder (L0→L1→L2) | ✅ Done (54 cells, 39 pass) |

### Week 2: Powered Hypothesis Triage (A3) — IN PROGRESS

| ID | Task | Time | Command / Action | Success Criteria |
|---|---|---|---|---|
| **H1** | Credit × Update on digits (n≥3) | 30 min | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}' --device cpu` | 6+ cells at L1/L2, verdicts with `power_achieved` |
| **H2** | Dynamics × Substrate on digits | 30 min | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}' --device cpu` | 6+ cells at L1/L2 |
| **H3** | Plasticity × Credit on digits | 30 min | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}' --device cpu` | 6+ cells at L1/L2 |
| **L2** | Fidelity ladder replication test | 10 min | `./experiment_shallow.sh 0.1 --ladder --policy tpe --device cpu` | L1/L2 cells with 3/5 seeds, claim-eligible > 0 |

> **L2 RUNNING (PID 1089510). Then run H1/H2/H3 sequentially on CPU. Collect verdicts.**

---

### Week 3: Sampler Comparison + First Artifact (A2, A4)

| ID | Task | Time | Command / Action | Success Criteria |
|---|---|---|---|---|
| **S1** | Static vs TPE identical budget | 30 min | `./experiment_shallow.sh 0.5 --policy random` (CI baseline) + `./experiment_shallow.sh 0.5 --policy tpe` | Two reports, marginal rankings compared |
| **A1** | Publish pre-registered comparison | 30 min | Write `docs/experiments/credit_vs_update_digits.md` from H1 results | Artifact exists, reproducible from store hash |

---

### Week 4: Instrument Correctness (B5–B10)

| ID | Task | Time | Command / Action | Success Criteria |
|---|---|---|---|---|
| **B5** | Gate calibration spec (1 page) | 1 hr | Write `docs/specs/gate_calibration.md` — sensitivity/specificity vs held-out | Spec approved |
| **B6** | Drift detection alert | 30 min | Add M2 alert: NaN rate > 5%, walltime collapse > 2×, identical val_acc | Alert fires in test |
| **B7** | Metric coverage warnings | 30 min | Refuse silently-empty report sections; print measured vs untouched | Warning in report |
| **B8** | `capabilities` command | 30 min | `uv run comp capabilities --store <db>` dumps machine-readable registry | Command works |
| **B9** | Sampler arc: delete `propose()` | 1 hr | Remove candidate-list `propose()`; policy-aware compatibility sampling | Tests pass |
| **B10** | Validation codegen | 2 hr | Generate `SystemConfig.validate` from registries; delete whitelists | Registry↔codegen↔validate agree |

---

### Week 5: Release 1.1 Prep

| ID | Task | Time | Success Criteria |
|---|---|---|---|
| **R1** | `CONTRIBUTING.md` with run gates | 30 min | `ruff format`, `ruff check`, `pyright` on changed, targeted tests |
| **R2** | Release notes | 30 min | Changelog from `cf9356c5`..HEAD |
| **R3** | Tag `v1.1.0` | 5 min | `git tag v1.1.0 && git push --tags` |
| **R4** | Clean checkout demo | 10 min | `uv run comp run demo` green on fresh clone |

---

## Phase 2 — The Evidence Generalizes (Weeks 6–13)

**Goal:** Claims refused when unregistered; HPO parity invariant; evidence beyond digits.

| ID | Task | Dependency | Time |
|---|---|---|---|
| **C1** | Pre-registration enforced (Class E refused) | B9, B10 | 1 week |
| **C2** | Blinding (arm labels → A/B/C) | C1 | 1 week |
| **C3** | HPO parity invariant in `comp run` | C1 | 1 week |
| **C4** | 7-domain expansion: vision (cifar100, svhn) | — | 2 weeks |
| **C5** | Cross-domain transfer test (digits→cifar10+shakespeare) | C4 | 1 week |
| **C6** | Cross-substrate robustness (digital vs memristive) | C4 | 1 week |
| **C7** | Default replication n_seeds ≥ 3 floor | C1 | 30 min |
| **C8** | Fair-HPO recovery study protocol | C3 | 1 week |
| **C9** | M2 drift gates in CI canary | B6 | 30 min |
| **C10** | Error-message catalogue (`docs/errors.md`) | C1 | 1 week |

**v1.2 acceptance:** C1–C3 enforced/tested; C4 ≥2 new tasks; C5 published; C8 protocol drafted; PyPI `computronium==1.2.0`.

---

## Phase 3 — The Consortium (Months 6–9)

| ID | Task | Dependency |
|---|---|---|
| **D1** | Distribution: PyPI, Docker, CHANGELOG, semver | v1.2 |
| **D2** | Ten-minute path: RunSpec YAML + `question_first()` | v1.2 |
| **D3** | API reference generated, complete | v1.2 |
| **D4** | Consortium pilot: 3 labs, pre-registered, published | D1–D3 |
| **D5** | Public record: provenance-hashed registry, corrections log | D4 |
| **D6** | Adoption kit: FAIRNESS_CONTRACT, templates, fork-and-run | D4 |
| **D7** | Docs IA: README ≤600 lines, depth→`docs/`, landing pages | D1 |
| **D8** | Release signing, `comp export --docker`, fix repro doc | D1 |

**v2.0 acceptance:** D1 published; D2 passes on clean VM; D4 signed off; D5 public; ≥1 external contributor.

---

## Continuous Engineering (Every Release)

| ID | Task | Cadence |
|---|---|---|
| **E1** | Register C paydown (650→0) | Per release, ratchet down |
| **E2** | Repo-wide pyright (strict on new) | Per release |
| **E3** | `pip-audit` clean (CI gate) | Per release |
| **E4** | CI: property + demo + vertical + drift locks | Every PR |
| **E5** | Determinism docs (CPU/GPU/BLAS variance) | Per release |
| **E6** | Dependency diet (`uv.lock` audit) | Annual |

---

## Experiment Queue (Ready to Run, ≤30 min each)

| # | Experiment | Command | Expected Outcome |
|---|---|---|---|
| 1 | **Fix verification** | `./experiment_shallow.sh 0.05 --policy tpe` | 100% pass, no errors |
| 2 | **Fidelity ladder** | `./experiment_shallow.sh 0.5 --ladder` | L2 cells, claim-eligible > 0 |
| 3 | **H1: Credit×Update** | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}'` | 6+ L1/L2 cells |
| 4 | **H2: Dynamics×Substrate** | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}'` | 6+ L1/L2 cells |
| 5 | **H3: Plasticity×Credit** | `./experiment_shallow.sh 0.5 --policy tpe --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}'` | 6+ L1/L2 cells |
| 6 | **Static vs TPE** | `./experiment_shallow.sh 0.5 --policy random` + TPE | Two comparable reports |
| 7 | **Multi-task TPE** | `./experiment_shallow.sh 0.5 --policy tpe --tasks digits,cifar10,fashion_mnist` | Cross-domain coverage |

---

## Immediate Next Steps (This Session)

### 1. Fix `temporal_psi` (F1) — 30 min
```bash
# Edit core/plasticity/temporal_psi.py:141
# h_aug.T @ residual shape mismatch: (64,17) @ (32,2) → fix dimensions
```

### 2. Fix numerical stability (F2) — 30 min
```bash
# Edit core/system_trainer/trainer.py
# Add gradient clipping: torch.nn.utils.clip_grad_norm_(params, 1.0)
# Add loss scaling for mixed precision
```

### 3. Smoke verify (F3) — 5 min
```bash
./experiment_shallow.sh 0.05 --policy tpe
# Expect: 100% pass, no quarantined cells
```

### 4. **Start fidelity ladder (L1) — 30 min BACKGROUND**
```bash
nohup ./experiment_shallow.sh 0.5 --ladder > logs/ladder_$(date +%s).log 2>&1 &
echo "PID: $! — check logs/ladder_*.log"
```

---

## Immediate Commands for Fresh Session

```bash
# 1. Check fidelity ladder completion
uv run comp status --store experiments/experiment_$(ls -t experiments/experiment_*.duckdb | head -1 | xargs basename | sed 's/.duckdb//').duckdb

# 2. Verify claim-eligible cells
uv run comp report --store <same_store> --format text

# 3. Run H1 (Credit × Update)
nohup ./experiment_shallow.sh 0.5 --policy tpe --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}' > logs/h1_$(date +%s).log 2>&1 &

# 4. While H1 runs, check H1 progress
uv run comp status --store <h1_store>
```

---

## Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-11-06 | TPE is primary sampler; random is CI-only | Random exhausts L0 in 50s; TPE consumes full budget |
| 2026-11-06 | Fidelity ladder is critical path to claims | Only L2 (n≥3) cells are claim-eligible |
| 2026-11-06 | All primitive bugs fixed in this session | temporal_psi, ConvGeometry, promotion, maturity, normalized_metric |
| 2026-11-06 | Max experiment time: 30 min | Keeps iteration tight; background for ladder |
| 2026-11-06 | Claim eligibility query fixed | `normalized_val_acc` → `normalized_metric` in SQL prefilter |
| 2026-11-06 | Ladder promotion expands to n_seeds replicates | L1=3 seeds, L2=5 seeds per cell for claim eligibility |
| 2026-11-06 | ProcessPoolExecutor uses 'spawn' not 'forkserver' | scipy sets forkserver which hangs with PyTorch workers |
| 2026-11-06 | Experiments run on CPU for stability | CUDA + multiprocessing hangs; CPU works reliably |

---

## Quick Reference: Commands to Run Now

```bash
# 1. Check ladder test completion
uv run comp status --store /tmp/test_ladder2.duckdb

# 2. Verify claim-eligible cells from ladder
uv run comp report --store /tmp/test_ladder2.duckdb --format text

# 3. Run H1 (Credit × Update) on CPU
nohup ./experiment_shallow.sh 0.5 --policy tpe --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}' --device cpu > logs/h1_$(date +%s).log 2>&1 &

# 4. Run H2 (Dynamics × Substrate) on CPU
nohup ./experiment_shallow.sh 0.5 --policy tpe --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}' --device cpu > logs/h2_$(date +%s).log 2>&1 &

# 5. Run H3 (Plasticity × Credit) on CPU
nohup ./experiment_shallow.sh 0.5 --policy tpe --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}' --device cpu > logs/h3_$(date +%s).log 2>&1 &
```

---

*Generated 2026-11-06 from Phase 0 measured data + bug fixes. Supersedes TODO82.md.*