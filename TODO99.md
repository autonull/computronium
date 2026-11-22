# TODO99 — Fix the Mechanisms, Then Test Them

**Status:** 2026-11-22. Supersedes TODO98. The previous plan ran SEC on broken mechanisms. This plan fixes mechanisms first, validates capability, then claims.

---

## The Problem (from TODO98 retrospective)

| What we did | Why it didn't work |
|-------------|-------------------|
| P4/P7: 34 SEC ladder cells on 17 credits | Only 2 credits produced claims; 7 are capability gaps (no `modulate()`, wrong architecture) |
| Narrower/wider ladders on same 7 credits | Knob tuning cannot fix a missing mechanism |
| 10 primitives unmeasured, 14 capability tests skipped | Rung-1 viability never established before rung-3 claims |

**The rule we ignored:** "A measurement that ends in a negative is not a deliverable; a **defect** is, because fixing it widens the system." (SEC §10) We measured negatives and called them coordinates.

---

## The Corrected Order

```
P3 (mechanism fixes) → Capability 75/75 (viability) → SEC (claims on working laws)
```

Not:
```
SEC → more SEC → maybe P3
```

---

## 1. P3: Mechanism Fixes (5 rows, 1 session each)

| Row | Defect | Fix | Test that must pass |
|-----|--------|-----|---------------------|
| 1 | `plasticity.substrate_coupled`: no σ channel | Build `θ` (substrate state) in `_step_psi`; carry through `modulate()` | `test_the_plastic_step_carries_the_substrate_state` xpasses |
| 2 | `plasticity.rule_state` (9): no `modulate()` hook | Implement `modulate(ψ, θ, state)` for each rule | Digest differs from `null` plasticity |
| 3 | `update.*` (EWC/SI/cascade/VON): wrong step semantics | `gradient_relative` table; VON lr = `step_size`; widen domain to 1.0 | Ladder reaches 0.1 ceiling, EWC/SI reach 0.3 (0.096×) |
| 4 | 10 credits: pseudo-gradient mismatch | Fix `pseudo_gradient_def` vs `compute_pseudo_gradient` in `ontology/credit/` | `test_primitive_contract` on pseudo-gradient count/shape |
| 5 | 10 primitives unmeasured: no base box | Add `BASE_BOXES` for quantum, photonic, nca, conv, etc. | `test_all_75_primitives_have_measured_row` passes |

**Deliverable:** All 75 laws in `works` or `refused` (with failing test), zero `defect-or-gap`.

---

## 2. Capability Suite: 75/75 at Rung-1 (1 session)

**Gate:** `uv run python -m pytest tests/primitives/test_primitive_capability.py -q`

| Current | Target |
|---------|--------|
| 62 passed / 14 skipped | 75 passed |

**What "passed" means:** 1 epoch / 1 seed on minimum viable task:
- Vision (digits/mnist): `val_acc > 0.10` (above chance 0.10)
- Tabular (iris): `val_acc > 0.33` (above chance 0.33)
- Graph (cora): `val_acc > 0.14` (above chance 0.14)
- Sequence (delayed_cue): non-zero update, finite loss
- Error-blind credits (`homeostatic`, `temporal_trace`): non-zero parameter update

**No SEC until this is green.** A primitive without rung-1 viability has no business in rung-3.

---

## 3. SEC: Claims on Working Laws Only (1-2 sessions)

**Scope:** Only credits that pass capability suite on ≥2 families (breadth gate).

**Current candidates (from breadth gate + P3 fixes):**
| Credit | Families passing | Status |
|--------|------------------|--------|
| `local_contrastive` | vision, tabular | ✅ Claim exists |
| `random_projections` | graph, tabular | ✅ Claim exists |
| `forward_tangent` | lm, sequence, vision | ⚠️ Needs P3 row 4 |
| `thermodynamic_contrast` | tabular, vision | ⚠️ Needs P3 row 5 (base box) |
| `target_inversion` | tabular, vision | ⚠️ Needs P3 row 1 (pc_alm dynamics) |
| `local_goodness` | tabular, vision | ⚠️ Needs P3 row 4 (lemma mode) |
| `pc_alm` | tabular, vision | ⚠️ Needs P3 row 5 (base box) |
| `gradient` | continual, graph, sequence, tabular, vision | ⚠️ Needs P3 row 3 (step semantics) |

**Target:** ≥3 claims from credits that *train*, not from knob coordinates.

---

## Session Plan

### Session 1 — P3 Row 1: σ Channel for `substrate_coupled`
```sh
# Edit: computronium/experiment/sec_loop.py _step_psi
#       computronium/ontology/plasticity/substrate_coupled.py modulate()
uv run python -m pytest tests/primitives/test_surface_fit.py::test_the_plastic_step_carries_the_substrate_state -v
uv run python scripts/probes/p1_law_surface.py --only signal --resume --steps 200 --out results/p1
uv run comp test --surface
```
**Exit criterion:** σ channel test xpasses; surface exits 0.

### Session 2 — P3 Row 2: `rule_state` + `substrate_coupled` `modulate()`
```sh
# Edit: computronium/ontology/plasticity/rule_state.py (9 rules)
#       computronium/ontology/plasticity/substrate_coupled.py modulate()
uv run python -m pytest tests/property/test_protocol_seams.py::test_a_plastic_laws_modulation_reaches_the_digest -v
uv run comp test --surface
```
**Exit criterion:** 10 plasticity laws have `modulate()`; digest differs from `null`.

### Session 3 — P3 Row 3: Update step semantics + domain
```sh
# Edit: computronium/ontology/update/ (EWC, SI, cascade, VON)
#       axis rows: step_size domain → 1.0
uv run python scripts/probes/p1_law_surface.py --only signal --resume --steps 200 --out results/p1
uv run comp test --surface
```
**Exit criterion:** EWC/SI reach 0.3 ceiling; VON has single lr.

### Session 4 — P3 Row 4: Pseudo-gradient audit (10 credits)
```sh
# Edit: computronium/ontology/credit/ (fix pseudo_gradient_def)
uv run python scripts/probes/p1_law_surface.py --only signal --resume --steps 200 --out results/p1
uv run comp test --surface
```
**Exit criterion:** All 10 credits pass `test_primitive_contract` pseudo-gradient check.

### Session 5 — P3 Row 5: Base boxes for 10 unmeasured primitives
```sh
# Edit: computronium/experiment/sec_pilot.py BASE_BOXES
# Add: quantum, photonic, nca, conv, complex, optical, rtrl_reference, rule_state, substrate_coupled, unbiased_rtrl
uv run python -m pytest tests/primitives/test_surface_lock.py::test_all_75_primitives_have_measured_row -v
uv run comp test --surface
```
**Exit criterion:** All 75 primitives have ≥1 measured row.

### Session 6 — Capability Suite 75/75
```sh
uv run python -m pytest tests/primitives/test_primitive_capability.py -q
# Fix any skipped: 1 epoch / 1 seed on minimum task
```
**Exit criterion:** 75 passed, 0 skipped.

### Session 7 — SEC on Working Laws
```sh
# Only credits with ≥2 viable families
uv run python scripts/probes/p4_sec_ladders.py --out results/p4
uv run python -m computronium.experiment.sec_claims --register --device auto
uv run python -m computronium.experiment.sec_claims --run --device auto
```
**Exit criterion:** ≥3 claims from working laws.

---

## Gates That Must Stay Green

```sh
uv run comp gate breadth              # 17/17
uv run python scripts/audit.py --static   # 0 findings
uv run python -m pytest tests/primitives/test_surface_lock.py -q
uv run python -m pytest tests/property/test_protocol_seams.py -q
uv run python -m pytest tests/primitives/test_primitive_capability.py -q  # after Session 6
```

---

## What We Stop Doing (Reaffirmed)

- Running SEC on primitives without rung-1 viability
- Calling a ladder coordinate a "result" when the mechanism is a capability gap
- Tuning knobs on credits that don't implement `modulate()` or have wrong step semantics
- Treating "0 unaccounted rows" as progress — the 10 unmeasured primitives are the blocker

---

## Definition of Done (Revised from TODO98 §5)

1. **Surface declared** — 75 laws, 6 seams, rule tables. ✅
2. **All 75 laws in `works` or `refused` (with failing test)** — zero `defect-or-gap`. ❌
3. **6/6 seams pass** — ✅
4. **Every `defect-or-gap` closed by a fix** — P3 rows 1-5. ❌
5. **All 75 primitives have ≥1 measured row** — 10 currently unmeasured. ❌
6. **Capability suite 75/75 at rung-1** — 62/14 now. ❌
7. **SEC claims on working laws only** — ≥3 claims from viable credits. ❌
8. **75/75 kernels kill+parity** — 10 implemented, 65 documented. ✅
9. **Audit consistency** — no per-family tests, no refusal without failing test. ✅

---

## Estimated Effort

| Phase | Sessions | Weeks |
|-------|----------|-------|
| P3 rows 1-5 (mechanism fixes) | 5 | 2-3 |
| Capability 75/75 | 1 | 1 |
| SEC on working laws | 1-2 | 1 |
| **Total** | **7-8** | **4-5** |

Each session = one landing (edit → gates → measurement → commit). No session runs SEC until capability gate is green.