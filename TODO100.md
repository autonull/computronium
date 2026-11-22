# TODO100 — SEC Loop: Real Experiments, Real Defects, Real Fixes

**Status:** 2026-11-22. SEC loop entered. Phase 1 (Rung 0) complete. Phase 2 (Rung 1) in progress.
**Principle:** Breadth before optimization. Every low cell is a defect probe. Fixes propagate across primitives via shared implementation.

---

## ✅ Phase 1 Complete: Rung 0 Wiring Verification (2026-11-22)

| Credit Family | Pseudo-Grad Norm | Status |
|---------------|------------------|--------|
| gradient | 2.38 | ✅ Wired |
| random_projections | 0.38 | ✅ Wired |
| local_contrastive | 144.27 | ✅ Wired |
| thermodynamic_contrast | 3.21 | ✅ Wired |
| pc_alm | 1.34 | ✅ Wired |
| target_inversion | 0.24 | ✅ Wired |
| pepita | 2.22 | ✅ Wired |
| forward_tangent | 100.42 | ✅ Wired |
| score_function | 33.16 | ✅ Wired |
| zeroth_order | 98.88 | ✅ Wired |
| surrogate | 5.17 | ✅ Wired |
| local_supervision | 1.53 | ✅ Wired |
| local_goodness | 0.18 | ✅ Wired |
| hybrid | 2.52 | ✅ Wired |
| eligibility_prop | 2.66 | ✅ Wired |
| unbiased_rtrl | 8.10 | ✅ Wired |
| rtrl_reference | 2.54 | ✅ Wired |
| homeostatic (error-blind) | 7.21 | ✅ Wired (non-zero update) |
| temporal_trace (error-blind) | 3.3e-7 | ⚠️ Near-zero (known: contract is non-zero update, not accuracy) |

**All 19 credits wired.** Positive control passes on mnist (val_acc=0.89, chance=0.10).
No "free settle telemetry failed" warnings.
All 75 primitive contract tests pass.

---

## 📊 Current Capability Map (Post-TODO99 + Phase 1)

---

## 🔬 SEC Loop Entry Point

**Decision:** "Which credit families achieve practical significance (d ≥ family_min) on their declared task families at their best declared box?"

**Actions on decision:**
- **YES (claim):** Pre-register paired comparison (Rung 3), measure with n=5 seeds, publish coordinate + cost
- **NO (defect):** Name mechanism + failing test → fix → re-measure at Rung 1
- **INCONCLUSIVE (gap):** Document capability gap (primitive needed, cost, family unlocked) → park

**Stop rule:** Climb rungs only while ambiguous. Cheapest falsifier first. Record rung, stop reason, box, cost.

**Error costs:**
- False claim (α=0.05 controlled by pre-registration)
- False defect (wasted fix effort) — mitigated by requiring named mechanism + failing test
- Missed capability (β) — mitigated by breadth-first mapping before any claim

---

## 📊 Current Capability Map (Post-Phase 1)

| Credit Family | Declared Families | Base Box (L0) | Rung 0 Wired? | Rung 1 Viable (L0, 1 epoch, 1 seed, mnist) | Status |
|---------------|-------------------|---------------|---------------|--------------------------------------------|--------|
| gradient | vision, seq, tab, cont, graph, rl, sci, lm, neuro | ff/inst/euclid | ✅ | val_acc=0.89 | **Claim candidate** |
| random_projections | vision, seq, tab | ff/inst/euclid | ✅ | val_acc=0.10 (at fb=0.01) | **Ladder needed** |
| local_contrastive | vision | ff/inst/euclid | ✅ | val_acc=0.08 | **Ladder needed** |
| thermodynamic_contrast | vision, seq | ff/energy_min/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| pc_alm | vision, graph* | ff/pc_alm/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| target_inversion | vision, cont* | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| pepita | vision, seq | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| forward_tangent | vision, seq | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| score_function | vision, seq, tab | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| zeroth_order | vision, seq, tab | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| surrogate | vision, seq, tab | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| local_supervision | vision, seq | ff/inst/euclid | ✅ | val_acc=0.67 | **Viable** |
| eligibility_prop | seq, rl | rec/inst/euclid | ✅ | ❌ (no vision family) | **Refused** |
| unbiased_rtrl | seq, rl | rec/inst/euclid | ✅ | ❌ (no vision family) | **Refused** |
| rtrl_reference | seq, rl | rec/inst/euclid | ✅ | ❌ (no vision family) | **Refused** |
| local_goodness | vision | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| hybrid | vision, seq | ff/inst/euclid | ✅ | ❓ (not screened yet) | **Screen needed** |
| homeostatic (error-blind) | all | any/any/any | ✅ | non-zero update | **Contract met** |
| temporal_trace (error-blind) | seq, rl | rec/inst/euclid | ✅ | non-zero update | **Contract met** |

*Added in TODO99 #3 (graph_energy_min, sequence_energy_min, continual_energy_min)

**Screened on mnist (vision): 4 measured, 1 refused (eligibility_prop), 14 unmeasured.**
Rung 1 viability: gradient (0.89), local_supervision (0.67) above chance (0.10).
random_projections at fb=0.01: val_acc=0.10 (at chance).

---

## 🏃 Phase 2: Rung 1 — Viability Ladder (In Progress)

## 🏃 Phase 1 Complete: Rung 0 — Wiring Verification ✅

**Done 2026-11-22:** All 19 credits verified for non-zero pseudo-gradient (error-aware) or non-zero update (error-blind).
Positive control passes on mnist (val_acc=0.89, chance=0.10).
No "free settle telemetry failed" warnings.
All 75 primitive contract tests pass.

---

## 🏃 Phase 2: Rung 1 — Viability Ladder (Minimum Fair Chance)

**Goal:** 1 epoch / 1 seed on minimum viable task > chance (error-aware) or non-zero update (error-blind).

**Task selection (cheapest first):**
| Family | Task | N×D | Rationale |
|--------|------|-----|-----------|
| vision | digits (mnist subset) | 1797×64 | Before full mnist (70k×784) |
| tabular | iris | 150×4 | Smallest tabular |
| graph | cora | 2708×1433 | Standard graph |
| sequence | sequential_mnist | 70k×28 | Time-major supported |
| continual | split_mnist | - | Task sequence |
| rl | cartpole | - | Fast RL |

**Ladder per credit (3 points on primary knob + 1 confirmation):**
| Credit | Primary Knob | 3-Point Ladder |
|--------|--------------|----------------|
| gradient | — (baseline) | N/A |
| random_projections | feedback_scale | [0.01, 0.1, 1.0] |
| local_contrastive | readout_scale | [1.0, 10.0, 100.0] |
| thermodynamic_contrast | beta | [0.01, 0.05, 0.1] |
| pc_alm | step_size | [0.05, 0.1, 0.2] |
| target_inversion | — | N/A (baseline) |
| pepita | feedback_scale | [0.01, 0.1, 1.0] |
| forward_tangent | estimator_samples | [200, 400, 800] |
| score_function | — | N/A |
| zeroth_order | fd_step | [0.001, 0.01, 0.1] |
| surrogate | temperature | [0.1, 1.0, 10.0] |
| local_supervision | — | N/A |
| eligibility_prop | lambda_ | [0.5, 0.9, 0.99] |
| unbiased_rtrl | — | N/A |
| rtrl_reference | — | N/A |
| local_goodness | — | N/A |
| hybrid | — | N/A |

**Pass criteria (Rung 1):**
- Error-aware: `val_acc > chance + 2σ` (above chance)
- Error-blind: non-zero parameter update, finite loss
- Best ladder point confirmed on 1 additional seed

**Output:** `results/sec/rung1_viability.json` — coordinate, metric, ladder point, seed, walltime

---

## 🏃 Phase 3: Rung 2 — Cross-Family Comparison at Best Box

**Goal:** Each credit at its best declared box, paired comparison (n=5 seeds).

**Pre-registration:** Use `EffectSizeRegistration.for_task_family()` with family min_d:
- vision/seq/rl/continual/neuro/quantum/photonic: d ≥ 0.8
- tabular/graph/sci/lm: d ≥ 0.5

**Comparison design:**
- Control: `gradient` (or `euclidean` update baseline)
- Treatment: each credit at its best ladder point
- Paired seeds (same seed, different credit)
- Metric: `val_acc` (normalized per task family)

**Command:**
```bash
uv run python -m computronium.experiment.sec_deep_dive \
  --credit <credit> --family <task_family> \
  --registration configs/preregistrations/sec_credit_<credit>.json \
  --n-seeds 5 --async
```

**Decision (Rung 2):**
- `passes_effect_size()` → **Provisional coordinate** (claim candidate)
- All ladder points fail → **Defect or capability gap** (triage)

---

## 🏃 Phase 4: Rung 3 — Confirmatory Paired Comparison (Claims)

**Goal:** Pre-registered paired comparison with n=5 seeds, sequential/always-valid CI.

**Pre-registration (committed before first seed):**
```json
{
  "claim": "credit.X beats gradient by d≥0.8 on mnist at box {...}",
  "metric": "val_acc",
  "min_d": 0.8,
  "alpha": 0.05,
  "min_seeds": 5,
  "box": {...},
  "created": "2026-11-22"
}
```

**Harness:** `paired_comparison(treatment, control, n_boot=10000, n_perm=10000)`
**Decision:** `passes_effect_size(registration)` → **Claim** / **Coordinate result**

**No optional stopping:** Fixed n=5, no peeking. CI is bootstrap percentile on mean difference.

---

## 🔧 Defect-to-Fix Propagation Strategy (Maximum Leverage)

**Principle:** One fix → multiple primitives. Shared implementation = shared defects.

### Defect Pattern → Root Cause → Fix Scope

| Defect Pattern | Likely Shared Root | Fix Propagates To |
|----------------|-------------------|-------------------|
| pseudo-grad shape mismatch | `target_kind` not declared on axis | All credits reading label |
| settle divergence | `max_steps=30` default, convergence=1e-4 | All energy_min dynamics |
| CUDA OOM | `ProcessPoolExecutor` + single GPU | All async evaluators |
| label channel missing | `readout_error` not added to pipeline | All credits needing it |
| geometry-compatibility crash | dispatch missing `_geometry_path` | All credit×geometry pairs |
| slow (>60s/epoch L0) | CPU-bound settle, no GPU kernel | All energy_min + recurrent |
| NaN/Inf loss | `max_energy` clamp missing | All substrates with noise |

### Fix Workflow (Rung 0/1 Failure → Fix → Verify)

```bash
# 1. Name the defect with failing test
pytest tests/primitives/test_<axis>_contract.py::test_<defect> -v

# 2. Fix in shared location (protocol, registry, kernel, dispatch)
# 3. Verify: re-run Rung 0/1 for ALL affected primitives
uv run python scripts/run_capability.py --session <A|B|C|D>

# 4. Record: defect ID, fix file, primitives fixed, re-measurement
```

**Continuous capability gate (TODO99 #4):**
```bash
# After each fix session
uv run python scripts/run_capability.py --session A  # plasticity
uv run python scripts/run_capability.py --session B  # update + credits
uv run python scripts/run_capability.py --session C  # dynamics + geometry
uv run python scripts/run_capability.py --session D  # substrate
```

---

## 📈 Experiment Tracking (Session Log Template)

```
## Session YYYY-MM-DD
**Decision:** Which credits achieve d≥family_min on declared families at best box?
**Experiment:** <command>
**Box:** <task, fidelity, seeds, knobs allowed>
**Rung / stop:** <0-3; why the rung stopped>
**Result:** <metric, ruler, cost>
**Triage:** <defect | capability gap | coordinate result; if defect, the failing test; if gap, the primitive that closes it>
**Fixes Applied:** <files changed>
**Next Experiment:** <planned command>
```

**Experiment Log Table:**

| Rung | Credit | Task Family | Box (geometry/dyn/credit) | Ladder Point | Val Acc | d | Pass? | Walltime | Defect/Gap |
|------|--------|-------------|---------------------------|--------------|---------|---|-------|----------|------------|
| 0 | random_projections | vision | ff/inst | — | wiring | — | ✅/❌ | 5s | — |
| 1 | random_projections | vision | ff/inst | fb=0.1 | 0.92 | 1.2 | ✅ | 45s | — |
| 2 | random_projections | vision | ff/inst | fb=0.1 | 0.93±0.01 | 1.1 | ✅ | 225s | — |
| 3 | random_projections | vision | ff/inst | fb=0.1 | paired n=5 | CI | claim/coord | 20min | — |

---

## 🎯 Success Criteria (Per Domain)

| Domain | Primary Metric | Claim Threshold | Minimum Credits Working |
|--------|---------------|-----------------|------------------------|
| Vision (mnist) | val_acc | > 0.95 | ≥3 error-aware |
| Graph (cora) | val_acc | > 0.70 | ≥2 error-aware |
| Tabular (iris) | val_acc | > 0.90 | ≥2 error-aware |
| Sequence | val_acc | > 0.95 | ≥2 error-aware |
| Continual | retention | > 0.80 | ≥2 error-aware |
| RL (cartpole) | mean_reward | > -200 | ≥2 error-aware |

**Non-negotiable:**
- Zero "free settle telemetry failed" warnings
- Every positive control completes (PASS or named FAIL-by-bar)
- Every number carries its ruler (resolution, chance rate, box)
- Claims within 1σ of threshold = `marginal` (re-measure as paired comparison)

---

## 🔄 The Self-Stabilizing Loop

| Computronium System | SEC Methodology (This Plan) |
|---------------------|----------------------------|
| 6 axes × primitives → search space | Decision loop × rung ladder × defect triage → fix space |
| Positive control (gate) | Rung 0 positive control PASS (100% target) |
| Energy minimization (settle) | DECIDE→FALSIFY→TRIAGE→FIX→VERIFY (stop when decided) |
| Credit assignment (local signal) | Viability ladder (minimum fair chance before ranking) |
| Defect patterns (symptom→cause) | Defect triage table → fix propagation across primitives |
| Normalized metrics (ruler-relative) | Effect size per family + declared box |
| Claim eligibility (n≥5, replay hash) | Pre-registered paired comparison + SEC loop |

**Why it stabilizes:**
1. Every anomaly → triage question (not "algorithm failure")
2. Every assumption → testable (Question Excluded Possibilities table)
3. Every fix → file (symptom→fix→file mapping prevents drift)
4. Every run → priced from reality (measured pilot → 2× watchdog)
5. Context → code (AGENTS.md rules, not prose in TODOs)
6. Every negative → exit (defect with test / gap with primitive / boxed coordinate)
7. Tuning → before ranking (each arm at best box before comparison)
8. Time → outcome (rung ladder + 2× measured-cost watchdog)
9. Claims → error control (sequential/always-valid CI, no optional stopping)

---

## 🚀 Immediate Next Actions

### Session A (Today): Rung 0 Wiring for All 17 Credits
```bash
# Parallel wiring check on digits (vision subset)
for credit in random_projections local_contrastive thermodynamic_contrast \
              pc_alm target_inversion pepita forward_tangent score_function \
              zeroth_order surrogate local_supervision local_goodness hybrid \
              eligibility_prop unbiased_rtrl rtrl_reference; do
  uv run python -m computronium.experiment.survey_cli 0.1 \
    --mode learn --policy tpe --device cuda \
    --tasks digits --fidelity L0 \
    --axes "credit=$credit,geometry=feedforward,dynamics=instantaneous,update=euclidean" \
    --epochs 1 --n-seeds 1 &
done
wait
```

### Session B: Rung 1 Ladder for Wired Credits
```bash
# 3-point ladder per credit on best geometry/dynamics
for credit in <wired_credits>; do
  for knob_val in <ladder_points>; do
    uv run python -m computronium.experiment.survey_cli 0.1 \
      --mode learn --policy tpe --device cuda \
      --tasks digits --fidelity L0 \
      --axes "credit=$credit,geometry=feedforward,dynamics=instantaneous,update=euclidean,credit.<knob>=$knob_val" \
      --epochs 1 --n-seeds 1 &
  done
done
wait
```

### Session C: Rung 2 Async SEC at Best Boxes
```bash
# Parallel SEC for each credit at its best ladder point
uv run python -m computronium.experiment.sec_deep_dive \
  --credit random_projections --family vision --n-seeds 5 --async
# ... repeat for each viable credit
```

### Session D: Rung 3 Pre-Registered Claims
```bash
# For credits passing Rung 2
uv run python -m computronium.experiment.sec_deep_dive \
  --credit random_projections --family vision \
  --registration configs/preregistrations/sec_credit_random_projections.json \
  --n-seeds 5
```

---

## 📋 Defect Registry (Living Document)

| Defect ID | Symptom | Mechanism | Failing Test | Fix File | Primitives Fixed | Verified |
|-----------|---------|-----------|--------------|----------|------------------|----------|
| GAP-001 | σ channel missing | θ not in _step_psi | test_plastic_step_carries_substrate_state | sec_loop.py | All plasticity | — |
| ... | ... | ... | ... | ... | ... | ... |

*Populated as defects are discovered. Each entry requires: named mechanism + failing test + fix file + verification.*

---

## 🏁 Exit Criteria for TODO100

- [ ] Rung 0: All 17 credits wired (pseudo-grad non-zero, settle converges)
- [ ] Rung 1: ≥12 credits viable on ≥1 declared family (ladder confirmed)
- [ ] Rung 2: ≥8 credits at best box with provisional coordinate
- [ ] Rung 3: ≥3 credits with confirmed claim (pre-registered, n=5, effect size)
- [ ] All defects in registry have fixing test + fix file + verification
- [ ] Capability gate green after each session (no regressions)
- [ ] Experiment log table complete with rung, stop reason, box, cost

**This is not a measurement campaign. This is a capability campaign. The deliverable is the system's ability to do something it could not do before.**

---

*TODO100 enters the SEC loop. Every run answers a decision. Every low cell is a defect probe. Fixes propagate across primitives. The map is the artifact, not the leaderboard.*