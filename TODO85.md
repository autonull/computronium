# TODO85 — Results-Now Strategy (Post-TODO84)

**Status:** Supersedes TODO84. All blockers fixed, all tests pass (883/883).
**Constraint:** Produce publishable evidence ASAP. No exploration. No "learning cycles." Ship results.

---

## 🎯 STRATEGY: THREE PARALLEL TRACKS, NO DEVIATION

| Track | Goal | Time/Week | Success Metric |
|-------|------|-----------|----------------|
| **A: Evidence** | Run ladder experiments that answer specific questions | 60% | ≥3 claim-grade cells per question |
| **B: Fix Blockers** | Fix anything that breaks Track A | 20% | 0 worker crashes, 0 flaky tests |
| **C: Ship** | Auto-generate paper figures, release artifacts | 20% | 1 figure/week, v1.2.0 ready |

**No track runs alone. Every session = A + (B if needed) + C.**

---

## 📋 QUESTION BACKLOG (Priority Order — Answer These)

| # | Question | Experiment (≤30 min) | Track A Command |
|---|----------|---------------------|-----------------|
| 1 | **Why ternary fails?** | Digital vs Ternary × weight_bits × LR | `./experiment_shallow.sh 0.3 --ladder --policy tpe --device cpu -w 4 --tasks digits --axes '{"substrate":["digital","ternary"],"credit":["gradient"],"update":["euclidean"]}' --hyperparams '{"substrate.weight_bits":[4,8,16,32],"dynamics.step_size":[1e-3,1e-2,1e-1]}' --skip-doctor` |
| 2 | **Gradient vs other credits?** | All credits × Digital × digits/fashion | `./experiment_shallow.sh 0.3 --ladder --policy tpe --device cpu -w 4 --tasks digits,fashion --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean"],"substrate":["digital"]}' --skip-doctor` |
| 3 | **Lion vs Euclidean vs Muon?** | All updates × Gradient × Digital | `./experiment_shallow.sh 0.3 --ladder --policy tpe --device cpu -w 4 --tasks digits,fashion,mnist --axes '{"credit":["gradient"],"update":["euclidean","lion","muon","natural_gradient"],"substrate":["digital"]}' --skip-doctor` |
| 4 | **Plasticity value?** | null vs rule_state vs temporal_psi × Gradient | `./experiment_shallow.sh 0.3 --ladder --policy tpe --device cpu -w 4 --tasks digits --axes '{"plasticity":["null","rule_state","temporal_psi"],"credit":["gradient"],"update":["euclidean"],"substrate":["digital","ternary"]}' --skip-doctor` |
| 5 | **Dynamics × Substrate?** | All dynamics × Digital/Ternary | `./experiment_shallow.sh 0.3 --ladder --policy tpe --device cpu -w 4 --tasks digits --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","ternary"],"credit":["gradient"],"update":["euclidean"]}' --skip-doctor` |
| 6 | **Full matrix (paper figure)** | Credit×Update×Substrate×Plasticity | `./experiment_shallow.sh 1.0 --ladder --policy tpe --device cpu -w 6 --tasks digits --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","muon"],"substrate":["digital","ternary"],"plasticity":["null","rule_state"]}' --skip-doctor` |

**Run in order. Stop when you have 3 claim-grade cells per question. Move to next.**

---

## ⚡ SESSION PROTOCOL (Copy-Paste-Run)

```bash
# 1. PICK NEXT UNANSWERED QUESTION FROM BACKLOG
# 2. RUN EXACT COMMAND FROM TABLE (adapt time/workers only)
# 3. ANALYZE (30 sec):
uv run comp report --store experiments/experiment_$(ls -t experiments/*.duckdb | head -1).duckdb --format text
# 4. LOG RESULT IN THIS FILE (see Cycle Log below)
# 5. IF BROKEN → TRACK B FIX (≤15 min), THEN RE-RUN
# 6. AUTO-GENERATE FIGURE (Track C):
uv run comp heatmap --store <latest>.duckdb --x credit --y update --z val_acc --out fig_q{N}.png
# 7. COMMIT + PUSH
```

---

## 🔧 TRACK B: BLOCKER FIXES (Only When Track A Breaks)

| Blocker | Fix | Time |
|---------|-----|------|
| Worker crash | Add deadline/timeout in wave.py | 15 min |
| Flaky test | Fix test, not code | 10 min |
| Ternary gradient quality | Add LR scaling by weight_bits | 20 min |
| CUDA multi-worker | Spawn + single GPU context | 30 min |
| Search space too large | Add incompatibility filter at harvest | 20 min |

**Fix only what blocks current question. No preventive work.**

---

## 📊 TRACK C: SHIP ARTIFACTS (Every Session)

| Artifact | Command | Destination |
|----------|---------|-------------|
| Heatmap | `uv run comp heatmap --store X --x A --y B --z val_acc --out fig.png` | `docs/figures/` |
| Ladder promotion | `uv run comp ladder --store X --out ladder.png` | `docs/figures/` |
| Comparison | `uv run comp compare --stores X Y --metric val_acc --by credit --out comp.csv` | `docs/data/` |
| Release note | `git log --oneline --since="1 week ago" > RELEASE_NOTES.md` | root |

**One artifact per question answered. Accumulate toward paper.**

---

## 📝 CYCLE LOG (Fill In As You Go)

| Q# | Question | Walltime | Claim-Grade Cells | Key Finding | Artifact | Fixed |
|----|----------|----------|-------------------|-------------|----------|-------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |

---

## 🚫 EXPLICITLY FORBIDDEN

- ❌ "Explore" or "see what happens"
- ❌ Running experiments not in the backlog
- ❌ Fixing things that aren't breaking current experiment
- ❌ Adding features not needed for current question
- ❌ Meetings, planning, retrospectives
- ❌ Any cycle > 30 min walltime

---

## 📦 COMMIT HISTORY (Baseline)

| Commit | Message |
|--------|---------|
| `3adf259e` | Fix planner _seen not cleared between startup trials and wave loop |
| `3744b6da` | Improve experiment_shallow.sh: add --skip-doctor flag |
| `9f07a70d` | Fix all pre-existing test failures |
| `60fe60cd` | Fix integration test regex |
| `3f51e370` | Fix TPE sampler: min_samples_per_combo |
| `131b528b` | Fix registry exports |
| ... | (see TODO84.md) |

---

## 🏁 START NOW

```bash
# Question 1: Why ternary fails?
./experiment_shallow.sh 0.3 --ladder --policy tpe --device cpu -w 4 --tasks digits \
  --axes '{"substrate":["digital","ternary"],"credit":["gradient"],"update":["euclidean"]}' \
  --hyperparams '{"substrate.weight_bits":[4,8,16,32],"dynamics.step_size":[1e-3,1e-2,1e-1]}' \
  --skip-doctor
```

**Run it. Analyze. Log. Fix if broken. Generate figure. Commit. Next question.**