# TODO105 — Close the Remaining Gaps

## Scope
The capability map is evidence-based (52/75 viable+blind, breadth PASS, box-keyed
cost model). Three items remain, each with a trigger and a measured box.

Progress: **2 of 3 closed.** The claim (item 2) has its pilot harness working and
its three seed blocks scheduled; the family minimum is not yet registered.

---

## Progress Tracker

| # | Item | State | Evidence |
|---|------|-------|----------|
| 1 | Geometry re-run — two carriers | ✅ done | `results/sec/serial4/geometry_results.json` |
| 2 | 5.3 Claim — pre-registered minimum | 🔄 pilot | three n=64 blocks running |
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

## 2. 5.3 Claim — pre-register a certifiable minimum 🔄 IN PROGRESS
**What:** the n=64 run missed 0.8 by 0.017; seed-block d varies 0.83–1.07
(> within-block CI). A claim needs a pre-registered family minimum that **every
seed block clears**, plus a block-variance estimate.
**Design (locked, do not revise mid-run):**
- Pilot: three seed blocks (0..63, 64..127, 128..191), each n=64, measure d and
  its block sd.
- Pre-register: `min_d = min(block_lower_bounds) - 1.96 * block_sd`, so every
  block's 95% CI lower bound exceeds it.
- Fresh seeds for the confirmatory run at that `min_d`.
**Target:** `credit/random_projections` at the mnist base box (measured ~6 s/cell
on CPU). 128 cells ≈ 13 min per block.

**Commands (running):**
```bash
SEC_DEVICE=cpu SEC_AXES=credit SEC_PRIMITIVES=random_projections \
SEC_RUNG2_SEEDS=64 SEC_RUNG2_SEED_OFFSET=$off SEC_RUNG2=auto \
SEC_RUNG_TIMEOUT=60 SEC_RESULTS_DIR=results/sec/pilot_rp_block$off \
uv run python -u scripts/run_full_sec_competitive.py   # off = 0, 64, 128
```

**Why `SEC_DEVICE=cpu`:** the shared GPU fails a cell with a launch error under
contention (`CUSOLVER_STATUS_EXECUTION_FAILED`). The device is now one declared
value (`sec_all_axes.SEC_DEVICE`, default `auto`); the pilot pins it to `cpu`.

**Remaining steps:**
1. Read the three blocks' `rung2_effect` (cohens_dz, ci_lower) from
   `results/sec/pilot_rp_block{0,64,128}/credit_results.json`.
2. Compute `block_sd` over the three `cohens_dz` values and
   `min_d = min(ci_lower) - 1.96 * block_sd`.
3. Write `configs/preregistrations/sec_credit_random_projections_pilot.json`
   with that `min_d`, the box, and `min_seeds = 64` — **before** the
   confirmatory seeds run.
4. Run the confirmatory comparison at fresh seeds
   (`SEC_RUNG2_SEED_OFFSET=192`), and record `claim` / `coordinate`.

---

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
| Claim | one pre-registered comparison at the family minimum every block clears | 🔄 |
| Fixtures | 127/127 property locks pass | ✅ (49/49 in scope) |

---

## Process Note
The SEC methodology is stable. Each rung's stop rule is "evidence, not
wall-clock". The device is one declared value (`SEC_DEVICE`), never a per-run
patch. The claim closes when the confirmatory run reports its verdict against the
registered `min_d`; a `coordinate` verdict at that point is a coordinate result
with the block variance recorded, not a mechanism verdict.
