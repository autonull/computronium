# TODO99 Accelerated — Parallel Mechanism Fixes

**Status:** 2026-11-22. Same deliverables as TODO99, compressed from 7-8 sessions to **4-5 sessions** by parallelizing independent work.

---

## Acceleration Strategy

| Principle | Application |
|-----------|-------------|
| **Independent work in parallel** | P3 rows 3, 4, 5 are independent → combine into 1-2 sessions |
| **Batch similar edits** | All 4 update laws in one pass; all 10 credits' pseudo-gradients in one pass |
| **Capability tests start early** | Run capability on fixed primitives immediately, don't wait for all 75 |
| **One surface re-measure per session** | Use `p1_law_surface.py --resume` (cached) instead of full re-runs |

---

## Session Plan (Accelerated)

### Session A — P3 Rows 1+2: Plasticity Protocol Fix (1 session)
**Combines:** σ channel + `modulate()` hooks for all 10 plasticity laws

```sh
# Edit: computronium/experiment/sec_loop.py _step_psi (σ channel)
# Edit: computronium/ontology/plasticity/*.py (10 files: rule_state ×9 + substrate_coupled)
# The modulate() implementation is similar across rules — batch the pattern
uv run python -m pytest tests/primitives/test_surface_fit.py::test_the_plastic_step_carries_the_substrate_state -v
uv run python -m pytest tests/property/test_protocol_seams.py::test_a_plastic_laws_modulation_reaches_the_digest -v
uv run python scripts/probes/p1_law_surface.py --only signal --resume --steps 200 --out results/p1
uv run comp test --surface
```
**Exit:** σ channel xpasses; 10 plasticity laws have `modulate()`; surface exits 0.
**Unlocks:** `substrate_coupled`, `rule_state` (9) — 10 primitives now measurable.

---

### Session B — P3 Rows 3+4: Update Semantics + Pseudo-Gradient (1 session)
**Combines:** 4 update laws + 10 credits' pseudo-gradients (independent subsystems)

```sh
# Edit: computronium/ontology/update/ (bayesian_online, cascade_synapse, elastic_consolidation, synaptic_intelligence)
#   - step_semantics: gradient_relative (not per_element_displacement)
#   - VON: single lr = step_size (delete von_alpha)
#   - axis rows: step_size domain → 1.0
# Edit: computronium/ontology/credit/ (10 credits: fix pseudo_gradient_def)
#   - LocalGoodnessCredit: lemma mode e₁ = one_hot(y) - softmax(out)
#   - Others: match compute_pseudo_gradient signature
uv run python scripts/probes/p1_law_surface.py --only signal --resume --steps 200 --out results/p1
uv run comp test --surface
```
**Exit:** EWC/SI reach 0.3 ceiling; 10 credits pass pseudo-gradient contract.
**Unlocks:** 4 update laws + 10 credits — 14 primitives now viable.

---

### Session C — P3 Row 5: Base Boxes + Capability Suite (1 session)
**Combines:** Mechanical BASE_BOXES additions + immediate capability validation

```sh
# Edit: computronium/experiment/sec_pilot.py BASE_BOXES
# Add 10 entries (quantum, photonic, nca, conv, complex, optical, rtrl_reference, rule_state, substrate_coupled, unbiased_rtrl)
# Copy pattern from existing boxes; task families from breadth gate
uv run python -m pytest tests/primitives/test_surface_lock.py::test_all_75_primitives_have_measured_row -v
uv run comp test --surface

# Capability suite: run ONLY the 14 skipped primitives (targeted, not full suite)
uv run python -m pytest tests/primitives/test_primitive_capability.py -k "skipped_primitive_names" -q
# Fix each skipped: 1 epoch / 1 seed on minimum task (digits/iris/cora/delayed_cue)
uv run python -m pytest tests/primitives/test_primitive_capability.py -q
```
**Exit:** All 75 primitives measured; capability suite 75/75 passed.
**Unlocks:** SEC can now run on viable primitives only.

---

### Session D — SEC on Working Laws (1 session)
**Scope:** Only credits with ≥2 viable families (from breadth gate + P3 fixes)

```sh
# Expected viable credits after P3: local_contrastive, random_projections, forward_tangent, 
# thermodynamic_contrast, target_inversion, local_goodness, pc_alm, gradient
# (eligibility_prop, pepita, local_supervision, score_function, zeroth_order remain capability gaps)
uv run python scripts/probes/p4_sec_ladders.py --out results/p4
uv run python -m computronium.experiment.sec_claims --register --device auto
uv run python -m computronium.experiment.sec_claims --run --device auto
```
**Exit:** ≥3 claims from working laws.

---

### Session E — Reproduction (E4) (1 session, parallelizable with D)
```sh
# Second device/profile reproduction for all E3 claims
uv run python -m computronium.experiment.sec_claims --register --device cuda
uv run python -m computronium.experiment.sec_claims --run --device cuda
```
**Can run in background during Session D.**

---

## Parallelization Details

### What Can Run Concurrently

| Workstream | Session | Can Pair With |
|------------|---------|---------------|
| Plasticity (σ + modulate) | A | — (foundational) |
| Update semantics | B | Pseudo-gradient (independent files) |
| Pseudo-gradient audit | B | Update semantics (independent files) |
| Base boxes | C | — (mechanical, fast) |
| Capability suite | C | Starts immediately after each fix |
| SEC ladders | D | Reproduction (E) on different device |

### File Independence Map

```
Plasticity (Session A):
  computronium/experiment/sec_loop.py (_step_psi)
  computronium/ontology/plasticity/*.py (10 files)

Update (Session B):
  computronium/ontology/update/bayesian_online.py
  computronium/ontology/update/cascade_synapse.py
  computronium/ontology/update/elastic_consolidation.py
  computronium/ontology/update/synaptic_intelligence.py
  computronium/ontology/axis/update.py (domain → 1.0)

Credits/Pseudo-gradient (Session B):
  computronium/ontology/credit/local_goodness.py
  computronium/ontology/credit/eligibility_prop.py
  computronium/ontology/credit/forward_tangent.py
  computronium/ontology/credit/gradient.py
  computronium/ontology/credit/hybrid.py
  computronium/ontology/credit/local_contrastive.py
  computronium/ontology/credit/local_supervision.py
  computronium/ontology/credit/pc_alm.py
  computronium/ontology/credit/pepita.py
  computronium/ontology/credit/random_projections.py

Base boxes (Session C):
  computronium/experiment/sec_pilot.py (BASE_BOXES dict only)
```

**No file conflicts** between plasticity, update, credits, base boxes.

---

## Time Savings

| Plan | Sessions | Wall-clock (est.) |
|------|----------|-------------------|
| TODO99 sequential | 7-8 | 4-5 weeks |
| Accelerated | 4-5 | **2-3 weeks** |
| Savings | **~40%** | **~40%** |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Session A too large (10 plasticity files) | Split into A1 (σ channel) + A2 (modulate) if >4h; still saves 1 session |
| Session B combines 2 subsystems | They're independent; if one fails, the other still ships |
| Capability suite finds new defects | Run targeted fixes in same session; don't block on full 75 |
| SEC on fewer credits | Only claim on working laws — this is the goal, not a reduction |

---

## Gates (Same as TODO99)

```sh
uv run comp gate breadth              # 17/17
uv run python scripts/audit.py --static   # 0 findings
uv run python -m pytest tests/primitives/test_surface_lock.py -q
uv run python -m pytest tests/property/test_protocol_seams.py -q
uv run python -m pytest tests/primitives/test_primitive_capability.py -q
```

---

## One-Sentence Summary

**Batch independent mechanism fixes (plasticity, update, credits, base boxes) into 3 sessions, run capability validation immediately on fixed primitives, then SEC on working laws only.**