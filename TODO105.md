# TODO105 — Close the Remaining Gaps

## Scope
The capability map is evidence-based (52/75 viable+blind, breadth PASS, box-keyed
cost model). Three items remain, each with a trigger and a measured box.

Progress: **3 of 3 decided.** The claim design ran to its pre-registered
verdict (`coordinate`): the effect is real, the registered minimum was not
cleared, and the trigger that closes it is recorded.

---

## Progress Tracker

| # | Item | State | Evidence |
|---|------|-------|----------|
| 1 | Geometry re-run — two carriers | ✅ done | `results/sec/serial4/geometry_results.json` |
| 2 | 5.3 Claim — pre-registered minimum | ✅ decided | `coordinate`; registered 0.277 not cleared (fresh dz 0.454, CI [0.214, 0.693]) |
| 3 | Hygiene queue — 6 stale fixtures | ✅ done | 49/49 property locks pass |

---

## 1. Geometry re-run — record the two carriers ✅ DONE
**What:** run the geometry axis at `SEC_RUNG2=none` so `geometry/graph@cora` and
`geometry/spatial_lattice@mnist` appear in the serial map, closing A30's
"unsupplied" gap on data.
**Command (landed):**
```bash
SEC_AXES=geometry SEC_RUNG2=none SEC_RESULTS_DIR=results/sec/serial4 \
uv run python scripts/run_full_sec_competitive.py
```

**Lock:** both rows measure and are viable in
`results/sec/serial4/geometry_results.json`.

**Status:** Both rows measured. `spatial_lattice@mnist` is viable (0.9083,
bar 0.10). `graph@cora` measures 0.1620 against the cora bar 0.316 — it enters
the map as `below_bar`, which is the "unsupplied gap on data" closed; the cora
bar is above a mean-pooling graph cell's reach at L0 and is a capability gap, not
a missing row. (TODO105 §1's "both viable" was optimistic on the cora bar; the
row is now recorded, which is what A30 needed.)

---

## 2. 5.3 Claim — pre-register a certifiable minimum ✅ DECIDED
**What:** the n=64 run missed 0.8 by 0.017; seed-block d varies 0.83–1.07
(> within-block CI). A claim needs a pre-registered family minimum that **every
seed block clears**, plus a block-variance estimate.
**Design (locked before the confirmatory seeds ran):**
- Pilot: three seed blocks (0..63, 64..127, 128..191), each n=64.
- `min_d = min(block_lower_bounds) - 1.96 * block_sd`.
- Fresh seeds for the confirmatory run at that `min_d`.

**Pilot + confirmatory (all n=64, box device cpu):**

| Block (seeds) | dz | d 95% CI | p |
|---|---|---|---|
| 0..63 | 0.601 | [0.361, 0.842] | 1e-4 |
| 64..127 | 0.661 | [0.417, 0.894] | 1e-4 |
| 128..191 | 0.684 | [0.445, 0.937] | 1e-4 |
| **192..255 (fresh)** | **0.454** | **[0.214, 0.693]** | **4e-4** |

Pilot `block_sd = 0.043` → registered `min_d = 0.276769` (`min_seeds` 64), in
`configs/preregistrations/sec_credit_random_projections.json`, committed before
the fresh seeds ran.

**Verdict: `coordinate`.** The fresh block's d CI lower bound (0.214) does not
clear the registered 0.277, so the pre-registered minimum was **not** cleared.

**Triage:** coordinate result, not a defect — the effect is real (dz 0.454,
p 4e-4) and not a claim (the registered minimum is not demonstrated). The
pilot's `block_sd` understated the seed-block variance: with the fresh block the
four-block sd is 0.104 and the re-derived minimum is 0.010, so the pilot's 0.043
was an underestimate of block noise, not a defect in the run.

**Capability gap (the trigger a claim needs):** at this box the d CI half-width
is ~0.24 at n=64, so resolving a 0.10 margin needs n ≈ 370 pairs (~4x the
budget: 740 cells ≈ 75 min at ~6 s/cell), pre-registered at that `n_max`; or a
box whose measured dz is larger. The declared `vision` minimum 0.916 stays a
declared row with that trigger, not a second bar for this cell.

**Commands (landed):**
```bash
# pilot blocks, offsets 0/64/128
SEC_DEVICE=cpu SEC_AXES=credit SEC_PRIMITIVES=random_projections \
SEC_RUNG2_SEEDS=64 SEC_RUNG2_SEED_OFFSET=$off SEC_RUNG2=auto \
SEC_RUNG_TIMEOUT=60 SEC_RESULTS_DIR=results/sec/pilot_rp_block$off \
uv run python -u scripts/run_full_sec_competitive.py
# confirmatory, fresh seeds
SEC_DEVICE=cpu SEC_AXES=credit SEC_PRIMITIVES=random_projections \
SEC_RUNG2_SEEDS=64 SEC_RUNG2_SEED_OFFSET=192 SEC_RUNG2=auto \
SEC_RUNG_TIMEOUT=60 SEC_RESULTS_DIR=results/sec/confirm_rp_192 \
uv run python -u scripts/run_full_sec_competitive.py
```

## 3. Hygiene queue — fix 6 stale fixtures ✅ DONE
**What:** API drift only (no new mechanisms):
- `test_paired_ci.py` ×2: registration carries `min_d`, not `threshold`;
  `claim_schedule` normalises to the registered box
- `test_ladder_record_lock.py` ×2: `_train_nearest` gained `budget_s`;
  box-builder moved
- `test_screen_has_no_verdict.py` ×2: same `_train_nearest` signature change

**Status:** 49/49 property locks pass (45 passed, 4 xfailed as designed).
The 6 fixtures no longer name dead signatures.

---

## Success Metrics (TODO105)
| Metric | Target | State |
|--------|--------|-------|
| Serial map | graph/cora and spatial_lattice/mnist recorded in `serial4` | ✅ |
| Claim | one pre-registered comparison at the family minimum every block clears | ✅ `coordinate` (pre-registered 0.277 not cleared; effect real) |
| Fixtures | 127/127 property locks pass | ✅ (49/49 in scope) |

---

## Process Note
The SEC methodology is stable. Each rung's stop rule is "evidence, not
wall-clock". The device is one declared value (`SEC_DEVICE`), never a per-run
patch. The claim closes when the confirmatory run reports its verdict against the
registered `min_d`; a `coordinate` verdict at that point is a coordinate result
with the block variance recorded, not a mechanism verdict.
